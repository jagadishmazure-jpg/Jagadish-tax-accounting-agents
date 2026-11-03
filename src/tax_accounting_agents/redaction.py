"""PII redaction. Checklist covers phone, SSN, card numbers, and email.

Card detection uses a digit-run pattern (13-19 digits, allowing spaces or
dashes) plus a Luhn check so ordinary long numbers are not wiped blindly.
"""

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]\d{3}[-.\s]\d{4}\b")
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")


def _luhn_ok(digits):
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _redact_cards(text):
    def repl(match):
        digits = re.sub(r"\D", "", match.group(0))
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            return "[CARD REDACTED]"
        return match.group(0)

    return CARD_RE.sub(repl, text)


def redact(text):
    """Redact email, SSN, phone, and card numbers from free text."""
    if not text:
        return text
    out = EMAIL_RE.sub("[EMAIL REDACTED]", text)
    out = SSN_RE.sub("[SSN REDACTED]", out)
    out = PHONE_RE.sub("[PHONE REDACTED]", out)
    out = _redact_cards(out)
    return out


def contains_pii(text):
    """True if any checklist pattern is still present (used by tests/gates)."""
    if not text:
        return False
    if EMAIL_RE.search(text) or SSN_RE.search(text) or PHONE_RE.search(text):
        return True
    for match in CARD_RE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            return True
    return False
