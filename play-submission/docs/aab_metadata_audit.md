# AAB Metadata Audit

## Purpose

Verify the release Android App Bundle that will be uploaded to Google Play, not only the debug APK used for emulator QA.

## Automated Gate

`scripts/check_aab_metadata.py` runs `bundletool dump manifest` against:

`app/build/outputs/bundle/release/app-release.aab`

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
| Application label reference | `@string/app_name` |
| Uses-permission entries | Only `ru.poryadok5.app.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` |

## Current Evidence

Latest local `bundletool dump manifest` output starts with:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android" android:compileSdkVersion="35" android:versionCode="1" android:versionName="1.0.0-rc1" package="ru.poryadok5.app" platformBuildVersionCode="35">
  <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="35"/>
  <permission android:name="ru.poryadok5.app.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION" android:protectionLevel="0x00000002"/>
  <uses-permission android:name="ru.poryadok5.app.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"/>
  <application android:label="@string/app_name" ...>
```

## Notes

- This audit checks the release AAB artifact path.
- The current local AAB remains unsigned when `PORYADOK5_*` signing inputs are absent.
- `android.permission.DUMP` appears only as a receiver protection requirement for AndroidX profile installer, not as an app `uses-permission`.
