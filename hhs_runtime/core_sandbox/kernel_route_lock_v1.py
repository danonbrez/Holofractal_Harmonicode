# GLOBAL ROUTE LOCK
# Forces all encoding + hashing to originate from kernel output only


def extract_symbols_strict(result):
    if result.get("status") != "LOCKED":
        raise ValueError("Kernel not locked")

    if "phase_symbols" not in result:
        raise ValueError("Kernel bypass detected")

    return result["phase_symbols"]
