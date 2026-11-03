"""Hash-chained audit log: each entry commits to the previous entry's hash."""

import hashlib
import json


def _hash_entry(prev_hash, entry):
    payload = json.dumps({"prev": prev_hash, "entry": entry}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


class AuditLog:
    def __init__(self):
        self.entries = []
        self.prev_hash = "GENESIS"

    def append(self, actor, action, detail=""):
        entry = {"actor": actor, "action": action, "detail": detail}
        digest = _hash_entry(self.prev_hash, entry)
        self.entries.append({"entry": entry, "prev_hash": self.prev_hash, "hash": digest})
        self.prev_hash = digest
        return digest

    def verify(self):
        """Recompute the chain; True only if nothing was altered or dropped."""
        prev = "GENESIS"
        for record in self.entries:
            if record["prev_hash"] != prev:
                return False
            if record["hash"] != _hash_entry(prev, record["entry"]):
                return False
            prev = record["hash"]
        return prev == self.prev_hash
