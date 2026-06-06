#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_qa_evidence.py"

spec = importlib.util.spec_from_file_location("qa_evidence_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)

DEFAULT_PACKAGE = "ru.poryadok5.app"
CUSTOM_PACKAGE = "com.example.custom"

FIXTURE = checker.EvidenceSet(
    name="Fixture emulator QA",
    report="docs/fixture_qa.md",
    directory="qa/fixture",
    report_snippets=("qa/fixture", "PASSED", "0 crash log lines"),
    pairs=("01-home",),
    files=("device_api.txt",),
    zero_byte_files=("app_error_matches.txt",),
    snippets=(
        ("01-home.xml", ("Порядок 5", checker.PACKAGE)),
        ("device_api.txt", ("35",)),
    ),
)

ALLOWLIST_FIXTURE = checker.EvidenceSet(
    name="Fixture crash allowlist",
    report="docs/fixture_allowed_crash_qa.md",
    directory="qa/fixture-allowed-crash",
    report_snippets=("qa/fixture-allowed-crash", "PASSED"),
    pairs=(),
    files=(),
    zero_byte_files=(),
    snippets=(),
    allow_crash_log_packages=("com.google.android.dialer",),
)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def long_text(snippets: tuple[str, ...]) -> str:
    text = "\n".join(snippets)
    filler = "\nЭмуляторный QA artefact для локальной проверки release candidate.\n"
    while len(text.encode("utf-8")) < 340:
        text += filler
    return text


def valid_png_bytes() -> bytes:
    return checker.PNG_HEADER + (b"\x00" * 280)


def resolve_marker(value: str, package_name: str = DEFAULT_PACKAGE) -> str:
    return value.replace(checker.APP_PACKAGE_TOKEN, package_name)


def valid_xml_text(extra: str = "Порядок 5", package_name: str = DEFAULT_PACKAGE) -> str:
    text = f'<hierarchy><node package="{package_name}" text="{extra}" /></hierarchy>'
    filler = "<node text=\"Состояние экрана\" />"
    while len(text.encode("utf-8")) < 300:
        text += filler
    return text


def write_evidence_set(root: Path, evidence: object, package_name: str = DEFAULT_PACKAGE) -> None:
    report = root / evidence.report
    directory = root / evidence.directory
    report.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir(parents=True, exist_ok=True)
    report.write_text(long_text(tuple(resolve_marker(snippet, package_name) for snippet in evidence.report_snippets)), encoding="utf-8")

    for stem in evidence.pairs:
        (directory / f"{stem}.xml").write_text(valid_xml_text(package_name=package_name), encoding="utf-8")
        (directory / f"{stem}.png").write_bytes(valid_png_bytes())

    for filename in evidence.files:
        text = "35\n"
        if filename.endswith(".txt"):
            text += "Дополнительная строка evidence.\n"
        (directory / filename).write_text(text, encoding="utf-8")

    for filename in evidence.zero_byte_files:
        (directory / filename).write_bytes(b"")

    for filename, snippets in evidence.snippets:
        path = directory / filename
        existing = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        resolved_snippets = [resolve_marker(snippet, package_name) for snippet in snippets]
        path.write_text(existing + "\n" + "\n".join(resolved_snippets), encoding="utf-8")


def with_fixture(test_body, package_name: str = DEFAULT_PACKAGE) -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-qa-evidence-test."))
    try:
        write_evidence_set(temp_dir, FIXTURE, package_name)
        test_body(temp_dir)
    finally:
        shutil.rmtree(temp_dir)


def failures_for(
    root: Path,
    evidence_sets: tuple[object, ...] = (FIXTURE,),
    package_name: str = DEFAULT_PACKAGE,
) -> list[str]:
    failures, _, _ = checker.qa_evidence_failures(root=root, evidence_sets=evidence_sets, package_name=package_name)
    return failures


def test_valid_fixture_passes() -> None:
    def run(root: Path) -> None:
        failures, pair_count, zero_count = checker.qa_evidence_failures(
            root=root,
            evidence_sets=(FIXTURE,),
            package_name=DEFAULT_PACKAGE,
        )
        assert_equal(failures, [])
        assert_equal(pair_count, 1)
        assert_equal(zero_count, 1)

    with_fixture(run)


def test_package_markers_use_gradle_release_identity() -> None:
    def run(root: Path) -> None:
        failures, pair_count, zero_count = checker.qa_evidence_failures(
            root=root,
            evidence_sets=(FIXTURE,),
            package_name=CUSTOM_PACKAGE,
        )
        assert_equal(failures, [])
        assert_equal(pair_count, 1)
        assert_equal(zero_count, 1)
        assert_failure_contains(failures_for(root, package_name=DEFAULT_PACKAGE), "UI XML evidence is missing")

    with_fixture(run, package_name=CUSTOM_PACKAGE)


def test_missing_report_fails() -> None:
    def run(root: Path) -> None:
        (root / FIXTURE.report).unlink()
        assert_failure_contains(failures_for(root), "missing evidence file: docs/fixture_qa.md")

    with_fixture(run)


def test_missing_evidence_directory_fails() -> None:
    def run(root: Path) -> None:
        shutil.rmtree(root / FIXTURE.directory)
        assert_failure_contains(failures_for(root), "missing evidence directory: qa/fixture")

    with_fixture(run)


def test_invalid_png_signature_fails() -> None:
    def run(root: Path) -> None:
        (root / FIXTURE.directory / "01-home.png").write_bytes(b"not-png" + b"\x00" * 300)
        assert_failure_contains(failures_for(root), "PNG evidence has invalid signature")

    with_fixture(run)


def test_xml_without_package_fails() -> None:
    def run(root: Path) -> None:
        (root / FIXTURE.directory / "01-home.xml").write_text("<hierarchy></hierarchy>" * 30, encoding="utf-8")
        assert_failure_contains(failures_for(root), "UI XML evidence is missing hierarchy/package markers")

    with_fixture(run)


def test_missing_required_snippet_fails() -> None:
    def run(root: Path) -> None:
        path = root / FIXTURE.directory / "device_api.txt"
        path.write_text("34\n", encoding="utf-8")
        assert_failure_contains(failures_for(root), "device_api.txt is missing evidence marker: 35")

    with_fixture(run)


def test_non_empty_zero_log_fails() -> None:
    def run(root: Path) -> None:
        (root / FIXTURE.directory / "app_error_matches.txt").write_text("error\n", encoding="utf-8")
        assert_failure_contains(failures_for(root), "expected empty zero-match log gate file")

    with_fixture(run)


def test_allowed_external_crash_log_passes() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-qa-evidence-test."))
    try:
        write_evidence_set(temp_dir, ALLOWLIST_FIXTURE)
        (temp_dir / ALLOWLIST_FIXTURE.directory / "crash.log").write_text(
            "FATAL EXCEPTION: main com.google.android.dialer",
            encoding="utf-8",
        )
        assert_equal(failures_for(temp_dir, (ALLOWLIST_FIXTURE,)), [])
    finally:
        shutil.rmtree(temp_dir)


def test_app_package_crash_log_fails_even_when_allowlisted() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-qa-evidence-test."))
    try:
        write_evidence_set(temp_dir, ALLOWLIST_FIXTURE)
        (temp_dir / ALLOWLIST_FIXTURE.directory / "crash.log").write_text(DEFAULT_PACKAGE, encoding="utf-8")
        assert_failure_contains(failures_for(temp_dir, (ALLOWLIST_FIXTURE,)), "crash log contains app package")
    finally:
        shutil.rmtree(temp_dir)


def main() -> int:
    tests = [
        test_valid_fixture_passes,
        test_package_markers_use_gradle_release_identity,
        test_missing_report_fails,
        test_missing_evidence_directory_fails,
        test_invalid_png_signature_fails,
        test_xml_without_package_fails,
        test_missing_required_snippet_fails,
        test_non_empty_zero_log_fails,
        test_allowed_external_crash_log_passes,
        test_app_package_crash_log_fails_even_when_allowlisted,
    ]
    for test in tests:
        test()
    print("PASS: QA evidence checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
