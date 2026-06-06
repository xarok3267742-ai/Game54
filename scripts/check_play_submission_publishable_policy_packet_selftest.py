#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_play_submission_publishable_policy_packet.py"

spec = importlib.util.spec_from_file_location("publishable_policy_packet_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def write_valid_packet(packet: Path) -> None:
    text_dir = packet / "text"
    text_dir.mkdir(parents=True, exist_ok=True)
    (text_dir / "privacy_policy_publishable_ru.html").write_text(
        "<!doctype html><html lang=\"ru\"><body>support@poryadok5.app</body></html>\n",
        encoding="utf-8",
    )
    (packet / "checksums.sha256").write_text(
        "abc123  ./text/privacy_policy_publishable_ru.html\n",
        encoding="utf-8",
    )


def with_packet(test_body) -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-publishable-policy-packet-test."))
    try:
        packet = temp_dir / "play-submission"
        write_valid_packet(packet)
        test_body(packet)
    finally:
        shutil.rmtree(temp_dir)


def test_valid_packet_passes() -> None:
    def run(packet: Path) -> None:
        assert_equal(checker.publishable_policy_packet_file_failures(packet), [])

    with_packet(run)


def test_missing_publishable_policy_fails() -> None:
    def run(packet: Path) -> None:
        (packet / "text" / "privacy_policy_publishable_ru.html").unlink()
        failures = checker.publishable_policy_packet_file_failures(packet)
        assert_failure_contains(failures, "did not generate text/privacy_policy_publishable_ru.html")

    with_packet(run)


def test_missing_checksums_fails() -> None:
    def run(packet: Path) -> None:
        (packet / "checksums.sha256").unlink()
        failures = checker.publishable_policy_packet_file_failures(packet)
        assert_failure_contains(failures, "checksums.sha256 is missing")

    with_packet(run)


def test_missing_checksum_entry_fails() -> None:
    def run(packet: Path) -> None:
        (packet / "checksums.sha256").write_text("abc123  ./README.md\n", encoding="utf-8")
        failures = checker.publishable_policy_packet_file_failures(packet)
        assert_failure_contains(failures, "does not include text/privacy_policy_publishable_ru.html")

    with_packet(run)


def main() -> int:
    tests = [
        test_valid_packet_passes,
        test_missing_publishable_policy_fails,
        test_missing_checksums_fails,
        test_missing_checksum_entry_fails,
    ]
    for test in tests:
        test()
    print("PASS: Play submission publishable policy packet checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
