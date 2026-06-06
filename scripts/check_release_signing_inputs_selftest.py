#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_release_signing_inputs.py"
INPUT_NAMES = (
    "PORYADOK5_KEYSTORE_PATH",
    "PORYADOK5_KEYSTORE_PASSWORD",
    "PORYADOK5_KEY_ALIAS",
    "PORYADOK5_KEY_PASSWORD",
    "PORYADOK5_KEYTOOL_PATH",
)


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_release_signing_inputs", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_release_signing_inputs"] = module
    spec.loader.exec_module(module)
    return module


class ReleaseSigningInputsSelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def call_main(
        self,
        argv: list[str],
        env: dict[str, str],
        properties_by_path: dict[Path, dict[str, str]] | None = None,
    ) -> tuple[int, str, str]:
        clean_env = {name: "" for name in INPUT_NAMES}
        clean_env["GRADLE_USER_HOME"] = ""
        clean_env.update(env)

        def fake_read_properties(path: Path) -> dict[str, str]:
            if properties_by_path is None:
                return {}
            return properties_by_path.get(path, {})

        with (
            mock.patch.dict(os.environ, clean_env, clear=False),
            mock.patch.object(sys, "argv", ["check_release_signing_inputs.py", *argv]),
            mock.patch.object(self.module, "read_properties", side_effect=fake_read_properties),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
            contextlib.redirect_stderr(io.StringIO()) as stderr,
        ):
            status = self.module.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def make_fake_keytool(self, directory: Path, body: str) -> Path:
        script = directory / "keytool"
        script.write_text("#!/usr/bin/env sh\n" + body + "\n", encoding="utf-8")
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return script

    def test_absent_inputs_pass_soft_mode(self) -> None:
        status, stdout, stderr = self.call_main([], {})
        self.assertEqual(status, 0)
        self.assertIn("local RC will remain unsigned", stdout)
        self.assertEqual(stderr, "")

    def test_absent_inputs_fail_strict_mode(self) -> None:
        status, _stdout, stderr = self.call_main(["--require"], {})
        self.assertEqual(status, 1)
        self.assertIn("release signing inputs are not configured", stderr)

    def test_partial_inputs_fail_without_printing_password(self) -> None:
        status, stdout, stderr = self.call_main(
            [],
            {
                "PORYADOK5_KEYSTORE_PATH": "/tmp/poryadok5-upload.jks",
                "PORYADOK5_KEYSTORE_PASSWORD": "secret-store-password",
            },
        )
        combined = stdout + stderr
        self.assertEqual(status, 1)
        self.assertIn("partial release signing configuration", combined)
        self.assertNotIn("secret-store-password", combined)

    def test_complete_inputs_accept_private_key_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            keystore = tmp_path / "upload.jks"
            keystore.write_text("test keystore bytes", encoding="utf-8")
            keytool = self.make_fake_keytool(tmp_path, 'printf "%s\\n" "Entry type: PrivateKeyEntry"')
            status, stdout, stderr = self.call_main(
                ["--require"],
                {
                    "PORYADOK5_KEYSTORE_PATH": str(keystore),
                    "PORYADOK5_KEYSTORE_PASSWORD": "store-pass",
                    "PORYADOK5_KEY_ALIAS": "poryadok5-upload",
                    "PORYADOK5_KEY_PASSWORD": "key-pass",
                    "PORYADOK5_KEYTOOL_PATH": str(keytool),
                },
            )
        self.assertEqual(status, 0)
        self.assertIn("PrivateKeyEntry", stdout)
        self.assertEqual(stderr, "")

    def test_complete_inputs_reject_non_private_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            keystore = tmp_path / "upload.jks"
            keystore.write_text("test keystore bytes", encoding="utf-8")
            keytool = self.make_fake_keytool(tmp_path, 'printf "%s\\n" "Entry type: trustedCertEntry"')
            status, stdout, stderr = self.call_main(
                ["--require"],
                {
                    "PORYADOK5_KEYSTORE_PATH": str(keystore),
                    "PORYADOK5_KEYSTORE_PASSWORD": "store-pass",
                    "PORYADOK5_KEY_ALIAS": "poryadok5-upload",
                    "PORYADOK5_KEY_PASSWORD": "key-pass",
                    "PORYADOK5_KEYTOOL_PATH": str(keytool),
                },
            )
        self.assertEqual(status, 1)
        self.assertIn("not a PrivateKeyEntry", stdout + stderr)

    def test_user_gradle_properties_take_precedence_over_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            keystore = tmp_path / "upload-from-user-properties.jks"
            keystore.write_text("test keystore bytes", encoding="utf-8")
            keytool = self.make_fake_keytool(tmp_path, 'printf "%s\\n" "Entry type: PrivateKeyEntry"')
            status, stdout, stderr = self.call_main(
                ["--require"],
                {
                    "PORYADOK5_KEYSTORE_PATH": "/does/not/matter/env-upload.jks",
                    "PORYADOK5_KEYSTORE_PASSWORD": "env-store-pass",
                    "PORYADOK5_KEY_ALIAS": "env-alias",
                    "PORYADOK5_KEY_PASSWORD": "env-key-pass",
                    "PORYADOK5_KEYTOOL_PATH": str(keytool),
                },
                {
                    self.module.USER_GRADLE_PROPERTIES: {
                        "PORYADOK5_KEYSTORE_PATH": str(keystore),
                        "PORYADOK5_KEYSTORE_PASSWORD": "user-store-pass",
                        "PORYADOK5_KEY_ALIAS": "user-alias",
                        "PORYADOK5_KEY_PASSWORD": "user-key-pass",
                    },
                },
            )
        self.assertEqual(status, 0)
        self.assertIn("user gradle.properties", stdout)
        self.assertEqual(stderr, "")

    def test_gradle_user_home_selects_matching_user_properties_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            gradle_home = tmp_path / "gradle-home"
            keystore = tmp_path / "upload-from-gradle-user-home.jks"
            keystore.write_text("test keystore bytes", encoding="utf-8")
            keytool = self.make_fake_keytool(tmp_path, 'printf "%s\\n" "Entry type: PrivateKeyEntry"')
            status, stdout, stderr = self.call_main(
                ["--require"],
                {
                    "GRADLE_USER_HOME": str(gradle_home),
                    "PORYADOK5_KEYSTORE_PATH": "/does/not/matter/env-upload.jks",
                    "PORYADOK5_KEYSTORE_PASSWORD": "env-store-pass",
                    "PORYADOK5_KEY_ALIAS": "env-alias",
                    "PORYADOK5_KEY_PASSWORD": "env-key-pass",
                    "PORYADOK5_KEYTOOL_PATH": str(keytool),
                },
                {
                    gradle_home / "gradle.properties": {
                        "PORYADOK5_KEYSTORE_PATH": str(keystore),
                        "PORYADOK5_KEYSTORE_PASSWORD": "user-home-store-pass",
                        "PORYADOK5_KEY_ALIAS": "user-home-alias",
                        "PORYADOK5_KEY_PASSWORD": "user-home-key-pass",
                    },
                },
            )
        self.assertEqual(status, 0)
        self.assertIn("user gradle.properties", stdout)
        self.assertEqual(stderr, "")

    def test_project_gradle_properties_are_rejected_even_when_environment_is_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            keystore = tmp_path / "upload.jks"
            keystore.write_text("test keystore bytes", encoding="utf-8")
            keytool = self.make_fake_keytool(tmp_path, 'printf "%s\\n" "Entry type: PrivateKeyEntry"')
            status, stdout, stderr = self.call_main(
                ["--require"],
                {
                    "PORYADOK5_KEYSTORE_PATH": str(keystore),
                    "PORYADOK5_KEYSTORE_PASSWORD": "env-store-pass",
                    "PORYADOK5_KEY_ALIAS": "env-alias",
                    "PORYADOK5_KEY_PASSWORD": "env-key-pass",
                    "PORYADOK5_KEYTOOL_PATH": str(keytool),
                },
                {
                    self.module.PROJECT_GRADLE_PROPERTIES: {
                        "PORYADOK5_KEYSTORE_PASSWORD": "project-secret",
                    },
                },
            )
        self.assertEqual(status, 1)
        combined = stdout + stderr
        self.assertIn("must not be stored in project gradle.properties", combined)
        self.assertNotIn("project-secret", combined)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseSigningInputsSelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: release signing input self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
