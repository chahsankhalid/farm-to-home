import asyncio
import contextvars
import logging
import uuid
from typing import Callable, Awaitable

from starlette.concurrency import run_in_threadpool, iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from <%my_service%>.config import ConfigLoader
from <%my_service%>.domain.models.credentials import Credentials
from <%my_service%>.domain.models.http_transaction import HttpTransaction
from <%my_service%>.persistence import http_transaction_log
from <%my_service%>.serialization import errors
from <%my_service%>.util import time, yaml

logger = logging.getLogger(__name__)
api_spec = yaml.yaml_file_to_dict('openapi', 'api-spec.yaml')
request_credentials = contextvars.ContextVar('request_credentials')

class FraudioMiddleware(BaseHTTPMiddleware):
    HEADERS_TO_REMOVE = ['authorization', 'cookie', 'cookies', 'x-fraudio-credentials']
    PATH_PREFIX = api_spec['servers'][0]['url']
    WHITELISTED_URLS = {'/'}
    WHITELISTED_URL_PREFIXES = ('/example-error', '/docs', '/echo', '/healthz')
    REDACT_BODY_URL_SUFFIXES = ()

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.current_epoch_seconds()
        request_path = request.url.path

        response = None
        problem = None

        if self._is_whitelisted_path(request_path):
            logger.debug(f'Path {request_path} is whitelisted, request will not be audited.')
            try:
                response = await call_next(request)
            except Exception as ex:
                problem = errors.handle_api_exception(None, ex)
        else:
            logger.debug(f'Processing request at path {request_path}...')
            config = ConfigLoader.get_instance()
            request_headers = self._filter_headers(dict(request.headers), self.HEADERS_TO_REMOVE)

            if not self._is_body_redacted_for_path(request_path) and (
                    ('content-length' in request.headers and request.headers['content-length'] != '0') or
                    'transfer-encoding' in request.headers
            ):
                # The request body must be read before the request is handled by the receiving endpoint.
                # Doing it here means it is automatically cached for the next read.
                try:
                    request_body_bytes = await asyncio.wait_for(request.body(), timeout=0.1)
                    request_body = None if len(request_body_bytes) == 0 else request_body_bytes.decode()
                except asyncio.TimeoutError:
                    logger.warning(f'Timeout at {request_path} while retrieving request body for audit trail!')
                    request_body = None
            else:
                request_body = None

            # Call the next middleware
            try:
                logger.debug(f'Hand-over to next middleware in the chain')
                response = await call_next(request)
                logger.debug(f'Got response from next middleware in the chain')
            except Exception as ex:
                logger.debug(f'Got error from next middleware in the chain')
                problem = errors.handle_api_exception(None, ex)

            # Extract request metrics
            request_method = request.method
            request_url = str(request.url)
            request_ip = request.client.host
            end_time = time.current_epoch_seconds()
            request_latency = time.get_request_time(start_time, end_time)

            request_auth_method = (
                'credentials' if len(request.headers.get('x-fraudio-credentials', '')) > 0 else
                None
            )

            raw_credentials = request.scope.get('extensions', {}).get('connexion_context', {}).get('token_info')
            credentials: Credentials | None = (
                Credentials.from_dict(raw_credentials)
                if raw_credentials
                else None
            )

            if response is None:
                if problem is None:
                    raise Exception(f'Programmer error in middleware: found neither an HTTP response nor a problem.')
                else:
                    response_status_code = problem.status_code  # Unfortunately not yet nullable in Kafka
                    response_headers = self._filter_headers(dict(problem.headers), self.HEADERS_TO_REMOVE)
                    response_body = problem.body
            else:
                response_status_code = str(response.status_code)
                response_headers = self._filter_headers(dict(response.headers), self.HEADERS_TO_REMOVE)

                if not self._is_body_redacted_for_path(request_path) and (
                        ('content-length' in response.headers and response.headers['content-length'] != '0')
                        or 'transfer-encoding' in response.headers
                ):
                    # Peek at the response body, store it in memory and create a new iterator to be consumed by others
                    response_body_chunks = [chunk async for chunk in response.body_iterator]
                    response_body = b''.join(response_body_chunks).decode()
                    response.body_iterator = iterate_in_threadpool(iter(response_body_chunks))
                else:
                    response_body = None

            customer_field_value = None if credentials is None else credentials.customer
            user_id = None if credentials is None else str(credentials.user_id)
            logger.info(
                f'Request by {customer_field_value} to {request_method} {request.url} - HTTP {response_status_code}'
            )

            http_transaction = HttpTransaction(
                id=str(uuid.uuid4()),
                request_method=request_method,
                request_url=request_url,
                environment=config.fraudio_env,
                response_status_code=response_status_code,
                latency=request_latency,
                token_type=request_auth_method,
                request_headers=request_headers,
                request_body=request_body,
                response_headers=response_headers,
                response_body=response_body,
                customer=customer_field_value,
                ip=request_ip,
                user_id=user_id
            )
            # Intentionally save this in a background task, so as not to hold up the response
            # noinspection PyAsyncCall
            asyncio.get_event_loop().create_task(
                run_in_threadpool(http_transaction_log.save_http_transaction, http_transaction),
                name='save_http_transaction'
            )

        if problem:
            return Response(
                content=problem.body,
                status_code=problem.status_code,
                headers=problem.headers,
                media_type=problem.content_type
            )
        else:
            return response

    @staticmethod
    def _filter_headers(headers: dict, to_remove: list[str]) -> dict:
        return {k: v for k, v in headers.items() if k.lower() not in to_remove}

    @staticmethod
    def _is_whitelisted_path(request_path: str):
        path = request_path.replace(FraudioMiddleware.PATH_PREFIX, "")
        return path.startswith(FraudioMiddleware.WHITELISTED_URL_PREFIXES) or \
            path in FraudioMiddleware.WHITELISTED_URLS or \
            len(path) == 0

    @staticmethod
    def _is_body_redacted_for_path(request_path: str):
        path = request_path.replace(FraudioMiddleware.PATH_PREFIX, "")
        return path.endswith(FraudioMiddleware.REDACT_BODY_URL_SUFFIXES)
