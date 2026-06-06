# Privacy And Permissions

## Данные

- Собираются: ничего.
- Передаются: ничего.
- Хранятся локально: onboarding flag, preferred area, haptics flag, total done, streak, last done date, completed task ids.
- Runtime mapping normalizes corrupted negative progress counters, malformed last done dates and blank/whitespace completed-task ids before they reach UI metrics.
- Progress writes also normalize negative counters, malformed last done dates and blank/whitespace completed-task ids before storing DataStore values.
- Preferred area/settings enum raw values are trimmed before fallback, so whitespace-corrupted local settings still restore the intended area when possible.
- Suggestion and progress-count rules normalize completed-task ids again at the engine boundary, so local corrupted ids cannot force immediate task repeats or undercount catalog progress.
- Персональные данные: не запрашиваются.
- Android app-data backup: disabled with `android:allowBackup="false"` and checked in source/built manifests by `scripts/check_android_backup_policy.py`.

## Permissions

Runtime permissions отсутствуют. Source manifest не объявляет internet, location, camera, contacts, microphone, storage или notifications.

Android package dump может показывать внутреннее app-specific разрешение `ru.poryadok5.app.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` с уровнем protection `signature`. Это служебное разрешение AndroidX для receiver isolation; оно не является dangerous/runtime permission, не запрашивается у пользователя и не даёт доступ к персональным данным или устройственным сенсорам.

Фактический APK gate: `scripts/check_apk_permissions.py` запускает `aapt dump permissions` на `app/build/outputs/apk/debug/app-debug.apk` и допускает только app-specific signature permission, вычисленный из Gradle `applicationId`. Любой `android.permission.*` или чужой permission должен провалить RC verification.

Manifest exposure gate: `scripts/check_manifest_component_exposure.py` проверяет source manifest и release AAB manifest. В release-сборке разрешены только exported launcher `MainActivity` для Gradle `applicationId`, non-exported `androidx.startup.InitializationProvider` и protected AndroidX profile receiver с `android.permission.DUMP`; лишние activity/service/provider/receiver, `android:debuggable=true`, `android:usesCleartextTraffic=true`, `android:networkSecurityConfig` и legacy external storage flags проваливают RC verification.

## SDKs

- Analytics: нет.
- Crash logs: нет.
- Ads: нет.
- Payments/IAP: нет.
- Device identifiers: не используются.
- User-generated content: нет.

Фактический dependency gate: `scripts/check_dependency_privacy.py` проверяет `releaseRuntimeClasspath` и прямые Gradle-зависимости на маркеры ads, analytics, crash-reporting, attribution, push marketing и tracking SDK. Evidence описан в `docs/dependency_privacy_audit.md`.

## Google Play Data Safety

Рекомендуемая декларация: app does not collect or share user data. Локальный прогресс не покидает устройство.

No-internet emulator QA passed with `Active default network: none`; see `docs/emulator_no_internet_qa.md`.

Android backup policy audit passed; see `docs/android_backup_policy_audit.md`.

## Privacy Policy Notes

Privacy policy draft prepared in `docs/privacy_policy_draft_ru.md`.
Self-contained static HTML version prepared in `docs/privacy_policy_ru.html` for hosting at a public HTTPS URL.
Перед публикацией нужно заменить контактный email на реальный адрес разработчика и указать опубликованный URL в Play Console.
