# Architecture

```mermaid
flowchart TD
    R[Synthetic return] --> RES[TaxResearchAgent]
    RES --> MULTI[Parallel research: Northland, Eastvale, Southport]
    MULTI --> REC[Reconcile caps: flag conflicts]
    R --> VAL[ReturnValidationAgent: first pass]
    VAL --> CRI[Self-critique loop: confirm or refute]
    CRI --> GATE{Human gate: named, single-use,\nscoped, expiring approval}
    GATE -- blocked --> PACK[AuditPrepAgent: audit pack]
    GATE -- passed --> PACK
    PACK --> LOG[Hash-chained audit log]
    REC --> PACK
```

## Components

- **TaxResearchAgent** — reads the synthetic rulebook by topic and
  jurisdiction. No external calls, no real tax law.
- **ReturnValidationAgent** — arithmetic, cap, completeness, and ratio
  checks, followed by a self-critique pass that re-derives each finding.
- **AuditPrepAgent** — builds the audit pack from confirmed findings only,
  with a PII-redacted summary.
- **FilingPipeline (orchestrator)** — runs research, validation, critique,
  gate, and pack in order, and records every stage in the audit log.
- **Guards** — PII redaction (email, SSN, phone, card), approval gates,
  budget validation, brand-name hash check, hash-chained audit.
