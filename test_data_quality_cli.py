from pathlib import Path

from data_quality_cli import validate_csv


def write_csv(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "data.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_valid_file_passes(tmp_path: Path) -> None:
    report = validate_csv(
        write_csv(tmp_path, "id,email,created_at\n1,a@example.com,2026-08-31\n"),
        required_columns=("id", "email", "created_at"),
        unique_key="id",
        non_empty_columns=("email",),
        date_columns=("created_at",),
    )
    assert report.passed
    assert report.total_rows == 1


def test_duplicate_empty_and_invalid_date_are_reported(tmp_path: Path) -> None:
    report = validate_csv(
        write_csv(tmp_path, "id,email,created_at\n1,,2026-08-31\n1,b@example.com,31/08/2026\n"),
        unique_key="id",
        non_empty_columns=("email",),
        date_columns=("created_at",),
    )
    assert {issue.code for issue in report.issues} == {"empty_value", "duplicate_key", "invalid_date"}


def test_missing_columns_are_reported(tmp_path: Path) -> None:
    report = validate_csv(write_csv(tmp_path, "id\n1\n"), required_columns=("id", "email"), unique_key="email")
    assert {issue.code for issue in report.issues} == {"missing_column"}
    assert {issue.column for issue in report.issues} == {"email"}

