# Play Console Submission Map

This file maps the current `Порядок 5` RC state to Play Console fields. It does not replace Play Console review, legal review or a public privacy policy URL.

Structured form answers are prepared in `docs/play_console_forms_answers.json` and checked by `scripts/check_play_console_forms.py`, including `packageName` synchronization with Gradle `applicationId`. Checker positive and negative paths are covered by `scripts/check_play_console_forms_selftest.py`.
Local content-risk consistency for Target Audience and Content Rating is checked by `scripts/check_policy_content_risk.py`; its positive and negative paths are covered by `scripts/check_policy_content_risk_selftest.py`. Evidence is in `docs/policy_content_risk_audit.md`.

Policy sources checked on 27 May 2026:

- Target API requirement: https://developer.android.com/google/play/requirements/target-sdk
- Android App Bundle publishing format: https://developer.android.com/guide/app-bundle
- Data Safety form guidance: https://support.google.com/googleplay/android-developer/answer/10787469
- Target audience and content: https://support.google.com/googleplay/android-developer/answer/9867159
- Preview assets and feature graphic: https://support.google.com/googleplay/android-developer/answer/9866151

## Create App

| Field | Value |
|---|---|
| App name | Порядок 5 |
| Default language | Russian |
| App or game | App |
| Free or paid | Free for v1 |
| Declarations | Accept Developer Program Policies, US export laws and Play App Signing terms in Play Console |
| Contact email | Use the real developer support email before publishing |

## Store Listing

Use `docs/store_listing_ru.md`.

| Field | Source |
|---|---|
| App name | `docs/store_listing_ru.md` |
| Short description | `docs/store_listing_ru.md` |
| Full description | `docs/store_listing_ru.md` |
| Release notes | `docs/store_listing_ru.md` |
| Store listing audit | `docs/store_listing_audit.md` |
| App icon | `store-assets/app-icon/play-store-icon-512.png` |
| Screenshots | `screenshots/play-store/*.png` |
| Screenshot index | `docs/screenshot_manifest.md` |
| Feature graphic | Candidate: `store-assets/feature-graphic/feature-graphic-candidate-03.png`; approve in Play Console preview before production |

## App Access

Structured source: `docs/play_console_forms_answers.json`.

| Question | Answer |
|---|---|
| Are all or some functions restricted? | No |
| Login required? | No |
| Account required? | No |
| Instructions for review | Install and open the app. All functionality is available offline without credentials. Settings include privacy and app version/about information. |

Local emulator evidence covers Android 15 timer/background and no-internet flows plus Android 16/API 36 smoke, compact-screen, large-screen and large-font flows; see `docs/qa_test_plan.md`.

## Ads

Structured source: `docs/play_console_forms_answers.json`.

| Question | Answer |
|---|---|
| Does the app contain ads? | No |
| Ad SDKs | None; checked by `scripts/check_dependency_privacy.py` |

## Data Safety

Structured source: `docs/play_console_forms_answers.json`.

Recommended declaration for current v1:

| Section | Answer |
|---|---|
| Data collected | No |
| Data shared | No |
| Security practices | No account, no network data transfer, local-only settings and progress |
| Data deletion | User can reset local progress in app settings or uninstall the app |

Local-only data that stays on device:

- onboarding completion flag;
- preferred area;
- haptics setting;
- total completed task count;
- streak days;
- last completion date;
- completed task ids.

These values are not sent to the developer or third parties.

Dependency privacy audit: `docs/dependency_privacy_audit.md` confirms the release runtime classpath has no ads, analytics, crash-reporting, attribution, push marketing or tracking SDK markers.

## Privacy Policy

Use `docs/privacy_policy_draft_ru.md` as the source text and `docs/privacy_policy_ru.html` as the ready-to-host static HTML page. Before submitting:

- replace the contact line with a real developer support email in the published policy;
- publish the policy at a stable public HTTPS URL;
- put that URL into Play Console.

## Target Audience And Content

Structured source: `docs/play_console_forms_answers.json`.

Recommended current declaration:

| Field | Answer |
|---|---|
| Target age | 13+ |
| Designed for children | No |
| Appeals primarily to children | No |
| User-generated content | No |
| Purchases | No |
| Ads | No |
| Sensitive categories | None: no gambling, finance, medical advice, dating, news or politics |

Reasoning: the app is a household/productivity utility for general users, not a children-directed product.

Local evidence: `docs/policy_content_risk_audit.md` scans task text and store listing for terms that would contradict the current sensitive-category and children-directed answers.

## Content Rating

Structured source: `docs/play_console_forms_answers.json`.

Expected questionnaire answers for current v1:

| Topic | Answer |
|---|---|
| Violence | No |
| Fear/horror | No |
| Sexual content | No |
| Controlled substances | No |
| Gambling | No |
| User-generated content | No |
| Online interaction | No |
| Location sharing | No |
| Purchases | No |
| Ads | No |

Expected rating: broad audience / low maturity, subject to the official questionnaire result.

Local evidence: `scripts/check_policy_content_risk.py` verifies current task text and store listing do not contradict the false answers for violence, fear/horror, sexual content, controlled substances, gambling, user-generated content, online interaction, location sharing, purchases and ads.

## Release Upload

| Field | Value |
|---|---|
| Package name | `ru.poryadok5.app` |
| Version code | `1` |
| Version name | `1.0.0-rc1` |
| Artifact | `app/build/outputs/bundle/release/app-release.aab` |
| Current artifact status | Unsigned unless `PORYADOK5_*` signing inputs are configured |
| Signing setup | `docs/signing_setup.md` |
| Upload preflight | `docs/play_upload_preflight.md` |
| Verification script | `scripts/verify_release_candidate.sh` |

## Internal Testing Track

1. Upload the signed `.aab`.
2. Add screenshots from `screenshots/play-store`.
3. Add `store-assets/feature-graphic/feature-graphic-candidate-03.png` after final visual approval.
4. Add privacy policy URL.
5. Complete Data Safety, Target Audience and Content Rating forms.
6. Create a small tester list.
7. Verify install, first launch, timer completion, settings reset and no-internet behavior from Play-distributed build.
