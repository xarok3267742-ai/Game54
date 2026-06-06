#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import check_policy_content_risk as checker

VALID_FORMS = {
    "targetAudienceAndContent": {
        "targetAgeGroups": ["13+"],
        "designedForChildren": False,
        "appealsPrimarilyToChildren": False,
        "childrenDirected": False,
        "userGeneratedContent": False,
        "purchases": False,
        "ads": False,
        "sensitiveCategories": [],
    },
    "contentRating": {
        "violence": False,
        "fearHorror": False,
        "sexualContent": False,
        "controlledSubstances": False,
        "gambling": False,
        "userGeneratedContent": False,
        "onlineInteraction": False,
        "locationSharing": False,
        "purchases": False,
        "ads": False,
    },
}

SAFE_VALUES = {
    "task_text": [
        ("task_text:p5_001:title", "Протрите рабочую поверхность"),
        ("task_text:p5_001:step1", "Соберите лишние бумаги в одну стопку"),
    ],
    "store_listing": [
        (
            "store_listing:line1",
            "Порядок 5 работает без аккаунта, не требует интернета, "
            "не показывает рекламу, не использует аналитику и не собирает персональные данные.",
        ),
    ],
}


class PolicyContentRiskSelfTest(unittest.TestCase):
    def failures_for(
        self,
        values_by_source: dict[str, list[tuple[str, str]]] | None = None,
        forms: object | None = None,
    ) -> list[str]:
        failures, scanned_values = checker.policy_content_failures(
            copy.deepcopy(VALID_FORMS) if forms is None else forms,
            copy.deepcopy(SAFE_VALUES) if values_by_source is None else values_by_source,
        )
        self.assertGreaterEqual(scanned_values, 0)
        return failures

    def assertFailureContains(self, needle: str, values_by_source: dict[str, list[tuple[str, str]]] | None = None, forms: object | None = None) -> None:
        failures = self.failures_for(values_by_source=values_by_source, forms=forms)
        self.assertTrue(
            any(needle in failure for failure in failures),
            msg=f"Expected failure containing {needle!r}; got {failures}",
        )

    def test_safe_values_pass(self) -> None:
        self.assertEqual([], self.failures_for())

    def test_non_object_forms_fail(self) -> None:
        self.assertFailureContains("JSON object", forms=[])

    def test_violence_term_in_task_text_fails(self) -> None:
        values = copy.deepcopy(SAFE_VALUES)
        values["task_text"].append(("task_text:p5_002:title", "Уберите игрушечное оружие со стола"))

        self.assertFailureContains("violence", values_by_source=values)

    def test_gambling_term_in_store_listing_fails(self) -> None:
        values = copy.deepcopy(SAFE_VALUES)
        values["store_listing"].append(("store_listing:line2", "Без аккаунта и рекламы, но есть азартные задания."))

        self.assertFailureContains("gambling", values_by_source=values)

    def test_medical_sensitive_term_fails(self) -> None:
        values = copy.deepcopy(SAFE_VALUES)
        values["task_text"].append(("task_text:p5_003:step1", "Проверьте лекарства и медицинские записи"))

        self.assertFailureContains("medicalAdvice", values_by_source=values)

    def test_children_directed_store_term_fails(self) -> None:
        values = copy.deepcopy(SAFE_VALUES)
        values["store_listing"].append(("store_listing:line2", "Подходит для детей и школьных заданий."))

        self.assertFailureContains("childrenDirectedAppeal", values_by_source=values)

    def test_missing_low_risk_claim_fails(self) -> None:
        values = copy.deepcopy(SAFE_VALUES)
        values["store_listing"] = [("store_listing:line1", "Порядок 5 помогает быстро навести порядок.")]

        self.assertFailureContains("не показывает рекламу", values_by_source=values)

    def test_positive_form_claim_fails_even_without_text_match(self) -> None:
        forms = copy.deepcopy(VALID_FORMS)
        forms["contentRating"]["onlineInteraction"] = True

        self.assertFailureContains("contentRating.onlineInteraction", forms=forms)


if __name__ == "__main__":
    unittest.main(verbosity=2)
