#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock
from urllib import error

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_play_upload_readiness.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_play_upload_readiness", MODULE_PATH)
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


class PlayUploadReadinessSelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def call_silently(self, func: object, *args: object) -> object:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return func(*args)

    def call_with_output(self, func: object, *args: object) -> tuple[object, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = func(*args)
        return result, stdout.getvalue(), stderr.getvalue()

    def test_url_validation_rejects_reserved_hosts(self) -> None:
        self.assertFalse(self.module.validate_url("http://privacy.poryadok5.app/policy"))
        self.assertFalse(self.module.validate_url("https://example.com/poryadok5/privacy"))
        self.assertFalse(self.module.validate_url("https://example.com:443/poryadok5/privacy"))
        self.assertFalse(self.module.validate_url("https://localhost/privacy"))
        self.assertFalse(self.module.validate_url("https://your-domain.example/poryadok5/privacy"))
        self.assertFalse(self.module.validate_url("https://your-domain.example:443/poryadok5/privacy"))
        self.assertTrue(self.module.validate_url("https://privacy.poryadok5.app/policy"))
        self.assertTrue(self.module.validate_url("https://privacy.poryadok5.app:443/policy"))

    def test_email_validation_rejects_reserved_domains(self) -> None:
        self.assertFalse(self.module.validate_email("support@example.com"))
        self.assertFalse(self.module.validate_email("support@your-domain.example"))
        self.assertFalse(self.module.validate_email("support-at-poryadok5.app"))
        self.assertTrue(self.module.validate_email("support@poryadok5.app"))

    def test_visible_text_extraction_removes_code_blocks(self) -> None:
        text = self.module.extract_visible_text(
            "<html><head><style>.x{color:red}</style></head>"
            "<body><script>window.track=true</script><p>Порядок&nbsp;5</p></body></html>",
        )
        self.assertEqual(text, "Порядок 5")

    def test_remote_privacy_policy_accepts_valid_content(self) -> None:
        body = """
        <html><body>
          <h1>Политика конфиденциальности: Порядок 5</h1>
          <p>Приложение не собирает и не передаёт персональные данные.</p>
          <p>Приложение не использует рекламу, аналитические SDK, crash-reporting SDK.</p>
          <p>support@poryadok5.app</p>
        </body></html>
        """
        with mock.patch.object(
            self.module.request,
            "urlopen",
            return_value=FakeResponse(status=200, content_type="text/html; charset=utf-8", body=body),
        ):
            self.assertTrue(
                self.call_silently(
                    self.module.verify_remote_privacy_policy,
                    "https://privacy.poryadok5.app/policy",
                    "support@poryadok5.app",
                    True,
                ),
            )

    def test_remote_privacy_policy_rejects_missing_support_email(self) -> None:
        body = """
        <html><body>
          <h1>Политика конфиденциальности: Порядок 5</h1>
          <p>Приложение не собирает и не передаёт персональные данные.</p>
          <p>Приложение не использует рекламу, аналитические SDK, crash-reporting SDK.</p>
        </body></html>
        """
        with mock.patch.object(
            self.module.request,
            "urlopen",
            return_value=FakeResponse(status=200, content_type="text/html; charset=utf-8", body=body),
        ):
            self.assertFalse(
                self.call_silently(
                    self.module.verify_remote_privacy_policy,
                    "https://privacy.poryadok5.app/policy",
                    "support@poryadok5.app",
                    True,
                ),
            )

    def test_remote_privacy_policy_handles_unreachable_url(self) -> None:
        with mock.patch.object(
            self.module.request,
            "urlopen",
            side_effect=error.URLError("offline"),
        ):
            self.assertTrue(
                self.call_silently(
                    self.module.verify_remote_privacy_policy,
                    "https://privacy.poryadok5.app/policy",
                    "support@poryadok5.app",
                    False,
                ),
            )
            self.assertFalse(
                self.call_silently(
                    self.module.verify_remote_privacy_policy,
                    "https://privacy.poryadok5.app/policy",
                    "support@poryadok5.app",
                    True,
                ),
            )

    def test_remote_privacy_policy_handles_timeout_without_crashing(self) -> None:
        with mock.patch.object(
            self.module.request,
            "urlopen",
            side_effect=TimeoutError("timed out"),
        ):
            self.assertTrue(
                self.call_silently(
                    self.module.verify_remote_privacy_policy,
                    "https://privacy.poryadok5.app/policy",
                    "support@poryadok5.app",
                    False,
                ),
            )
            self.assertFalse(
                self.call_silently(
                    self.module.verify_remote_privacy_policy,
                    "https://privacy.poryadok5.app/policy",
                    "support@poryadok5.app",
                    True,
                ),
            )

    def test_remote_privacy_policy_reports_http_status(self) -> None:
        http_error = error.HTTPError(
            "https://privacy.poryadok5.app/policy",
            404,
            "Not Found",
            hdrs=None,
            fp=None,
        )
        with mock.patch.object(
            self.module.request,
            "urlopen",
            side_effect=http_error,
        ):
            soft_result, soft_stdout, soft_stderr = self.call_with_output(
                self.module.verify_remote_privacy_policy,
                "https://privacy.poryadok5.app/policy",
                "support@poryadok5.app",
                False,
            )
            strict_result, strict_stdout, strict_stderr = self.call_with_output(
                self.module.verify_remote_privacy_policy,
                "https://privacy.poryadok5.app/policy",
                "support@poryadok5.app",
                True,
            )

        self.assertTrue(soft_result)
        self.assertEqual(soft_stderr, "")
        self.assertIn("WARN: privacy policy URL returned HTTP 404", soft_stdout)
        self.assertFalse(strict_result)
        self.assertEqual(strict_stdout, "")
        self.assertIn("FAIL: privacy policy URL must return HTTP 200, got 404", strict_stderr)

    def test_publishable_privacy_policy_accepts_generated_contact_file(self) -> None:
        body = """
        <html><body>
          <h1>Политика конфиденциальности: Порядок 5</h1>
          <p>Приложение не собирает и не передаёт персональные данные.</p>
          <p>Приложение не использует рекламу, аналитические SDK, crash-reporting SDK.</p>
          <p class="contact-note">Контактный email разработчика:
            <a href="mailto:support@poryadok5.app">support@poryadok5.app</a>
          </p>
        </body></html>
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "privacy.html"
            path.write_text(body, encoding="utf-8")
            with mock.patch.object(self.module, "PUBLISHABLE_PRIVACY_HTML", path):
                self.assertEqual(
                    self.call_silently(
                        self.module.publishable_privacy_policy_failures,
                        "support@poryadok5.app",
                    ),
                    [],
                )
                self.assertTrue(
                    self.call_silently(
                        self.module.publishable_privacy_policy_ready,
                        "support@poryadok5.app",
                    ),
                )

    def test_publishable_privacy_policy_rejects_contact_instruction(self) -> None:
        body = """
        <html><body>
          <h1>Политика конфиденциальности: Порядок 5</h1>
          <p>Приложение не собирает и не передаёт персональные данные.</p>
          <p>Приложение не использует рекламу, аналитические SDK, crash-reporting SDK.</p>
          <p class="contact-note">Перед публикацией замените эту строку</p>
        </body></html>
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "privacy.html"
            path.write_text(body, encoding="utf-8")
            with mock.patch.object(self.module, "PUBLISHABLE_PRIVACY_HTML", path):
                failures = self.call_silently(
                    self.module.publishable_privacy_policy_failures,
                    "support@poryadok5.app",
                )
                self.assertTrue(failures)
                self.assertFalse(
                    self.call_silently(
                        self.module.publishable_privacy_policy_ready,
                        "support@poryadok5.app",
                    ),
                )

    def test_artifact_manifest_soft_reports_upload_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "artifact_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "playUploadReady": False,
                        "uploadBlockers": [
                            "signed_upload_aab_missing",
                            "support_email_missing",
                        ],
                    },
                ),
                encoding="utf-8",
            )

            with mock.patch.object(self.module, "RELEASE_ARTIFACT_MANIFEST", manifest_path):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_artifact_manifest_upload_state,
                    False,
                )

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("NOTE: release artifact manifest upload blockers remain", stdout)
        self.assertIn("signed_upload_aab_missing, support_email_missing", stdout)

    def test_artifact_manifest_strict_rejects_upload_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "artifact_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "playUploadReady": False,
                        "uploadBlockers": [
                            "signed_upload_aab_missing",
                            "support_email_missing",
                        ],
                    },
                ),
                encoding="utf-8",
            )

            with mock.patch.object(self.module, "RELEASE_ARTIFACT_MANIFEST", manifest_path):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_artifact_manifest_upload_state,
                    True,
                )

        self.assertFalse(result)
        self.assertEqual(stdout, "")
        self.assertIn(
            "FAIL: release artifact manifest still has upload blockers: "
            "signed_upload_aab_missing, support_email_missing",
            stderr,
        )

    def test_artifact_manifest_strict_accepts_upload_ready_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "artifact_manifest.json"
            manifest_path.write_text(
                json.dumps({"playUploadReady": True, "uploadBlockers": []}),
                encoding="utf-8",
            )

            with mock.patch.object(self.module, "RELEASE_ARTIFACT_MANIFEST", manifest_path):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_artifact_manifest_upload_state,
                    True,
                )

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("PASS: release artifact manifest marks Play upload as ready", stdout)

    def test_artifact_manifest_current_state_checker_passes_through_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "checker.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "RELEASE_ARTIFACT_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(0, "PASS: release artifact manifest matches current build and packet state\n"),
                ),
            ):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_artifact_manifest_current_state,
                )

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("PASS: release artifact manifest matches current build and packet state", stdout)

    def test_artifact_manifest_current_state_checker_fails_on_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "checker.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "RELEASE_ARTIFACT_CHECKER", checker_path),
                mock.patch.object(self.module, "run", return_value=(1, "sha256 is out of sync\n")),
            ):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_artifact_manifest_current_state,
                )

        self.assertFalse(result)
        self.assertIn("sha256 is out of sync", stdout)
        self.assertIn("FAIL: release artifact manifest does not match current build and packet state", stderr)

    def test_upload_blocker_handoff_checker_passes_through_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "upload_blockers.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "UPLOAD_BLOCKERS_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(0, "PASS: Play upload blocker handoff matches release artifact manifest\n"),
                ),
            ):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_upload_blocker_handoff_state,
                )

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("PASS: Play upload blocker handoff matches release artifact manifest", stdout)

    def test_upload_blocker_handoff_checker_fails_on_stale_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "upload_blockers.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "UPLOAD_BLOCKERS_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(
                        1,
                        "Play upload blocker handoff check failed:\n"
                        "  upload blocker handoff blocker order/content is out of sync\n",
                    ),
                ),
            ):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_upload_blocker_handoff_state,
                )

        self.assertFalse(result)
        self.assertIn("upload blocker handoff blocker order/content is out of sync", stdout)
        self.assertIn(
            "FAIL: Play upload blocker handoff is not synchronized with the release artifact manifest",
            stderr,
        )

    def test_packet_sync_checker_passes_through_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "packet_sync.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "PACKET_SYNC_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(
                        0,
                        "PASS: Play submission packet files match source materials and checksums cover current packet files\n",
                    ),
                ),
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_packet_sync_state)

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("PASS: Play submission packet files match source materials", stdout)

    def test_packet_sync_checker_fails_on_stale_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "packet_sync.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "PACKET_SYNC_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(1, "Play submission packet sync check failed:\n  packet file is stale\n"),
                ),
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_packet_sync_state)

        self.assertFalse(result)
        self.assertIn("packet file is stale", stdout)
        self.assertIn("FAIL: Play submission packet is not synchronized with source materials", stderr)

    def test_packet_doc_coverage_checker_passes_through_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "packet_doc_coverage.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "PACKET_DOC_COVERAGE_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(
                        0,
                        "PASS: Play submission packet covers 47 required RC documents from documentation inventory\n",
                    ),
                ),
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_packet_doc_coverage_state)

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("PASS: Play submission packet covers 47 required RC documents", stdout)

    def test_packet_doc_coverage_checker_fails_on_missing_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "packet_doc_coverage.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "PACKET_DOC_COVERAGE_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(
                        1,
                        "Play submission documentation coverage check failed:\n"
                        "  required document packet copy is missing: docs/product_spec.md\n",
                    ),
                ),
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_packet_doc_coverage_state)

        self.assertFalse(result)
        self.assertIn("required document packet copy is missing: docs/product_spec.md", stdout)
        self.assertIn("FAIL: Play submission packet does not cover required RC documentation", stderr)

    def test_soft_release_signing_inputs_accept_absent_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "checker.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "SIGNING_INPUT_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(0, "PASS: release signing inputs are absent; local RC will remain unsigned\n"),
                ) as run_mock,
            ):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_release_signing_inputs,
                    False,
                )

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("PASS: release signing inputs are absent", stdout)
        self.assertNotIn("--require", run_mock.call_args.args[0])

    def test_strict_release_signing_inputs_require_external_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            checker_path = Path(tmp_dir) / "checker.py"
            checker_path.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "SIGNING_INPUT_CHECKER", checker_path),
                mock.patch.object(
                    self.module,
                    "run",
                    return_value=(1, "FAIL: release signing inputs are not configured\n"),
                ) as run_mock,
            ):
                result, stdout, stderr = self.call_with_output(
                    self.module.verify_release_signing_inputs,
                    True,
                )

        self.assertFalse(result)
        self.assertIn("--require", run_mock.call_args.args[0])
        self.assertIn("FAIL: release signing inputs are not configured", stdout)
        self.assertIn("FAIL: release signing inputs are required for Play upload readiness", stderr)

    def test_play_console_evidence_passes_through_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            forms_checker = tmp_path / "forms.py"
            policy_checker = tmp_path / "policy.py"
            forms_checker.write_text("# test helper\n", encoding="utf-8")
            policy_checker.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "PLAY_FORMS_CHECKER", forms_checker),
                mock.patch.object(self.module, "POLICY_CONTENT_CHECKER", policy_checker),
                mock.patch.object(
                    self.module,
                    "run",
                    side_effect=[
                        (0, "PASS: Play Console form answers match the current RC model\n"),
                        (0, "PASS: policy content risk scan matches Play form claims\n"),
                    ],
                ) as run_mock,
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_play_console_evidence)

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("PASS: Play Console form answers match the current RC model", stdout)
        self.assertIn("PASS: policy content risk scan matches Play form claims", stdout)
        self.assertEqual(
            [call.args[0] for call in run_mock.call_args_list],
            [
                [sys.executable, str(forms_checker)],
                [sys.executable, str(policy_checker)],
            ],
        )

    def test_play_console_evidence_rejects_forms_checker_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            forms_checker = tmp_path / "forms.py"
            policy_checker = tmp_path / "policy.py"
            forms_checker.write_text("# test helper\n", encoding="utf-8")
            policy_checker.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "PLAY_FORMS_CHECKER", forms_checker),
                mock.patch.object(self.module, "POLICY_CONTENT_CHECKER", policy_checker),
                mock.patch.object(
                    self.module,
                    "run",
                    side_effect=[
                        (1, "Play Console forms check failed:\n  dataSafety.collectsUserData must be false\n"),
                        (0, "PASS: policy content risk scan matches Play form claims\n"),
                    ],
                ),
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_play_console_evidence)

        self.assertFalse(result)
        self.assertIn("Play Console forms check failed", stdout)
        self.assertIn("PASS: policy content risk scan matches Play form claims", stdout)
        self.assertIn("FAIL: Play Console forms checker failed", stderr)

    def test_play_console_evidence_rejects_policy_checker_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            forms_checker = tmp_path / "forms.py"
            policy_checker = tmp_path / "policy.py"
            forms_checker.write_text("# test helper\n", encoding="utf-8")
            policy_checker.write_text("# test helper\n", encoding="utf-8")

            with (
                mock.patch.object(self.module, "PLAY_FORMS_CHECKER", forms_checker),
                mock.patch.object(self.module, "POLICY_CONTENT_CHECKER", policy_checker),
                mock.patch.object(
                    self.module,
                    "run",
                    side_effect=[
                        (0, "PASS: Play Console form answers match the current RC model\n"),
                        (1, "Policy content risk check failed:\n  violence: risky term matched\n"),
                    ],
                ),
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_play_console_evidence)

        self.assertFalse(result)
        self.assertIn("PASS: Play Console form answers match the current RC model", stdout)
        self.assertIn("Policy content risk check failed", stdout)
        self.assertIn("FAIL: policy content risk checker failed", stderr)

    def test_soft_manual_inputs_warn_on_invalid_external_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            privacy_html = tmp_path / "privacy_policy_ru.html"
            publishable_html = tmp_path / "privacy_policy_publishable_ru.html"
            feature_graphic = tmp_path / "feature.png"
            play_icon = tmp_path / "icon.png"
            forms_answers = tmp_path / "forms.json"

            privacy_html.write_text(
                '<html><body><p class="contact-note">Перед публикацией замените эту строку</p></body></html>',
                encoding="utf-8",
            )
            feature_graphic.write_bytes(b"png")
            play_icon.write_bytes(b"png")
            forms_answers.write_text("{}", encoding="utf-8")

            env = {
                "PORYADOK5_PRIVACY_POLICY_URL": "https://example.com:443/privacy",
                "PORYADOK5_SUPPORT_EMAIL": "support@example.com",
                "PORYADOK5_FEATURE_GRAPHIC_APPROVED": "true",
            }

            with (
                mock.patch.object(self.module, "PRIVACY_HTML", privacy_html),
                mock.patch.object(self.module, "PUBLISHABLE_PRIVACY_HTML", publishable_html),
                mock.patch.object(self.module, "FEATURE_GRAPHIC", feature_graphic),
                mock.patch.object(self.module, "PLAY_STORE_ICON", play_icon),
                mock.patch.object(self.module, "FORMS_ANSWERS", forms_answers),
                mock.patch.dict("os.environ", env, clear=True),
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_manual_upload_inputs, False)

        self.assertTrue(result)
        self.assertEqual(stderr, "")
        self.assertIn("WARN: PORYADOK5_PRIVACY_POLICY_URL is set but is not a valid public HTTPS URL", stdout)
        self.assertIn("WARN: PORYADOK5_SUPPORT_EMAIL is set but is not a valid non-reserved support email", stdout)
        self.assertIn("WARN: PORYADOK5_FEATURE_GRAPHIC_APPROVED is set to 'true'", stdout)

    def test_strict_manual_inputs_fail_on_invalid_external_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            privacy_html = tmp_path / "privacy_policy_ru.html"
            publishable_html = tmp_path / "privacy_policy_publishable_ru.html"
            feature_graphic = tmp_path / "feature.png"
            play_icon = tmp_path / "icon.png"
            forms_answers = tmp_path / "forms.json"

            privacy_html.write_text(
                '<html><body><p class="contact-note">Перед публикацией замените эту строку</p></body></html>',
                encoding="utf-8",
            )
            feature_graphic.write_bytes(b"png")
            play_icon.write_bytes(b"png")
            forms_answers.write_text("{}", encoding="utf-8")

            env = {
                "PORYADOK5_PRIVACY_POLICY_URL": "https://example.com:443/privacy",
                "PORYADOK5_SUPPORT_EMAIL": "support@example.com",
            }

            with (
                mock.patch.object(self.module, "PRIVACY_HTML", privacy_html),
                mock.patch.object(self.module, "PUBLISHABLE_PRIVACY_HTML", publishable_html),
                mock.patch.object(self.module, "FEATURE_GRAPHIC", feature_graphic),
                mock.patch.object(self.module, "PLAY_STORE_ICON", play_icon),
                mock.patch.object(self.module, "FORMS_ANSWERS", forms_answers),
                mock.patch.dict("os.environ", env, clear=True),
            ):
                result, stdout, stderr = self.call_with_output(self.module.verify_manual_upload_inputs, True)

        self.assertFalse(result)
        self.assertIn("PASS: feature graphic candidate exists", stdout)
        self.assertIn("FAIL: PORYADOK5_PRIVACY_POLICY_URL is set but is not a valid public HTTPS URL", stderr)
        self.assertIn("FAIL: PORYADOK5_SUPPORT_EMAIL is set but is not a valid non-reserved support email", stderr)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PlayUploadReadinessSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: Play upload readiness self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
