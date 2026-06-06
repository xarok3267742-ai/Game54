#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_GRADLE = ROOT / "app" / "build.gradle.kts"


def _require(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if match is None:
        raise ValueError(f"{label} not found in app/build.gradle.kts")
    return match.group(1)


def parse_gradle_release_identity(app_gradle_text: str) -> dict[str, object]:
    version_code_raw = _require(r"versionCode = ([0-9]+)", app_gradle_text, "versionCode")
    return {
        "appId": _require(r'applicationId = "([^"]+)"', app_gradle_text, "applicationId"),
        "versionCode": int(version_code_raw),
        "versionName": _require(r'versionName = "([^"]+)"', app_gradle_text, "versionName"),
    }


def read_gradle_release_identity(app_gradle: Path = APP_GRADLE) -> dict[str, object]:
    return parse_gradle_release_identity(app_gradle.read_text(encoding="utf-8"))
