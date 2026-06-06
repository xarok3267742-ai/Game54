#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from play_upload_blocker_handoff import (
    BLOCKER_DETAILS,
    BLOCKER_RECORD_KEYS,
    HANDOFF_GENERATED_FROM,
    HANDOFF_SCHEMA_VERSION,
    TOP_LEVEL_KEYS,
    blocker_record,
)
from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "play-submission" / "release" / "artifact_manifest.json"
HANDOFF = ROOT / "play-submission" / "release" / "upload_blockers.json"


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_json_object(path: Path, label: str, root: Path, failures: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        failures.append(f"{label} is missing: {display_path(path, root)}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{label} is invalid JSON: {exc}")
        return None
    if not isinstance(value, dict):
        failures.append(f"{label} must be a JSON object")
        return None
    return value


def exact_key_failures(label: str, record: dict[str, Any], expected: set[str]) -> list[str]:
    failures: list[str] = []
    actual = set(record)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        failures.append(f"{label} is missing keys: {', '.join(missing)}")
    if unexpected:
        failures.append(f"{label} contains unexpected keys: {', '.join(unexpected)}")
    return failures


def upload_blocker_handoff_failures(
    *,
    root: Path = ROOT,
    manifest_path: Path = MANIFEST,
    handoff_path: Path = HANDOFF,
) -> list[str]:
    failures: list[str] = []
    manifest = read_json_object(manifest_path, "release artifact manifest", root, failures)
    handoff = read_json_object(handoff_path, "upload blocker handoff", root, failures)
    if manifest is None or handoff is None:
        return failures

    failures.extend(exact_key_failures("upload blocker handoff", handoff, TOP_LEVEL_KEYS))
    if handoff.get("schemaVersion") != HANDOFF_SCHEMA_VERSION:
        failures.append(f"upload blocker handoff schemaVersion must be {HANDOFF_SCHEMA_VERSION}")
    if handoff.get("generatedFrom") != HANDOFF_GENERATED_FROM:
        failures.append(f"upload blocker handoff generatedFrom must be {HANDOFF_GENERATED_FROM}")

    try:
        expected_identity = read_gradle_release_identity()
    except (OSError, ValueError) as exc:
        failures.append(f"release identity could not be read from Gradle: {exc}")
        expected_identity = {}

    for key, expected_value in expected_identity.items():
        if manifest.get(key) != expected_value:
            failures.append(f"artifact manifest {key} is out of sync with Gradle release identity")
        if handoff.get(key) != expected_value:
            failures.append(f"upload blocker handoff {key} is out of sync with Gradle release identity")

    manifest_ready = manifest.get("playUploadReady")
    if handoff.get("playUploadReady") != manifest_ready:
        failures.append("upload blocker handoff playUploadReady is out of sync with artifact manifest")

    manifest_blockers = manifest.get("uploadBlockers")
    if not isinstance(manifest_blockers, list) or not all(isinstance(item, str) for item in manifest_blockers):
        failures.append("artifact manifest uploadBlockers must be a list of strings")
        manifest_blockers = []

    unknown_manifest_blockers = sorted(set(manifest_blockers) - set(BLOCKER_DETAILS))
    if unknown_manifest_blockers:
        failures.append(f"artifact manifest has unknown upload blockers: {', '.join(unknown_manifest_blockers)}")

    handoff_blockers = handoff.get("blockers")
    if not isinstance(handoff_blockers, list):
        failures.append("upload blocker handoff blockers must be a list")
        handoff_blockers = []

    ids: list[str] = []
    for index, raw_record in enumerate(handoff_blockers, start=1):
        label = f"upload blocker record {index}"
        if not isinstance(raw_record, dict):
            failures.append(f"{label} must be a JSON object")
            continue
        failures.extend(exact_key_failures(label, raw_record, BLOCKER_RECORD_KEYS))
        blocker_id = raw_record.get("id")
        if not isinstance(blocker_id, str):
            failures.append(f"{label} id must be a string")
            continue
        ids.append(blocker_id)
        if blocker_id not in BLOCKER_DETAILS:
            failures.append(f"{label} id is unknown: {blocker_id}")
            continue
        expected_record = blocker_record(blocker_id)
        for key, expected_value in expected_record.items():
            if raw_record.get(key) != expected_value:
                failures.append(f"{label} {key} is out of sync for {blocker_id}")

    duplicate_ids = sorted({blocker_id for blocker_id in ids if ids.count(blocker_id) > 1})
    if duplicate_ids:
        failures.append(f"upload blocker handoff contains duplicate blockers: {', '.join(duplicate_ids)}")

    if ids != manifest_blockers:
        failures.append("upload blocker handoff blocker order/content is out of sync with artifact manifest")

    if manifest_ready is True and manifest_blockers:
        failures.append("artifact manifest playUploadReady=true cannot have uploadBlockers")
    if handoff.get("playUploadReady") is True and ids:
        failures.append("upload blocker handoff playUploadReady=true cannot have open blockers")

    return failures


def main() -> int:
    failures = upload_blocker_handoff_failures()
    if failures:
        print("Play upload blocker handoff check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Play upload blocker handoff matches release artifact manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
