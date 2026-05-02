from multiprocessing import Pool, cpu_count
from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.enforce_wrapper_v1 import enforce_kernel
from hhs_runtime.core_sandbox.state_generator_depth5_v1 import state_generator_depth5
from hhs_runtime.core_sandbox.mutation_complex_v2 import mutate_complex


def trial(S):
    S2 = mutate_complex(S)
    r = enforce_kernel(S2)
    if r.get("status") != "LOCKED":
        return None, None, r
    return tuple(encode_state(S2)), S2, r


def run():
    seen = {}
    rejects = {}

    states = list(state_generator_depth5())

    with Pool(cpu_count()) as p:
        results = p.map(trial, states)

    for H,S,r in results:
        if H is None:
            reason = (r or {}).get("reason","unknown")
            rejects[reason] = rejects.get(reason,0)+1
            continue

        if H in seen and seen[H] != S:
            return {"collision":True,"rejects":rejects}

        seen[H] = S

    return {"collision":False,"checked":len(seen),"rejects":rejects}


if __name__ == "__main__":
    print(run())
