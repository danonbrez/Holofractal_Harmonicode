from multiprocessing import Pool,cpu_count
from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.enforce_wrapper_v1 import enforce_kernel
from hhs_runtime.core_sandbox.state_generator_depth5_v1 import state_generator_depth5
from hhs_runtime.core_sandbox.mutation_v1 import mutate


def trial(S):
    S2=mutate(S)
    r=enforce_kernel(S2)
    if r.get("status")!="LOCKED":
        return None
    return tuple(encode_state(S2)),S2


def run():
    seen={}
    states=list(state_generator_depth5())
    with Pool(cpu_count()) as p:
        results=p.map(trial,states)

    for item in results:
        if item is None:
            continue
        H,S=item
        if H in seen and seen[H]!=S:
            return {"collision":True}
        seen[H]=S

    return {"collision":False,"checked":len(seen)}
