def get_symbols(result):
    if result.get("status") != "LOCKED":
        raise ValueError("Kernel not locked")

    if "phase_symbols" not in result:
        raise ValueError("Missing kernel-issued symbols")

    return result["phase_symbols"]
