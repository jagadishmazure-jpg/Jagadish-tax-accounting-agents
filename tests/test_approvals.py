import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tax_accounting_agents.approvals import (
    Approval, consume_approval, filing_gate, grant_approval, parse_consent,
)

SCOPE = "synthetic-filing-review"


def test_grant_requires_named_person():
    try:
        grant_approval("  ", SCOPE)
    except ValueError:
        pass
    else:
        raise AssertionError("blank approver must be rejected")


def test_grant_requires_scope():
    try:
        grant_approval("Priya Raman", "  ")
    except ValueError:
        pass
    else:
        raise AssertionError("blank scope must be rejected")


def test_single_use_consumption():
    approval = grant_approval("Priya Raman", SCOPE)
    assert consume_approval(approval, SCOPE) is True
    assert consume_approval(approval, SCOPE) is False  # second use blocked


def test_wrong_scope_rejected():
    approval = grant_approval("Priya Raman", SCOPE)
    assert consume_approval(approval, "other-scope") is False
    assert approval.consumed is False


def test_expired_approval_rejected():
    approval = Approval("Priya Raman", SCOPE,
                        datetime.now(timezone.utc) - timedelta(minutes=1))
    assert consume_approval(approval, SCOPE) is False


def test_absent_approval_blocks_gate():
    passed, _ = filing_gate(None, SCOPE, "yes", 0.95)
    assert passed is False


def test_bypass_attempt_without_approval_fails():
    # Bypass path: caller passes no approval object at all.
    passed, reason = filing_gate(None, SCOPE, "yes, approved", 0.99)
    assert passed is False and "approval" in reason


def test_reject_consent_blocks_gate():
    approval = grant_approval("Priya Raman", SCOPE)
    passed, _ = filing_gate(approval, SCOPE, "no", 0.95)
    assert passed is False and approval.consumed is False


def test_self_contradicting_consent_is_ambiguous():
    assert parse_consent("yes, wait, no") == "ambiguous"
    assert parse_consent("yes but wait, no") == "ambiguous"


def test_self_contradicting_consent_blocks_gate():
    approval = grant_approval("Priya Raman", SCOPE)
    passed, _ = filing_gate(approval, SCOPE, "yes, wait, no", 0.95)
    assert passed is False and approval.consumed is False


def test_absent_consent_blocks_gate():
    approval = grant_approval("Priya Raman", SCOPE)
    assert filing_gate(approval, SCOPE, "", 0.95)[0] is False
    assert filing_gate(approval, SCOPE, None, 0.95)[0] is False


def test_low_confidence_blocks_gate_even_with_approval():
    approval = grant_approval("Priya Raman", SCOPE)
    passed, reason = filing_gate(approval, SCOPE, "yes", 0.5)
    assert passed is False and "confidence" in reason and approval.consumed is False


def test_valid_gate_passes_and_consumes():
    approval = grant_approval("Priya Raman", SCOPE)
    passed, _ = filing_gate(approval, SCOPE, "yes, approved", 0.9)
    assert passed is True and approval.consumed is True
