# Policy Content Risk Audit

## Scope

This audit supports the current Play Console Target Audience and Content Rating answers for `Порядок 5`. It does not replace the manual Play Console questionnaire.

Sources scanned:

- `app/src/main/res/raw/tasks_ru.json`
- `docs/store_listing_ru.md`
- `docs/play_console_forms_answers.json`

## Automated Gate

`scripts/check_policy_content_risk.py` verifies:

- target audience remains `13+`;
- child-directed, children-primary-appeal, ads, purchases and user-generated-content answers remain false;
- content rating answers for violence, fear/horror, sexual content, controlled substances, gambling, online interaction, location sharing, purchases and ads remain false;
- sensitive categories remain empty;
- task text and store listing do not contain terms that would contradict the current low-risk declarations;
- store listing keeps explicit no-account, no-internet, no-ads, no-analytics and no-personal-data claims.

`scripts/check_policy_content_risk_selftest.py` covers positive and negative paths for risky terms in task text and store listing, sensitive categories, child-directed appeal, missing low-risk claims and Play form mismatches.

## Current Evidence

- App category: productivity/lifestyle utility.
- User-generated content: absent.
- Online interaction: absent.
- Ads and purchases: absent.
- Sensitive categories: absent.
- Target audience declaration: `13+`, not children-directed.

## Manual Boundary

Status: `LOCAL_PROVEN_FOR_CONTENT_SCAN`, `EXTERNAL_REQUIRED_FOR_PLAY_FORM_SUBMISSION`.

The script proves local text/content consistency. Final Data Safety, Target Audience and Content Rating confirmation still must be completed inside Play Console before upload readiness can be claimed.
