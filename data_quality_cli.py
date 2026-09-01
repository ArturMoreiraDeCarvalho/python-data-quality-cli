"""Dependency-free CSV validation CLI for portfolio and learning."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Issue:
    row: int
    column: str
    code: str
    message: str


@dataclass(frozen=True)
class QualityReport:
    file: str
    columns: tuple[str, ...]
    total_rows: int
    issues: tuple[Issue, ...]

    @property
    def passed(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "columns": list(self.columns),
            "total_rows": self.total_rows,
            "passed": self.passed,
            "issues": [issue.__dict__ for issue in self.issues],
        }


def _normalise_names(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value.strip() for value in values if value.strip()))


def validate_csv(
    path: str | Path,
    *,
    required_columns: Sequence[str] = (),
    unique_key: str | None = None,
    non_empty_columns: Sequence[str] = (),
    date_columns: Sequence[str] = (),
) -> QualityReport:
    required = _normalise_names(required_columns)
    non_empty = _normalise_names(non_empty_columns)
    dates = _normalise_names(date_columns)
    issues: list[Issue] = []

    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = tuple(reader.fieldnames or ())
        known_columns = set(columns)
        for column in sorted(set(required) - known_columns):
            issues.append(Issue(1, column, "missing_column", "Required column is missing"))
        configured_columns = (*non_empty, *dates) + ((unique_key,) if unique_key else ())
        for column in configured_columns:
            if column and column not in known_columns:
                issues.append(Issue(1, column, "missing_column", "Configured column is missing"))

        seen: dict[str, int] = {}
        total_rows = 0
        for csv_row, row in enumerate(reader, start=2):
            total_rows += 1
            if unique_key and unique_key in known_columns:
                value = (row.get(unique_key) or "").strip()
                if value and value in seen:
                    issues.append(Issue(csv_row, unique_key, "duplicate_key", f"Value already appears on row {seen[value]}"))
                elif value:
                    seen[value] = csv_row
            for column in non_empty:
                if column in known_columns and not (row.get(column) or "").strip():
                    issues.append(Issue(csv_row, column, "empty_value", "Value must not be empty"))
            for column in dates:
                value = (row.get(column) or "").strip()
                if value:
                    try:
                        date.fromisoformat(value)
                    except ValueError:
                        issues.append(Issue(csv_row, column, "invalid_date", "Use the YYYY-MM-DD format"))

    return QualityReport(str(path), columns, total_rows, tuple(issues))


def _csv_values(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a CSV file with explicit data quality rules.")
    parser.add_argument("file", type=Path, help="CSV file to validate")
    parser.add_argument("--required", default="", help="Comma-separated required columns")
    parser.add_argument("--unique-key", help="Column whose non-empty values must be unique")
    parser.add_argument("--non-empty", default="", help="Comma-separated columns that cannot be empty")
    parser.add_argument("--date-column", default="", help="Comma-separated ISO date columns")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = validate_csv(
            args.file,
            required_columns=_csv_values(args.required),
            unique_key=args.unique_key,
            non_empty_columns=_csv_values(args.non_empty),
            date_columns=_csv_values(args.date_column),
        )
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    elif report.passed:
        print(f"PASS: {report.total_rows} row(s) checked in {report.file}")
    else:
        print(f"FAIL: {len(report.issues)} issue(s) in {report.file}")
        for issue in report.issues:
            print(f"  row {issue.row}, {issue.column}: {issue.code} - {issue.message}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
