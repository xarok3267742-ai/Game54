#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_rc_traceability.py"

spec = importlib.util.spec_from_file_location("rc_traceability_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

REQUIREMENTS = {
    "R01_LOCAL": {
        "status": checker.LOCAL_PROVEN,
        "evidence": {
            "docs/local.md": ("local-marker",),
        },
    },
    "R02_LOCAL": {
        "status": checker.LOCAL_PROVEN,
        "evidence": {
            "docs/local-second.md": ("second-marker",),
        },
    },
    "R03_EXTERNAL": {
        "status": checker.EXTERNAL_REQUIRED,
        "evidence": {
            "docs/external.md": ("external-marker",),
        },
    },
}


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def write_fixture(root: Path) -> Path:
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "local.md").write_text("local-marker\n", encoding="utf-8")
    (docs / "local-second.md").write_text("second-marker\n", encoding="utf-8")
    (docs / "external.md").write_text("external-marker\n", encoding="utf-8")
    report = docs / "rc_requirement_traceability.md"
    report.write_text(
        "\n".join(
            [
                "# RC Requirement Traceability",
                "| ID | Requirement | Status | Evidence |",
                "|---|---|---|---|",
                "| R01_LOCAL | Local one | LOCAL_PROVEN | `docs/local.md` |",
                "| R02_LOCAL | Local two | LOCAL_PROVEN | `docs/local-second.md` |",
                "| R03_EXTERNAL | External one | EXTERNAL_REQUIRED | `docs/external.md` |",
            ]
        ),
        encoding="utf-8",
    )
    return report


def with_fixture(test_body) -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-rc-traceability-test."))
    try:
        report = write_fixture(temp_dir)
        test_body(temp_dir, report)
    finally:
        shutil.rmtree(temp_dir)


def failures_for(root: Path, report: Path, requirements: dict[str, dict[str, object]] = REQUIREMENTS) -> list[str]:
    return checker.traceability_failures(
        root=root,
        report=report,
        requirements=requirements,
        min_local_count=2,
        expected_external_count=1,
    )


def test_valid_fixture_passes() -> None:
    def run(root: Path, report: Path) -> None:
        assert_equal(failures_for(root, report), [])

    with_fixture(run)


def test_missing_report_fails() -> None:
    def run(root: Path, report: Path) -> None:
        report.unlink()
        assert_failure_contains(failures_for(root, report), "missing traceability report")

    with_fixture(run)


def test_missing_report_row_fails() -> None:
    def run(root: Path, report: Path) -> None:
        report.write_text(report.read_text(encoding="utf-8").replace("| R02_LOCAL |", "| R02_OTHER |"), encoding="utf-8")
        failures = failures_for(root, report)
        assert_failure_contains(failures, "traceability report is missing R02_LOCAL")
        assert_failure_contains(failures, "traceability report table is missing row for R02_LOCAL")

    with_fixture(run)


def test_missing_status_fails() -> None:
    def run(root: Path, report: Path) -> None:
        report.write_text(report.read_text(encoding="utf-8").replace("EXTERNAL_REQUIRED", "WAITING"), encoding="utf-8")
        assert_failure_contains(failures_for(root, report), "traceability report is missing status EXTERNAL_REQUIRED")

    with_fixture(run)


def test_report_row_status_mismatch_fails_even_when_status_exists_elsewhere() -> None:
    def run(root: Path, report: Path) -> None:
        text = report.read_text(encoding="utf-8")
        text = text.replace(
            "| R03_EXTERNAL | External one | EXTERNAL_REQUIRED | `docs/external.md` |",
            "| R03_EXTERNAL | External one | LOCAL_PROVEN | `docs/external.md` |",
        )
        report.write_text(text + "\nEXTERNAL_REQUIRED\n", encoding="utf-8")
        assert_failure_contains(
            failures_for(root, report),
            "traceability report row R03_EXTERNAL has status LOCAL_PROVEN instead of EXTERNAL_REQUIRED",
        )

    with_fixture(run)


def test_unexpected_report_row_fails() -> None:
    def run(root: Path, report: Path) -> None:
        text = report.read_text(encoding="utf-8")
        text += "\n| R99_STALE | Old row | LOCAL_PROVEN | `docs/local.md` |"
        report.write_text(text, encoding="utf-8")
        assert_failure_contains(failures_for(root, report), "traceability report table has unexpected row for R99_STALE")

    with_fixture(run)


def test_duplicate_report_row_fails() -> None:
    def run(root: Path, report: Path) -> None:
        text = report.read_text(encoding="utf-8")
        text += "\n| R02_LOCAL | Duplicate local two | LOCAL_PROVEN | `docs/local-second.md` |"
        report.write_text(text, encoding="utf-8")
        assert_failure_contains(failures_for(root, report), "traceability report table has duplicate row for R02_LOCAL")

    with_fixture(run)


def test_unexpected_evidence_path_fails() -> None:
    def run(root: Path, report: Path) -> None:
        text = report.read_text(encoding="utf-8")
        text = text.replace(
            "| R01_LOCAL | Local one | LOCAL_PROVEN | `docs/local.md` |",
            "| R01_LOCAL | Local one | LOCAL_PROVEN | `docs/local.md`, `docs/not-evidence.md` |",
        )
        report.write_text(text, encoding="utf-8")
        assert_failure_contains(
            failures_for(root, report),
            "traceability report row R01_LOCAL has unexpected evidence path: docs/not-evidence.md",
        )

    with_fixture(run)


def test_no_recognized_evidence_path_fails() -> None:
    def run(root: Path, report: Path) -> None:
        text = report.read_text(encoding="utf-8")
        text = text.replace(
            "| R01_LOCAL | Local one | LOCAL_PROVEN | `docs/local.md` |",
            "| R01_LOCAL | Local one | LOCAL_PROVEN | `docs/not-evidence.md` |",
        )
        report.write_text(text, encoding="utf-8")
        failures = failures_for(root, report)
        assert_failure_contains(failures, "traceability report row R01_LOCAL has no recognized evidence paths")
        assert_failure_contains(
            failures,
            "traceability report row R01_LOCAL has unexpected evidence path: docs/not-evidence.md",
        )

    with_fixture(run)


def test_missing_evidence_file_fails() -> None:
    def run(root: Path, report: Path) -> None:
        (root / "docs/local.md").unlink()
        assert_failure_contains(failures_for(root, report), "R01_LOCAL: missing evidence file docs/local.md")

    with_fixture(run)


def test_missing_evidence_marker_fails() -> None:
    def run(root: Path, report: Path) -> None:
        (root / "docs/external.md").write_text("wrong-marker\n", encoding="utf-8")
        assert_failure_contains(failures_for(root, report), "R03_EXTERNAL: docs/external.md is missing evidence marker")

    with_fixture(run)


def test_expected_external_count_fails() -> None:
    def run(root: Path, report: Path) -> None:
        failures = checker.traceability_failures(
            root=root,
            report=report,
            requirements=REQUIREMENTS,
            min_local_count=2,
            expected_external_count=2,
        )
        assert_failure_contains(failures, "expected 2 external requirements, found 1")

    with_fixture(run)


def test_minimum_local_count_fails() -> None:
    def run(root: Path, report: Path) -> None:
        failures = checker.traceability_failures(
            root=root,
            report=report,
            requirements=REQUIREMENTS,
            min_local_count=3,
            expected_external_count=1,
        )
        assert_failure_contains(failures, "traceability coverage is unexpectedly low")

    with_fixture(run)


def main() -> int:
    tests = [
        test_valid_fixture_passes,
        test_missing_report_fails,
        test_missing_report_row_fails,
        test_missing_status_fails,
        test_report_row_status_mismatch_fails_even_when_status_exists_elsewhere,
        test_unexpected_report_row_fails,
        test_duplicate_report_row_fails,
        test_unexpected_evidence_path_fails,
        test_no_recognized_evidence_path_fails,
        test_missing_evidence_file_fails,
        test_missing_evidence_marker_fails,
        test_expected_external_count_fails,
        test_minimum_local_count_fails,
    ]
    for test in tests:
        test()
    print("PASS: RC requirement traceability checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
