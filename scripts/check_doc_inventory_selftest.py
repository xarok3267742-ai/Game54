#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_doc_inventory.py"

spec = importlib.util.spec_from_file_location("doc_inventory_checker", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def assert_equal(actual: object, expected: object) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def assert_failure_contains(failures: list[str], expected: str) -> None:
    assert any(expected in failure for failure in failures), failures


def write_valid_fixture(root: Path) -> None:
    filler = (
        "\nДокумент проверяет релиз-кандидат Порядок 5, локальные артефакты, "
        "ручные действия Google Play и доказательства готовности.\n"
    )
    for relative_path, snippets in checker.REQUIRED_FILES.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        body = f"# {relative_path}\n" + "\n".join(snippets) + filler
        while len(body.encode("utf-8")) < checker.MIN_BYTES + 20:
            body += filler
        path.write_text(body, encoding="utf-8")

    inventory_lines = [
        "# Documentation Inventory\n\n",
        "This inventory keeps story_bible.md absent for this non-story product.\n\n",
        "| Requirement | File | Status |\n",
        "|---|---|---|\n",
    ]
    for relative_path in checker.REQUIRED_FILES:
        inventory_lines.append(f"| Test row | `{relative_path}` | RC_READY |\n")
    (root / checker.DOC_INVENTORY_PATH).write_text("".join(inventory_lines), encoding="utf-8")


def with_fixture(test_body) -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="poryadok5-doc-inventory-test."))
    try:
        write_valid_fixture(temp_dir)
        test_body(temp_dir)
    finally:
        shutil.rmtree(temp_dir)


def test_valid_inventory_passes() -> None:
    def run(root: Path) -> None:
        assert_equal(checker.doc_inventory_failures(root), [])

    with_fixture(run)


def test_missing_document_fails() -> None:
    def run(root: Path) -> None:
        (root / "docs/product_spec.md").unlink()
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(failures, "missing required document: docs/product_spec.md")

    with_fixture(run)


def test_directory_instead_of_document_fails() -> None:
    def run(root: Path) -> None:
        path = root / "docs/ui_audit.md"
        path.unlink()
        path.mkdir()
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(failures, "required document is not a file: docs/ui_audit.md")

    with_fixture(run)


def test_tiny_document_fails() -> None:
    def run(root: Path) -> None:
        (root / "docs/release_plan.md").write_text("RC Target", encoding="utf-8")
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(failures, "document is too small to prove coverage: docs/release_plan.md")

    with_fixture(run)


def test_missing_required_marker_fails() -> None:
    def run(root: Path) -> None:
        path = root / "docs/google_play_checklist.md"
        text = path.read_text(encoding="utf-8").replace("Manual Play Console Actions", "Ручные действия консоли")
        path.write_text(text, encoding="utf-8")
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(
            failures,
            "docs/google_play_checklist.md is missing required marker: Manual Play Console Actions",
        )

    with_fixture(run)


def test_inventory_table_missing_required_row_fails() -> None:
    def run(root: Path) -> None:
        path = root / checker.DOC_INVENTORY_PATH
        text = path.read_text(encoding="utf-8")
        text = text.replace("| Test row | `docs/product_spec.md` | RC_READY |\n", "")
        path.write_text(text, encoding="utf-8")
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(
            failures,
            "documentation inventory table is missing required file row: docs/product_spec.md",
        )

    with_fixture(run)


def test_inventory_table_unexpected_row_fails() -> None:
    def run(root: Path) -> None:
        path = root / checker.DOC_INVENTORY_PATH
        text = path.read_text(encoding="utf-8")
        text += "| Stale row | `docs/old_release_notes.md` | STALE |\n"
        path.write_text(text, encoding="utf-8")
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(
            failures,
            "documentation inventory table has unexpected file row: docs/old_release_notes.md",
        )

    with_fixture(run)


def test_inventory_table_allowed_tooling_row_passes() -> None:
    def run(root: Path) -> None:
        path = root / checker.DOC_INVENTORY_PATH
        text = path.read_text(encoding="utf-8")
        text += "| Tooling row | `scripts/check_qa_evidence.py` | LOCAL_PROVEN |\n"
        path.write_text(text, encoding="utf-8")
        assert_equal(checker.doc_inventory_failures(root), [])

    with_fixture(run)


def test_inventory_table_duplicate_row_fails() -> None:
    def run(root: Path) -> None:
        path = root / checker.DOC_INVENTORY_PATH
        text = path.read_text(encoding="utf-8")
        text += "| Duplicate row | `docs/product_spec.md` | RC_READY |\n"
        path.write_text(text, encoding="utf-8")
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(
            failures,
            "documentation inventory table has duplicate file row: docs/product_spec.md",
        )

    with_fixture(run)


def test_inventory_table_missing_fails() -> None:
    def run(root: Path) -> None:
        path = root / checker.DOC_INVENTORY_PATH
        path.write_text("# Documentation Inventory\n\nstory_bible.md\n", encoding="utf-8")
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(failures, "documentation inventory table is missing or has no file rows")

    with_fixture(run)


def test_story_bible_file_fails() -> None:
    def run(root: Path) -> None:
        path = root / "docs/story_bible.md"
        path.write_text("Сюжетный документ не нужен для этого продукта.", encoding="utf-8")
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(failures, "story bible files must be absent")

    with_fixture(run)


def test_story_bible_root_file_fails() -> None:
    def run(root: Path) -> None:
        path = root / "story_bible.md"
        path.write_text("Сюжетный документ не нужен для этого продукта.", encoding="utf-8")
        failures = checker.doc_inventory_failures(root)
        assert_failure_contains(failures, "story bible files must be absent")

    with_fixture(run)


def test_story_bible_inside_build_is_ignored() -> None:
    def run(root: Path) -> None:
        path = root / "app/build/story_bible.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Сгенерированный build файл игнорируется.", encoding="utf-8")
        assert_equal(checker.doc_inventory_failures(root), [])

    with_fixture(run)


def main() -> int:
    tests = [
        test_valid_inventory_passes,
        test_missing_document_fails,
        test_directory_instead_of_document_fails,
        test_tiny_document_fails,
        test_missing_required_marker_fails,
        test_inventory_table_missing_required_row_fails,
        test_inventory_table_unexpected_row_fails,
        test_inventory_table_allowed_tooling_row_passes,
        test_inventory_table_duplicate_row_fails,
        test_inventory_table_missing_fails,
        test_story_bible_file_fails,
        test_story_bible_root_file_fails,
        test_story_bible_inside_build_is_ignored,
    ]
    for test in tests:
        test()
    print("PASS: documentation inventory checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
