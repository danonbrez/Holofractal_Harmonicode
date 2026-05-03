from decimal import Decimal
from collections import defaultdict


# In-memory learning store (can later bind to verbatim DB)
_CORRECTION_MEMORY = defaultdict(lambda: {
    "increase": 0,
    "decrease": 0,
    "success": 0,
    "failure": 0
})


def record_outcome(constraint_name, direction, success):
    entry = _CORRECTION_MEMORY[constraint_name]

    if direction in ("increase", "decrease"):
        entry[direction] += 1

    if success:
        entry["success"] += 1
    else:
        entry["failure"] += 1


def get_bias(constraint_name):
    entry = _CORRECTION_MEMORY[constraint_name]

    total = entry["increase"] + entry["decrease"]

    if total == 0:
        return None

    if entry["increase"] > entry["decrease"]:
        return "increase"
    elif entry["decrease"] > entry["increase"]:
        return "decrease"

    return None


def apply_adaptive_correction(state, corrections):
    v = Decimal(state.get("v", 1))

    for name, c in corrections.items():
        suggestion = c["suggestion"]

        # learned bias overrides naive direction if available
        bias = get_bias(name)
        direction = bias if bias else suggestion

        if direction == "increase":
            v += Decimal("0.01")
        elif direction == "decrease":
            v -= Decimal("0.01")

    state["v"] = v
    return state


def record_iteration(trace, success):
    for name, c in trace.get("corrections", {}).items():
        record_outcome(name, c["suggestion"], success)