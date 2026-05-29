import http.client as status

from connexion import problem


class FraudioServiceException(Exception):
    def __init__(self,
                 http_status=status.INTERNAL_SERVER_ERROR,
                 summary='Internal server error.'):
        http_status_title = status.responses.get(http_status, '')
        self.problem = problem(http_status, http_status_title, summary)
        super(FraudioServiceException, self).__init__(str(summary))


class DuplicateValueException(FraudioServiceException):
    def __init__(self, field=None, value=None, summary=None):
        summary = summary or f'Duplicate value \'{value}\' in field \'{field}\'.'
        super(DuplicateValueException, self).__init__(status.BAD_REQUEST, summary)


class KeyNotFoundException(FraudioServiceException):
    def __init__(self, resource_name: str, **keys):
        formatted_keys = ', '.join(f'{key}=\'{value}\'' for key, value in keys.items())
        summary = f'Could not find any {resource_name} identified by {formatted_keys}.'
        super(KeyNotFoundException, self).__init__(status.NOT_FOUND, summary)


# For /delete
class MissingConfirmationException(FraudioServiceException):
    def __init__(self, required_confirmation_message=None):
        summary = f'This operation needs to be confirmed with the message \'{required_confirmation_message}\'.'
        super(MissingConfirmationException, self).__init__(status.BAD_REQUEST, summary)


class InvalidMappingDefinitionException(FraudioServiceException):
    def __init__(self, target_field=None):
        summary = f'Invalid mapping definition for target field \'{target_field}\'.'
        super(InvalidMappingDefinitionException, self).__init__(status.INTERNAL_SERVER_ERROR, summary)


class UpdateViolation(FraudioServiceException):
    def __init__(self, **keys):
        formatted_keys = ', '.join(f'{key}=\'{value}\'' for key, value in keys.items())
        summary = f'There is a constraint violation for the requested update {formatted_keys}.'
        super(UpdateViolation, self).__init__(status.BAD_REQUEST, summary)


class MissingCustomerIdException(FraudioServiceException):
    def __init__(self, user_id):
        summary = f'This operation requires a customer ID, but it has not been configured for user ID \'{user_id}\'.'
        super(MissingCustomerIdException, self).__init__(status.FORBIDDEN, summary)
