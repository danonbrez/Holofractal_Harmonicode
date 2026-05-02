# Global Symbol Enforcement Patch
# Replaces direct encode_state usage with kernel-routed symbol extraction

from hhs_runtime.core_sandbox.kernel_symbol_router_v1 import get_symbols
from hhs_runtime.core_sandbox.enforce_wrapper_v1 import enforce_kernel


def get_hash_from_state(S):
    result = enforce_kernel(S)

    if result.get("status") != "LOCKED":
        return None

    symbols = get_symbols(result)

    return tuple(symbols)
