from __future__ import annotations
LEVELS=["SOURCE_PRESENT","COMPILED","LINKED","CALLABLE","EXECUTED","POSITIVE_TESTED","NEGATIVE_TESTED","REPLAYED","PERSISTED","RECOVERED","SANITIZED","PACKAGED","VERIFIED"]
class EvidenceReconciler:
    def reconcile(self,obligation:dict,evidence:dict)->dict:
        flags={k:bool(evidence.get(k.lower(),False)) for k in ("IMPLEMENTED","REACHABLE","TESTED","EVIDENCED","DEPENDENCIES_CLOSED")}
        closed=all(flags.values()) and not evidence.get("stub_detected",False)
        level="SOURCE_PRESENT"
        for candidate in LEVELS:
            if evidence.get(candidate.lower(),False): level=candidate
        state="VERIFIED" if closed else ("FAILED" if evidence.get("failed") else "PARTIALLY_TESTED")
        return {"obligation_id":obligation["obligation_id"],"evidence_level":level,"closure_factors":flags,"stub_detected":bool(evidence.get("stub_detected")),"closed":closed,"ledger_state":state}
    def stub_scan(self,text:str)->list[str]:
        needles=("TODO","NOT_IMPLEMENTED","pass # placeholder","return True # stub","mock-only","IMPLEMENTED_BY_DESCRIPTION")
        return [n for n in needles if n.lower() in text.lower()]
