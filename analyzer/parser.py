"""Parsing helpers for the log analyzer."""

import json

from datetime import datetime, timezone

from .models import LogEntry


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


def parse_text_log(line: str) -> LogEntry:
    """Parse a whitespace-delimited log line into a LogEntry.

    Expected format:
    <timestamp> <ip> <method> <path> <status> <response_time> [extra...]
    """
    if line is None:
        raise ValueError("log line is required")

    raw = line.strip()
    if not raw:
        raise ValueError("log line is empty")

    parts = raw.split()
    if len(parts) < 5:
        raise ValueError("log line has too few fields")

    timestamp = None
    remaining = []
    for timestamp_tokens in (2, 1):
        if len(parts) < timestamp_tokens + 4:
            continue
        timestamp_text = " ".join(parts[:timestamp_tokens])
        try:
            timestamp = parse_timestamp(timestamp_text)
        except ValueError:
            continue
        remaining = parts[timestamp_tokens:]
        break

    if timestamp is None:
        raise ValueError(f"invalid log line '{raw}'")

    ip = remaining[0]
    method = remaining[1]
    path = remaining[2]

    if len(remaining) >= 5:
        status_text = remaining[3]
        response_time_text = remaining[4]
    else:
        status_text = None
        response_time_text = remaining[3]

    status = None
    if status_text and status_text != "-":
        try:
            status = int(status_text)
        except ValueError as exc:
            raise ValueError(f"invalid status '{status_text}'") from exc

    try:
        response_time_ms = parse_response_time(response_time_text)
    except ValueError as exc:
        raise ValueError(f"invalid log line '{raw}'") from exc

    return LogEntry(
        timestamp=timestamp,
        ip=ip,
        method=method,
        path=path,
        status=status,
        response_time_ms=response_time_ms,
    )


def parse_json_log(line: str) -> LogEntry:
    """Parse a JSON-encoded log line into a LogEntry."""
    if line is None:
        raise ValueError("log line is required")

    raw = line.strip()
    if not raw:
        raise ValueError("log line is empty")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid json log line") from exc

    if not isinstance(payload, dict):
        raise ValueError("invalid json log line")

    required_fields = ["timestamp", "ip", "method", "path", "response_time"]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        missing_fields = ", ".join(missing)
        raise ValueError(f"missing required fields: {missing_fields}")

    ip = payload.get("ip")
    method = payload.get("method")
    path = payload.get("path")
    if not isinstance(ip, str) or not ip.strip():
        raise ValueError(f"invalid ip '{ip}'")
    if not isinstance(method, str) or not method.strip():
        raise ValueError(f"invalid method '{method}'")
    if not isinstance(path, str) or not path.strip():
        raise ValueError(f"invalid path '{path}'")

    status_value = payload.get("status")
    status = None
    if status_value is not None and status_value != "-":
        try:
            status = int(status_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid status '{status_value}'") from exc

    try:
        timestamp = parse_timestamp(str(payload.get("timestamp")))
        response_time_ms = parse_response_time(str(payload.get("response_time")))
    except ValueError as exc:
        raise ValueError("invalid json log line") from exc

    return LogEntry(
        timestamp=timestamp,
        ip=ip.strip(),
        method=method.strip(),
        path=path.strip(),
        status=status,
        response_time_ms=response_time_ms,
    )


def parse_line(line: str) -> LogEntry | None:
    try:
        return parse_json_log(line)
    except ValueError:
        pass

    try:
        return parse_text_log(line)
    except ValueError:
        return None

