# Stack Version Audit

## Expected RC Stack

| Item | Expected |
|---|---|
| Gradle wrapper | 8.11.1 |
| Android Gradle Plugin | 8.9.1 |
| Kotlin Android plugin | 2.0.21 |
| Kotlin Compose plugin | 2.0.21 |
| Compose BOM | 2026.04.01 |
| DataStore Preferences | 1.1.7 |
| applicationId | `ru.poryadok5.app` |
| minSdk | 26 |
| compileSdk | 35 |
| targetSdk | 35 |
| versionCode | 1 |
| versionName | `1.0.0-rc1` |

## Automated Gate

`scripts/check_stack_versions.py` reads:

- `gradle/wrapper/gradle-wrapper.properties`
- `build.gradle.kts`
- `app/build.gradle.kts`
- `docs/tech_stack.md`
- `docs/tech_stack_decision.md`

The gate fails if the Gradle stack, Android package metadata, SDK levels or release version drift from the RC plan.

## Current Result

Current stack version check passes. The dependency privacy report also confirms `androidx.compose:compose-bom:2026.04.01` resolves to the expected Compose dependency family for release runtime.
