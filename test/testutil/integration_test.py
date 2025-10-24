import asyncio
import functools
from typing import Callable

from httpx import AsyncClient

from <%my_service%>.middleware.fraudio_middleware import FraudioMiddleware
from <%my_service%>.util.paths import repository_path
from test.testutil import assertion, loadtestdata
from test.testutil.mock_kafka_producer import MockKafkaProducer

HTTP_TRANSACTION_KAFKA_TOPIC = 'fraudio-tst-env.fct.bronze.http-transactions.v0'


def integration_test(method: str,
                     url: str,
                     test_data_path: str,
                     response_code: int,
                     response_filename: str | None = None,
                     response_body: dict | None = None,
                     response_headers: dict | None = None,
                     request_filename: str | None = None,
                     request_headers: dict | None = None,
                     kafka_http_transaction_filename: str | None = None) -> Callable:
    def decorator_integration_test(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not 'api_client' in kwargs or not 'mock_kafka_producer' in kwargs:
                raise Exception(f'Missing some required decorator args in: {args}, {kwargs}')
            api_client: AsyncClient = kwargs['api_client']
            mock_kafka_producer: MockKafkaProducer = kwargs['mock_kafka_producer']

            func_result = await func(*args, **kwargs)
            headers = request_headers or {}
            body = loadtestdata.json_as_dict(_datapath(test_data_path, request_filename)) if request_filename else None
            response = await api_client.request(method, FraudioMiddleware.PATH_PREFIX + url, headers=headers, json=body)

            response_file_path = _datapath(test_data_path, response_filename)
            assertion.assert_json_response(response, response_code, response_body, response_file_path)

            if response_headers:
                expected_headers = {
                    k: loadtestdata.json_as_dict(_datapath(test_data_path, v)) if v[-5:] == '.json' else v
                    for k, v in response_headers.items()
                }
                assertion.assert_response_headers(response, expected_headers)

            await _test_http_transaction(mock_kafka_producer, test_data_path, kafka_http_transaction_filename)
            return func_result

        return wrapper

    return decorator_integration_test


async def _test_http_transaction(mock_kafka_producer: MockKafkaProducer,
                                 test_data_path: str,
                                 kafka_http_transaction_filename: str = None) -> None:
    if kafka_http_transaction_filename:
        events_file_path = _datapath_http_transactions(test_data_path, kafka_http_transaction_filename)
        expected_objects: list = loadtestdata.json_as_dict(events_file_path)
        await _receive_http_transactions()
        actual_objects = mock_kafka_producer.get(HTTP_TRANSACTION_KAFKA_TOPIC)
        assertion.assert_kafka_http_transaction_events(actual_objects, expected_objects)


async def _receive_http_transactions():
    http_transaction_tasks = [task for task in asyncio.all_tasks() if task.get_name() == 'save_http_transaction']
    has_tasks = len(http_transaction_tasks) > 0
    if has_tasks:
        await asyncio.wait(http_transaction_tasks)
    return has_tasks


def _datapath(test_data_path: str | None, filename: str | None) -> str | None:
    if test_data_path and filename:
        return str(repository_path.joinpath('test', 'testdata', test_data_path, filename))


def _datapath_http_transactions(test_data_path: str | None, filename: str | None) -> str | None:
    if test_data_path and filename:
        return _datapath(f'{test_data_path}/http_transactions', filename)
