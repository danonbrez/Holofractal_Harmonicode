import math
from hhs_runtime.core_sandbox.adversarial_complex_v2 import run


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

    return {
        "collision": result.get("collision"),
        "checked": result.get("checked"),
        "entropy": entropy(rejects),
        "rejects": rejects
    }


if __name__ == "__main__":
    print(analyze())
