"""AuditPrepAgent: builds an audit-preparation pack from validated work.

The pack contains only redacted text. Confirmed findings become checklist
items; tentative or refuted findings are listed separately and never
presented as established problems.
"""

from .redaction import contains_pii, redact


class AuditPrepAgent:
    def build_pack(self, tax_return, findings, research_results):
        confirmed = [f for f in findings if f.status == "confirmed"]
        other = [f for f in findings if f.status != "confirmed"]
        checklist = [
            f"Resolve confirmed finding: {f.check} ({f.severity})" for f in confirmed
        ]
        if not checklist:
            checklist = ["No confirmed findings; pack is a clean review record."]
        documents = ["synthetic-return-summary", "synthetic-rule-extract"]
        documents += sorted({r.topic for r in research_results})
        summary = redact(
            f"Filer {tax_return.filer_id} in {tax_return.jurisdiction}: "
            f"income {tax_return.income:.2f}, deductions "
            f"{tax_return.deductions:.2f}. Notes: {tax_return.notes}")
        assert not contains_pii(summary), "pack summary must be PII-free"
        return {
            "filer_id": tax_return.filer_id,
            "jurisdiction": tax_return.jurisdiction,
            "checklist": checklist,
            "confirmed_count": len(confirmed),
            "unconfirmed_count": len(other),
            "documents": documents,
            "redacted_summary": summary,
        }
