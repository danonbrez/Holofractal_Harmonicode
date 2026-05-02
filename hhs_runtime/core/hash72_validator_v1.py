PHASE_MOD = 72


def u(k: int) -> int:
    return k % PHASE_MOD


def validate_phase_ring():
    return u(72) == u(0)


def validate_full_population(symbols):
    return len(symbols) == 72 and all(s is not None for s in symbols)


def validate_closure():
    return sum(range(72)) % 72 == 0


def validate_hash72(symbols):
    return (
        validate_phase_ring()
        and validate_full_population(symbols)
        and validate_closure()
    )
