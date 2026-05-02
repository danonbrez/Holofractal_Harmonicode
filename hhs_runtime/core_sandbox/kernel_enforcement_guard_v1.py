# HARD KERNEL ENFORCEMENT GUARD
# Ensures no bypass of kernel-issued phase_symbols


def require_kernel_symbols(result):
    if result.get("status") != "LOCKED":
        return result

    if "phase_symbols" not in result:
        return {
            "status": "QUARANTINED",
            "reason": "kernel_symbol_bypass_detected"
        }

    return result
