"""Pass 218 Iteration 22 governed semantic-graph candidate assembly.

Iteration 22 combines inherited WordNet lexical priors with the exact,
revisable distributional candidates emitted by Iteration 21. The result is a
deterministic semantic-graph candidate suitable for later semantic compression
and curriculum reasoning, but it carries no empirical-truth, action, model-
activation, or canonical-learning authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import (
    default_wordnet_paths,
    load_wordnet_relations,
)
from hhs_runtime.pass218.genesis import repository_asset_manifest
from hhs_runtime.pass218.relational_consumption_i21 import (
    MAX_I21_QUERY_TOKENS,
    MAX_I21_TOP_K,
)

PASS218_I22_SEMANTIC_GRAPH_VERSION = "HHS-P218-I22-SEMANTIC-GRAPH-V1"
PASS218_I22_GRAPH_SCHEMA = "HHS-P218-I22-SEMANTIC-GRAPH-CANDIDATE-V1"
PASS218_I22_STATUS_SCHEMA = "HHS-P218-I22-SEMANTIC-GRAPH-STATUS-V1"

_TOKEN_SPACE = re.compile(r"\s+")


class Pass218I22SemanticGraphError(RuntimeError):
    """Fail-closed Iteration 22 graph-assembly error."""


class Pass218I21RelationalControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def consume(self, payload: Mapping[str, Any]) -> dict[str, Any]: ...


class Pass218I22LexicalPriorProviderProtocol(Protocol):
    def snapshot(self, tokens: tuple[str, ...]) -> dict[str, Any]: ...
    def status(self) -> dict[str, Any]: ...


def _normalize_token(value: str) -> str:
    token = _TOKEN_SPACE.sub(" ", str(value).strip().lower())
    if not token:
        raise Pass218I22SemanticGraphError("P218_I22_TOKEN_REQUIRED")
    if len(token) > 256:
        raise Pass218I22SemanticGraphError("P218_I22_TOKEN_TOO_LONG")
    return token


def _distinction_id(token: str) -> str:
    return hash72_digest(
        {"domain": "HHS-P218-DISTINCTION-I1-V1"},
        {"lexeme": _normalize_token(token)},
    )


@dataclass(frozen=True)
class Pass218I22GraphQuery:
    tokens: tuple[str, ...]
    top_k: int = 8

    def validated(self) -> "Pass218I22GraphQuery":
        if isinstance(self.top_k, bool) or not isinstance(self.top_k, int):
            raise Pass218I22SemanticGraphError("P218_I22_TOP_K_INTEGER_REQUIRED")
        if self.top_k < 1 or self.top_k > MAX_I21_TOP_K:
            raise Pass218I22SemanticGraphError("P218_I22_TOP_K_OUT_OF_RANGE")
        tokens = tuple(sorted({_normalize_token(token) for token in self.tokens}))
        if not tokens:
            raise Pass218I22SemanticGraphError("P218_I22_QUERY_EMPTY")
        if len(tokens) > MAX_I21_QUERY_TOKENS:
            raise Pass218I22SemanticGraphError("P218_I22_QUERY_TOKEN_LIMIT")
        return Pass218I22GraphQuery(tokens=tokens, top_k=self.top_k)


class Pass218I22WordNetPriorProvider:
    """Repository-native lexical prior provider reusing the inherited parser."""

    def __init__(self, repository_root: str | Path) -> None:
        self.repository_root = Path(repository_root).resolve()
        self._asset_manifest: dict[str, Any] | None = None
        self._relation_db: Mapping[str, Any] | None = None
        self._load_error_code: str | None = None

    def _load(self) -> None:
        if self._asset_manifest is not None and self._relation_db is not None:
            return
        try:
            self._asset_manifest = repository_asset_manifest(self.repository_root)
            self._relation_db = load_wordnet_relations(
                default_wordnet_paths(self.repository_root / "hhs_runtime"),
                require_all=True,
            )
            self._load_error_code = None
        except Exception as exc:
            self._load_error_code = type(exc).__name__
            raise Pass218I22SemanticGraphError(
                f"P218_I22_WORDNET_LOAD_FAILED:{self._load_error_code}"
            ) from exc

    @staticmethod
    def _relation(
        source: str,
        target: str,
        relation_type: str,
        status: int,
    ) -> dict[str, Any]:
        body = {
            "source_token": _normalize_token(source),
            "target_token": _normalize_token(target),
            "source_id_hash72": _distinction_id(source),
            "target_id_hash72": _distinction_id(target),
            "relation_type": relation_type,
            "status": status,
            "provenance": "WORDNET_REVISABLE_PRIOR",
            "revisable_candidate": True,
            "empirical_truth_authority": False,
        }
        body["lexical_prior_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I22-WORDNET-PRIOR-V1"},
            body,
        )
        return body

    def snapshot(self, tokens: tuple[str, ...]) -> dict[str, Any]:
        self._load()
        assert self._asset_manifest is not None
        assert self._relation_db is not None
        relations: list[dict[str, Any]] = []
        for source in tokens:
            entry = self._relation_db.get(source)
            if entry is None:
                continue
            groups = (
                ("LEXICAL_SYNONYM", 1, entry.synonyms),
                ("LEXICAL_ANTONYM", -1, entry.antonyms),
                ("LEXICAL_HYPERNYM", 1, entry.hypernyms),
                ("LEXICAL_HYPONYM", 1, entry.hyponyms),
            )
            for relation_type, status, targets in groups:
                for target in sorted(
                    {_normalize_token(value) for value in targets if str(value).strip()}
                ):
                    relations.append(
                        self._relation(source, target, relation_type, status)
                    )
        relations.sort(
            key=lambda item: (
                item["source_id_hash72"],
                item["relation_type"],
                item["target_id_hash72"],
                item["lexical_prior_hash72"],
            )
        )
        return {
            "schema": "HHS-P218-I22-WORDNET-SNAPSHOT-V1",
            "asset_manifest_hash72": self._asset_manifest["asset_manifest_hash72"],
            "relations": relations,
            "relation_count": len(relations),
            "definitions_retained": False,
            "examples_retained": False,
            "empirical_truth_authority": False,
        }

    def status(self) -> dict[str, Any]:
        try:
            self._load()
        except Pass218I22SemanticGraphError:
            return {
                "lexical_prior_ready": False,
                "asset_manifest_hash72": None,
                "load_error_code": self._load_error_code,
            }
        assert self._asset_manifest is not None
        return {
            "lexical_prior_ready": True,
            "asset_manifest_hash72": self._asset_manifest["asset_manifest_hash72"],
            "load_error_code": None,
        }


class Pass218I22SemanticGraphCandidateAssembler:
    """Fuse lexical priors and I21 evidence without semantic promotion."""

    _FORBIDDEN_TRUE = (
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
    )

    def __init__(
        self,
        i21_control: Pass218I21RelationalControlProtocol,
        lexical_provider: Pass218I22LexicalPriorProviderProtocol,
    ) -> None:
        self.i21_control = i21_control
        self.lexical_provider = lexical_provider
        self.graph_count = 0
        self.last_graph_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _validated_i21_status(self) -> dict[str, Any]:
        status = self.i21_control.status()
        if not bool(status.get("candidate_consumption_ready")):
            raise Pass218I22SemanticGraphError(
                "P218_I22_I21_CANDIDATE_PROVIDER_REQUIRED"
            )
        if status.get("candidate_semantics") != "REVISABLE_RELATIONAL_EVIDENCE":
            raise Pass218I22SemanticGraphError("P218_I22_I21_SEMANTICS_INVALID")
        for field in self._FORBIDDEN_TRUE:
            if bool(status.get(field)):
                raise Pass218I22SemanticGraphError(
                    f"P218_I22_I21_SAFETY_DRIFT:{field}"
                )
        binding_hash72 = str(status.get("i20_binding_hash72") or "")
        if not binding_hash72:
            raise Pass218I22SemanticGraphError(
                "P218_I22_I20_BINDING_HASH72_REQUIRED"
            )
        return status

    def _validated_i21_batch(
        self,
        query: Pass218I22GraphQuery,
        status: Mapping[str, Any],
    ) -> dict[str, Any]:
        batch = self.i21_control.consume(
            {"tokens": list(query.tokens), "top_k": query.top_k}
        )
        if batch.get("candidate_semantics") != "REVISABLE_RELATIONAL_EVIDENCE":
            raise Pass218I22SemanticGraphError("P218_I22_I21_BATCH_SEMANTICS_INVALID")
        for field in self._FORBIDDEN_TRUE:
            if bool(batch.get(field)):
                raise Pass218I22SemanticGraphError(
                    f"P218_I22_I21_BATCH_SAFETY_DRIFT:{field}"
                )
        if batch.get("i20_binding_hash72") != status.get("i20_binding_hash72"):
            raise Pass218I22SemanticGraphError("P218_I22_I20_BINDING_MISMATCH")
        if not str(batch.get("batch_hash72") or ""):
            raise Pass218I22SemanticGraphError("P218_I22_I21_BATCH_HASH72_REQUIRED")
        return batch

    @staticmethod
    def _edge(
        *,
        source_token: str,
        target_token: str,
        relation_type: str,
        status: int,
        provenance: str,
        upstream_hash72: str,
        exact_strength: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if status not in (-1, 0, 1):
            raise Pass218I22SemanticGraphError("P218_I22_EDGE_STATUS_INVALID")
        body: dict[str, Any] = {
            "source_token": _normalize_token(source_token),
            "target_token": _normalize_token(target_token),
            "source_id_hash72": _distinction_id(source_token),
            "target_id_hash72": _distinction_id(target_token),
            "relation_type": str(relation_type),
            "status": status,
            "provenance": str(provenance),
            "upstream_hash72": str(upstream_hash72),
            "revisable_candidate": True,
            "empirical_truth_authority": False,
            "action_authority": False,
            "canonical_learning_commit": False,
        }
        if exact_strength is not None:
            numerator = int(exact_strength["numerator"])
            denominator = int(exact_strength["denominator"])
            if numerator < 0 or denominator <= 0:
                raise Pass218I22SemanticGraphError(
                    "P218_I22_EXACT_STRENGTH_INVALID"
                )
            body["exact_strength"] = {
                "numerator": numerator,
                "denominator": denominator,
            }
        body["edge_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I22-SEMANTIC-EDGE-V1"},
            body,
        )
        return body

    @staticmethod
    def _bundle(edges: list[Mapping[str, Any]]) -> dict[str, Any]:
        first = edges[0]
        statuses = sorted({int(edge["status"]) for edge in edges})
        if -1 in statuses and 1 in statuses:
            polarity = "MIXED_POLARITY_EVIDENCE"
        elif 1 in statuses:
            polarity = "SUPPORT_PRESENT"
        elif -1 in statuses:
            polarity = "COUNTERINDICATION_PRESENT"
        else:
            polarity = "UNRESOLVED_ONLY"
        channels = [
            {
                "relation_type": edge["relation_type"],
                "status": edge["status"],
                "provenance": edge["provenance"],
                "upstream_hash72": edge["upstream_hash72"],
                **(
                    {"exact_strength": dict(edge["exact_strength"])}
                    if "exact_strength" in edge
                    else {}
                ),
            }
            for edge in sorted(
                edges,
                key=lambda item: (
                    str(item["relation_type"]),
                    int(item["status"]),
                    str(item["upstream_hash72"]),
                ),
            )
        ]
        body = {
            "source_token": first["source_token"],
            "target_token": first["target_token"],
            "source_id_hash72": first["source_id_hash72"],
            "target_id_hash72": first["target_id_hash72"],
            "evidence_channel_count": len(channels),
            "status_polarities": statuses,
            "polarity_class": polarity,
            "channels": channels,
            "pair_truth_promotion": False,
        }
        body["bundle_hash72"] = hash72_digest(
            {"domain": "HHS-P218-I22-EVIDENCE-BUNDLE-V1"},
            body,
        )
        return body

    def assemble(self, query: Pass218I22GraphQuery) -> dict[str, Any]:
        validated = query.validated()
        try:
            i21_status = self._validated_i21_status()
            i21_batch = self._validated_i21_batch(validated, i21_status)
            lexical = self.lexical_provider.snapshot(validated.tokens)
            asset_hash72 = str(lexical.get("asset_manifest_hash72") or "")
            if not asset_hash72:
                raise Pass218I22SemanticGraphError(
                    "P218_I22_LEXICAL_ASSET_HASH72_REQUIRED"
                )
            if bool(lexical.get("empirical_truth_authority")):
                raise Pass218I22SemanticGraphError(
                    "P218_I22_LEXICAL_SAFETY_DRIFT"
                )

            edges: list[dict[str, Any]] = []
            for item in lexical.get("relations", []):
                edges.append(
                    self._edge(
                        source_token=str(item["source_token"]),
                        target_token=str(item["target_token"]),
                        relation_type=str(item["relation_type"]),
                        status=int(item["status"]),
                        provenance=str(item["provenance"]),
                        upstream_hash72=str(item["lexical_prior_hash72"]),
                    )
                )
            for result in i21_batch.get("results", []):
                source = str(result["source_token"])
                for candidate in result.get("candidates", []):
                    edges.append(
                        self._edge(
                            source_token=source,
                            target_token=str(candidate["target"]),
                            relation_type=str(candidate["relation_type"]),
                            status=int(candidate["status"]),
                            provenance=str(candidate["provenance"]),
                            upstream_hash72=str(candidate["candidate_hash72"]),
                            exact_strength=candidate["similarity_squared"],
                        )
                    )
            edges.sort(
                key=lambda item: (
                    item["source_id_hash72"],
                    item["relation_type"],
                    item["target_id_hash72"],
                    item["edge_hash72"],
                )
            )

            lexemes = set(validated.tokens)
            for edge in edges:
                lexemes.add(edge["source_token"])
                lexemes.add(edge["target_token"])
            nodes = []
            for lexeme in sorted(lexemes):
                body = {
                    "lexeme": lexeme,
                    "distinction_id_hash72": _distinction_id(lexeme),
                    "revisable_candidate": True,
                }
                body["node_hash72"] = hash72_digest(
                    {"domain": "HHS-P218-I22-SEMANTIC-NODE-V1"},
                    body,
                )
                nodes.append(body)

            grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
            for edge in edges:
                key = (edge["source_id_hash72"], edge["target_id_hash72"])
                grouped.setdefault(key, []).append(edge)
            bundles = [
                self._bundle(grouped[key])
                for key in sorted(grouped)
            ]
            mixed_polarity_count = sum(
                1
                for bundle in bundles
                if bundle["polarity_class"] == "MIXED_POLARITY_EVIDENCE"
            )

            body = {
                "schema": PASS218_I22_GRAPH_SCHEMA,
                "version": PASS218_I22_SEMANTIC_GRAPH_VERSION,
                "query": {
                    "tokens": list(validated.tokens),
                    "top_k": validated.top_k,
                },
                "i20_binding_hash72": i21_batch["i20_binding_hash72"],
                "i21_batch_hash72": i21_batch["batch_hash72"],
                "wordnet_asset_manifest_hash72": asset_hash72,
                "nodes": nodes,
                "edges": edges,
                "evidence_bundles": bundles,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "evidence_bundle_count": len(bundles),
                "mixed_polarity_pair_count": mixed_polarity_count,
                "semantic_graph_status": "REVISABLE_SEMANTIC_GRAPH_CANDIDATE",
                "candidate_semantic_compression_input_ready": True,
                "authoritative_semantic_compression_ready": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
            }
            graph_hash72 = hash72_digest(
                {"domain": PASS218_I22_GRAPH_SCHEMA},
                body,
            )
            result = {**body, "graph_hash72": graph_hash72}
            self.graph_count += 1
            self.last_graph_hash72 = graph_hash72
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I22SemanticGraphError):
                raise
            raise Pass218I22SemanticGraphError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i21 = self.i21_control.status()
        lexical = self.lexical_provider.status()
        ready = bool(i21.get("candidate_consumption_ready")) and bool(
            lexical.get("lexical_prior_ready")
        )
        return {
            "schema": PASS218_I22_STATUS_SCHEMA,
            "version": PASS218_I22_SEMANTIC_GRAPH_VERSION,
            "semantic_graph_candidate_ready": ready,
            "i20_binding_hash72": i21.get("i20_binding_hash72"),
            "wordnet_asset_manifest_hash72": lexical.get("asset_manifest_hash72"),
            "graph_count": self.graph_count,
            "last_graph_hash72": self.last_graph_hash72,
            "i22_error_code": self.last_error_code or lexical.get("load_error_code"),
            "semantic_graph_status": "REVISABLE_SEMANTIC_GRAPH_CANDIDATE",
            "candidate_semantic_compression_input_ready": ready,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }


__all__ = [
    "PASS218_I22_GRAPH_SCHEMA",
    "PASS218_I22_SEMANTIC_GRAPH_VERSION",
    "PASS218_I22_STATUS_SCHEMA",
    "Pass218I22GraphQuery",
    "Pass218I22SemanticGraphCandidateAssembler",
    "Pass218I22SemanticGraphError",
    "Pass218I22WordNetPriorProvider",
]
