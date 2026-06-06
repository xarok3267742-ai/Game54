# APK Metadata Audit

## Purpose

Verify that the artifact installed for local QA exposes the release-candidate Android metadata expected by Google Play preparation.

## Automated Gate

`scripts/check_apk_metadata.py` runs `aapt dump badging` against:

`app/build/outputs/apk/debug/app-debug.apk`

Package and version expectations are read from `app/build.gradle.kts` through `scripts/release_identity.py`; the stack-version gate separately proves those Gradle values match the RC plan.

The gate checks:

| Field | Expected |
|---|---|
| Package name | `ru.poryadok5.app` |
| Version code | `1` |
| Version name | `1.0.0-rc1` |
| Compile SDK | `35` |
| Min SDK | `26` |
| Target SDK | `35` |
| Application label | `Порядок 5` |

## Current Evidence

Latest local `aapt dump badging` output starts with:

```text
package: name='ru.poryadok5.app' versionCode='1' versionName='1.0.0-rc1' platformBuildVersionName='15' platformBuildVersionCode='35' compileSdkVersion='35' compileSdkVersionCodename='15'
sdkVersion:'26'
targetSdkVersion:'35'
application-label:'Порядок 5'
```

## Notes

- This audit checks the debug APK used for emulator QA.
- The release AAB has its own metadata audit in `docs/aab_metadata_audit.md`.
- Upload readiness still depends on release signing through `PORYADOK5_*` inputs.
