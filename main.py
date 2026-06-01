"""CLI entrypoint for the log analyzer."""

from __future__ import annotations

import argparse
import sys

from analyzer.analyzer import LogAnalyzer


def build_parser() -> argparse.ArgumentParser:
	"""Create the argument parser for the CLI."""
	parser = argparse.ArgumentParser(description="Analyze log files.")
	parser.add_argument("log_file", help="Path to the log file.")
	return parser


def main(argv: list[str] | None = None) -> int:
	"""Run the log analyzer CLI."""
	parser = build_parser()
	args = parser.parse_args(argv)

	analyzer = LogAnalyzer()
	try:
		analyzer.process_file(args.log_file)
	except FileNotFoundError:
		print(f"File not found: {args.log_file}", file=sys.stderr)
		return 1
	except PermissionError:
		print(f"Permission denied: {args.log_file}", file=sys.stderr)
		return 1

	print(analyzer.generate_report())
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
