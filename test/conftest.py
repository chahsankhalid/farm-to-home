from datetime import timedelta
from typing import AsyncGenerator, Any
from uuid import UUID

import pytest
from connexion import AsyncApp
from httpx import AsyncClient, ASGITransport

from insight_engine import app
from insight_engine.domain.models.credentials import Credentials
from insight_engine.domain.models.enums import OnboardingStage, ApiMode
from insight_engine.persistence.kafka_streaming import kafka_streaming
from insight_engine.util import time
from insight_engine.util.serdes import obj_to_json
from test.testutil.mock_kafka_producer import MockKafkaProducer
from test.testutil.mock_kafka_schema_registry import MockKafkaSchemaRegistry
from test.testutil.mocking import Mocking


@pytest.fixture(scope='session', autouse=True)
async def _mock_kafka_producer() -> MockKafkaProducer:
    return MockKafkaProducer()


@pytest.fixture(scope='session', autouse=True)
async def _mock_kafka_schema_registry() -> MockKafkaSchemaRegistry:
    return MockKafkaSchemaRegistry()

@pytest.fixture(scope='session', autouse=True)
async def testapp(
    _mock_kafka_producer: MockKafkaProducer,
    _mock_kafka_schema_registry: MockKafkaSchemaRegistry
) -> AsyncGenerator[AsyncApp, Any]:
    testapp: AsyncApp = app.create_app()

    # For some reason, the lifespan handler is not called automatically in test scope
    async with app.lifespan_handler(testapp.middleware):
        kafka_streaming.setup(None, _mock_kafka_producer, _mock_kafka_schema_registry)
        yield testapp


@pytest.fixture(scope='function', autouse=True)
async def mock_kafka_producer(_mock_kafka_producer: MockKafkaProducer) -> MockKafkaProducer:
    _mock_kafka_producer.reset()
    return _mock_kafka_producer

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
