import math

from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.adversarial_complex_v2 import run

PHASE_MOD = 72


def phase_distribution(symbols):
    counts = [0] * PHASE_MOD
    for i, _ in enumerate(symbols):
        k = i % PHASE_MOD
        counts[k] += 1
    total = sum(counts)
    return [c / total if total > 0 else 0 for c in counts]


def kl_divergence(p, q):
    eps = 1e-12
    s = 0.0
    for pi, qi in zip(p, q):
        if pi > 0:
            s += pi * math.log((pi + eps) / (qi + eps), 2)
    return s


def l2_distance(p, q):
    return math.sqrt(sum((pi - qi) ** 2 for pi, qi in zip(p, q)))


def uniform_distribution(n):
    return [1.0 / n] * n


def analyze():
    result = run()
    rejects = result.get("rejects", {})

    # Reference: uniform phase distribution over 72
    ref = uniform_distribution(PHASE_MOD)

    # Sample a representative symbol stream (baseline)
    base_symbols = encode_state({"left": "x", "right": "y"})
    base_dist = phase_distribution(base_symbols)

    # Drift of baseline vs uniform
    base_kl = kl_divergence(base_dist, ref)
    base_l2 = l2_distance(base_dist, ref)

    # Aggregate drift estimate weighted by rejection counts (proxy)
    total_rejects = sum(rejects.values())
    weighted_kl = 0.0
    weighted_l2 = 0.0

    if total_rejects > 0:
        for _, count in rejects.items():
            # reuse base distribution as proxy per rejected sample
            w = count / total_rejects
            weighted_kl += w * base_kl
            weighted_l2 += w * base_l2

    return {
        "collision": result.get("collision"),
        "checked": result.get("checked"),
        "drift": {
            "kl_base_vs_uniform": base_kl,
            "l2_base_vs_uniform": base_l2,
            "kl_weighted": weighted_kl,
            "l2_weighted": weighted_l2,
        },
        "rejects": rejects,
    }


if __name__ == "__main__":
    print(analyze())
