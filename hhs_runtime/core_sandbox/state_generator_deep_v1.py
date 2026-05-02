BASE=["x","y","z","w"]


def compose(a,b):
    return a+b


def state_generator_deep(depth=3):
    if depth==1:
        for a in BASE:
            for b in BASE:
                yield {"left":a,"right":b}
    else:
        for a in BASE:
            for b in BASE:
                for c in BASE:
                    for d in BASE:
                        yield {
                            "left":compose(compose(a,b),c),
                            "right":d
                        }
