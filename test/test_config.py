from <%my_service%>.config import ConfigLoader
from <%my_service%>.util import time

def test_correct_environment():
    cfg = ConfigLoader.get_instance()
    assert cfg.fraudio_env_display_name == 'Unit test'
    assert cfg.fraudio_kafka_servers == ['fakeserver1', 'fakeserver2']
    assert cfg.cached_table_freshness_check_interval_seconds == 10


def test_timezone_configuration(api_client):
    current_epoch = time.current_epoch_seconds()
    assert current_epoch == time.from_epoch_seconds(current_epoch).timestamp()
