import random

BASE = ["x","y","z","w"]


def mutate_complex(S):
    l = S.get("left","x")
    r = S.get("right","y")

    mode = random.randint(0,5)

    if mode == 0:
        return {"left": r+l, "right": l+r}

    if mode == 1:
        return {"left": l[::-1], "right": r[::-1]}

    if mode == 2:
        return {"left": l + random.choice(BASE), "right": r}

    if mode == 3:
        return {"left": l, "right": r + random.choice(BASE)}

    if mode == 4:
        return {
            "left": random.choice(BASE) + random.choice(BASE),
            "right": random.choice(BASE)
        }

    if mode == 5:
        return {
            "left": "".join(random.choices(BASE,k=3)),
            "right": "".join(random.choices(BASE,k=2))
        }

    return S
