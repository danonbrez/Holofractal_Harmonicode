def collision_search(state_generator, encode, enforce_kernel):
    seen = {}

    for S in state_generator():

        result = enforce_kernel(S)

        if result.get("status") != "LOCKED":
            continue

        H = tuple(encode(S))

        if H in seen:
            if seen[H] != S:
                return {
                    "collision": True,
                    "state_1": seen[H],
                    "state_2": S,
                    "hash": H,
                }

        seen[H] = S

    return {"collision": False, "checked": len(seen)}
