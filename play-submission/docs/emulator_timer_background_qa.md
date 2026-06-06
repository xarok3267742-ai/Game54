# Emulator QA: Timer Background/Resume

## Scope

Validate the Android timer flow after moving the timer implementation to wall-clock time.

## Environment

- Device serial: `emulator-5554`.
- Android: 15, API 35.
- Model: Android SDK built for arm64.
- App package: `ru.poryadok5.app`.
- Build: debug APK installed with `./gradlew :app:installDebug --console=plain`.
- App data: cleared before the run with `adb shell pm clear ru.poryadok5.app`.
- Unrelated old test packages were removed from the emulator before QA to avoid focus hijacking.

## Evidence Directory

`qa/emulator-android15-timer-background`

Key files:

- `01-onboarding.xml`
- `02-home.xml`, `02-home.png`
- `03-timer-start.xml`, `03-timer-start.png`
- `04-timer-after-background.xml`, `04-timer-after-background.png`
- `05-timer-paused.xml`
- `06-timer-paused-after-wait.xml`, `06-timer-paused-after-wait.png`
- `07-timer-resumed.xml`, `07-timer-resumed.png`
- `08-result.xml`, `08-result.png`
- `crash-logcat.txt`
- `timer-background-evidence.txt`

## Flow Result

| Step | Evidence | Result |
|---|---|---|
| Fresh launch | `01-onboarding.xml` | Onboarding rendered in Russian. |
| Enter app | `02-home.xml` | Home rendered; selected 3-minute timer target. |
| Start timer | `03-timer-start.xml` | Timer screen rendered for task `Сложить плед`; visible time `2:58`. |
| Background/resume | `04-timer-after-background.xml` | App returned to timer screen; visible time `2:28`, proving the timer did not freeze while backgrounded. |
| Pause | `05-timer-paused.xml` | Pause state showed `Продолжить`; visible time `2:09`. |
| Wait while paused | `06-timer-paused-after-wait.xml` | After waiting, visible time stayed `2:09`. |
| Resume | `07-timer-resumed.xml` | After resume and short wait, visible time decreased to `2:05`; button returned to `Пауза`. |
| Complete task | `08-result.xml` | Result screen rendered with `1` completed task, `1 дн.` streak and `1%` catalog progress. |
| Crash buffer | `crash-logcat.txt` | 0 crash log lines. |

Background timing recorded in `timer-background-evidence.txt`:

- `background_start_utc=2026-05-27T11:07:59Z`
- `foreground_return_utc=2026-05-27T11:08:07Z`

## Verdict

Passed for Android 15 debug smoke QA. The timer catches up after background/resume, pause holds time stable, resume continues countdown, completion records progress, and no crash entries were recorded.
