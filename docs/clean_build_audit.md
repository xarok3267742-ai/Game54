# Clean Build Audit

## Purpose

The original RC test plan requires a clean Gradle build, not only incremental checks.
`scripts/verify_release_candidate.sh` now starts its Gradle gate with `clean` and then rebuilds tests, lint, debug APK and release AAB from scratch.

## Automated Gate

The verifier runs:

```bash
./gradlew clean :app:printReleaseSigningStatus test lint assembleDebug bundleRelease --console=plain
```

After the clean build finishes, the verifier refreshes `play-submission` through `scripts/build_play_submission_packet.sh`.
This keeps packet checksums and artifact status synchronized with the current build output.

## Current Result

Current clean Gradle RC verification passes in this environment.
The release AAB remains unsigned until `PORYADOK5_*` signing inputs are provided.
