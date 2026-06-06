# Screenshot Plan

## Goal

Prepare real Google Play screenshots from the actual Android app. Do not use fake UI or manually recreated screens.

## Current RC Capture

Captured screenshots are stored in `screenshots/play-store` and indexed in `docs/screenshot_manifest.md`.

## Required Screens

1. Onboarding: first-run value, starting-area choice, unframed `Первые 5 минут` summary and start action.
2. Home: compact icon header actions, quick task, selection-quality hint, launch action, aligned progress metrics and collapsed filter disclosure summary.
3. Task timer: countdown, steps, pause/reset.
4. Result: completion message, aligned progress metrics and next-task preview.
5. Progress: numeric catalog percent, completed-count copy, per-area bars and rhythm notes.
6. Settings/privacy: offline/no account/no ads/no analytics message.

## Device Targets

- Phone portrait, 1080x2400 or similar.
- Optional second set on a smaller phone if layout is manually checked.

## Capture Commands

```bash
adb -s <serial> shell am start -n ru.poryadok5.app/.MainActivity
adb -s <serial> exec-out screencap -p > screenshots/play-store/02-home.png
```

## Quality Checklist

- Screenshots come from `ru.poryadok5.app`.
- No other app appears in the frame.
- No debug overlay, notification drawer, permission prompt or keyboard.
- Text is readable and not cut off.
- Primary CTA labels are white/`onPrimary` on sage buttons.
- Bottom navigation bar does not cover app actions.
- Store captions are live listing text, not embedded tiny image text.
