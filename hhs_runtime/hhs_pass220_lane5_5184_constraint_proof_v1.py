"""Candidate proof envelope for 5184-position typed BigInt metadata.

This pre-admission verifier is not the signed C VM81/Hash72/Hash216 authority.
It rechecks every serialized position and the ordered constraint ledger.
"""
from __future__ import annotations
from hashlib import sha256
import json
from typing import Mapping, Sequence

WIDTH = 5184
SCHEMA = "HHS_PASS220_LANE5_5184_CONSTRAINT_PROOF_V1"
FORBIDDEN = ("canonical_mutation_authority", "hash72_mint_authority",
             "hash216_mint_authority", "persistence_authority")


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def prove_candidate_grid(positions: Sequence[Mapping], *, pipeline_root: str,
                         graph_root: str, ordered_constraints: Sequence[Mapping]) -> dict:
    if not isinstance(pipeline_root, str) or len(pipeline_root) != 72:
        raise ValueError("PIPELINE_ROOT_REQUIRED")
    if not isinstance(graph_root, str) or len(graph_root) != 72:
        raise ValueError("CONSTRUCTOR_GRAPH_ROOT_REQUIRED")
    if not isinstance(positions, (tuple, list)) or len(positions) != WIDTH:
        raise ValueError("EXACT_5184_POSITIONS_REQUIRED")
    if not isinstance(ordered_constraints, (tuple, list)) or not ordered_constraints:
        raise ValueError("ORDERED_CONSTRAINTS_REQUIRED")
    entries = []
    for n, cell in enumerate(positions):
        if not isinstance(cell, Mapping) or type(cell.get("linear5184")) is not int or cell["linear5184"] != n:
            raise ValueError("POSITION_ORDER_OR_IDENTITY")
        if cell.get("cell81") != n // 64 or cell.get("operation64") != n % 64:
            raise ValueError("VM81_ADDRESS_MISMATCH")
        if cell.get("hash72_major") != n // 72 or cell.get("hash72_minor") != n % 72:
            raise ValueError("HASH72_ADDRESS_MISMATCH")
        data = cell.get("bigint_decimal")
        if not isinstance(data, str) or not data or data in ("-0", "+0") or (
            data[0] == "-" and (len(data) == 1 or data[1] == "0")
        ) or (data[0] == "0" and len(data) > 1) or not (
            data.isascii() and (data.isdigit() or data[0] == "-" and data[1:].isdigit())
        ):
            raise ValueError("NONCANONICAL_BIGINT")
        if any(cell.get(flag) is not False for flag in FORBIDDEN):
            raise ValueError("UNAUTHORIZED_CANONICAL_AUTHORITY")
        entries.append([n, n // 64, n % 64, n // 72, n % 72, data])
    gates = []
    for i, gate in enumerate(ordered_constraints):
        if not isinstance(gate, Mapping) or gate.get("order") != i or gate.get("closed") is not True:
            raise ValueError("GATE_NOT_CLOSED_IN_ORDER")
        if gate.get("bypassed") is True and (gate.get("phase_written") is not False or gate.get("gain") != "1"):
            raise ValueError("HNAN_BYPASS_CHANGED_PHASE")
        if not isinstance(gate.get("constraint_id"), str) or not gate["constraint_id"]:
            raise ValueError("CONSTRAINT_ID_REQUIRED")
        gates.append([i, gate["constraint_id"], bool(gate.get("bypassed", False))])
    payload = {"schema": SCHEMA, "positions": entries, "ordered_gates": gates,
               "inherited_pipeline_root": pipeline_root,
               "inherited_constructor_graph_root": graph_root}
    digest = sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return {"schema": SCHEMA, "candidate_only": True,
            "all_5184_positions_verified": True,
            "ordered_constraint_closure_verified": True,
            "candidate_evidence_sha256": digest,
            "inherited_pipeline_root": pipeline_root,
            "inherited_constructor_graph_root": graph_root,
            "signed_vm81_admission_verified": False,
            "canonical_hash216_minted": False}


def verify_candidate_grid(positions, *, pipeline_root, graph_root,
                          ordered_constraints, claimed_proof):
    actual = prove_candidate_grid(
        positions, pipeline_root=pipeline_root, graph_root=graph_root,
        ordered_constraints=ordered_constraints)
    if not isinstance(claimed_proof, Mapping) or dict(claimed_proof) != actual:
        raise ValueError("REPLAY_PROOF_MISMATCH")
    return actual
