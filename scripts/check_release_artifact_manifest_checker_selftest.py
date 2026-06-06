#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Optional
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_release_artifact_manifest.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_release_artifact_manifest", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReleaseArtifactManifestCheckerSelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def make_workspace(
        self,
        root: Path,
        *,
        release_bytes: bytes = b"release-aab",
        packet_bytes: Optional[bytes] = None,
        signature_status: str = "signed_verified",
        signed_status: str = "true",
        upload_blockers: list[str] | None = None,
        path_overrides: dict[str, str] | None = None,
        manifest_extra_fields: dict[str, object] | None = None,
        artifact_extra_fields: dict[str, dict[str, object]] | None = None,
    ) -> dict[str, Path]:
        debug_apk = root / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
        release_aab = root / "app" / "build" / "outputs" / "bundle" / "release" / "app-release.aab"
        packet_dir = root / "play-submission" / "release"
        packet_aab = packet_dir / "app-release.aab"
        artifact_status = packet_dir / "artifact_status.properties"
        manifest = packet_dir / "artifact_manifest.json"

        debug_apk.parent.mkdir(parents=True)
        release_aab.parent.mkdir(parents=True)
        packet_dir.mkdir(parents=True)

        debug_apk.write_bytes(b"debug-apk")
        release_aab.write_bytes(release_bytes)
        if packet_bytes is not None:
            packet_aab.write_bytes(packet_bytes)

        if signed_status == "true":
            artifact_status.write_text(
                "signed_or_configured=true\n"
                "artifact=release/app-release.aab\n"
                "reason=release AAB signature verified by jarsigner\n",
                encoding="utf-8",
            )
        else:
            artifact_status.write_text(
                "signed_or_configured=false\n"
                "artifact=not_included_unsigned_local_rc\n"
                "reason=release AAB is unsigned\n",
                encoding="utf-8",
            )

        packet_exists = packet_aab.exists()
        blockers = upload_blockers
        if blockers is None:
            blockers = (
                ["release_signing_inputs_missing"]
                if signature_status == "signed_verified" and packet_exists
                else ["release_signing_inputs_missing", "signed_upload_aab_missing"]
            )

        manifest_data = {
            "schemaVersion": 1,
            "appId": "ru.poryadok5.app",
            "versionCode": 1,
            "versionName": "1.0.0-rc1",
            "localRcReady": True,
            "playUploadReady": not blockers,
            "packetArtifactStatus": self.module.read_properties(artifact_status),
            "uploadBlockers": blockers,
            "artifacts": {
                "debugApk": {
                    "exists": True,
                    "path": "app/build/outputs/apk/debug/app-debug.apk",
                    "bytes": debug_apk.stat().st_size,
                    "sha256": sha256(debug_apk),
                },
                "releaseAab": {
                    "exists": True,
                    "path": "app/build/outputs/bundle/release/app-release.aab",
                    "bytes": release_aab.stat().st_size,
                    "sha256": sha256(release_aab),
                    "signatureStatus": signature_status,
                },
                "packetReleaseAab": (
                    {
                        "exists": True,
                        "path": "play-submission/release/app-release.aab",
                        "bytes": packet_aab.stat().st_size,
                        "sha256": sha256(packet_aab),
                    }
                    if packet_exists
                    else {
                        "exists": False,
                        "path": "play-submission/release/app-release.aab",
                    }
                ),
            },
        }
        for artifact_key, overridden_path in (path_overrides or {}).items():
            artifact_record = manifest_data["artifacts"][artifact_key]
            artifact_record["path"] = overridden_path
        for artifact_key, extra_fields in (artifact_extra_fields or {}).items():
            artifact_record = manifest_data["artifacts"][artifact_key]
            artifact_record.update(extra_fields)
        manifest_data.update(manifest_extra_fields or {})

        manifest.write_text(json.dumps(manifest_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        return {
            "root": root,
            "manifest": manifest,
            "debug_apk": debug_apk,
            "release_aab": release_aab,
            "packet_aab": packet_aab,
            "artifact_status": artifact_status,
        }

    def call_main(
        self,
        paths: dict[str, Path],
        *,
        signing_inputs_ready: bool = False,
        play_forms_ready: bool = True,
        policy_content_ready: bool = True,
    ) -> tuple[int, str, str]:
        def fake_checker_passes(path: Path) -> bool:
            if path == self.module.PLAY_FORMS_CHECKER:
                return play_forms_ready
            if path == self.module.POLICY_CONTENT_CHECKER:
                return policy_content_ready
            return False

        with (
            mock.patch.object(self.module, "ROOT", paths["root"]),
            mock.patch.object(self.module, "MANIFEST", paths["manifest"]),
            mock.patch.object(self.module, "DEBUG_APK", paths["debug_apk"]),
            mock.patch.object(self.module, "RELEASE_AAB", paths["release_aab"]),
            mock.patch.object(self.module, "PACKET_AAB", paths["packet_aab"]),
            mock.patch.object(self.module, "ARTIFACT_STATUS", paths["artifact_status"]),
            mock.patch.object(
                self.module,
                "read_gradle_release_identity",
                return_value={
                    "appId": "ru.poryadok5.app",
                    "versionCode": 1,
                    "versionName": "1.0.0-rc1",
                },
            ),
            mock.patch.object(self.module, "release_signing_inputs_ready", return_value=signing_inputs_ready),
            mock.patch.object(self.module, "checker_passes", side_effect=fake_checker_passes),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
            contextlib.redirect_stderr(io.StringIO()) as stderr,
        ):
            status = self.module.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_signed_packet_identity_match_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(Path(tmp_dir), packet_bytes=b"release-aab", upload_blockers=[])
            status, stdout, stderr = self.call_main(paths, signing_inputs_ready=True)

        self.assertEqual(status, 0)
        self.assertIn("release artifact manifest matches current build and packet state", stdout)
        self.assertEqual(stderr, "")

    def test_gradle_identity_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(Path(tmp_dir), packet_bytes=b"release-aab", upload_blockers=[])
            with (
                mock.patch.object(self.module, "ROOT", paths["root"]),
                mock.patch.object(self.module, "MANIFEST", paths["manifest"]),
                mock.patch.object(self.module, "DEBUG_APK", paths["debug_apk"]),
                mock.patch.object(self.module, "RELEASE_AAB", paths["release_aab"]),
                mock.patch.object(self.module, "PACKET_AAB", paths["packet_aab"]),
                mock.patch.object(self.module, "ARTIFACT_STATUS", paths["artifact_status"]),
                mock.patch.object(
                    self.module,
                    "read_gradle_release_identity",
                    return_value={
                        "appId": "ru.poryadok5.app",
                        "versionCode": 2,
                        "versionName": "1.0.0-rc1",
                    },
                ),
                mock.patch.object(self.module, "release_signing_inputs_ready", return_value=True),
                mock.patch.object(self.module, "checker_passes", return_value=True),
                contextlib.redirect_stdout(io.StringIO()) as stdout,
                contextlib.redirect_stderr(io.StringIO()) as stderr,
            ):
                status = self.module.main()

        self.assertEqual(status, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("versionCode is out of sync with app/build.gradle.kts", stderr.getvalue())

    def test_artifact_record_path_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=b"release-aab",
                upload_blockers=[],
                path_overrides={"releaseAab": "app/build/outputs/bundle/release/wrong.aab"},
            )
            status, stdout, stderr = self.call_main(paths, signing_inputs_ready=True)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("releaseAab path is out of sync", stderr)

    def test_unexpected_top_level_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=b"release-aab",
                upload_blockers=[],
                manifest_extra_fields={"manualNote": "do not ship"},
            )
            status, stdout, stderr = self.call_main(paths, signing_inputs_ready=True)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("release artifact manifest contains unexpected keys: manualNote", stderr)

    def test_unexpected_artifact_record_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=b"release-aab",
                upload_blockers=[],
                artifact_extra_fields={"debugApk": {"copiedFrom": "manual"}},
            )
            status, stdout, stderr = self.call_main(paths, signing_inputs_ready=True)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("debugApk artifact record contains unexpected keys: copiedFrom", stderr)

    def test_unknown_upload_blocker_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=b"release-aab",
                upload_blockers=["manual_blocker"],
            )
            status, stdout, stderr = self.call_main(paths, signing_inputs_ready=True)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("uploadBlockers contains unknown blockers: manual_blocker", stderr)

    def test_duplicate_upload_blocker_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=b"release-aab",
                upload_blockers=["support_email_missing", "support_email_missing"],
            )
            status, stdout, stderr = self.call_main(paths, signing_inputs_ready=True)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("uploadBlockers contains duplicates: support_email_missing", stderr)

    def test_signed_packet_sha_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(Path(tmp_dir), packet_bytes=b"different-aab")
            status, stdout, stderr = self.call_main(paths)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("packet release AAB sha256 must match current release AAB sha256", stderr)

    def test_signed_status_without_packet_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(Path(tmp_dir), packet_bytes=None)
            status, stdout, stderr = self.call_main(paths)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("signed release AAB must be included", stderr)

    def test_unsigned_artifact_status_true_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=None,
                signature_status="unsigned",
                signed_status="true",
                upload_blockers=["signed_upload_aab_missing"],
            )
            status, stdout, stderr = self.call_main(paths)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("packet artifact status must not mark unsigned or unverified AAB", stderr)

    def test_missing_signing_input_blocker_fails_when_inputs_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=None,
                signature_status="unsigned",
                signed_status="false",
                upload_blockers=["signed_upload_aab_missing"],
            )
            status, stdout, stderr = self.call_main(paths)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("release_signing_inputs_missing blocker must be present", stderr)

    def test_stale_signing_input_blocker_fails_when_inputs_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=b"release-aab",
                upload_blockers=["release_signing_inputs_missing"],
            )
            status, stdout, stderr = self.call_main(paths, signing_inputs_ready=True)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("release_signing_inputs_missing blocker must be absent", stderr)

    def test_missing_play_forms_evidence_blocker_fails_when_checker_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(Path(tmp_dir), packet_bytes=b"release-aab", upload_blockers=[])
            status, stdout, stderr = self.call_main(
                paths,
                signing_inputs_ready=True,
                play_forms_ready=False,
                policy_content_ready=True,
            )

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("play_console_forms_evidence_failed blocker must be present", stderr)

    def test_stale_policy_content_evidence_blocker_fails_when_checker_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            paths = self.make_workspace(
                Path(tmp_dir),
                packet_bytes=b"release-aab",
                upload_blockers=["policy_content_risk_evidence_failed"],
            )
            status, stdout, stderr = self.call_main(
                paths,
                signing_inputs_ready=True,
                play_forms_ready=True,
                policy_content_ready=True,
            )

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("policy_content_risk_evidence_failed blocker must be absent", stderr)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseArtifactManifestCheckerSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: release artifact manifest checker self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
