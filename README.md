# Log Analyzer

A lightweight Python log analyzer that parses mixed-format access logs, aggregates key metrics, and produces a concise, human-readable report.

## Features

- Multiple timestamp formats
- JSON log support
- Malformed line handling
- Error endpoint analysis
- Slow endpoint analysis
- CLI interface
- Synthetic log generator

## Installation

Python 3.12+ is required.

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate Sample Logs

```bash
python scripts/generate_logs.py
```

Optional arguments:

- `--output`
- `--entries`

## Run Analyzer

```bash
python main.py sample.log
```

## Run Tests

```bash
pytest
```

## Project Structure

- `analyzer/` parsing and analytics logic
- `analyzer/models.py` data model for log entries
- `analyzer/parser.py` text and JSON parsers
- `analyzer/analyzer.py` aggregation and reporting
- `scripts/generate_logs.py` synthetic log generator
- `tests/` pytest suite for parsing logic
- `main.py` CLI entrypoint

## Design Decisions

Malformed lines are handled gracefully to avoid halting analysis on large, imperfect log files and to keep reports representative of the usable data.

## Dependencies

- Python 3.12+
- pytest (for tests)

## Example Output

```text
Total lines: 10000
Valid entries: 9492
Malformed entries: 508

Status Codes
------------
200 : 1368
404 : 1303

Top Endpoints
-------------
/api/users : 1093
/api/orders : 1079
```