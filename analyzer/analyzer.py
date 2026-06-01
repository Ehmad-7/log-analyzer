"""Log analyzer statistics and aggregation."""

from collections import Counter

from .models import LogEntry
from .parser import parse_line


class LogAnalyzer:
    """Collects aggregate statistics for parsed log entries."""

    def __init__(self) -> None:
        self.total_lines: int = 0
        self.valid_lines: int = 0
        self.malformed_lines: int = 0
        self.status_code_counts: Counter[int] = Counter()
        self.error_endpoint_counts: Counter[str] = Counter()
        self.endpoint_counts: Counter[str] = Counter()
        self.response_time_totals: Counter[str] = Counter()
        self.response_time_counts: Counter[str] = Counter()
        self.unique_ips: set[str] = set()

    def process_entry(self, entry: LogEntry) -> None:
        """Update statistics based on a valid LogEntry."""
        self.total_lines += 1
        self.valid_lines += 1

        if entry.status is not None:
            self.status_code_counts[entry.status] += 1
            if entry.status >= 400:
                self.error_endpoint_counts[entry.path] += 1

        self.endpoint_counts[entry.path] += 1
        self.response_time_totals[entry.path] += entry.response_time_ms
        self.response_time_counts[entry.path] += 1
        self.unique_ips.add(entry.ip)

    def process_malformed_line(self) -> None:
        """Record a malformed log line in aggregate statistics."""
        self.total_lines += 1
        self.malformed_lines += 1

    def process_file(self, file_path: str) -> None:
        """Process a log file line by line and update statistics."""
        with open(file_path, "r", encoding="utf-8") as handle:
            for line in handle:
                entry = parse_line(line)
                if entry is None:
                    self.process_malformed_line()
                else:
                    self.process_entry(entry)

    @property
    def unique_ip_count(self) -> int:
        """Return the total count of unique IP addresses."""
        return len(self.unique_ips)

    def top_error_endpoints(self, limit: int = 10) -> list[tuple[str, int]]:
        """Return endpoints with the most errors.

        Results are returned as (endpoint, error_count) tuples.
        """
        if limit <= 0:
            return []
        return self.error_endpoint_counts.most_common(limit)

    def top_slowest_endpoints(self, limit: int = 10) -> list[tuple[str, float]]:
        """Return endpoints ordered by average response time.

        Results are returned as (endpoint, average_ms) tuples.
        """
        if limit <= 0:
            return []

        averages = []
        for endpoint, total_time in self.response_time_totals.items():
            count = self.response_time_counts.get(endpoint, 0)
            if count > 0:
                averages.append((endpoint, total_time / count))

        averages.sort(key=lambda item: item[1], reverse=True)
        return averages[:limit]
