#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_play_submission_packet_contents.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_play_submission_packet_contents", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PlaySubmissionPacketContentsSelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def make_packet(
        self,
        root: Path,
        *,
        signed_status: bool,
        include_upload_aab: bool,
        extra_file: str | None = None,
        omit_file: str | None = None,
    ) -> Path:
        packet = root / "play-submission"
        for relative_path in self.module.BASE_ALLOWED_FILES:
            if relative_path == omit_file:
                continue
            path = packet / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("packet test file\n", encoding="utf-8")

        artifact_status = packet / "release" / "artifact_status.properties"
        if signed_status:
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

        if include_upload_aab:
            upload_aab = packet / "release" / "app-release.aab"
            upload_aab.parent.mkdir(parents=True, exist_ok=True)
            upload_aab.write_bytes(b"upload-aab")

        if extra_file is not None:
            extra_path = packet / extra_file
            extra_path.parent.mkdir(parents=True, exist_ok=True)
            extra_path.write_text("extra file\n", encoding="utf-8")

        return packet

    def call_main(self, packet: Path) -> tuple[int, str, str]:
        with (
            mock.patch.object(self.module, "PACKET", packet),
            mock.patch.object(self.module, "ARTIFACT_STATUS", packet / "release" / "artifact_status.properties"),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
            contextlib.redirect_stderr(io.StringIO()) as stderr,
        ):
            status = self.module.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_unsigned_packet_passes_without_upload_aab(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = self.make_packet(Path(tmp_dir), signed_status=False, include_upload_aab=False)
            status, stdout, stderr = self.call_main(packet)

        self.assertEqual(status, 0)
        self.assertIn("allowed files", stdout)
        self.assertEqual(stderr, "")

    def test_signed_packet_passes_with_upload_aab(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = self.make_packet(Path(tmp_dir), signed_status=True, include_upload_aab=True)
            status, stdout, stderr = self.call_main(packet)

        self.assertEqual(status, 0)
        self.assertIn("allowed files", stdout)
        self.assertEqual(stderr, "")

    def test_signed_packet_fails_without_upload_aab(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = self.make_packet(Path(tmp_dir), signed_status=True, include_upload_aab=False)
            status, stdout, stderr = self.call_main(packet)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("missing packet files: release/app-release.aab", stderr)

    def test_unsigned_packet_rejects_upload_aab(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = self.make_packet(Path(tmp_dir), signed_status=False, include_upload_aab=True)
            status, stdout, stderr = self.call_main(packet)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("unexpected packet files: release/app-release.aab", stderr)
        self.assertIn("release/app-release.aab is present even though artifact status is not signed/configured", stderr)

    def test_forbidden_key_like_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = self.make_packet(
                Path(tmp_dir),
                signed_status=False,
                include_upload_aab=False,
                extra_file="release/local-upload.jks",
            )
            status, stdout, stderr = self.call_main(packet)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("forbidden key/keystore-like file in packet", stderr)

    def test_missing_base_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = self.make_packet(
                Path(tmp_dir),
                signed_status=False,
                include_upload_aab=False,
                omit_file="docs/google_play_checklist.md",
            )
            status, stdout, stderr = self.call_main(packet)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("missing packet files: docs/google_play_checklist.md", stderr)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PlaySubmissionPacketContentsSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: Play submission packet contents self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
