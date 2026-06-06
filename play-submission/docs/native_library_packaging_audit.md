# Native Library Packaging Audit

## Purpose

The app has small transitive AndroidX native libraries. This audit verifies installable APK packaging for those libraries instead of relying only on release AAB structure.

## Automated Gate

`scripts/check_native_library_packaging.py` checks:

- native library entries in `app/build/outputs/apk/debug/app-debug.apk`;
- native library entries in a temporary `universal.apk` generated from `app/build/outputs/bundle/release/app-release.aab` with `bundletool build-apks --mode=universal`;
- all native libraries in those installable APKs are uncompressed;
- both installable APKs pass Android SDK `zipalign -c -P 16 -v 4`.

The checker creates temporary `.apks` and APK files outside the project workspace and removes them before exiting.

## Current Result

Current status: `LOCAL_PROVEN`.

The installable debug APK and the bundle-derived universal APK both contain the expected transitive native libraries as uncompressed entries and pass the 16 KB zip alignment check.
