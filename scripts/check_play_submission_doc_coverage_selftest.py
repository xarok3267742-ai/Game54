#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_play_submission_doc_coverage import (
    expected_doc_packet_mapping,
    play_submission_doc_coverage_failures,
)


class PlaySubmissionDocCoverageSelfTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="poryadok5-doc-coverage.")
        self.root = Path(self.tmp.name)
        self.packet = self.root / "play-submission"
        self.required = {
            "README.md": ("Порядок 5",),
            "AGENTS.md": ("Definition of Done",),
            "docs/product_spec.md": ("Core Loop",),
            "docs/store_listing_ru.md": ("Store Listing Draft",),
            "docs/privacy_policy_draft_ru.md": ("Политика конфиденциальности",),
            "docs/privacy_policy_ru.html": ("Политика конфиденциальности",),
        }
        self.expected = expected_doc_packet_mapping(self.required)
        self.mappings = tuple(sorted(self.expected.items()))
        self.allowed = set(self.expected.values())
        for source_relative, packet_relative in self.expected.items():
            source_path = self.root / source_relative
            packet_path = self.packet / packet_relative
            content = f"source copy for {source_relative}\n".encode("utf-8")
            source_path.parent.mkdir(parents=True, exist_ok=True)
            packet_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_bytes(content)
            packet_path.write_bytes(content)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def failures(
        self,
        *,
        required: dict[str, tuple[str, ...]] | None = None,
        mappings: tuple[tuple[str, str], ...] | None = None,
        allowed: set[str] | None = None,
    ) -> list[str]:
        return play_submission_doc_coverage_failures(
            root=self.root,
            packet=self.packet,
            required_files=required or self.required,
            mappings=mappings if mappings is not None else self.mappings,
            allowed_files=allowed if allowed is not None else self.allowed,
            optional_allowed_files=set(),
        )

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_special_destinations_are_expected(self) -> None:
        self.assertEqual("project/README.md", self.expected["README.md"])
        self.assertEqual("project/AGENTS.md", self.expected["AGENTS.md"])
        self.assertEqual("text/store_listing_ru.md", self.expected["docs/store_listing_ru.md"])
        self.assertEqual("text/privacy_policy_draft_ru.md", self.expected["docs/privacy_policy_draft_ru.md"])
        self.assertEqual("text/privacy_policy_ru.html", self.expected["docs/privacy_policy_ru.html"])
        self.assertEqual("docs/product_spec.md", self.expected["docs/product_spec.md"])

    def test_missing_sync_mapping_fails(self) -> None:
        mappings = tuple(pair for pair in self.mappings if pair[0] != "docs/product_spec.md")
        failures = self.failures(mappings=mappings)
        self.assertTrue(
            any("required document is missing from packet sync mapping: docs/product_spec.md" in item for item in failures)
        )

    def test_wrong_sync_destination_fails(self) -> None:
        mappings = tuple(
            ("docs/product_spec.md", "docs/wrong_product_spec.md") if pair[0] == "docs/product_spec.md" else pair
            for pair in self.mappings
        )
        failures = self.failures(mappings=mappings)
        self.assertTrue(any("required document has wrong packet sync destination" in item for item in failures))

    def test_missing_allowlist_entry_fails(self) -> None:
        allowed = set(self.allowed)
        allowed.remove("docs/product_spec.md")
        failures = self.failures(allowed=allowed)
        self.assertTrue(any("required document packet path is not allowlisted: docs/product_spec.md" in item for item in failures))

    def test_missing_packet_copy_fails(self) -> None:
        (self.packet / "docs/product_spec.md").unlink()
        failures = self.failures()
        self.assertTrue(any("required document packet copy is missing: docs/product_spec.md" in item for item in failures))

    def test_stale_packet_copy_fails(self) -> None:
        (self.packet / "docs/product_spec.md").write_text("stale copy\n", encoding="utf-8")
        failures = self.failures()
        self.assertTrue(any("required document packet copy is stale: docs/product_spec.md" in item for item in failures))

    def test_unsupported_required_source_fails(self) -> None:
        required = dict(self.required)
        required["OTHER.md"] = ("Other",)
        (self.root / "OTHER.md").write_text("Other\n", encoding="utf-8")
        failures = self.failures(required=required)
        self.assertTrue(any("required document has no packet destination rule: OTHER.md" in item for item in failures))


if __name__ == "__main__":
    unittest.main(verbosity=2)
