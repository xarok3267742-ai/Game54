#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from check_screen_state_saveability import screen_state_saveability_failures

VALID_APP = """
private sealed interface AppScreen {
    data object Onboarding : AppScreen
    data object Home : AppScreen
    data object Progress : AppScreen
    data object Settings : AppScreen
    data class Details(val taskId: String) : AppScreen
    data class Timer(val taskId: String) : AppScreen
    data class Result(val taskId: String) : AppScreen
}

private val AppScreenSaver = Saver<AppScreen, String>(
    save = { screen -> screen.toRoute() },
    restore = { route -> appScreenFromRoute(route) },
)

import ru.poryadok5.app.domain.isRouteSafeTaskId

@Composable
fun PoryadokApp() {
    var screen by rememberSaveable(stateSaver = AppScreenSaver) {
        mutableStateOf<AppScreen>(AppScreen.Home)
    }
}

private fun AppScreen.toRoute(): String {
    return when (this) {
        AppScreen.Onboarding -> "onboarding"
        AppScreen.Home -> "home"
        AppScreen.Progress -> "progress"
        AppScreen.Settings -> "settings"
        is AppScreen.Details -> "details:$taskId"
        is AppScreen.Timer -> "timer:$taskId"
        is AppScreen.Result -> "result:$taskId"
    }
}

private fun appScreenFromRoute(route: String): AppScreen {
    val taskId = route.substringAfter(':', "")
    val routeTaskId = taskId.takeIf(::isRouteSafeTaskId)
    return when (route.substringBefore(':')) {
        "details" -> routeTaskId?.let(AppScreen::Details) ?: AppScreen.Home
        "timer" -> routeTaskId?.let(AppScreen::Timer) ?: AppScreen.Home
        "result" -> routeTaskId?.let(AppScreen::Result) ?: AppScreen.Home
        else -> AppScreen.Home
    }
}
"""


def assert_passes(text: str) -> None:
    with tempfile.TemporaryDirectory(prefix="poryadok5-screen-state.") as tmp_dir:
        path = Path(tmp_dir) / "PoryadokApp.kt"
        path.write_text(text, encoding="utf-8")
        failures = screen_state_saveability_failures(path)
        assert failures == [], failures


def assert_fails(text: str, expected: str) -> None:
    with tempfile.TemporaryDirectory(prefix="poryadok5-screen-state.") as tmp_dir:
        path = Path(tmp_dir) / "PoryadokApp.kt"
        path.write_text(text, encoding="utf-8")
        failures = screen_state_saveability_failures(path)
        assert any(expected in failure for failure in failures), failures


def test_valid_fixture_passes() -> None:
    assert_passes(VALID_APP)


def test_plain_remember_screen_state_fails() -> None:
    broken = VALID_APP.replace(
        "var screen by rememberSaveable(stateSaver = AppScreenSaver)",
        "var screen by remember",
    )
    assert_fails(broken, "rememberSaveable(stateSaver = AppScreenSaver)")
    assert_fails(broken, "screen state must survive Activity recreation")


def test_missing_timer_route_fails() -> None:
    broken = VALID_APP.replace('is AppScreen.Timer -> "timer:$taskId"', "")
    assert_fails(broken, 'is AppScreen.Timer -> "timer:$taskId"')


def test_missing_result_restore_fails() -> None:
    broken = VALID_APP.replace(
        '"result" -> routeTaskId?.let(AppScreen::Result) ?: AppScreen.Home',
        "",
    )
    assert_fails(broken, '"result" -> routeTaskId?.let(AppScreen::Result) ?: AppScreen.Home')


def test_missing_route_task_id_validation_fails() -> None:
    broken = VALID_APP.replace("val routeTaskId = taskId.takeIf(::isRouteSafeTaskId)", "val routeTaskId = taskId")
    assert_fails(broken, "taskId.takeIf(::isRouteSafeTaskId)")


def test_raw_nonblank_restore_fails() -> None:
    broken = VALID_APP.replace(
        '"timer" -> routeTaskId?.let(AppScreen::Timer) ?: AppScreen.Home',
        '"timer" -> taskId.takeIf(String::isNotBlank)?.let(AppScreen::Timer) ?: AppScreen.Home',
    )
    assert_fails(broken, '"timer" -> routeTaskId?.let(AppScreen::Timer) ?: AppScreen.Home')


def main() -> int:
    test_valid_fixture_passes()
    test_plain_remember_screen_state_fails()
    test_missing_timer_route_fails()
    test_missing_result_restore_fails()
    test_missing_route_task_id_validation_fails()
    test_raw_nonblank_restore_fails()
    print("PASS: screen state saveability checker self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
