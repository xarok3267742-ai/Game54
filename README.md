# Порядок 5

`Порядок 5` — offline-first Android-приложение для коротких микрозадач по дому, рабочему месту, кухне, личным вещам и цифровому порядку. Пользователь выбирает зону, уровень энергии и длительность 3/5/10 минут, запускает таймер и отмечает результат.

## Почему выбрана эта идея

Идея небольшая, понятная русскоязычной casual-аудитории и реалистична для release candidate без backend, аккаунтов, рекламы, аналитики и персональных данных. В отличие от простой игры, продукт не требует большого баланса уровней, сложных ассетов и рискованной монетизации.

## Стек

- Kotlin + Jetpack Compose + Material 3
- Gradle Kotlin DSL, Android Gradle Plugin 8.9.1
- Kotlin 2.0.21, Compose BOM 2026.04.01
- minSdk 26, compileSdk 35, targetSdk 35
- DataStore Preferences для локального прогресса

## Команды

```bash
./gradlew clean
./gradlew test
./gradlew lint
./gradlew assembleDebug
./gradlew bundleRelease
```

Если `ANDROID_HOME` не задан, используйте `local.properties`:

```properties
sdk.dir=/Users/andrejivliev/Library/Android/sdk
```

## Структура

- `app/src/main/java/ru/poryadok5/app/domain` — модели, выбор задач, правила прогресса.
- `app/src/main/java/ru/poryadok5/app/data` — загрузка каталога и DataStore.
- `app/src/main/java/ru/poryadok5/app/ui` — Compose UI, экраны, тема и компоненты.
- `app/src/main/res/raw/tasks_ru.json` — 80 оригинальных русскоязычных задач.
- `docs` — продуктовая, техническая, QA и Google Play документация.

## Google Play

Release bundle собирается командой:

```bash
./gradlew bundleRelease
```

Текущий `app/build/outputs/bundle/release/app-release.aab` собирается как локальный RC artifact. Если `PORYADOK5_*` signing inputs не заданы, он будет unsigned и не Play-upload-ready.

Полный локальный RC gate:

```bash
scripts/verify_release_candidate.sh
```

Release signing описан в [docs/signing_setup.md](</Users/andrejivliev/Desktop/54 Game/docs/signing_setup.md>). Store listing draft, store listing audit, privacy policy draft, ready-to-host privacy policy HTML, Play Console submission map, structured Play Console form answers, documentation inventory, stack version audit, clean build audit, packaged app contents audit, packaged task catalog audit, screenshot plan и screenshot manifest лежат в `docs/store_listing_ru.md`, `docs/store_listing_audit.md`, `docs/privacy_policy_draft_ru.md`, `docs/privacy_policy_ru.html`, `docs/play_console_submission.md`, `docs/play_console_forms_answers.json`, `docs/doc_inventory.md`, `docs/stack_version_audit.md`, `docs/clean_build_audit.md`, `docs/packaged_app_contents_audit.md`, `docs/packaged_task_catalog_audit.md`, `docs/screenshot_plan.md` и `docs/screenshot_manifest.md`. QA evidence включает Android 15, Android 16, compact-screen, large-screen и large-font emulator reports in `docs/qa_test_plan.md`. Play Store app icon находится в `store-assets/app-icon/play-store-icon-512.png`; реальные RC screenshots находятся в `screenshots/play-store`; feature graphic candidate находится в `store-assets/feature-graphic/feature-graphic-candidate-03.png`. Собранный локальный submission packet создаётся в `play-submission` and includes `text/privacy_policy_ru.html`.

Upload preflight для момента после configured signing inputs, public privacy URL и ручных Play Console confirmations:

```bash
scripts/check_play_upload_readiness.py --require-upload-ready
```

Финальный handoff command для подписанного upload packet:

```bash
scripts/prepare_play_upload_candidate.sh
```

## Signed AAB Through GitHub Actions

Workflow `.github/workflows/signed-aab.yml` builds a signed `app-release.aab` from GitHub without committing a keystore. Add these repository secrets before running it:

- `PORYADOK5_KEYSTORE_BASE64` — base64 of the upload `.jks` file.
- `PORYADOK5_KEYSTORE_PASSWORD`
- `PORYADOK5_KEY_ALIAS`
- `PORYADOK5_KEY_PASSWORD`

Optional secrets for a stricter Play handoff packet:

- `PORYADOK5_SUPPORT_EMAIL`
- `PORYADOK5_PRIVACY_POLICY_URL`
- `PORYADOK5_FEATURE_GRAPHIC_APPROVED=yes`
- `PORYADOK5_DATA_SAFETY_CONFIRMED=yes`
- `PORYADOK5_TARGET_AUDIENCE_CONFIRMED=yes`
- `PORYADOK5_CONTENT_RATING_CONFIRMED=yes`
- `PORYADOK5_INTERNAL_TESTING_CONFIRMED=yes`

Run **Actions → Build signed AAB → Run workflow**. The workflow verifies release signing with `jarsigner`, uploads `poryadok5-signed-aab` as an Actions artifact, and can attach the AAB to a GitHub Release when `create_github_release` is enabled.
