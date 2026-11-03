import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tax_accounting_agents.jurisdictions import parallel_research, reconcile
from tax_accounting_agents.research import TaxResearchAgent

AGENT = TaxResearchAgent()


def test_research_finds_synthetic_rule():
    result = AGENT.research("standard-deduction", "Northland")
    assert len(result.rules) == 1 and result.rules[0].rule_id == "SYN-001"


def test_research_unknown_topic_is_empty():
    assert AGENT.research("no-such-topic", "Northland").rules == []


def test_research_unknown_jurisdiction_is_empty():
    assert AGENT.research("standard-deduction", "Nowhere").rules == []


def test_parallel_research_covers_all_jurisdictions():
    results = parallel_research("standard-deduction")
    assert {r.jurisdiction for r in results} == {"Northland", "Eastvale", "Southport"}
    assert all(len(r.rules) == 1 for r in results)


def test_reconcile_flags_conflicting_caps():
    result = reconcile(parallel_research("standard-deduction"))
    assert result["conflict"] is True
    assert result["caps"] == {"Northland": 12000.0, "Eastvale": 9500.0,
                              "Southport": 14000.0}


def test_reconcile_no_conflict_when_caps_agree():
    results = parallel_research("record-retention")
    # No caps at all: nothing to conflict over.
    assert reconcile(results)["conflict"] is False


def test_parallel_research_subset():
    results = parallel_research("credit-cap", ["Northland", "Eastvale"])
    assert len(results) == 2
