import logging
from datetime import timedelta, datetime
from threading import RLock
from uuid import UUID

from marshmallow.exceptions import ValidationError
from orjson import JSONDecodeError

from <%my_service%>.config import ConfigLoader
from <%my_service%>.domain.models.credentials import Credentials
from <%my_service%>.util import time
from <%my_service%>.util.serdes import json_to_obj

logger = logging.getLogger(__name__)
config = ConfigLoader.get_instance()
migrate_lock = RLock()


# Called by Connexion. Handles the X-Fraudio-Credentials header.
async def x_fraudio_credentials(header_value):
    if header_value is None or header_value == '':
        return None
    else:
        try:
            credentials_dict = json_to_obj(header_value)
            credentials = Credentials.from_dict(credentials_dict)
            customer = credentials.customer
            if credentials.expires_on and credentials.expires_on <= time.current_datetime():
                logger.error(f'An X-Fraudio-Credentials header was already expired for customer "{customer}"!')
                return None
            else:
                logger.debug(f'The X-Fraudio-Credentials header was parsed successfully for customer "{customer}".')
                return credentials.to_dict()
        except JSONDecodeError as e:
            logger.warning(f'Error parsing X-Fraudio-Credentials header json: {e}.')
            return None
        except ValidationError as e:
            logger.warning(f'Error parsing X-Fraudio-Credentials header json: {e}.')
            return None
        except TypeError as e:
            logger.warning(f'Error parsing X-Fraudio-Credentials header as a Credentials object: {e}.')
            return None
        except Exception as e:
            logger.warning('Unexpected error processing X-Fraudio-Credentials header: %s', e, exc_info=True)
            logger.debug(header_value)
            return None
