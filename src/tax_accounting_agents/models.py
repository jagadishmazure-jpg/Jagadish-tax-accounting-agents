"""Data models. All figures are synthetic and invented for demonstration."""

from dataclasses import dataclass, field


@dataclass
class SyntheticReturn:
    """A wholly fictional tax return used only to exercise the workflow."""

    filer_id: str
    jurisdiction: str
    income: float
    deductions: float
    credits: float
    line_items: list = field(default_factory=list)  # list of (label, amount)
    notes: str = ""


@dataclass
class Rule:
    rule_id: str
    jurisdiction: str
    topic: str
    summary: str
    cap: float | None = None


@dataclass
class Finding:
    check: str
    severity: str  # "info" | "warning" | "error"
    message: str
    status: str = "tentative"  # "tentative" | "confirmed" | "refuted"


@dataclass
class ResearchResult:
    jurisdiction: str
    topic: str
    rules: list
