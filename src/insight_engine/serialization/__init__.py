import datetime
import typing
from datetime import timezone

from marshmallow.fields import DateTime, Field


# By default, Marshmallow cannot deserialize dicts that already contain the target type
# This is an issue for the datetime type because SQL results do have dicts with datetime.
# See https://github.com/marshmallow-code/marshmallow/issues/1415
def _register_identity_deserializers(*custom_deserializer_fields: typing.Type[Field]):
    format_suffix = '_allow_identity'
    for field in custom_deserializer_fields:
        if not field.DEFAULT_FORMAT.endswith(format_suffix):
            original_format = field.DEFAULT_FORMAT
            original_serialize = field.SERIALIZATION_FUNCS[original_format]
            original_deserialize = field.DESERIALIZATION_FUNCS[original_format]

            # noinspection PyProtectedMember
            original_deserialize_signature = typing.get_type_hints(field._deserialize)
            original_deserialized_type = original_deserialize_signature.get('return')
            custom_deserialize = lambda v: v if isinstance(v, original_deserialized_type) else original_deserialize(v)

            custom_format = f'{original_format}{format_suffix}'
            field.SERIALIZATION_FUNCS[custom_format] = original_serialize
            field.DESERIALIZATION_FUNCS[custom_format] = custom_deserialize
            field.DEFAULT_FORMAT = custom_format


def _register_utc_datetime_deserializer():
    original_deserializer = DateTime.DESERIALIZATION_FUNCS[DateTime.DEFAULT_FORMAT]
    DateTime.DESERIALIZATION_FUNCS[DateTime.DEFAULT_FORMAT] = lambda serialized_time: (
        original_deserializer(serialized_time).replace(tzinfo=timezone.utc)
    )


DateTime.DEFAULT_FORMAT = 'timestamp'
_register_identity_deserializers(DateTime)
_register_utc_datetime_deserializer()
