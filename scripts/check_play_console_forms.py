#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / "docs" / "play_console_forms_answers.json"
PRIVACY_HTML = ROOT / "docs" / "privacy_policy_ru.html"
STORE_LISTING = ROOT / "docs" / "store_listing_ru.md"

APP_ACCESS_FALSE_KEYS = (
    "restrictedFunctions",
    "loginRequired",
    "accountRequired",
)
TARGET_FALSE_KEYS = (
    "designedForChildren",
    "appealsPrimarilyToChildren",
    "childrenDirected",
    "userGeneratedContent",
    "purchases",
    "ads",
)
CONTENT_RATING_FALSE_KEYS = (
    "violence",
    "fearHorror",
    "sexualContent",
    "controlledSubstances",
    "gambling",
    "userGeneratedContent",
    "onlineInteraction",
    "locationSharing",
    "purchases",
    "ads",
)
REQUIRED_SOURCES = {
    "https://support.google.com/googleplay/android-developer/answer/10787469",
    "https://support.google.com/googleplay/android-developer/answer/9867159",
    "https://support.google.com/googleplay/android-developer/answer/9898843",
}


def expected_package_name(release_identity: dict[str, object] | None = None) -> str:
    identity = release_identity or read_gradle_release_identity()
    return str(identity["appId"])


def forms_failures(
    data: object,
    *,
    privacy_html_exists: bool,
    store_listing_text: str | None,
    release_identity: dict[str, object] | None = None,
) -> list[str]:
    failures: list[str] = []

    if not isinstance(data, dict):
        return ["Play Console forms answers must be a JSON object"]

    expected_package = expected_package_name(release_identity)
    if data.get("packageName") != expected_package:
        failures.append(f"packageName must be {expected_package}")
    if data.get("appCategory") != "app":
        failures.append("appCategory must be app")
    if data.get("freeOrPaid") != "free":
        failures.append("freeOrPaid must be free for v1")

    app_access = data.get("appAccess", {})
    if not isinstance(app_access, dict):
        failures.append("appAccess must be an object")
        app_access = {}
    for key in APP_ACCESS_FALSE_KEYS:
        if app_access.get(key) is not False:
            failures.append(f"appAccess.{key} must be false")

    ads = data.get("ads", {})
    if not isinstance(ads, dict):
        failures.append("ads must be an object")
        ads = {}
    if ads.get("containsAds") is not False:
        failures.append("ads.containsAds must be false")
    if ads.get("adSdks") != []:
        failures.append("ads.adSdks must be empty")

    data_safety = data.get("dataSafety", {})
    if not isinstance(data_safety, dict):
        failures.append("dataSafety must be an object")
        data_safety = {}
    if data_safety.get("collectsUserData") is not False:
        failures.append("dataSafety.collectsUserData must be false")
    if data_safety.get("sharesUserData") is not False:
        failures.append("dataSafety.sharesUserData must be false")
    if data_safety.get("privacyPolicyRequired") is not True:
        failures.append("dataSafety.privacyPolicyRequired must be true")
    if data_safety.get("privacyPolicySource") != "docs/privacy_policy_ru.html":
        failures.append("dataSafety.privacyPolicySource must point to docs/privacy_policy_ru.html")
    if len(data_safety.get("localOnlyData", [])) < 5:
        failures.append("dataSafety.localOnlyData should enumerate local-only settings/progress values")
    if not privacy_html_exists:
        failures.append("privacy policy HTML source is missing")

    target = data.get("targetAudienceAndContent", {})
    if not isinstance(target, dict):
        failures.append("targetAudienceAndContent must be an object")
        target = {}
    if target.get("targetAgeGroups") != ["13+"]:
        failures.append("targetAudienceAndContent.targetAgeGroups must be ['13+']")
    for key in TARGET_FALSE_KEYS:
        if target.get(key) is not False:
            failures.append(f"targetAudienceAndContent.{key} must be false")
    if target.get("sensitiveCategories") != []:
        failures.append("targetAudienceAndContent.sensitiveCategories must be empty")

    rating = data.get("contentRating", {})
    if not isinstance(rating, dict):
        failures.append("contentRating must be an object")
        rating = {}
    for key in CONTENT_RATING_FALSE_KEYS:
        if rating.get(key) is not False:
            failures.append(f"contentRating.{key} must be false")

    sources = data.get("officialSources", [])
    if not isinstance(sources, list) or set(sources) != REQUIRED_SOURCES:
        failures.append("officialSources must include Data Safety, Target Audience and Content Rating help pages")

    if store_listing_text is not None:
        listing = store_listing_text.lower()
        risky_terms = ("реклама", "покупк", "аккаунт", "регистрац")
        if "не показывает рекламу" not in listing:
            failures.append("store listing should explicitly say the app does not show ads")
        if "без аккаунта" not in listing:
            failures.append("store listing should explicitly say no account is required")
        if any(term in listing for term in risky_terms) and "не собирает персональные данные" not in listing:
            failures.append("store listing privacy claims must remain explicit when ads/account terms are present")
    else:
        failures.append("store listing draft is missing")

    return failures


def main() -> int:
    if not FORMS.exists():
        print(f"FAIL: Play Console forms answers are missing: {FORMS}", file=sys.stderr)
        return 1

    try:
        data = json.loads(FORMS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"FAIL: invalid JSON in {FORMS}: {error}", file=sys.stderr)
        return 1

    try:
        release_identity = read_gradle_release_identity()
    except (OSError, ValueError) as exc:
        print(f"FAIL: release identity could not be read from Gradle: {exc}", file=sys.stderr)
        return 1

    store_listing_text = STORE_LISTING.read_text(encoding="utf-8") if STORE_LISTING.exists() else None
    failures = forms_failures(
        data,
        privacy_html_exists=PRIVACY_HTML.exists(),
        store_listing_text=store_listing_text,
        release_identity=release_identity,
    )

    if failures:
        print("Play Console forms check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: Play Console form answers match the current no-data/no-ads/no-account RC model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
