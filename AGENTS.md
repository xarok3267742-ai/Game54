# AGENTS.md

## Проект

`Порядок 5` — Android-first offline-приложение для коротких задач по наведению порядка. MVP должен оставаться небольшим, стабильным и готовым к Google Play release candidate.

## Стек и команды

- Kotlin, Jetpack Compose, Material 3, Gradle Kotlin DSL.
- Запуск проверок: `./gradlew test`, `./gradlew lint`, `./gradlew assembleDebug`, `./gradlew bundleRelease`.
- Проверка signing режима: `./gradlew :app:printReleaseSigningStatus`.
- Android SDK задаётся через `ANDROID_HOME` или локальный `local.properties`.

## Архитектура

- `domain`: чистые модели и правила выбора/прогресса.
- `data`: локальный JSON-каталог и DataStore Preferences.
- `ui`: Compose state machine, экраны и дизайн-система.
- Нет backend, аккаунтов, analytics, ads, IAP и runtime permissions.

## Правила кода

- Не добавлять тяжёлые зависимости без необходимости.
- Не хранить секреты, keystore, API keys или приватные URL в репозитории.
- Release signing задавать только через `PORYADOK5_*` Gradle properties/environment variables.
- Не показывать пользователю технические ошибки без понятного русского текста.
- Для нового пользовательского контента использовать русский язык.
- Каталог задач должен оставаться валидным JSON и покрываться unit tests.

## Правила UI/UX

- UI должен выглядеть как законченный mobile product, а не прототип.
- Основной сценарий: onboarding → выбор фильтра → задача → таймер → результат → прогресс.
- Tap targets не меньше 48dp; радиусы карточек и контролов до 8dp.
- Не использовать визуальный шум, слабые самодельные картинки или fake store creatives.

## Правила ассетов

- Финальные иллюстрации, feature graphic и store creatives не создавать кодом.
- В релизном пути разрешены только минимальные vector/adaptive icon assets и реальные app screenshots.
- Слабые или случайные картинки не использовать; вместо них документировать prompts и quality checklist.

## Правила документации

Поддерживать актуальными `README.md` и документы в `docs`: продукт, стек, release, QA, privacy, UI, performance, accessibility, assets и Google Play checklist.

## Definition of Done

1. Продукт запускается.
2. MVP-идея закончена и задокументирована.
3. UI выглядит цельным.
4. Нет временного контента.
5. Основные сценарии работают.
6. Ассеты консистентны и честно промаркированы.
7. Код поддерживаемый.
8. Debug/release проверки выполнены насколько позволяет среда.
9. Google Play checklist создан.
10. Release report создан.
