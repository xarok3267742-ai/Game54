# Android Backup Policy Audit

## Purpose

`Порядок 5` stores onboarding, settings and progress only on the device. The app should not opt into Android app-data backup or data extraction for those local values.

## Automated Gate

`scripts/check_android_backup_policy.py` verifies:

- source manifest `app/src/main/AndroidManifest.xml` sets `android:allowBackup="false"`;
- built debug APK manifest keeps `android:allowBackup=false`;
- release AAB base manifest keeps `android:allowBackup=false`;
- source and built manifests do not define `android:backupAgent`, `android:fullBackupContent` or `android:dataExtractionRules`.

## Current Result

Current status: `LOCAL_PROVEN`.

The app stores progress locally through DataStore and has Android backup disabled in source and built artifacts. This supports the current privacy posture that local progress does not leave the device through app-managed or manifest-enabled backup behavior.
