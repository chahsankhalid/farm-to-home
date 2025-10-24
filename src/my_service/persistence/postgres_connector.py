import logging
from datetime import datetime
from enum import Enum
from functools import partial
from typing import Callable, Any

import asyncpg
import asyncpg_trek
import asyncpg_trek.asyncpg
from asyncpg import Connection
from asyncpg.connection import LoggedQuery

from <%my_service%>.config import ConfigLoader
from <%my_service%>.domain.models.enums import ApiMode, HashType, RecordStatus, LoginType, OnboardingStage
from <%my_service%>.persistence import migrations
from <%my_service%>.util import paths, time

logger = logging.getLogger(__name__)
config = ConfigLoader.get_instance()


class PostgresConnector:
    def __init__(self):
        self.enabled = False
        self.pool = None

    async def async_setup(self, pool: asyncpg.pool.Pool = None):
        host = config.fraudio_postgres_host
        logger.info(f'Attempting to connect to Postgres DB at {host}...')
        self.pool = pool or await asyncpg.create_pool(
            host=host,
            port=config.fraudio_postgres_port,
            database=config.fraudio_postgres_database,
            user=config.fraudio_postgres_user,
            password=config.fraudio_postgres_password,
            init=PostgresConnector._init_connection,
            min_size=config.fraudio_postgres_min_connections,
            max_size=config.fraudio_postgres_max_connections
        )
        await self._migrate()
        self.enabled = True

    async def async_teardown(self):
        if self.enabled:
            await self.pool.close()
            self.enabled = False

    async def _migrate(self) -> None:
        script_dir = paths.app_path.joinpath('persistence').joinpath('migrations')
        target_revision = migrations.target_revision
        logger.debug(f'Migrating Postgres schema to {target_revision}...')
        async with self.pool.acquire() as connection:
            backend = asyncpg_trek.asyncpg.AsyncpgBackend(connection)
            async with backend.connect():
                try:
                    plan = await asyncpg_trek.plan(backend, script_dir, target_revision, asyncpg_trek.Direction.up)
                    logger.debug(f'Migration direction UP to {target_revision}...')
                except LookupError as _:
                    plan = await asyncpg_trek.plan(backend, script_dir, target_revision, asyncpg_trek.Direction.down)
                    logger.debug(f'Migration direction DOWN to {target_revision}...')
                await asyncpg_trek.execute(backend, plan)
                logger.debug(f'Migrated Postgres schema to {target_revision}.')

    async def fetch_one(self, query: str, *args: Any) -> Any | None:
        return await self._run(query, *args, method=lambda conn: partial(conn.fetchrow))

    async def fetch_many(self, query: str, *args: Any) -> list[Any]:
        return (await self._run(query, *args, method=lambda conn: partial(conn.fetch))) or []

    async def fetch_value(self, query: str, *args: Any) -> Any | None:
        return await self._run(query, *args, method=lambda conn: partial(conn.fetchval))

    async def execute(self, query: str, *args: Any) -> int:
        result = await self._run(query, *args, method=lambda conn: partial(conn.execute))
        parts = result.split(' ')
        if len(parts) == 3 and parts[0] == 'INSERT' and parts[2].isnumeric():
            return int(parts[2])
        elif len(parts) == 2 and parts[0] == 'UPDATE' and parts[1].isnumeric():
            return int(parts[1])
        else:
            logger.warning(f'Unexpected result after {parts[0]} query: "{result}"')

    async def _run(self, query: str, *args: Any, method: Callable[[Connection], Callable]) -> Any:
        if not self.enabled:
            logger.debug('DB skipped: Postgres connector is not initialized.')
            return
        async with self.pool.acquire() as connection:
            # Use logger.debug directly rather than add_query_logger, to avoid logging system calls
            logger.debug(f'Running DB query: [{query}] {args}')
            result = await method(connection)(query, *args)
            return result

    @staticmethod
    async def _init_connection(connection):
        connection.add_query_logger(PostgresConnector._log_query_exceptions)
        await connection.set_type_codec('timestamp',
                                        schema='pg_catalog',
                                        format='binary',
                                        encoder=PostgresConnector._encode_timestamp,
                                        decoder=PostgresConnector._decode_timestamp)
        enum_mapping = {
            'api_mode': ApiMode,
            'hash_type': HashType,
            'record_status': RecordStatus,
            'login_type': LoginType,
            'onboarding_stage': OnboardingStage
        }
        for pg_enum_name, py_enum in enum_mapping.items():
            try:
                await connection.set_type_codec(pg_enum_name,
                                                encoder=PostgresConnector._encode_enum,
                                                decoder=partial(PostgresConnector._decode_enum, py_enum))
            except ValueError:
                logger.warning(f'Codec could not be created, enum not found in database: {pg_enum_name}')

    @staticmethod
    def _log_query_exceptions(logged_query: LoggedQuery):
        query_exception = logged_query.exception
        elapsed_seconds = logged_query.elapsed
        if query_exception:
            logger.info(f'Query exception: {query_exception}')
        elif elapsed_seconds > 0.5:
            logger.debug(f'Query took longer than 500ms!')

    @staticmethod
    def _encode_enum(v):
        return v.value if isinstance(v, Enum) else v

    @staticmethod
    def _decode_enum(construct, v):
        return construct(v)

    @staticmethod
    def _encode_timestamp(v):
        # The switch case is necessary for PATCH requests,
        #   where the body is not first converted to a typed object, but directly applied
        epoch_seconds: float = (
            v if isinstance(v, float) else
            v.timestamp() if isinstance(v, datetime) else
            v
        )
        return int((epoch_seconds - 946684800) * 1_000_000).to_bytes(8, byteorder='big')

    @staticmethod
    def _decode_timestamp(v):
        return time.from_epoch_seconds(int.from_bytes(v, byteorder='big') / 1_000_000 + 946684800)


db = PostgresConnector()
