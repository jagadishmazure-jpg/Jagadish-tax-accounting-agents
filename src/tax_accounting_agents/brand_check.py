"""Brand/name check.

The blocklist is stored as SHA-256 hashes only, never as plain names, so this
repo does not repeat real brand names. `is_blocked` hashes normalized tokens
from the candidate text and compares against the hashes.
"""

import hashlib
import re

# SHA-256 hashes of real tax-product brand tokens. Names intentionally absent.
BLOCKLIST_HASHES = frozenset({
    "a37fb71ee89dec2f098f1b33eeb09b60844412f99526f99179aeb1a7cb53c3fe",
    "8123606b56085947c16ef00cc7240303b2311777a0893ab27f46c250f841cf88",
    "90144a5888027dc7d523a257df96871bdd46b8d7f600ffe03bd00bf4cfbc52d1",
    "a001fc000e9c3d111902c9532255d1e63521891e01189e602b173a3d934f21e0",
    "2bfde07e26f3847cf4c221cebdddf9464866a8a02946e544593a23667a5eee46",
    "ec236e342276a7e5422c767dbdf295bd016b598b25a81372f643fef45b22ff30",
    "d338ad8d986b7a7e70358d77b41d2d5868d57352a05556e4660326013a1ee4aa",
})


def _token_hashes(text):
    tokens = re.findall(r"[a-z0-9& ]+", text.lower())
    out = set()
    for token in tokens:
        cleaned = " ".join(token.split())
        if cleaned:
            out.add(hashlib.sha256(cleaned.encode()).hexdigest())
    return out


def is_blocked(text, blocklist=None):
    blocklist = BLOCKLIST_HASHES if blocklist is None else blocklist
    return bool(_token_hashes(text or "") & set(blocklist))
