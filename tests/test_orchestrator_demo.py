import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tax_accounting_agents.approvals import grant_approval
from tax_accounting_agents.demo import run_demo
from tax_accounting_agents.models import SyntheticReturn
from tax_accounting_agents.orchestrator import FilingPipeline


def _ret(**over):
    base = dict(filer_id="F-1", jurisdiction="Northland", income=80000.0,
                deductions=5000.0, credits=1000.0,
                line_items=[("wages", 50000.0), ("other", 30000.0)])
    base.update(over)
    return SyntheticReturn(**base)


def test_pipeline_gate_passes_with_valid_approval():
    approval = grant_approval("Priya Raman", FilingPipeline.SCOPE)
    result = FilingPipeline().run(_ret(), approval, "yes, approved", 0.9)
    assert result["gate_passed"] is True
    assert result["audit_chain_valid"] is True


def test_pipeline_blocks_without_approval():
    result = FilingPipeline().run(_ret(), None, "yes", 0.95)
    assert result["gate_passed"] is False
    # Pack is still built: recovery record exists even when blocked.
    assert result["pack"]["confirmed_count"] == 0


def test_pipeline_blocks_on_self_contradicting_consent():
    approval = grant_approval("Priya Raman", FilingPipeline.SCOPE)
    result = FilingPipeline().run(_ret(), approval, "yes, wait, no", 0.95)
    assert result["gate_passed"] is False


def test_pipeline_blocks_on_low_confidence():
    approval = grant_approval("Priya Raman", FilingPipeline.SCOPE)
    result = FilingPipeline().run(_ret(), approval, "yes", 0.4)
    assert result["gate_passed"] is False


def test_pipeline_reports_confirmed_finding_and_conflict():
    approval = grant_approval("Priya Raman", FilingPipeline.SCOPE)
    result = FilingPipeline().run(_ret(deductions=13000.0), approval, "yes", 0.9)
    assert result["confirmed_count"] == 1
    assert result["reconciliation"]["conflict"] is True
    assert result["metrics"]["jurisdictions_compared"] == 3


def test_pipeline_metrics_match_counts():
    approval = grant_approval("Priya Raman", FilingPipeline.SCOPE)
    result = FilingPipeline().run(_ret(deductions=13000.0), approval, "yes", 0.9)
    assert result["metrics"]["findings_total"] == len(result["findings"])
    assert result["metrics"]["findings_confirmed"] == result["confirmed_count"]
    assert result["metrics"]["audit_entries"] == 4


def test_demo_numbers_are_asserted():
    result = run_demo()
    assert result["gate_passed"] is True
    assert result["confirmed_count"] == 1
    assert result["metrics"]["findings_total"] == 1
    assert result["metrics"]["jurisdictions_compared"] == 3
    assert result["reconciliation"]["conflict"] is True
    assert len(result["pack"]["checklist"]) == 1
    assert result["metrics"]["audit_entries"] == 4
    assert result["audit_chain_valid"] is True
    assert "example.test" not in result["pack"]["redacted_summary"]
