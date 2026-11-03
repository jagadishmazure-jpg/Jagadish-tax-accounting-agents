# Implementation guide

## Run

```bash
python3 -m pytest tests/ -q
PYTHONPATH=src python3 -m tax_accounting_agents.demo
```

No third-party dependencies; Python 3.12 standard library only.

## Adopting this pattern

1. Replace `rules.py` with a versioned rule source you control, and store
   the rule version with every pipeline run.
2. Keep the critique pass: any finding used downstream must carry status
   `confirmed`, never `tentative`.
3. Keep the gate in front of every filing-facing step, with named-person
   approvals and an expiry you can defend.
4. Redact before the audit pack is stored or shown, and assert the pack
   summary is PII-free in tests.
5. Never connect this demo to a real filing system or real taxpayer data
   without a full review by qualified tax professionals.

## Threat model (summary)

- **Prompt/data injection via return notes:** notes are treated as data,
  redacted, and never executed; no language-model calls exist in this repo.
- **Approval forgery or replay:** approvals are single-use, scoped, and
  expiring; reuse and wrong-scope use are tested as failures.
- **Audit tampering:** hash chaining detects altered or dropped entries.
- **PII leakage into packs/logs:** redaction covers email, SSN, phone, and
  card numbers, and the pack asserts a PII-free summary.
- **Silent jurisdiction mix-ups:** parallel-research reconciliation flags
  cap conflicts instead of picking one value.
