# Google Play Checklist

## Store Listing

- App name, descriptions, release notes, screenshot captions and keywords are prepared in `docs/store_listing_ru.md`.
- Store listing limits and screenshot caption coverage are checked by `scripts/check_store_listing.py`; evidence is in `docs/store_listing_audit.md`.
- Play Console field map is prepared in `docs/play_console_submission.md`.
- Structured Play Console form answers are prepared in `docs/play_console_forms_answers.json` and checked by `scripts/check_play_console_forms.py`, including `packageName` synchronization with Gradle `applicationId`.
- Policy content risk audit is prepared in `docs/policy_content_risk_audit.md` and checked by `scripts/check_policy_content_risk.py`.
- Play upload preflight is prepared in `docs/play_upload_preflight.md` and automated by `scripts/check_play_upload_readiness.py`.
- Required RC documentation inventory is prepared in `docs/doc_inventory.md` and checked by `scripts/check_doc_inventory.py`.
- Stack versions are documented in `docs/stack_version_audit.md` and checked by `scripts/check_stack_versions.py`.
- Clean Gradle build behavior is documented in `docs/clean_build_audit.md`; `scripts/verify_release_candidate.sh` starts with `./gradlew clean`.
- Local submission packet can be built with `scripts/build_play_submission_packet.sh` into `play-submission`.
- Settings screen exposes app version/about and local-only privacy information for reviewer orientation.

## Visuals

- App icon: ImageGen-derived Play Store 512x512 PNG exists at `store-assets/app-icon/play-store-icon-512.png`; Android launcher resources are generated from the same source as raster density PNGs and checked by `scripts/check_play_store_icon.py`, `scripts/check_store_asset_pixels.py` and `scripts/check_packaged_app_contents.py`.
- Feature graphic: candidate exists at `store-assets/feature-graphic/feature-graphic-candidate-03.png` and is 1024x500 PNG without alpha. Status remains `CONCEPT_CANDIDATE` until final Play Console preview approval.
- Screenshots: real app screenshots captured in `screenshots/play-store`. Manifest: `docs/screenshot_manifest.md`; pixel-level gate: `scripts/check_store_asset_pixels.py`.

## Android Requirements

- Publishing format: Android App Bundle.
- compileSdk/targetSdk: 35.
- minSdk: 26.
- versionCode: 1.
- versionName: 1.0.0-rc1.
- Stack version gate: `scripts/check_stack_versions.py` verifies Gradle 8.11.1, AGP 8.9.1, Kotlin 2.0.21, Compose BOM 2026.04.01, DataStore 1.1.7, SDK levels and package/version metadata.
- AAB metadata: `scripts/check_aab_metadata.py` verifies package id, version, minSdk, targetSdk, compileSdk and uses-permission entries from the release AAB.
- AAB universal APK expansion: `scripts/check_aab_universal_apk.py` verifies `bundletool build-apks --mode=universal` can expand the release AAB and that the extracted `universal.apk` keeps expected package/version/sdk/label/permission metadata. Evidence: `docs/aab_universal_apk_audit.md`.
- APK metadata: `scripts/check_apk_metadata.py` verifies package id, version, minSdk, targetSdk, compileSdk and app label from the built APK used for emulator QA.
- Permissions: no dangerous/runtime Android permissions and no platform permissions such as internet, location, camera, contacts, microphone, storage or notifications. AndroidX adds an internal app-specific signature-level receiver permission that is not user-facing; `scripts/check_apk_permissions.py` derives that permission from Gradle `applicationId` and verifies the built APK does not contain any other uses-permission entries.
- Android backup/data extraction: disabled with `android:allowBackup="false"` and checked in source manifest, debug APK and release AAB by `scripts/check_android_backup_policy.py`. Evidence: `docs/android_backup_policy_audit.md`.
- Manifest component exposure: release AAB manifest is checked by `scripts/check_manifest_component_exposure.py`; only the Gradle-identity launcher `MainActivity`, non-exported AndroidX Startup provider and AndroidX ProfileInstaller receiver protected by `android.permission.DUMP` are allowed. The same gate rejects cleartext/debuggable/network-security legacy exposure flags.
- Packaged contents: `scripts/check_packaged_app_contents.py` verifies debug APK and release AAB contain required runtime entries and exclude workspace-only docs, QA evidence, store assets, privacy drafts and signing-like files. Evidence: `docs/packaged_app_contents_audit.md`.
- Dependency privacy: `scripts/check_dependency_privacy.py` verifies release runtime dependencies and direct Gradle dependencies do not include ads, analytics, crash-reporting, attribution, push marketing or tracking SDK markers. Evidence: `docs/dependency_privacy_audit.md`.
- Native code: small transitive AndroidX `.so` libraries are present; `scripts/check_native_library_packaging.py` verifies installable APK native libraries are uncompressed and pass Android SDK `zipalign -P 16`. Evidence: `docs/native_library_packaging_audit.md`.
- Emulator QA: Android 15 timer/background and no-internet flows passed; Android 16/API 36 smoke, compact-screen, large-screen and large-font flows passed. Evidence is linked from `docs/qa_test_plan.md`.

Sources:
- Target API: https://developer.android.com/google/play/requirements/target-sdk
- App Bundle: https://developer.android.com/guide/app-bundle
- 16 KB page size: https://developer.android.com/guide/practices/page-sizes
- Play Store icon: https://developer.android.google.cn/distribute/google-play/resources/icon-design-specifications

## Privacy And Data Safety

- Data collected: none.
- Data shared: none.
- Accounts: none.
- Ads: none.
- Analytics: none.
- Payments/IAP: none.
- User-generated content: none.
- Device identifiers: not used.
- Release runtime SDK audit: passed, see `docs/dependency_privacy_audit.md`.
- Public privacy policy source is prepared as Markdown in `docs/privacy_policy_draft_ru.md` and as self-contained static HTML in `docs/privacy_policy_ru.html`.
- Static HTML policy is checked by `scripts/check_privacy_policy_html.py` for Russian language metadata, no external references and no-data-collection claims.

Sources:
- Data Safety: https://support.google.com/googleplay/android-developer/answer/10787469
- Target Audience: https://support.google.com/googleplay/android-developer/answer/9867159
- Preview assets: https://support.google.com/googleplay/android-developer/answer/9866151

## Age Rating

Ожидаемый рейтинг: подходит широкой аудитории. Нет насилия, gambling, adult, медицины, финансовых советов, политики и пользовательского контента.

Local content-risk scan: `scripts/check_policy_content_risk.py`; evidence: `docs/policy_content_risk_audit.md`.

## Manual Play Console Actions

- Создать app entry.
- Загрузить signed `.aab`.
- Заполнить Data Safety и privacy policy URL.
- Опубликовать `docs/privacy_policy_ru.html` at a stable public HTTPS URL after replacing the contact line with a real developer support email.
- Заполнить content rating questionnaire.
- Добавить screenshots из `screenshots/play-store` и feature graphic candidate after final visual approval.
- Пройти internal testing.

Detailed field-by-field submission notes: `docs/play_console_submission.md`.

## Release Build Status

`app/build/outputs/bundle/release/app-release.aab` создаётся. Если `PORYADOK5_*` signing inputs отсутствуют, artifact unsigned. Signing setup: `docs/signing_setup.md`.

Run `scripts/verify_release_candidate.sh` for the full local RC gate. It performs a clean Gradle build and refreshes `play-submission`.
For strict upload readiness after configured signing inputs and Play Console manual confirmations, run `scripts/check_play_upload_external_inputs.py` before the final rebuild, then `scripts/check_play_upload_readiness.py --require-upload-ready`; readiness also reruns Play Console form and policy content evidence.
