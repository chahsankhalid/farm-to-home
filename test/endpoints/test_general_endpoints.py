from <%my_service%>.domain import api_info
from test.testutil.integration_test import integration_test

TEST_DATA_PATH = 'general'


@integration_test(
    method='GET',
    url='/',
    test_data_path=TEST_DATA_PATH,
    response_filename='welcome-1-response.json',
    response_code=200,
    request_headers={'X-Fraudio-Credentials': ''},
    kafka_http_transaction_filename='zero_records.json')
async def test_welcome(api_client, mock_kafka_producer):
    pass


@integration_test(
    method='GET',
    url='/healthz',
    test_data_path=TEST_DATA_PATH,
    response_code=200,
    response_body={'status': 'Healthy', 'app_version': api_info.fetch_version()},
    request_headers={'X-Fraudio-Credentials': ''},
    kafka_http_transaction_filename='zero_records.json')
async def test_welcome(api_client, mock_kafka_producer):
    pass


@integration_test(
    method='GET',
    url='/example-error',
    test_data_path=TEST_DATA_PATH,
    response_filename='error-duplicate-response.json',
    response_code=400,
    request_headers={'X-Fraudio-Credentials': ''},
    kafka_http_transaction_filename='zero_records.json')
async def test_error_duplicate(api_client, mock_kafka_producer):
    pass


@integration_test(
    method='GET',
    url='/example-error/internal',
    test_data_path=TEST_DATA_PATH,
    response_filename='error-internal-response.json',
    response_code=500,
    kafka_http_transaction_filename='zero_records.json')
async def test_error_internal(api_client, mock_kafka_producer):
    pass


@integration_test(
    method='GET',
    url='/example-error/forbidden',
    test_data_path=TEST_DATA_PATH,
    response_filename='forbidden-response.json',
    response_code=403,
    kafka_http_transaction_filename='zero_records.json')
async def test_forbidden(api_client, mock_kafka_producer):
    pass


@integration_test(
    method='POST',
    url='/echo',
    test_data_path=TEST_DATA_PATH,
    request_filename='echo-1-request.json',
    response_filename='echo-1-response.json',
    response_code=200,
    request_headers={'X-Fraudio-Credentials': ''},
    kafka_http_transaction_filename='zero_records.json')
async def test_echo(api_client, mock_kafka_producer):
    pass
