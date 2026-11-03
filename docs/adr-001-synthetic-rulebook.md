# ADR 001 — Synthetic rulebook, not real tax law

## Decision

All rules in this repo are invented, with simulated jurisdiction names.

## Rationale

A portfolio demo must not present itself as tax advice or reproduce real
tax-code text. A synthetic rulebook lets the workflow — research,
validation, critique, reconciliation, gating, audit pack — be exercised
and tested without any risk that a reader mistakes demo output for a
real filing position.

## Consequence

Nothing in this repo may be used for a real return. Any real deployment
must substitute a vetted, versioned, professionally reviewed rule source
and re-run the full suite against it.
