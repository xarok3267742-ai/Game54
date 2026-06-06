#!/usr/bin/env python3
from __future__ import annotations

import unittest

import check_home_filter_disclosure as checker


VALID_APP = """
private val ChevronDownIcon = ImageVector.Builder(name = "ChevronDown").build()
private val ChevronUpIcon = ImageVector.Builder(name = "ChevronUp").build()

@Composable
private fun HomeScreen() {
    var filtersExpanded by rememberSaveable { mutableStateOf(false) }
    HomeFilterDisclosure(
        filter = filter,
        expanded = filtersExpanded,
        onToggle = { filtersExpanded = !filtersExpanded },
        onAreaSelected = onAreaSelected,
        onEnergySelected = onEnergySelected,
        onMinutesSelected = onMinutesSelected,
    )
}

@Composable
private fun HomeFilterDisclosure(
    filter: TaskFilter,
    expanded: Boolean,
    onToggle: () -> Unit,
    onAreaSelected: (TaskArea) -> Unit,
    onEnergySelected: (EnergyLevel) -> Unit,
    onMinutesSelected: (Int) -> Unit,
) {
    if (expanded) {
    AppCard {
        HomeFilterSummaryRow(filter = filter, expanded = true, onToggle = onToggle)
        AnimatedVisibility(visible = expanded) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Зона", style = MaterialTheme.typography.titleMedium)
                AreaSelector(filter.area, onAreaSelected)
                Text("Энергия", style = MaterialTheme.typography.titleMedium)
                Text("Время", style = MaterialTheme.typography.titleMedium)
                SupportedTaskMinutes.forEach { minutes -> Text("$minutes мин") }
            }
        }
    }
    } else {
        Column(modifier = Modifier.fillMaxWidth()) {
            HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)
            HomeFilterSummaryRow(
                filter = filter,
                expanded = false,
                onToggle = onToggle,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 6.dp),
            )
            HorizontalDivider(color = MaterialTheme.colorScheme.surfaceVariant)
        }
    }
}

@Composable
private fun HomeFilterSummaryRow(
    filter: TaskFilter,
    expanded: Boolean,
    onToggle: () -> Unit,
    modifier: Modifier = Modifier,
) {
        Row(
            modifier = modifier
                .defaultMinSize(minHeight = 56.dp)
                .clickable(
                    role = Role.Button,
                    onClick = onToggle,
                )
                .semantics {
                    stateDescription = if (expanded) "Подбор раскрыт" else "Подбор скрыт"
                },
        ) {
            Column {
                Text("Настроить подбор", style = MaterialTheme.typography.titleMedium)
            }
            FilterDisclosureIndicator(expanded = expanded)
        }
}

@Composable
private fun FilterDisclosureIndicator(expanded: Boolean) {
    Row(
        modifier = Modifier
            .defaultMinSize(minHeight = 48.dp)
            .padding(start = 12.dp),
    ) {
        Text(text = if (expanded) "Скрыть" else "Изменить")
        Icon(
            imageVector = if (expanded) ChevronUpIcon else ChevronDownIcon,
            contentDescription = null,
        )
    }
}

@Composable
private fun TaskDetailsScreen() {}
"""

VALID_DOCS = {
    "docs/product_spec.md": "Home показывает компактный текущий подбор лёгкой строкой и раскрывает зону/энергию/время по желанию.",
    "docs/ui_audit.md": "Home filter disclosure keeps a компактный summary with whole-row 56dp action target, шеврон and unframed collapsed row.",
    "docs/qa_test_plan.md": "check_home_filter_disclosure.py covers Home filter disclosure.",
}


class HomeFilterDisclosureSelfTest(unittest.TestCase):
    def failures(self, app: str = VALID_APP, docs: dict[str, str] | None = None) -> list[str]:
        return checker.home_filter_disclosure_failures(
            app_source=app,
            docs=VALID_DOCS if docs is None else docs,
        )

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual([], self.failures())

    def test_missing_disclosure_state_fails(self) -> None:
        broken = VALID_APP.replace(
            "    var filtersExpanded by rememberSaveable { mutableStateOf(false) }\n",
            "",
        )
        self.assertTrue(any("filtersExpanded" in failure for failure in self.failures(app=broken)))

    def test_filter_controls_before_disclosure_fail(self) -> None:
        broken = VALID_APP.replace(
            '        AnimatedVisibility(visible = expanded) {\n',
            '        Text("Зона", style = MaterialTheme.typography.titleMedium)\n'
            '        AnimatedVisibility(visible = expanded) {\n',
        )
        failures = self.failures(app=broken)
        self.assertTrue(any("appears before disclosure" in failure for failure in failures), msg=failures)

    def test_missing_toggle_copy_fails(self) -> None:
        broken = VALID_APP.replace('text = if (expanded) "Скрыть" else "Изменить"', 'text = "Изменить"')
        self.assertTrue(any("Скрыть" in failure for failure in self.failures(app=broken)))

    def test_old_text_button_toggle_fails(self) -> None:
        broken = VALID_APP.replace(
            "FilterDisclosureIndicator(expanded = expanded)",
            'TextButton(onClick = { filtersExpanded = !filtersExpanded }) { Text(if (filtersExpanded) "Скрыть" else "Изменить") }',
        )
        self.assertTrue(any("TextButton" in failure for failure in self.failures(app=broken)))

    def test_missing_chevron_icon_fails(self) -> None:
        broken = VALID_APP.replace("imageVector = if (expanded) ChevronUpIcon else ChevronDownIcon", "imageVector = ChevronDownIcon")
        self.assertTrue(any("ChevronUpIcon" in failure for failure in self.failures(app=broken)))

    def test_missing_whole_row_semantics_fails(self) -> None:
        broken = VALID_APP.replace('stateDescription = if (expanded) "Подбор раскрыт" else "Подбор скрыт"', "")
        self.assertTrue(any("stateDescription" in failure for failure in self.failures(app=broken)))

    def test_collapsed_app_card_fails(self) -> None:
        broken = VALID_APP.replace(
            "    } else {\n        Column(modifier = Modifier.fillMaxWidth()) {",
            "    } else {\n        AppCard {",
        )
        self.assertTrue(any("Collapsed Home filter summary should be unframed" in failure for failure in self.failures(app=broken)))

    def test_missing_docs_fail(self) -> None:
        docs = dict(VALID_DOCS)
        docs["docs/ui_audit.md"] = "Home filter disclosure only."
        failures = self.failures(docs=docs)
        self.assertTrue(any("компактный summary" in failure for failure in failures), msg=failures)


if __name__ == "__main__":
    unittest.main(verbosity=2)
