"""Bind the existing I077 exact native VM81 execution to its frozen whitepaper.

The native executor, not Python, performs the two ordered symbolic operations.
This receipt is evidence of I077 execution; it cannot admit the 69-paper corpus.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
from hhs_runtime.hhs_pass220_i077_vm81_exact_matrix_power_execution_v1 import (
    VM81ExactMatrixPowerExecutor,
)
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import (
    build_dependency_graph, bind_native_evidence, _hash,
)
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

SOURCE="docs/whitepapers/HHS_PASS_220_I077_VM81_EXACT_MATRIX_POWER_EXECUTION_V1.md"
NODES=("MatrixPower[M_wz,x^2]","MatrixPower[M_xy,x^4]")

def execute_i077_whitepaper_binding(native_library: str) -> dict:
    graph=build_dependency_graph()
    matching=[n for n in graph["nodes"] if n["source"]==SOURCE]
    if len(matching)!=1:
        raise ProofCorpusError("I077_FROZEN_SOURCE_REQUIRED")
    if not isinstance(native_library,str) or not Path(native_library).is_file():
        raise ProofCorpusError("I077_NATIVE_LIBRARY_REQUIRED")
    executor=VM81ExactMatrixPowerExecutor(native_library)
    desc=executor.descriptor
    required=("native_symbolic_executor","rectangular_4x2_supported",
              "vm81_transport_admission","hash72_execution_receipt",
              "hash216_transition_identity","deterministic_replay")
    prohibited=("matrix_power_value_derivation","host_matrixpower_authority",
                "host_square_matrix_requirement_authority",
                "numeric_exponent_evaluation_authority","floating_point_authority",
                "canonical_vm81_mutation_authority","canonical_hash72_commit_authority",
                "canonical_hash216_commit_authority")
    if desc["node_count"]!=2 or desc["rows"]!=4 or desc["columns"]!=2 or (
        any(desc[k] is not True for k in required) or
        any(desc[k] is not False for k in prohibited)
    ):
        raise ProofCorpusError("I077_NATIVE_DESCRIPTOR_REJECTED")
    executions=executor.execute_all()
    if len(executions)!=2 or tuple(x.source_node for x in executions)!=NODES:
        raise ProofCorpusError("I077_ORDERED_SOURCE_NODES_REJECTED")
    records=[]
    for row in executions:
        verified=("source_identity_exact","ordered_topology_verified",
                  "exact_symbolic_node_executed","exact_vm81_admission_verified",
                  "atomic_frame_commit_verified","hash72_receipt_verified",
                  "hash216_transition_identity_verified","deterministic_replay_verified")
        forbidden=("host_matrixpower_used","square_matrix_requirement_imported",
                   "numeric_exponent_evaluated","matrix_power_value_derived",
                   "canonical_state_persisted","floating_point_authority")
        if (row.rows,row.columns)!=(4,2) or len(row.cell_tokens)!=8 or (
            any(getattr(row,k) is not True for k in verified) or
            any(getattr(row,k) is not False for k in forbidden) or
            row.vm81_steps!=1 or row.replay_vm81_steps!=1 or
            row.receipt_hash72!=row.replay_hash72 or
            len(row.proof_hash216)!=216 or len(row.transition_hash216)!=216 or
            any(len(h)!=72 for h in (row.change_hash72,row.receipt_hash72,row.replay_hash72))
        ):
            raise ProofCorpusError("I077_NATIVE_EXECUTION_RECEIPT_REJECTED")
        records.append({"source_node":row.source_node,
                        "source_node_sha256":row.source_node_sha256,
                        "ordered_cells_sha256":row.ordered_cells_sha256,
                        "proof_hash216":row.proof_hash216,
                        "transition_hash216":row.transition_hash216,
                        "vm5184_address":row.vm5184_address})
    if records[0]["transition_hash216"]==records[1]["transition_hash216"]:
        raise ProofCorpusError("I077_DISTINCT_TRANSITIONS_REQUIRED")
    receipt={"source_sha256":matching[0]["source_sha256"],
             "checker":"VM81_EXACT","native_verification_receipt":True,
             "proof_receipt_sha256":_hash([matching[0]["source_sha256"],records])}
    binding=bind_native_evidence(graph,SOURCE,receipt)
    return {"source":SOURCE,"native_executions":records,
            "binding":binding,"full_corpus_proved":False,
            "canonical_hash216_newly_minted":False}
