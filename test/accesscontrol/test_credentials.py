from insight_engine.accesscontrol.credentials import x_fraudio_credentials


async def test_invalid_input_returns_none():
    assert await x_fraudio_credentials('') is None
    assert await x_fraudio_credentials('[]') is None
    assert await x_fraudio_credentials('{}') is None
    assert await x_fraudio_credentials('{\"fake\":\"data\"}') is None
