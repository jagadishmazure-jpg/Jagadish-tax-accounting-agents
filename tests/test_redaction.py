import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tax_accounting_agents.redaction import contains_pii, redact


def test_redacts_email():
    assert "@" not in redact("reach jane@example.test please") or "REDACTED" in redact(
        "reach jane@example.test please")
    assert "jane@example.test" not in redact("reach jane@example.test please")


def test_redacts_ssn():
    assert "123-45-6789" not in redact("ssn 123-45-6789 here")


def test_redacts_phone():
    assert "555-123-4567" not in redact("call 555-123-4567 now")


def test_redacts_card_number():
    out = redact("card 4111 1111 1111 1111 charged")
    assert "4111" not in out and "REDACTED" in out


def test_redacts_dashed_card():
    out = redact("card 4111-1111-1111-1111 charged")
    assert "4111-1111" not in out


def test_contains_pii_detects_all_four_types():
    assert contains_pii("mail jane@example.test")
    assert contains_pii("ssn 123-45-6789")
    assert contains_pii("call 555-123-4567")
    assert contains_pii("card 4111 1111 1111 1111")


def test_contains_pii_false_for_clean_text():
    assert not contains_pii("income 80000, deductions 13000")


def test_redact_is_idempotent_and_pii_free():
    once = redact("jane@example.test, 123-45-6789, 555-123-4567, 4111 1111 1111 1111")
    assert not contains_pii(once)
    assert redact(once) == once
