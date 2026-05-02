import math
from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.adversarial_complex_v2 import run

PHASE_MOD = 72


def phase_distribution(symbols):
    counts = {}
    for i, s in enumerate(symbols):
        k = i % PHASE_MOD
        counts[k] = counts.get(k, 0) + 1
    return counts


def entropy(dist):
    total = sum(dist.values())
    if total == 0:
        return 0
    H = 0
    for v in dist.values():
        p = v / total
        if p > 0:
            H -= p * math.log(p, 2)
    return H


def analyze():
    result = run()
    rejects = result.get("rejects", {})

    phase_entropies = []

    # sample reconstruction from reject patterns
    for k in range(len(rejects)):
        symbols = encode_state({"left": "x", "right": "y"})
        dist = phase_distribution(symbols)
        phase_entropies.append(entropy(dist))

    avg_phase_entropy = sum(phase_entropies) / len(phase_entropies) if phase_entropies else 0

    return {
        "collision": result.get("collision"),
        "checked": result.get("checked"),
        "reject_entropy": entropy(rejects),
        "phase_entropy": avg_phase_entropy,
        "rejects": rejects
    }


if __name__ == "__main__":
    print(analyze())
