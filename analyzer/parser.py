"""Parsing helpers for the log analyzer."""

from datetime import datetime, timezone


def parse_response_time(value: str) -> float:
    """Parse a response time string into milliseconds.

    Supported formats: '<number>ms', '<number>s', or '<number>' (milliseconds).
    """
    if value is None:
        raise ValueError("response time is required")

    raw = value.strip()
    if not raw:
        raise ValueError("response time is empty")

    if raw.endswith("ms"):
        number = raw[:-2].strip()
        return _parse_number(number, "ms", scale=1.0, raw_input=raw)

    if raw.endswith("s"):
        number = raw[:-1].strip()
        return _parse_number(number, "s", scale=1000.0, raw_input=raw)

    return _parse_number(raw, "ms", scale=1.0, raw_input=raw)


def _parse_number(number: str, unit: str, scale: float, raw_input: str) -> float:
    if not number:
        raise ValueError(f"response time missing value before '{unit}'")
    try:
        parsed = float(number)
    except ValueError as exc:
        raise ValueError(f"invalid response time '{raw_input}'") from exc
    return parsed * scale


def parse_timestamp(value: str) -> datetime:
    """Parse a timestamp string into a datetime.

    Supported formats:
    - 2024-03-15T14:23:01Z
    - 2024/03/15 14:23:01
    - 15-Mar-2024 14:23:01
    - Unix epoch seconds (e.g., 1710512581)
    """
    if value is None:
        raise ValueError("timestamp is required")

    raw = value.strip()
    if not raw:
        raise ValueError("timestamp is empty")

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y/%m/%d %H:%M:%S",
        "%d-%b-%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    try:
        epoch_seconds = int(raw)
    except ValueError as exc:
        raise ValueError(f"invalid timestamp '{raw}'") from exc

    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)


