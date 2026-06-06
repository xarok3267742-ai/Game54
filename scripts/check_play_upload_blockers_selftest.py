#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check_play_upload_blockers.py"
GENERATOR_PATH = ROOT / "scripts" / "generate_play_upload_blockers.py"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PlayUploadBlockersSelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = load_module("check_play_upload_blockers", CHECKER_PATH)
        cls.generator = load_module("generate_play_upload_blockers", GENERATOR_PATH)

    def write_manifest(self, path: Path, *, blockers: list[str], ready: bool = False) -> None:
        path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "appId": "ru.poryadok5.app",
                    "versionCode": 1,
                    "versionName": "1.0.0-rc1",
                    "playUploadReady": ready,
                    "uploadBlockers": blockers,
                },
            ),
            encoding="utf-8",
        )

    def failures_for(self, manifest: Path, handoff: Path) -> list[str]:
        with mock.patch.object(
            self.checker,
            "read_gradle_release_identity",
            return_value={
                "appId": "ru.poryadok5.app",
                "versionCode": 1,
                "versionName": "1.0.0-rc1",
            },
        ):
            return self.checker.upload_blocker_handoff_failures(
                root=manifest.parents[2],
                manifest_path=manifest,
                handoff_path=handoff,
            )

    def generate_for(self, manifest: Path, handoff: Path) -> int:
        with (
            mock.patch.object(self.generator, "MANIFEST", manifest),
            mock.patch.object(self.generator, "OUTPUT", handoff),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return self.generator.main()

    def test_generated_handoff_passes_checker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = Path(tmp_dir) / "play-submission" / "release"
            packet.mkdir(parents=True)
            manifest = packet / "artifact_manifest.json"
            handoff = packet / "upload_blockers.json"
            self.write_manifest(
                manifest,
                blockers=["release_signing_inputs_missing", "support_email_missing"],
            )

            self.assertEqual(self.generate_for(manifest, handoff), 0)
            self.assertEqual(self.failures_for(manifest, handoff), [])

    def test_missing_blocker_record_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = Path(tmp_dir) / "play-submission" / "release"
            packet.mkdir(parents=True)
            manifest = packet / "artifact_manifest.json"
            handoff = packet / "upload_blockers.json"
            self.write_manifest(
                manifest,
                blockers=["release_signing_inputs_missing", "support_email_missing"],
            )
            self.assertEqual(self.generate_for(manifest, handoff), 0)
            payload = json.loads(handoff.read_text(encoding="utf-8"))
            payload["blockers"] = payload["blockers"][:1]
            handoff.write_text(json.dumps(payload), encoding="utf-8")

            failures = self.failures_for(manifest, handoff)

        self.assertIn("upload blocker handoff blocker order/content is out of sync with artifact manifest", failures)

    def test_record_content_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = Path(tmp_dir) / "play-submission" / "release"
            packet.mkdir(parents=True)
            manifest = packet / "artifact_manifest.json"
            handoff = packet / "upload_blockers.json"
            self.write_manifest(manifest, blockers=["support_email_missing"])
            self.assertEqual(self.generate_for(manifest, handoff), 0)
            payload = json.loads(handoff.read_text(encoding="utf-8"))
            payload["blockers"][0]["requiredAction"] = "Outdated action"
            handoff.write_text(json.dumps(payload), encoding="utf-8")

            failures = self.failures_for(manifest, handoff)

        self.assertIn("upload blocker record 1 requiredAction is out of sync for support_email_missing", failures)

    def test_ready_state_rejects_open_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = Path(tmp_dir) / "play-submission" / "release"
            packet.mkdir(parents=True)
            manifest = packet / "artifact_manifest.json"
            handoff = packet / "upload_blockers.json"
            self.write_manifest(manifest, blockers=["support_email_missing"], ready=True)
            self.assertEqual(self.generate_for(manifest, handoff), 0)

            failures = self.failures_for(manifest, handoff)

        self.assertIn("artifact manifest playUploadReady=true cannot have uploadBlockers", failures)
        self.assertIn("upload blocker handoff playUploadReady=true cannot have open blockers", failures)

    def test_unknown_blocker_fails_generation_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            packet = Path(tmp_dir) / "play-submission" / "release"
            packet.mkdir(parents=True)
            manifest = packet / "artifact_manifest.json"
            handoff = packet / "upload_blockers.json"
            self.write_manifest(manifest, blockers=["unknown_blocker"])

            self.assertEqual(self.generate_for(manifest, handoff), 1)
            handoff.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "appId": "ru.poryadok5.app",
                        "versionCode": 1,
                        "versionName": "1.0.0-rc1",
                        "playUploadReady": False,
                        "generatedFrom": "play-submission/release/artifact_manifest.json",
                        "blockers": [
                            {
                                "id": "unknown_blocker",
                                "status": "open",
                                "category": "unknown",
                                "scope": "unknown",
                                "requiredAction": "unknown",
                                "evidence": "unknown",
                                "verification": "unknown",
                            },
                        ],
                    },
                ),
                encoding="utf-8",
            )

            failures = self.failures_for(manifest, handoff)

        self.assertIn("artifact manifest has unknown upload blockers: unknown_blocker", failures)
        self.assertIn("upload blocker record 1 id is unknown: unknown_blocker", failures)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PlayUploadBlockersSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: Play upload blocker handoff self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
