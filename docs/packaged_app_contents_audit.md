# Packaged App Contents Audit

## Status

`LOCAL_PROVEN`.

## Purpose

This audit documents the local gate that inspects the built debug APK and release AAB as ZIP artifacts. It verifies that runtime package contents stay scoped to application code, Android resources, the local task catalog, launcher assets and transitive AndroidX runtime metadata.

## Automated Gate

`scripts/check_packaged_app_contents.py` validates:

- debug APK exists and is readable as a ZIP artifact;
- release AAB exists and is readable as a ZIP artifact;
- required runtime entries are present and non-empty, including manifests, dex files, resources, launcher icon resources and `tasks_ru.json`;
- AndroidX Compose/DataStore runtime metadata and native library prefixes are present where expected;
- workspace-only folders are absent from packaged artifacts: `docs/`, `qa/`, `screenshots/`, `store-assets/` and `play-submission/`;
- Play submission text and generated packet artifacts are absent from packaged artifacts;
- key/keystore-like files and local signing config filenames are absent from packaged artifacts;
- source/document file suffixes such as `.kt`, `.java`, `.rtf` and `.docx` are absent from packaged artifacts.

Current local result:

```text
PASS: packaged app contents are scoped to runtime artifacts
```

## Release Impact

This gate reduces the risk that release outputs accidentally include local QA evidence, Play listing material, store screenshots, privacy policy drafts, signing setup notes or key-like files. It complements the release hygiene workspace scan and the Play submission packet allowlist.
