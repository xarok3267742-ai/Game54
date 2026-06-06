#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from check_doc_inventory import REQUIRED_FILES
from check_play_submission_packet_contents import BASE_ALLOWED_FILES, OPTIONAL_ALLOWED_FILES
from check_play_submission_packet_sync import SOURCE_TO_PACKET

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "play-submission"

SPECIAL_PACKET_DESTINATIONS = {
    "README.md": "project/README.md",
    "AGENTS.md": "project/AGENTS.md",
    "docs/store_listing_ru.md": "text/store_listing_ru.md",
    "docs/privacy_policy_draft_ru.md": "text/privacy_policy_draft_ru.md",
    "docs/privacy_policy_ru.html": "text/privacy_policy_ru.html",
}


def packet_destination_for_source(relative_path: str) -> str | None:
    if relative_path in SPECIAL_PACKET_DESTINATIONS:
        return SPECIAL_PACKET_DESTINATIONS[relative_path]
    if relative_path.startswith("docs/"):
        return relative_path
    return None


def expected_doc_packet_mapping(required_files: dict[str, tuple[str, ...]]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for source_relative in required_files:
        packet_relative = packet_destination_for_source(source_relative)
        if packet_relative is not None:
            expected[source_relative] = packet_relative
    return expected


def play_submission_doc_coverage_failures(
    *,
    root: Path = ROOT,
    packet: Path = PACKET,
    required_files: dict[str, tuple[str, ...]] | None = None,
    mappings: tuple[tuple[str, str], ...] = SOURCE_TO_PACKET,
    allowed_files: set[str] | None = None,
    optional_allowed_files: set[str] | None = None,
) -> list[str]:
    required = required_files or REQUIRED_FILES
    allowed = allowed_files or BASE_ALLOWED_FILES
    optional = optional_allowed_files or OPTIONAL_ALLOWED_FILES
    all_allowed = set(allowed) | set(optional)
    mapping_pairs = set(mappings)
    mapping_by_source: dict[str, set[str]] = {}
    failures: list[str] = []

    for source_relative, packet_relative in mappings:
        mapping_by_source.setdefault(source_relative, set()).add(packet_relative)

    expected = expected_doc_packet_mapping(required)
    unsupported = sorted(set(required) - set(expected))
    for source_relative in unsupported:
        failures.append(f"required document has no packet destination rule: {source_relative}")

    for source_relative, expected_packet_relative in sorted(expected.items()):
        expected_pair = (source_relative, expected_packet_relative)
        if expected_pair not in mapping_pairs:
            actual_destinations = sorted(mapping_by_source.get(source_relative, set()))
            if actual_destinations:
                failures.append(
                    f"required document has wrong packet sync destination: "
                    f"{source_relative} -> {', '.join(actual_destinations)} "
                    f"(expected {expected_packet_relative})"
                )
            else:
                failures.append(
                    f"required document is missing from packet sync mapping: "
                    f"{source_relative} -> {expected_packet_relative}"
                )

        if expected_packet_relative not in all_allowed:
            failures.append(f"required document packet path is not allowlisted: {expected_packet_relative}")

        source_path = root / source_relative
        packet_path = packet / expected_packet_relative
        if not source_path.exists():
            failures.append(f"required document source file is missing: {source_relative}")
            continue
        if not packet_path.exists():
            failures.append(f"required document packet copy is missing: {expected_packet_relative}")
            continue
        if source_path.read_bytes() != packet_path.read_bytes():
            failures.append(
                f"required document packet copy is stale: {expected_packet_relative} differs from {source_relative}"
            )

    return failures


def main() -> int:
    failures = play_submission_doc_coverage_failures()
    if failures:
        print("Play submission documentation coverage check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        f"PASS: Play submission packet covers {len(REQUIRED_FILES)} required RC documents from documentation inventory"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
