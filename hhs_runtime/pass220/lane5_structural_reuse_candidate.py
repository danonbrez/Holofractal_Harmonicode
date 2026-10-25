"""Candidate-only structural reuse check for two native trajectory projections.

This is equality of bounded ordered geometry, not execution equivalence.
"""
from __future__ import annotations
from hhs_runtime.pass220.lane5_trajectory_relations import SCHEMA as TRAJECTORY_SCHEMA

SCHEMA = "HHS_PASS220_LANE5_STRUCTURAL_REUSE_CANDIDATE_V1"

def compare_structure(*, left, right, left_contract, right_contract):
    if any(not isinstance(c, str) or not c.strip() for c in (left_contract,right_contract)):
        raise ValueError("typed source and destination contract identifiers required")
    for item in (left,right):
        if not isinstance(item,dict) or item.get("schema") != TRAJECTORY_SCHEMA:
            raise ValueError("trajectory candidate required")
        if item.get("candidate_only") is not True or item.get("canonical_hash216_verified") is not False:
            raise ValueError("unsigned candidate projection required")
        d=item.get("phase_delta_72")
        r=item.get("reciprocal_phase_delta_72")
        if (not isinstance(d,list) or not isinstance(r,list) or len(d)!=72 or len(r)!=72
                or any(type(v) is not int for v in d+r)
                or any(a+b for a,b in zip(d,r))):
            raise ValueError("72 exact ordered reciprocal deltas required")
        for key in ("source_tick","middle_tick","target_tick","nucleus_id"):
            if type(item.get(key)) is not int or item[key]<0:
                raise ValueError("exact nonnegative tick and nucleus required")
        if item["middle_tick"] != item["source_tick"]+1 or item["target_tick"] != item["middle_tick"]+1:
            raise ValueError("consecutive trajectory ticks required")
        for key in ("ordered_neighbor_id_before","ordered_neighbor_id_after"):
            ids=item.get(key)
            if not isinstance(ids,list) or len(ids)!=9 or len(set(ids))!=9 or any(type(v) is not int or not 0<=v<10368 for v in ids):
                raise ValueError("nine unique particle identities required")
            if ids[0] != item["nucleus_id"]:
                raise ValueError("nucleus not conserved")
        if item.get("neighbor_identity_changed") is not (item["ordered_neighbor_id_before"]!=item["ordered_neighbor_id_after"]):
            raise ValueError("neighbor change flag inconsistent")
    # Address-independent comparison: exact phase differences and reordering
    # pattern only; cannot itself prove constructor/ABI/output equivalence.
    def pattern(item):
        return tuple(item["ordered_neighbor_id_before"].index(pid) if pid in item["ordered_neighbor_id_before"] else -1
                     for pid in item["ordered_neighbor_id_after"])
    same_delta=left["phase_delta_72"]==right["phase_delta_72"]
    same_pattern=pattern(left)==pattern(right)
    return {
        "schema":SCHEMA,
        "left_contract":left_contract,
        "right_contract":right_contract,
        "identical_ordered_phase_deltas":same_delta,
        "identical_neighbor_permutation_pattern":same_pattern,
        "structural_reuse_candidate":same_delta and same_pattern,
        "cross_modality_equivalence_verified":False,
        "source_destination_abi_verified":False,
        "native_receipts_verified":False,
        "candidate_only":True,
        "requires_exact_cpu_vm81_replay":True,
        "canonical_vm81_mutation_authority":False,
        "canonical_hash72_mint_authority":False,
        "canonical_hash216_mint_authority":False,
    }
