# Store Asset Pixel Audit

## Status

`LOCAL_PROVEN`.

## Purpose

This audit documents the local pixel-level gate for Google Play store assets. It complements the screenshot manifest, Play Store icon check and feature graphic notes by verifying that PNG files are parseable, correctly sized, nonblank and distinct.

## Automated Gate

`scripts/check_store_asset_pixels.py` validates:

- exactly six Play Store screenshots in `screenshots/play-store`;
- screenshot dimensions `1080x2400`;
- screenshot PNG format: 8-bit RGBA, non-interlaced;
- screenshot sampled alpha is fully opaque;
- each screenshot has enough sampled colors and luminance range to reject blank frames;
- screenshot pixel digests are unique and average-hash distance is not near-duplicate;
- feature graphic candidate dimensions `1024x500`;
- feature graphic PNG format: 8-bit RGB, non-interlaced, no alpha;
- Play Store icon dimensions `512x512` and 8-bit RGBA format.

`scripts/check_store_asset_pixels_selftest.py` covers synthetic PNG positive and negative paths for parsing outside the repo, transparency, wrong dimensions, flat images and average-hash duplicate detection.

Current local result:

```text
PASS: store asset pixels validated (6 screenshots 1080x2400, feature graphic 1024x500, icon 512x512)
```

The current Onboarding screenshot was refreshed after the unframed `Первые 5 минут` flow-summary polish. The current Home screenshot was refreshed after replacing the collapsed `Настроить подбор` raised card with an unframed divider-row summary on Android 16. The current Result screenshot was refreshed after adding decorative `HomeIcon` / `StatsIcon` cues to the peer actions on Android 16. The current Timer screenshot was refreshed after adding decorative icons to `Пауза`/`Продолжить` and `Сброс` on Android 16. The current Progress screenshot was refreshed after the unframed `ProgressRhythmSummary` polish on Android 16. The current Settings screenshot was refreshed after replacing the paragraph-heavy `О приложении` block with compact `Версия` / `Каталог` / `Данные` facts on Android 16, then refreshed again after widening `Данные` and spacing the reset section so the first viewport ends cleanly. The current Play Store icon was refreshed from ImageGen source 04 and regenerated as a friendlier five-tile checklist/home composition without the previous harsh task-dot look. These assets remain covered by the same opacity, nonblank, dimension and uniqueness gates where applicable.

## Covered Assets

| Asset | Path | Pixel Gate |
|---|---|---|
| Onboarding screenshot | `screenshots/play-store/01-onboarding.png` | 1080x2400, opaque, nonblank, unique |
| Home screenshot | `screenshots/play-store/02-home.png` | 1080x2400, opaque, nonblank, unique |
| Timer screenshot | `screenshots/play-store/03-timer.png` | 1080x2400, opaque, nonblank, unique |
| Result screenshot | `screenshots/play-store/04-result.png` | 1080x2400, opaque, nonblank, unique |
| Progress screenshot | `screenshots/play-store/05-progress.png` | 1080x2400, opaque, nonblank, unique |
| Settings screenshot | `screenshots/play-store/06-settings.png` | 1080x2400, opaque, nonblank, unique |
| Feature graphic candidate | `store-assets/feature-graphic/feature-graphic-candidate-03.png` | 1024x500, RGB, nonblank |
| Play Store icon | `store-assets/app-icon/play-store-icon-512.png` | 512x512, RGBA, nonblank |

## Release Impact

This gate improves the local RC evidence for store assets. It does not turn the feature graphic candidate into a production-approved final creative; Play Console preview approval remains an external requirement.
