#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/src/main/java/ru/poryadok5/app/ui/PoryadokApp.kt"

REQUIRED_SNIPPETS = (
    "private val AppScreenSaver = Saver<AppScreen, String>",
    "save = { screen -> screen.toRoute() }",
    "restore = { route -> appScreenFromRoute(route) }",
    "var screen by rememberSaveable(stateSaver = AppScreenSaver)",
    'is AppScreen.Details -> "details:$taskId"',
    'is AppScreen.Timer -> "timer:$taskId"',
    'is AppScreen.Result -> "result:$taskId"',
    "import ru.poryadok5.app.domain.isRouteSafeTaskId",
    "val routeTaskId = taskId.takeIf(::isRouteSafeTaskId)",
    '"details" -> routeTaskId?.let(AppScreen::Details) ?: AppScreen.Home',
    '"timer" -> routeTaskId?.let(AppScreen::Timer) ?: AppScreen.Home',
    '"result" -> routeTaskId?.let(AppScreen::Result) ?: AppScreen.Home',
    "else -> AppScreen.Home",
)

FORBIDDEN_SNIPPETS = (
    ("var screen by remember {", "screen state must survive Activity recreation"),
)


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def screen_state_saveability_failures(app_path: Path = APP) -> list[str]:
    if not app_path.exists():
        return [f"missing app UI file: {display_path(app_path)}"]

    source = app_path.read_text(encoding="utf-8")
    failures: list[str] = []
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in source:
            failures.append(f"{display_path(app_path)} is missing screen saveability snippet: {snippet}")

    for snippet, reason in FORBIDDEN_SNIPPETS:
        if snippet in source:
            failures.append(f"{display_path(app_path)} contains forbidden snippet {snippet!r}: {reason}")

    return failures


def main() -> int:
    failures = screen_state_saveability_failures()
    if failures:
        print("Screen state saveability check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: App screen state is saveable across Activity recreation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
