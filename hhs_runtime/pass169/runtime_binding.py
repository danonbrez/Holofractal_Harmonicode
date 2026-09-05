"""Pass 219 I168 canonical Pass169 binding over the deployed shared Runtime ABI.

This module is transport glue only.  Canonical computation is performed by
`hhs_exact_pass219_i168_bind_canonical` inside `libhhs_runtime`, which in turn
uses inherited Pass159 source/compiler calls plus the sealed I162 VM81 and I163
reverse authorities.  Python never recomputes canonical algebra.
"""
from __future__ import annotations

import ctypes
from ctypes import POINTER, Structure, c_char, c_size_t, c_uint8, c_uint16, c_uint32, c_uint64
from hashlib import sha256
from pathlib import Path
from typing import Any

from hhs_python.runtime.hhs_exact_ctypes_bridge import _RUNTIME_LIB

CANONICAL_SOURCE_BYTES = 632
CANONICAL_SOURCE_SHA256 = "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53"
CANONICAL_SOURCE_PATH = Path("HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode")
FIXED_RESOLUTION = "72^42=5184^21"
CONTRACT_ID = "HHS-P169-HSAE-VM81-ESCPR"

HHS_EXACT_STATUS_OK = 0
HHS_EXACT_PASS219_I168_VERIFIED = 1
HHS_EXACT_PASS219_I168_ALL_OPS = 0x0FFF

VERIFIED_OPERATIONS = (
    "tokens",
    "ast",
    "constraints",
    "typecheck",
    "normalize",
    "prove",
    "evaluate-candidate",
    "admit",
    "commit",
    "receipt",
    "replay",
    "reverse",
)


class HHSExactPass219I168RuntimeBindingV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("decision", c_uint32),
        ("reason", c_uint32),
        ("operation_verified_mask", c_uint16),
        ("required_operation_mask", c_uint16),
        ("source_identity_exact", c_uint8),
        ("pass159_frontend_chain_complete", c_uint8),
        ("typed_proof_verified", c_uint8),
        ("interpreter_compiler_match", c_uint8),
        ("exact_vm81_admission_verified", c_uint8),
        ("atomic_commit_verified", c_uint8),
        ("hash72_receipts_verified", c_uint8),
        ("hash216_identities_verified", c_uint8),
        ("deterministic_replay_verified", c_uint8),
        ("reverse_restores_prior_state_verified", c_uint8),
        ("live_runtime_abi_verified", c_uint8),
        ("canonical_computation_through_runtime_abi", c_uint8),
        ("single_vm81_commit_authority", c_uint8),
        ("fallback_used", c_uint8),
        ("floating_point_authority", c_uint8),
        ("hash216_persistence_authority", c_uint8),
        ("vm5184_address", c_uint16),
        ("reserved0", c_uint16),
        ("forward_vm81_steps", c_uint64),
        ("replay_vm81_steps", c_uint64),
        ("reverse_vm81_steps", c_uint64),
        ("source_hash216", c_char * 217),
        ("tokens_hash216", c_char * 217),
        ("ast_hash216", c_char * 217),
        ("type_environment_hash216", c_char * 217),
        ("constraint_graph_hash216", c_char * 217),
        ("normalized_ir_hash216", c_char * 217),
        ("vmir_hash216", c_char * 217),
        ("proof_hash216", c_char * 217),
        ("transition_hash216", c_char * 217),
        ("reverse_hash216", c_char * 217),
        ("receipt_hash72", c_char * 73),
        ("replay_hash72", c_char * 73),
        ("reverse_hash72", c_char * 73),
    ]


_RUNTIME_LIB.hhs_exact_pass219_i168_version.argtypes = []
_RUNTIME_LIB.hhs_exact_pass219_i168_version.restype = c_uint32
_RUNTIME_LIB.hhs_exact_pass219_i168_bind_canonical.argtypes = [
    POINTER(c_uint8), c_size_t, POINTER(HHSExactPass219I168RuntimeBindingV1)
]
_RUNTIME_LIB.hhs_exact_pass219_i168_bind_canonical.restype = ctypes.c_int


class Pass169RuntimeBindingError(RuntimeError):
    pass


def _text(value: bytes) -> str:
    return value.decode("ascii")


def _stable_id(kind: str, identity: str) -> str:
    return f"{kind}:sha256:{sha256(identity.encode('ascii')).hexdigest()}"


class Pass169CanonicalRuntimeBinding:
    """Lazy deterministic view of the one canonical Pass169 Runtime ABI proof."""

    def __init__(self, repository_root: str | Path) -> None:
        self.repository_root = Path(repository_root).resolve()
        self._record: dict[str, Any] | None = None

    @property
    def canonical_source_id(self) -> str:
        return f"canonical:sha256:{CANONICAL_SOURCE_SHA256}"

    def _source_bytes(self) -> bytes:
        data = (self.repository_root / CANONICAL_SOURCE_PATH).read_bytes()
        if len(data) != CANONICAL_SOURCE_BYTES or sha256(data).hexdigest() != CANONICAL_SOURCE_SHA256:
            raise Pass169RuntimeBindingError("PASS169_CANONICAL_SOURCE_IDENTITY_MISMATCH")
        return data

    def record(self) -> dict[str, Any]:
        if self._record is not None:
            return dict(self._record)
        data = self._source_bytes()
        raw = (c_uint8 * len(data)).from_buffer_copy(data)
        binding = HHSExactPass219I168RuntimeBindingV1()
        status = _RUNTIME_LIB.hhs_exact_pass219_i168_bind_canonical(raw, len(data), ctypes.byref(binding))
        if status != HHS_EXACT_STATUS_OK:
            raise Pass169RuntimeBindingError(f"PASS169_I168_RUNTIME_BINDING_STATUS_{status}")
        if binding.decision != HHS_EXACT_PASS219_I168_VERIFIED:
            raise Pass169RuntimeBindingError(
                f"PASS169_I168_RUNTIME_BINDING_REJECTED_REASON_{binding.reason}"
            )
        if binding.operation_verified_mask != HHS_EXACT_PASS219_I168_ALL_OPS:
            raise Pass169RuntimeBindingError("PASS169_I168_OPERATION_MASK_INCOMPLETE")

        record = {
            "schema": "HHS_PASS219_I168_RUNTIME_BINDING_RECORD_V1",
            "contract_id": CONTRACT_ID,
            "fixed_resolution": FIXED_RESOLUTION,
            "abi_version": int(_RUNTIME_LIB.hhs_exact_pass219_i168_version()),
            "decision": int(binding.decision),
            "operation_verified_mask": int(binding.operation_verified_mask),
            "required_operation_mask": int(binding.required_operation_mask),
            "verified_operations": list(VERIFIED_OPERATIONS),
            "source_id": self.canonical_source_id,
            "canonical_source_sha256": CANONICAL_SOURCE_SHA256,
            "source_hash216": _text(binding.source_hash216),
            "tokens_hash216": _text(binding.tokens_hash216),
            "ast_hash216": _text(binding.ast_hash216),
            "type_environment_hash216": _text(binding.type_environment_hash216),
            "constraint_graph_hash216": _text(binding.constraint_graph_hash216),
            "normalized_ir_hash216": _text(binding.normalized_ir_hash216),
            "vmir_hash216": _text(binding.vmir_hash216),
            "proof_hash216": _text(binding.proof_hash216),
            "transition_hash216": _text(binding.transition_hash216),
            "reverse_hash216": _text(binding.reverse_hash216),
            "receipt_hash72": _text(binding.receipt_hash72),
            "replay_hash72": _text(binding.replay_hash72),
            "reverse_hash72": _text(binding.reverse_hash72),
            "vm5184_address": int(binding.vm5184_address),
            "forward_vm81_steps": int(binding.forward_vm81_steps),
            "replay_vm81_steps": int(binding.replay_vm81_steps),
            "reverse_vm81_steps": int(binding.reverse_vm81_steps),
            "source_identity_exact": bool(binding.source_identity_exact),
            "pass159_frontend_chain_complete": bool(binding.pass159_frontend_chain_complete),
            "typed_proof_verified": bool(binding.typed_proof_verified),
            "interpreter_compiler_equality_verified": bool(binding.interpreter_compiler_match),
            "exact_vm81_admission_verified": bool(binding.exact_vm81_admission_verified),
            "atomic_commit_verified": bool(binding.atomic_commit_verified),
            "hash72_receipts_verified": bool(binding.hash72_receipts_verified),
            "hash216_identities_verified": bool(binding.hash216_identities_verified),
            "deterministic_replay_verified": bool(binding.deterministic_replay_verified),
            "reverse_restores_prior_state_verified": bool(binding.reverse_restores_prior_state_verified),
            "live_runtime_abi_verified": bool(binding.live_runtime_abi_verified),
            "canonical_computation_through_runtime_abi": bool(binding.canonical_computation_through_runtime_abi),
            "single_vm81_commit_authority": bool(binding.single_vm81_commit_authority),
            "fallback_used": bool(binding.fallback_used),
            "floating_point_canonical_authority": bool(binding.floating_point_authority),
            "hash216_persistence_authority": bool(binding.hash216_persistence_authority),
        }
        required_true = (
            "source_identity_exact",
            "pass159_frontend_chain_complete",
            "typed_proof_verified",
            "interpreter_compiler_equality_verified",
            "exact_vm81_admission_verified",
            "atomic_commit_verified",
            "hash72_receipts_verified",
            "hash216_identities_verified",
            "deterministic_replay_verified",
            "reverse_restores_prior_state_verified",
            "live_runtime_abi_verified",
            "canonical_computation_through_runtime_abi",
            "single_vm81_commit_authority",
        )
        if not all(record[name] is True for name in required_true):
            raise Pass169RuntimeBindingError("PASS169_I168_AUTHORITY_EVIDENCE_INCOMPLETE")
        if record["fallback_used"] or record["floating_point_canonical_authority"] or record["hash216_persistence_authority"]:
            raise Pass169RuntimeBindingError("PASS169_I168_AUTHORITY_BOUNDARY_VIOLATION")

        record["candidate_id"] = _stable_id("candidate", record["proof_hash216"])
        record["transition_id"] = _stable_id("transition", record["transition_hash216"])
        record["proof_id"] = _stable_id("proof", record["proof_hash216"])
        self._record = record
        return dict(record)

    def _check_identity(self, params: dict[str, Any], record: dict[str, Any]) -> None:
        source_id = params.get("source_id")
        if source_id not in (None, "", record["source_id"]):
            raise Pass169RuntimeBindingError("PASS169_NONCANONICAL_SOURCE_RUNTIME_AUTHORITY_DENIED")
        candidate_id = params.get("candidate_id")
        if candidate_id not in (None, "", record["candidate_id"]):
            raise Pass169RuntimeBindingError("PASS169_CANDIDATE_ID_NOT_FOUND")
        transition_id = params.get("transition_id")
        if transition_id not in (None, "", record["transition_id"], record["proof_id"]):
            raise Pass169RuntimeBindingError("PASS169_TRANSITION_ID_NOT_FOUND")

    def dispatch(self, operation: str, **params: Any) -> dict[str, Any]:
        op = operation.strip().lower()
        record = self.record()
        self._check_identity(params, record)
        common = {
            "ok": True,
            "contract": CONTRACT_ID,
            "operation": op,
            "source_id": record["source_id"],
            "runtime_abi_verified": True,
            "canonical_authority": True,
            "canonical_state_persisted": False,
            "floating_point_canonical_authority": False,
        }
        if op == "tokens":
            return {**common, "artifact_kind": "TOKEN_STREAM", "hash216": record["tokens_hash216"]}
        if op == "ast":
            return {**common, "artifact_kind": "AST", "hash216": record["ast_hash216"]}
        if op == "symbols":
            return {**common, "artifact_kind": "TYPE_ENVIRONMENT", "hash216": record["type_environment_hash216"]}
        if op == "constraints":
            return {**common, "artifact_kind": "CONSTRAINT_GRAPH", "hash216": record["constraint_graph_hash216"]}
        if op == "typecheck":
            return {**common, "verified": True, "type_environment_hash216": record["type_environment_hash216"]}
        if op == "normalize":
            return {**common, "normalized_ir_hash216": record["normalized_ir_hash216"], "vmir_hash216": record["vmir_hash216"]}
        if op in {"prove", "prove-constraint", "export-proof"}:
            return {**common, "proof_id": record["proof_id"], "proof_hash216": record["proof_hash216"], "typed_proof_verified": True}
        if op == "evaluate-candidate":
            return {**common, "candidate_id": record["candidate_id"], "proof_hash216": record["proof_hash216"], "candidate_verified": True}
        if op in {"admit", "validate"}:
            return {**common, "candidate_id": record["candidate_id"], "admitted": True, "vm5184_address": record["vm5184_address"]}
        if op == "commit":
            return {**common, "candidate_id": record["candidate_id"], "transition_id": record["transition_id"], "transition_hash216": record["transition_hash216"], "receipt_hash72": record["receipt_hash72"], "atomic_commit_verified": True}
        if op == "receipt":
            return {**common, "transition_id": record["transition_id"], "transition_hash216": record["transition_hash216"], "receipt_hash72": record["receipt_hash72"], "hash72_receipt_verified": True}
        if op == "replay":
            return {**common, "transition_id": record["transition_id"], "replay_hash72": record["replay_hash72"], "deterministic_replay_verified": True, "replay_vm81_steps": record["replay_vm81_steps"]}
        if op == "reverse":
            return {**common, "transition_id": record["transition_id"], "reverse_hash216": record["reverse_hash216"], "reverse_hash72": record["reverse_hash72"], "prior_state_restored": True, "reverse_vm81_steps": record["reverse_vm81_steps"]}
        if op == "inspect":
            return {**common, "candidate_id": record["candidate_id"], "transition_id": record["transition_id"], "proof_id": record["proof_id"], "proof_hash216": record["proof_hash216"], "transition_hash216": record["transition_hash216"]}
        if op == "divergence":
            return {**common, "transition_id": record["transition_id"], "divergence_detected": False, "deterministic_replay_verified": True}
        raise Pass169RuntimeBindingError(f"PASS169_RUNTIME_OPERATION_UNKNOWN:{operation}")


__all__ = [
    "CANONICAL_SOURCE_SHA256",
    "HHSExactPass219I168RuntimeBindingV1",
    "Pass169CanonicalRuntimeBinding",
    "Pass169RuntimeBindingError",
    "VERIFIED_OPERATIONS",
]
