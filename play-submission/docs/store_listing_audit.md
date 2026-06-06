# Store Listing Audit

## Current Limits

Official Play Console Help sources checked on 27 May 2026:

- App name: 30 characters.
- Short description: 80 characters.
- Full description: 4000 characters.
- Release notes: 500 Unicode characters per language.

Sources:

- https://support.google.com/googleplay/android-developer/answer/9859152
- https://support.google.com/googleplay/android-developer/answer/9859348
- https://support.google.com/googleplay/android-developer/answer/13393723

## Automated Gate

`scripts/check_store_listing.py` verifies:

- required sections exist in `docs/store_listing_ru.md`;
- app name, short description, full description and release notes fit current Play character limits;
- full description does not copy the short description verbatim;
- screenshot caption count matches the real PNG screenshot count in `screenshots/play-store`;
- captions stay compact;
- search keywords are present and unique;
- obvious ranking, award, discount or guarantee claims are absent.

`scripts/check_store_listing_selftest.py` covers positive and negative paths for required sections, Play field limits, short/full description repetition, screenshot caption count, caption length, duplicate keywords, risky promotional claims and missing screenshots.

## Current Result

Current `docs/store_listing_ru.md` passes the automated store listing gate.
