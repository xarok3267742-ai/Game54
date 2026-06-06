#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT / "app" / "src" / "main" / "java" / "ru" / "poryadok5" / "app" / "data" / "TaskRepository.kt"
MAIN_ACTIVITY = ROOT / "app" / "src" / "main" / "java" / "ru" / "poryadok5" / "app" / "MainActivity.kt"
TEST = ROOT / "app" / "src" / "test" / "java" / "ru" / "poryadok5" / "app" / "TaskCatalogTest.kt"

REQUIRED_SNIPPETS: tuple[tuple[Path, tuple[str, ...]], ...] = (
    (
        REPOSITORY,
        (
            "internal fun parseTaskCatalog",
            "import ru.poryadok5.app.domain.SupportedTaskMinutes",
            "import ru.poryadok5.app.domain.isRouteSafeTaskId",
            "require(tasks.isNotEmpty())",
            "val ids = mutableSetOf<String>()",
            "parseTaskId(item.getString(\"id\"))",
            "val area = parseCatalogArea(item.getString(\"area\"), id)",
            "validateTaskIdArea(id, area)",
            "require(ids.add(id))",
            "area = area",
            "parseCatalogEnergy(item.getString(\"energy\"), id)",
            "parseTaskMinutes(item.getInt(\"minutes\"), id)",
            "parseRequiredText(item.getString(\"title\"), id, \"название\")",
            "parseTaskSteps(item.getJSONArray(\"steps\"), id)",
            "parseRequiredText(item.getString(\"resultText\"), id, \"результат\")",
            "Задача должна содержать id",
            "isRouteSafeTaskId(id)",
            "неподдерживаемый id",
            "private fun validateTaskIdArea(id: String, area: TaskArea)",
            "area.catalogIdPrefix()",
            "не соответствует зоне",
            "Повторяющийся id задачи",
            "require(value in SupportedTaskMinutes)",
            "неподдерживаемое время",
            "require(stepsJson.length() == 3)",
            "Неизвестная зона задачи",
            "Неизвестный уровень энергии задачи",
            "содержит пустой шаг",
        ),
    ),
    (MAIN_ACTIVITY, ("loadError = \"Не удалось прочитать локальный список задач.\"",)),
    (
        TEST,
        (
            "taskParserRejectsEmptyCatalog",
            "taskParserRejectsUnknownAreaInsteadOfFallingBack",
            "taskParserRejectsUnknownEnergyInsteadOfFallingBack",
            "taskParserRejectsBlankId",
            "taskParserRejectsRouteUnsafeId",
            "taskParserRejectsIdAreaMismatch",
            "taskParserRejectsDuplicateIds",
            "taskParserRejectsUnsupportedMinutes",
            "taskParserRejectsBlankTitle",
            "taskParserRejectsWrongStepCountBeforeUiCanReadFirstStep",
            "taskParserRejectsBlankStep",
            "taskParserRejectsBlankResultText",
        ),
    ),
)

FORBIDDEN_SNIPPETS: tuple[tuple[Path, str, str], ...] = (
    (REPOSITORY, "TaskArea.fromRaw", "task catalog parser must not silently fall back for unknown areas"),
    (REPOSITORY, "EnergyLevel.fromRaw", "task catalog parser must not silently fall back for unknown energy levels"),
    (REPOSITORY, "require(value in setOf(3, 5, 10))", "task catalog parser must use shared SupportedTaskMinutes"),
    (REPOSITORY, "val area = TaskArea.fromRaw", "task catalog parser must not derive area permissively"),
    (REPOSITORY, "TaskIdPattern.matches(id)", "task catalog parser must use shared isRouteSafeTaskId"),
    (MAIN_ACTIVITY, "loadError = it.message", "user-facing launch error must not expose technical exception text"),
)


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def task_repository_parser_failures(
    required_snippets: tuple[tuple[Path, tuple[str, ...]], ...] = REQUIRED_SNIPPETS,
    forbidden_snippets: tuple[tuple[Path, str, str], ...] = FORBIDDEN_SNIPPETS,
) -> list[str]:
    failures: list[str] = []

    for path, snippets in required_snippets:
        if not path.exists():
            failures.append(f"missing parser evidence file: {display_path(path)}")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                failures.append(f"{display_path(path)} is missing required parser snippet: {snippet}")

    for path, snippet, reason in forbidden_snippets:
        if not path.exists():
            continue
        if snippet in path.read_text(encoding="utf-8"):
            failures.append(f"{display_path(path)} contains forbidden snippet {snippet!r}: {reason}")

    return failures


def main() -> int:
    failures = task_repository_parser_failures()
    if failures:
        print("Task repository parser check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: task repository parser is strict for catalog ids/enums/minutes/text/steps "
        "and launch errors stay generic Russian text"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
