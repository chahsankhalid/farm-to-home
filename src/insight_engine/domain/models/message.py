from dataclasses import dataclass

from insight_engine.serialization.serializable import Serializable


@dataclass
class Message(Serializable):
    message: str
