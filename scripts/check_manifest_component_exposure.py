#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from release_identity import read_gradle_release_identity

ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
RELEASE_AAB = ROOT / "app/build/outputs/bundle/release/app-release.aab"
ALLOWED_PROVIDER = "androidx.startup.InitializationProvider"
ALLOWED_PROFILE_RECEIVER = "androidx.profileinstaller.ProfileInstallReceiver"
ALLOWED_PROFILE_RECEIVER_PERMISSION = "android.permission.DUMP"
ALLOWED_PROFILE_RECEIVER_ACTIONS = {
    "androidx.profileinstaller.action.INSTALL_PROFILE",
    "androidx.profileinstaller.action.SKIP_FILE",
    "androidx.profileinstaller.action.SAVE_PROFILE",
    "androidx.profileinstaller.action.BENCHMARK_OPERATION",
}
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def android_attr(node: ET.Element, name: str) -> str | None:
    return node.attrib.get(f"{ANDROID_NS}{name}")


def main_activity_name(package_name: str) -> str:
    return f"{package_name}.MainActivity"


def component_name(node: ET.Element, package_name: str) -> str:
    raw_name = android_attr(node, "name") or ""
    if raw_name.startswith("."):
        return f"{package_name}{raw_name}"
    if "." not in raw_name and raw_name:
        return f"{package_name}.{raw_name}"
    return raw_name


def is_true(node: ET.Element, name: str) -> bool:
    return android_attr(node, name) == "true"


def is_false(node: ET.Element, name: str) -> bool:
    return android_attr(node, name) == "false"


def child_components(application: ET.Element, tag: str) -> list[ET.Element]:
    return list(application.findall(tag))


def intent_filter_actions(component: ET.Element) -> set[str]:
    actions: set[str] = set()
    for intent_filter in component.findall("intent-filter"):
        for action in intent_filter.findall("action"):
            action_name = android_attr(action, "name")
            if action_name:
                actions.add(action_name)
    return actions


def has_launcher_filter(activity: ET.Element) -> bool:
    for intent_filter in activity.findall("intent-filter"):
        actions = {
            android_attr(action, "name")
            for action in intent_filter.findall("action")
        }
        categories = {
            android_attr(category, "name")
            for category in intent_filter.findall("category")
        }
        if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in categories:
            return True
    return False


def application_hardening_failures(application: ET.Element, label: str) -> list[str]:
    failures: list[str] = []
    if is_true(application, "debuggable"):
        failures.append(f"{label} application must not set android:debuggable=true")
    if is_true(application, "usesCleartextTraffic"):
        failures.append(f"{label} application must not set android:usesCleartextTraffic=true")
    if android_attr(application, "networkSecurityConfig"):
        failures.append(f"{label} application must not define android:networkSecurityConfig")
    if is_true(application, "requestLegacyExternalStorage"):
        failures.append(f"{label} application must not set android:requestLegacyExternalStorage=true")
    return failures


def find_application(manifest: ET.Element, label: str) -> tuple[ET.Element | None, list[str]]:
    application = manifest.find("application")
    if application is None:
        return None, [f"{label} manifest is missing <application>"]
    return application, []


def validate_source_manifest(xml_text: str, package_name: str | None = None) -> list[str]:
    package_name = package_name or str(read_gradle_release_identity()["appId"])
    expected_main_activity = main_activity_name(package_name)
    manifest = ET.fromstring(xml_text)
    failures = [
        f"source manifest must not request permission: {android_attr(permission, 'name')}"
        for permission in manifest.findall("uses-permission")
    ]

    application, app_failures = find_application(manifest, "source")
    failures.extend(app_failures)
    if application is None:
        return failures

    failures.extend(application_hardening_failures(application, "source"))

    activities = child_components(application, "activity")
    if len(activities) != 1:
        failures.append(f"source manifest must declare exactly one activity, found {len(activities)}")
    else:
        activity = activities[0]
        activity_name = component_name(activity, package_name)
        if activity_name != expected_main_activity:
            failures.append(f"source activity must be {expected_main_activity}, got {activity_name or '<missing>'}")
        if not is_true(activity, "exported"):
            failures.append("source MainActivity must set android:exported=true")
        if not has_launcher_filter(activity):
            failures.append("source MainActivity must have MAIN/LAUNCHER intent filter")

    for tag in ("service", "receiver", "provider"):
        components = child_components(application, tag)
        if components:
            names = ", ".join(component_name(component, package_name) or "<missing>" for component in components)
            failures.append(f"source manifest must not declare {tag} components: {names}")

    return failures


def validate_release_manifest(xml_text: str, package_name: str | None = None) -> list[str]:
    package_name = package_name or str(read_gradle_release_identity()["appId"])
    expected_main_activity = main_activity_name(package_name)
    manifest = ET.fromstring(xml_text)
    application, app_failures = find_application(manifest, "release AAB")
    failures = list(app_failures)
    if application is None:
        return failures

    failures.extend(application_hardening_failures(application, "release AAB"))

    activities = child_components(application, "activity")
    main_activities = [activity for activity in activities if component_name(activity, package_name) == expected_main_activity]
    if len(main_activities) != 1:
        failures.append(f"release AAB must include exactly one {expected_main_activity}, found {len(main_activities)}")
    else:
        main_activity = main_activities[0]
        if not is_true(main_activity, "exported"):
            failures.append("release AAB MainActivity must set android:exported=true")
        if not has_launcher_filter(main_activity):
            failures.append("release AAB MainActivity must have MAIN/LAUNCHER intent filter")

    unexpected_activities = [
        component_name(activity, package_name) or "<missing>"
        for activity in activities
        if component_name(activity, package_name) != expected_main_activity
    ]
    if unexpected_activities:
        failures.append(f"release AAB has unexpected activity components: {', '.join(unexpected_activities)}")

    services = child_components(application, "service")
    if services:
        names = ", ".join(component_name(service, package_name) or "<missing>" for service in services)
        failures.append(f"release AAB must not declare service components: {names}")

    providers = child_components(application, "provider")
    for provider in providers:
        name = component_name(provider, package_name)
        if name != ALLOWED_PROVIDER:
            failures.append(f"release AAB has unexpected provider component: {name or '<missing>'}")
        if name == ALLOWED_PROVIDER and not is_false(provider, "exported"):
            failures.append(f"release AAB provider {ALLOWED_PROVIDER} must set android:exported=false")

    receivers = child_components(application, "receiver")
    for receiver in receivers:
        name = component_name(receiver, package_name)
        if name != ALLOWED_PROFILE_RECEIVER:
            failures.append(f"release AAB has unexpected receiver component: {name or '<missing>'}")
            continue
        if not is_true(receiver, "exported"):
            failures.append(f"release AAB receiver {ALLOWED_PROFILE_RECEIVER} must set android:exported=true")
        if android_attr(receiver, "permission") != ALLOWED_PROFILE_RECEIVER_PERMISSION:
            failures.append(
                f"release AAB receiver {ALLOWED_PROFILE_RECEIVER} must require "
                f"{ALLOWED_PROFILE_RECEIVER_PERMISSION}"
            )
        actions = intent_filter_actions(receiver)
        if actions != ALLOWED_PROFILE_RECEIVER_ACTIONS:
            failures.append(
                "release AAB profile receiver actions must match AndroidX profile installer actions; "
                f"got {sorted(actions)}"
            )

    return failures


def find_java() -> Path | None:
    java_home = os.environ.get("JAVA_HOME")
    if java_home and (Path(java_home) / "bin/java").is_file():
        return Path(java_home) / "bin/java"

    studio_java = Path("/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin/java")
    if studio_java.is_file():
        return studio_java

    return None


def bundletool_classpath() -> str:
    jars = sorted((Path.home() / ".gradle/caches/modules-2/files-2.1").glob("**/*.jar"))
    return ":".join(str(jar) for jar in jars)


def dump_release_manifest(java: Path) -> str:
    classpath = bundletool_classpath()
    if "bundletool" not in classpath:
        raise RuntimeError("bundletool jar not found in Gradle cache.")

    result = subprocess.run(
        [
            str(java),
            "-cp",
            classpath,
            "com.android.tools.build.bundletool.BundleToolMain",
            "dump",
            "manifest",
            f"--bundle={RELEASE_AAB}",
            "--module=base",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout)
    return result.stdout


def main() -> int:
    if not SOURCE_MANIFEST.exists():
        return fail(f"Missing source manifest: {SOURCE_MANIFEST.relative_to(ROOT)}")
    if not RELEASE_AAB.exists():
        return fail(f"Missing release AAB: {RELEASE_AAB.relative_to(ROOT)}")

    try:
        release_identity = read_gradle_release_identity()
    except (OSError, ValueError) as exc:
        return fail(f"release identity could not be read from Gradle: {exc}")
    package_name = str(release_identity["appId"])

    java = find_java()
    if java is None:
        return fail("Java runtime not found. Set JAVA_HOME or install Android Studio JBR.")

    try:
        release_manifest = dump_release_manifest(java)
    except Exception as exc:
        return fail(f"bundletool manifest dump failed: {exc}")

    failures = validate_source_manifest(SOURCE_MANIFEST.read_text(encoding="utf-8"), package_name)
    failures.extend(validate_release_manifest(release_manifest, package_name))

    if failures:
        print("Manifest component exposure check failed:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print("PASS: manifest component exposure is limited to launcher activity and protected AndroidX internals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
