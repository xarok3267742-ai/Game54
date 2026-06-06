# Release Hygiene

## Scope

This project must not store upload keystores, private keys, local signing property files or real signing passwords in the repository.

Release signing remains external and is supplied through `PORYADOK5_*` environment variables, CI secrets or a local Gradle properties file outside the project directory.

## Automated Gate

`scripts/check_release_hygiene.py` verifies:

- `.gitignore` contains release-safety patterns for local build files, `.env` files and common key/keystore extensions.
- No `.jks`, `.keystore`, `.p12`, `.pfx`, `.pem` or `.key` files exist in the checked workspace outside ignored build directories.
- No `keystore.properties`, `signing.properties`, `.env` or `.env.*` files exist in the checked workspace.
- No private key block appears in text files.
- No real-looking `PORYADOK5_KEYSTORE_PASSWORD` or `PORYADOK5_KEY_PASSWORD` assignment appears in project files. Documented example values such as `...` and `change-me` are allowed.
- `gradle.properties` and `local.properties` do not contain `PORYADOK5_*` signing values.

`scripts/check_release_hygiene_selftest.py` verifies the gate itself against clean temporary workspaces, key/keystore-like files, project signing values, real-looking password assignments, safe example assignments and private key blocks.

## Current Result

Current workspace status: `LOCAL_PROVEN`.

The upload AAB is intentionally unsigned until external signing inputs are supplied. The strict upload handoff remains controlled by `scripts/prepare_play_upload_candidate.sh` and `scripts/check_play_upload_readiness.py --require-upload-ready`.

`scripts/check_release_signing_inputs.py` is the companion preflight for external signing values. In local RC mode it passes when no signing values are present; in strict handoff mode it requires a complete external configuration and verifies the keystore alias without printing secret values.

`scripts/smoke_test_release_signing_pipeline.sh` uses a temporary keystore and isolated temporary Gradle user home outside the project to prove the Gradle signing path, signing-input preflight and packet inclusion logic. It removes the temporary keystore, restores the unsigned local RC packet, verifies that no signed AAB remains in `play-submission/release`, and rechecks the packet manifest/allowlist before exiting.
