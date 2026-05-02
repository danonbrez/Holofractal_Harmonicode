# LOCKED ENCODER: forces kernel-only symbol generation

from hhs_runtime.core_sandbox.enforce_wrapper_v1 import enforce_kernel
from hhs_runtime.core_sandbox.kernel_symbol_router_v1 import get_symbols


def encode_state(S):
    result = enforce_kernel(S)
    return get_symbols(result)
