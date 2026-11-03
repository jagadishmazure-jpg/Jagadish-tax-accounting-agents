"""Cost/budget inputs: negatives are rejected, never silently clamped."""


def validate_amount(value, name="amount"):
    if value is None:
        raise ValueError(f"{name} is required")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    if value < 0:
        raise ValueError(f"{name} must not be negative")
    return float(value)


def estimate_cost(line_items):
    """Sum validated per-item costs; any negative item rejects the estimate."""
    total = 0.0
    for label, amount in line_items:
        total += validate_amount(amount, f"cost for {label}")
    return total
