from __future__ import annotations
from .common import sha256_text, canonical_json
CONDITIONS={"CONTRADICTION","FAILED_TEST","AMBIGUOUS_IMPLEMENTATION_CHOICE","UNEXPECTED_RUNTIME_STATE","MISSING_DEPENDENCY","RESOURCE_BOUND","NOVEL_ALGORITHM_REQUIRED","NATIVE_SEMANTIC_EXPLANATION_REQUIRED"}
class BoundedSemanticReasoner:
    def request(self,condition:str,obligation_ids:list[str],verbatim:list[str],facts:list[str],allowed:list[str],prohibited:list[str],budget:int=8)->dict:
        if condition not in CONDITIONS: raise ValueError("INVALID_REASONING_CONDITION")
        if budget<1 or budget>64: raise ValueError("INVALID_REASONING_BUDGET")
        packet={"condition":condition,"obligation_ids":sorted(obligation_ids),"verbatim_contract_text":verbatim,"facts":facts,"allowed_decision_space":allowed,"prohibited_substitutions":prohibited,"resource_bound_steps":budget}
        packet["request_id"]="P151-SEM-"+sha256_text(canonical_json(packet))[:24].upper(); return packet
    def reason(self,packet:dict)->dict:
        facts=list(packet.get("facts",[])); allowed=list(packet.get("allowed_decision_space",[])); budget=int(packet["resource_bound_steps"])
        if not allowed: status="SEMANTIC_REASONING_RESOURCE_BOUNDED"; repairs=[]
        else: status="ADVISORY_CANDIDATE"; repairs=allowed[:budget]
        return {"schema":"HHS_PASS151_SEMANTIC_RESPONSE_V1","request_id":packet["request_id"],"status":status,"diagnosis":f"Bounded diagnosis for {packet['condition']}","facts":facts,"inferences":[],"uncertainties":[] if facts else ["NO_EXECUTION_FACTS"],"candidate_repairs":repairs,"recommended_repair":repairs[0] if repairs else None,"affected_obligations":packet["obligation_ids"],"required_validation":["EXECUTE_REPAIR","RUN_REQUIRED_TESTS","RECONCILE_EVIDENCE"],"termination_condition":"BUDGET_OR_CANDIDATE_EXHAUSTED","declares_completion":False}
