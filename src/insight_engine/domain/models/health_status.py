from dataclasses import dataclass

from insight_engine.serialization.serializable import Serializable


@dataclass
class HealthStatus(Serializable):
    status: str
    app_version: str
