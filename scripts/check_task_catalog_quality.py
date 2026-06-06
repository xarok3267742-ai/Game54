#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "app" / "src" / "main" / "res" / "raw" / "tasks_ru.json"

REQUIRED_KEYS = {"id", "area", "energy", "minutes", "title", "steps", "resultText"}
AREA_PREFIXES = {
    "Home": "home",
    "Work": "work",
    "Digital": "digital",
    "Kitchen": "kitchen",
    "Personal": "personal",
}
ALLOWED_ENERGIES = {"Light", "Medium", "Active"}
ALLOWED_MINUTES = {3, 5, 10}
MIN_ENERGY_COUNTS = {"Light": 20, "Medium": 20, "Active": 15}
MIN_MINUTE_COUNTS = {3: 20, 5: 20, 10: 15}
EXPECTED_TASKS_PER_AREA = 16
EXPECTED_TOTAL_TASKS = EXPECTED_TASKS_PER_AREA * len(AREA_PREFIXES)
EXPECTED_STEPS_PER_TASK = 3

CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
LATIN_RE = re.compile(r"[A-Za-z]")
MULTISPACE_RE = re.compile(r"\s{2,}")
ID_RE = re.compile(r"^(?P<prefix>[a-z]+)_(?P<number>\d{3})$")
FORBIDDEN_TOKENS = ("TO" + "DO", "FIX" + "ME", "Lor" + "em", "place" + "holder", "Hello" + " world")


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_catalog(failures: list[str]) -> list[Any]:
    if not CATALOG.exists():
        fail(f"missing task catalog: {display_path(CATALOG)}", failures)
        return []

    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"task catalog is not valid JSON: {exc}", failures)
        return []

    if not isinstance(data, list):
        fail("task catalog root must be a JSON array", failures)
        return []

    return data


def check_text(
    *,
    value: Any,
    label: str,
    task_id: str,
    min_chars: int,
    max_chars: int,
    should_end_with_punctuation: bool,
    failures: list[str],
) -> str:
    if not isinstance(value, str):
        fail(f"{task_id}: {label} must be a string", failures)
        return ""

    if value != value.strip():
        fail(f"{task_id}: {label} has leading or trailing whitespace", failures)
    if MULTISPACE_RE.search(value):
        fail(f"{task_id}: {label} has repeated whitespace", failures)
    if not CYRILLIC_RE.search(value):
        fail(f"{task_id}: {label} must contain Cyrillic text", failures)
    if LATIN_RE.search(value):
        fail(f"{task_id}: {label} must not contain Latin letters", failures)
    if not (min_chars <= len(value) <= max_chars):
        fail(f"{task_id}: {label} length {len(value)} is outside {min_chars}..{max_chars}", failures)
    if should_end_with_punctuation and value[-1:] not in ".!?":
        fail(f"{task_id}: {label} must end with sentence punctuation", failures)

    lower_value = value.casefold()
    for token in FORBIDDEN_TOKENS:
        if token.casefold() in lower_value:
            fail(f"{task_id}: {label} contains a draft marker", failures)

    return value


def check_task(index: int, task: Any, failures: list[str]) -> dict[str, Any] | None:
    if not isinstance(task, dict):
        fail(f"task at index {index} must be a JSON object", failures)
        return None

    task_id = str(task.get("id", f"index_{index}"))
    keys = set(task)
    missing = sorted(REQUIRED_KEYS - keys)
    extra = sorted(keys - REQUIRED_KEYS)
    if missing:
        fail(f"{task_id}: missing keys: {', '.join(missing)}", failures)
    if extra:
        fail(f"{task_id}: unexpected keys: {', '.join(extra)}", failures)

    raw_id = task.get("id")
    if not isinstance(raw_id, str):
        fail(f"{task_id}: id must be a string", failures)
        raw_id = task_id
    id_match = ID_RE.match(raw_id)

    area = task.get("area")
    if area not in AREA_PREFIXES:
        fail(f"{raw_id}: area must be one of {sorted(AREA_PREFIXES)}", failures)
    elif not id_match or id_match.group("prefix") != AREA_PREFIXES[area]:
        fail(f"{raw_id}: id prefix must match area {area}", failures)

    energy = task.get("energy")
    if energy not in ALLOWED_ENERGIES:
        fail(f"{raw_id}: energy must be one of {sorted(ALLOWED_ENERGIES)}", failures)

    minutes = task.get("minutes")
    if type(minutes) is not int:
        fail(f"{raw_id}: minutes must be an integer", failures)
    elif minutes not in ALLOWED_MINUTES:
        fail(f"{raw_id}: minutes must be one of {sorted(ALLOWED_MINUTES)}", failures)

    title = check_text(
        value=task.get("title"),
        label="title",
        task_id=raw_id,
        min_chars=8,
        max_chars=60,
        should_end_with_punctuation=False,
        failures=failures,
    )
    result_text = check_text(
        value=task.get("resultText"),
        label="resultText",
        task_id=raw_id,
        min_chars=24,
        max_chars=96,
        should_end_with_punctuation=True,
        failures=failures,
    )

    steps = task.get("steps")
    checked_steps: list[str] = []
    if not isinstance(steps, list):
        fail(f"{raw_id}: steps must be an array", failures)
    elif len(steps) != EXPECTED_STEPS_PER_TASK:
        fail(f"{raw_id}: steps must contain exactly {EXPECTED_STEPS_PER_TASK} items", failures)
    else:
        for step_index, step in enumerate(steps, start=1):
            checked_steps.append(
                check_text(
                    value=step,
                    label=f"steps[{step_index}]",
                    task_id=raw_id,
                    min_chars=10,
                    max_chars=96,
                    should_end_with_punctuation=True,
                    failures=failures,
                )
            )
        if len(set(checked_steps)) != len(checked_steps):
            fail(f"{raw_id}: steps must not repeat within one task", failures)

    return {
        "id": raw_id,
        "area": area,
        "energy": energy,
        "minutes": minutes,
        "title": title,
        "resultText": result_text,
        "steps": checked_steps,
    }


def check_distribution(tasks: list[dict[str, Any]], failures: list[str]) -> None:
    ids = [task["id"] for task in tasks]
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        fail("duplicate task ids: " + ", ".join(duplicate_ids), failures)

    title_keys = [task["title"].casefold() for task in tasks if task["title"]]
    duplicate_titles = sorted(item for item, count in Counter(title_keys).items() if count > 1)
    if duplicate_titles:
        fail("duplicate task titles detected", failures)

    step_keys = [step.casefold() for task in tasks for step in task["steps"] if step]
    duplicate_steps = sorted(item for item, count in Counter(step_keys).items() if count > 1)
    if duplicate_steps:
        fail("duplicate task steps detected", failures)

    area_counts = Counter(task["area"] for task in tasks)
    for area in AREA_PREFIXES:
        actual = area_counts.get(area, 0)
        if actual != EXPECTED_TASKS_PER_AREA:
            fail(f"area {area} has {actual} tasks, expected {EXPECTED_TASKS_PER_AREA}", failures)

    energy_counts = Counter(task["energy"] for task in tasks)
    for energy, minimum in MIN_ENERGY_COUNTS.items():
        actual = energy_counts.get(energy, 0)
        if actual < minimum:
            fail(f"energy {energy} has {actual} tasks, expected at least {minimum}", failures)

    minute_counts = Counter(task["minutes"] for task in tasks)
    for minutes, minimum in MIN_MINUTE_COUNTS.items():
        actual = minute_counts.get(minutes, 0)
        if actual < minimum:
            fail(f"duration {minutes} has {actual} tasks, expected at least {minimum}", failures)

    for area, prefix in AREA_PREFIXES.items():
        numbers: list[int] = []
        for task_id in ids:
            match = ID_RE.match(task_id)
            if match and match.group("prefix") == prefix:
                numbers.append(int(match.group("number")))
        expected_numbers = list(range(1, EXPECTED_TASKS_PER_AREA + 1))
        if sorted(numbers) != expected_numbers:
            fail(f"area {area} ids must be sequential {prefix}_001..{prefix}_016", failures)


def main() -> int:
    failures: list[str] = []
    raw_tasks = load_catalog(failures)

    if len(raw_tasks) != EXPECTED_TOTAL_TASKS:
        fail(f"task catalog contains {len(raw_tasks)} tasks, expected {EXPECTED_TOTAL_TASKS}", failures)

    checked_tasks = [
        checked
        for index, raw_task in enumerate(raw_tasks)
        if (checked := check_task(index, raw_task, failures)) is not None
    ]
    check_distribution(checked_tasks, failures)

    if failures:
        print("Task catalog quality check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    area_counts = Counter(task["area"] for task in checked_tasks)
    energy_counts = Counter(task["energy"] for task in checked_tasks)
    minute_counts = Counter(task["minutes"] for task in checked_tasks)
    max_title = max(len(task["title"]) for task in checked_tasks)
    max_step = max(len(step) for task in checked_tasks for step in task["steps"])
    max_result = max(len(task["resultText"]) for task in checked_tasks)

    print(
        "PASS: task catalog quality covers "
        f"{len(checked_tasks)} tasks; "
        f"areas={dict(sorted(area_counts.items()))}; "
        f"energies={dict(sorted(energy_counts.items()))}; "
        f"minutes={dict(sorted(minute_counts.items()))}; "
        f"max_lengths=title:{max_title},step:{max_step},result:{max_result}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
