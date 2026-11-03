"""Print the real test total by collecting (not running) the suite."""

import subprocess
import sys

out = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
    capture_output=True, text=True, cwd=__file__.rsplit("/scripts/", 1)[0])
print(out.stdout)
print(out.stderr, file=sys.stderr)
