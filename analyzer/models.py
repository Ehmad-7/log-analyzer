"""Data models for parsed log entries."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LogEntry:
    """Represents a parsed log entry with normalized request metadata."""

    timestamp: datetime
    ip: str
    method: str
    path: str
    status: Optional[int]
    response_time_ms: float
