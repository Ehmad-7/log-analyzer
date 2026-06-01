# ANSWERS

## 1. How to run

### Requirements

* Python 3.12+
* pytest (for running tests)

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
```

### Generate sample logs

```bash
python scripts/generate_logs.py
```

### Run the analyzer

```bash
python main.py sample.log
```

### Run tests

```bash
pytest
```

---

## 2. Stack choice

I chose Python because the task is primarily focused on text processing, parsing, aggregation, and reporting. Python provides excellent standard-library support for JSON handling, date parsing, file processing, collections, and command-line interfaces while keeping the implementation concise and readable.

A worse choice for this task would have been a frontend-focused framework such as React because the challenge is centered on processing large log files and handling malformed input rather than building a user interface.

---

## 3. One real edge case

The parser correctly handles log files that contain multiple timestamp formats within the same file.

Examples:

* `2024-03-15T14:23:01Z`
* `2024/03/15 14:23:01`
* `15-Mar-2024 14:23:01`
* Unix epoch timestamps such as `1710512581`

This handling is implemented in `analyzer/parser.py` inside the `parse_timestamp()` function.

Without this handling, valid log entries would be incorrectly classified as malformed whenever the log format changed, reducing the accuracy of the analysis report.

---

## 4. AI usage

I used GitHub Copilot during development.

Examples:

* Generating the initial implementations of parsing helper functions.
* Generating portions of the synthetic log generator.
* Generating the initial pytest test cases.
* Generating documentation structure for the README.

AI-generated code was reviewed and modified before use.

One example is the text log parser. The initial implementation assumed timestamps were always a single token. This would fail for timestamp formats such as `2024/03/15 14:23:01` and `15-Mar-2024 14:23:01`. I modified the implementation so that it correctly detects and parses supported timestamp formats before extracting the remaining fields.

---

## 5. Honest gap

The current implementation treats endpoints with path parameters as separate endpoints. For example:

* `/api/users/1`
* `/api/users/2`

are reported independently.

With an additional day, I would normalize dynamic path segments so that these requests are aggregated under a common endpoint pattern such as:

`/api/users/{id}`

This would produce more meaningful slow-endpoint and error-endpoint statistics.
