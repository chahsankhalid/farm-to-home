import functools
import inspect
import logging
from uuid import UUID

from connexion import context

from <%my_service%>.accesscontrol.exceptions import AccessDeniedException, InvalidSessionException, \
    MissingEndpointArgumentsException
from <%my_service%>.domain.models.credentials import Credentials
from <%my_service%>.serialization.serializable import Serializable

logger = logging.getLogger(__name__)


# Decorator with parameters
def authorize(scope=None):
    def decorator(function):
        function_arg_spec = inspect.getfullargspec(function)
        function_argument_names = function_arg_spec.args
        function_argument_annotations = function_arg_spec.annotations
        function_module_path = f'{function.__module__}.{function.__name__}'

        @functools.wraps(function)
        async def wrapper(*args, **kwargs):
            kwargs['credentials'] = None
            requires_authorization = scope is not None
            is_authenticated = 'token_info' in context.context
            if is_authenticated:
                credential_props = context.context['token_info']
                credentials = Credentials.from_dict(credential_props)
                kwargs['credentials'] = credentials
                if requires_authorization:
                    require_permission(credentials, scope)
            elif requires_authorization:
                raise InvalidSessionException()
            if any(key for key in function_argument_names if key not in kwargs):
                raise MissingEndpointArgumentsException(function_module_path, function_argument_names,
                                                        list(kwargs.keys()))
            relevant_kwargs = {}
            for key in function_argument_names:
                value = kwargs[key]
                if isinstance(value, str) and issubclass(function_argument_annotations[key], UUID):
                    value = UUID(value, version=4)
                elif isinstance(value, dict) and issubclass(function_argument_annotations[key], Serializable):
                    value = function_argument_annotations[key].from_dict(value)
                relevant_kwargs[key] = value
            result = await function(*args, **relevant_kwargs)
            return result

        return wrapper

    return decorator


def require_permission(credentials, scope):
    is_admin = f'pfd.transactions.debug' in credentials.scopes
    has_scope = scope in credentials.scopes
    if not is_admin and not has_scope:
        username = credentials.username if credentials.can_read_user() else None
        raise AccessDeniedException(username, scope)


__all__ = [
    'authorize',
    'require_permission'
]
