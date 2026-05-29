from dataclasses import dataclass
from typing import Any

from insight_engine.serialization.serializable import Serializable


@dataclass
class CachedHashEntry(Serializable):
    result: Any
    cached_on: float
