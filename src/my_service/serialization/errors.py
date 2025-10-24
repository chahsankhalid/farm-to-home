import http.client as status
import logging
import traceback

import connexion.problem
from anyio import EndOfStream
from asyncpg import UniqueViolationError
from connexion.lifecycle import ConnexionRequest, ConnexionResponse
from starlette.exceptions import HTTPException

from <%my_service%>.accesscontrol.exceptions import AclException
from <%my_service%>.config import ConfigLoader
from <%my_service%>.util.exceptions import FraudioServiceException, DuplicateValueException

logger = logging.getLogger(__name__)
config = ConfigLoader.get_instance()


# All API and internal errors are converted to the HTTP Problem spec in RFC-7807
# noinspection PyUnusedLocal
def handle_api_exception(request: ConnexionRequest | None, exception: Exception) -> ConnexionResponse:
    if isinstance(exception, AclException) or isinstance(exception, FraudioServiceException):
        logger.debug(f'Gracefully handled {exception.__class__.__name__}: {exception}')
        return exception.problem
    elif isinstance(exception, HTTPException) and exception.status_code != 500:
        logger.debug(f'Gracefully handled {exception.__class__.__name__}: {exception}')
        status_code = exception.status_code
        http_status_title = status.responses.get(exception.status_code, '')
        return connexion.problem(status_code, http_status_title, exception.detail)
    elif isinstance(exception, UniqueViolationError):
        return DuplicateValueException(summary=exception.detail).problem
    else:
        warning_message = f'Unhandled {exception.__class__.__name__} while handling a request'
        if config.log_stacktraces_http_500:
            if isinstance(exception.__context__, EndOfStream):
                exception.__context__ = None
            stack_trace = "".join(traceback.format_exception(exception))
            logger.warning(f'{warning_message}: {exception}\n{stack_trace}')
        else:
            logger.warning(f'{warning_message}: {exception}')

        summary = 'An unhandled exception has occurred while handling your request. ' + \
                  'The application has logged this as an incident - please contact an administrator.'
        problem = FraudioServiceException(summary=summary).problem
        return problem
