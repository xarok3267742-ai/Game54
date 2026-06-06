#!/usr/bin/env python3
from __future__ import annotations

import unittest

from privacy_policy_common import (
    PRE_PUBLICATION_CONTACT_TEXT,
    build_contact_paragraph,
    render_publishable_policy,
    validate_publishable_policy,
    validate_support_email,
)

SUPPORT_EMAIL = "support@poryadok5.app"

SOURCE_POLICY = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Политика конфиденциальности — Порядок 5</title>
  <style>body {{ font-family: sans-serif; }}</style>
</head>
<body>
  <h1>Политика конфиденциальности</h1>
  <p>Порядок 5 не собирает персональные данные.</p>
  <p>Порядок 5 не передаёт персональные данные третьим лицам.</p>
  <p>Порядок 5 не использует рекламу, аналитические SDK или crash-reporting SDK.</p>
  <p class="contact-note">{PRE_PUBLICATION_CONTACT_TEXT} на реальный email разработчика.</p>
</body>
</html>
"""


class PrivacyPolicyRenderingSelfTest(unittest.TestCase):
    def test_render_replaces_pre_publication_contact_line(self) -> None:
        rendered = render_publishable_policy(SOURCE_POLICY, SUPPORT_EMAIL)

        self.assertIn(SUPPORT_EMAIL, rendered)
        self.assertIn(f"mailto:{SUPPORT_EMAIL}", rendered)
        self.assertNotIn(PRE_PUBLICATION_CONTACT_TEXT, rendered)
        self.assertEqual([], validate_publishable_policy(rendered, SUPPORT_EMAIL))

    def test_render_accepts_existing_requested_contact(self) -> None:
        source = SOURCE_POLICY.replace(
            f'<p class="contact-note">{PRE_PUBLICATION_CONTACT_TEXT} на реальный email разработчика.</p>',
            build_contact_paragraph(SUPPORT_EMAIL),
        )

        rendered = render_publishable_policy(source, SUPPORT_EMAIL)

        self.assertEqual(source, rendered)
        self.assertEqual([], validate_publishable_policy(rendered, SUPPORT_EMAIL))

    def test_render_rejects_source_without_contact_path(self) -> None:
        source = SOURCE_POLICY.replace(
            f'<p class="contact-note">{PRE_PUBLICATION_CONTACT_TEXT} на реальный email разработчика.</p>',
            '<p class="contact-note">Контактный email будет добавлен перед публикацией.</p>',
        )

        with self.assertRaises(ValueError):
            render_publishable_policy(source, SUPPORT_EMAIL)

    def test_validation_rejects_pre_publication_text(self) -> None:
        failures = validate_publishable_policy(SOURCE_POLICY, SUPPORT_EMAIL)

        self.assertTrue(
            any("pre-publication contact instruction" in failure for failure in failures),
            msg=failures,
        )

    def test_validation_rejects_external_http_reference(self) -> None:
        rendered = render_publishable_policy(SOURCE_POLICY, SUPPORT_EMAIL)
        with_external_reference = rendered.replace("</head>", '<link rel="stylesheet" href="https://cdn.poryadok5.app/policy.css"></head>')

        failures = validate_publishable_policy(with_external_reference, SUPPORT_EMAIL)

        self.assertTrue(
            any("external references" in failure for failure in failures),
            msg=failures,
        )

    def test_validation_requires_real_support_email(self) -> None:
        rendered = render_publishable_policy(SOURCE_POLICY, SUPPORT_EMAIL)
        without_email = rendered.replace(SUPPORT_EMAIL, "support@example.com")

        self.assertFalse(validate_support_email("support@example.com"))
        failures = validate_publishable_policy(without_email)

        self.assertTrue(
            any("valid developer support email" in failure for failure in failures),
            msg=failures,
        )

    def test_validation_requires_expected_support_email_when_supplied(self) -> None:
        rendered = render_publishable_policy(SOURCE_POLICY, SUPPORT_EMAIL)

        failures = validate_publishable_policy(rendered, "help@poryadok5.app")

        self.assertTrue(
            any("requested support email" in failure for failure in failures),
            msg=failures,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
