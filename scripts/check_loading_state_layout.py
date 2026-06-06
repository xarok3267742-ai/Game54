#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "app/src/main/java/ru/poryadok5/app/ui/components/AppComponents.kt"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"
ACCESSIBILITY_NOTES = ROOT / "docs/accessibility_notes.md"

LOADING_REQUIRED_MARKERS: tuple[str, ...] = (
    "fun LoadingState(message: String)",
    ".fillMaxSize()",
    "contentAlignment = Alignment.Center",
    "CircularProgressIndicator(color = Sage)",
    "verticalArrangement = Arrangement.spacedBy(16.dp)",
    "Text(message, style = MaterialTheme.typography.bodyMedium)",
)

FORBIDDEN_MARKERS: tuple[str, ...] = (
    ".fillMaxWidth()\n            .padding(32.dp)",
    "Spacer(Modifier.height(16.dp))",
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (UI_AUDIT, ("Loading states", "full-screen centered")),
    (QA_PLAN, ("check_loading_state_layout.py", "Loading state layout")),
    (ACCESSIBILITY_NOTES, ("Loading state", "centered")),
)


def function_body(source: str, name: str) -> str:
    marker = f"fun {name}("
    start = source.find(marker)
    if start < 0:
        return ""
    next_match = re.search(r"\n@Composable\n(?:private\s+)?fun\s+", source[start + len(marker):])
    if next_match is None:
        return source[start:]
    return source[start:start + len(marker) + next_match.start()]


def read_doc(path: Path, docs: dict[str, str] | None, root: Path) -> str | None:
    doc_key = str(path.relative_to(root))
    if docs is not None:
        return docs.get(doc_key, "")
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def loading_state_layout_failures(
    components_source: str | None = None,
    docs: dict[str, str] | None = None,
    components_path: Path = COMPONENTS,
    root: Path = ROOT,
) -> list[str]:
    if components_source is None:
        if not components_path.exists():
            return [f"missing components file: {components_path.relative_to(root)}"]
        components_source = components_path.read_text(encoding="utf-8")

    failures: list[str] = []
    loading = function_body(components_source, "LoadingState")
    if not loading:
        failures.append("LoadingState body was not found")
    else:
        for marker in LOADING_REQUIRED_MARKERS:
            if marker not in loading:
                failures.append(f"Loading state layout is missing marker: {marker}")
        for marker in FORBIDDEN_MARKERS:
            if marker in loading:
                failures.append(f"Loading state layout contains old marker: {marker}")

    for path, markers in DOC_REQUIRED_MARKERS:
        text = read_doc(path, docs, root)
        if text is None:
            failures.append(f"missing documentation file: {path.relative_to(root)}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"{path.relative_to(root)} is missing marker: {marker}")

    return failures


def main() -> int:
    failures = loading_state_layout_failures()
    if failures:
        print("Loading state layout check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: LoadingState is full-screen, centered and product-consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
