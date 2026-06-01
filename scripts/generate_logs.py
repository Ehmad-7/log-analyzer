"""Generate sample log files for the log analyzer."""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone

DEFAULT_OUTPUT = "sample.log"
DEFAULT_ENTRIES = 10000

METHODS = ["GET", "POST", "PUT", "DELETE"]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500]
ENDPOINTS = [
    "/api/users",
    "/api/users/{id}",
    "/api/login",
    "/api/logout",
    "/api/orders",
    "/api/orders/{id}",
    "/api/products",
    "/api/report",
    "/api/export",
]
EXTRA_FIELDS = [
    "Mozilla/5.0",
    '"https://example.com/login page"',
    '"Some User Agent With Spaces"',
]


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the generator CLI."""
    parser = argparse.ArgumentParser(description="Generate sample log files.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output log file path.")
    parser.add_argument(
        "--entries",
        type=int,
        default=DEFAULT_ENTRIES,
        help="Number of log entries to generate.",
    )
    return parser


def random_ip(rng: random.Random) -> str:
    """Generate a random IPv4 address."""
    return ".".join(str(rng.randint(1, 254)) for _ in range(4))


def random_endpoint(rng: random.Random) -> str:
    """Choose a random endpoint, filling IDs where needed."""
    endpoint = rng.choice(ENDPOINTS)
    if "{id}" in endpoint:
        return endpoint.format(id=rng.randint(1, 5000))
    return endpoint


def random_timestamp(rng: random.Random) -> datetime:
    """Generate a random datetime within a fixed range."""
    start = datetime(2024, 3, 15, tzinfo=timezone.utc)
    offset_seconds = rng.randint(0, 60 * 60 * 24 * 30)
    return start + timedelta(seconds=offset_seconds)


def format_timestamp(timestamp: datetime, kind: str) -> str:
    """Format a datetime into one of the supported timestamp formats."""
    if kind == "iso":
        return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    if kind == "slash":
        return timestamp.strftime("%Y/%m/%d %H:%M:%S")
    if kind == "text":
        return timestamp.strftime("%d-%b-%Y %H:%M:%S")
    if kind == "epoch":
        return str(int(timestamp.timestamp()))
    raise ValueError(f"unsupported timestamp kind '{kind}'")


def format_response_time(rng: random.Random, kind: str) -> str:
    """Format a response time string for supported formats."""
    ms = rng.randint(5, 1200)
    if kind == "ms":
        return f"{ms}ms"
    if kind == "s":
        return f"{ms / 1000:.3f}s"
    if kind == "raw":
        return str(ms)
    raise ValueError(f"unsupported response time kind '{kind}'")


def build_standard_entry(rng: random.Random) -> str:
    """Build a standard log entry."""
    timestamp = format_timestamp(random_timestamp(rng), "iso")
    ip = random_ip(rng)
    method = rng.choice(METHODS)
    path = random_endpoint(rng)
    status = rng.choice(STATUS_CODES)
    response_time = format_response_time(rng, "ms")
    return f"{timestamp} {ip} {method} {path} {status} {response_time}"


def build_unusual_entry(rng: random.Random) -> str:
    """Build a valid but unusual log entry."""
    timestamp_kind = rng.choice(["slash", "text", "epoch"])
    timestamp = format_timestamp(random_timestamp(rng), timestamp_kind)
    ip = random_ip(rng)
    method = rng.choice(METHODS)
    path = random_endpoint(rng)

    status = "-" if rng.random() < 0.3 else str(rng.choice(STATUS_CODES))
    response_kind = rng.choice(["s", "raw", "ms"])
    response_time = format_response_time(rng, response_kind)

    entry = f"{timestamp} {ip} {method} {path} {status} {response_time}"

    if rng.random() < 0.5:
        extras = rng.choice(EXTRA_FIELDS)
        entry = f"{entry} {extras}"
    return entry


def build_json_entry(rng: random.Random) -> str:
    """Build a JSON log entry string."""
    timestamp = format_timestamp(random_timestamp(rng), "iso")
    ip = random_ip(rng)
    method = rng.choice(METHODS)
    path = random_endpoint(rng)
    status = rng.choice(STATUS_CODES)
    response_time = format_response_time(rng, rng.choice(["ms", "s", "raw"]))

    payload = {
        "timestamp": timestamp,
        "ip": ip,
        "method": method,
        "path": path,
        "status": status if rng.random() > 0.1 else None,
        "response_time": response_time,
    }
    return json.dumps(payload, separators=(",", ":"))


def build_malformed_entry(rng: random.Random) -> str:
    """Build a malformed log entry string."""
    options = [
        "",
        "garbage !!! not a log line",
        "2024-03-15T14:23:01Z 192.168.1.42 GET",
        "{\"timestamp\":\"2024-03-15T14:23:01Z\", \"ip\":\"192.168.1.42\"",
        "{not-json}",
    ]
    return rng.choice(options)


def generate_entries(count: int, rng: random.Random) -> list[str]:
    """Generate a list of log entry strings."""
    entries: list[str] = []
    for _ in range(count):
        roll = rng.random()
        if roll < 0.85:
            entries.append(build_standard_entry(rng))
        elif roll < 0.90:
            entries.append(build_json_entry(rng))
        elif roll < 0.95:
            entries.append(build_unusual_entry(rng))
        else:
            entries.append(build_malformed_entry(rng))
    return entries


def main(argv: list[str] | None = None) -> int:
    """Run the log generator CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.entries < 0:
        parser.error("--entries must be a non-negative integer")

    rng = random.Random()
    entries = generate_entries(args.entries, rng)

    with open(args.output, "w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(f"{entry}\n")

    print(f"Generated {args.entries} entries to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
