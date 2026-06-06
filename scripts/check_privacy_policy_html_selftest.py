#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_privacy_policy_html.py"

spec = importlib.util.spec_from_file_location("privacy_policy_html_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def valid_policy_html() -> str:
    required_text = "\n".join(f"<p>{snippet}</p>" for snippet in checker.REQUIRED_SNIPPETS)
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Политика конфиденциальности: Порядок 5</title>
</head>
<body>
  <h1>Политика конфиденциальности: Порядок 5</h1>
  {required_text}
  <a href="mailto:support@example.com">контакт</a>
</body>
</html>
"""


def failures_for(html: str) -> list[str]:
    return checker.privacy_policy_failures(html)


def test_valid_policy_passes() -> None:
    assert_equal(failures_for(valid_policy_html()), [])


def test_wrong_language_fails() -> None:
    html = valid_policy_html().replace('<html lang="ru">', '<html lang="en">')
    assert_failure_contains(failures_for(html), "html lang must be ru")


def test_missing_title_fails() -> None:
    html = valid_policy_html().replace("<title>Политика конфиденциальности: Порядок 5</title>", "")
    assert_failure_contains(failures_for(html), "missing <title>")


def test_missing_h1_fails() -> None:
    html = valid_policy_html().replace("<h1>Политика конфиденциальности: Порядок 5</h1>", "")
    assert_failure_contains(failures_for(html), "missing <h1>")


def test_missing_required_text_fails() -> None:
    html = valid_policy_html().replace("не собирает и не передаёт персональные данные", "не хватает ключевой строки")
    assert_failure_contains(failures_for(html), "missing required text")


def test_external_href_fails() -> None:
    html = valid_policy_html().replace("mailto:support@example.com", "https://example.com/privacy")
    assert_failure_contains(failures_for(html), "external references are not allowed")


def test_external_script_fails() -> None:
    html = valid_policy_html().replace("</body>", '<script src="https://example.com/app.js"></script></body>')
    failures = failures_for(html)
    assert_failure_contains(failures, "external references are not allowed")
    assert_failure_contains(failures, "forbidden pattern found")


def test_tracking_marker_fails() -> None:
    html = valid_policy_html().replace("</body>", "<p>google-analytics</p></body>")
    assert_failure_contains(failures_for(html), "forbidden pattern found")


def main() -> int:
    tests = [
        test_valid_policy_passes,
        test_wrong_language_fails,
        test_missing_title_fails,
        test_missing_h1_fails,
        test_missing_required_text_fails,
        test_external_href_fails,
        test_external_script_fails,
        test_tracking_marker_fails,
    ]
    for test in tests:
        test()
    print("PASS: privacy policy HTML checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
