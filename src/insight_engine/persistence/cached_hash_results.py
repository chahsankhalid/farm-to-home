import asyncio
import hashlib
import logging
from typing import Any

from insight_engine.config import ConfigLoader
from insight_engine.persistence.cached_hash_entry import CachedHashEntry
from insight_engine.util import time

logger = logging.getLogger(__name__)
config = ConfigLoader.get_instance()


class CachedHashResults:
    def __init__(self):
        self.hashes: dict[str, CachedHashEntry] = {}
        self.refresh_task = None

    async def async_setup(self):
        self.refresh_task = asyncio.get_event_loop().create_task(self._clear_expired_entries())

    async def async_teardown(self):
        if self.refresh_task:
            self.refresh_task.cancel()

    def get(self, key: str, refresh_retention: bool = False) -> Any | None:
        secure_key = CachedHashResults._secure_key(key)
        current_time = time.current_epoch_seconds()
        if secure_key in self.hashes:
            hash_entry = self.hashes[secure_key]
            if refresh_retention:
                hash_entry.cached_on = current_time
                return hash_entry.result
            elif self._check_freshness(secure_key, hash_entry, time.current_epoch_seconds()):
                return hash_entry.result
            else:
                return None
        else:
            return None

    def set(self, key: str, result: Any):
        secure_key = CachedHashResults._secure_key(key)
        current_time = time.current_epoch_seconds()
        self.hashes[secure_key] = CachedHashEntry(result, current_time)

    async def _clear_expired_entries(self):
        while True:
            await asyncio.sleep(config.cached_hash_freshness_check_interval_seconds)
            current_time = time.current_epoch_seconds()
            for cache_key, cached_entry in self.hashes.items():
                self._check_freshness(cache_key, cached_entry, current_time)

    def _check_freshness(self, secure_key: str, hash_entry: CachedHashEntry, current_time: float) -> bool:
        is_fresh = current_time - hash_entry.cached_on <= config.cached_hash_retention_seconds
        if not is_fresh:
            self.hashes.pop(secure_key)  # Expire entry
        return is_fresh

    # A dict is usually already a hashmap, so normally there is no need to hash keys again.
    # We do hash it here, using a fast hash algorithm, so that we don't have to store the plain text keys in memory.
    @staticmethod
    def _secure_key(key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()


cached_hash_results = CachedHashResults()
