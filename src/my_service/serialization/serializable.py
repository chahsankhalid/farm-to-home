from dataclasses import asdict, is_dataclass, fields
from typing import Self, Type

import marshmallow_dataclass
from marshmallow import Schema

_serializable_schemas: dict[Type, Schema] = {}
_api_safe_schemas: dict[Type, Schema] = {}


# Base class to offer serialization capabilities with marshmallow-dataclass
class Serializable:
    # Native dict of this dataclass (with intact objects, enums, datetimes, etc.)
    def to_native_dict(self) -> dict:
        # noinspection PyTypeChecker,PyDataclass
        return asdict(self)

    # Dataclass from native dict (with intact objects, enums, datetimes, etc.)
    @classmethod
    def from_native_dict(cls, dct: dict) -> Self:
        # noinspection PyArgumentList
        return cls(**dct)

    # Serialized dict of this dataclass
    def to_dict(self) -> dict:
        return type(self)._serializable_schema().dump(self)

    # API-safe serialized dict (excludes fields marked as sensitive)
    def to_api_dict(self) -> dict:
        return type(self)._api_safe_schema().dump(self)

    # Dataclass from a serialized dict
    @classmethod
    def from_dict(cls, dct: dict) -> Self:
        return cls._serializable_schema().load(dct)

    @classmethod
    def _serializable_schema(cls):
        if cls not in _serializable_schemas:
            schema = marshmallow_dataclass.class_schema(cls)()
            _serializable_schemas[cls] = schema
        return _serializable_schemas[cls]

    @classmethod
    def _api_safe_schema(cls):
        if cls not in _api_safe_schemas:
            # Get the base schema
            base_schema_class = marshmallow_dataclass.class_schema(cls)
            
            # Find fields that should be excluded from API responses
            sensitive_fields = []
            if hasattr(cls, '__dataclass_fields__'):
                for field_name, field_info in cls.__dataclass_fields__.items():
                    if field_info.metadata.get('api_exclude', False):
                        sensitive_fields.append(field_name)
            
            # Create a new schema class with sensitive fields excluded
            class ApiSafeSchema(base_schema_class):
                class Meta(getattr(base_schema_class, 'Meta', object)):
                    exclude = sensitive_fields
            
            _api_safe_schemas[cls] = ApiSafeSchema()
        return _api_safe_schemas[cls]
