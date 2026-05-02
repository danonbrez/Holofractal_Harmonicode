from hhs_runtime.core_sandbox.adversarial_parallel_with_rejects_v1 import run


def analyze():
    result = run()

    rejects = result.get("rejects", {})
    total = sum(rejects.values()) if rejects else 0

    distribution = {}

    for k, v in rejects.items():
        if total > 0:
            distribution[k] = {
                "count": v,
                "ratio": v / total
            }
        else:
            distribution[k] = {
                "count": v,
                "ratio": 0
            }

    return {
        "collision": result.get("collision"),
        "checked": result.get("checked"),
        "distribution": distribution
    }


if __name__ == "__main__":
    print(analyze())
