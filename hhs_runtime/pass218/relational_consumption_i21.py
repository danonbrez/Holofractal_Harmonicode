"""Pass 218 Iteration 21 governed relational-candidate consumption.

Iteration 21 consumes only the exact revisable Pass 166 relations exposed by a
ready Iteration 20 binding. It does not activate models, retain corpus prose,
promote candidates to truth, mint action authority, or invoke canonical
learning commits. Candidate batches are deterministic and Hash72 sealed so the
same exact query against the same I20 binding can be replayed and compared.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.genesis import ExactDistributionalRelation

PASS218_I21_RELATIONAL_CONSUMPTION_VERSION = "HHS-P218-I21-RELATIONAL-CONSUMPTION-V1"
PASS218_I21_CANDIDATE_BATCH_SCHEMA = "HHS-P218-I21-RELATIONAL-CANDIDATE-BATCH-V1"
PASS218_I21_STATUS_SCHEMA = "HHS-P218-I21-RELATIONAL-CONSUMPTION-STATUS-V1"
MAX_I21_QUERY_TOKENS = 72
MAX_I21_TOP_K = 72

_TOKEN_SPACE = re.compile(r"\s+")


class Pass218I21RelationalConsumptionError(RuntimeError):
    """Fail-closed Iteration 21 candidate-consumption error."""


class Pass218I20ModelControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def exact_provider(self) -> Any: ...


def _normalize_token(value: str) -> str:
    token = _TOKEN_SPACE.sub(" ", str(value).strip().lower())
    if not token:
        raise Pass218I21RelationalConsumptionError("P218_I21_TOKEN_REQUIRED")
    if len(token) > 256:
        raise Pass218I21RelationalConsumptionError("P218_I21_TOKEN_TOO_LONG")
    return token


@dataclass(frozen=True)
class Pass218I21CandidateQuery:
    tokens: tuple[str, ...]
    top_k: int = 8

    def validated(self) -> "Pass218I21CandidateQuery":
        if isinstance(self.top_k, bool) or not isinstance(self.top_k, int):
            raise Pass218I21RelationalConsumptionError("P218_I21_TOP_K_INTEGER_REQUIRED")
        if self.top_k < 1 or self.top_k > MAX_I21_TOP_K:
            raise Pass218I21RelationalConsumptionError("P218_I21_TOP_K_OUT_OF_RANGE")
        normalized = tuple(sorted({_normalize_token(token) for token in self.tokens}))
        if not normalized:
            raise Pass218I21RelationalConsumptionError("P218_I21_QUERY_EMPTY")
        if len(normalized) > MAX_I21_QUERY_TOKENS:
            raise Pass218I21RelationalConsumptionError("P218_I21_QUERY_TOKEN_LIMIT")
        return Pass218I21CandidateQuery(tokens=normalized, top_k=self.top_k)


class Pass218I21RelationalCandidateConsumer:
    """Consume exact I20 relations as sealed, non-authoritative candidates."""

    def __init__(self, i20_control: Pass218I20ModelControlProtocol) -> None:
        self.i20_control = i20_control
        self.batch_count = 0
        self.last_batch_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_") or text.startswith("P166_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _i20_snapshot(self) -> dict[str, Any]:
        status = self.i20_control.status()
        if not bool(status.get("relational_candidate_provider_ready")):
            raise Pass218I21RelationalConsumptionError(
                "P218_I21_I20_RELATIONAL_PROVIDER_REQUIRED"
            )
        binding_hash72 = str(status.get("binding_hash72") or "")
        if not binding_hash72:
            raise Pass218I21RelationalConsumptionError(
                "P218_I21_I20_BINDING_HASH72_REQUIRED"
            )
        forbidden_true = (
            "browser_model_activation_permitted",
            "canonical_learning_commit_invoked",
            "truth_promotion",
            "action_authority_minted",
            "pass165_source_retaining_learning_commit_invoked",
            "verbatim_corpus_source_retained",
            "authoritative_float_weights_created",
        )
        for field in forbidden_true:
            if bool(status.get(field)):
                raise Pass218I21RelationalConsumptionError(
                    f"P218_I21_I20_SAFETY_DRIFT:{field}"
                )
        return {
            "i20_binding_hash72": binding_hash72,
            "model_id": status.get("model_id"),
            "canonical_model_root": status.get("canonical_model_root"),
            "index_root": status.get("index_root"),
        }

    @staticmethod
    def _candidate_record(
        source_token: str,
        relation: ExactDistributionalRelation,
        *,
        rank: int,
    ) -> dict[str, Any]:
        item = relation.to_record()
        body = {
            "source_token": source_token,
            "rank": rank,
            "target": item["target"],
            "relation_type": "DISTRIBUTIONAL_NEIGHBOR",
            "status": int(item["status"]),
            "similarity_squared": {
                "numerator": int(item["similarity_squared"]["numerator"]),
                "denominator": int(item["similarity_squared"]["denominator"]),
            },
            "vector_identity": str(item["vector_identity"]),
            "provenance": "PASS166_EXACT_WORD2VEC_VIA_I20",
            "revisable_candidate": True,
            "empirical_truth_authority": False,
            "action_authority": False,
            "canonical_learning_commit": False,
        }
        body["candidate_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I21-RELATIONAL-CANDIDATE-V1"},
            body,
        )
        return body

    def consume(self, query: Pass218I21CandidateQuery) -> dict[str, Any]:
        """Return one deterministic exact candidate batch without promotion."""
        validated = query.validated()
        try:
            snapshot = self._i20_snapshot()
            provider = self.i20_control.exact_provider()
            token_records: list[dict[str, Any]] = []
            for source_token in validated.tokens:
                neighbors: Sequence[ExactDistributionalRelation] = provider.exact_neighbors(
                    source_token,
                    top_k=validated.top_k,
                )
                candidates = [
                    self._candidate_record(source_token, relation, rank=rank)
                    for rank, relation in enumerate(neighbors, start=1)
                ]
                token_records.append(
                    {
                        "source_token": source_token,
                        "candidate_count": len(candidates),
                        "candidates": candidates,
                    }
                )

            body = {
                "schema": PASS218_I21_CANDIDATE_BATCH_SCHEMA,
                "version": PASS218_I21_RELATIONAL_CONSUMPTION_VERSION,
                **snapshot,
                "query": {
                    "tokens": list(validated.tokens),
                    "top_k": validated.top_k,
                },
                "results": token_records,
                "candidate_semantics": "REVISABLE_RELATIONAL_EVIDENCE",
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
            }
            batch_hash72 = hash72_digest(
                {"domain": PASS218_I21_CANDIDATE_BATCH_SCHEMA},
                body,
            )
            result = {**body, "batch_hash72": batch_hash72}
            self.batch_count += 1
            self.last_batch_hash72 = batch_hash72
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._code(exc)
            if isinstance(exc, Pass218I21RelationalConsumptionError):
                raise
            raise Pass218I21RelationalConsumptionError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i20_status = self.i20_control.status()
        ready = bool(i20_status.get("relational_candidate_provider_ready"))
        return {
            "schema": PASS218_I21_STATUS_SCHEMA,
            "version": PASS218_I21_RELATIONAL_CONSUMPTION_VERSION,
            "candidate_consumption_ready": ready,
            "i20_binding_hash72": i20_status.get("binding_hash72"),
            "batch_count": self.batch_count,
            "last_batch_hash72": self.last_batch_hash72,
            "i21_error_code": self.last_error_code,
            "candidate_semantics": "REVISABLE_RELATIONAL_EVIDENCE",
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }


__all__ = [
    "MAX_I21_QUERY_TOKENS",
    "MAX_I21_TOP_K",
    "PASS218_I21_CANDIDATE_BATCH_SCHEMA",
    "PASS218_I21_RELATIONAL_CONSUMPTION_VERSION",
    "PASS218_I21_STATUS_SCHEMA",
    "Pass218I21CandidateQuery",
    "Pass218I21RelationalCandidateConsumer",
    "Pass218I21RelationalConsumptionError",
]
