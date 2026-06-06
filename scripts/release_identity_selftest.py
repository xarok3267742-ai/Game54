#!/usr/bin/env python3
from __future__ import annotations

import unittest

from release_identity import parse_gradle_release_identity


VALID_APP_GRADLE = """
android {
    defaultConfig {
        applicationId = "ru.poryadok5.app"
        versionCode = 1
        versionName = "1.0.0-rc1"
    }
}
"""


class ReleaseIdentitySelfTest(unittest.TestCase):
    def test_valid_identity_parses(self) -> None:
        self.assertEqual(
            parse_gradle_release_identity(VALID_APP_GRADLE),
            {
                "appId": "ru.poryadok5.app",
                "versionCode": 1,
                "versionName": "1.0.0-rc1",
            },
        )

    def test_missing_application_id_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "applicationId not found"):
            parse_gradle_release_identity(VALID_APP_GRADLE.replace('applicationId = "ru.poryadok5.app"\n', ""))

    def test_missing_version_code_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "versionCode not found"):
            parse_gradle_release_identity(VALID_APP_GRADLE.replace("versionCode = 1\n", ""))

    def test_missing_version_name_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "versionName not found"):
            parse_gradle_release_identity(VALID_APP_GRADLE.replace('versionName = "1.0.0-rc1"\n', ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
