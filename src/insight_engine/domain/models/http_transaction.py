from dataclasses import dataclass, field

from insight_engine.serialization.serializable import Serializable
from insight_engine.util.serdes import convert_dict_values_types, dict_keys_snake_to_camel


@dataclass
class HttpTransaction(Serializable):
    id: str
    request_method: str
    request_url: str
    token_type: str
    environment: str
    response_status_code: str
    latency: int
    request_headers: dict = field(default_factory=dict)
    request_body: str | None = None
    response_headers: dict = field(default_factory=dict)
    response_body: str | None = None
    customer: str | None = None
    ip: str | None = None
    user_id: str | None = None

    def kafka_key(self) -> dict:
        return {'id': self.id}

    def kafka_value(self) -> dict:
        camel_keys_dict: dict = dict_keys_snake_to_camel(self.to_dict())
        converted_value_types_dict = convert_dict_values_types(camel_keys_dict)
        return converted_value_types_dict
