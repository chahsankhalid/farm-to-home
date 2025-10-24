from datetime import timedelta
from typing import AsyncGenerator, Any
from uuid import UUID

import pytest
from connexion import AsyncApp
from httpx import AsyncClient, ASGITransport

from <%my_service%> import app
from <%my_service%>.domain.models.credentials import Credentials
from <%my_service%>.domain.models.enums import OnboardingStage, ApiMode
from <%my_service%>.persistence.data_tables import data_tables
from <%my_service%>.persistence.kafka_streaming import kafka_streaming
from <%my_service%>.persistence.postgres_connector import db
from <%my_service%>.util import time
from <%my_service%>.util.serdes import obj_to_json
from test.testutil.mock_kafka_producer import MockKafkaProducer
from test.testutil.mock_kafka_schema_registry import MockKafkaSchemaRegistry
from test.testutil.mock_pg_connection import MockPgConnection
from test.testutil.mock_pg_pool import MockPgPool
from test.testutil.mocking import Mocking


@pytest.fixture(scope='session', autouse=True)
async def _mock_kafka_producer() -> MockKafkaProducer:
    return MockKafkaProducer()


@pytest.fixture(scope='session', autouse=True)
async def _mock_kafka_schema_registry() -> MockKafkaSchemaRegistry:
    return MockKafkaSchemaRegistry()


@pytest.fixture(scope='session', autouse=True)
async def _mock_pg_pool() -> MockPgPool:
    pg_connection = MockPgConnection()
    pg_pool = MockPgPool(pg_connection)
    return pg_pool


@pytest.fixture(scope='session', autouse=True)
async def testapp(_mock_kafka_producer: MockKafkaProducer,
                  _mock_kafka_schema_registry: MockKafkaSchemaRegistry,
                  _mock_pg_pool: MockPgPool) -> AsyncGenerator[AsyncApp, Any]:
    testapp: AsyncApp = app.create_app()
    # For some reason, the lifespan handler is not called automatically in test scope
    async with app.lifespan_handler(testapp.middleware):
        kafka_streaming.setup(None, _mock_kafka_producer, _mock_kafka_schema_registry)
        await db.async_setup(_mock_pg_pool)
        yield testapp
        await db.async_teardown()


@pytest.fixture(scope='function', autouse=True)
async def mock_kafka_producer(_mock_kafka_producer: MockKafkaProducer) -> MockKafkaProducer:
    _mock_kafka_producer.reset()
    return _mock_kafka_producer


@pytest.fixture(scope='function', autouse=True)
async def mock_pg_connection(_mock_pg_pool: MockPgPool) -> MockPgConnection:
    connection = _mock_pg_pool.connection
    connection.reset()
    await data_tables.force_refresh()
    return connection


@pytest.fixture(scope='function')
async def _mocking() -> Mocking:
    return Mocking()


@pytest.fixture(scope='function')
async def api_client(_mocking: Mocking, testapp: AsyncApp) -> AsyncGenerator[AsyncClient, Any]:
    current_time = time.current_datetime()
    credentials_expire_on = current_time + timedelta(seconds=300)

    transport = ASGITransport(app=testapp)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        client.headers.setdefault('X-Fraudio-Credentials', obj_to_json(Credentials(
            UUID('00000000000000000000000000000001', version=4),
            UUID('00000000000000000000000000000100', version=4),
            UUID('00000000000000000000000000010000', version=4),
            [
                'common.general.read',
                'common.customers.read',
                'common.keys.read',
                'common.customers.create',
                'common.tokens.create'
            ],
            'g.josquin@fraudio.com',
            'a1b2c3d',
            'mytenant',
            'mytenant-test-trial',
            [],
            {},
            OnboardingStage.INTEGRATING,
            ApiMode.SANDBOX,
            credentials_expire_on
        ).to_dict()))
        yield client
