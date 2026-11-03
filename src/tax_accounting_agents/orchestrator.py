"""Orchestrator-worker pipeline covering prevent/detect/respond/recover,
plus governance and measurement. Human approval gates anything filing-facing.
"""

from .approvals import filing_gate
from .audit import AuditLog
from .audit_prep import AuditPrepAgent
from .jurisdictions import parallel_research, reconcile
from .research import TaxResearchAgent
from .validation import ReturnValidationAgent


class FilingPipeline:
    SCOPE = "synthetic-filing-review"

    def __init__(self):
        self.researcher = TaxResearchAgent()
        self.validator = ReturnValidationAgent()
        self.audit_prep = AuditPrepAgent()
        self.audit = AuditLog()

    def run(self, tax_return, approval=None, consent_text=None, confidence=None):
        # Prevent: research the synthetic rules before any checking.
        research = self.researcher.research_topics(
            ["standard-deduction", "credit-cap"], tax_return.jurisdiction)
        multi = parallel_research("standard-deduction")
        reconciliation = reconcile(multi)
        self.audit.append("orchestrator", "research-complete",
                         f"{len(research)} topics; conflict={reconciliation['conflict']}")
        # Detect: validate, then self-critique.
        findings = self.validator.validate_with_critique(tax_return)
        confirmed = [f for f in findings if f.status == "confirmed"]
        self.audit.append("validator", "validation-complete",
                         f"{len(confirmed)} confirmed of {len(findings)} findings")
        # Respond gate: anything filing-facing needs the human gate.
        passed, reason = filing_gate(approval, self.SCOPE, consent_text, confidence)
        self.audit.append("gate", "filing-gate", f"passed={passed}: {reason}")
        # Recover: build the audit pack regardless of gate outcome so the
        # review record exists even when filing-facing work is blocked.
        pack = self.audit_prep.build_pack(tax_return, findings, research)
        self.audit.append("audit-prep", "pack-built",
                         f"{pack['confirmed_count']} confirmed findings")
        return {
            "gate_passed": passed,
            "gate_reason": reason,
            "findings": findings,
            "confirmed_count": len(confirmed),
            "pack": pack,
            "reconciliation": reconciliation,
            "audit_chain_valid": self.audit.verify(),
            # Measurement: counts from this run only.
            "metrics": {
                "topics_researched": len(research),
                "jurisdictions_compared": len(multi),
                "findings_total": len(findings),
                "findings_confirmed": len(confirmed),
                "audit_entries": len(self.audit.entries),
            },
        }
