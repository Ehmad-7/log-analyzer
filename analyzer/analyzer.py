"""Log analyzer statistics and aggregation."""

from collections import Counter

from .models import LogEntry


class LogAnalyzer:
    """Collects aggregate statistics for parsed log entries."""

    def __init__(self) -> None:
        self.total_lines: int = 0
        self.valid_lines: int = 0
        self.malformed_lines: int = 0
        self.status_code_counts: Counter[int] = Counter()
        self.endpoint_counts: Counter[str] = Counter()
        self.unique_ips: set[str] = set()

    def process_entry(self, entry: LogEntry) -> None:
        """Update statistics based on a valid LogEntry."""
        self.total_lines += 1
        self.valid_lines += 1

        if entry.status is not None:
            self.status_code_counts[entry.status] += 1

        self.endpoint_counts[entry.path] += 1
        self.unique_ips.add(entry.ip)

    def process_malformed_line(self) -> None:
        """Record a malformed log line in aggregate statistics."""
        self.total_lines += 1
        self.malformed_lines += 1

    @property
    def unique_ip_count(self) -> int:
        """Return the total count of unique IP addresses."""
        return len(self.unique_ips)
