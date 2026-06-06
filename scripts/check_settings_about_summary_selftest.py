#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from check_settings_about_summary import settings_about_summary_failures


DOCS = {
    "docs/product_spec.md": "Settings compact about summary Версия Каталог Данные",
    "docs/ui_audit.md": "Settings about summary Версия Каталог Данные",
    "docs/qa_test_plan.md": "check_settings_about_summary.py Settings about summary",
}


def valid_source() -> str:
    return textwrap.dedent(
        '''
        @Composable
        private fun SettingsScreen(catalogSize: Int) {
            AppCard(containerColor = BlueSoft) {
                Text("О приложении", style = MaterialTheme.typography.titleLarge)
                Text("Порядок 5", style = MaterialTheme.typography.titleMedium)
                SettingsAboutSummary(catalogSize = catalogSize)
            }
            Spacer(modifier = Modifier.height(32.dp))
        }

        @Composable
        private fun SettingsAboutSummary(catalogSize: Int) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SettingsAboutFact(
                    label = "Версия",
                    value = BuildConfig.VERSION_NAME,
                    modifier = Modifier.weight(0.85f),
                )
                SettingsAboutFact(
                    label = "Каталог",
                    value = "$catalogSize задач",
                    modifier = Modifier.weight(1f),
                )
                SettingsAboutFact(
                    label = "Данные",
                    value = "на устройстве",
                    modifier = Modifier.weight(1.35f),
                )
            }
        }

        @Composable
        private fun SettingsAboutFact(label: String, value: String, modifier: Modifier = Modifier) {
            Column(
                modifier = modifier
                    .defaultMinSize(minHeight = 56.dp)
                    .padding(horizontal = 4.dp, vertical = 6.dp),
                verticalArrangement = Arrangement.spacedBy(2.dp),
            ) {
                Text(label, style = MaterialTheme.typography.bodyMedium, color = MutedText)
                Text(value, style = MaterialTheme.typography.labelLarge, color = Sage)
            }
        }

        @Composable
        private fun PrivacyBadgeGrid() {}
        '''
    )


class SettingsAboutSummaryCheckTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(settings_about_summary_failures(valid_source(), DOCS), [])

    def test_missing_summary_call_fails(self) -> None:
        source = valid_source().replace("SettingsAboutSummary(catalogSize = catalogSize)", "")

        failures = settings_about_summary_failures(source, DOCS)

        self.assertTrue(any("SettingsAboutSummary(catalogSize = catalogSize)" in failure for failure in failures))

    def test_long_paragraph_fails(self) -> None:
        source = valid_source().replace(
            "SettingsAboutSummary(catalogSize = catalogSize)",
            'Text("Локальный каталог из $catalogSize микрозадач для дома, рабочего места, кухни, личных вещей и цифрового порядка.")',
        )

        failures = settings_about_summary_failures(source, DOCS)

        self.assertTrue(any("long paragraph" in failure for failure in failures))

    def test_missing_data_fact_fails(self) -> None:
        source = valid_source().replace('label = "Данные"', 'label = "Хранение"')

        failures = settings_about_summary_failures(source, DOCS)

        self.assertTrue(any('label = "Данные"' in failure for failure in failures))

    def test_framed_fact_fails(self) -> None:
        source = valid_source().replace("Column(", "Surface(\n        Column(", 1)

        failures = settings_about_summary_failures(source, DOCS)

        self.assertTrue(any("unframed" in failure for failure in failures))

    def test_missing_docs_fail(self) -> None:
        docs = dict(DOCS)
        docs["docs/product_spec.md"] = "Settings"

        failures = settings_about_summary_failures(valid_source(), docs)

        self.assertTrue(any("docs/product_spec.md" in failure for failure in failures))

    def test_missing_app_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.kt"

            failures = settings_about_summary_failures(app_path=missing, root=root)

        self.assertTrue(any("missing app file" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
