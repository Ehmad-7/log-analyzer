from datetime import datetime, timezone
import pytest
from analyzer import parser as parser_module


def test_parse_response_time_ms() -> None:
    assert parser_module.parse_response_time("142ms") == 142.0


def test_parse_response_time_seconds() -> None:
    assert parser_module.parse_response_time("0.142s") == 142.0


def test_parse_response_time_raw() -> None:
    assert parser_module.parse_response_time("142") == 142.0


def test_parse_response_time_invalid() -> None:
    with pytest.raises(ValueError):
        parser_module.parse_response_time("bad")


def test_parse_timestamp_iso() -> None:
    expected = datetime(2024, 3, 15, 14, 23, 1)
    assert parser_module.parse_timestamp("2024-03-15T14:23:01Z") == expected


def test_parse_timestamp_slash() -> None:
    expected = datetime(2024, 3, 15, 14, 23, 1)
    assert parser_module.parse_timestamp("2024/03/15 14:23:01") == expected


def test_parse_timestamp_text() -> None:
    expected = datetime(2024, 3, 15, 14, 23, 1)
    assert parser_module.parse_timestamp("15-Mar-2024 14:23:01") == expected


def test_parse_timestamp_epoch() -> None:
    expected = datetime.fromtimestamp(1710512581, tz=timezone.utc)
    assert parser_module.parse_timestamp("1710512581") == expected


def test_parse_text_log_standard() -> None:
    entry = parser_module.parse_text_log(
        "2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms"
    )
    assert entry.ip == "192.168.1.42"
    assert entry.method == "GET"
    assert entry.path == "/api/users"
    assert entry.status == 200
    assert entry.response_time_ms == 142.0


def test_parse_text_log_missing_status() -> None:
    entry = parser_module.parse_text_log(
        "2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 142ms"
    )
    assert entry.status is None
    assert entry.response_time_ms == 142.0


def test_parse_json_log_valid() -> None:
    log_line = (
        "{"
        '"timestamp":"2024-03-15T14:23:01Z",'
        '"ip":"192.168.1.42",'
        '"method":"GET",'
        '"path":"/api/users",'
        '"status":200,'
        '"response_time":"142ms"'
        "}"
    )
    entry = parser_module.parse_json_log(log_line)
    assert entry.ip == "192.168.1.42"
    assert entry.method == "GET"
    assert entry.path == "/api/users"
    assert entry.status == 200
    assert entry.response_time_ms == 142.0


def test_parse_json_log_missing_field() -> None:
    log_line = (
        "{"
        '"timestamp":"2024-03-15T14:23:01Z",'
        '"method":"GET",'
        '"path":"/api/users",'
        '"response_time":"142ms"'
        "}"
    )
    with pytest.raises(ValueError):
        parser_module.parse_json_log(log_line)


def test_parse_line_valid() -> None:
    entry = parser_module.parse_line(
        "2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms"
    )
    assert entry is not None
    assert entry.status == 200


def test_parse_line_malformed() -> None:
    assert parser_module.parse_line("this is not a log") is None
