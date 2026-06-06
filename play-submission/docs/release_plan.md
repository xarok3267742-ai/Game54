# Release Plan

## RC Target

`1.0.0-rc1`, `versionCode=1`, `applicationId=ru.poryadok5.app`.

## Что должно быть готово

- Рабочий Android app bundle.
- Debug APK для проверки на эмуляторе.
- Каталог задач и unit tests.
- Документация по Google Play, privacy, QA, performance, accessibility и ассетам.
- Реальные screenshots из приложения перед публикацией: RC set captured in `screenshots/play-store`.
- Feature graphic candidate: `store-assets/feature-graphic/feature-graphic-candidate-03.png`.
- Локальный verifier script: `scripts/verify_release_candidate.sh`.
- Локальный Play submission packet: `play-submission`, создаётся через `scripts/build_play_submission_packet.sh`.

## Перед Play Console

1. Создать upload keystore вне репозитория.
2. Настроить signing config через `PORYADOK5_*` Gradle properties или CI secrets.
3. Собрать signed `.aab`.
4. Проверить `./gradlew :app:printReleaseSigningStatus`.
5. Добавить в Play Console screenshots from `screenshots/play-store`; recapture from signed release only if UI changes.
6. Опубликовать `docs/privacy_policy_ru.html` на стабильном публичном HTTPS URL после замены контактной строки на реальный email разработчика. Markdown source: `docs/privacy_policy_draft_ru.md`.
7. Заполнить Data Safety: no data collected/shared.
8. Проверить app content, target audience и age rating.
9. Перед загрузкой прогнать `scripts/verify_release_candidate.sh`; it runs a clean Gradle build and refreshes `play-submission`.
10. Optional: вручную пересобрать local submission packet with `scripts/build_play_submission_packet.sh` after any docs/assets-only change.
11. После настройки signing inputs, privacy URL и ручных Play Console confirmations прогнать `scripts/check_play_upload_external_inputs.py`, затем `scripts/check_play_upload_readiness.py --require-upload-ready`; final handoff runs both gates automatically.
12. После любых UI/navigation changes повторить at least Android 15 or Android 16 smoke evidence before production rollout.
13. Если меняется layout, повторить compact-screen evidence before production rollout.
14. Если меняются width constraints или tablet behavior, повторить large-screen evidence before production rollout.
15. Если меняются typography, spacing или button/chip layout, повторить large-font evidence before production rollout.

## Rollout

Сначала internal testing track, затем closed testing, затем production rollout после ручной проверки store listing.
