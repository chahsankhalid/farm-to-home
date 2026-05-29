import logging

from insight_engine.util import paths

logger = logging.getLogger(__name__)


def fetch_version() -> str:
    version_file_path = paths.repository_path.joinpath('VERSION')
    with open(version_file_path, 'r') as f:
        return f.readline().strip()


version = fetch_version()
