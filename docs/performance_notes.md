# Performance Notes

## Expected Profile

- App is Kotlin/Compose only, no backend, no network-loaded images and no runtime bitmap illustration content beyond launcher/store assets.
- Catalog is 80 small JSON records loaded from bundled raw resource.
- DataStore stores small preferences only.

## Checks

- Cold start: expected lightweight; no network or remote initialization.
- Asset size: minimal raster launcher PNG resources plus static store assets; no in-app illustration payload.
- Main thread: JSON load is dispatched through `Dispatchers.IO`.
- Memory: task catalog is small and retained in Compose state.
- FPS: no game loop; animations are small UI transitions and timer progress.
- Dependencies: Compose, DataStore, coroutines, org.json test dependency.
- Native libraries: small transitive AndroidX libraries are packaged by Compose/DataStore; `scripts/check_native_library_packaging.py` verifies debug APK and bundle-derived universal APK native libraries are uncompressed and pass `zipalign -c -P 16 -v 4`.

## Optimization Decisions

- No bitmap illustrations in app runtime beyond generated launcher icon resources.
- No analytics/ad SDKs.
- No image loading libraries.
- No navigation dependency; simple Compose state machine is sufficient.
