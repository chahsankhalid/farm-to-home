import logging
from threading import RLock
from typing import Any, Type, TypeVar, Iterator, Callable, Coroutine

from asyncpg import Record

from <%my_service%>.config import ConfigLoader
from <%my_service%>.domain.models.query_filters import QueryFilter
from <%my_service%>.persistence.postgres_connector import db
from <%my_service%>.serialization.serializable import Serializable
from <%my_service%>.util import time

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=Serializable)
refresh_lock = RLock()
config = ConfigLoader.get_instance()


class DataTable:
    def __init__(self, table_name: str, cache_in_memory: bool = False):
        self.table_name = table_name
        self.is_cached = cache_in_memory
        self.cached_rows = []  # Stored in native format (e.g. datetime objects, Enum instances)
        self.is_refresh_requested = True
        self.t_latest_refresh = 0

    async def refresh(self):
        """Pull new data from the database and replaces the previously cached data"""
        self._require_caching()
        self.is_refresh_requested = True
        with refresh_lock:  # Only one thread may refresh a full table at the same time
            if self.is_refresh_requested:  # In case another thread already refreshed it
                logger.debug(f'Refreshing cache for table {self.table_name}...')
                all_records: list[Record] = await db.fetch_many(f'SELECT * FROM {self.table_name}')
                self.cached_rows = [dict(record) for record in all_records]
                self.is_refresh_requested = False
                self.t_latest_refresh = time.current_epoch_seconds()
                logger.debug(f'Refreshed cache for table {self.table_name}, there were {len(self.cached_rows)} rows')

    async def refresh_if_stale(self) -> bool:
        """Refresh the table only if it is stale according to latest refresh, configuration and requested refreshes"""
        self._require_caching()
        is_stale = self._is_stale()
        if is_stale:
            await self.refresh()
        return is_stale

    async def request_refresh(self) -> bool:
        """
        May be used to suggest that a refresh is desirable, e.g. in case of an unknown token. If the minimal refresh
        interval has passed, the refresh happens immediately. Otherwise, the refresh is scheduled for the next interval.
        This allows a request with an unknown token to trigger a refresh, but prevents repeated bad request from
        continuously re-triggering refreshes.
        If no refresh is requested, the table is refreshed periodically accoring to the maximal refresh interval.
        """
        self._require_caching()
        logger.debug(f'Requested refresh of table {self.table_name}')
        self.is_refresh_requested = True
        return await self.refresh_if_stale()

    async def all(self, cls: Type[T], from_cache: bool = False, **keys: Any) -> list[T]:
        if from_cache:
            return list(self._select_from_cache(cls, **keys))
        else:
            key_clauses, parameter_values = DataTable._key_values_clause(**keys)
            clause = ' AND '.join(key_clauses) or 'TRUE'
            records = await db.fetch_many(f'SELECT * FROM {self.table_name} WHERE {clause}', *parameter_values)
            rows = [dict(record) for record in records]
            return [cls.from_native_dict(row) for row in rows]

    async def one_by_key(self, cls: Type[T], from_cache: bool = False, **keys: Any) -> T | None:
        if from_cache:
            return next(self._select_from_cache(cls, **keys), None)
        else:
            key_clauses, parameter_values = DataTable._key_values_clause(**keys)
            clause = ' AND '.join(key_clauses) or 'TRUE'
            query = f'SELECT * FROM {self.table_name} WHERE {clause} LIMIT 1'
            record = await db.fetch_one(query, *parameter_values)
            return cls.from_native_dict(dict(record)) if record else None

    async def add(self, dto: Serializable) -> bool:
        dto_dict = dto.to_native_dict()
        columns, values = zip(*dto_dict.items()) if len(dto_dict) else ([], [])
        columns_str = ', '.join(columns)
        placeholders = ', '.join(f'${i + 1}' for i in range(len(values)))

        query = f'INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})'
        rows_inserted = await db.execute(query, *values)
        if rows_inserted == 1:
            logger.debug(f'Inserted a new row into table {self.table_name}')
            if self.is_cached:
                self.cached_rows.append(dto_dict)
            return True
        else:
            logger.warning(f'Expected 1 new row in table {self.table_name}, but {rows_inserted} rows were inserted')
            return False

    def update(self, **keys: Any) -> Callable[..., Coroutine[Any, Any, bool]]:
        async def with_values(**updates: Any) -> bool:
            if not keys or not updates:
                return False

            update_clauses, update_values = DataTable._key_values_clause(operator='=', **updates)
            update_clause = ', '.join(update_clauses)

            match_clauses, match_values = DataTable._key_values_clause(param_offset=len(update_values), **keys)
            match_clause = ' AND '.join(match_clauses)

            query = f'UPDATE {self.table_name} SET {update_clause} WHERE {match_clause}'
            rows_updated = await db.execute(query, *(update_values + match_values))
            if rows_updated == 1:
                logger.debug(f'Updated a row in table {self.table_name}')
                if self.is_cached:
                    # It's too tricky and unnecessary to attempt to do in-memory updates.
                    # When this happens, just refresh the whole table.
                    await self.request_refresh()
                return True
            else:
                logger.debug(f'There were {rows_updated} updated rows in table {self.table_name}')
                return False

        return with_values

    def _select_from_cache(self, cls: Type[T], **keys: Any) -> Iterator[T]:
        self._require_caching()
        return (
            cls.from_native_dict(row)
            for row in self.cached_rows
            if all(
            (
                row[key] in value if type(value) in [list, tuple]
                else value.accepts(row[key]) if isinstance(value, QueryFilter)
                else row[key] == value
            )
            for key, value in keys.items()
        ))

    def _is_stale(self):
        t_now = time.current_epoch_seconds()
        dt = t_now - self.t_latest_refresh
        return dt > config.cached_table_refresh_interval_max_seconds or (
                dt > config.cached_table_refresh_interval_min_seconds and self.is_refresh_requested
        )

    def _require_caching(self):
        if not self.is_cached:
            raise Exception(f'Table {self.table_name} is not marked as cached, but a cache refresh was requested.')

    @staticmethod
    def _key_values_clause(param_offset: int = 0, operator: str | None = None, **keys: Any) -> (list[str], list[Any]):
        key_clauses = []
        parameter_values = []
        next_param_num = 1
        for index, (key, value) in enumerate(keys.items()):
            if value is None:
                if operator:
                    key_clauses.append(f'{key} {operator} NULL')
                else:
                    key_clauses.append(f'{key} IS NULL')
            elif isinstance(value, QueryFilter):
                key_clause, num_value_clauses = value.to_sql_clause(key, next_param_num)
                key_clauses.append(key_clause)
                next_param_num += num_value_clauses
                for _ in range(num_value_clauses):
                    parameter_values.append(value.value)
            else:
                param_arg = f'${next_param_num + param_offset}'
                next_param_num += 1
                if type(value) in {list, tuple}:
                    if operator:
                        key_clauses.append(f'{key} {operator} {param_arg}')
                    else:
                        key_clauses.append(f'{key} = ANY({param_arg})')
                    parameter_values.append(set(value))
                else:
                    # Use null-safe operator by default
                    op = operator or '='
                    key_clauses.append(f'{key} {op} {param_arg}')
                    parameter_values.append(value)
        return key_clauses, parameter_values
