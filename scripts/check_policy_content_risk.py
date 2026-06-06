#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "app" / "src" / "main" / "res" / "raw" / "tasks_ru.json"
STORE_LISTING = ROOT / "docs" / "store_listing_ru.md"
FORMS = ROOT / "docs" / "play_console_forms_answers.json"


@dataclass(frozen=True)
class RiskCategory:
    form_path: tuple[str, str]
    patterns: tuple[str, ...]
    sources: tuple[str, ...]


RISK_CATEGORIES: dict[str, RiskCategory] = {
    "violence": RiskCategory(
        form_path=("contentRating", "violence"),
        patterns=(r"\bнасили", r"\bоруж", r"\bкров", r"\bубий", r"\bдрак", r"\bвойн", r"\bтеррор", r"\bweapon", r"\bkill"),
        sources=("task_text", "store_listing"),
    ),
    "fearHorror": RiskCategory(
        form_path=("contentRating", "fearHorror"),
        patterns=(r"\bужас", r"\bхоррор", r"\bстрах", r"\bпуга", r"\bhorror", r"\bfear"),
        sources=("task_text", "store_listing"),
    ),
    "sexualContent": RiskCategory(
        form_path=("contentRating", "sexualContent"),
        patterns=(r"\bсекс", r"\bинтим", r"\bэрот", r"\bпорн", r"\badult", r"\bsex"),
        sources=("task_text", "store_listing"),
    ),
    "controlledSubstances": RiskCategory(
        form_path=("contentRating", "controlledSubstances"),
        patterns=(r"\bалкогол", r"\bнаркот", r"\bтабак", r"\bсигар", r"\bвейп", r"\bdrug", r"\balcohol", r"\btobacco"),
        sources=("task_text", "store_listing"),
    ),
    "gambling": RiskCategory(
        form_path=("contentRating", "gambling"),
        patterns=(r"\bазарт", r"\bказино", r"\bставк", r"\bлотере", r"\bbet", r"\bcasino", r"\blottery", r"\bgambling"),
        sources=("task_text", "store_listing"),
    ),
    "userGeneratedContent": RiskCategory(
        form_path=("contentRating", "userGeneratedContent"),
        patterns=(r"пользовательск\w+\s+контент", r"\bфорум", r"\bкоммент", r"\bпрофил[ья]", r"\bugc\b"),
        sources=("store_listing",),
    ),
    "onlineInteraction": RiskCategory(
        form_path=("contentRating", "onlineInteraction"),
        patterns=(r"\bчат", r"\bмессендж", r"\bсоцсет", r"\bличн\w+\s+сообщ", r"онлайн[- ]?взаим"),
        sources=("store_listing",),
    ),
    "locationSharing": RiskCategory(
        form_path=("contentRating", "locationSharing"),
        patterns=(r"\bгеолокац", r"\bgps\b", r"\bкоординат", r"\bместополож", r"\bадрес\b", r"\blocation"),
        sources=("store_listing",),
    ),
    "medicalAdvice": RiskCategory(
        form_path=("targetAudienceAndContent", "sensitiveCategories"),
        patterns=(r"\bмедицин", r"\bлечени", r"\bдиагноз", r"\bврач", r"\bлекарств", r"\bтаблет", r"\bmedical", r"\bhealth"),
        sources=("task_text", "store_listing"),
    ),
    "financialAdvice": RiskCategory(
        form_path=("targetAudienceAndContent", "sensitiveCategories"),
        patterns=(r"\bкредит", r"\bинвест", r"\bбанк", r"\bкрипт", r"\bналог", r"\bдоход", r"\bstock", r"\bcrypto"),
        sources=("task_text", "store_listing"),
    ),
    "newsPolitics": RiskCategory(
        form_path=("targetAudienceAndContent", "sensitiveCategories"),
        patterns=(r"\bполит", r"\bвыбор", r"\bпарт", r"\bновост", r"\bpolitic", r"\bnews"),
        sources=("task_text", "store_listing"),
    ),
    "dating": RiskCategory(
        form_path=("targetAudienceAndContent", "sensitiveCategories"),
        patterns=(r"\bзнакомств", r"\bсвидан", r"\bромантич", r"\bdating"),
        sources=("task_text", "store_listing"),
    ),
    "childrenDirectedAppeal": RiskCategory(
        form_path=("targetAudienceAndContent", "childrenDirected"),
        patterns=(r"\bдетск", r"\bдети\b", r"\bреб[её]н", r"\bмалыш", r"\bшкол", r"\bchildren", r"\bkids"),
        sources=("store_listing",),
    ),
}


def read_json(path: Path, failures: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        failures.append(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        failures.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return None


def collect_task_text(failures: list[str]) -> list[tuple[str, str]]:
    data = read_json(TASKS, failures)
    if not isinstance(data, list):
        failures.append("task catalog must be a JSON array for policy content scan")
        return []

    values: list[tuple[str, str]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            failures.append(f"task at index {index} must be an object for policy content scan")
            continue
        task_id = str(item.get("id", f"index_{index}"))
        for field in ("title", "resultText"):
            value = item.get(field)
            if isinstance(value, str):
                values.append((f"task_text:{task_id}:{field}", value))
        steps = item.get("steps")
        if isinstance(steps, list):
            for step_index, step in enumerate(steps, start=1):
                if isinstance(step, str):
                    values.append((f"task_text:{task_id}:step{step_index}", step))
    return values


def collect_store_listing(failures: list[str]) -> list[tuple[str, str]]:
    if not STORE_LISTING.exists():
        failures.append(f"missing store listing: {STORE_LISTING.relative_to(ROOT)}")
        return []
    return [
        (f"store_listing:line{line_number}", line)
        for line_number, line in enumerate(STORE_LISTING.read_text(encoding="utf-8").splitlines(), start=1)
        if line.strip()
    ]


def source_values(failures: list[str]) -> dict[str, list[tuple[str, str]]]:
    return {
        "task_text": collect_task_text(failures),
        "store_listing": collect_store_listing(failures),
    }


def form_value(forms: dict[str, Any], path: tuple[str, str]) -> Any:
    section, key = path
    value = forms.get(section)
    if not isinstance(value, dict):
        return None
    return value.get(key)


def check_form_claims(forms: dict[str, Any], failures: list[str]) -> None:
    target = forms.get("targetAudienceAndContent", {})
    rating = forms.get("contentRating", {})
    if not isinstance(target, dict):
        failures.append("targetAudienceAndContent must be an object")
        target = {}
    if not isinstance(rating, dict):
        failures.append("contentRating must be an object")
        rating = {}

    if target.get("targetAgeGroups") != ["13+"]:
        failures.append("target audience must remain 13+ for the current RC")
    for key in ("designedForChildren", "appealsPrimarilyToChildren", "childrenDirected", "userGeneratedContent", "purchases", "ads"):
        if target.get(key) is not False:
            failures.append(f"targetAudienceAndContent.{key} must be false")
    if target.get("sensitiveCategories") != []:
        failures.append("targetAudienceAndContent.sensitiveCategories must remain empty")

    for key in ("violence", "fearHorror", "sexualContent", "controlledSubstances", "gambling", "userGeneratedContent", "onlineInteraction", "locationSharing", "purchases", "ads"):
        if rating.get(key) is not False:
            failures.append(f"contentRating.{key} must be false")


def scan_categories(forms: dict[str, Any], values_by_source: dict[str, list[tuple[str, str]]], failures: list[str]) -> int:
    match_count = 0
    for category, metadata in RISK_CATEGORIES.items():
        expected_value = form_value(forms, metadata.form_path)
        if metadata.form_path[1] == "sensitiveCategories":
            category_declared_absent = expected_value == []
        else:
            category_declared_absent = expected_value is False

        if not category_declared_absent:
            failures.append(f"{category}: Play Console form claim is not absent/false")
            continue

        compiled = [re.compile(pattern, flags=re.IGNORECASE) for pattern in metadata.patterns]
        for source_name in metadata.sources:
            for label, text in values_by_source.get(source_name, []):
                for pattern in compiled:
                    if pattern.search(text):
                        match_count += 1
                        failures.append(f"{category}: risky term matched {pattern.pattern!r} in {label}: {text}")
    return match_count


def check_positive_low_risk_claims(values_by_source: dict[str, list[tuple[str, str]]], failures: list[str]) -> None:
    listing = "\n".join(text for _, text in values_by_source.get("store_listing", [])).casefold()
    required_claims = (
        "без аккаунта",
        "не требует интернета",
        "не показывает рекламу",
        "не использует аналитику",
        "не собирает персональные данные",
    )
    for claim in required_claims:
        if claim not in listing:
            failures.append(f"store listing must keep low-risk claim: {claim}")


def policy_content_failures(forms: object, values_by_source: dict[str, list[tuple[str, str]]]) -> tuple[list[str], int]:
    failures: list[str] = []
    normalized_values = {
        "task_text": values_by_source.get("task_text", []),
        "store_listing": values_by_source.get("store_listing", []),
    }

    if not isinstance(forms, dict):
        failures.append("Play Console forms answers must be a JSON object")
        forms = {}

    check_form_claims(forms, failures)
    scan_categories(forms, normalized_values, failures)
    check_positive_low_risk_claims(normalized_values, failures)
    scanned_values = sum(len(values) for values in normalized_values.values())
    return failures, scanned_values


def main() -> int:
    failures: list[str] = []
    forms = read_json(FORMS, failures)
    values_by_source = source_values(failures)
    content_failures, scanned_values = policy_content_failures(forms, values_by_source)
    failures.extend(content_failures)

    if failures:
        print("Policy content risk check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        "PASS: policy content risk scan matches Play form claims "
        f"({len(RISK_CATEGORIES)} categories, {scanned_values} text values scanned)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
