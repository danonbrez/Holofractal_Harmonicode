def project_to_72_phase(S):
    left = S.get("left", "x")
    right = S.get("right", "y")

    base = [left, right, left+right, right+left]

    symbols = []
    for k in range(72):
        symbols.append(base[k % 4])

    return symbols


def encode_state(S):
    return project_to_72_phase(S)
