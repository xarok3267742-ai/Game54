# Tech Stack

## Android

- Application id: `ru.poryadok5.app`
- minSdk: 26
- compileSdk: 35
- targetSdk: 35
- versionCode: 1
- versionName: `1.0.0-rc1`

## Language And UI

- Kotlin 2.0.21
- Jetpack Compose
- Material 3
- Compose BOM 2026.04.01
- Gradle Kotlin DSL
- Android Gradle Plugin 8.9.1

## Local Storage

- DataStore Preferences for onboarding, preferred area, haptics setting and progress.
- `app/src/main/res/raw/tasks_ru.json` for the offline task catalog.

## Release Tooling

- `./gradlew test`
- `./gradlew lint`
- `./gradlew assembleDebug`
- `./gradlew bundleRelease`
- `scripts/verify_release_candidate.sh`
- `scripts/check_stack_versions.py`

## Automated Gate

`scripts/check_stack_versions.py` verifies Gradle wrapper, AGP, Kotlin, Compose BOM, DataStore, SDK levels, package id and release version against the RC plan.

## Release Policy

The app has no backend, accounts, ads, analytics, IAP or runtime permissions in v1.
Upload signing is configured only through `PORYADOK5_*` inputs and no keystore is stored in the repository.

Detailed rationale remains in `docs/tech_stack_decision.md`.
