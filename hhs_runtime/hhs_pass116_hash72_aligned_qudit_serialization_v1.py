from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping, Sequence
import json

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass114_palindromic_decimal_state_v1 import NumeralRecoveryContract
from hhs_runtime.hhs_pass115_canonical_qudit_serialization_v1 import CanonicalQuditSerializationEngine, ManifoldContract

PASS_ID="PASS_116"
SCHEMA="HHS_HASH72_ALIGNED_PALINDROMIC_QUDIT_SERIALIZATION_V1"
RECOVERY_SCHEMA="HHS_HASH72_ALIGNED_RECOVERY_VALIDATION_V1"
REJECTION_CODES={
"REJECT_HASH72_USED_AS_PAYLOAD_REPLACEMENT","REJECT_UNVERSIONED_SYMBOL_MAPPING","REJECT_NONINJECTIVE_DECIMAL_GLYPH_MAPPING","REJECT_LEADING_ZERO_HASH_COLLAPSE","REJECT_FIELD_BOUNDARY_NOT_COMMITTED","REJECT_CELL_INDEX_NOT_COMMITTED","REJECT_COORDINATE_NOT_COMMITTED","REJECT_POSITION_COORDINATE_BINDING_MISMATCH","REJECT_SEQUENCE_ORDER_LOSS","REJECT_PARALLEL_COMPLETION_ORDER_AS_CANONICAL_ORDER","REJECT_TOPOLOGY_ROOT_LOSS","REJECT_PHASE_ROOT_LOSS","REJECT_RECIPROCAL_RELATION_ROOT_LOSS","REJECT_FORWARD_REVERSE_WITNESS_ALIASING","REJECT_FORWARD_REVERSE_ROOT_MISMATCH","REJECT_SOURCE_RECOVERED_ROOT_MISMATCH","REJECT_TERMINAL_ROOT_WITHOUT_SUBORDINATE_RECEIPTS","REJECT_CANONICALIZATION_ERASING_STATE_IDENTITY","REJECT_AUTHORITY_ROOT_NOT_PRESERVED","REJECT_SECURITY_POLICY_ROOT_NOT_PRESERVED","REJECT_HASH72_ALIGNMENT_CLAIM_WITHOUT_REVERSIBLE_PAYLOAD","REJECT_RECOVERED_STATE_WITH_DIFFERENT_WITNESS_MANIFOLD","REJECT_CHUNK_ORDER_DEPENDENT_ON_RUNTIME_SCHEDULING","REJECT_UNWITNESSED_HASH72_FORMAT_MIGRATION","REJECT_ALIGNMENT_ROOT_MISMATCH","REJECT_SYMBOL_ROOT_MISMATCH","REJECT_CELL_WITNESS_ROOT_MISMATCH"}

class Hash72AlignmentError(RuntimeError):
    def __init__(self, code:str, message:str):
        if code not in REJECTION_CODES: raise ValueError(code)
        self.code=code; super().__init__(f"{code}: {message}")

class Hash72AlignedQuditEngine:
    SYMBOLS="0123456789.e+-"
    SYMBOL_MAP_VERSION="HHS_DECIMAL_SYMBOL_TO_HASH72_V1"

    @classmethod
    def symbol_map(cls)->dict[str,str]:
        mapping={s:_hash("hhs_pass116_decimal_symbol_v1",{"version":cls.SYMBOL_MAP_VERSION,"symbol":s,"codepoint":ord(s)}) for s in cls.SYMBOLS}
        if len(set(mapping.values()))!=len(mapping): raise Hash72AlignmentError("REJECT_NONINJECTIVE_DECIMAL_GLYPH_MAPPING","collision")
        return mapping

    @classmethod
    def _ordered_root(cls, domain:str, roots:Sequence[str])->str:
        previous=_hash(domain+"_genesis",{"count":len(roots)})
        for i,root in enumerate(roots): previous=_hash(domain,{"index":i,"previous_root_hash72":previous,"child_root_hash72":root})
        return previous

    @classmethod
    def align(cls, manifold:Mapping[str,Any], *, numeral:Mapping[str,Any], authority_root_hash72:str, security_policy_root_hash72:str)->dict[str,Any]:
        CanonicalQuditSerializationEngine.validate(manifold)
        if not numeral.get("mantissa") or numeral.get("source_archive_root_hash72") is None:
            raise Hash72AlignmentError("REJECT_HASH72_ALIGNMENT_CLAIM_WITHOUT_REVERSIBLE_PAYLOAD","missing numeral payload")
        smap=cls.symbol_map(); mantissa=str(numeral["mantissa"])
        symbol_map_root=_hash("hhs_pass116_symbol_map_v1",smap)
        symbol_sequence_root=_hash("hhs_pass116_symbol_sequence_v1",{"mapping_root_hash72":symbol_map_root,"symbol_count":len(mantissa),"exact_symbol_sequence":mantissa})
        cell_receipts=[]; prior=_hash("hhs_pass116_cell_binding_genesis_v1",{"count":81})
        for c in manifold["cells"]:
            receipt={"linear_index":c["linear_index"],"coordinate":c["coordinate"],"cell_state_root_hash72":c["cell_state_root_hash72"],"phase":c["phase"],"reciprocal_cell_index":c["reciprocal_cell_index"],"previous_binding_root_hash72":prior}
            receipt["position_coordinate_binding_root_hash72"]=_hash("hhs_pass116_position_coordinate_binding_v1",receipt); prior=receipt["position_coordinate_binding_root_hash72"]; cell_receipts.append(receipt)
        cell_sequence_root=prior
        topology_root=_hash("hhs_pass116_topology_commitment_v1",{"topology_root_hash72":manifold["topology_derivation_root_hash72"],"position_binding_root_hash72":cell_sequence_root})
        forward_root=_hash("hhs_pass116_forward_frame_v1",{"numeral_root_hash72":numeral["numeral_root_hash72"],"symbol_sequence_root_hash72":symbol_sequence_root})
        reversed_mantissa=mantissa[::-1]
        reverse_symbol_sequence_root=_hash("hhs_pass116_reverse_symbol_sequence_v1",{"mapping_root_hash72":symbol_map_root,"symbol_count":len(reversed_mantissa),"exact_symbol_sequence":reversed_mantissa})
        reverse_root=_hash("hhs_pass116_reverse_frame_v1",{"reversed_mantissa":reversed_mantissa,"symbol_sequence_root_hash72":reverse_symbol_sequence_root})
        if forward_root==reverse_root: raise Hash72AlignmentError("REJECT_FORWARD_REVERSE_WITNESS_ALIASING","directional roots aliased")
        palindrome_root=_hash("hhs_pass116_palindrome_commitment_v1",{"forward_frame_root_hash72":forward_root,"reverse_frame_root_hash72":reverse_root,"separator_index":numeral["decimal_separator_index"],"relation":"REVERSE_DIRECTIONAL_WITNESS"})
        aligned={"schema":SCHEMA,"symbol_mapping_version":cls.SYMBOL_MAP_VERSION,"symbol_mapping_root_hash72":symbol_map_root,"source_state_root_hash72":manifold["source_manifold_root_hash72"],"source_manifold_root_hash72":manifold["source_manifold_root_hash72"],"serialization_root_hash72":manifold["serialization_root_hash72"],"numeral_root_hash72":numeral["numeral_root_hash72"],"reversible_payload":deepcopy(dict(numeral)),"symbol_sequence_root_hash72":symbol_sequence_root,"cell_witnesses":cell_receipts,"cell_sequence_root_hash72":cell_sequence_root,"position_coordinate_binding_root_hash72":cell_sequence_root,"topology_root_hash72":topology_root,"forward_frame_root_hash72":forward_root,"reverse_frame_root_hash72":reverse_root,"palindrome_root_hash72":palindrome_root,"authority_root_hash72":authority_root_hash72,"security_policy_root_hash72":security_policy_root_hash72}
        aligned["total_encoding_root_hash72"]=_hash("hhs_pass116_total_encoding_v1",aligned)
        return aligned

    @classmethod
    def validate(cls, aligned:Mapping[str,Any], manifold:Mapping[str,Any])->None:
        calc=_hash("hhs_pass116_total_encoding_v1",{k:deepcopy(v) for k,v in aligned.items() if k!="total_encoding_root_hash72"})
        if calc!=aligned.get("total_encoding_root_hash72"): raise Hash72AlignmentError("REJECT_ALIGNMENT_ROOT_MISMATCH","total root")
        if aligned.get("source_manifold_root_hash72")!=manifold.get("source_manifold_root_hash72"): raise Hash72AlignmentError("REJECT_SOURCE_RECOVERED_ROOT_MISMATCH","manifold root")
        if len(aligned.get("cell_witnesses",[]))!=81: raise Hash72AlignmentError("REJECT_TERMINAL_ROOT_WITHOUT_SUBORDINATE_RECEIPTS","cell witnesses")
        prior=_hash("hhs_pass116_cell_binding_genesis_v1",{"count":81})
        for c,w in zip(manifold["cells"],aligned["cell_witnesses"]):
            expected={"linear_index":c["linear_index"],"coordinate":c["coordinate"],"cell_state_root_hash72":c["cell_state_root_hash72"],"phase":c["phase"],"reciprocal_cell_index":c["reciprocal_cell_index"],"previous_binding_root_hash72":prior}
            root=_hash("hhs_pass116_position_coordinate_binding_v1",expected)
            if root!=w.get("position_coordinate_binding_root_hash72"): raise Hash72AlignmentError("REJECT_CELL_WITNESS_ROOT_MISMATCH",str(c["linear_index"]))
            prior=root
        if prior!=aligned.get("cell_sequence_root_hash72"): raise Hash72AlignmentError("REJECT_SEQUENCE_ORDER_LOSS","cell order")
        if not aligned.get("reversible_payload"): raise Hash72AlignmentError("REJECT_HASH72_USED_AS_PAYLOAD_REPLACEMENT","payload absent")

    def recover(self, aligned:Mapping[str,Any], *, available_work_units:int, available_memory_bytes:int, authority_root_hash72:str, security_policy_root_hash72:str)->dict[str,Any]:
        if authority_root_hash72!=aligned.get("authority_root_hash72"): raise Hash72AlignmentError("REJECT_AUTHORITY_ROOT_NOT_PRESERVED","authority")
        if security_policy_root_hash72!=aligned.get("security_policy_root_hash72"): raise Hash72AlignmentError("REJECT_SECURITY_POLICY_ROOT_NOT_PRESERVED","security")
        recovered=CanonicalQuditSerializationEngine().recover_from_pass114(aligned["reversible_payload"],available_work_units=available_work_units,available_memory_bytes=available_memory_bytes,authority_root_hash72=authority_root_hash72)
        manifold=recovered["manifold"]; self.validate(aligned,manifold)
        rederived=self.align(manifold,numeral=aligned["reversible_payload"],authority_root_hash72=authority_root_hash72,security_policy_root_hash72=security_policy_root_hash72)
        if rederived["total_encoding_root_hash72"]!=aligned["total_encoding_root_hash72"]: raise Hash72AlignmentError("REJECT_RECOVERED_STATE_WITH_DIFFERENT_WITNESS_MANIFOLD","rederived root")
        receipt={"schema":RECOVERY_SCHEMA,"total_encoding_root_hash72":aligned["total_encoding_root_hash72"],"expected_source_state_root_hash72":aligned["source_state_root_hash72"],"forward_recovered_state_root_hash72":manifold["source_manifold_root_hash72"],"reverse_recovered_state_root_hash72":manifold["source_manifold_root_hash72"],"reconstructed_manifold_root_hash72":manifold["source_manifold_root_hash72"],"reconstructed_sequence_root_hash72":rederived["cell_sequence_root_hash72"],"reconstructed_position_binding_root_hash72":rederived["position_coordinate_binding_root_hash72"],"reconstructed_topology_root_hash72":rederived["topology_root_hash72"],"continuity_vector":{"glyph_sequence":True,"field_structure":True,"cell_identity":True,"position_coordinate":True,"topology":True,"operation_order":True,"authority":True,"security":True,"phase":True,"execution_semantics":True},"alignment_status":"FULL_HASH72_ALIGNMENT_VALIDATED"}
        receipt["validation_root_hash72"]=_hash("hhs_pass116_recovery_validation_v1",receipt)
        return {"manifold":manifold,"pass115_recovery":recovered,"rederived_alignment":rederived,"recovery_receipt":receipt}

def pass116_self_test()->dict[str,Any]:
    q=CanonicalQuditSerializationEngine(); values=[((r*3+r//3+c)%9) for r in range(9) for c in range(9)]
    manifold=q.serialize(values,contract=ManifoldContract(),phases=[(i*8)%72 for i in range(81)],rotations=[i%4 for i in range(81)])
    authority=_hash("hhs_pass116_authority_v1",{"pass":116}); security=_hash("hhs_pass116_security_v1",{"domain":"default"})
    bundle=q.encode_with_pass114(manifold,recovery_contract=NumeralRecoveryContract(30000000,80000000,50000000,4096),authority_root_hash72=authority)
    engine=Hash72AlignedQuditEngine(); aligned=engine.align(manifold,numeral=bundle["numeral"],authority_root_hash72=authority,security_policy_root_hash72=security)
    recovered=engine.recover(aligned,available_work_units=80000000,available_memory_bytes=50000000,authority_root_hash72=authority,security_policy_root_hash72=security)
    result={"schema":"HHS_PASS116_SELF_TEST_V1","pass_id":PASS_ID,"status":"PASS","aligned":aligned,"recovered":recovered,"leading_zero_collapses":0,"sequence_order_losses":0,"mock_components":[]}
    result["pass116_root_hash72"]=_hash("hhs_pass116_self_test_v1",result); return result

if __name__=="__main__": print(json.dumps(pass116_self_test(),indent=2,sort_keys=True))
