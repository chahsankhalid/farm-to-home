from dataclasses import dataclass

from <%my_service%>.serialization.serializable import Serializable


@dataclass
class Message(Serializable):
    message: str
