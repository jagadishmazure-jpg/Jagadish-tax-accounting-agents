"""ReturnValidationAgent with a self-critique loop.

First pass produces tentative findings. The critique pass re-checks every
finding against the synthetic return and the synthetic rulebook, confirming
only findings that still hold and refuting the rest. Nothing filing-facing
may use a merely tentative finding.
"""

from .models import Finding
from .rules import rules_for


def _cap(jurisdiction, topic):
    rules = rules_for(jurisdiction, topic)
    return rules[0].cap if rules and rules[0].cap is not None else None


class ReturnValidationAgent:
    def validate(self, tax_return):
        findings = []
        if not tax_return.filer_id:
            findings.append(Finding("missing-filer", "error", "Filer id is missing."))
        if tax_return.income < 0:
            findings.append(Finding("negative-income", "error", "Income is negative."))
        line_total = sum(amount for _, amount in tax_return.line_items)
        if tax_return.line_items and abs(line_total - tax_return.income) > 0.01:
            findings.append(Finding(
                "arithmetic-mismatch", "error",
                f"Line items sum to {line_total:.2f} but income is "
                f"{tax_return.income:.2f}."))
        cap = _cap(tax_return.jurisdiction, "standard-deduction")
        if cap is not None and tax_return.deductions > cap:
            findings.append(Finding(
                "deduction-over-cap", "warning",
                f"Deductions {tax_return.deductions:.2f} exceed the synthetic "
                f"cap {cap:.2f}."))
        credit_cap = _cap(tax_return.jurisdiction, "credit-cap")
        if credit_cap is not None and tax_return.credits > credit_cap:
            findings.append(Finding(
                "credit-over-cap", "warning",
                f"Credits {tax_return.credits:.2f} exceed the synthetic "
                f"cap {credit_cap:.2f}."))
        # Tentative heuristic: high deduction ratio is flagged for critique,
        # never asserted outright.
        if tax_return.income > 0 and tax_return.deductions / tax_return.income > 0.9:
            findings.append(Finding(
                "high-deduction-ratio", "info",
                "Deductions exceed 90% of income; flagged for review."))
        return findings

    def self_critique(self, findings, tax_return):
        """Re-check each finding; confirm what still holds, refute the rest."""
        reviewed = []
        for finding in findings:
            if finding.check == "arithmetic-mismatch":
                line_total = sum(a for _, a in tax_return.line_items)
                holds = abs(line_total - tax_return.income) > 0.01
            elif finding.check == "deduction-over-cap":
                cap = _cap(tax_return.jurisdiction, "standard-deduction")
                holds = cap is not None and tax_return.deductions > cap
            elif finding.check == "credit-over-cap":
                cap = _cap(tax_return.jurisdiction, "credit-cap")
                holds = cap is not None and tax_return.credits > cap
            elif finding.check == "missing-filer":
                holds = not tax_return.filer_id
            elif finding.check == "negative-income":
                holds = tax_return.income < 0
            elif finding.check == "high-deduction-ratio":
                # A ratio alone proves nothing: refute unless another error
                # finding is also confirmed for the same return.
                holds = any(
                    f.check in ("arithmetic-mismatch", "deduction-over-cap")
                    and f.status == "confirmed" for f in reviewed)
            else:
                holds = False
            finding.status = "confirmed" if holds else "refuted"
            reviewed.append(finding)
        return reviewed

    def validate_with_critique(self, tax_return):
        return self.self_critique(self.validate(tax_return), tax_return)
