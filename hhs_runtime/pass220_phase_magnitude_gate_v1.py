"""Source-locked Module 15 phase/magnitude gate continuation.
No scalar solve, commutation, or canonical VM81/Hash216 mint.
"""
COMPOSITION = "(x/2)+(a²/b²)=x⁴/a²"
CANCELLATION = "x-x=x+y=y+x=y-y=(x²-y²)-((x³y²)/b)+x/xy=xy-yx=(x/y)(y/x)-x⁴=1/(a²-b)"
EXPECTED_CHAIN = (
    "x-x", "x+y", "y+x", "y-y",
    "(x²-y²)-((x³y²)/b)+x/xy",
    "xy-yx", "(x/y)(y/x)-x⁴", "1/(a²-b)",
)

def split_ordered_equals(source: str) -> tuple[str, ...]:
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    parts = []
    start = 0
    for index, symbol in enumerate(source):
        if symbol in "([{":
            stack.append(symbol)
        elif symbol in ")]}":
            if not stack or stack.pop() != pairs[symbol]:
                raise ValueError("MISMATCHED_DELIMITER")
        elif symbol == "=" and not stack:
            if index == start or (index+1 < len(source) and source[index+1] == "="):
                raise ValueError("EMPTY_OR_DOUBLE_EQUALS")
            parts.append(source[start:index])
            start = index + 1
    if stack or start == len(source):
        raise ValueError("UNCLOSED_OR_EMPTY_GATE")
    parts.append(source[start:])
    return tuple(parts)

def candidate_gate_receipt() -> dict:
    composition = split_ordered_equals(COMPOSITION)
    chain = split_ordered_equals(CANCELLATION)
    if len(composition) != 2 or chain != EXPECTED_CHAIN:
        raise ValueError("CANONICAL_ORDER_DIVERGENCE")
    return {
        "composition_operands": composition,
        "cancellation_operands": chain,
        "composition_gates": 1,
        "cancellation_gates": len(chain)-1,
        "typed_rank_one_fraction_not_scalar_division": True,
        "preserve_ordered_commutator": "xy-yx",
        "hnan_zero_quantizer_policy": "GAIN_ONE_NO_PHASE_WRITE",
        "candidate_only": True,
        "native_vm81_admitted": False,
        "canonical_hash216_minted": False,
    }
