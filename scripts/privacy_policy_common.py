#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

PRE_PUBLICATION_CONTACT_TEXT = "Перед публикацией замените эту строку"
PRE_PUBLICATION_CONTACT_RE = re.compile(
    r'<p\s+class="contact-note">[^<]*Перед публикацией замените эту строку[^<]*</p>',
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
EMAIL_FIND_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
RESERVED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}
RESERVED_PRIVACY_HOSTS = {
    "example.com",
    "example.org",
    "example.net",
    "your-domain.example",
    "localhost",
    "127.0.0.1",
    "::1",
}
REQUIRED_PRIVACY_SNIPPETS = (
    "Порядок 5",
    "Политика конфиденциальности",
    "не собирает",
    "не передаёт",
    "персональные данные",
    "не использует рекламу",
    "аналитические SDK",
    "crash-reporting SDK",
)


class PrivacyLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.external_refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key: value or "" for key, value in attrs}
        for key in ("href", "src"):
            value = attrs_map.get(key, "")
            if value.startswith(("http://", "https://", "//")):
                self.external_refs.append(value)


def validate_support_email(value: str) -> bool:
    if not EMAIL_RE.match(value):
        return False
    domain = value.rsplit("@", 1)[1].lower()
    return domain not in RESERVED_EMAIL_DOMAINS and not domain.endswith(".example")


def validate_privacy_url(value: str) -> bool:
    if not value.startswith("https://"):
        return False
    if not re.match(r"^https://[^/\s]+\.[^/\s]+(?:/.*)?$", value):
        return False
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    return host not in RESERVED_PRIVACY_HOSTS and not host.endswith(".example")


def extract_visible_text(markup: str) -> str:
    without_blocks = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup)
    without_tags = re.sub(r"(?s)<[^>]+>", " ", without_blocks)
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


def find_valid_support_emails(markup: str) -> list[str]:
    visible_text = extract_visible_text(markup)
    emails = sorted(set(EMAIL_FIND_RE.findall(visible_text)))
    return [email for email in emails if validate_support_email(email)]


def build_contact_paragraph(support_email: str) -> str:
    safe_email = html.escape(support_email, quote=True)
    return (
        '<p class="contact-note">Контактный email разработчика: '
        f'<a href="mailto:{safe_email}">{safe_email}</a></p>'
    )


def render_publishable_policy(source_html: str, support_email: str) -> str:
    contact_paragraph = build_contact_paragraph(support_email)
    rendered, replacements = PRE_PUBLICATION_CONTACT_RE.subn(contact_paragraph, source_html, count=1)
    if replacements == 1:
        return rendered
    if PRE_PUBLICATION_CONTACT_TEXT in source_html:
        raise ValueError("contact paragraph could not be replaced")
    if support_email in extract_visible_text(source_html):
        return source_html
    raise ValueError("source policy lacks the pre-publication instruction and the requested support email")


def validate_publishable_policy(markup: str, support_email: str = "") -> list[str]:
    failures: list[str] = []
    visible_text = extract_visible_text(markup)

    if PRE_PUBLICATION_CONTACT_TEXT in visible_text:
        failures.append("publishable privacy policy still contains the pre-publication contact instruction")

    for snippet in REQUIRED_PRIVACY_SNIPPETS:
        if snippet not in visible_text:
            failures.append(f"publishable privacy policy is missing text: {snippet}")

    parser = PrivacyLinkParser()
    parser.feed(markup)
    if parser.external_refs:
        failures.append(f"publishable privacy policy contains external references: {parser.external_refs}")

    if support_email:
        if not validate_support_email(support_email):
            failures.append("support email is missing or uses a reserved domain")
        elif support_email not in visible_text:
            failures.append("publishable privacy policy does not contain the requested support email")
    elif not find_valid_support_emails(markup):
        failures.append("publishable privacy policy does not contain a valid developer support email")

    return failures
