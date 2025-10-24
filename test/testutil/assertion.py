import logging
import pprint

from httpx import Response

from <%my_service%>.config import ConfigLoader
from <%my_service%>.util.serdes import obj_to_json, json_to_obj
from test.testutil import loadtestdata

logger = logging.getLogger(__name__)
config = ConfigLoader.get_instance()
pp = pprint.PrettyPrinter(indent=4)


def assert_json_response(response: Response, status: int, response_body: dict | None = None,
                         response_file_path=None) -> None:
    if response.status_code != status:
        raw_body = response.text
        message = (
            '(no response body)' if raw_body is None
            else f'Expected HTTP {status}, got HTTP {response.status_code} with body {pp.pformat(raw_body)}'
        )
        assert response.status_code == status, logger.error(message)

    has_response = response_body is not None or response_file_path is not None
    if has_response:
        response_content_type = response.headers.get('Content-Type')
        assert response_content_type == 'application/json' or response_content_type == 'application/problem+json'
        actual_object = response.json()
        if response_file_path:
            assert isinstance(response_file_path, str)
            assert response_file_path[-5:] == '.json'
            response_body = loadtestdata.json_as_dict(response_file_path)
        if response_body is not None:
            expected_object = response_body
            assert actual_object == expected_object, logger.error(f'Actual:\n{obj_to_json(actual_object)}')


def assert_response_headers(response: Response, response_headers: dict | None = None) -> None:
    for header_key, header_value in response_headers.items():
        actual_value = response.headers.get(header_key, '')
        if type(header_value) == dict:
            actual_object = json_to_obj(actual_value)
            assert actual_object == header_value, logger.error(f'Actual:\n{actual_value}')
        else:
            assert actual_value == header_value, logger.error(f'Actual:\n{actual_value}')


def assert_kafka_events(events: dict, events_file_path=None) -> None:
    if events_file_path is None:
        assert len(events) == 0
    else:
        expected_object = loadtestdata.json_as_dict(events_file_path)
        assert events == expected_object, logger.error(f'Actual:\n{obj_to_json(event)}')


def assert_kafka_http_transaction_events(actual_objects: list, expected_objects: list) -> None:
    # Zip allows uneven lists, it just truncates them
    for actual_object, expected_object in zip(actual_objects, expected_objects):
        actual: dict = actual_object['value'].copy()
        expected: dict = expected_object['value'].copy()

        environment = config.fraudio_env
        assert actual.get('environment') == environment

        fields_to_drop = ['environment', 'id', 'latency']

        for f in fields_to_drop:
            actual.pop(f)
            expected.pop(f)

        assert actual == expected, logger.error(f'Actual:\n{obj_to_json(actual)}')

    # These assertions allow failing the test if there are any additional unmatched items on either side
    actually_unexpected = actual_objects[len(expected_objects):]
    assert actually_unexpected == [], logger.error(f'Actual:\n{obj_to_json(actually_unexpected)}')
    actually_missing = expected_objects[len(actual_objects):]
    assert [] == actually_missing
