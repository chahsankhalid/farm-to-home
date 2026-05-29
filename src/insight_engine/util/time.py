# Timezones are a hassle. If the application or database is run in any time zone other than UTC,
# the datetime package can easily be misused to produce incorrect timestamps, or timestamps that change when
# inserted into the database and read back from the database.
# We should always use this util in order to avoid these problems.
#
# Examples of gotchas:
# * Results of datetime.utcnow().timestamp() and datetime.now(timezone.utc) are different
# * datetime.datetime.fromisoformat(x) does not work on all valid ISO-8601 dates
#
# This package always uses UTC datetimes

from datetime import datetime, timezone

from dateutil import parser


def current_datetime() -> datetime:
    return _current_datetime()


def current_epoch_seconds() -> float:
    return _current_datetime().timestamp()


def from_epoch_seconds(epoch_seconds):
    return datetime.fromtimestamp(epoch_seconds, timezone.utc)


def from_iso8601(iso_8601_date) -> datetime:
    return parser.parse(iso_8601_date).astimezone(timezone.utc)


def seconds_to_milliseconds(seconds: float) -> float:
    return seconds * 1000


def get_request_time(start_time: float, end_time: float) -> int:
    interval = end_time - start_time
    return round(seconds_to_milliseconds(interval))


def _current_datetime() -> datetime:
    return datetime.now(timezone.utc)
