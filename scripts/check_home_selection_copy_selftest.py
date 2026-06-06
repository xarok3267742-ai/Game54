#!/usr/bin/env python3
from __future__ import annotations

import unittest

from check_home_selection_copy import home_selection_copy_failures

VALID_APP = """
private fun TaskSuggestionQuality.homeSelectionNote(): String {
    return when (this) {
        TaskSuggestionQuality.Exact -> "Совпадает с выбором"
        TaskSuggestionQuality.AreaAndDuration -> "Зона и время совпали"
        TaskSuggestionQuality.CatalogFallback -> "Ближайшая свободная задача"
    }
}
"""

VALID_DOCS = {
    "docs/product_spec.md": "Home shows Совпадает с выбором and Ближайшая свободная задача.",
    "docs/ui_audit.md": "Home selection copy is concise and без слова `фильтр`.",
    "docs/qa_test_plan.md": "check_home_selection_copy.py verifies Home selection copy.",
}


def assert_passes(failures: list[str]) -> None:
    if failures:
        raise AssertionError("expected no failures, got: " + "; ".join(failures))


def assert_fails(failures: list[str], marker: str) -> None:
    if not any(marker in failure for failure in failures):
        raise AssertionError(f"expected failure containing {marker!r}, got: {failures!r}")


class HomeSelectionCopySelfTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        assert_passes(home_selection_copy_failures(app_source=VALID_APP, docs=VALID_DOCS))

    def test_missing_exact_copy_fails(self) -> None:
        broken = VALID_APP.replace("Совпадает с выбором", "Точно по выбору")
        assert_fails(home_selection_copy_failures(app_source=broken, docs=VALID_DOCS), "Совпадает с выбором")

    def test_old_filter_copy_fails(self) -> None:
        broken = VALID_APP.replace("Совпадает с выбором", "Подбор: точно по фильтру")
        assert_fails(home_selection_copy_failures(app_source=broken, docs=VALID_DOCS), "technical wording")

    def test_missing_doc_marker_fails(self) -> None:
        docs = dict(VALID_DOCS)
        docs["docs/ui_audit.md"] = "Home selection copy is concise."
        assert_fails(home_selection_copy_failures(app_source=VALID_APP, docs=docs), "docs/ui_audit.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
