"""Synthetic tax-filing workflow agents (demonstration only, no real tax advice)."""

from .models import Finding, Rule, SyntheticReturn
from .research import TaxResearchAgent
from .validation import ReturnValidationAgent
from .audit_prep import AuditPrepAgent
from .orchestrator import FilingPipeline

__all__ = [
    "Finding",
    "Rule",
    "SyntheticReturn",
    "TaxResearchAgent",
    "ReturnValidationAgent",
    "AuditPrepAgent",
    "FilingPipeline",
]
