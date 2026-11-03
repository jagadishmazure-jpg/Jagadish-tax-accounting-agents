"""Multi-jurisdiction parallel research (simulated jurisdictions).

Research for each jurisdiction runs concurrently and the results are then
reconciled: where caps differ across jurisdictions, a conflict is recorded
instead of silently picking one value.
"""

from concurrent.futures import ThreadPoolExecutor

from .research import TaxResearchAgent
from .rules import JURISDICTIONS


def parallel_research(topic, jurisdictions=None, agent=None):
    jurisdictions = list(jurisdictions or JURISDICTIONS)
    agent = agent or TaxResearchAgent()
    with ThreadPoolExecutor(max_workers=len(jurisdictions)) as pool:
        results = list(pool.map(lambda j: agent.research(topic, j), jurisdictions))
    return results


def reconcile(results):
    """Return {'caps': {jurisdiction: cap}, 'conflict': bool, 'note': str}."""
    caps = {}
    for result in results:
        for rule in result.rules:
            if rule.cap is not None:
                caps[result.jurisdiction] = rule.cap
    distinct = set(caps.values())
    conflict = len(distinct) > 1
    note = (
        "Caps differ across jurisdictions; apply each jurisdiction's own cap."
        if conflict
        else "Caps agree across jurisdictions."
    )
    return {"caps": caps, "conflict": conflict, "note": note}
