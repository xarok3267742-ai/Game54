#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

import check_play_console_forms as checker

DEFAULT_IDENTITY = {"appId": "ru.poryadok5.app", "versionCode": 1, "versionName": "1.0.0-rc1"}
CUSTOM_IDENTITY = {"appId": "com.example.custom", "versionCode": 7, "versionName": "2.3.0"}

VALID_FORMS = {
    "packageName": "ru.poryadok5.app",
    "appCategory": "app",
    "freeOrPaid": "free",
    "appAccess": {
        "restrictedFunctions": False,
        "loginRequired": False,
        "accountRequired": False,
    },
    "ads": {
        "containsAds": False,
        "adSdks": [],
    },
    "dataSafety": {
        "collectsUserData": False,
        "sharesUserData": False,
        "privacyPolicyRequired": True,
        "privacyPolicySource": "docs/privacy_policy_ru.html",
        "localOnlyData": [
            "onboarding completion flag",
            "preferred area",
            "haptics setting",
            "total completed task count",
            "streak days",
        ],
    },
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
    "officialSources": sorted(checker.REQUIRED_SOURCES),
}

VALID_LISTING = (
    "Порядок 5 работает без аккаунта, не показывает рекламу "
    "и не собирает персональные данные."
)


class PlayConsoleFormsSelfTest(unittest.TestCase):
    def failures_for(
        self,
        forms: object,
        listing: str | None = VALID_LISTING,
        release_identity: dict[str, object] = DEFAULT_IDENTITY,
    ) -> list[str]:
        return checker.forms_failures(
            forms,
            privacy_html_exists=True,
            store_listing_text=listing,
            release_identity=release_identity,
        )

    def assertFailureContains(
        self,
        forms: object,
        needle: str,
        listing: str | None = VALID_LISTING,
        release_identity: dict[str, object] = DEFAULT_IDENTITY,
    ) -> None:
        failures = self.failures_for(forms, listing, release_identity)
        self.assertTrue(
            any(needle in failure for failure in failures),
            msg=f"Expected failure containing {needle!r}; got {failures}",
        )

    def test_valid_forms_pass(self) -> None:
        self.assertEqual([], self.failures_for(copy.deepcopy(VALID_FORMS)))

    def test_package_name_uses_gradle_release_identity(self) -> None:
        forms = copy.deepcopy(VALID_FORMS)
        forms["packageName"] = "com.example.custom"

        self.assertEqual([], self.failures_for(forms, release_identity=CUSTOM_IDENTITY))
        self.assertFailureContains(copy.deepcopy(VALID_FORMS), "packageName must be com.example.custom", release_identity=CUSTOM_IDENTITY)

    def test_non_object_fails(self) -> None:
        self.assertFailureContains([], "JSON object")

    def test_ads_claim_fails(self) -> None:
        forms = copy.deepcopy(VALID_FORMS)
        forms["ads"]["containsAds"] = True

        self.assertFailureContains(forms, "ads.containsAds")

    def test_data_collection_claim_fails(self) -> None:
        forms = copy.deepcopy(VALID_FORMS)
        forms["dataSafety"]["collectsUserData"] = True

        self.assertFailureContains(forms, "dataSafety.collectsUserData")

    def test_children_directed_claim_fails(self) -> None:
        forms = copy.deepcopy(VALID_FORMS)
        forms["targetAudienceAndContent"]["childrenDirected"] = True

        self.assertFailureContains(forms, "childrenDirected")

    def test_content_rating_online_interaction_fails(self) -> None:
        forms = copy.deepcopy(VALID_FORMS)
        forms["contentRating"]["onlineInteraction"] = True

        self.assertFailureContains(forms, "onlineInteraction")

    def test_missing_official_source_fails(self) -> None:
        forms = copy.deepcopy(VALID_FORMS)
        forms["officialSources"] = list(sorted(checker.REQUIRED_SOURCES))[:-1]

        self.assertFailureContains(forms, "officialSources")

    def test_store_listing_without_no_ads_claim_fails(self) -> None:
        self.assertFailureContains(copy.deepcopy(VALID_FORMS), "does not show ads", listing="Порядок 5 работает без аккаунта.")

    def test_missing_privacy_policy_source_fails(self) -> None:
        failures = checker.forms_failures(
            copy.deepcopy(VALID_FORMS),
            privacy_html_exists=False,
            store_listing_text=VALID_LISTING,
            release_identity=DEFAULT_IDENTITY,
        )

        self.assertTrue(
            any("privacy policy HTML source is missing" in failure for failure in failures),
            msg=failures,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
