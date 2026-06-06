# AAB Universal APK Audit

## Purpose

This audit verifies that the release Android App Bundle can be converted by `bundletool` into a universal APK and that the bundle-derived APK keeps the expected Play release metadata.

## Automated Gate

`scripts/check_aab_universal_apk.py` runs:

- `bundletool build-apks --mode=universal` against `app/build/outputs/bundle/release/app-release.aab`;
- `aapt dump badging` against the extracted temporary `universal.apk`;
- package, version, compile SDK, min SDK, target SDK, app label and permission checks.

Package and version expectations are read from `app/build.gradle.kts` through `scripts/release_identity.py`; the stack-version gate separately proves those Gradle values match the RC plan.

Expected values:

- package: `ru.poryadok5.app`;
- versionCode: `1`;
- versionName: `1.0.0-rc1`;
- compileSdk: `35`;
- minSdk: `26`;
- targetSdk: `35`;
- app label: `Порядок 5`;
- permissions: only the allowed app-specific AndroidX receiver permission.

## Current Result

Current status: `LOCAL_PROVEN`.

The checker creates only temporary files outside the project workspace and removes them before exiting. It does not replace Play Console internal testing, but it proves that the local release AAB can be expanded into an APK set with the expected app identity.
