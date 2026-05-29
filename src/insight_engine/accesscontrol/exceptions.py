import http.client as status

from connexion import problem


class AclException(Exception):

    def __init__(self,
                 http_status=status.INTERNAL_SERVER_ERROR,
                 summary='Internal server error.'):
        status_response = status.responses[http_status]
        self.problem = problem(http_status, status_response, summary)
        super(AclException, self).__init__(str(summary))


class InvalidAuthenticationException(AclException):

    def __init__(self):
        summary = f'An authentication header was found but it did not contain a valid token.'
        super(InvalidAuthenticationException, self).__init__(status.UNAUTHORIZED, summary)


class InvalidLoginException(AclException):

    def __init__(self):
        summary = f'The login request did not contain valid credentials.'
        super(InvalidLoginException, self).__init__(status.UNAUTHORIZED, summary)


class InvalidLogoutException(AclException):

    def __init__(self):
        summary = f'The logout request did not match a previous login request.'
        super(InvalidLogoutException, self).__init__(status.BAD_REQUEST, summary)


class InvalidSessionException(AclException):

    def __init__(self):
        summary = f'Your session is invalid. This may occur when an unsecured endpoint uses @authorize.'
        super(InvalidSessionException, self).__init__(status.FORBIDDEN, summary)


class MissingEndpointArgumentsException(AclException):

    def __init__(self, endpoint: str, expected_args: list[str], actual_args: list[str]):
        summary = f'The endpoint {endpoint} is expecting args {expected_args}, got args {actual_args}.'
        super(MissingEndpointArgumentsException, self).__init__(status.INTERNAL_SERVER_ERROR, summary)


class AccessDeniedException(AclException):

    def __init__(self, user_name=None, *scopes):
        user_part = f'User \'{user_name}\' is' if user_name else 'You are'
        summary = f'{user_part} not allowed to scopes \'{'\', \''.join(scopes)}\'.'
        super(AccessDeniedException, self).__init__(status.FORBIDDEN, summary)
