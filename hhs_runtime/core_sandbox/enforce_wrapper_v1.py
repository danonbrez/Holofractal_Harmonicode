from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.kernel_payload_builder_v1 import kernel_payload_builder
from hhs_runtime.core_sandbox.hhs_global_kernel_enforcer_v1 import enforce_global_kernel


def enforce_kernel(S):
    symbols = encode_state(S)

    payload = kernel_payload_builder({**S, "symbols": symbols})

    return enforce_global_kernel(S, payload)
