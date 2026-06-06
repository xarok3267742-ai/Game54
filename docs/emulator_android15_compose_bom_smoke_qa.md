# Android 15 Compose BOM Smoke QA

## Scope

- Device: Android 15/API 35 emulator, serial `emulator-5554`.
- Build: debug APK from the current Compose BOM 2026.04.01 stack.
- Package: `ru.poryadok5.app`.
- Evidence directory: `qa/emulator-android15-compose-bom-smoke`.

This pass rechecked the core app flow after the Compose BOM stack update: onboarding, home, timer start, pause/resume, completion/result and persistence after relaunch.

## Result

QA status: `PASSED_WITH_AVD_CAVEAT`.

The app flow passed. The only caveat was unrelated emulator state: two pre-existing test packages on the same AVD briefly took focus during capture. They were removed from emulator state before final relaunch evidence was captured:

- `com.andrejivliev.fiftyfive`
- `com.betguidepoland.app`

The final package list evidence contains only `ru.poryadok5.app`.

## Flow Evidence

| Step | Evidence | Result |
|---|---|---|
| First launch onboarding | `01-onboarding-summary.txt`, `01-onboarding.png` | Russian onboarding visible; primary action `Начать` reachable. |
| Home after onboarding | `02-home-summary.txt`, `02-home.png` | Home filters, progress counters and `Запустить таймер` visible. |
| Timer start | `03-after-launch-summary.txt`, `03-after-launch.png` | Task `Протереть зеркало` started; timer showed `4:58`; controls `Пауза`, `Сброс`, `Готово` visible. |
| Pause | `04-paused-summary.txt`, `04-paused.png` | Timer paused at `4:30`; button changed to `Продолжить`. |
| Resume | `05-resumed.xml`, `05-resumed.png` | Timer screen remained usable after resume. |
| Completion/result | `10-result-summary.txt`, `10-result.png` | Result screen showed `Готово`, `1` completed task, `1 дн.` streak and `1%` catalog progress. |
| Final clean relaunch | `12-final-clean-summary.txt`, `12-final-clean.png` | Home relaunched cleanly after removing unrelated packages; persisted progress stayed at `1`, `1 дн.`, `1%`. |
| Final no-crash relaunch | `13-final-no-crash-relaunch.png` | Final relaunch screenshot captured after clearing crash logs. |

## Logs

- `app-pid-error-matches.txt`: 0 app-specific error matches.
- `final-app-pid-error-matches.txt`: 0 app-specific error matches after AVD cleanup.
- `clean-crash-buffer-after-cleanup.txt`: 0 crash-buffer lines after clearing logs and relaunching the app.
- Earlier `crash-buffer.txt` contains a `com.android.commands.uiautomator.Launcher` crash caused by repeated UI Automator dumps. That crash belongs to the shell UI automation tool, not to `ru.poryadok5.app`.

## AVD Caveat

During capture, `focus-before-relaunch.txt` recorded `com.andrejivliev.fiftyfive`, and `focus-final.txt` recorded `com.betguidepoland.app`. `focus-after-completion.txt` recorded the correct app focus for the valid result evidence. After cleanup, `packages-after-cleanup.txt` contained only `package:ru.poryadok5.app`, and `12-final-clean-summary.txt` showed the correct Poryadok home UI.

## Release Impact

This QA pass supports the RC claim that the app still works on Android 15 after the Compose BOM update. It does not remove the external Play upload blockers: signing environment variables, public privacy policy URL, real developer support email, Play Console form confirmations and final feature graphic approval.
