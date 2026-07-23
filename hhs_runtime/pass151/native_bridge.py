from __future__ import annotations
from pathlib import Path
from .common import append_jsonl, sha256_text, canonical_json
REQUIRED=("claim_id","input_commitment","constraint_root","runtime_version","operator_registry_root","ordered_execution_trace_root","pre_state_commitment","post_state_commitment","result_commitment","hash72_receipt","hash216_evidence_reference","replay_receipt")
class RuntimeNativeValidationBridge:
    def __init__(self,path:str|Path): self.path=Path(path)
    def submit(self,claim:dict)->dict:
        missing=[k for k in REQUIRED if not claim.get(k)]
        if missing: return {"accepted":False,"classification":"PASS_151_NATIVE_VALIDATION_UNAVAILABLE","missing":missing}
        record={"schema":"HHS_PASS151_NATIVE_CLAIM_V1",**claim,"record_root":sha256_text(canonical_json(claim)),"classification":"STRUCTURALLY_COMPLETE_PENDING_VM81_REPLAY"}
        append_jsonl(self.path,record); return {"accepted":True,"classification":record["classification"],"record_root":record["record_root"]}
