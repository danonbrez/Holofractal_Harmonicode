from __future__ import annotations
from .common import sha256_text
CLASSES={"CURRENT_USER_SPECIFICATION","RATIFIED_CONTRACT","VALIDATED_AMENDMENT","EXECUTION_EVIDENCE","RUNTIME_RECEIPT","IMPLEMENTATION_STATE","DIAGNOSTIC_OBSERVATION","SEMANTIC_HYPOTHESIS","EXAMPLE","BACKGROUND_DISCUSSION","MODEL_INFERENCE","DEPRECATED_STATEMENT","CONTRADICTED_STATEMENT"}
RANK={k:i for i,k in enumerate(reversed(["CURRENT_USER_SPECIFICATION","RATIFIED_CONTRACT","VALIDATED_AMENDMENT","EXECUTION_EVIDENCE","RUNTIME_RECEIPT","IMPLEMENTATION_STATE","DIAGNOSTIC_OBSERVATION","SEMANTIC_HYPOTHESIS","EXAMPLE","BACKGROUND_DISCUSSION","MODEL_INFERENCE","DEPRECATED_STATEMENT","CONTRADICTED_STATEMENT"]))}
class ContextConstraintMembrane:
    def classify(self,text:str,context_class:str,source:str="inline",scope:str="global",superseded_by:str|None=None)->dict:
        if context_class not in CLASSES: raise ValueError("INVALID_CONTEXT_CLASS")
        pid="P151-CTX-"+sha256_text(f"{source}|{scope}|{text}")[:24].upper()
        return {"schema":"HHS_PASS151_CONTEXT_ITEM_V1","context_id":pid,"exact_text":text,"context_class":context_class,"source":source,"scope":scope,"superseded_by":superseded_by,"binding":context_class in {"CURRENT_USER_SPECIFICATION","RATIFIED_CONTRACT","VALIDATED_AMENDMENT"} and not superseded_by}
    def resolve(self,items:list[dict])->list[dict]:
        return sorted(items,key=lambda x:(-RANK[x["context_class"]],x["context_id"]))
    def admission(self,recommendation:dict,binding_items:list[dict])->dict:
        text=str(recommendation.get("text","")); lowered=text.lower(); violations=[]
        if any(w in lowered for w in ("ignore the contract","weaken must","skip required test","treat stub as implemented","foreign operator semantics","hash216 acceptance means vm81 admission","o = pi","o=π")): violations.append("UNAUTHORIZED_SUBSTITUTION")
        if recommendation.get("declares_completion"): violations.append("SEMANTIC_REASONER_CANNOT_CLOSE")
        missing=[i["context_id"] for i in binding_items if i.get("binding") and i["exact_text"] not in recommendation.get("preserved_obligations",[])]
        if missing: violations.append("VERBATIM_OBLIGATION_NOT_PRESERVED")
        return {"admitted":not violations,"violations":violations,"missing_context_ids":missing}
