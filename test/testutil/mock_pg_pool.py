from contextlib import asynccontextmanager

from testutil.mock_pg_connection import MockPgConnection


class MockPgPool:
    def __init__(self, mock_connection: MockPgConnection):
        self.connection = mock_connection

    async def close(self):
        self.connection.reset()

    @asynccontextmanager
    async def acquire(self, *_):
        yield self.connection
