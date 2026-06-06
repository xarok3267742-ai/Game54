#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

pass() {
  printf 'PASS: %s\n' "$1"
}

note() {
  printf 'NOTE: %s\n' "$1"
}

find_keytool() {
  if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/keytool" ]]; then
    printf '%s\n' "$JAVA_HOME/bin/keytool"
    return
  fi

  local studio_jbr="/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/keytool"
  if [[ -x "$studio_jbr" ]]; then
    printf '%s\n' "$studio_jbr"
    return
  fi

  command -v keytool || true
}

find_jarsigner() {
  if [[ -n "${JAVA_HOME:-}" && -x "$JAVA_HOME/bin/jarsigner" ]]; then
    printf '%s\n' "$JAVA_HOME/bin/jarsigner"
    return
  fi

  local studio_jbr="/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/jarsigner"
  if [[ -x "$studio_jbr" ]]; then
    printf '%s\n' "$studio_jbr"
    return
  fi

  command -v jarsigner || true
}

aab_is_signed() {
  local aab="$1"
  local output status
  set +e
  output="$("$JARSIGNER_BIN" -verify -verbose -certs "$aab" 2>&1)"
  status=$?
  set -e

  if [[ "$status" -eq 0 ]] &&
    printf '%s\n' "$output" | grep -q "jar verified" &&
    ! printf '%s\n' "$output" | grep -q "jar is unsigned"; then
    return 0
  fi

  if printf '%s\n' "$output" | grep -q "jar is unsigned"; then
    return 1
  fi

  printf '%s\n' "$output" >&2
  return 2
}

restore_unsigned_local_rc() {
  note "Restoring unsigned local RC bundle and packet"
  ./gradlew \
    -PPORYADOK5_KEYSTORE_PATH= \
    -PPORYADOK5_KEYSTORE_PASSWORD="" \
    -PPORYADOK5_KEY_ALIAS= \
    -PPORYADOK5_KEY_PASSWORD="" \
    bundleRelease \
    --console=plain
  env \
    -u PORYADOK5_SUPPORT_EMAIL \
    -u PORYADOK5_KEYSTORE_PATH \
    -u PORYADOK5_KEYSTORE_PASSWORD \
    -u PORYADOK5_KEY_ALIAS \
    -u PORYADOK5_KEY_PASSWORD \
    scripts/build_play_submission_packet.sh

  if aab_is_signed "app/build/outputs/bundle/release/app-release.aab"; then
    printf 'FAIL: restore left app-release.aab signed\n' >&2
    return 1
  fi
  if [[ -f play-submission/release/app-release.aab ]]; then
    printf 'FAIL: restore left signed AAB in play-submission/release\n' >&2
    return 1
  fi
  grep -qx "signed_or_configured=false" play-submission/release/artifact_status.properties || {
    printf 'FAIL: restore did not mark packet artifact status as unsigned local RC\n' >&2
    return 1
  }
  grep -qx "artifact=not_included_unsigned_local_rc" play-submission/release/artifact_status.properties || {
    printf 'FAIL: restore did not mark packet artifact as excluded unsigned local RC\n' >&2
    return 1
  }
  scripts/check_release_artifact_manifest.py || return 1
  scripts/check_play_submission_packet_contents.py || return 1
}

cleanup() {
  local status=$?
  set +e
  if [[ "${RESTORE_NEEDED:-false}" == "true" ]]; then
    restore_unsigned_local_rc
    local restore_status=$?
    if [[ "$restore_status" -ne 0 ]]; then
      status=1
    fi
  fi
  if [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]]; then
    rm -rf "$TEMP_DIR"
  fi
  exit "$status"
}

trap cleanup EXIT

KEYTOOL_BIN="$(find_keytool)"
[[ -n "$KEYTOOL_BIN" ]] || fail "keytool not found. Install JDK or set JAVA_HOME."

JARSIGNER_BIN="$(find_jarsigner)"
[[ -n "$JARSIGNER_BIN" ]] || fail "jarsigner not found. Install JDK or set JAVA_HOME."

TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/poryadok5-signing-smoke.XXXXXX")"
SMOKE_KEYSTORE="$TEMP_DIR/poryadok5-upload-smoke.jks"
SMOKE_GRADLE_USER_HOME="$TEMP_DIR/gradle-user-home"
SMOKE_ALIAS="poryadok5-upload-smoke"
SMOKE_PASSWORD="Poryadok5SmokePass123"
RESTORE_NEEDED=false

printf '== Poryadok 5 release signing pipeline smoke test ==\n'
note "Creating temporary keystore outside the project workspace"
"$KEYTOOL_BIN" -genkeypair \
  -v \
  -keystore "$SMOKE_KEYSTORE" \
  -storetype JKS \
  -storepass "$SMOKE_PASSWORD" \
  -keypass "$SMOKE_PASSWORD" \
  -alias "$SMOKE_ALIAS" \
  -keyalg RSA \
  -keysize 2048 \
  -validity 30 \
  -dname "CN=Poryadok5 Release Signing Smoke, OU=Local QA, O=Ivliev, L=Local, ST=Local, C=US" \
  >/dev/null
pass "Temporary keystore created"
mkdir -p "$SMOKE_GRADLE_USER_HOME"

env \
  GRADLE_USER_HOME="$SMOKE_GRADLE_USER_HOME" \
  PORYADOK5_KEYSTORE_PATH="$SMOKE_KEYSTORE" \
  PORYADOK5_KEYSTORE_PASSWORD="$SMOKE_PASSWORD" \
  PORYADOK5_KEY_ALIAS="$SMOKE_ALIAS" \
  PORYADOK5_KEY_PASSWORD="$SMOKE_PASSWORD" \
  scripts/check_release_signing_inputs.py --require

RESTORE_NEEDED=true

./gradlew \
  -PPORYADOK5_KEYSTORE_PATH="$SMOKE_KEYSTORE" \
  -PPORYADOK5_KEYSTORE_PASSWORD="$SMOKE_PASSWORD" \
  -PPORYADOK5_KEY_ALIAS="$SMOKE_ALIAS" \
  -PPORYADOK5_KEY_PASSWORD="$SMOKE_PASSWORD" \
  :app:printReleaseSigningStatus \
  bundleRelease \
  --console=plain

if aab_is_signed "app/build/outputs/bundle/release/app-release.aab"; then
  pass "Gradle produced a signed release AAB with temporary signing inputs"
else
  fail "Gradle did not produce a signed release AAB with temporary signing inputs"
fi

env \
  PORYADOK5_KEYSTORE_PATH="$SMOKE_KEYSTORE" \
  PORYADOK5_KEYSTORE_PASSWORD="$SMOKE_PASSWORD" \
  PORYADOK5_KEY_ALIAS="$SMOKE_ALIAS" \
  PORYADOK5_KEY_PASSWORD="$SMOKE_PASSWORD" \
  scripts/build_play_submission_packet.sh
grep -qx "signed_or_configured=true" play-submission/release/artifact_status.properties ||
  fail "packet artifact status did not mark the signed AAB as included"
[[ -f play-submission/release/app-release.aab ]] ||
  fail "signed AAB was not copied into play-submission/release"
env \
  PORYADOK5_KEYSTORE_PATH="$SMOKE_KEYSTORE" \
  PORYADOK5_KEYSTORE_PASSWORD="$SMOKE_PASSWORD" \
  PORYADOK5_KEY_ALIAS="$SMOKE_ALIAS" \
  PORYADOK5_KEY_PASSWORD="$SMOKE_PASSWORD" \
  scripts/check_release_artifact_manifest.py
scripts/check_play_submission_packet_contents.py

set +e
readiness_output="$(env \
  GRADLE_USER_HOME="$SMOKE_GRADLE_USER_HOME" \
  PORYADOK5_KEYSTORE_PATH="$SMOKE_KEYSTORE" \
  PORYADOK5_KEYSTORE_PASSWORD="$SMOKE_PASSWORD" \
  PORYADOK5_KEY_ALIAS="$SMOKE_ALIAS" \
  PORYADOK5_KEY_PASSWORD="$SMOKE_PASSWORD" \
  scripts/check_play_upload_readiness.py 2>&1)"
readiness_status=$?
set -e
printf '%s\n' "$readiness_output"
[[ "$readiness_status" -eq 0 ]] ||
  fail "signed packet readiness audit failed with temporary signing inputs"
printf '%s\n' "$readiness_output" | grep -q "PASS: release signing inputs are complete" ||
  fail "signed packet readiness audit did not verify temporary signing inputs"
if printf '%s\n' "$readiness_output" | grep -q "release signing inputs are absent"; then
  fail "signed packet readiness audit reported absent signing inputs"
fi

pass "Signed packet path works with temporary signing inputs"

printf '== Signing pipeline smoke test passed; cleanup will restore unsigned local RC ==\n'
