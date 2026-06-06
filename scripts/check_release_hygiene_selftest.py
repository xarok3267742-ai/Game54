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
MODULE_PATH = ROOT / "scripts" / "check_release_hygiene.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_release_hygiene", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseHygieneSelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def create_workspace(self, root: Path) -> None:
        gitignore = "\n".join(self.module.REQUIRED_GITIGNORE_PATTERNS) + "\n"
        (root / ".gitignore").write_text(gitignore, encoding="utf-8")
        (root / "docs").mkdir()
        (root / "docs" / "notes.md").write_text("release hygiene test file\n", encoding="utf-8")

    def call_main(self, root: Path) -> tuple[int, str, str]:
        with (
            mock.patch.object(self.module, "ROOT", root),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
            contextlib.redirect_stderr(io.StringIO()) as stderr,
        ):
            status = self.module.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_clean_workspace_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_workspace(root)
            status, stdout, stderr = self.call_main(root)

        self.assertEqual(status, 0)
        self.assertIn("release hygiene check found no keystores", stdout)
        self.assertEqual(stderr, "")

    def test_key_like_files_are_rejected_outside_build_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_workspace(root)
            (root / "upload.jks").write_bytes(b"not a real key")
            status, stdout, stderr = self.call_main(root)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("forbidden key/keystore-like file exists: upload.jks", stderr)

    def test_key_like_files_are_ignored_inside_build_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_workspace(root)
            build_dir = root / "app" / "build" / "outputs"
            build_dir.mkdir(parents=True)
            (build_dir / "generated.jks").write_bytes(b"generated test bytes")
            status, stdout, stderr = self.call_main(root)

        self.assertEqual(status, 0)
        self.assertIn("release hygiene check found no keystores", stdout)
        self.assertEqual(stderr, "")

    def test_build_tree_is_pruned_before_file_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_workspace(root)
            build_dir = root / "app" / "build" / "outputs"
            build_dir.mkdir(parents=True)
            (build_dir / "generated.jks").write_bytes(b"generated test bytes")
            copied_build_dir = root / "app" / "build 100" / "outputs"
            copied_build_dir.mkdir(parents=True)
            (copied_build_dir / "generated.jks").write_bytes(b"generated test bytes")
            copied_packet_dir = root / "play-submission 250" / "release"
            copied_packet_dir.mkdir(parents=True)
            (copied_packet_dir / "generated.jks").write_bytes(b"generated test bytes")
            (root / "docs" / "release.md").write_text("visible doc\n", encoding="utf-8")
            with mock.patch.object(self.module, "ROOT", root):
                files = {str(path.relative_to(root)) for path in self.module.iter_repo_files()}

        self.assertIn("docs/release.md", files)
        self.assertNotIn("app/build/outputs/generated.jks", files)
        self.assertNotIn("app/build 100/outputs/generated.jks", files)
        self.assertNotIn("play-submission 250/release/generated.jks", files)

    def test_project_gradle_signing_values_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_workspace(root)
            key_name = "PORYADOK5_" + "KEY_ALIAS"
            (root / "gradle.properties").write_text(f"{key_name}=upload\n", encoding="utf-8")
            status, stdout, stderr = self.call_main(root)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("PORYADOK5 signing values must not be stored in gradle.properties", stderr)

    def test_real_looking_password_assignment_is_rejected_without_echoing_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_workspace(root)
            env_name = "PORYADOK5_" + "KEYSTORE_PASSWORD"
            secret_value = "RealSigningPassword123"
            (root / "docs" / "bad.md").write_text(
                f"export {env_name}={secret_value}\n",
                encoding="utf-8",
            )
            status, stdout, stderr = self.call_main(root)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("real-looking PORYADOK5_KEYSTORE_PASSWORD assignment", stderr)
        self.assertNotIn(secret_value, stderr)

    def test_safe_example_password_assignments_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_workspace(root)
            env_name = "PORYADOK5_" + "KEY_PASSWORD"
            (root / "docs" / "example.md").write_text(
                f"export {env_name}=change-me\n",
                encoding="utf-8",
            )
            status, stdout, stderr = self.call_main(root)

        self.assertEqual(status, 0)
        self.assertIn("release hygiene check found no keystores", stdout)
        self.assertEqual(stderr, "")

    def test_private_key_blocks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_workspace(root)
            private_key_text = "-----BEGIN " + "PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----\n"
            (root / "docs" / "private.txt").write_text(private_key_text, encoding="utf-8")
            status, stdout, stderr = self.call_main(root)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("private key block found in text file: docs/private.txt", stderr)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseHygieneSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: release hygiene self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
