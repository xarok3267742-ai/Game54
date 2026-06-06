#!/usr/bin/env python3
from __future__ import annotations

import unittest

import check_store_listing as checker


VALID_LISTING = """# Store Listing Draft

## App Name

Порядок 5

## Short Description

Короткие задачи для порядка без большой уборки.

## Full Description

Порядок 5 помогает навести порядок маленькими шагами. Выберите зону, уровень энергии и время, получите конкретную задачу, запустите таймер и отметьте результат.

Порядок 5 не требует интернета, не показывает рекламу, не использует аналитику и не собирает персональные данные. Прогресс хранится только на устройстве.

## Release Notes

Первый release candidate: задачи, таймер и локальный прогресс.

## Screenshot Captions

- Выберите зону, энергию и время.
- Получите одну конкретную задачу.

## Search Keywords

порядок, уборка, чеклист, таймер, дом
"""


class StoreListingSelfTest(unittest.TestCase):
    def failures_for(self, text: str = VALID_LISTING, screenshot_total: int = 2) -> list[str]:
        failures, _sections, _captions = checker.store_listing_failures(text, screenshot_total=screenshot_total)
        return failures

    def assertFailureContains(self, needle: str, text: str = VALID_LISTING, screenshot_total: int = 2) -> None:
        failures = self.failures_for(text=text, screenshot_total=screenshot_total)
        self.assertTrue(
            any(needle in failure for failure in failures),
            msg=f"Expected failure containing {needle!r}; got {failures}",
        )

    def test_valid_listing_passes(self) -> None:
        self.assertEqual([], self.failures_for())

    def test_missing_required_section_fails(self) -> None:
        text = VALID_LISTING.replace("## Release Notes", "## Release")

        self.assertFailureContains("missing required section: Release Notes", text=text)

    def test_app_name_limit_fails(self) -> None:
        text = VALID_LISTING.replace("Порядок 5", "Очень длинное название приложения для проверки", 1)

        self.assertFailureContains("App Name", text=text)

    def test_full_description_repeating_short_description_fails(self) -> None:
        short = "Короткие задачи для порядка без большой уборки."
        text = VALID_LISTING.replace(
            "Порядок 5 помогает навести порядок маленькими шагами.",
            short + "\n\nПорядок 5 помогает навести порядок маленькими шагами.",
        )

        self.assertFailureContains("repeats the Short Description", text=text)

    def test_caption_count_mismatch_fails(self) -> None:
        self.assertFailureContains("Screenshot Captions has 2 items, but 3 screenshots exist", screenshot_total=3)

    def test_long_caption_fails(self) -> None:
        long_caption = "- " + ("Очень длинная подпись " * 6).strip()
        text = VALID_LISTING.replace("- Выберите зону, энергию и время.", long_caption)

        self.assertFailureContains("Screenshot caption 1", text=text)

    def test_duplicate_keywords_fail(self) -> None:
        text = VALID_LISTING.replace("порядок, уборка, чеклист, таймер, дом", "порядок, уборка, порядок, таймер, дом")

        self.assertFailureContains("duplicates", text=text)

    def test_forbidden_promotional_claim_fails(self) -> None:
        text = VALID_LISTING.replace("Порядок 5 помогает", "Гарантированно #1. Порядок 5 помогает")

        self.assertFailureContains("risky promotional", text=text)

    def test_missing_screenshots_fail(self) -> None:
        self.assertFailureContains("no PNG screenshots", screenshot_total=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
