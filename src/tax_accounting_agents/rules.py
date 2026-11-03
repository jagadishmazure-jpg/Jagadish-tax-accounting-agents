"""Synthetic rulebook.

These rules are invented for this demonstration. They are NOT real tax law,
do not describe any real jurisdiction, and must never be used for a real
filing. Jurisdiction names are simulated.
"""

from .models import Rule

RULEBOOK = [
    Rule("SYN-001", "Northland", "standard-deduction",
         "Synthetic standard deduction cap for the demo rulebook.", cap=12000.0),
    Rule("SYN-002", "Northland", "credit-cap",
         "Synthetic total-credit cap for the demo rulebook.", cap=3000.0),
    Rule("SYN-003", "Eastvale", "standard-deduction",
         "Synthetic standard deduction cap for the demo rulebook.", cap=9500.0),
    Rule("SYN-004", "Eastvale", "credit-cap",
         "Synthetic total-credit cap for the demo rulebook.", cap=2500.0),
    Rule("SYN-005", "Southport", "standard-deduction",
         "Synthetic standard deduction cap for the demo rulebook.", cap=14000.0),
    Rule("SYN-006", "Southport", "credit-cap",
         "Synthetic total-credit cap for the demo rulebook.", cap=4000.0),
    Rule("SYN-007", "Northland", "record-retention",
         "Synthetic retention rule: keep supporting records for the demo period."),
    Rule("SYN-008", "Eastvale", "record-retention",
         "Synthetic retention rule: keep supporting records for the demo period."),
]

JURISDICTIONS = ["Northland", "Eastvale", "Southport"]


def rules_for(jurisdiction, topic):
    return [r for r in RULEBOOK if r.jurisdiction == jurisdiction and r.topic == topic]
