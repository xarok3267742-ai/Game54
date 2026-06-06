# Dependency Privacy Audit

## Purpose

Verify that the release runtime dependency graph stays aligned with the Google Play Data Safety declaration: no ads, analytics, crash reporting, attribution, push marketing or tracking SDKs.

## Automated Gate

`scripts/check_dependency_privacy.py` runs:

```bash
./gradlew :app:dependencies --configuration releaseRuntimeClasspath --console=plain
```

The script saves the raw evidence to:

`build/reports/dependency-privacy/releaseRuntimeClasspath.txt`

It scans both the release runtime dependency report and `app/build.gradle.kts` for SDK markers from these categories:

| Category | Examples |
|---|---|
| Ads | Google Mobile Ads, AdMob, AppLovin, ironSource, Unity Ads |
| Analytics or measurement | Firebase Analytics, Google Analytics, Play Services Measurement |
| Crash reporting | Crashlytics, Sentry, Bugsnag, Datadog |
| Attribution or tracking | Adjust, AppsFlyer, Facebook SDK, Flurry, AppMetrica, MyTracker, Amplitude, Mixpanel, OneSignal |
| Firebase platform | Firebase BOM, Firebase common, Firebase messaging/installations |

Any match fails `scripts/verify_release_candidate.sh`.

## Current Evidence

Latest release runtime classpath contains only expected local/offline app dependencies:

- Kotlin stdlib and Kotlinx coroutines/serialization.
- AndroidX Activity, Core, Lifecycle, SavedState, Startup, ProfileInstaller, DataStore and annotations.
- Jetpack Compose runtime, UI, Foundation, Animation and Material 3.
- Okio, Guava `listenablefuture`, JetBrains annotations and JSpecify transitive support libraries.

No ads, analytics, crash-reporting, attribution, push marketing or tracking SDK marker was found.

## Notes

- `androidx.profileinstaller` and `androidx.tracing` are AndroidX performance/runtime support libraries; they are not telemetry SDKs and do not collect app analytics.
- This audit complements manifest and built-artifact permission checks. The app still has no `android.permission.INTERNET` declaration.
