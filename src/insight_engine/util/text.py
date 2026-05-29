import random
import secrets
import string
from uuid import UUID

_alphanum_alphabet = string.ascii_letters + string.digits
_alphanum_alphabet_set = set(_alphanum_alphabet)

_separator_chars = set('\t _./\\|,;:')


def generate_uuid() -> UUID:
    return _random_uuid()


def generate_alphanum(target_length: int) -> str:
    return ''.join(_select_random(_alphanum_alphabet) for _ in range(target_length))


def only_alphanum(text: str) -> str:
    return ''.join(c for c in str(text) if c in _alphanum_alphabet_set)


def to_alphanum_with_dashes(text: str) -> str:
    text_with_consecutive_dashes = ''.join(
        c
        if c in _alphanum_alphabet_set
        else '-' if c in _separator_chars
        else ''
        for c in str(text)
    )
    parts = [p for p in text_with_consecutive_dashes.split('-') if len(p) > 0]
    return '-'.join(parts)

def _select_random(seq):
    return secrets.choice(seq)


def _random_uuid():
    return UUID(int=random.getrandbits(128), version=4)
