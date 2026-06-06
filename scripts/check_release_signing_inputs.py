#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_NAMES = (
    "PORYADOK5_KEYSTORE_PATH",
    "PORYADOK5_KEYSTORE_PASSWORD",
    "PORYADOK5_KEY_ALIAS",
    "PORYADOK5_KEY_PASSWORD",
)
USER_GRADLE_PROPERTIES = Path.home() / ".gradle" / "gradle.properties"
PROJECT_GRADLE_PROPERTIES = ROOT / "gradle.properties"


@dataclass(frozen=True)
class SigningInput:
    value: str
    source: str


def read_properties(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def load_signing_inputs() -> dict[str, SigningInput]:
    property_sources = (
        (PROJECT_GRADLE_PROPERTIES, "project gradle.properties"),
        (user_gradle_properties(), "user gradle.properties"),
    )
    property_values: dict[str, SigningInput] = {}

    for path, label in property_sources:
        for key, value in read_properties(path).items():
            if key in INPUT_NAMES and value:
                property_values[key] = SigningInput(value=value, source=label)

    return load_signing_inputs_from(property_values)


def user_gradle_properties() -> Path:
    gradle_user_home = os.environ.get("GRADLE_USER_HOME", "").strip()
    if gradle_user_home:
        return Path(gradle_user_home).expanduser() / "gradle.properties"
    return USER_GRADLE_PROPERTIES


def load_signing_inputs_from(property_values: dict[str, SigningInput]) -> dict[str, SigningInput]:
    values: dict[str, SigningInput] = {}
    for name in INPUT_NAMES:
        if name in property_values:
            values[name] = property_values[name]
            continue
        env_value = os.environ.get(name, "").strip()
        if env_value:
            values[name] = SigningInput(value=env_value, source="environment")
    return values


def project_gradle_signing_inputs() -> list[str]:
    return sorted(
        key
        for key, value in read_properties(PROJECT_GRADLE_PROPERTIES).items()
        if key in INPUT_NAMES and value
    )


def find_keytool() -> str | None:
    explicit = os.environ.get("PORYADOK5_KEYTOOL_PATH", "").strip()
    if explicit:
        path = Path(explicit)
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
        return None

    java_home = os.environ.get("JAVA_HOME", "").strip()
    if java_home:
        candidate = Path(java_home) / "bin" / "keytool"
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)

    studio_jbr = Path("/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/keytool")
    if studio_jbr.exists() and os.access(studio_jbr, os.X_OK):
        return str(studio_jbr)

    completed = subprocess.run(
        ["/usr/bin/env", "sh", "-c", "command -v keytool"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if completed.returncode == 0 and completed.stdout.strip():
        return completed.stdout.strip()
    return None


def is_inside_project(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def verify_keystore_alias(inputs: dict[str, SigningInput], keytool: str) -> tuple[bool, str]:
    path = Path(inputs["PORYADOK5_KEYSTORE_PATH"].value).expanduser()
    store_password = inputs["PORYADOK5_KEYSTORE_PASSWORD"].value
    alias = inputs["PORYADOK5_KEY_ALIAS"].value

    command = [
        keytool,
        "-list",
        "-v",
        "-keystore",
        str(path),
        "-storepass",
        store_password,
        "-alias",
        alias,
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return False, "keytool could not open the keystore alias with the supplied store password"
    if "PrivateKeyEntry" not in completed.stdout:
        return False, "keystore alias exists but is not a PrivateKeyEntry"
    return True, "keytool verified the keystore alias as a PrivateKeyEntry"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check external Poryadok 5 release signing inputs.")
    parser.add_argument("--require", action="store_true", help="fail when signing inputs are absent")
    args = parser.parse_args()

    inputs = load_signing_inputs()
    present = sorted(inputs)
    missing = [name for name in INPUT_NAMES if name not in inputs]

    if not present:
        if args.require:
            print("FAIL: release signing inputs are not configured", file=sys.stderr)
            return 1
        print("PASS: release signing inputs are absent; local RC will remain unsigned")
        return 0

    failures: list[str] = []
    if missing:
        failures.append("partial release signing configuration: missing " + ", ".join(missing))

    keystore_input = inputs.get("PORYADOK5_KEYSTORE_PATH")
    if keystore_input is not None:
        keystore_path = Path(keystore_input.value).expanduser()
        if is_inside_project(keystore_path):
            failures.append("keystore path must be outside the project workspace")
        if not keystore_path.exists():
            failures.append("keystore file does not exist")
        elif not keystore_path.is_file():
            failures.append("keystore path is not a file")

    project_property_inputs = project_gradle_signing_inputs()
    if project_property_inputs:
        failures.append("PORYADOK5 signing values must not be stored in project gradle.properties")

    keytool = find_keytool()
    if keytool is None:
        failures.append("keytool was not found; set JAVA_HOME or PORYADOK5_KEYTOOL_PATH")

    if not failures and keytool is not None:
        verified, message = verify_keystore_alias(inputs, keytool)
        if verified:
            sources = sorted({signing_input.source for signing_input in inputs.values()})
            print(
                "PASS: release signing inputs are complete ("
                + ", ".join(sources)
                + f"); {message}"
            )
            return 0
        else:
            failures.append(message)

    if failures:
        print("Release signing input check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
