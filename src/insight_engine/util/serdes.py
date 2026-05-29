from typing import Any

import orjson


def snake_to_camel(string: str) -> str:
    head, *tail = string.split('_')
    return head + ''.join([p.capitalize() for p in tail])


def obj_to_json(obj: Any) -> str:
    return orjson.dumps(obj).decode()


def json_to_obj(input: str | bytes) -> Any:
    if type(input) == bytes:
        return orjson.loads(input)
    else:
        return orjson.loads(input.encode())


def dict_keys_snake_to_camel(dct: dict) -> dict:
    return {snake_to_camel(k): v for k, v in dct.items()}


def convert_dict_values_types(dct: dict) -> dict:
    return {k: nested_dict_values_to_str(v) for k, v in dct.items()}


def nested_dict_values_to_str(value: Any) -> Any:
    if isinstance(value, dict):
        return obj_to_json(value)
    else:
        return value
