def kernel_payload_builder(S):
    return {
        "S": 1,
        "b2": 2,
        "xy_phase": 1,
        "c": -1,
        "u": 1,
        "xy": 1,
        "yx": -1,
        "phase_symbols": S.get("symbols")
    }
