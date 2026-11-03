import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tax_accounting_agents.models import SyntheticReturn
from tax_accounting_agents.validation import ReturnValidationAgent

AGENT = ReturnValidationAgent()


def _ret(**over):
    base = dict(filer_id="F-1", jurisdiction="Northland", income=80000.0,
                deductions=5000.0, credits=1000.0,
                line_items=[("wages", 50000.0), ("other", 30000.0)])
    base.update(over)
    return SyntheticReturn(**base)


def test_clean_return_has_no_confirmed_findings():
    findings = AGENT.validate_with_critique(_ret())
    assert [f for f in findings if f.status == "confirmed"] == []


def test_arithmetic_mismatch_confirmed():
    findings = AGENT.validate_with_critique(_ret(line_items=[("wages", 100.0)]))
    assert any(f.check == "arithmetic-mismatch" and f.status == "confirmed"
               for f in findings)


def test_deduction_over_cap_confirmed():
    findings = AGENT.validate_with_critique(_ret(deductions=13000.0))
    assert any(f.check == "deduction-over-cap" and f.status == "confirmed"
               for f in findings)


def test_credit_over_cap_confirmed():
    findings = AGENT.validate_with_critique(_ret(credits=9999.0))
    assert any(f.check == "credit-over-cap" and f.status == "confirmed"
               for f in findings)


def test_missing_filer_confirmed():
    findings = AGENT.validate_with_critique(_ret(filer_id=""))
    assert any(f.check == "missing-filer" and f.status == "confirmed" for f in findings)


def test_negative_income_confirmed():
    findings = AGENT.validate_with_critique(_ret(income=-5.0, line_items=[]))
    assert any(f.check == "negative-income" and f.status == "confirmed" for f in findings)


def test_self_critique_refutes_lone_ratio_flag():
    # Ratio flag alone, with no confirmed error, must be refuted by critique.
    findings = AGENT.validate_with_critique(
        _ret(income=10000.0, deductions=9500.0, line_items=[("wages", 10000.0)]))
    ratio = [f for f in findings if f.check == "high-deduction-ratio"]
    assert ratio and ratio[0].status == "refuted"


def test_first_pass_findings_are_tentative():
    findings = AGENT.validate(_ret(deductions=13000.0))
    assert all(f.status == "tentative" for f in findings)


def test_critique_never_leaves_tentative():
    findings = AGENT.validate_with_critique(_ret(deductions=13000.0, credits=9999.0))
    assert all(f.status in ("confirmed", "refuted") for f in findings)


def test_cap_boundary_not_flagged():
    findings = AGENT.validate_with_critique(_ret(deductions=12000.0))
    assert not any(f.check == "deduction-over-cap" for f in findings)
