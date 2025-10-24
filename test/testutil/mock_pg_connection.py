import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)


class MockPgConnection:

    def __init__(self):
        self.tables = defaultdict(lambda: [])

    def reset(self):
        self.tables.clear()

    async def fetch(self, query: str, *args: Any) -> list[Any]:
        prefix = 'SELECT * FROM '
        if query.startswith(prefix):
            remaining_query = query[len(prefix):]
            table_name, _, _ = remaining_query.partition(' ')
            rows = self.tables[table_name]
            return rows
        else:
            return []

    async def fetchrow(self, query: str, *args: Any) -> Any | None:
        rows = await self.fetch(query, *args)
        return rows[0] if rows else None

    async def fetchval(self, query: str, *args: Any) -> Any | None:
        return None

    async def execute(self, query: str, *args: Any) -> str:
        if query.startswith('INSERT '):
            return 'INSERT 0 1'
        else:
            return 'UPDATE 1'

    # noinspection PyUnusedLocal
    @asynccontextmanager
    async def transaction(self, isolation: str):
        yield

    def add_query_logger(self, callback):
        return
