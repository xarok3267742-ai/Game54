# Release Signing Setup

## Current Policy

The project supports release signing, but does not store upload keys, passwords or keystore files in the repository.

If signing values are absent, `./gradlew bundleRelease` still builds a local RC `.aab`, but it is unsigned and not ready for Play Console upload.

## Required Inputs

Provide these as Gradle properties or environment variables:

- `PORYADOK5_KEYSTORE_PATH`
- `PORYADOK5_KEYSTORE_PASSWORD`
- `PORYADOK5_KEY_ALIAS`
- `PORYADOK5_KEY_PASSWORD`

## Local Environment Example

```bash
export PORYADOK5_KEYSTORE_PATH="$HOME/secure/poryadok5-upload.jks"
export PORYADOK5_KEYSTORE_PASSWORD="..."
export PORYADOK5_KEY_ALIAS="poryadok5-upload"
export PORYADOK5_KEY_PASSWORD="..."

scripts/check_release_signing_inputs.py --require
./gradlew :app:printReleaseSigningStatus
./gradlew bundleRelease
```

## Gradle Properties Example

Use a local file that is not committed, such as `~/.gradle/gradle.properties`:

```properties
PORYADOK5_KEYSTORE_PATH=/Users/you/secure/poryadok5-upload.jks
PORYADOK5_KEYSTORE_PASSWORD=change-me
PORYADOK5_KEY_ALIAS=poryadok5-upload
PORYADOK5_KEY_PASSWORD=change-me
```

## Keystore Creation

Create the upload keystore outside the repository:

```bash
keytool -genkeypair \
  -v \
  -keystore "$HOME/secure/poryadok5-upload.jks" \
  -alias poryadok5-upload \
  -keyalg RSA \
  -keysize 4096 \
  -validity 10000
```

## Verification

After `bundleRelease`, verify the bundle:

```bash
jarsigner -verify -verbose -certs app/build/outputs/bundle/release/app-release.aab
```

Expected:

- Without signing inputs: `jar is unsigned`.
- With signing inputs: entries show verified signatures.

Before running a full signed build, use:

```bash
scripts/check_release_signing_inputs.py --require
```

The checker verifies that all four `PORYADOK5_*` signing inputs are present, the keystore file exists outside the project workspace, `keytool` can open the alias with the supplied store password, and the alias is a `PrivateKeyEntry`. It does not print passwords and does not generate or modify a keystore.

The strict Play upload readiness gate also runs this checker, so `scripts/check_play_upload_readiness.py --require-upload-ready` requires current external signing inputs as well as a signed AAB.

The checker follows the same precedence as the Gradle signing config: local Gradle properties win over environment variables, and environment variables are used only as a fallback. When `GRADLE_USER_HOME` is set, the checker reads `GRADLE_USER_HOME/gradle.properties` as Gradle's user properties file. Any `PORYADOK5_*` signing value in project `gradle.properties` is rejected even when environment variables are also set, because project-local signing values must not be committed.

To prove the Gradle signing wiring without using a real upload key, run:

```bash
scripts/smoke_test_release_signing_pipeline.sh
```

The smoke test creates a temporary keystore outside the project, builds a signed AAB, verifies that `play-submission/release/app-release.aab` is included only when the bundle is signed, then restores the normal unsigned local RC bundle and packet. The temporary keystore is deleted at the end.

For the final Play upload handoff, use:

```bash
scripts/prepare_play_upload_candidate.sh
```

That script accepts signing configured either through environment variables or through local Gradle properties. The submission packet includes `release/app-release.aab` only when the built bundle signature verifies with `jarsigner`.

## Security Notes

- Do not commit `.jks`, `.keystore`, passwords or local signing property files.
- Store the upload key in a password manager or secure backup.
- Google Play App Signing still requires a Play Console setup step before production upload.
