#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_ui_label_consistency.py"


VALID_UI = """
MetricPill("выполнено", "0", MetricTone.Sage)
MetricPill("выполнено", "1", MetricTone.Sage)
MetricPill("выполнено", "2", MetricTone.Sage)
private fun TaskCard() {
    TaskStatusPill(
        text = statusText ?: if (completed) "выполнено" else "новая",
        completed = completed,
    )
}
private fun TaskStatusPill() {
    Surface(
        modifier = Modifier.size(8.dp),
        shape = CircleShape,
    ) {}
}
"""


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_ui_label_consistency", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UiLabelConsistencySelfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def call_main(self, source: str) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ui_source = Path(tmp_dir) / "PoryadokApp.kt"
            ui_source.write_text(source, encoding="utf-8")
            with (
                mock.patch.object(self.module, "UI_SOURCE", ui_source),
                contextlib.redirect_stdout(io.StringIO()) as stdout,
                contextlib.redirect_stderr(io.StringIO()) as stderr,
            ):
                status = self.module.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_valid_ui_passes(self) -> None:
        status, stdout, stderr = self.call_main(VALID_UI)

        self.assertEqual(status, 0)
        self.assertIn("task status is non-interactive", stdout)
        self.assertEqual(stderr, "")

    def test_old_metric_label_fails(self) -> None:
        broken = VALID_UI.replace('MetricPill("выполнено"', 'MetricPill("сделано"', 1)
        status, stdout, stderr = self.call_main(broken)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn('MetricPill("сделано"', stderr)

    def test_old_completed_status_fails(self) -> None:
        broken = VALID_UI.replace('"выполнено" else "новая"', '"сделано" else "новая"')
        status, stdout, stderr = self.call_main(broken)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("TaskCard completed status chip", stderr)

    def test_missing_metric_label_fails(self) -> None:
        broken = VALID_UI.replace('MetricPill("выполнено", "2", MetricTone.Sage)\n', "")
        status, stdout, stderr = self.call_main(broken)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("expected 3 aligned", stderr)

    def test_missing_status_pill_fails(self) -> None:
        broken = VALID_UI.replace("    TaskStatusPill(\n", "    Text(\n")
        status, stdout, stderr = self.call_main(broken)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("TaskCard must render status through TaskStatusPill", stderr)

    def test_button_like_status_pill_fails(self) -> None:
        broken = VALID_UI.replace(
            "        shape = CircleShape,\n",
            "        shape = CircleShape,\n"
            "        border = BorderStroke(1.dp, MaterialTheme.colorScheme.surfaceVariant),\n",
        )
        status, stdout, stderr = self.call_main(broken)

        self.assertEqual(status, 1)
        self.assertEqual(stdout, "")
        self.assertIn("TaskStatusPill must not look or behave like a button", stderr)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(UiLabelConsistencySelfTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("PASS: UI label consistency self-test")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
