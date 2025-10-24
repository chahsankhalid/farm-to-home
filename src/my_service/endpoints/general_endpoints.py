import logging

from <%my_service%>.accesscontrol.authorization import authorize
from <%my_service%>.domain import api_info
from <%my_service%>.domain.models.health_status import HealthStatus
from <%my_service%>.domain.models.message import Message
from <%my_service%>.util.exceptions import DuplicateValueException
from <%my_service%>.util.paths import app_name

logger = logging.getLogger(__name__)
resource_name = 'general'


@authorize()
async def welcome():
    msg = f'Welcome to Fraudio! This is the {repo_name()} API.'
    return Message(msg)


@authorize()
async def healthz():
    return HealthStatus(
        status='Healthy',
        app_version=api_info.version
    )


@authorize()
async def echo(body):
    return body


@authorize()
async def duplicate_value_error():
    raise DuplicateValueException('transactionid', '000001')


@authorize()
async def internal_error():
    raise ValueError('This is an example of an internal server error.')


@authorize(f'common.forbidden.read')
async def forbidden_error():
    msg = 'This path is forbidden for everyone.'
    return Message(msg)
