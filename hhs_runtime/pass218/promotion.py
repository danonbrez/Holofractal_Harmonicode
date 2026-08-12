"""Pass 218 Iteration 5 promotion-admission proof membrane.

This layer proves that an Iteration-4 candidate is reproducible from the exact
closed/purge-proven source transaction and binds an explicit caller-supplied
authority grant to that exact proof. It does not perform canonical vector,
learning, or VM81 mutation. The resulting authorization envelope is the sole
input a later canonical target adapter may accept.
"""
from __future__ import annotations

from base64 import b64decode
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass163.vmrc import COORDINATES, SNAPSHOT_BYTES

from .staging import (
    ClosedTransactionVectorVM5184Adapter,
    Pass218VectorStageValidationError,
)

PASS218_PROMOTION_MEMBRANE_VERSION = "HHS-P218-PROMOTION-ADMISSION-I5-V1"
PROMOTION_SCOPE = "PASS217_VECTOR_VM5184_PROMOTION"


class Pass218PromotionError(RuntimeError):
    pass


class Pass218PromotionValidationError(Pass218PromotionError):
    pass


class Pass218PromotionStateError(Pass218PromotionError):
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


def _projection_support(raw: bytes) -> tuple[int, ...]:
    if len(raw) != SNAPSHOT_BYTES:
        raise Pass218PromotionValidationError("P218_I5_PROJECTION_LENGTH_INVALID")
    return tuple(
        index
        for index in range(COORDINATES)
        if (raw[index // 8] >> (7 - (index % 8))) & 1
    )


def _entry_identity(entry: Mapping[str, Any]) -> str:
    body = {key: _copy(value) for key, value in entry.items() if key != "entry_id_sha256"}
    return sha256(
        b"HHS-P218-I4-P217-VECTOR-ENTRY\0" + _canonical_bytes(body)
    ).hexdigest()


@dataclass(frozen=True)
class PromotionProof:
    transaction_id_hash72: str
    entry_id_sha256: str
    staging_hash72: str
    staging_validation_hash72: str
    staging_hash216: str
    projection_hash72: str
    projection_sha256: str
    dependency_scope_hash72: str
    vector_entry_sha256: str
    proof_hash72: str
    validation_hash72: str
    proof_hash216: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-I5-PROMOTION-PROOF-V1",
            "membrane_version": PASS218_PROMOTION_MEMBRANE_VERSION,
            "transaction_id_hash72": self.transaction_id_hash72,
            "entry_id_sha256": self.entry_id_sha256,
            "staging_hash72": self.staging_hash72,
            "staging_validation_hash72": self.staging_validation_hash72,
            "staging_hash216": self.staging_hash216,
            "projection_hash72": self.projection_hash72,
            "projection_sha256": self.projection_sha256,
            "dependency_scope_hash72": self.dependency_scope_hash72,
            "vector_entry_sha256": self.vector_entry_sha256,
            "proof_hash72": self.proof_hash72,
            "validation_hash72": self.validation_hash72,
            "proof_hash216": self.proof_hash216,
            "hash216_semantics": [
                "VECTOR_VM5184_STAGE_CANDIDATE",
                "PROMOTABILITY_PROOF",
                "PROOF_VALIDATION_RECEIPT",
            ],
            "promotable": True,
            "explicit_authority_grant_present": False,
            "canonical_mutation_permitted": False,
            "canonical_vector_store_mutation_invoked": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "authoritative_float_weights": False,
        }


@dataclass(frozen=True)
class PromotionAuthorityGrant:
    grantor_authority_hash72: str
    grant_sequence: int
    target_scope: str
    entry_id_sha256: str
    staging_hash72: str
    projection_sha256: str
    proof_hash72: str
    grant_hash72: str
    validation_hash72: str
    grant_hash216: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-I5-PROMOTION-AUTHORITY-GRANT-V1",
            "membrane_version": PASS218_PROMOTION_MEMBRANE_VERSION,
            "grantor_authority_hash72": self.grantor_authority_hash72,
            "grant_sequence": self.grant_sequence,
            "target_scope": self.target_scope,
            "entry_id_sha256": self.entry_id_sha256,
            "staging_hash72": self.staging_hash72,
            "projection_sha256": self.projection_sha256,
            "proof_hash72": self.proof_hash72,
            "grant_hash72": self.grant_hash72,
            "validation_hash72": self.validation_hash72,
            "grant_hash216": self.grant_hash216,
            "hash216_semantics": [
                "PROMOTABILITY_PROOF",
                "EXPLICIT_PROMOTION_GRANT",
                "GRANT_VALIDATION_RECEIPT",
            ],
            "grant_authorizes_only_exact_candidate": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "learning_authority_granted": False,
            "canonical_mutation_invoked": False,
        }

    @classmethod
    def bind(
        cls,
        proof: "PromotionProof | Mapping[str, Any]",
        *,
        grantor_authority_hash72: str,
        grant_sequence: int,
        target_scope: str = PROMOTION_SCOPE,
    ) -> "PromotionAuthorityGrant":
        proof_record = proof.to_record() if isinstance(proof, PromotionProof) else _copy(proof)
        PromotionProofMembrane.validate_proof_record(proof_record)
        if not validate_hash72(grantor_authority_hash72):
            raise Pass218PromotionValidationError("P218_I5_GRANTOR_AUTHORITY_HASH72_INVALID")
        if not isinstance(grant_sequence, int) or isinstance(grant_sequence, bool) or grant_sequence < 0:
            raise Pass218PromotionValidationError("P218_I5_GRANT_SEQUENCE_INVALID")
        if target_scope != PROMOTION_SCOPE:
            raise Pass218PromotionValidationError("P218_I5_GRANT_SCOPE_INVALID")
        payload = {
            "schema": "HHS-P218-I5-PROMOTION-AUTHORITY-GRANT-PAYLOAD-V1",
            "grantor_authority_hash72": grantor_authority_hash72,
            "grant_sequence": grant_sequence,
            "target_scope": target_scope,
            "entry_id_sha256": proof_record["entry_id_sha256"],
            "staging_hash72": proof_record["staging_hash72"],
            "projection_sha256": proof_record["projection_sha256"],
            "proof_hash72": proof_record["proof_hash72"],
        }
        grant_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTION-AUTHORITY-GRANT-V1"}, payload
        )
        validation_payload = {
            "schema": "HHS-P218-I5-PROMOTION-GRANT-VALIDATION-V1",
            "grant_hash72": grant_hash72,
            "grantor_authority_hash72": grantor_authority_hash72,
            "grant_sequence": grant_sequence,
            "scope_exact": target_scope == PROMOTION_SCOPE,
            "candidate_exact": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "learning_authority_granted": False,
        }
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTION-GRANT-VALIDATION-V1"},
            validation_payload,
        )
        grant_hash216 = proof_record["proof_hash72"] + grant_hash72 + validation_hash72
        if not _valid_hash216(grant_hash216):
            raise Pass218PromotionValidationError("P218_I5_GRANT_HASH216_INVALID")
        return cls(
            grantor_authority_hash72=grantor_authority_hash72,
            grant_sequence=grant_sequence,
            target_scope=target_scope,
            entry_id_sha256=str(proof_record["entry_id_sha256"]),
            staging_hash72=str(proof_record["staging_hash72"]),
            projection_sha256=str(proof_record["projection_sha256"]),
            proof_hash72=str(proof_record["proof_hash72"]),
            grant_hash72=grant_hash72,
            validation_hash72=validation_hash72,
            grant_hash216=grant_hash216,
        )


@dataclass(frozen=True)
class PromotionAuthorization:
    authorization_hash72: str
    validation_hash72: str
    authorization_hash216: str
    entry_id_sha256: str
    proof_hash72: str
    grant_hash72: str
    staging_hash72: str
    projection_sha256: str
    target_scope: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-I5-PROMOTION-AUTHORIZATION-V1",
            "membrane_version": PASS218_PROMOTION_MEMBRANE_VERSION,
            "authorization_hash72": self.authorization_hash72,
            "validation_hash72": self.validation_hash72,
            "authorization_hash216": self.authorization_hash216,
            "hash216_semantics": [
                "PROMOTABILITY_PROOF",
                "EXPLICIT_AUTHORITY_GRANT",
                "PROMOTION_AUTHORIZATION_RECEIPT",
            ],
            "entry_id_sha256": self.entry_id_sha256,
            "proof_hash72": self.proof_hash72,
            "grant_hash72": self.grant_hash72,
            "staging_hash72": self.staging_hash72,
            "projection_sha256": self.projection_sha256,
            "target_scope": self.target_scope,
            "state": "AUTHORIZED_PENDING_CANONICAL_COMMIT",
            "proof_required": True,
            "grant_required": True,
            "canonical_mutation_permitted": True,
            "canonical_vector_store_mutation_invoked": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
        }


class PromotionProofMembrane:
    @staticmethod
    def validate_proof_record(record: Mapping[str, Any]) -> None:
        required_hash72 = (
            "transaction_id_hash72",
            "staging_hash72",
            "staging_validation_hash72",
            "projection_hash72",
            "dependency_scope_hash72",
            "proof_hash72",
            "validation_hash72",
        )
        if record.get("schema") != "HHS-P218-I5-PROMOTION-PROOF-V1":
            raise Pass218PromotionValidationError("P218_I5_PROOF_SCHEMA_INVALID")
        if any(not validate_hash72(str(record.get(key, ""))) for key in required_hash72):
            raise Pass218PromotionValidationError("P218_I5_PROOF_HASH72_INVALID")
        for key in ("entry_id_sha256", "projection_sha256", "vector_entry_sha256"):
            if not _valid_sha256(str(record.get(key, ""))):
                raise Pass218PromotionValidationError("P218_I5_PROOF_SHA256_INVALID:" + key)
        for key in ("staging_hash216", "proof_hash216"):
            if not _valid_hash216(str(record.get(key, ""))):
                raise Pass218PromotionValidationError("P218_I5_PROOF_HASH216_INVALID:" + key)
        if record.get("promotable") is not True:
            raise Pass218PromotionValidationError("P218_I5_PROOF_NOT_PROMOTABLE")
        if record.get("explicit_authority_grant_present") is not False:
            raise Pass218PromotionValidationError("P218_I5_PROOF_MUST_NOT_SELF_GRANT")
        if record.get("canonical_mutation_permitted") is not False:
            raise Pass218PromotionValidationError("P218_I5_PROOF_MUST_NOT_AUTHORIZE_MUTATION")
        expected_payload = {
            "schema": "HHS-P218-I5-PROMOTABILITY-PROOF-PAYLOAD-V1",
            "transaction_id_hash72": record["transaction_id_hash72"],
            "entry_id_sha256": record["entry_id_sha256"],
            "staging_hash72": record["staging_hash72"],
            "staging_validation_hash72": record["staging_validation_hash72"],
            "staging_hash216": record["staging_hash216"],
            "projection_hash72": record["projection_hash72"],
            "projection_sha256": record["projection_sha256"],
            "dependency_scope_hash72": record["dependency_scope_hash72"],
            "vector_entry_sha256": record["vector_entry_sha256"],
            "exact_stage_replay": True,
            "pass217_entry_identity_exact": True,
            "vm5184_projection_exact": True,
            "dependency_scope_exact": True,
            "candidate_only": True,
            "verbatim_source_retained": False,
        }
        expected_proof_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTABILITY-PROOF-V1"},
            expected_payload,
        )
        if record["proof_hash72"] != expected_proof_hash72:
            raise Pass218PromotionValidationError("P218_I5_PROOF_HASH72_MISMATCH")
        expected_validation_payload = {
            "schema": "HHS-P218-I5-PROMOTABILITY-PROOF-VALIDATION-V1",
            "proof_hash72": expected_proof_hash72,
            "entry_id_sha256": record["entry_id_sha256"],
            "exact_stage_replay": True,
            "support_partition_complete": True,
            "support_partition_disjoint": True,
            "explicit_authority_grant_present": False,
            "canonical_mutation_permitted": False,
            "truth_promotion": False,
            "action_authority_minted": False,
        }
        expected_validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTABILITY-PROOF-VALIDATION-V1"},
            expected_validation_payload,
        )
        if record["validation_hash72"] != expected_validation_hash72:
            raise Pass218PromotionValidationError("P218_I5_PROOF_VALIDATION_HASH72_MISMATCH")
        expected_hash216 = (
            str(record["staging_hash72"])
            + expected_proof_hash72
            + expected_validation_hash72
        )
        if record["proof_hash216"] != expected_hash216:
            raise Pass218PromotionValidationError("P218_I5_PROOF_HASH216_LANE_MISMATCH")

    @staticmethod
    def _validate_stage_geometry(stage: Mapping[str, Any]) -> None:
        entry = stage.get("vector_entry")
        if not isinstance(entry, Mapping):
            raise Pass218PromotionValidationError("P218_I5_VECTOR_ENTRY_MISSING")
        if entry.get("schema") != "HHS_PASS_217_VECTOR_STORE_ENTRY_V1":
            raise Pass218PromotionValidationError("P218_I5_VECTOR_ENTRY_SCHEMA_INVALID")
        if entry.get("admission_status") != "CANDIDATE":
            raise Pass218PromotionValidationError("P218_I5_STAGE_NOT_CANDIDATE")
        if _entry_identity(entry) != entry.get("entry_id_sha256"):
            raise Pass218PromotionValidationError("P218_I5_VECTOR_ENTRY_IDENTITY_MISMATCH")
        try:
            projection = b64decode(str(stage["vm5184_projection_b64"]), validate=True)
        except Exception as exc:
            raise Pass218PromotionValidationError("P218_I5_PROJECTION_B64_INVALID") from exc
        if len(projection) != SNAPSHOT_BYTES:
            raise Pass218PromotionValidationError("P218_I5_PROJECTION_LENGTH_INVALID")
        if sha256(projection).hexdigest() != stage.get("vm5184_projection_sha256"):
            raise Pass218PromotionValidationError("P218_I5_PROJECTION_SHA256_MISMATCH")
        if hash72_digest(b"", projection) != stage.get("vm5184_projection_hash72"):
            raise Pass218PromotionValidationError("P218_I5_PROJECTION_HASH72_MISMATCH")
        support = _projection_support(projection)
        forward = tuple(entry.get("forward_support", ()))
        inverse = tuple(entry.get("inverse_support", ()))
        if support != forward:
            raise Pass218PromotionValidationError("P218_I5_FORWARD_SUPPORT_MISMATCH")
        forward_set = set(forward)
        expected_inverse = tuple(index for index in range(COORDINATES) if index not in forward_set)
        if inverse != expected_inverse:
            raise Pass218PromotionValidationError("P218_I5_INVERSE_SUPPORT_MISMATCH")
        frontier = tuple(entry.get("dependency_frontier", ()))
        if (
            frontier != tuple(sorted(set(frontier)))
            or any(not isinstance(value, int) or not 0 <= value < COORDINATES for value in frontier)
        ):
            raise Pass218PromotionValidationError("P218_I5_DEPENDENCY_FRONTIER_INVALID")
        if stage.get("authoritative_vector_store_promotion") is not False:
            raise Pass218PromotionValidationError("P218_I5_STAGE_AUTHORITY_FLAG_INVALID")
        if stage.get("canonical_vm81_commit_invoked") is not False:
            raise Pass218PromotionValidationError("P218_I5_STAGE_VM81_FLAG_INVALID")
        if stage.get("canonical_learning_commit_invoked") is not False:
            raise Pass218PromotionValidationError("P218_I5_STAGE_LEARNING_FLAG_INVALID")

    def prove(
        self,
        *,
        closed_transaction_snapshot: Mapping[str, Any],
        staged_candidate: Mapping[str, Any],
    ) -> PromotionProof:
        try:
            reproduced = ClosedTransactionVectorVM5184Adapter().stage(
                closed_transaction_snapshot
            )
        except Pass218VectorStageValidationError as exc:
            raise Pass218PromotionValidationError(
                "P218_I5_STAGE_REPLAY_INVALID:" + str(exc)
            ) from exc
        staged = _copy(staged_candidate)
        if reproduced != staged:
            raise Pass218PromotionValidationError("P218_I5_EXACT_STAGE_REPLAY_MISMATCH")
        self._validate_stage_geometry(staged)

        entry = staged["vector_entry"]
        dependency_payload = {
            "schema": "HHS-P218-I5-DEPENDENCY-SCOPE-V1",
            "entry_id_sha256": entry["entry_id_sha256"],
            "forward_support": entry["forward_support"],
            "dependency_frontier": entry["dependency_frontier"],
            "ordered_path": entry["ordered_path"],
        }
        dependency_scope_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-DEPENDENCY-SCOPE-V1"},
            dependency_payload,
        )
        vector_entry_sha256 = sha256(_canonical_bytes(entry)).hexdigest()
        proof_payload = {
            "schema": "HHS-P218-I5-PROMOTABILITY-PROOF-PAYLOAD-V1",
            "transaction_id_hash72": staged["transaction_id_hash72"],
            "entry_id_sha256": entry["entry_id_sha256"],
            "staging_hash72": staged["staging_hash72"],
            "staging_validation_hash72": staged["validation_hash72"],
            "staging_hash216": staged["staging_hash216"],
            "projection_hash72": staged["vm5184_projection_hash72"],
            "projection_sha256": staged["vm5184_projection_sha256"],
            "dependency_scope_hash72": dependency_scope_hash72,
            "vector_entry_sha256": vector_entry_sha256,
            "exact_stage_replay": True,
            "pass217_entry_identity_exact": True,
            "vm5184_projection_exact": True,
            "dependency_scope_exact": True,
            "candidate_only": True,
            "verbatim_source_retained": False,
        }
        proof_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTABILITY-PROOF-V1"},
            proof_payload,
        )
        validation_payload = {
            "schema": "HHS-P218-I5-PROMOTABILITY-PROOF-VALIDATION-V1",
            "proof_hash72": proof_hash72,
            "entry_id_sha256": entry["entry_id_sha256"],
            "exact_stage_replay": True,
            "support_partition_complete": (
                len(entry["forward_support"]) + len(entry["inverse_support"])
                == COORDINATES
            ),
            "support_partition_disjoint": not (
                set(entry["forward_support"]) & set(entry["inverse_support"])
            ),
            "explicit_authority_grant_present": False,
            "canonical_mutation_permitted": False,
            "truth_promotion": False,
            "action_authority_minted": False,
        }
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTABILITY-PROOF-VALIDATION-V1"},
            validation_payload,
        )
        proof_hash216 = staged["staging_hash72"] + proof_hash72 + validation_hash72
        if not _valid_hash216(proof_hash216):
            raise Pass218PromotionValidationError("P218_I5_PROOF_HASH216_INVALID")
        proof = PromotionProof(
            transaction_id_hash72=str(staged["transaction_id_hash72"]),
            entry_id_sha256=str(entry["entry_id_sha256"]),
            staging_hash72=str(staged["staging_hash72"]),
            staging_validation_hash72=str(staged["validation_hash72"]),
            staging_hash216=str(staged["staging_hash216"]),
            projection_hash72=str(staged["vm5184_projection_hash72"]),
            projection_sha256=str(staged["vm5184_projection_sha256"]),
            dependency_scope_hash72=dependency_scope_hash72,
            vector_entry_sha256=vector_entry_sha256,
            proof_hash72=proof_hash72,
            validation_hash72=validation_hash72,
            proof_hash216=proof_hash216,
        )
        self.validate_proof_record(proof.to_record())
        return proof


class PromotionAuthorizationJournal:
    """Non-canonical authorization journal with deterministic pre-commit rollback."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _validate_grant(
        proof_record: Mapping[str, Any],
        grant_record: Mapping[str, Any],
    ) -> None:
        if grant_record.get("schema") != "HHS-P218-I5-PROMOTION-AUTHORITY-GRANT-V1":
            raise Pass218PromotionValidationError("P218_I5_GRANT_SCHEMA_INVALID")
        if not validate_hash72(str(grant_record.get("grantor_authority_hash72", ""))):
            raise Pass218PromotionValidationError("P218_I5_GRANTOR_AUTHORITY_HASH72_INVALID")
        sequence = grant_record.get("grant_sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
            raise Pass218PromotionValidationError("P218_I5_GRANT_SEQUENCE_INVALID")
        if grant_record.get("target_scope") != PROMOTION_SCOPE:
            raise Pass218PromotionValidationError("P218_I5_GRANT_SCOPE_INVALID")
        for grant_key, proof_key in (
            ("entry_id_sha256", "entry_id_sha256"),
            ("staging_hash72", "staging_hash72"),
            ("projection_sha256", "projection_sha256"),
            ("proof_hash72", "proof_hash72"),
        ):
            if grant_record.get(grant_key) != proof_record.get(proof_key):
                raise Pass218PromotionValidationError(
                    "P218_I5_GRANT_CANDIDATE_BINDING_MISMATCH:" + grant_key
                )
        expected_payload = {
            "schema": "HHS-P218-I5-PROMOTION-AUTHORITY-GRANT-PAYLOAD-V1",
            "grantor_authority_hash72": grant_record["grantor_authority_hash72"],
            "grant_sequence": sequence,
            "target_scope": grant_record["target_scope"],
            "entry_id_sha256": grant_record["entry_id_sha256"],
            "staging_hash72": grant_record["staging_hash72"],
            "projection_sha256": grant_record["projection_sha256"],
            "proof_hash72": grant_record["proof_hash72"],
        }
        expected_grant_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTION-AUTHORITY-GRANT-V1"},
            expected_payload,
        )
        if grant_record.get("grant_hash72") != expected_grant_hash72:
            raise Pass218PromotionValidationError("P218_I5_GRANT_HASH72_MISMATCH")
        expected_validation_payload = {
            "schema": "HHS-P218-I5-PROMOTION-GRANT-VALIDATION-V1",
            "grant_hash72": expected_grant_hash72,
            "grantor_authority_hash72": grant_record["grantor_authority_hash72"],
            "grant_sequence": sequence,
            "scope_exact": True,
            "candidate_exact": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "learning_authority_granted": False,
        }
        expected_validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTION-GRANT-VALIDATION-V1"},
            expected_validation_payload,
        )
        if grant_record.get("validation_hash72") != expected_validation_hash72:
            raise Pass218PromotionValidationError(
                "P218_I5_GRANT_VALIDATION_HASH72_MISMATCH"
            )
        expected_grant_hash216 = (
            str(proof_record["proof_hash72"])
            + expected_grant_hash72
            + expected_validation_hash72
        )
        if grant_record.get("grant_hash216") != expected_grant_hash216:
            raise Pass218PromotionValidationError("P218_I5_GRANT_HASH216_LANE_MISMATCH")
        if grant_record.get("canonical_mutation_invoked") is not False:
            raise Pass218PromotionValidationError("P218_I5_GRANT_MUTATION_FLAG_INVALID")

    def authorize(
        self,
        proof: "PromotionProof | Mapping[str, Any]",
        grant: "PromotionAuthorityGrant | Mapping[str, Any]",
    ) -> dict[str, Any]:
        proof_record = proof.to_record() if isinstance(proof, PromotionProof) else _copy(proof)
        grant_record = grant.to_record() if isinstance(grant, PromotionAuthorityGrant) else _copy(grant)
        PromotionProofMembrane.validate_proof_record(proof_record)
        self._validate_grant(proof_record, grant_record)

        payload = {
            "schema": "HHS-P218-I5-PROMOTION-AUTHORIZATION-PAYLOAD-V1",
            "entry_id_sha256": proof_record["entry_id_sha256"],
            "proof_hash72": proof_record["proof_hash72"],
            "grant_hash72": grant_record["grant_hash72"],
            "staging_hash72": proof_record["staging_hash72"],
            "projection_sha256": proof_record["projection_sha256"],
            "target_scope": grant_record["target_scope"],
        }
        authorization_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTION-AUTHORIZATION-V1"},
            payload,
        )
        validation_payload = {
            "schema": "HHS-P218-I5-PROMOTION-AUTHORIZATION-VALIDATION-V1",
            "authorization_hash72": authorization_hash72,
            "proof_present": True,
            "grant_present": True,
            "candidate_binding_exact": True,
            "scope_exact": True,
            "canonical_mutation_permitted": True,
            "canonical_mutation_invoked": False,
        }
        validation_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PROMOTION-AUTHORIZATION-VALIDATION-V1"},
            validation_payload,
        )
        authorization_hash216 = (
            proof_record["proof_hash72"]
            + grant_record["grant_hash72"]
            + validation_hash72
        )
        if not _valid_hash216(authorization_hash216):
            raise Pass218PromotionValidationError(
                "P218_I5_AUTHORIZATION_HASH216_INVALID"
            )
        authorization = PromotionAuthorization(
            authorization_hash72=authorization_hash72,
            validation_hash72=validation_hash72,
            authorization_hash216=authorization_hash216,
            entry_id_sha256=str(proof_record["entry_id_sha256"]),
            proof_hash72=str(proof_record["proof_hash72"]),
            grant_hash72=str(grant_record["grant_hash72"]),
            staging_hash72=str(proof_record["staging_hash72"]),
            projection_sha256=str(proof_record["projection_sha256"]),
            target_scope=str(grant_record["target_scope"]),
        ).to_record()
        existing = self._records.get(authorization_hash72)
        if existing is not None:
            if existing != authorization:
                raise Pass218PromotionStateError("P218_I5_AUTHORIZATION_IDENTITY_CONFLICT")
            return _copy(existing)
        self._records[authorization_hash72] = _copy(authorization)
        return _copy(authorization)

    def rollback(self, authorization_hash72: str, *, reason_code: str) -> dict[str, Any]:
        if not reason_code or not isinstance(reason_code, str):
            raise Pass218PromotionValidationError("P218_I5_ROLLBACK_REASON_REQUIRED")
        try:
            current = self._records[authorization_hash72]
        except KeyError as exc:
            raise Pass218PromotionStateError("P218_I5_AUTHORIZATION_NOT_FOUND") from exc
        if current["state"] == "ROLLED_BACK_BEFORE_CANONICAL_COMMIT":
            return _copy(current)
        if current["state"] != "AUTHORIZED_PENDING_CANONICAL_COMMIT":
            raise Pass218PromotionStateError("P218_I5_ROLLBACK_STATE_INVALID")
        rollback_payload = {
            "schema": "HHS-P218-I5-PRECOMMIT-ROLLBACK-V1",
            "authorization_hash72": authorization_hash72,
            "entry_id_sha256": current["entry_id_sha256"],
            "reason_code": reason_code,
            "canonical_mutation_invoked": False,
        }
        rollback_hash72 = hash72_digest(
            {"domain": "HHS-P218-I5-PRECOMMIT-ROLLBACK-V1"},
            rollback_payload,
        )
        rolled = {
            **current,
            "state": "ROLLED_BACK_BEFORE_CANONICAL_COMMIT",
            "canonical_mutation_permitted": False,
            "rollback_reason_code": reason_code,
            "rollback_hash72": rollback_hash72,
            "canonical_vector_store_mutation_invoked": False,
            "canonical_vm81_commit_invoked": False,
            "canonical_learning_commit_invoked": False,
        }
        self._records[authorization_hash72] = _copy(rolled)
        return _copy(rolled)

    def mutation_precondition(
        self,
        authorization_hash72: str,
        *,
        entry_id_sha256: str,
        projection_sha256: str,
        target_scope: str = PROMOTION_SCOPE,
    ) -> bool:
        record = self._records.get(authorization_hash72)
        return bool(
            record
            and record.get("state") == "AUTHORIZED_PENDING_CANONICAL_COMMIT"
            and record.get("canonical_mutation_permitted") is True
            and record.get("entry_id_sha256") == entry_id_sha256
            and record.get("projection_sha256") == projection_sha256
            and record.get("target_scope") == target_scope
            and record.get("proof_required") is True
            and record.get("grant_required") is True
        )

    def get(self, authorization_hash72: str) -> dict[str, Any] | None:
        record = self._records.get(authorization_hash72)
        return None if record is None else _copy(record)

    def record(self) -> dict[str, Any]:
        rows = [
            {
                "authorization_hash72": key,
                "entry_id_sha256": value["entry_id_sha256"],
                "state": value["state"],
                "canonical_mutation_permitted": value["canonical_mutation_permitted"],
                "canonical_mutation_invoked": False,
            }
            for key, value in sorted(self._records.items())
        ]
        return {
            "schema": "HHS-P218-I5-PROMOTION-AUTHORIZATION-JOURNAL-V1",
            "authorization_count": len(rows),
            "authorization_rows": rows,
            "journal_root_hash72": hash72_digest(
                {"domain": "HHS-P218-I5-PROMOTION-AUTHORIZATION-JOURNAL-V1"},
                rows,
            ),
            "canonical_vector_store": False,
            "canonical_vm81_authority": False,
            "canonical_learning_authority": False,
        }
