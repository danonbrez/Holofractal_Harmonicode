"""Bound ordered symbolic P metadata to the inherited executed HNAN/I074 gate.

The raw frame is a separately supplied representation: this verifier does not
claim that symbolic P metadata alone generates that frame. Existing I148,
HNAN and I074 verifiers remain authority for their respective witnesses.
"""
from __future__ import annotations
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_hash216_symbolic_tensor_metadata_v1 import (
    TensorRef, SymbolicTensorError, compose_metadata,
)
from hhs_runtime.hhs_pass220_hnan_lane5_i074_candidate_binding_v1 import (
    execute_candidate, Lane5HNANBindingError,
)

SCHEMA = "HHS_PASS220_SYMBOLIC_HNAN_I074_LINEAGE_ADAPTER_V1"


def bind_symbolic_to_inherited_hnan(
    operation: str,
    left: TensorRef,
    right: TensorRef,
    raw5184: str,
    *,
    candidate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify a symbolic expression against the inherited HNAN gate witness.

    Fail-closed if either operand's supplied lineage does not match the I074
    candidate's ordered 216-character lineage. A different lineage requires
    an actual ancestry bridge and cannot be silently substituted.
    """
    metadata = compose_metadata(operation, left, right)
    inherited = execute_candidate(raw5184, candidate=candidate)
    if inherited["raw_roundtrip_exact"] is not True:
        raise Lane5HNANBindingError("INHERITED_RAW_ROUNDTRIP_REQUIRED")
    if inherited["hnan_gate_inherited"] is not True:
        raise Lane5HNANBindingError("INHERITED_HNAN_GATE_REQUIRED")
    if inherited["three_binary_perspectives_retained"] is not True:
        raise Lane5HNANBindingError("INHERITED_ORDERED_PHASE_WITNESS_REQUIRED")
    expected = inherited["i074_hash216"]
    if left.hash216_lineage != expected or right.hash216_lineage != expected:
        raise SymbolicTensorError("OPERAND_HASH216_LINEAGE_NOT_BOUND_TO_I074")
    record = {
        "schema": SCHEMA,
        "ordered_symbolic_constructor_sha256": metadata["constructor_witness_sha256"],
        "operation": metadata["operator"],
        "derived_P": metadata["derived_P"],
        "global_constraint_root": metadata["global_constraint_root"],
        "ordered_inputs": metadata["ordered_inputs"],
        "i074_candidate_root_sha256": inherited["i074_candidate_root_sha256"],
        "i074_hash216": expected,
        "raw5184_sha256": inherited["raw5184_sha256"],
        "hnan_inherited_gate_executed": True,
        "exact_raw_roundtrip_verified": True,
        "same_ancestry_lineage_verified": True,
        "symbolic_P_to_raw5184_constructor_proved": False,
        "global_hnan_closure_for_symbolic_operation_proved": False,
        "metadata_link_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    record["candidate_receipt_sha256"] = sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":")
    ).encode("ascii")).hexdigest()
    return record
