#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_GITIGNORE_PATTERNS = (
    ".gradle/",
    "build/",
    "app/build/",
    "local.properties",
    ".DS_Store",
    "*.keystore",
    "*.jks",
    "*.p12",
    "*.pfx",
    "*.pem",
    "*.key",
    "keystore.properties",
    "signing.properties",
    ".env",
    ".env.*",
)

FORBIDDEN_FILENAMES = {
    ".env",
    "keystore.properties",
    "signing.properties",
}

FORBIDDEN_SUFFIXES = (
    ".jks",
    ".keystore",
    ".p12",
    ".pfx",
    ".pem",
    ".key",
)

SKIP_DIRS = {
    ".gradle",
    ".kotlin",
    "app/build",
    "build",
}

SKIP_TOP_LEVEL_DIR_PREFIXES = (
    "play-submission",
    "qa",
    "screenshots",
    "store-assets",
)

SKIP_APP_DIR_PREFIXES = (
    "build",
)

SAFE_EXAMPLE_VALUES = {
    "...",
    "change-me",
    "<redacted>",
    "redacted",
}

PASSWORD_ASSIGNMENT_RE = re.compile(
    r"(?:export\s+)?(?P<name>PORYADOK5_(?:KEYSTORE_PASSWORD|KEY_PASSWORD))\s*=\s*[\"']?(?P<value>[^\"'\s]+)"
)

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def should_skip(path: Path) -> bool:
    rel = relative(path)
    if any(rel == skip or rel.startswith(f"{skip}/") for skip in SKIP_DIRS):
        return True
    parts = path.relative_to(ROOT).parts
    if not parts:
        return False
    if any(
        parts[0] == prefix or parts[0].startswith(f"{prefix} ")
        for prefix in SKIP_TOP_LEVEL_DIR_PREFIXES
    ):
        return True
    if len(parts) >= 2 and parts[0] == "app":
        return any(
            parts[1] == prefix or parts[1].startswith(f"{prefix} ")
            for prefix in SKIP_APP_DIR_PREFIXES
        )
    return False


def iter_repo_files() -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        current = Path(dirpath)
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if not should_skip(current / dirname)
        ]
        for filename in filenames:
            path = current / filename
            if not should_skip(path) and path.is_file():
                files.append(path)
    return files


def text_or_none(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def check_gitignore(failures: list[str]) -> None:
    gitignore = ROOT / ".gitignore"
    if not gitignore.exists():
        failures.append(".gitignore is missing")
        return
    lines = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    for pattern in REQUIRED_GITIGNORE_PATTERNS:
        if pattern not in lines:
            failures.append(f".gitignore is missing required release hygiene pattern: {pattern}")


def check_forbidden_files(failures: list[str]) -> None:
    for path in iter_repo_files():
        name = path.name
        if name in FORBIDDEN_FILENAMES or name.startswith(".env."):
            failures.append(f"forbidden local secret/config file exists: {relative(path)}")
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden key/keystore-like file exists: {relative(path)}")


def check_secret_text(failures: list[str]) -> None:
    for path in iter_repo_files():
        text = text_or_none(path)
        if text is None:
            continue

        if PRIVATE_KEY_RE.search(text):
            failures.append(f"private key block found in text file: {relative(path)}")

        for match in PASSWORD_ASSIGNMENT_RE.finditer(text):
            value = match.group("value").strip()
            if value not in SAFE_EXAMPLE_VALUES and not value.startswith("$"):
                failures.append(
                    f"real-looking {match.group('name')} assignment found in {relative(path)}"
                )

        if path.name in {"gradle.properties", "local.properties"} and "PORYADOK5_" in text:
            failures.append(f"PORYADOK5 signing values must not be stored in {relative(path)}")


def main() -> int:
    failures: list[str] = []
    check_gitignore(failures)
    check_forbidden_files(failures)
    check_secret_text(failures)

    if failures:
        print("Release hygiene check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: release hygiene check found no keystores, private keys or real signing secret assignments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
