#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_ACTIVITY = ROOT / "app/src/main/java/ru/poryadok5/app/MainActivity.kt"
PRODUCT_SPEC = ROOT / "docs/product_spec.md"
UI_AUDIT = ROOT / "docs/ui_audit.md"
QA_PLAN = ROOT / "docs/qa_test_plan.md"

MAIN_REQUIRED_MARKERS: tuple[str, ...] = (
    "var loadAttempt by remember { mutableIntStateOf(0) }",
    "LaunchedEffect(taskRepository, loadAttempt)",
    "tasks = null",
    "loadError = null",
    "loadError = \"Не удалось прочитать локальный список задач.\"",
    "StartupErrorState(",
    "onRetry = { loadAttempt += 1 }",
    "private fun StartupErrorState(message: String, onRetry: () -> Unit)",
    'text = "Не удалось запустить приложение"',
    '"Каталог хранится на устройстве. Попробуйте загрузить его ещё раз."',
    'PrimaryAction("Повторить загрузку", onRetry)',
)

FORBIDDEN_MARKERS: tuple[str, ...] = (
    "loadError = it.message",
    "private fun ErrorState(",
    'Text(\n            text = "Не удалось запустить приложение.\\n$message"',
)

DOC_REQUIRED_MARKERS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (PRODUCT_SPEC, ("Startup error", "Повторить загрузку", "generic Russian")),
    (UI_AUDIT, ("Startup error retry", "Повторить загрузку", "generic Russian")),
    (QA_PLAN, ("check_startup_error_retry.py", "Startup error retry")),
)


def read_doc(path: Path, docs: dict[str, str] | None, root: Path) -> str | None:
    doc_key = str(path.relative_to(root))
    if docs is not None:
        return docs.get(doc_key, "")
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def startup_error_retry_failures(
    main_source: str | None = None,
    docs: dict[str, str] | None = None,
    main_path: Path = MAIN_ACTIVITY,
    root: Path = ROOT,
) -> list[str]:
    if main_source is None:
        if not main_path.exists():
            return [f"missing MainActivity: {main_path.relative_to(root)}"]
        main_source = main_path.read_text(encoding="utf-8")

    failures: list[str] = []
    for marker in MAIN_REQUIRED_MARKERS:
        if marker not in main_source:
            failures.append(f"Startup error retry is missing marker: {marker}")

    for marker in FORBIDDEN_MARKERS:
        if marker in main_source:
            failures.append(f"Startup error retry contains forbidden marker: {marker}")

    effect = function_body(main_source, "onCreate")
    if effect and effect.find("tasks = null") > effect.find("loadError = null"):
        failures.append("Startup retry should clear tasks before clearing the error state for a clean loading transition")

    for path, markers in DOC_REQUIRED_MARKERS:
        text = read_doc(path, docs, root)
        if text is None:
            failures.append(f"missing documentation file: {path.relative_to(root)}")
            continue
        for marker in markers:
            if marker not in text:
                failures.append(f"{path.relative_to(root)} is missing marker: {marker}")

    return failures


def function_body(source: str, name: str) -> str:
    match = re.search(rf"\bfun\s+{re.escape(name)}\s*\(", source)
    if not match:
        return ""
    return source[match.start():]


def main() -> int:
    failures = startup_error_retry_failures()
    if failures:
        print("Startup error-retry check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: startup catalog errors stay generic and offer a retry action")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
