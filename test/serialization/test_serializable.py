from uuid import UUID

from insight_engine.domain.models.credentials import Credentials
from insight_engine.util import time

from insight_engine.domain.models.enums import ApiMode, OnboardingStage


async def test_serializable_datetimes():
    sample_credentials = _sample_credentials()
    record = sample_credentials.to_dict()
    assert Credentials.from_dict(record) == sample_credentials


async def test_serializable_datetimes_from_sql_record():
    sample_credentials = _sample_credentials()
    record = sample_credentials.to_native_dict()
    assert Credentials.from_native_dict(record) == sample_credentials


def _sample_credentials():
    return Credentials(
        user_id=UUID('00000000000000000000000000000001', version=4),
        tenant_id=UUID('00000000000000000000000000000002', version=4),
        api_key_id=UUID('00000000000000000000000000000003', version=4),
        scopes=['abc', 'def-geh'],
        username='user@example.com',
        api_key_fingerprint='a1b2c3d',
        tenant='sometenant',
        customer='sometenant-test-trial',
        tenant_ancestors=['fraudio', 'supertenant'],
        tenant_descendants={
            'subtenant1': {'subsubtenant': {}},
            'subtenant2': {}
        },
        onboarding_stage=OnboardingStage.INTEGRATING,
        api_mode=ApiMode.SANDBOX,
        expires_on=time.current_datetime()
    )
