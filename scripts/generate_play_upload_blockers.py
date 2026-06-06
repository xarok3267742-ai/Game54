#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from play_upload_blocker_handoff import payload_from_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "play-submission" / "release" / "artifact_manifest.json"
OUTPUT = ROOT / "play-submission" / "release" / "upload_blockers.json"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    if not MANIFEST.exists():
        print(f"FAIL: release artifact manifest is missing: {display_path(MANIFEST)}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: release artifact manifest is invalid JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(manifest, dict):
        print("FAIL: release artifact manifest must be a JSON object", file=sys.stderr)
        return 1

    try:
        payload = payload_from_manifest(manifest)
    except ValueError as exc:
        print(f"FAIL: upload blocker handoff could not be generated: {exc}", file=sys.stderr)
        return 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Built {display_path(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
