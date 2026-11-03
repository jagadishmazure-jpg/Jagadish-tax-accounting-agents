# Guardrails and measurement

## Guardrails

- **PII redaction checklist:** email addresses, Social Security numbers,
  phone numbers, and card numbers (13–19 digits with a Luhn check).
  Redaction is asserted on every audit-pack summary.
- **Confirmation gates:** every gate is tested on three paths — bypass
  (no approval supplied), reject (explicit "no"), and absent (no approval,
  empty consent). Low-confidence results and self-contradicting consent
  ("yes, wait, no") are tested as blocking cases.
- **Approvals:** named person, single use, exact scope, expiry. A consumed
  or expired approval cannot be reused.
- **Budgets:** any negative cost input raises an error; negatives are never
  clamped to zero silently.
- **Brand check:** the blocklist is stored as SHA-256 hashes only, and a
  test asserts it is non-empty.
- **Audit integrity:** the log is hash-chained; tampering with or dropping
  an entry breaks verification, and both cases are tested.

## Measurement (per run, not a quality claim)

Each pipeline run reports counts from that run only: topics researched,
jurisdictions compared, findings total and confirmed, audit entries, and
whether the audit chain verifies. These are regression-check numbers from
a small synthetic suite, not accuracy claims about real tax work.
