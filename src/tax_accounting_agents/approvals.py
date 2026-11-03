"""Named-person, single-use, scoped, expiring approvals + consent parsing.

A filing-facing step may proceed only when a live, unconsumed approval from a
named person covers that exact scope. Anything else is a hard stop.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

CONFIDENCE_THRESHOLD = 0.7


@dataclass
class Approval:
    approver: str  # named person, never a role placeholder alone
    scope: str
    expires_at: datetime
    consumed: bool = False

    def is_live(self, now=None):
        now = now or datetime.now(timezone.utc)
        return (not self.consumed) and bool(self.approver.strip()) and now < self.expires_at


def grant_approval(approver, scope, ttl_minutes=60):
    if not approver or not approver.strip():
        raise ValueError("approver must be a named person")
    if not scope or not scope.strip():
        raise ValueError("scope must be non-empty")
    if ttl_minutes <= 0:
        raise ValueError("ttl_minutes must be positive")
    return Approval(
        approver=approver.strip(),
        scope=scope.strip(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
    )


def consume_approval(approval, scope):
    """Consume a live approval for exactly `scope`; returns True on success."""
    if approval is None:
        return False
    if not approval.is_live():
        return False
    if approval.scope != scope:
        return False
    approval.consumed = True
    return True


def parse_consent(text):
    """Return 'approved', 'rejected', or 'ambiguous'.

    Self-contradicting input such as "yes, wait, no" is ambiguous, never
    approval. Silence / empty input is also ambiguous (absent path).
    """
    if text is None:
        return "ambiguous"
    lowered = text.strip().lower()
    if not lowered:
        return "ambiguous"
    has_yes = any(w in lowered for w in ("yes", "approve", "approved", "confirm"))
    has_no = any(w in lowered for w in ("no", "reject", "wait", "stop", "not yet"))
    if has_yes and has_no:
        return "ambiguous"
    if has_yes:
        return "approved"
    if has_no:
        return "rejected"
    return "ambiguous"


def filing_gate(approval, scope, consent_text, confidence):
    """Full gate for a filing-facing step.

    Passes only when: consent is unambiguous approval, confidence meets the
    threshold, and a live approval for the scope is consumed. Returns
    (passed, reason).
    """
    consent = parse_consent(consent_text)
    if consent != "approved":
        return False, f"consent is {consent}, not approval"
    if confidence is None or confidence < CONFIDENCE_THRESHOLD:
        return False, "confidence below threshold"
    if not consume_approval(approval, scope):
        return False, "no live approval for scope"
    return True, "gate passed"
