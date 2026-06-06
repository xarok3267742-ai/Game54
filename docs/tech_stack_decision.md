# Tech Stack Decision

## Выбранный стек

- Kotlin + Jetpack Compose + Material 3.
- Gradle Kotlin DSL.
- Android Gradle Plugin 8.9.1.
- Kotlin 2.0.21.
- Compose BOM 2026.04.01.
- DataStore Preferences 1.1.7.
- minSdk 26, compileSdk 35, targetSdk 35.

## Почему выбран

Репозиторий был пустым, а среда содержит Android SDK, Java 21, Gradle и AVD. Нативный Android быстрее всего даёт production-ready контроль над manifest, permissions, resources, adaptive icon и app bundle.

## Альтернативы

- Flutter: хорош для cross-platform, но в этой задаче лишний слой.
- React Native/Expo: быстрее для web-like UI, но сложнее с release Android package без дополнительного сервиса.
- Godot/игровой стек: не нужен, так как выбран application MVP.

## Команды

```bash
./gradlew clean
./gradlew test
./gradlew lint
./gradlew assembleDebug
./gradlew bundleRelease
```

## Автоматическая проверка

`scripts/check_stack_versions.py` фиксирует Gradle wrapper, AGP, Kotlin, Compose BOM, DataStore, SDK levels, package id and release version against this RC stack decision.

## Ограничения окружения

- `ANDROID_HOME` не был задан, поэтому создан локальный `local.properties` с найденным SDK.
- Compose BOM 2026.04.01 доступен в Google Maven and is used to match the original RC stack plan.
- Финальная upload signing key не создаётся и не хранится в проекте.
- Compose/DataStore добавляют небольшие AndroidX native libraries; они проверяются на 16 KB alignment.
