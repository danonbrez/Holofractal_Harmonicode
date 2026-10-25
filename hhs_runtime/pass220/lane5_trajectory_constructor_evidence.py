"""Candidate-only association between trajectory geometry and a constructor record.

Opaque Hash216-looking identifiers are not receipts. Do not promote this
association without inherited native predecessor verification and VM81 replay.
"""
from __future__ import annotations

from hhs_runtime.pass220.lane5_trajectory_relations import SCHEMA as TRAJECTORY_SCHEMA

SCHEMA = "HHS_PASS220_TRAJECTORY_CONSTRUCTOR_EVIDENCE_CANDIDATE_V1"

def associate_constructor(*, trajectory, constructor_id, source_contract, destination_contract,
                          elapsed_ns, claimed_hash216):
    if not isinstance(trajectory, dict) or trajectory.get("schema") != TRAJECTORY_SCHEMA:
        raise ValueError("ordered trajectory relationship required")
    if trajectory.get("candidate_only") is not True or trajectory.get("canonical_hash216_verified") is not False:
        raise ValueError("unverified trajectory candidate required")
    delta = trajectory.get("phase_delta_72")
    reciprocal = trajectory.get("reciprocal_phase_delta_72")
    if (not isinstance(delta, list) or not isinstance(reciprocal, list)
            or len(delta) != 72 or len(reciprocal) != 72
            or any(type(x) is not int for x in delta+reciprocal)
            or any(a+b != 0 for a,b in zip(delta,reciprocal))):
        raise ValueError("exact reciprocal 72-position phase delta required")
    if not all(type(trajectory.get(k)) is int for k in ("source_tick","middle_tick","target_tick")):
        raise ValueError("exact computational ticks required")
    if not trajectory["source_tick"]+1 == trajectory["middle_tick"] or not trajectory["middle_tick"]+1 == trajectory["target_tick"]:
        raise ValueError("contiguous trajectory required")
    if any(not isinstance(v,str) or not v.strip() for v in (constructor_id,source_contract,destination_contract)):
        raise ValueError("nonempty constructor and contract identities required")
    if type(elapsed_ns) is not int or elapsed_ns < 0:
        raise ValueError("measured elapsed_ns must be nonnegative integer")
    if not isinstance(claimed_hash216,str) or len(claimed_hash216) != 216:
        raise ValueError("216-symbol claimed receipt identity required")
    return {
        "schema": SCHEMA,
        "constructor_id": constructor_id,
        "source_contract": source_contract,
        "destination_contract": destination_contract,
        "claimed_hash216": claimed_hash216,
        "observed_elapsed_ns": elapsed_ns,
        "nucleus_id": trajectory["nucleus_id"],
        "source_tick": trajectory["source_tick"],
        "target_tick": trajectory["target_tick"],
        "phase_delta_72": list(delta),
        "neighbor_identity_changed": trajectory["neighbor_identity_changed"],
        "cross_modality_equivalence_verified": False,
        "native_execution_receipt_verified": False,
        "source_contract_verified": False,
        "destination_contract_verified": False,
        "candidate_only": True,
        "requires_exact_cpu_vm81_replay": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
    }
