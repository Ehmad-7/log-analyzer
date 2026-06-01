"""Parsing helpers for the log analyzer."""


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