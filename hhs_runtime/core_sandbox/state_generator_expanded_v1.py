BASE=["x","y","z","w"]


def state_generator_expanded():
    for a in BASE:
        for b in BASE:
            for c in BASE:
                yield {"left":a+b,"right":c}
