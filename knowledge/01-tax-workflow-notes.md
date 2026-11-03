# Tax filing workflow — distilled notes

Original notes written for this project. All examples are synthetic.

## The workflow in stages

1. **Research first.** Before any return is checked, the applicable rules are
   pulled from a rulebook. In this demo the rulebook is synthetic and
   invented; a real deployment would point at a vetted, versioned source of
   real rules and keep the version with every decision.
2. **Validate, then critique.** A first validation pass flags problems; a
   second pass re-checks each flag against the same return and rulebook.
   Flags that do not survive re-checking are marked refuted, not deleted, so
   the review record shows what was considered and why it was dropped.
3. **Reconcile across jurisdictions.** When several simulated jurisdictions
   are researched in parallel, their caps can differ. The pipeline records
   the conflict and applies each jurisdiction's own cap rather than picking
   a winner silently.
4. **Gate anything filing-facing.** A named person must approve the exact
   scope, once, before expiry. Ambiguous or self-contradicting consent never
   counts as approval, and low-confidence results are blocked even when
   consent is present.
5. **Prepare the audit pack last.** The pack lists confirmed findings as
   checklist items, keeps unconfirmed items separate, and contains only
   redacted text.

## Why the human gate sits where it does

Validation can catch arithmetic and cap problems, but it cannot take
responsibility for a filing. The gate therefore sits between detection and
any filing-facing step: everything before it is preparation, everything
after it is accountable action, and the hash-chained log ties the two sides
together.
