import os

import pytest
from <%my_service%>.util.paths import app_name

os.environ['FRAUDIO_ENV'] = 'UNITTEST'

# This overriddes a config value to verify that environment variable substitution works
os.environ[f'{app_name().upper()}_FRAUDIO_KAFKA_SERVERS'] = 'fakeserver1,fakeserver2'
os.environ[f'{app_name().upper()}_CACHED_TABLE_FRESHNESS_CHECK_INTERVAL_SECONDS'] = '10'

pytest.register_assert_rewrite('testutil.assertion')
