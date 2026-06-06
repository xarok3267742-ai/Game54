#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from check_play_submission_packet_sync import packet_sync_failures


class PlaySubmissionPacketSyncSelfTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="poryadok5-packet-sync.")
        self.root = Path(self.tmp.name)
        self.packet = self.root / "play-submission"
        self.mappings = (
            ("docs/source.md", "docs/source.md"),
            ("screenshots/play-store/01.png", "assets/screenshots/01.png"),
        )
        self.write_file(self.root / "docs/source.md", b"source document\n")
        self.write_file(self.root / "screenshots/play-store/01.png", b"\x89PNG\r\n\x1a\nimage\n")
        self.write_file(self.packet / "docs/source.md", b"source document\n")
        self.write_file(self.packet / "assets/screenshots/01.png", b"\x89PNG\r\n\x1a\nimage\n")
        self.write_checksums()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    @staticmethod
    def write_file(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def write_checksums(self, omit: set[str] | None = None, extra: dict[str, bytes] | None = None) -> None:
        omit = omit or set()
        extra = extra or {}
        lines: list[str] = []
        for path in sorted(self.packet.rglob("*")):
            if not path.is_file() or path.name == "checksums.sha256":
                continue
            relative = str(path.relative_to(self.packet))
            if relative in omit:
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  ./{relative}\n")
        for relative, data in sorted(extra.items()):
            digest = hashlib.sha256(data).hexdigest()
            lines.append(f"{digest}  ./{relative}\n")
        (self.packet / "checksums.sha256").write_text("".join(lines), encoding="utf-8")

    def failures(self) -> list[str]:
        return packet_sync_failures(self.root, self.packet, self.mappings)

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_missing_source_fails(self) -> None:
        (self.root / "docs/source.md").unlink()
        self.assertTrue(any("missing source file: docs/source.md" in failure for failure in self.failures()))

    def test_missing_packet_file_fails(self) -> None:
        (self.packet / "docs/source.md").unlink()
        failures = self.failures()
        self.assertTrue(any("missing packet file: docs/source.md" in failure for failure in failures))

    def test_stale_packet_file_fails_even_when_checksums_match_packet(self) -> None:
        (self.packet / "docs/source.md").write_bytes(b"stale packet document\n")
        self.write_checksums()
        self.assertTrue(any("packet file is stale: docs/source.md" in failure for failure in self.failures()))

    def test_missing_checksum_file_fails(self) -> None:
        (self.packet / "checksums.sha256").unlink()
        self.assertTrue(any("missing packet checksum file" in failure for failure in self.failures()))

    def test_checksum_mismatch_fails(self) -> None:
        (self.packet / "docs/source.md").write_bytes(b"changed after checksum\n")
        self.assertTrue(any("checksum mismatch for packet file: docs/source.md" in failure for failure in self.failures()))

    def test_missing_checksum_entry_fails(self) -> None:
        self.write_checksums(omit={"docs/source.md"})
        self.assertTrue(
            any("packet file missing checksum entry: docs/source.md" in failure for failure in self.failures())
        )

    def test_stale_checksum_entry_fails(self) -> None:
        self.write_checksums(extra={"stale.txt": b"old file\n"})
        self.assertTrue(
            any("checksum entry points to missing packet file: stale.txt" in failure for failure in self.failures())
        )

    def test_malformed_checksum_line_fails(self) -> None:
        (self.packet / "checksums.sha256").write_text("bad checksum line\n", encoding="utf-8")
        self.assertTrue(any("malformed checksum line" in failure for failure in self.failures()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
