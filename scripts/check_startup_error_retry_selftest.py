#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from check_startup_error_retry import startup_error_retry_failures


DOCS = {
    "docs/product_spec.md": "Startup error Повторить загрузку generic Russian",
    "docs/ui_audit.md": "Startup error retry Повторить загрузку generic Russian",
    "docs/qa_test_plan.md": "check_startup_error_retry.py Startup error retry",
}


def valid_source() -> str:
    return textwrap.dedent(
        '''
        class MainActivity {
            fun onCreate() {
                var tasks by remember { mutableStateOf<List<MicroTask>?>(null) }
                var loadError by remember { mutableStateOf<String?>(null) }
                var loadAttempt by remember { mutableIntStateOf(0) }

                LaunchedEffect(taskRepository, loadAttempt) {
                    tasks = null
                    loadError = null
                    runCatching {
                        taskRepository.loadTasks()
                    }.onFailure {
                        loadError = "Не удалось прочитать локальный список задач."
                    }
                }

                StartupErrorState(
                    message = loadError.orEmpty(),
                    onRetry = { loadAttempt += 1 },
                )
            }
        }

        @Composable
        private fun StartupErrorState(message: String, onRetry: () -> Unit) {
            Text(
                    text = "Не удалось запустить приложение",
            )
            Text("Каталог хранится на устройстве. Попробуйте загрузить его ещё раз.")
            PrimaryAction("Повторить загрузку", onRetry)
        }
        '''
    )


class StartupErrorRetryCheckTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(startup_error_retry_failures(valid_source(), DOCS), [])

    def test_missing_retry_action_fails(self) -> None:
        source = valid_source().replace('PrimaryAction("Повторить загрузку", onRetry)', "")

        failures = startup_error_retry_failures(source, DOCS)

        self.assertTrue(any("Повторить загрузку" in failure for failure in failures))

    def test_technical_error_leak_fails(self) -> None:
        source = valid_source().replace(
            'loadError = "Не удалось прочитать локальный список задач."',
            "loadError = it.message",
        )

        failures = startup_error_retry_failures(source, DOCS)

        self.assertTrue(any("loadError = it.message" in failure for failure in failures))

    def test_old_error_state_fails(self) -> None:
        source = valid_source().replace("private fun StartupErrorState", "private fun ErrorState")

        failures = startup_error_retry_failures(source, DOCS)

        self.assertTrue(any("private fun ErrorState(" in failure for failure in failures))

    def test_missing_docs_fail(self) -> None:
        docs = dict(DOCS)
        docs["docs/product_spec.md"] = "Startup error"

        failures = startup_error_retry_failures(valid_source(), docs)

        self.assertTrue(any("docs/product_spec.md" in failure for failure in failures))

    def test_missing_main_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.kt"

            failures = startup_error_retry_failures(main_path=missing, root=root)

        self.assertTrue(any("missing MainActivity" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
