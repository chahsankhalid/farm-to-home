from dataclasses import dataclass

from <%my_service%>.serialization.serializable import Serializable


@dataclass
class HealthStatus(Serializable):
    status: str
    app_version: str
