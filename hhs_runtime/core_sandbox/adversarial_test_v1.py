from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.enforce_wrapper_v1 import enforce_kernel
from hhs_runtime.core_sandbox.state_generator_depth5_v1 import state_generator_depth5
from hhs_runtime.core_sandbox.mutation_v1 import mutate


def run():
    seen={}
    for S in state_generator_depth5():
        S2=mutate(S)
        r=enforce_kernel(S2)
        if r.get("status")!="LOCKED":
            continue
        H=tuple(encode_state(S2))
        if H in seen and seen[H]!=S2:
            return {"collision":True}
        seen[H]=S2
    return {"collision":False,"checked":len(seen)}
