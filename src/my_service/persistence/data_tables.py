import asyncio
import logging

from <%my_service%>.config import ConfigLoader
from <%my_service%>.persistence.data_table import DataTable

logger = logging.getLogger(__name__)
config = ConfigLoader.get_instance()


class DataTables:
    def __init__(self):
        self.refresh_task = None
        self.data_tables = {}
        self.cached_table_names = set(config.cached_tables)

    def get(self, table_name: str) -> DataTable | None:
        if table_name not in self.data_tables:
            self.data_tables[table_name] = DataTable(table_name,
                                                     cache_in_memory=(table_name in self.cached_table_names))
        return self.data_tables.get(table_name, None)

    async def force_refresh(self):
        for table_name, data_table in self.data_tables.items():
            if table_name in self.cached_table_names:
                await data_table.refresh()

    async def request_refresh(self) -> float:
        num_refresh_requests = 0
        num_requests_honored = 0
        for table_name, data_table in self.data_tables.items():
            if table_name in self.cached_table_names:
                num_refresh_requests += 1
                num_requests_honored += await data_table.request_refresh()
        return num_requests_honored

    async def periodic_refresh(self):
        while True:
            await asyncio.sleep(config.cached_table_freshness_check_interval_seconds)
            for table_name, data_table in self.data_tables.items():
                if table_name in self.cached_table_names:
                    await data_table.refresh_if_stale()

    async def async_setup(self):
        await self.force_refresh()
        self.refresh_task = asyncio.get_event_loop().create_task(self.periodic_refresh())

    async def async_teardown(self):
        if self.refresh_task:
            self.refresh_task.cancel()


data_tables = DataTables()
