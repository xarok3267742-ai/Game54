#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_SOURCE = ROOT / "app" / "src" / "main" / "java"
ENGINE = MAIN_SOURCE / "ru" / "poryadok5" / "app" / "domain" / "PoryadokEngine.kt"
UI = MAIN_SOURCE / "ru" / "poryadok5" / "app" / "ui" / "PoryadokApp.kt"
TEST = ROOT / "app" / "src" / "test" / "java" / "ru" / "poryadok5" / "app" / "TaskCatalogTest.kt"

FORBIDDEN_RUNTIME_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("hardcoded progress denominator", re.compile(r"\bиз\s+80\b", re.IGNORECASE)),
    ("hardcoded catalog microtask count", re.compile(r"\b80\s+микрозадач", re.IGNORECASE)),
    ("hardcoded unique task count", re.compile(r"\b80\s+уникальн", re.IGNORECASE)),
)

REQUIRED_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (ENGINE, ("fun totalTasks(): Int = tasks.size",)),
    (UI, ("engine.totalTasks()", "catalogSize: Int", "$catalogSize задач")),
    (TEST, ("engineReportsCatalogSizeForRuntimeUi", "assertEquals(3, engine.totalTasks())")),
)


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def runtime_catalog_count_failures(
    root: Path = ROOT,
    main_source: Path = MAIN_SOURCE,
    required_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = REQUIRED_SNIPPETS,
) -> list[str]:
    failures: list[str] = []

    if not main_source.exists():
        return [f"missing runtime source directory: {display_path(main_source, root)}"]

    for path in sorted(main_source.rglob("*.kt")):
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_RUNTIME_PATTERNS:
            for match in pattern.finditer(text):
                line_number = text.count("\n", 0, match.start()) + 1
                failures.append(f"{display_path(path, root)}:{line_number}: {label}")

    for path, snippets in required_snippets:
        if not path.exists():
            failures.append(f"missing catalog-count evidence file: {display_path(path, root)}")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                failures.append(f"{display_path(path, root)} is missing required snippet: {snippet}")

    return failures


def main() -> int:
    failures = runtime_catalog_count_failures()
    if failures:
        print("Runtime catalog count check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: runtime catalog count is derived from PoryadokEngine instead of hardcoded UI text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
