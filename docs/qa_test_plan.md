# QA Test Plan

## Automated

- `scripts/verify_release_candidate.sh`: full local RC gate; starts with `./gradlew clean` and then runs signing status, tests, lint, debug APK, release AAB, metadata, privacy, store assets, docs and packet checks.
- `./gradlew test`: проверяет 80 задач, уникальные id, зоны, energy, minute values, отсутствие forbidden tokens, streak rules including malformed stored-date cleanup, negative-counter resilience, blank/whitespace completion id handling, settings enum raw-value trimming, DataStore preference mapping/progress normalization/write helpers, wall-clock timer rules, engine suggestion, suggestion-quality classification, completed-id trimming, Home skip exclusion, next task после completion без immediate repeat при доступной соседней задаче, runtime catalog-size reporting, фильтрацию неизвестных completed ids в progress и per-area completed count для Progress UI.
- Timer completion UI disables the “Готово” action after the first submit for the current task to avoid duplicate progress writes from rapid taps.
- Timer session goal keeps the original duration visible as `Цель: 5 мин` above the countdown after the user starts a task.
- Timer completion dock keeps “Готово” pinned below the scrollable timer content, so the finish action remains reachable on compact screens.
- Timer secondary controls keep decorative icons for `Пауза`/`Продолжить` and `Сброс`, while text labels remain the accessible source of meaning.
- Timer expiry UI disables the impossible pause/resume action and labels it `Время вышло`; reset and completion remain available.
- `scripts/check_aab_metadata.py`: проверяет package/version/sdk/uses-permission metadata фактического release AAB через `bundletool dump manifest`.
- `scripts/check_aab_metadata_selftest.py`: проверяет positive/negative paths AAB manifest metadata parser для package, version, targetSdk, app label, allowed app permission и disallowed uses-permission.
- `scripts/check_aab_universal_apk.py`: проверяет, что release AAB разворачивается через `bundletool build-apks --mode=universal`, а извлечённый `universal.apk` сохраняет ожидаемые package/version/sdk/label/permission metadata.
- `scripts/check_aab_universal_apk_selftest.py`: проверяет positive/negative paths bundle-derived APK badging parser и `.apks` archive gate, включая missing `toc.pb`, missing/empty `universal.apk` и bad ZIP.
- `scripts/check_apk_metadata.py`: проверяет фактические package/version/sdk/app label metadata через `aapt dump badging`.
- `scripts/check_apk_metadata_selftest.py`: проверяет positive/negative paths APK badging parser для package, versionName, targetSdk и app label.
- `scripts/check_apk_permissions.py`: проверяет фактические APK permissions через `aapt dump permissions`.
- `scripts/check_apk_permissions_selftest.py`: проверяет positive/negative paths permission parser для empty/allowed permissions, `INTERNET`, dangerous location, notifications и unexpected app-specific permissions.
- `scripts/check_android_backup_policy.py`: проверяет `android:allowBackup=false` и отсутствие backup/data extraction manifest hooks в source manifest, debug APK и release AAB.
- `scripts/check_android_backup_policy_selftest.py`: проверяет positive/negative paths для source/AAB manifest backup flags и debug APK `aapt dump xmltree` parsing.
- `scripts/check_manifest_component_exposure.py`: проверяет source manifest и release AAB manifest на отсутствие лишних exposed activity/service/provider/receiver компонентов и cleartext/debuggable/network-security exposure flags.
- `scripts/check_manifest_component_exposure_selftest.py`: проверяет positive и negative paths для component exposure, cleartext traffic и protected AndroidX profile receiver.
- `scripts/check_packaged_app_contents.py`: проверяет ZIP-содержимое debug APK и release AAB, required runtime entries и отсутствие workspace-only docs/QA/store/signing files внутри app artifacts.
- `scripts/check_packaged_app_contents_selftest.py`: проверяет positive/negative paths packaged contents gate для missing/empty required entries, missing prefixes, workspace-only paths, source suffixes, signing config filenames, bad ZIP и empty artifacts.
- `scripts/check_native_library_packaging.py`: проверяет native `.so` packaging в debug APK и bundle-derived universal APK, включая uncompressed entries и `zipalign -P 16`.
- `scripts/check_native_library_packaging_selftest.py`: проверяет positive/negative paths native packaging gate для compressed `.so`, empty `.so`, universal APK extraction и zipalign status/output parsing.
- `scripts/check_task_catalog_quality.py`: проверяет 80 задач, 16 задач на область, последовательные ids, распределение energy/minutes, кириллицу, длины строк, 3 шага на задачу и отсутствие дублей.
- `scripts/check_task_catalog_quality_selftest.py`: проверяет positive/negative paths source catalog quality gate для required keys, area/id matching, minutes type, Cyrillic/Latin text, punctuation, repeated steps, duplicate titles, area count, sequential ids, draft markers и load failures.
- `scripts/check_runtime_catalog_count.py`: проверяет, что runtime progress/about UI получает размер каталога из `PoryadokEngine`, а не держит hardcoded `80` в Kotlin UI text.
- `scripts/check_runtime_catalog_count_selftest.py`: проверяет positive/negative paths runtime catalog-count gate для hardcoded progress/about copy, engine contract, UI usage и unit-test evidence.
- `scripts/check_engine_completed_id_normalization.py`: проверяет, что `PoryadokEngine` нормализует completed ids перед suggestion exclusion и progress-count calculations.
- `scripts/check_engine_completed_id_normalization_selftest.py`: проверяет positive/negative paths для raw completed-id usage в engine suggestions и progress counts.
- `scripts/check_home_task_skip.py`: проверяет, что Home-действие `Другая задача` подключено к engine exclusions, не пишет progress и покрыто unit tests на альтернативу/исчерпание списка.
- `scripts/check_home_skip_exhausted_hint.py`: проверяет Home skip exhausted hint, чтобы disabled `Другая задача` объяснялась текстом `Других задач по этому подбору сейчас нет` только при `!canSkipTask`.
- `scripts/check_home_skip_exhausted_hint_selftest.py`: проверяет positive/negative paths для Home skip exhausted hint guard.
- `scripts/check_home_selection_copy.py`: проверяет Home selection copy, чтобы подсказка качества подбора оставалась пользовательской (`Совпадает с выбором`, `Зона и время совпали`, `Ближайшая свободная задача`) и не возвращала техническое слово `фильтр`.
- `scripts/check_home_selection_copy_selftest.py`: проверяет positive/negative paths для Home selection copy guard, включая missing copy, старое `Подбор: точно по фильтру` и docs markers.
- `scripts/check_home_action_icons.py`: проверяет Home action icons, чтобы `Запустить таймер`, `Другая задача` и `Все шаги` сохраняли текстовые labels и decorative vector icons без новой тяжёлой icon dependency.
- `scripts/check_home_action_icons_selftest.py`: проверяет positive/negative paths для Home action icons guard, включая missing icons, пропажу text label, не-decorative icon semantics, spacing и docs markers.
- `scripts/check_main_flow_action_icons.py`: проверяет main-flow CTA icons, чтобы onboarding/details/timer/result/progress actions and timer controls сохраняли decorative icons, включая локальный `PauseIcon`, и text labels без `material-icons-extended`.
- `scripts/check_main_flow_action_icons_selftest.py`: проверяет positive/negative paths для main-flow CTA icons guard, включая missing timer pause/reset/progress/result icons, heavy dependency drift и docs markers.
- `scripts/check_task_result_preview.py`: проверяет Home task result preview, чтобы ожидаемый результат показывался compact result preview с отдельной меткой `После`, а не старой inline строкой `После: ...`.
- `scripts/check_task_result_preview_selftest.py`: проверяет positive/negative paths для Home task result preview guard, включая старую inline строку, framed/interactive drift, undersized preview и docs markers.
- `scripts/check_result_next_details.py`: проверяет, что Result primary `Посмотреть следующую` открывает details для `nextTask.id`, а `Запустить таймер` остаётся вторичным shortcut.
- `scripts/check_result_next_details_selftest.py`: проверяет positive/negative paths для Result next-details route guard.
- `scripts/check_result_action_layout.py`: проверяет Result action layout, где `На главный экран` и `Посмотреть итоги` остаются icon-supported peer actions с `HomeIcon` / `StatsIcon` в одной строке, а не четырьмя stacked full-width кнопками.
- `scripts/check_result_action_layout_selftest.py`: проверяет positive/negative paths для Result action-layout guard, включая missing peer icons.
- `scripts/check_result_content_focus.py`: проверяет, что Result использует task-specific result text, не возвращает общий блок `Что изменилось`, а next-task preview с `showResult = true` идёт перед primary actions.
- `scripts/check_result_content_focus_selftest.py`: проверяет positive/negative paths для Result content-focus guard, включая old generic amber copy, missing `showResult` и неправильный порядок next-task preview.
- `scripts/check_result_completion_identity.py`: проверяет, что Result показывает `Сделано: …` с названием выполненной задачи между `Готово` and task-specific outcome text.
- `scripts/check_result_completion_identity_selftest.py`: проверяет positive/negative paths для Result completion identity guard, включая missing copy, ошибочный `nextTask.title`, неправильный порядок и docs markers.
- `scripts/check_progress_continue_action.py`: проверяет, что экран “Итоги” сохраняет primary action “Продолжить с задачей” и возвращает пользователя на Home task flow.
- `scripts/check_progress_continue_action_selftest.py`: проверяет positive/negative paths для Progress continue-action guard.
- `scripts/check_progress_focus_summary.py`: проверяет, что “Итоги” получает `nextFocusArea` из `PoryadokEngine`, показывает compact summary `Следующая зона` / `Каталог закрыт` и не превращает его во вложенную карточку или кнопку.
- `scripts/check_progress_focus_summary_selftest.py`: проверяет positive/negative paths для Progress focus summary guard, включая missing `nextFocusArea`, missing complete-state copy, framed/interactive drift и docs markers.
- `scripts/check_progress_rhythm_summary.py`: проверяет Progress rhythm summary, чтобы “Итоги” показывали компактные non-interactive unframed факты `Серия` и `Счётчик` вместо длинного справочного абзаца или вложенных карточек.
- `scripts/check_progress_rhythm_summary_selftest.py`: проверяет positive/negative paths для Progress rhythm summary guard: старый абзац, missing counter fact, interactive drift, framed/nested-card drift, undersized facts and docs markers.
- `scripts/check_settings_danger_action.py`: проверяет, что подтверждённый destructive reset в Settings использует `DangerAction` с 52dp target и Material `error` styling.
- `scripts/check_settings_danger_action_selftest.py`: проверяет positive/negative paths для Settings DangerAction guard.
- `scripts/check_settings_reset_cancel.py`: проверяет, что Settings reset confirmation показывает `Отмена` перед `Сбросить прогресс` и отмена закрывает confirm state без запуска reset.
- `scripts/check_settings_reset_cancel_selftest.py`: проверяет positive/negative paths для reset-cancel guard.
- `scripts/check_settings_privacy_summary.py`: проверяет, что Settings privacy block остаётся scannable через unframed `PrivacyBadgeGrid` с `Без интернета` / `работает офлайн`, `Без аккаунта` / `вход не нужен`, `Без рекламы` / `нет баннеров`, `Без аналитики` / `нет трекеров`, не выглядит как вложенные карточки и не называет продукт игрой.
- `scripts/check_settings_privacy_summary_selftest.py`: проверяет positive/negative paths для Settings privacy summary guard, включая framed/nested-card drift, interactive drift и undersized facts.
- `scripts/check_settings_about_summary.py`: проверяет Settings about summary, чтобы `О приложении` показывал compact facts `Версия`, `Каталог`, `Данные`, держал `на устройстве` в широкой колонке и отделял reset section от первого viewport вместо длинного paragraph-heavy блока.
- `scripts/check_settings_about_summary_selftest.py`: проверяет positive/negative paths для Settings about summary guard, включая missing summary, возврат длинного абзаца, missing `Данные`, framed drift и docs markers.
- `scripts/check_task_filter_minutes_normalization.py`: проверяет, что UI и `PoryadokEngine` нормализуют duration-фильтр к 3/5/10 минутам перед suggestion matching.
- `scripts/check_task_filter_minutes_normalization_selftest.py`: проверяет positive/negative paths для raw duration usage в engine, stable index и UI filter construction.
- `scripts/check_screen_state_saveability.py`: проверяет, что текущий internal screen хранится через saveable `AppScreen` route saver, включая task-bound details/timer/result routes и route-safe task-id validation при восстановлении.
- `scripts/check_screen_state_saveability_selftest.py`: проверяет positive/negative paths screen-state gate для plain `remember`, missing route serialization, missing task-bound restore coverage, missing route-id validation и raw nonblank restore drift.
- `scripts/check_task_repository_parser.py`: проверяет, что runtime parser каталога отклоняет blank ids, route-unsafe ids, duplicate ids, id/area mismatches, unsupported minutes через общий `SupportedTaskMinutes` и shared `isRouteSafeTaskId`, не использует permissive fallback для area/energy; launch error остаётся русским generic text.
- `scripts/check_task_repository_parser_selftest.py`: проверяет positive/negative paths parser gate для permissive fallback, route-unsafe id drift, local task-id regex drift, missing id/area validation, hardcoded duration-set drift, missing duration/step validation, technical error leakage и missing parser tests.
- `scripts/check_startup_error_retry.py`: проверяет Startup error retry, чтобы локальная ошибка загрузки каталога оставалась generic Russian, не показывала exception text и давала действие `Повторить загрузку`.
- `scripts/check_startup_error_retry_selftest.py`: проверяет positive/negative paths для Startup error retry guard.
- `scripts/check_packaged_task_catalog.py`: проверяет, что `tasks_ru.json` внутри debug APK и release AAB байт-в-байт совпадает с source catalog.
- `scripts/check_packaged_task_catalog_selftest.py`: проверяет positive/negative paths packaged catalog gate для invalid JSON, non-array root, wrong task count, missing packaged entry, extra task-like JSON, bad ZIP, missing artifact и source/package mismatch.
- `scripts/check_store_listing_selftest.py`: проверяет positive/negative paths для Play listing gate: required sections, limits, caption count/length, duplicate keywords и risky promotional claims.
- `scripts/check_play_store_icon_selftest.py`: проверяет positive/negative paths Play Store icon gate для PNG signature, short header, dimensions, RGBA format, bit depth и byte-size limit.
- `scripts/check_store_asset_pixels.py`: проверяет PNG-pixel gate для Play screenshots, app icon и feature graphic candidate: размеры, format, opacity, nonblank и near-duplicate screenshots.
- `scripts/check_store_asset_pixels_selftest.py`: проверяет synthetic PNG positive/negative paths для parser/pixel gate, включая temporary files outside repo, transparency, wrong dimensions, flat frames и average-hash duplicate detection.
- `scripts/check_dependency_privacy.py`: проверяет release runtime dependencies и прямые Gradle-зависимости на отсутствие ads, analytics, crash-reporting, attribution, push marketing и tracking SDK.
- `scripts/check_dependency_privacy_selftest.py`: проверяет positive/negative paths dependency privacy marker detection для разрешённых AndroidX dependencies и запрещённых ads, analytics, crash reporting, tracking и Firebase SDK markers.
- `scripts/check_lifecycle_state_collection.py`: проверяет, что `MainActivity` собирает DataStore preferences через `collectAsStateWithLifecycle`, а не plain `collectAsState`.
- `scripts/check_lifecycle_state_collection_selftest.py`: проверяет positive/negative paths lifecycle-state gate для missing lifecycle dependency, lifecycle-unaware import и lifecycle-unaware Flow collection call.
- `scripts/check_loading_state_layout.py`: проверяет Loading state layout, чтобы startup/progress loading использовал full-screen centered spinner, а не ширинный top-heavy блок.
- `scripts/check_loading_state_layout_selftest.py`: проверяет positive/negative paths для Loading state layout guard.
- `scripts/check_progress_persistence_normalization.py`: проверяет, что completed-task ids и last-done dates нормализуются через shared domain helpers в progress rules и DataStore read/write paths, а whitespace/malformed cases покрыты unit tests.
- `scripts/check_progress_persistence_normalization_selftest.py`: проверяет positive/negative paths для missing normalizer, raw blank-only filters, raw date persistence и missing whitespace/malformed-date unit-test evidence.
- `scripts/check_settings_enum_normalization.py`: проверяет, что settings enum raw values trim-ятся перед fallback, включая preferred-area DataStore mapping.
- `scripts/check_settings_enum_normalization_selftest.py`: проверяет positive/negative paths для missing trim, raw enum matching и missing settings normalization tests.
- `scripts/check_play_console_forms_selftest.py`: проверяет positive/negative paths для structured Play Console answers: no ads, no user data collection, not children-directed, no online interaction, required official sources, privacy source и store listing claims.
- `scripts/check_policy_content_risk.py`: проверяет task text и store listing against current Target Audience and Content Rating claims.
- `scripts/check_policy_content_risk_selftest.py`: проверяет positive/negative paths content-risk gate для risky terms в задачах/listing, sensitive categories, child-directed appeal, low-risk claims и mismatch Play form answers.
- `scripts/check_qa_evidence.py`: проверяет emulator QA reports, evidence directories, UI XML/PNG pairs, ключевые UI markers, Gradle `applicationId` package markers и empty app-specific crash/error gates.
- `scripts/check_qa_evidence_selftest.py`: проверяет positive/negative paths QA evidence gate для Gradle identity package markers, reports, evidence directories, UI XML package markers, PNG signatures, snippet markers, zero-match logs и allowed external crash logs.
- `scripts/check_doc_inventory.py`: проверяет обязательные RC-документы, marker strings, минимальный размер файлов и отсутствие `story_bible.md` в release-owned source/documentation paths без обхода Gradle/build output.
- `scripts/check_doc_inventory_selftest.py`: проверяет positive/negative paths documentation inventory gate для missing docs, directories instead of files, tiny docs, missing markers, root/docs story bible detection и build-output exclusion.
- `scripts/check_header_icon_vectors.py`: проверяет, что `HeaderAction` и back action используют vector icons вместо текстовых glyph-иконок, что “Итоги” использует `StatsIcon` вместо completion-check и что русские accessibility labels сохранены.
- `scripts/check_header_icon_vectors_selftest.py`: проверяет positive/negative paths для HeaderAction vector-icon guard, включая регрессию `StatsIcon` → checkmark.
- `scripts/check_onboarding_copy_alignment.py`: проверяет onboarding copy и unframed `Первые 5 минут` summary, чтобы первый запуск обещал только стартовую зону, а энергия и время оставались в Home-блоке “Настроить подбор”.
- `scripts/check_onboarding_copy_alignment_selftest.py`: проверяет positive/negative paths для onboarding copy alignment guard, включая запрет старых `StepRow`/`Как это работает` на первом запуске.
- `scripts/check_home_filter_disclosure.py`: проверяет Home filter disclosure, чтобы настройка зоны/энергии/времени раскрывалась по явному whole-row 56dp действию, collapsed-состояние оставалось unframed summary вместо raised card, а индикатор `Изменить`/`Скрыть` сохранял шеврон.
- `scripts/check_home_filter_disclosure_selftest.py`: проверяет positive/negative paths для Home filter disclosure guard, включая запрет возврата к маленькому `TextButton` и пропажу шеврон-индикатора.
- `scripts/check_task_details_briefing.py`: проверяет Task details briefing, чтобы экран деталей показывал `выбрана`, `Перед стартом`, unframed зона/энергия/время facts, compact `После` outcome preview и сохранял briefing перед полным списком шагов.
- `scripts/check_task_details_briefing_selftest.py`: проверяет positive/negative paths для Task details briefing guard, включая missing selected-status marker, неправильный порядок outcome preview и framed Surface/border regression.
- `scripts/check_task_details_start_dock.py`: проверяет Task details start dock, чтобы `Начать` был закреплён внизу, а scroll content имел bottom clearance.
- `scripts/check_task_details_start_dock_selftest.py`: проверяет positive/negative paths для Task details start dock guard.
- `scripts/check_timer_session_goal.py`: проверяет Timer session goal, чтобы исходная длительность `Цель: 5 мин` оставалась рядом с метаданными задачи и выше progress/countdown.
- `scripts/check_timer_session_goal_selftest.py`: проверяет positive/negative paths для Timer session goal guard.
- `scripts/check_timer_outcome_preview.py`: проверяет Timer outcome preview, чтобы compact `После` оставался под списком шагов и до pause/reset controls.
- `scripts/check_timer_outcome_preview_selftest.py`: проверяет positive/negative paths для Timer outcome preview guard, включая missing preview, неправильный порядок, старый inline `После: ...` и documentation markers.
- `scripts/check_timer_completion_dock.py`: проверяет Timer completion dock, чтобы `Готово` оставалось в закреплённой нижней панели, а прокручиваемый контент таймера имел нижний запас.
- `scripts/check_timer_completion_dock_selftest.py`: проверяет positive/negative paths для Timer completion dock guard.
- `scripts/check_progress_line_component.py`: проверяет, что timer/catalog/zone progress bars используют `ProgressLine` вместо Material `LinearProgressIndicator`, сохраняют semantics и не рисуют ложный end-dot у нулевого прогресса.
- `scripts/check_progress_line_component_selftest.py`: проверяет positive/negative paths для ProgressLine guard.
- `scripts/check_privacy_policy_rendering_selftest.py`: проверяет генерацию publishable privacy policy с real support email, отказ при нерешаемой contact line, запрет внешних HTTP references и mismatch support email.
- `scripts/check_publishable_privacy_policy_selftest.py`: проверяет positive/negative paths publishable privacy policy checker для optional local mode, strict missing inputs, reserved email, requested-email mismatch и pre-publication contact text.
- `scripts/check_publishable_privacy_policy_cli_selftest.py`: проверяет CLI-цепочку `render_privacy_policy.py` + `check_publishable_privacy_policy.py` на реальном source HTML и временном output вне workspace.
- `scripts/check_play_submission_publishable_policy_packet.py`: проверяет, что `scripts/build_play_submission_packet.sh` при реальном support email генерирует publishable privacy policy, включает её в packet/checksums и затем восстанавливает packet.
- `scripts/check_play_submission_publishable_policy_packet_selftest.py`: проверяет positive/negative paths packet publishable-policy gate для missing HTML, missing checksums и missing checksum entry.
- `scripts/check_play_upload_external_inputs_selftest.py`: проверяет ранний handoff preflight для support email, privacy URL, live privacy policy content и manual Play Console confirmation flags без реальной сети.
- `scripts/check_play_upload_readiness_selftest.py`: проверяет правила strict upload gate для packet sync pass-through/failure, release signing inputs, privacy URL, support email, опубликованного текста privacy policy, Play Console forms/policy checker pass-through, freshness-checker вызова для `artifact_manifest.json` и upload blockers без зависимости от внешней сети.
- `scripts/check_play_upload_candidate_handoff.py`: проверяет порядок финального handoff, чтобы external upload inputs проверялись до полного verifier, а signed bundle и packet пересобирались после cleanup полного verifier и до strict upload gate.
- `scripts/check_play_upload_candidate_handoff_selftest.py`: проверяет positive/negative paths handoff checker для strict signing check, external input preflight, signed bundle rebuild, packet rebuild, strict upload gate и shell safety markers.
- `scripts/check_prepare_play_upload_candidate_negative_path.py`: запускает финальный handoff в изолированной среде без signing inputs и проверяет, что он падает на Step 1 до external input preflight, полного verifier, signed rebuild и packet rebuild.
- `scripts/check_prepare_play_upload_candidate_external_inputs_negative_path.py`: запускает финальный handoff с временными signing inputs и без external upload inputs, затем проверяет, что он падает на Step 2 до полного verifier, signed rebuild и packet rebuild.
- `scripts/check_release_artifact_manifest_checker_selftest.py`: проверяет negative paths checker для signed packet AAB identity, missing packet AAB, signing-input/evidence blocker mismatch и неверного artifact status.
- `scripts/check_release_artifact_manifest_selftest.py`: проверяет, что generated artifact manifest отклоняет reserved privacy hosts с портами и корректно классифицирует signing-input, Play form/policy evidence и upload blockers.
- `scripts/check_play_submission_packet_contents.py`: проверяет allowlist содержимого `play-submission`, чтобы packet не содержал лишние файлы, build output или key/keystore-like artifacts.
- `scripts/check_play_submission_packet_contents_selftest.py`: проверяет positive/negative paths allowlist для unsigned packet, signed AAB inclusion, missing files и key-like files.
- `scripts/check_play_submission_packet_sync.py`: проверяет, что copied docs/assets/screenshots в `play-submission` byte-for-byte совпадают с source materials, а `checksums.sha256` покрывает текущие packet files без stale/missing entries.
- `scripts/check_play_submission_packet_sync_selftest.py`: проверяет positive/negative paths packet sync gate для stale packet files, missing checksum entries, stale checksum entries, malformed checksum lines и checksum mismatches.
- `scripts/check_release_hygiene.py`: проверяет, что workspace не содержит upload keystore, private keys, signing property files или реальные signing password assignments.
- `scripts/check_release_hygiene_selftest.py`: проверяет сам release hygiene gate на clean workspace, key/keystore-like files, project signing values, real-looking password assignments, safe examples и private key blocks.
- `scripts/check_release_signing_inputs_selftest.py`: проверяет absent/strict/partial signing inputs, Gradle-property precedence over environment values, `GRADLE_USER_HOME`, project `gradle.properties` rejection, readable private-key alias and non-private alias rejection.
- `scripts/check_accessibility_targets.py`: проверяет 48dp+ tap targets для интерактивных shared components, selected-state semantics для filter chips, top/header actions, 56dp full-row settings switch target, disabled expired timer control, явный `onPrimary` label color для primary CTA, семантику back action и русские content descriptions для compact header actions.
- `scripts/check_accessibility_targets_selftest.py`: проверяет positive/negative paths accessibility gate для primary CTA content/label contrast, filter chip selected semantics, header tap target, settings full-row switch target, expired timer control, back action label, header action label и документации 48dp.
- `scripts/check_ui_label_consistency.py`: проверяет, что активные Home/Result/Progress metric labels используют `выполнено`, а task status рендерится через неинтерактивный `TaskStatusPill`, не похожий на кнопку.
- `scripts/check_ui_label_consistency_selftest.py`: проверяет positive/negative paths для отката metric label к `сделано`, missing `выполнено` metric labels, missing `TaskStatusPill` и button-like status pill regressions.
- `scripts/check_rc_traceability.py`: проверяет матрицу требований исходного RC-плана и отделяет локально доказанные пункты от внешних Play upload действий.
- `scripts/check_rc_traceability_selftest.py`: проверяет positive/negative paths traceability gate для missing rows/statuses, missing evidence files, missing evidence markers и local/external requirement counts.
- `scripts/check_stack_versions_selftest.py`: проверяет positive/negative paths stack version gate для Gradle wrapper, AGP, Kotlin plugins, Compose BOM, DataStore, SDK levels, app metadata и docs markers.
- `scripts/check_visible_text_ru.py`: проверяет, что видимые app strings остаются русскоязычными.
- `scripts/check_visible_text_ru_selftest.py`: проверяет positive/negative paths Russian visible text gate для кириллицы, interpolation, ignored non-visible strings, Kotlin visible calls, model labels и strings XML.
- `scripts/check_privacy_policy_html_selftest.py`: проверяет positive/negative paths static privacy policy HTML gate для `lang=ru`, title/h1, no-data text, external references, scripts и tracking markers.
- `./gradlew lint`: Android lint, manifest/resources/static checks.
- `./gradlew assembleDebug`: debug package.
- `./gradlew bundleRelease`: release app bundle.

## Manual Emulator QA

1. Установить debug build на Android 15 AVD.
2. Запустить приложение.
3. Пройти onboarding.
4. На главном экране проверить подсказку качества подбора, compact result preview `После`, метрики “выполнено”, “серия”, “каталог”, selected state у chips, затем нажать “Другая задача” и убедиться, что заголовок задачи меняется без увеличения progress.
5. Открыть детали задачи и проверить, что summary карточка не дублирует первый шаг, показывает статус `выбрана`, блок `Перед стартом` показывает unframed зона/энергия/время facts и `После` outcome preview перед блоком “Шаги”, а закреплённый `Начать` запускает таймер.
6. Запустить таймер, проверить `Цель: 5 мин` над прогрессом/обратным отсчётом, compact `После` под шагами, закреплённое `Готово` в нижнем dock, нажать pause/resume/reset; при истечении времени pause/resume должен стать disabled `Время вышло`.
7. Отправить приложение в background во время таймера и вернуться: таймер должен догнать реальное прошедшее время.
8. Завершить задачу.
9. При быстром повторном нажатии “Готово” убедиться, что completion записывается один раз.
10. На result проверить `Сделано: …` с названием выполненной задачи, метрики “выполнено”, “серия”, “каталог”, task-specific result text без общего блока `Что изменилось`, next-task preview с `После`, Result action layout с `На главный экран` и `Посмотреть итоги` в одной peer-строке, нажать “Посмотреть следующую” и убедиться, что открываются details следующей задачи без записи progress; вернуться и проверить вторичный shortcut `Запустить таймер`, убедившись, что не стартует та же задача, если есть другая подходящая в exact filter или той же зоне/длительности. Для полностью закрытого каталога проверить состояние “Каталог пройден” и кнопку “Повторить задачу”.
11. Проверить progress: на “Итоги” должны быть метрики “выполнено”, “серия”, “каталог”, нейтральная строка “Отмечено задач: N из M.”, прогресс по зонам, unframed Progress rhythm summary с `Серия` / `Счётчик` и действие “Продолжить с задачей”; нажатие возвращает на Home без записи нового прогресса.
12. Нажать system Back с внутренних экранов: ожидается возврат в app flow, а не неожиданный выход в launcher.
13. Открыть settings, проверить unframed privacy facts, compact about summary `Версия` / `Каталог` / `Данные`, что `на устройстве` не ломается на несколько строк и reset card не торчит тонким срезом снизу, переключить haptics нажатием по строке настройки, сменить preferred area.
14. В settings нажать “Подготовить сброс”, проверить, что видны “Отмена” и “Сбросить прогресс”; нажать “Отмена” и убедиться, что сброс не выполнен. Затем повторить подтверждение, нажать “Сбросить прогресс” и проверить inline-сообщение “Готово. Прогресс сброшен, можно начать заново.”
15. Перезапустить приложение и проверить сохранение onboarding/settings.
16. Проверить без интернета: сценарий должен работать полностью.

## Screen Sizes

- Medium phone 1080x2400: captured screenshot set exists in `screenshots/play-store`.
- Compact phone 720x1280: Android 16 compact-screen QA passed with scroll evidence in `qa/emulator-android16-compact-screen`.
- Large viewport 2000x2560: Android 16 large-screen QA passed with centered max-width evidence in `qa/emulator-android16-large-screen`.
- Large font: Android 16 large-font QA passed at `font_scale=1.3` on 1080x2400.
- Проверить, что тексты не обрезаются и кнопки не перекрываются.

## Crash Checks

- `adb logcat -b crash` после smoke flow.
- Проверить, что нет runtime permission prompts.

## Выполненный Smoke QA

- Debug APK установлен на Android 15 AVD.
- Onboarding, home, timer, result и progress проверены через ADB taps/screenshots.
- App process remained alive; app-filtered logcat did not show crashes.
- Settings flow checked and captured in the final screenshot set.
- Contaminated AVD focus switching was caused by unrelated pre-existing packages. They were removed from `emulator-5554` before final screenshot capture.

## Выполненный Android 15 Primary CTA Contrast QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- Onboarding, Home, Timer and Result were captured from the real app UI after the explicit primary CTA `onPrimary` label fix.
- Primary actions `Начать`, `Запустить таймер`, `Готово` and `Посмотреть следующую` were visually checked as readable white text on sage buttons.
- App-specific fatal/ANR match file contained 0 lines for `ru.poryadok5.app`.
- Evidence: `docs/emulator_android15_primary_action_contrast_qa_2026_06_03.md` and `qa/emulator-android15-primary-action-contrast-qa-2026-06-03`.

## Выполненный Android 15 Settings Haptics Row QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- Settings was opened through Home `Опции`.
- The haptics row exposed a checkable/clickable full-row target with bounds `[100,822][980,995]`.
- A tap on the `Тактильный отклик` text label changed the row state from `checked=true` to `checked=false`.
- App-specific fatal/ANR match file contained 0 lines for `ru.poryadok5.app`.
- Evidence: `docs/emulator_android15_settings_haptics_row_qa_2026_06_03.md` and `qa/emulator-android15-settings-haptics-row-qa-2026-06-03`.

## Выполненный Android 15 Settings Reset Cancel QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- Settings reset confirmation was opened through `Подготовить сброс`.
- The confirmation state showed `Отмена` before `Сбросить прогресс`.
- Tapping `Отмена` returned to `Подготовить сброс`, hid `Сбросить прогресс` and did not show the reset success notice.
- Repeating confirmation and tapping `Сбросить прогресс` showed `Готово. Прогресс сброшен, можно начать заново.`
- App-specific fatal/ANR match file contained 0 lines for `ru.poryadok5.app`.
- Crash buffer contained an unrelated `com.android.bluetooth` / `droid.bluetooth` system crash; focus stayed on `ru.poryadok5.app/.MainActivity`.
- Evidence: `docs/emulator_android15_settings_reset_cancel_qa_2026_06_03.md` and `qa/emulator-android15-settings-reset-cancel-qa-2026-06-03`.

## Выполненный Android 15 Settings Privacy Summary QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5554`.
- Fresh debug install and app data clear.
- Settings was opened through Home `Опции` after the `PrivacyBadgeGrid` polish.
- The Settings privacy card showed `Прогресс хранится только на устройстве` and all four unframed facts with compact explanations: `Без интернета` / `работает офлайн`, `Без аккаунта` / `вход не нужен`, `Без рекламы` / `нет баннеров`, `Без аналитики` / `нет трекеров`.
- The refreshed Play screenshot `screenshots/play-store/06-settings.png` was captured from the real app UI at 1080x2400.
- App-specific crash match file contained 0 lines.
- Evidence: `docs/emulator_android15_settings_privacy_summary_qa_2026_06_06.md` and `qa/emulator-android15-settings-privacy-summary-qa-2026-06-06`.

## Выполненный Android 15 Progress Continue QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- Onboarding, Home timer start, Timer completion and Result-to-Progress were checked through ADB UI tree dumps and screenshots.
- Progress showed `Итоги`, `Отмечено задач: 1 из 80.` and the new action `Продолжить с задачей`.
- Tapping `Продолжить с задачей` returned to Home with `1 дн.` and `1%`, without adding a second completion.
- The refreshed Play screenshot `screenshots/play-store/05-progress.png` was captured from the real app UI at 1080x2400.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_progress_continue_qa_2026_06_04.md` and `qa/emulator-android15-progress-continue-qa-2026-06-04`.

## Выполненный Android 15 Home Task Skip QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- Home was captured before pressing `Другая задача`; this refreshed `screenshots/play-store/02-home.png` from the real app UI.
- Pressing `Другая задача` changed the task from `Подготовить спокойный угол` to `Навести порядок на диване`.
- The `выполнено` metric stayed at `0`, so skip did not record progress.
- Final focus stayed on `ru.poryadok5.app/.MainActivity`.
- Crash buffer and fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_home_task_skip_qa_2026_06_03.md` and `qa/emulator-android15-home-task-skip-qa-2026-06-03`.

## Выполненный Android 15 Result Next Details QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- Onboarding, Home timer start, Timer completion and Result were checked through ADB UI tree dumps and screenshots.
- Result was captured after adding `Посмотреть шаги`; this refreshed `screenshots/play-store/04-result.png` from the real app UI.
- Result preview showed `Навести порядок на диване`; tapping `Посмотреть шаги` opened Details for the same task with `Выбранная задача` and `Шаги`.
- Crash buffer and fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_result_next_details_qa_2026_06_03.md` and `qa/emulator-android15-result-next-details-qa-2026-06-03`.

## Выполненный Android 15 Result Action Layout QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- Onboarding, Home timer start, Timer completion and Result were checked through ADB UI tree dumps and screenshots.
- Result was captured after compacting the action layout; this refreshed `screenshots/play-store/04-result.png` from the real app UI.
- `На главный экран` and `Посмотреть итоги` were visible as equal-width peer actions in one row above the Android navigation bar.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_result_action_layout_qa_2026_06_05.md` and `qa/emulator-android15-result-action-layout-qa-2026-06-05`.

## Выполненный Android 15 Result Details-First QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5554`.
- Fresh debug install and app data clear.
- Onboarding, Home timer start, Timer completion, Result and Result-primary-to-Details were checked through ADB UI tree dumps and screenshots.
- Result was captured after making `Посмотреть следующую` the primary action; this refreshed `screenshots/play-store/04-result.png` from the real app UI.
- Tapping `Посмотреть следующую` opened Details for the fresh next task with `Выбранная задача`, `Перед стартом`, `Шаги` and pinned `Начать 5 мин`.
- `Запустить таймер` remained visible as the secondary direct-start shortcut.
- App-specific crash match file contained 0 lines.
- Evidence: `docs/emulator_android15_result_details_first_qa_2026_06_06.md` and `qa/emulator-android15-result-details-first-qa-2026-06-06`.

## Выполненный Android 15 Task Status Pill QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5554`.
- Fresh debug install and app data clear.
- Onboarding, Home timer start, Timer completion and Result were checked through ADB UI tree dumps and screenshots.
- Home and Result were captured after replacing the button-like task status chip with `TaskStatusPill`; this refreshed `screenshots/play-store/02-home.png` and `screenshots/play-store/04-result.png`.
- The visible status `новая` appears as plain text with a dot indicator rather than a clickable/focusable UI node.
- App-specific crash match file contained 0 lines.
- Evidence: `docs/emulator_android15_task_status_pill_qa_2026_06_06.md` and `qa/emulator-android15-task-status-pill-qa-2026-06-06`.

## Выполненный Android 15 ProgressLine QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- Onboarding, Home timer start, Timer completion and Result-to-Progress were checked through ADB UI tree dumps and screenshots.
- Timer and Progress were captured after replacing Material progress bars with `ProgressLine`; this refreshed `screenshots/play-store/03-timer.png` and `screenshots/play-store/05-progress.png` from the real app UI.
- Progress rows with `0 из 16` no longer showed a false right-edge end-dot; the completed `Дом` row kept the expected left fill.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_progress_line_qa_2026_06_05.md` and `qa/emulator-android15-progress-line-qa-2026-06-05`.

## Выполненный Android 15 Onboarding Copy QA

- Android 15 AVD `Medium_Phone_API_35_Default`, serial `emulator-5566`.
- Fresh debug install and app data clear.
- The first-run onboarding screen was captured after aligning “Как это работает” copy with the visible controls.
- Onboarding showed `Выбираете стартовую зону.`, `Получаете задачу и при желании уточняете подбор.` and a visible `Начать` primary action.
- The refreshed Play screenshot `screenshots/play-store/01-onboarding.png` was captured from the real app UI at 1080x2400.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_onboarding_copy_qa_2026_06_06.md` and `qa/emulator-android15-onboarding-copy-qa-2026-06-06`.

## Выполненный Android 15 Onboarding Flow Summary QA

- Android 15/API 35 AVD, serial `emulator-5554`.
- Fresh debug install on 1080x2400, density 420, font scale 1.0.
- The first-run onboarding screen was captured after replacing the framed `Как это работает` card with the unframed `Первые 5 минут` summary.
- Onboarding showed `Сначала`, `Затем`, `После`, the three aligned flow facts and a visible `Начать` primary action.
- The refreshed Play screenshot `screenshots/play-store/01-onboarding.png` was captured from the real app UI at 1080x2400.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_onboarding_flow_summary_qa_2026_06_06.md` and `qa/emulator-android15-onboarding-flow-summary-qa-2026-06-06`.

## Выполненный Android 16 Home Filter Disclosure QA

- Android 16/API 36 AVD `Medium_Phone_API_36`, serial `emulator-5556`.
- Fresh debug install on 1080x2400, density 420.
- Onboarding and Home were checked after the collapsed Home filter disclosure polish.
- The collapsed Home state showed `Настроить подбор`, current selection summary and `Изменить`, without expanded zone/energy/time controls in the first viewport.
- Tapping `Изменить` revealed `Скрыть` and zone controls; scrolling the expanded block exposed `Энергия`, `Лёгкая`, `Средняя`, `Бодрая`, `Время`, `3 мин`, `5 мин` and `10 мин`.
- The refreshed Play screenshot `screenshots/play-store/02-home.png` was captured from the real app UI at 1080x2400.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android16_home_filter_disclosure_qa_2026_06_06.md` and `qa/emulator-android16-home-filter-disclosure-qa-2026-06-06`.

## Выполненный Android 15 Home Filter Whole-Row QA

- Android 15/API 35 AVD, serial `emulator-5554`.
- Fresh debug install on 1080x2400, density 420, font scale 1.0.
- Collapsed Home was captured after making `Настроить подбор` a whole-row 56dp toggle.
- Tapping the `Настроить подбор` summary text, not the old small `Изменить` label, opened the expanded filter state.
- The refreshed Play screenshot `screenshots/play-store/02-home.png` was captured from the real app UI at 1080x2400.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_home_filter_whole_row_qa_2026_06_06.md` and `qa/emulator-android15-home-filter-whole-row-qa-2026-06-06`.

## Выполненный Android 15 Home Filter Chevron QA

- Android 15/API 35 AVD, serial `emulator-5554`.
- Fresh debug install on 1080x2400, density 420, font scale 1.0.
- Collapsed Home was captured after adding the `Изменить`/`Скрыть` chevron indicator.
- Tapping the `Настроить подбор` summary text opened the expanded filter state while preserving the whole-row 56dp toggle behavior.
- The refreshed Play screenshot `screenshots/play-store/02-home.png` was captured from the real app UI at 1080x2400.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_home_filter_chevron_qa_2026_06_06.md` and `qa/emulator-android15-home-filter-chevron-qa-2026-06-06`.

## Выполненный Android 16 Home Filter Unframed Summary QA

- Android 16/API 36 AVD `Medium_Phone_API_36`, serial `emulator-5554`.
- Fresh debug install on 1080x2400, density 420.
- Collapsed Home was captured after replacing the raised `Настроить подбор` card with an unframed divider-row summary.
- Collapsed XML showed `Настроить подбор`, current selection summary and `Изменить`, while `Энергия` and `Время` stayed hidden.
- Tapping the whole row opened `Скрыть` and `Зона`; after scrolling, expanded XML showed `Энергия`, `Лёгкая`, `Средняя`, `Бодрая`, `Время`, `3 мин`, `5 мин` and `10 мин`.
- The refreshed Play screenshot `screenshots/play-store/02-home.png` was captured from the real app UI at 1080x2400.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android16_home_filter_unframed_summary_qa_2026_06_06.md` and `qa/emulator-android16-home-filter-unframed-summary-qa-2026-06-06`.

## Выполненный Android 16 Task Details Briefing QA

- Android 16/API 36 AVD `Medium_Phone_API_36`, serial `emulator-5554`.
- Fresh debug install on 1080x2400, density 420.
- Home `Все шаги` opened Task details from the real app flow.
- Details showed `Выбранная задача`, `Перед стартом`, `зона`, `энергия`, `время`, `После` and `Шаги`.
- After scrolling Details, `Начать 5 мин` remained reachable and opened `Таймер` with `Пауза`.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android16_task_details_briefing_qa_2026_06_06.md` and `qa/emulator-android16-task-details-briefing-qa-2026-06-06`.

## Выполненный Android 15 Task Details Unframed Briefing QA

- Android 15/API 35 AVD, serial `emulator-5554`.
- Fresh debug install on 1080x2400, density 420, font scale 1.0.
- Home `Все шаги` opened Task details from the real app flow.
- Details showed `Выбранная задача`, `выбрана`, `Перед стартом`, unframed зона/энергия/время facts, `После`, `Шаги` and pinned `Начать 5 мин`.
- Tapping `Начать 5 мин` opened `Таймер` with `Цель: 5 мин`, `Пауза` and `Готово`.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_task_details_unframed_qa_2026_06_06.md` and `qa/emulator-android15-task-details-unframed-qa-2026-06-06`.

## Выполненный Android 15 Timer Completion Dock QA

- Android 15/API 35 AVD, serial `emulator-5556`.
- Fresh debug install on 1080x2400, density 420.
- Onboarding and Home timer start were checked through ADB UI tree dumps and screenshots.
- Timer showed `Таймер`, `Пауза`, `Сброс`, `План` and the pinned bottom `Готово` action.
- The refreshed Play screenshot `screenshots/play-store/03-timer.png` was captured from the real app UI at 1080x2400.
- Crash buffer and app-specific fatal/ANR match files contained 0 lines.
- Evidence: `docs/emulator_android15_timer_completion_dock_qa_2026_06_06.md` and `qa/emulator-android15-timer-completion-dock-qa-2026-06-06`.

## Выполненный Timer Background QA

- Android 15 AVD `emulator-5554`.
- Fresh debug install and app data clear.
- Onboarding, home, 3-minute timer, background/resume, pause/resume and completion were checked through ADB UI tree dumps and screenshots.
- Timer caught up after background/resume: timer screen moved from `2:58` at start evidence to `2:28` after returning from background.
- Pause held the timer stable at `2:09` after a wait, then resume continued countdown to `2:05`.
- Result screen recorded `1` completed task, `1 дн.` streak and `1%` catalog progress.
- Crash buffer contained 0 lines.
- Evidence: `docs/emulator_timer_background_qa.md` and `qa/emulator-android15-timer-background`.

## Выполненный Timer Double-Submit QA

- Android 15 AVD `emulator-5554`.
- Fresh debug install and app data clear.
- Onboarding, home, 5-minute timer, two fast “Готово” taps, result and progress were checked through ADB UI tree dumps and screenshots.
- Result screen recorded `1` completed task, `1 дн.` streak and `1%` catalog progress after the double tap.
- Progress screen recorded one unique completed task; current UI expectation is neutral catalog copy `Отмечено задач: 1 из 80.` plus the numeric `каталог` percent metric.
- App PID fatal/exception/crash filter contained 0 lines; crash buffer contained 0 lines.
- The first attempt hit unrelated AVD focus state; unrelated packages were removed, app data/logcat were cleared and the clean rerun passed.
- Evidence: `docs/emulator_android15_timer_double_submit_qa.md` and `qa/emulator-android15-timer-double-submit`.

## Выполненный No-Internet QA

- Android 15 AVD `emulator-5554`.
- Fresh debug install and app data clear.
- Wifi and mobile data were disabled through ADB.
- `dumpsys connectivity` reported `Active default network: none`.
- Onboarding, home, 3-minute timer and result were checked through ADB UI tree dumps and screenshots.
- Result screen recorded `1` completed task, `1 дн.` streak and `1%` catalog progress.
- Crash buffer contained 0 lines.
- Evidence: `docs/emulator_no_internet_qa.md` and `qa/emulator-android15-no-internet`.

## Выполненный Android 16 Smoke QA

- Android 16/API 36 AVD `Medium_Phone_API_36`, serial `emulator-5560`.
- Fresh debug install and app data clear.
- Onboarding, home, 3-minute timer, pause/resume, completion, progress, settings and force-stop/restart persistence were checked through ADB UI tree dumps and screenshots.
- System Back from “Итоги” returned to Home after adding Compose `BackHandler` coverage.
- Result and restart screens recorded `1` completed task, `1 дн.` streak and `1%` catalog progress.
- Crash buffer contained 0 lines.
- Evidence: `docs/emulator_android16_smoke_qa.md` and `qa/emulator-android16-smoke`.

## Выполненный Android 15 Compose BOM Smoke QA

- Android 15/API 35 AVD, serial `emulator-5554`.
- Debug APK from the current Compose BOM 2026.04.01 stack.
- Onboarding, home, 5-minute timer, pause/resume, completion/result and relaunch persistence were checked through ADB UI tree dumps, screenshots and app-specific log evidence.
- Result screen recorded `1` completed task, `1 дн.` streak and `1%` catalog progress.
- The AVD had two unrelated pre-existing packages that briefly took focus during capture; `com.andrejivliev.fiftyfive` and `com.betguidepoland.app` were removed from emulator state before final clean relaunch evidence.
- App-specific error match files contained 0 lines; the final crash buffer after cleanup contained 0 lines.
- Evidence: `docs/emulator_android15_compose_bom_smoke_qa.md` and `qa/emulator-android15-compose-bom-smoke`.

## Выполненный Android 16 Compact Screen QA

- Android 16/API 36 AVD `Medium_Phone_API_36`, serial `emulator-5560`.
- Viewport temporarily overridden to `720x1280`, density `320`; baseline `1080x2400`, density `420` restored after capture.
- Onboarding, home filters, scroll to primary action, 3-minute timer, pause/resume, completion, result-to-home and settings reset-confirmation were checked through ADB UI tree dumps and screenshots.
- Primary actions below the fold were reachable by vertical scroll.
- App-filtered crash and logcat error match files contained 0 lines for `ru.poryadok5.app`.
- Evidence: `docs/emulator_android16_compact_screen_qa.md` and `qa/emulator-android16-compact-screen`.

## Выполненный Android 16 Large Screen QA

- Android 16/API 36 AVD `Medium_Phone_API_36`, serial `emulator-5560`.
- Viewport temporarily overridden to `2000x2560`, density `320`; baseline `1080x2400`, density `420` restored after capture.
- Onboarding, home, 3-minute timer, result-to-home and settings were checked through ADB UI tree dumps and screenshots.
- Main content and top bars were centered with max-width constraints instead of stretching edge-to-edge.
- Crash buffer contained 0 lines; app-filtered crash/logcat error match files contained 0 lines.
- Evidence: `docs/emulator_android16_large_screen_qa.md` and `qa/emulator-android16-large-screen`.

## Выполненный Android 16 Large Font QA

- Android 16/API 36 AVD `Medium_Phone_API_36`, serial `emulator-5560`.
- Normal phone viewport `1080x2400`, density `420`.
- System `font_scale` temporarily set to `1.3`; baseline `1.0` restored after capture.
- Onboarding, home, 3-minute timer, pause/resume, completion, progress, system Back, settings and reset-confirmation were checked through ADB UI tree dumps and screenshots.
- Primary actions remained reachable with scaled text.
- Crash buffer contained 0 lines; app-filtered crash/logcat error match files contained 0 lines.
- Evidence: `docs/emulator_android16_large_font_qa.md` and `qa/emulator-android16-large-font`.
