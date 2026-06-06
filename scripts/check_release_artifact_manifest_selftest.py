#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_release_artifact_manifest.py"

VALID_POLICY_HTML = """
<html><body>
  <h1>Политика конфиденциальности: Порядок 5</h1>
  <p>Приложение не собирает и не передаёт персональные данные.</p>
  <p>Приложение не использует рекламу, аналитические SDK, crash-reporting SDK.</p>
  <p class="contact-note">Контактный email разработчика:
    <a href="mailto:support@poryadok5.app">support@poryadok5.app</a>
  </p>
</body></html>
"""

SOURCE_POLICY_HTML = """
<html><body>
  <h1>Политика конфиденциальности: Порядок 5</h1>
  <p>Перед публикацией замените эту строку</p>
</body></html>
"""


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("generate_release_artifact_manifest", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseArtifactManifestSelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_privacy_url_validation_rejects_reserved_hosts_with_ports(self) -> None:
        invalid_urls = (
            "http://privacy.poryadok5.app/policy",
            "https://example.com/policy",
            "https://example.com:443/policy",
            "https://your-domain.example/policy",
            "https://your-domain.example:443/policy",
            "https://localhost/privacy",
            "https://127.0.0.1/privacy",
        )
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.module.validate_url(url))

        self.assertTrue(self.module.validate_url("https://privacy.poryadok5.app/policy"))
        self.assertTrue(self.module.validate_url("https://privacy.poryadok5.app:443/policy"))

    def test_upload_blockers_report_local_unsigned_rc_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_policy = tmp_path / "privacy_policy_ru.html"
            publishable_policy = tmp_path / "privacy_policy_publishable_ru.html"
            source_policy.write_text(SOURCE_POLICY_HTML, encoding="utf-8")

            with (
                mock.patch.object(self.module, "PRIVACY_HTML", source_policy),
                mock.patch.object(self.module, "PUBLISHABLE_PRIVACY_HTML", publishable_policy),
                mock.patch.object(self.module, "release_signing_inputs_ready", return_value=False),
                mock.patch.object(self.module, "checker_passes", return_value=True),
                mock.patch.dict("os.environ", {}, clear=True),
            ):
                blockers = self.module.upload_blockers("unsigned", False)

        self.assertIn("release_signing_inputs_missing", blockers)
        self.assertIn("signed_upload_aab_missing", blockers)
        self.assertIn("public_privacy_policy_url_missing", blockers)
        self.assertIn("support_email_missing", blockers)
        self.assertIn("privacy_policy_contact_not_replaced", blockers)
        self.assertIn("feature_graphic_not_confirmed", blockers)
        self.assertIn("data_safety_not_confirmed", blockers)
        self.assertIn("target_audience_not_confirmed", blockers)
        self.assertIn("content_rating_not_confirmed", blockers)
        self.assertIn("internal_testing_not_confirmed", blockers)

    def test_upload_blockers_clear_when_external_inputs_are_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_policy = tmp_path / "privacy_policy_ru.html"
            publishable_policy = tmp_path / "privacy_policy_publishable_ru.html"
            source_policy.write_text(SOURCE_POLICY_HTML, encoding="utf-8")
            publishable_policy.write_text(VALID_POLICY_HTML, encoding="utf-8")

            env = {
                "PORYADOK5_PRIVACY_POLICY_URL": "https://privacy.poryadok5.app/policy",
                "PORYADOK5_SUPPORT_EMAIL": "support@poryadok5.app",
                "PORYADOK5_FEATURE_GRAPHIC_APPROVED": "yes",
                "PORYADOK5_DATA_SAFETY_CONFIRMED": "yes",
                "PORYADOK5_TARGET_AUDIENCE_CONFIRMED": "yes",
                "PORYADOK5_CONTENT_RATING_CONFIRMED": "yes",
                "PORYADOK5_INTERNAL_TESTING_CONFIRMED": "yes",
            }

            with (
                mock.patch.object(self.module, "PRIVACY_HTML", source_policy),
                mock.patch.object(self.module, "PUBLISHABLE_PRIVACY_HTML", publishable_policy),
                mock.patch.object(self.module, "release_signing_inputs_ready", return_value=True),
                mock.patch.object(self.module, "checker_passes", return_value=True),
                mock.patch.dict("os.environ", env, clear=True),
            ):
                blockers = self.module.upload_blockers("signed_verified", True)

        self.assertEqual(blockers, [])

    def test_upload_blockers_report_signed_aab_without_current_signing_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_policy = tmp_path / "privacy_policy_ru.html"
            publishable_policy = tmp_path / "privacy_policy_publishable_ru.html"
            source_policy.write_text(SOURCE_POLICY_HTML, encoding="utf-8")
            publishable_policy.write_text(VALID_POLICY_HTML, encoding="utf-8")

            env = {
                "PORYADOK5_PRIVACY_POLICY_URL": "https://privacy.poryadok5.app/policy",
                "PORYADOK5_SUPPORT_EMAIL": "support@poryadok5.app",
                "PORYADOK5_FEATURE_GRAPHIC_APPROVED": "yes",
                "PORYADOK5_DATA_SAFETY_CONFIRMED": "yes",
                "PORYADOK5_TARGET_AUDIENCE_CONFIRMED": "yes",
                "PORYADOK5_CONTENT_RATING_CONFIRMED": "yes",
                "PORYADOK5_INTERNAL_TESTING_CONFIRMED": "yes",
            }

            with (
                mock.patch.object(self.module, "PRIVACY_HTML", source_policy),
                mock.patch.object(self.module, "PUBLISHABLE_PRIVACY_HTML", publishable_policy),
                mock.patch.object(self.module, "release_signing_inputs_ready", return_value=False),
                mock.patch.object(self.module, "checker_passes", return_value=True),
                mock.patch.dict("os.environ", env, clear=True),
            ):
                blockers = self.module.upload_blockers("signed_verified", True)

        self.assertEqual(blockers, ["release_signing_inputs_missing"])

    def test_upload_blockers_report_play_form_and_policy_evidence_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_policy = tmp_path / "privacy_policy_ru.html"
            publishable_policy = tmp_path / "privacy_policy_publishable_ru.html"
            source_policy.write_text(SOURCE_POLICY_HTML, encoding="utf-8")
            publishable_policy.write_text(VALID_POLICY_HTML, encoding="utf-8")

            env = {
                "PORYADOK5_PRIVACY_POLICY_URL": "https://privacy.poryadok5.app/policy",
                "PORYADOK5_SUPPORT_EMAIL": "support@poryadok5.app",
                "PORYADOK5_FEATURE_GRAPHIC_APPROVED": "yes",
                "PORYADOK5_DATA_SAFETY_CONFIRMED": "yes",
                "PORYADOK5_TARGET_AUDIENCE_CONFIRMED": "yes",
                "PORYADOK5_CONTENT_RATING_CONFIRMED": "yes",
                "PORYADOK5_INTERNAL_TESTING_CONFIRMED": "yes",
            }

            with (
                mock.patch.object(self.module, "PRIVACY_HTML", source_policy),
                mock.patch.object(self.module, "PUBLISHABLE_PRIVACY_HTML", publishable_policy),
                mock.patch.object(self.module, "release_signing_inputs_ready", return_value=True),
                mock.patch.object(self.module, "checker_passes", return_value=False),
                mock.patch.dict("os.environ", env, clear=True),
            ):
                blockers = self.module.upload_blockers("signed_verified", True)

        self.assertEqual(
            blockers,
            [
                "play_console_forms_evidence_failed",
                "policy_content_risk_evidence_failed",
            ],
        )

    def test_main_uses_gradle_release_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            release_dir = tmp_path / "play-submission" / "release"
            release_dir.mkdir(parents=True)
            artifact_status = release_dir / "artifact_status.properties"
            artifact_status.write_text(
                "signed_or_configured=false\n"
                "artifact=not_included_unsigned_local_rc\n"
                "reason=release AAB is unsigned\n",
                encoding="utf-8",
            )
            output = release_dir / "artifact_manifest.json"

            with (
                mock.patch.object(self.module, "RELEASE_DIR", release_dir),
                mock.patch.object(self.module, "ARTIFACT_STATUS", artifact_status),
                mock.patch.object(self.module, "DEBUG_APK", tmp_path / "missing-debug.apk"),
                mock.patch.object(self.module, "RELEASE_AAB", tmp_path / "missing-release.aab"),
                mock.patch.object(self.module, "PACKET_AAB", tmp_path / "missing-packet.aab"),
                mock.patch.object(self.module, "OUTPUT", output),
                mock.patch.object(
                    self.module,
                    "read_gradle_release_identity",
                    return_value={
                        "appId": "com.example.changed",
                        "versionCode": 42,
                        "versionName": "2.0.0",
                    },
                ),
                mock.patch.object(self.module, "upload_blockers", return_value=["signed_upload_aab_missing"]),
            ):
                status = self.module.main()

            manifest = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(status, 0)
        self.assertEqual(manifest["appId"], "com.example.changed")
        self.assertEqual(manifest["versionCode"], 42)
        self.assertEqual(manifest["versionName"], "2.0.0")


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseArtifactManifestSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: release artifact manifest self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
