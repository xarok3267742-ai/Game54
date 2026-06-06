#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_publishable_privacy_policy.py"

spec = importlib.util.spec_from_file_location("publishable_privacy_policy_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

SUPPORT_EMAIL = "support@poryadok5.app"


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def valid_policy_html(email: str = SUPPORT_EMAIL) -> str:
    return f"""<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>Политика конфиденциальности</title></head>
<body>
<h1>Политика конфиденциальности: Порядок 5</h1>
<p>Порядок 5 не собирает и не передаёт персональные данные.</p>
<p>Приложение не использует рекламу, аналитические SDK или crash-reporting SDK.</p>
<p>Контактный email разработчика: <a href="mailto:{email}">{email}</a></p>
</body>
</html>
"""


def with_temp_policy(test_body) -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-publishable-policy-test."))
    try:
        policy = temp_dir / "privacy_policy_publishable_ru.html"
        policy.write_text(valid_policy_html(), encoding="utf-8")
        test_body(policy)
    finally:
        shutil.rmtree(temp_dir)


def test_valid_policy_passes() -> None:
    def run(policy: Path) -> None:
        assert_equal(checker.publishable_privacy_policy_failures(policy, True, SUPPORT_EMAIL), [])

    with_temp_policy(run)


def test_optional_missing_policy_passes() -> None:
    missing = Path(tempfile.mkdtemp(prefix="poryadok5-publishable-policy-test.")) / "missing.html"
    try:
        assert_equal(checker.publishable_privacy_policy_failures(missing, False, ""), [])
    finally:
        shutil.rmtree(missing.parent)


def test_required_missing_support_email_fails() -> None:
    def run(policy: Path) -> None:
        failures = checker.publishable_privacy_policy_failures(policy, True, "")
        assert_failure_contains(failures, "set PORYADOK5_SUPPORT_EMAIL")

    with_temp_policy(run)


def test_required_missing_policy_file_fails() -> None:
    missing = Path(tempfile.mkdtemp(prefix="poryadok5-publishable-policy-test.")) / "missing.html"
    try:
        failures = checker.publishable_privacy_policy_failures(missing, True, SUPPORT_EMAIL)
        assert_failure_contains(failures, "publishable privacy policy is missing")
    finally:
        shutil.rmtree(missing.parent)


def test_reserved_support_email_fails() -> None:
    def run(policy: Path) -> None:
        failures = checker.publishable_privacy_policy_failures(policy, True, "support@example.com")
        assert_failure_contains(failures, "real non-reserved email")

    with_temp_policy(run)


def test_missing_requested_support_email_fails() -> None:
    def run(policy: Path) -> None:
        failures = checker.publishable_privacy_policy_failures(policy, True, "help@poryadok5.app")
        assert_failure_contains(failures, "does not contain the requested support email")

    with_temp_policy(run)


def test_pre_publication_contact_instruction_fails() -> None:
    def run(policy: Path) -> None:
        policy.write_text(
            valid_policy_html().replace("Контактный email разработчика:", "Перед публикацией замените эту строку"),
            encoding="utf-8",
        )
        failures = checker.publishable_privacy_policy_failures(policy, True, SUPPORT_EMAIL)
        assert_failure_contains(failures, "pre-publication contact instruction")

    with_temp_policy(run)


def main() -> int:
    tests = [
        test_valid_policy_passes,
        test_optional_missing_policy_passes,
        test_required_missing_support_email_fails,
        test_required_missing_policy_file_fails,
        test_reserved_support_email_fails,
        test_missing_requested_support_email_fails,
        test_pre_publication_contact_instruction_fails,
    ]
    for test in tests:
        test()
    print("PASS: publishable privacy policy checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
