def state_generator():
    base = ["x", "y", "z", "w"]

    for a in base:
        for b in base:
            yield {"left": a, "right": b}
