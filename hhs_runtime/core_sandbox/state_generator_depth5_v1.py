BASE=["x","y","z","w"]

def compose(a,b):
    return a+b


def state_generator_depth5():
    for a in BASE:
        for b in BASE:
            for c in BASE:
                for d in BASE:
                    for e in BASE:
                        yield {
                            "left":compose(compose(compose(a,b),c),d),
                            "right":e
                        }
