"""Demo: runs the pipeline on a synthetic return and prints run numbers."""

from .approvals import grant_approval
from .models import SyntheticReturn
from .orchestrator import FilingPipeline


def run_demo():
    tax_return = SyntheticReturn(
        filer_id="DEMO-FILER-001",
        jurisdiction="Northland",
        income=80000.0,
        deductions=13000.0,  # over the synthetic Northland cap of 12000
        credits=1000.0,
        line_items=[("wages", 50000.0), ("other", 30000.0)],
        notes="Demo return; contact demo@example.test, card 4111 1111 1111 1111.",
    )
    approval = grant_approval("Priya Raman", FilingPipeline.SCOPE)
    result = FilingPipeline().run(
        tax_return, approval=approval, consent_text="yes, approved", confidence=0.9)
    print(f"gate_passed={result['gate_passed']}")
    print(f"confirmed_findings={result['confirmed_count']}")
    print(f"findings_total={result['metrics']['findings_total']}")
    print(f"jurisdictions_compared={result['metrics']['jurisdictions_compared']}")
    print(f"reconciliation_conflict={result['reconciliation']['conflict']}")
    print(f"pack_checklist_items={len(result['pack']['checklist'])}")
    print(f"audit_entries={result['metrics']['audit_entries']}")
    print(f"audit_chain_valid={result['audit_chain_valid']}")
    print(f"redacted_summary={result['pack']['redacted_summary']}")
    return result


if __name__ == "__main__":
    run_demo()
