#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock
from urllib import error

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_play_upload_external_inputs.py"


VALID_ENV = {
    "PORYADOK5_PRIVACY_POLICY_URL": "https://privacy.poryadok5.app/policy",
    "PORYADOK5_SUPPORT_EMAIL": "support@poryadok5.app",
    "PORYADOK5_FEATURE_GRAPHIC_APPROVED": "yes",
    "PORYADOK5_DATA_SAFETY_CONFIRMED": "yes",
    "PORYADOK5_TARGET_AUDIENCE_CONFIRMED": "yes",
    "PORYADOK5_CONTENT_RATING_CONFIRMED": "yes",
    "PORYADOK5_INTERNAL_TESTING_CONFIRMED": "yes",
}

VALID_POLICY_HTML = """
<html><body>
  <h1>Политика конфиденциальности: Порядок 5</h1>
  <p>Приложение не собирает и не передаёт персональные данные.</p>
  <p>Приложение не использует рекламу, аналитические SDK, crash-reporting SDK.</p>
  <p>support@poryadok5.app</p>
</body></html>
"""


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_play_upload_external_inputs", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, *, status: int, content_type: str, body: str) -> None:
        self.status = status
        self.headers = {"Content-Type": content_type}
        self._body = body.encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read(self, limit: int) -> bytes:
        return self._body[:limit]


class PlayUploadExternalInputsSelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def call_main(self) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = self.module.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_complete_inputs_and_remote_policy_pass(self) -> None:
        with mock.patch.object(
            self.module.request,
            "urlopen",
            return_value=FakeResponse(status=200, content_type="text/html; charset=utf-8", body=VALID_POLICY_HTML),
        ):
            self.assertEqual(self.module.external_input_failures(VALID_ENV), [])

    def test_missing_inputs_fail_without_network(self) -> None:
        with mock.patch.object(self.module.request, "urlopen") as urlopen_mock:
            failures = self.module.external_input_failures({})

        self.assertTrue(failures)
        self.assertIn("set PORYADOK5_PRIVACY_POLICY_URL", "\n".join(failures))
        self.assertIn("set PORYADOK5_SUPPORT_EMAIL", "\n".join(failures))
        self.assertIn("set PORYADOK5_DATA_SAFETY_CONFIRMED=yes", "\n".join(failures))
        urlopen_mock.assert_not_called()

    def test_invalid_yes_flag_value_fails(self) -> None:
        env = dict(VALID_ENV)
        env["PORYADOK5_FEATURE_GRAPHIC_APPROVED"] = "true"
        with mock.patch.object(
            self.module.request,
            "urlopen",
            return_value=FakeResponse(status=200, content_type="text/html; charset=utf-8", body=VALID_POLICY_HTML),
        ):
            failures = self.module.external_input_failures(env)

        self.assertIn("set PORYADOK5_FEATURE_GRAPHIC_APPROVED=yes", "\n".join(failures))

    def test_remote_policy_http_error_fails(self) -> None:
        http_error = error.HTTPError(
            "https://privacy.poryadok5.app/policy",
            404,
            "Not Found",
            hdrs=None,
            fp=None,
        )
        with mock.patch.object(self.module.request, "urlopen", side_effect=http_error):
            failures = self.module.external_input_failures(VALID_ENV)

        self.assertEqual(failures, ["privacy policy URL must return HTTP 200, got 404"])

    def test_remote_policy_missing_support_email_fails(self) -> None:
        body = VALID_POLICY_HTML.replace("support@poryadok5.app", "")
        with mock.patch.object(
            self.module.request,
            "urlopen",
            return_value=FakeResponse(status=200, content_type="text/html; charset=utf-8", body=body),
        ):
            failures = self.module.external_input_failures(VALID_ENV)

        self.assertEqual(failures, ["published privacy policy does not contain PORYADOK5_SUPPORT_EMAIL"])

    def test_main_reports_failures(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=True):
            status, stdout, stderr = self.call_main()

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("Play upload external input check failed", stderr)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PlayUploadExternalInputsSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: Play upload external inputs self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
