from dataclasses import dataclass

from <%my_service%>.serialization.serializable import Serializable


@dataclass
class Password(Serializable):
    password: str
