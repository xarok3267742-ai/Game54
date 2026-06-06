#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CATALOG = ROOT / "app/src/main/res/raw/tasks_ru.json"
EXPECTED_TASK_COUNT = 80


@dataclass(frozen=True)
class CatalogArtifact:
    label: str
    path: Path
    entry: str


ARTIFACTS = (
    CatalogArtifact(
        label="debug APK",
        path=ROOT / "app/build/outputs/apk/debug/app-debug.apk",
        entry="res/raw/tasks_ru.json",
    ),
    CatalogArtifact(
        label="release AAB",
        path=ROOT / "app/build/outputs/bundle/release/app-release.aab",
        entry="base/res/raw/tasks_ru.json",
    ),
)


def parse_catalog(data: bytes, label: str, failures: list[str]) -> list[Any]:
    try:
        catalog = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        failures.append(f"{label} catalog is not valid UTF-8 JSON: {exc}")
        return []
    if not isinstance(catalog, list):
        failures.append(f"{label} catalog root must be a JSON array")
        return []
    if len(catalog) != EXPECTED_TASK_COUNT:
        failures.append(f"{label} catalog has {len(catalog)} tasks; expected {EXPECTED_TASK_COUNT}")
    return catalog


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_zip_entry(artifact: CatalogArtifact, failures: list[str]) -> bytes | None:
    if not artifact.path.exists():
        failures.append(f"{artifact.label} is missing: {display_path(artifact.path)}")
        return None

    try:
        with zipfile.ZipFile(artifact.path) as archive:
            names = archive.namelist()
            if artifact.entry not in names:
                failures.append(f"{artifact.label} missing packaged task catalog: {artifact.entry}")
                return None

            catalog_like_entries = [
                name for name in names if name.endswith(".json") and "tasks" in Path(name).name
            ]
            if catalog_like_entries != [artifact.entry]:
                failures.append(
                    f"{artifact.label} has unexpected task-like JSON entries: "
                    + ", ".join(catalog_like_entries)
                )

            return archive.read(artifact.entry)
    except zipfile.BadZipFile:
        failures.append(f"{artifact.label} is not a readable ZIP artifact: {display_path(artifact.path)}")
        return None


def main() -> int:
    failures: list[str] = []

    if not SOURCE_CATALOG.exists():
        print(f"FAIL: source task catalog is missing: {SOURCE_CATALOG.relative_to(ROOT)}", file=sys.stderr)
        return 1

    source_bytes = SOURCE_CATALOG.read_bytes()
    source_catalog = parse_catalog(source_bytes, "source", failures)
    source_digest = hashlib.sha256(source_bytes).hexdigest()

    for artifact in ARTIFACTS:
        packaged_bytes = read_zip_entry(artifact, failures)
        if packaged_bytes is None:
            continue

        packaged_catalog = parse_catalog(packaged_bytes, artifact.label, failures)
        packaged_digest = hashlib.sha256(packaged_bytes).hexdigest()

        if packaged_bytes != source_bytes:
            failures.append(
                f"{artifact.label} packaged catalog bytes differ from source "
                f"(source {source_digest}, packaged {packaged_digest})"
            )
        if packaged_catalog != source_catalog:
            failures.append(f"{artifact.label} packaged catalog JSON differs from source")

    if failures:
        print("Packaged task catalog check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: packaged task catalog matches source in debug APK and release AAB "
        f"({EXPECTED_TASK_COUNT} tasks, sha256 {source_digest})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
