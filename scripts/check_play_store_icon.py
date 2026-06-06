#!/usr/bin/env python3
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / "store-assets" / "app-icon" / "play-store-icon-512.png"
MAX_BYTES = 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def play_store_icon_failures(data: bytes, max_bytes: int = MAX_BYTES) -> list[str]:
    failures: list[str] = []

    if len(data) > max_bytes:
        failures.append(f"file is {len(data)} bytes; limit is {max_bytes}")
    if not data.startswith(PNG_SIGNATURE):
        failures.append("file is not a PNG")
    elif len(data) < 33:
        failures.append("PNG header is too short to read image metadata")
    else:
        width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
        if width != 512 or height != 512:
            failures.append(f"dimensions are {width}x{height}; expected 512x512")
        if bit_depth != 8 or color_type != 6:
            failures.append(f"PNG must be 32-bit RGBA; got bit depth {bit_depth}, color type {color_type}")

    return failures


def main() -> int:
    if not ICON.exists():
        print(f"FAIL: Play Store icon is missing: {ICON}", file=sys.stderr)
        return 1

    data = ICON.read_bytes()
    failures = play_store_icon_failures(data)

    if failures:
        print("Play Store icon check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(f"PASS: Play Store icon is 512x512 32-bit PNG and {len(data)} bytes ({ICON})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
