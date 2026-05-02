from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.enforce_wrapper_v1 import enforce_kernel
from hhs_runtime.core_sandbox.state_generator_deep_v1 import state_generator_deep


def run():
    seen={}
    for S in state_generator_deep():
        r=enforce_kernel(S)
        if r.get("status")!="LOCKED":
            continue
        H=tuple(encode_state(S))
        if H in seen and seen[H]!=S:
            return {"collision":True}
        seen[H]=S
    return {"collision":False,"checked":len(seen)}
