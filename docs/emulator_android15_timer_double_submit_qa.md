# Android 15 Timer Double-Submit QA

## Scope

Validate that the timer completion action records progress once when the user taps “Готово” twice quickly.

## Environment

- Date: 2026-05-27.
- Device: Android 15 AVD, serial `emulator-5554`.
- Viewport: 1080x2400, density 420.
- Package: `ru.poryadok5.app`.
- Build: debug APK installed with `./gradlew :app:installDebug --console=plain`.

## Flow Evidence

Evidence directory: `qa/emulator-android15-timer-double-submit`.

Steps performed:

1. Cleared app data and logcat.
2. Launched `ru.poryadok5.app/.MainActivity`.
3. Completed onboarding.
4. Started the default 5-minute timer.
5. Sent two fast taps to the “Готово” button using coordinates derived from `06-timer-clean-before.xml`.
6. Captured result screen.
7. Opened progress screen.
8. Captured crash buffer, app PID logcat and final focus.

Important evidence files:

- `06-timer-clean-before.xml`: timer screen before double submit.
- `06-timer-double-complete-taps.txt`: two “Готово” tap coordinates.
- `07-result-after-double.xml`: result screen after double submit.
- `08-progress-after-double.xml`: progress screen after double submit.
- `app-pid-error-filtered.txt`: app process fatal/exception/crash filter.
- `crash-buffer.txt`: Android crash buffer.
- `focus-final.txt`: final focused app.

## Result

- Result screen showed `1` total completed task, `1 дн.` streak and `1%` catalog progress.
- Progress screen showed `1` completed task and `1 из 80` unique completed tasks.
- App PID fatal/exception/crash filter contained 0 lines.
- Crash buffer contained 0 lines.
- Final focus remained `ru.poryadok5.app/.MainActivity`.

## AVD Caveat

The first capture attempt briefly focused an unrelated pre-existing package on the emulator. The package was removed from emulator state, app data was cleared, logcat was cleared and the flow was rerun successfully. Evidence is preserved in `focus-hijack-before-cleanup.txt`, `packages-before-cleanup.txt`, `uninstall-betguide.txt` and `uninstall-fiftyfive.txt`.

## Status

`PASSED_WITH_AVD_CAVEAT`.
