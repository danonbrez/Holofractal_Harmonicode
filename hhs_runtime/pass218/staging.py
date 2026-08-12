"""Pass 218 Iteration 4 non-authoritative vector/VM5184 staging adapter.

Only a fully CLOSED Iteration-3 source transaction with a valid purge proof may
enter this layer. The adapter reuses inherited Pass 165 projection logic,
Pass 163 VMRC geometry, Pass 175 instruction addressing, and the Pass 217
authenticated vector-entry shape. It does not invoke canonical vector-store,
VM81, or learning commit authority.
"""
from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES
from hhs_runtime.pass165.ingestion import MultimodalLearningService, Token
from hhs_runtime.pass175.runtime import InstructionAddress

from .transaction import (
    Pass218TransactionValidationError,
    SourceTransaction,
    TransactionPhase,
)

PASS218_VECTOR_VM5184_STAGER_VERSION = "HHS-P218-VECTOR-VM5184-STAGER-I4-V1"


class Pass218VectorStageError(RuntimeError):
    pass


class Pass218VectorStageValidationError(Pass218VectorStageError):
    pass


class Pass218VectorStageStateError(Pass218VectorStageError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _copy(value: Any) -> Any:
    return json.loads(_canonical_bytes(value).decode("utf-8"))


def _valid_sha256(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _valid_hash216(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 216
        and all(validate_hash72(value[start:start + 72]) for start in (0, 72, 144))
    )


def _set_bit_positions(raw: bytes) -> tuple[int, ...]:
    if len(raw) != SNAPSHOT_BYTES:
        raise Pass218VectorStageValidationError("P218_I4_VM5184_LENGTH_INVALID")
    return tuple(
        index
        for index in range(COORDINATES)
        if (raw[index // 8] >> (7 - (index % 8))) & 1
    )


def _beat_token(beat: Mapping[str, Any], transaction_id_hash72: str) -> Token:
    ordinal = int(beat.get("ordinal", -1))
    beat_hash72 = str(beat.get("beat_hash72", ""))
    source_span_sha256 = str(beat.get("source_span_sha256", ""))
    if ordinal < 0:
        raise Pass218VectorStageValidationError("P218_I4_BEAT_ORDINAL_INVALID")
    if not validate_hash72(beat_hash72):
        raise Pass218VectorStageValidationError("P218_I4_BEAT_HASH72_INVALID")
    if not _valid_sha256(source_span_sha256):
        raise Pass218VectorStageValidationError("P218_I4_BEAT_SOURCE_DIGEST_INVALID")
    relation_types = tuple(sorted(str(v) for v in beat.get("relation_types", [])))
    token_body = {
        "domain": "HHS-P218-I4-STRUCTURAL-BEAT-TOKEN-V1",
        "transaction_id_hash72": transaction_id_hash72,
        "ordinal": ordinal,
        "beat_hash72": beat_hash72,
        "source_span_sha256": source_span_sha256,
        "paragraph_count": int(beat.get("paragraph_count", 0)),
        "token_count": int(beat.get("token_count", 0)),
        "sentence_count": int(beat.get("sentence_count", 0)),
        "dialogue_turn_count": int(beat.get("dialogue_turn_count", 0)),
        "negation_count": int(beat.get("negation_count", 0)),
        "modal_count": int(beat.get("modal_count", 0)),
        "authority_count": int(beat.get("authority_count", 0)),
        "temporal_count": int(beat.get("temporal_count", 0)),
        "dominant_perspective": str(beat.get("dominant_perspective", "UNSPECIFIED")),
        "relation_types": list(relation_types),
    }
    token_id = sha256(_canonical_bytes(token_body)).hexdigest()
    return Token(
        token_id=token_id,
        modality="HHS_VECTOR_PACKET",
        token_class="P218_STRUCTURAL_NARRATIVE_BEAT",
        canonical_payload=beat_hash72,
        source_span=(ordinal, ordinal + 1),
        temporal_span=(ordinal, ordinal + 1),
        spatial_span=None,
        structural_path=f"p218/transaction/{transaction_id_hash72}/beat/{ordinal}",
        local_relations=relation_types,
        provenance_root=source_span_sha256,
    )


def _projection_edges(tokens: Sequence[Token]) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (left.token_id, right.token_id, "PRECEDES")
        for left, right in zip(tokens, tokens[1:])
    )


def _dependency_frontier(beats: Sequence[Mapping[str, Any]]) -> tuple[int, ...]:
    positions = {
        int.from_bytes(
            sha256(
                (
                    str(beat.get("beat_hash72", ""))
                    + ":"
                    + str(beat.get("source_span_sha256", ""))
                ).encode("ascii")
            ).digest()[:2],
            "big",
        )
        % COORDINATES
        for beat in beats
    }
    return tuple(sorted(positions))


def _ordered_path(forward_support: Sequence[int]) -> tuple[str, ...]:
    selected = tuple(forward_support[:32])
    if not selected:
        selected = (0,)
    out = []
    for state in selected:
        address = InstructionAddress.from_state(state)
        out.append(
            f"VM5184/{address.state}/CELL/{address.cell}/OP/{address.operation}"
        )
    return tuple(out)


@dataclass(frozen=True)
class VectorVM5184StageCandidate:
    transaction_id_hash72: str
    transaction_hash216: str
    structural_record_hash72: str
    purge_receipt_hash72: str
    vector_entry: Mapping[str, Any]
    projection_bytes: bytes
    projection_hash72: str
    projection_sha256: str
    staging_hash72: str
    validation_hash72: str
    staging_hash216: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-I4-VECTOR-VM5184-STAGE-CANDIDATE-V1",
            "stager_version": PASS218_VECTOR_VM5184_STAGER_VERSION,
            "transaction_id_hash72": self.transaction_id_hash72,
            "transaction_hash216": self.transaction_hash216,
            "structural_record_hash72": self.structural_record_hash72,
            "purge_receipt_hash72": self.purge_receipt_hash72,
            "vector_entry": _copy(self.vector_entry),
            "vm5184_projection_b64": b64encode(self.projection_bytes).decode("ascii"),
            "vm5184_projection_bytes": len(self.projection_bytes),
            "vm5184_projection_hash72": self.projection_hash72,
            "vm5184_projection_sha256": self.projection_sha256,
            "vm5184_projection_popcount": len(self.vector_entry["forward_support"]),
            "staging_hash72": self.staging_hash72,
            "validation_hash72": self.validation_hash72,
            "staging_hash216": self.staging_hash216,
            "hash216_semantics": [
                "CLOSED_SOURCE_TRANSACTION",
                "VECTOR_VM5184_STAGE_CANDIDATE",
                "STAGING_VALIDATION_RECEIPT",
            ],
            "inherited_projection_surface": "PASS165_MULTIMODAL_LEARNING_SERVICE_PROJECT_5184",
            "inherited_vm_geometry": "PASS163_VMRC_81x64",
            "inherited_instruction_addressing": "PASS175_INSTRUCTION_ADDRESS",
            "inherited_vector_entry_contract": "HHS_PASS_217_VECTOR_STORE_ENTRY_V1",
            "verbatim_source_retained": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "authoritative_vector_store_promotion": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "authoritative_float_weights": False,
        }


class NonAuthoritativeVectorStageStore:
    """Content-addressed candidate store outside canonical vector/VM81 authority."""

    def __init__(self) -> None:
        self._candidates: dict[str, dict[str, Any]] = {}

    def stage(self, candidate: VectorVM5184StageCandidate) -> dict[str, Any]:
        record = candidate.to_record()
        entry = record["vector_entry"]
        if entry.get("admission_status") != "CANDIDATE":
            raise Pass218VectorStageValidationError("P218_I4_STAGE_NOT_CANDIDATE")
        if record.get("authoritative_vector_store_promotion") is not False:
            raise Pass218VectorStageValidationError("P218_I4_AUTHORITY_FLAG_INVALID")
        key = str(entry["entry_id_sha256"])
        existing = self._candidates.get(key)
        if existing is not None:
            if existing != record:
                raise Pass218VectorStageStateError("P218_I4_STAGE_IDENTITY_CONFLICT")
            return _copy(existing)
        self._candidates[key] = _copy(record)
        return _copy(record)

    def get(self, entry_id_sha256: str) -> dict[str, Any] | None:
        value = self._candidates.get(entry_id_sha256)
        return None if value is None else _copy(value)

    def record(self) -> dict[str, Any]:
        rows = [
            {
                "entry_id_sha256": key,
                "staging_hash72": value["staging_hash72"],
                "validation_hash72": value["validation_hash72"],
            }
            for key, value in sorted(self._candidates.items())
        ]
        return {
            "schema": "HHS-P218-I4-NONAUTHORITATIVE-VECTOR-STAGE-STORE-V1",
            "candidate_count": len(rows),
            "candidate_rows": rows,
            "stage_root_hash72": hash72_digest(
                {"domain": "HHS-P218-I4-VECTOR-STAGE-STORE-ROOT-V1"}, rows
            ),
            "authoritative_vector_store": False,
            "vm81_commit_authority": False,
        }


class ClosedTransactionVectorVM5184Adapter:
    def __init__(self, *, stage_store: NonAuthoritativeVectorStageStore | None = None) -> None:
        self.stage_store = stage_store or NonAuthoritativeVectorStageStore()

    @staticmethod
    def _restore_closed(snapshot: Mapping[str, Any]) -> SourceTransaction:
        try:
            transaction = SourceTransaction.restore(snapshot)
        except Pass218TransactionValidationError as exc:
            raise Pass218VectorStageValidationError(
                "P218_I4_TRANSACTION_RESTORE_INVALID:" + str(exc)
            ) from exc
        if transaction.phase != TransactionPhase.CLOSED:
            raise Pass218VectorStageValidationError(
                "P218_I4_TRANSACTION_NOT_CLOSED"
            )
        closure = transaction.closure_receipt
        purge = transaction.purge_receipt
        if not isinstance(closure, Mapping) or not isinstance(purge, Mapping):
            raise Pass218VectorStageValidationError(
                "P218_I4_PURGE_OR_CLOSURE_RECEIPT_MISSING"
            )
        if (
            closure.get("managed_buffer_zeroized") is not True
            or closure.get("managed_buffer_cleared") is not True
            or closure.get("verbatim_source_retained") is not False
            or closure.get("truth_promotion") is not False
            or closure.get("action_authority_minted") is not False
            or closure.get("authoritative_vector_store_promotion") is not False
        ):
            raise Pass218VectorStageValidationError(
                "P218_I4_CLOSURE_AUTHORITY_OR_PURGE_INVALID"
            )
        if (
            purge.get("managed_buffer_zeroized") is not True
            or purge.get("managed_buffer_cleared") is not True
            or purge.get("verbatim_source_retained") is not False
            or purge.get("physical_memory_erasure_claimed") is not False
        ):
            raise Pass218VectorStageValidationError("P218_I4_PURGE_PROOF_INVALID")
        if closure.get("purge_receipt_hash72") != purge.get("purge_receipt_hash72"):
            raise Pass218VectorStageValidationError(
                "P218_I4_PURGE_RECEIPT_MISMATCH"
            )
        admitted = transaction.store.admitted_record(transaction.transaction_id_hash72)
        if admitted is None:
            raise Pass218VectorStageValidationError(
                "P218_I4_STRUCTURAL_RECORD_NOT_ADMITTED"
            )
        return transaction

    @staticmethod
    def _validate_vector_entry(entry: Mapping[str, Any]) -> None:
        required = {
            "schema",
            "entry_id_sha256",
            "parent_state_sha256",
            "candidate_state_sha256",
            "hash216_transition_sha256",
            "forward_support",
            "inverse_support",
            "ordered_path",
            "bracketing",
            "dependency_frontier",
            "collision_bucket",
            "admission_status",
        }
        if set(entry) != required:
            raise Pass218VectorStageValidationError(
                "P218_I4_VECTOR_ENTRY_FIELD_SET_INVALID"
            )
        if entry["schema"] != "HHS_PASS_217_VECTOR_STORE_ENTRY_V1":
            raise Pass218VectorStageValidationError(
                "P218_I4_VECTOR_ENTRY_SCHEMA_INVALID"
            )
        for key in (
            "entry_id_sha256",
            "parent_state_sha256",
            "candidate_state_sha256",
            "hash216_transition_sha256",
        ):
            if not _valid_sha256(str(entry[key])):
                raise Pass218VectorStageValidationError(
                    "P218_I4_VECTOR_ENTRY_SHA256_INVALID:" + key
                )
        for key in ("forward_support", "inverse_support", "dependency_frontier"):
            values = list(entry[key])
            if (
                values != sorted(set(values))
                or any(not isinstance(v, int) or not 0 <= v < COORDINATES for v in values)
            ):
                raise Pass218VectorStageValidationError(
                    "P218_I4_VECTOR_ENTRY_SUPPORT_INVALID:" + key
                )
        if not isinstance(entry["ordered_path"], list) or not entry["ordered_path"]:
            raise Pass218VectorStageValidationError(
                "P218_I4_VECTOR_ENTRY_ORDERED_PATH_INVALID"
            )
        if entry["admission_status"] != "CANDIDATE":
            raise Pass218VectorStageValidationError(
                "P218_I4_VECTOR_ENTRY_AUTHORITY_INVALID"
            )
        if not isinstance(entry["collision_bucket"], int) or entry["collision_bucket"] < 0:
            raise Pass218VectorStageValidationError(
                "P218_I4_VECTOR_ENTRY_COLLISION_BUCKET_INVALID"
            )

    def build(self, snapshot: Mapping[str, Any]) -> VectorVM5184StageCandidate:
        transaction = self._restore_closed(snapshot)
        closure = transaction.closure_receipt
        purge = transaction.purge_receipt
        assert closure is not None and purge is not None
        structural = transaction.store.admitted_record(transaction.transaction_id_hash72)
        assert structural is not None

        structural_hash72 = str(closure["structural_record_hash72"])
        recomputed_structural_hash72 = hash72_digest(
            {"domain": "HHS-P218-I3-STRUCTURAL-RECORD-V1"}, structural
        )
        if recomputed_structural_hash72 != structural_hash72:
            raise Pass218VectorStageValidationError(
                "P218_I4_STRUCTURAL_RECORD_HASH_MISMATCH"
            )

        beats = structural.get("beats")
        if not isinstance(beats, list) or not beats:
            raise Pass218VectorStageValidationError("P218_I4_STRUCTURAL_BEATS_EMPTY")

        tokens = tuple(
            _beat_token(beat, transaction.transaction_id_hash72)
            for beat in beats
        )
        edges = _projection_edges(tokens)
        projection = MultimodalLearningService.project_5184(tokens, edges).to_bytes()
        forward_support = _set_bit_positions(projection)
        forward_set = set(forward_support)
        inverse_support = tuple(
            index for index in range(COORDINATES) if index not in forward_set
        )
        dependency_frontier = _dependency_frontier(beats)
        projection_hash72 = hash72_digest(b"", projection)
        projection_sha256 = sha256(projection).hexdigest()
        transaction_hash216 = str(closure["transaction_hash216"])
        if not _valid_hash216(transaction_hash216):
            raise Pass218VectorStageValidationError(
                "P218_I4_CLOSED_TRANSACTION_HASH216_INVALID"
            )

        parent_state_sha256 = sha256(
            (
                transaction.transaction_id_hash72
                + ":"
                + structural_hash72
                + ":"
                + str(purge["purge_receipt_hash72"])
            ).encode("ascii")
        ).hexdigest()
        candidate_state_sha256 = sha256(
            projection
            + structural_hash72.encode("ascii")
            + projection_hash72.encode("ascii")
        ).hexdigest()
        hash216_transition_sha256 = sha256(
            transaction_hash216.encode("ascii")
        ).hexdigest()
        entry_body = {
            "schema": "HHS_PASS_217_VECTOR_STORE_ENTRY_V1",
            "parent_state_sha256": parent_state_sha256,
            "candidate_state_sha256": candidate_state_sha256,
            "hash216_transition_sha256": hash216_transition_sha256,
            "forward_support": list(forward_support),
            "inverse_support": list(inverse_support),
            "ordered_path": list(_ordered_path(forward_support)),
            "bracketing": "P218_I4_NONAUTHORITATIVE_CLOSED_TRANSACTION_STAGE",
            "dependency_frontier": list(dependency_frontier),
            "collision_bucket": max(0, (len(tokens) + len(edges)) * 3 - len(forward_support)),
            "admission_status": "CANDIDATE",
        }
        entry_id_sha256 = sha256(
            b"HHS-P218-I4-P217-VECTOR-ENTRY\0" + _canonical_bytes(entry_body)
        ).hexdigest()
        vector_entry = {"entry_id_sha256": entry_id_sha256, **entry_body}
        self._validate_vector_entry(vector_entry)

        staging_payload = {
            "schema": "HHS-P218-I4-VECTOR-VM5184-STAGING-V1",
            "stager_version": PASS218_VECTOR_VM5184_STAGER_VERSION,
            "transaction_id_hash72": transaction.transaction_id_hash72,
            "transaction_hash216_sha256": hash216_transition_sha256,
            "structural_record_hash72": structural_hash72,
            "purge_receipt_hash72": str(purge["purge_receipt_hash72"]),
            "vector_entry": vector_entry,
            "vm5184_projection_hash72": projection_hash72,
            "vm5184_projection_sha256": projection_sha256,
            "vm5184_projection_bytes": len(projection),
            "inherited_projection_surface": "PASS165_MULTIMODAL_LEARNING_SERVICE_PROJECT_5184",
            "inherited_vm_geometry": "PASS163_VMRC_81x64",
            "inherited_instruction_addressing": "PASS175_INSTRUCTION_ADDRESS",
            "authoritative_vector_store_promotion": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "verbatim_source_retained": False,
        }
        staging_hash72 = hash72_digest(
            {"domain": "HHS-P218-I4-VECTOR-VM5184-STAGING-V1"}, staging_payload
        )
        validation_payload = {
            "schema": "HHS-P218-I4-VECTOR-VM5184-STAGING-VALIDATION-V1",
            "transaction_id_hash72": transaction.transaction_id_hash72,
            "staging_hash72": staging_hash72,
            "projection_length_exact": len(projection) == SNAPSHOT_BYTES,
            "projection_support_partition_complete": (
                len(forward_support) + len(inverse_support) == COORDINATES
            ),
            "projection_support_disjoint": not (
                set(forward_support) & set(inverse_support)
            ),
            "closed_transaction_required": True,
            "purge_proof_required": True,
            "vector_admission_status": "CANDIDATE",
            "authoritative_vector_store_promotion": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "authoritative_float_weights": False,
        }
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I4-VECTOR-VM5184-STAGING-VALIDATION-V1"},
            validation_payload,
        )
        staging_hash216 = (
            str(closure["closure_hash72"]) + staging_hash72 + validation_hash72
        )
        if not _valid_hash216(staging_hash216):
            raise Pass218VectorStageValidationError(
                "P218_I4_STAGING_HASH216_INVALID"
            )
        return VectorVM5184StageCandidate(
            transaction_id_hash72=transaction.transaction_id_hash72,
            transaction_hash216=transaction_hash216,
            structural_record_hash72=structural_hash72,
            purge_receipt_hash72=str(purge["purge_receipt_hash72"]),
            vector_entry=vector_entry,
            projection_bytes=projection,
            projection_hash72=projection_hash72,
            projection_sha256=projection_sha256,
            staging_hash72=staging_hash72,
            validation_hash72=validation_hash72,
            staging_hash216=staging_hash216,
        )

    def stage(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        candidate = self.build(snapshot)
        return self.stage_store.stage(candidate)
