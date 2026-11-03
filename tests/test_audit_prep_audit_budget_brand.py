import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tax_accounting_agents.audit import AuditLog
from tax_accounting_agents.audit_prep import AuditPrepAgent
from tax_accounting_agents.brand_check import BLOCKLIST_HASHES, is_blocked
from tax_accounting_agents.budget import estimate_cost, validate_amount
from tax_accounting_agents.models import Finding, SyntheticReturn
from tax_accounting_agents.research import TaxResearchAgent


def _ret():
    return SyntheticReturn(
        filer_id="F-9", jurisdiction="Northland", income=80000.0,
        deductions=13000.0, credits=1000.0,
        line_items=[("wages", 80000.0)],
        notes="call jane@example.test or 555-123-4567")


def test_pack_checklist_covers_confirmed_findings():
    findings = [Finding("deduction-over-cap", "warning", "over", "confirmed"),
                Finding("high-deduction-ratio", "info", "ratio", "refuted")]
    pack = AuditPrepAgent().build_pack(
        _ret(), findings, TaxResearchAgent().research_topics(
            ["standard-deduction"], "Northland"))
    assert pack["confirmed_count"] == 1 and pack["unconfirmed_count"] == 1
    assert any("deduction-over-cap" in item for item in pack["checklist"])


def test_pack_summary_is_pii_free():
    pack = AuditPrepAgent().build_pack(_ret(), [], [])
    assert "jane@example.test" not in pack["redacted_summary"]
    assert "555-123-4567" not in pack["redacted_summary"]
    assert "REDACTED" in pack["redacted_summary"]


def test_pack_clean_return_note():
    pack = AuditPrepAgent().build_pack(_ret(), [], [])
    assert pack["checklist"] == ["No confirmed findings; pack is a clean review record."]


# Audit chain
def test_audit_chain_verifies():
    log = AuditLog()
    log.append("orchestrator", "step-a")
    log.append("validator", "step-b")
    assert log.verify() is True


def test_audit_chain_detects_tampering():
    log = AuditLog()
    log.append("orchestrator", "step-a")
    log.entries[0]["entry"]["action"] = "forged"
    assert log.verify() is False


def test_audit_chain_detects_dropped_entry():
    log = AuditLog()
    log.append("a", "one")
    log.append("b", "two")
    log.entries.pop(0)
    assert log.verify() is False


# Budget
def test_budget_rejects_negative_amount():
    try:
        validate_amount(-1.0, "filing cost")
    except ValueError:
        pass
    else:
        raise AssertionError("negative amount must be rejected")


def test_budget_rejects_negative_line_item():
    try:
        estimate_cost([("review", 10.0), ("filing", -5.0)])
    except ValueError:
        pass
    else:
        raise AssertionError("negative line item must be rejected")


def test_budget_zero_allowed_and_sums():
    assert estimate_cost([("a", 10.0), ("b", 0.0)]) == 10.0


def test_budget_rejects_non_number():
    try:
        validate_amount("ten")
    except ValueError:
        pass
    else:
        raise AssertionError("non-number must be rejected")


# Brand check
def test_brand_blocklist_is_non_empty():
    assert len(BLOCKLIST_HASHES) > 0


def test_brand_check_blocks_hashed_token_via_custom_list():
    custom = {hashlib.sha256("exampleblockedtoken".encode()).hexdigest()}
    assert is_blocked("ExampleBlockedToken", blocklist=custom) is True
    assert is_blocked("Alderfen Ledger", blocklist=custom) is False


def test_fictional_name_not_blocked_by_default_list():
    assert is_blocked("Alderfen Ledger") is False
