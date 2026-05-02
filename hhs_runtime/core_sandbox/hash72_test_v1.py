from hhs_runtime.core_sandbox.hash72_encoder_v1 import encode_state
from hhs_runtime.core_sandbox.enforce_wrapper_v1 import enforce_kernel


def run_test():
    seen={}
    for a in ["x","y","z","w"]:
        for b in ["x","y","z","w"]:
            S={"left":a,"right":b}
            r=enforce_kernel(S)
            if r.get("status")!="LOCKED":
                continue
            H=tuple(encode_state(S))
            if H in seen and seen[H]!=S:
                return {"collision":True}
            seen[H]=S
    return {"collision":False}
