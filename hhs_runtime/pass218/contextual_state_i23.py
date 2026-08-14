"""Pass 218 Iteration 23 governed contextual-state hydration candidates.

Iteration 23 consumes only the revisable semantic-graph candidates emitted by
Iteration 22 and deterministically selects a bounded local relational working
state under an exact context and attention configuration. It does not create a
narrative beat, hydrate a user perspective, promote a grounded manifold,
perform formal/analogical typing, mint action authority, or commit learning.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import deque
import re
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.relational_consumption_i21 import (
    MAX_I21_QUERY_TOKENS,
    MAX_I21_TOP_K,
)

PASS218_I23_CONTEXTUAL_STATE_VERSION = "HHS-P218-I23-CONTEXTUAL-STATE-V1"
PASS218_I23_CONTEXTUAL_STATE_SCHEMA = "HHS-P218-I23-CONTEXTUAL-STATE-CANDIDATE-V1"
PASS218_I23_STATUS_SCHEMA = "HHS-P218-I23-CONTEXTUAL-STATE-STATUS-V1"

MAX_I23_CONTEXT_ID_LENGTH = 512
MAX_I23_ATTENTION_RADIUS = 6
MAX_I23_HYDRATED_NODES = 72
MAX_I23_ALLOWED_RELATION_FAMILIES = 72

_SPACE = re.compile(r"\s+")


class Pass218I23ContextualStateError(RuntimeError):
    """Fail-closed Iteration 23 contextual-hydration error."""


class Pass218I22SemanticGraphControlProtocol(Protocol):
    def status(self) -> dict[str, Any]: ...
    def assemble(self, payload: Mapping[str, Any]) -> dict[str, Any]: ...


def _normalize_token(value: str) -> str:
    token = _SPACE.sub(" ", str(value).strip().lower())
    if not token:
        raise Pass218I23ContextualStateError("P218_I23_TOKEN_REQUIRED")
    if len(token) > 256:
        raise Pass218I23ContextualStateError("P218_I23_TOKEN_TOO_LONG")
    return token


def _normalize_context_id(value: str) -> str:
    context = _SPACE.sub(" ", str(value).strip())
    if not context:
        raise Pass218I23ContextualStateError("P218_I23_CONTEXT_ID_REQUIRED")
    if len(context) > MAX_I23_CONTEXT_ID_LENGTH:
        raise Pass218I23ContextualStateError("P218_I23_CONTEXT_ID_TOO_LONG")
    return context


def _normalize_relation_family(value: str) -> str:
    family = str(value).strip().upper()
    if not family:
        raise Pass218I23ContextualStateError("P218_I23_RELATION_FAMILY_REQUIRED")
    if len(family) > 128:
        raise Pass218I23ContextualStateError("P218_I23_RELATION_FAMILY_TOO_LONG")
    return family


@dataclass(frozen=True)
class Pass218I23ContextQuery:
    tokens: tuple[str, ...]
    context_id: str
    attention_tokens: tuple[str, ...] = ()
    top_k: int = 8
    attention_radius: int = 1
    max_hydrated_nodes: int = 24
    allowed_relation_families: tuple[str, ...] = ()

    def validated(self) -> "Pass218I23ContextQuery":
        if isinstance(self.top_k, bool) or not isinstance(self.top_k, int):
            raise Pass218I23ContextualStateError("P218_I23_TOP_K_INTEGER_REQUIRED")
        if self.top_k < 1 or self.top_k > MAX_I21_TOP_K:
            raise Pass218I23ContextualStateError("P218_I23_TOP_K_OUT_OF_RANGE")
        if isinstance(self.attention_radius, bool) or not isinstance(
            self.attention_radius, int
        ):
            raise Pass218I23ContextualStateError(
                "P218_I23_ATTENTION_RADIUS_INTEGER_REQUIRED"
            )
        if self.attention_radius < 0 or self.attention_radius > MAX_I23_ATTENTION_RADIUS:
            raise Pass218I23ContextualStateError(
                "P218_I23_ATTENTION_RADIUS_OUT_OF_RANGE"
            )
        if isinstance(self.max_hydrated_nodes, bool) or not isinstance(
            self.max_hydrated_nodes, int
        ):
            raise Pass218I23ContextualStateError(
                "P218_I23_MAX_HYDRATED_NODES_INTEGER_REQUIRED"
            )
        if self.max_hydrated_nodes < 1 or self.max_hydrated_nodes > MAX_I23_HYDRATED_NODES:
            raise Pass218I23ContextualStateError(
                "P218_I23_MAX_HYDRATED_NODES_OUT_OF_RANGE"
            )

        tokens = tuple(sorted({_normalize_token(token) for token in self.tokens}))
        if not tokens:
            raise Pass218I23ContextualStateError("P218_I23_QUERY_EMPTY")
        if len(tokens) > MAX_I21_QUERY_TOKENS:
            raise Pass218I23ContextualStateError("P218_I23_QUERY_TOKEN_LIMIT")

        attention = tuple(
            sorted({_normalize_token(token) for token in self.attention_tokens})
        )
        if not attention:
            attention = tokens
        if len(attention) > MAX_I21_QUERY_TOKENS:
            raise Pass218I23ContextualStateError("P218_I23_ATTENTION_TOKEN_LIMIT")

        families = tuple(
            sorted(
                {
                    _normalize_relation_family(family)
                    for family in self.allowed_relation_families
                }
            )
        )
        if len(families) > MAX_I23_ALLOWED_RELATION_FAMILIES:
            raise Pass218I23ContextualStateError(
                "P218_I23_RELATION_FAMILY_LIMIT"
            )

        return Pass218I23ContextQuery(
            tokens=tokens,
            context_id=_normalize_context_id(self.context_id),
            attention_tokens=attention,
            top_k=self.top_k,
            attention_radius=self.attention_radius,
            max_hydrated_nodes=self.max_hydrated_nodes,
            allowed_relation_families=families,
        )


class Pass218I23ContextualStateHydrator:
    """Select a deterministic local working state from one I22 graph candidate."""

    _FORBIDDEN_TRUE = (
        "truth_promotion",
        "action_authority_minted",
        "canonical_learning_commit_invoked",
        "model_activation_invoked",
        "verbatim_corpus_source_retained",
        "authoritative_float_weights_created",
        "authoritative_semantic_compression_ready",
    )

    def __init__(self, i22_control: Pass218I22SemanticGraphControlProtocol) -> None:
        self.i22_control = i22_control
        self.contextual_state_count = 0
        self.last_contextual_state_hash72: str | None = None
        self.last_error_code: str | None = None

    @staticmethod
    def _error_code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def _validated_i22_status(self) -> dict[str, Any]:
        status = self.i22_control.status()
        if not bool(status.get("semantic_graph_candidate_ready")):
            raise Pass218I23ContextualStateError(
                "P218_I23_I22_SEMANTIC_GRAPH_PROVIDER_REQUIRED"
            )
        if status.get("semantic_graph_status") != "REVISABLE_SEMANTIC_GRAPH_CANDIDATE":
            raise Pass218I23ContextualStateError("P218_I23_I22_SEMANTICS_INVALID")
        if not bool(status.get("candidate_semantic_compression_input_ready")):
            raise Pass218I23ContextualStateError(
                "P218_I23_I22_CANDIDATE_INPUT_REQUIRED"
            )
        for field in self._FORBIDDEN_TRUE:
            if bool(status.get(field)):
                raise Pass218I23ContextualStateError(
                    f"P218_I23_I22_SAFETY_DRIFT:{field}"
                )
        return status

    def _validated_i22_graph(
        self,
        query: Pass218I23ContextQuery,
        status: Mapping[str, Any],
    ) -> dict[str, Any]:
        graph = self.i22_control.assemble(
            {
                "tokens": list(query.tokens),
                "top_k": query.top_k,
            }
        )
        if graph.get("semantic_graph_status") != "REVISABLE_SEMANTIC_GRAPH_CANDIDATE":
            raise Pass218I23ContextualStateError("P218_I23_I22_GRAPH_SEMANTICS_INVALID")
        if not bool(graph.get("candidate_semantic_compression_input_ready")):
            raise Pass218I23ContextualStateError(
                "P218_I23_I22_GRAPH_CANDIDATE_INPUT_REQUIRED"
            )
        for field in self._FORBIDDEN_TRUE:
            if bool(graph.get(field)):
                raise Pass218I23ContextualStateError(
                    f"P218_I23_I22_GRAPH_SAFETY_DRIFT:{field}"
                )
        graph_hash72 = str(graph.get("graph_hash72") or "")
        if not graph_hash72:
            raise Pass218I23ContextualStateError("P218_I23_I22_GRAPH_HASH72_REQUIRED")
        if (
            status.get("i20_binding_hash72")
            and graph.get("i20_binding_hash72") != status.get("i20_binding_hash72")
        ):
            raise Pass218I23ContextualStateError("P218_I23_I20_BINDING_MISMATCH")
        return graph

    @staticmethod
    def _filtered_edges(
        graph: Mapping[str, Any],
        allowed_relation_families: Sequence[str],
    ) -> list[dict[str, Any]]:
        allowed = set(allowed_relation_families)
        edges: list[dict[str, Any]] = []
        for edge in graph.get("edges", []):
            relation_type = str(edge.get("relation_type") or "").upper()
            if allowed and relation_type not in allowed:
                continue
            edges.append(dict(edge))
        edges.sort(
            key=lambda item: (
                str(item["source_id_hash72"]),
                str(item["relation_type"]),
                str(item["target_id_hash72"]),
                str(item["edge_hash72"]),
            )
        )
        return edges

    @staticmethod
    def _distances(
        node_by_lexeme: Mapping[str, Mapping[str, Any]],
        edges: Sequence[Mapping[str, Any]],
        attention_tokens: Sequence[str],
        radius: int,
    ) -> dict[str, int]:
        adjacency: dict[str, set[str]] = {
            str(node["lexeme"]): set() for node in node_by_lexeme.values()
        }
        for edge in edges:
            source = str(edge["source_token"])
            target = str(edge["target_token"])
            adjacency.setdefault(source, set()).add(target)
            adjacency.setdefault(target, set()).add(source)

        seeds = sorted(
            token for token in attention_tokens if token in node_by_lexeme
        )
        if not seeds:
            raise Pass218I23ContextualStateError(
                "P218_I23_ATTENTION_SEED_NOT_IN_GRAPH"
            )

        distance: dict[str, int] = {}
        queue: deque[str] = deque()
        for seed in seeds:
            distance[seed] = 0
            queue.append(seed)

        while queue:
            current = queue.popleft()
            current_distance = distance[current]
            if current_distance >= radius:
                continue
            for neighbor in sorted(adjacency.get(current, ())):
                if neighbor in distance:
                    continue
                distance[neighbor] = current_distance + 1
                queue.append(neighbor)
        return distance

    @staticmethod
    def _selected_nodes(
        node_by_lexeme: Mapping[str, Mapping[str, Any]],
        distances: Mapping[str, int],
        max_hydrated_nodes: int,
    ) -> list[dict[str, Any]]:
        ranked = sorted(
            (
                (int(distance), str(node_by_lexeme[lexeme]["distinction_id_hash72"]), lexeme)
                for lexeme, distance in distances.items()
            ),
            key=lambda item: item,
        )
        selected = ranked[:max_hydrated_nodes]
        nodes: list[dict[str, Any]] = []
        for distance, _, lexeme in selected:
            node = dict(node_by_lexeme[lexeme])
            node["context_distance"] = distance
            nodes.append(node)
        return nodes

    @staticmethod
    def _participation(
        nodes: Sequence[Mapping[str, Any]],
        selected_lexemes: set[str],
        attention_tokens: set[str],
        hydrated_edges: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        influential = set()
        for edge in hydrated_edges:
            influential.add(str(edge["source_token"]))
            influential.add(str(edge["target_token"]))
        records: list[dict[str, Any]] = []
        for node in sorted(
            nodes,
            key=lambda item: str(item["distinction_id_hash72"]),
        ):
            lexeme = str(node["lexeme"])
            body = {
                "lexeme": lexeme,
                "distinction_id_hash72": str(node["distinction_id_hash72"]),
                "stored_addressable": True,
                "retrieved": True,
                "hydrated": lexeme in selected_lexemes,
                "attention_active": lexeme in attention_tokens,
                "candidate_influential": lexeme in influential,
                "validated": False,
                "promoted": False,
            }
            body["participation_hash72"] = hash72_digest(
                {"domain": "HHS-P218-I23-PARTICIPATION-V1"},
                body,
            )
            records.append(body)
        return records

    def hydrate(self, query: Pass218I23ContextQuery) -> dict[str, Any]:
        validated = query.validated()
        try:
            i22_status = self._validated_i22_status()
            graph = self._validated_i22_graph(validated, i22_status)

            nodes = [dict(node) for node in graph.get("nodes", [])]
            node_by_lexeme = {
                str(node["lexeme"]): node
                for node in nodes
            }
            if not node_by_lexeme:
                raise Pass218I23ContextualStateError("P218_I23_I22_GRAPH_EMPTY")

            edges = self._filtered_edges(
                graph,
                validated.allowed_relation_families,
            )
            distances = self._distances(
                node_by_lexeme,
                edges,
                validated.attention_tokens,
                validated.attention_radius,
            )
            hydrated_nodes = self._selected_nodes(
                node_by_lexeme,
                distances,
                validated.max_hydrated_nodes,
            )
            hydrated_lexemes = {
                str(node["lexeme"]) for node in hydrated_nodes
            }
            hydrated_edges = [
                edge
                for edge in edges
                if str(edge["source_token"]) in hydrated_lexemes
                and str(edge["target_token"]) in hydrated_lexemes
            ]
            hydrated_edges.sort(
                key=lambda item: (
                    str(item["source_id_hash72"]),
                    str(item["relation_type"]),
                    str(item["target_id_hash72"]),
                    str(item["edge_hash72"]),
                )
            )

            attention_set = set(validated.attention_tokens)
            participation = self._participation(
                nodes,
                hydrated_lexemes,
                attention_set,
                hydrated_edges,
            )
            context_config = {
                "context_id": validated.context_id,
                "context_id_hash72": hash72_digest(
                    {"domain": "HHS-P218-I23-CONTEXT-ID-V1"},
                    {"context_id": validated.context_id},
                ),
                "attention_tokens": list(validated.attention_tokens),
                "attention_radius": validated.attention_radius,
                "max_hydrated_nodes": validated.max_hydrated_nodes,
                "allowed_relation_families": list(
                    validated.allowed_relation_families
                ),
                "traversal_semantics": "BIDIRECTIONAL_DISCOVERY_DIRECTION_PRESERVED",
            }
            context_config_hash72 = hash72_digest(
                {"domain": "HHS-P218-I23-CONTEXT-CONFIG-V1"},
                context_config,
            )

            body = {
                "schema": PASS218_I23_CONTEXTUAL_STATE_SCHEMA,
                "version": PASS218_I23_CONTEXTUAL_STATE_VERSION,
                "query": {
                    "tokens": list(validated.tokens),
                    "top_k": validated.top_k,
                },
                "i20_binding_hash72": graph.get("i20_binding_hash72"),
                "i21_batch_hash72": graph.get("i21_batch_hash72"),
                "i22_graph_hash72": graph["graph_hash72"],
                "wordnet_asset_manifest_hash72": graph.get(
                    "wordnet_asset_manifest_hash72"
                ),
                "context_configuration": context_config,
                "context_configuration_hash72": context_config_hash72,
                "hydrated_nodes": hydrated_nodes,
                "hydrated_edges": hydrated_edges,
                "participation": participation,
                "retrieved_node_count": len(nodes),
                "hydrated_node_count": len(hydrated_nodes),
                "hydrated_edge_count": len(hydrated_edges),
                "attention_active_count": sum(
                    1 for item in participation if item["attention_active"]
                ),
                "candidate_influential_count": sum(
                    1 for item in participation if item["candidate_influential"]
                ),
                "contextual_state_status": "REVISABLE_CONTEXTUAL_STATE_CANDIDATE",
                "contextual_hydration_candidate_ready": True,
                "narrative_beat_integration_invoked": False,
                "perspective_hydration_invoked": False,
                "grounded_relational_manifold_ready": False,
                "formal_analogical_typing_invoked": False,
                "authoritative_semantic_compression_ready": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "canonical_learning_commit_invoked": False,
                "model_activation_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
            }
            state_hash72 = hash72_digest(
                {"domain": PASS218_I23_CONTEXTUAL_STATE_SCHEMA},
                body,
            )
            result = {**body, "contextual_state_hash72": state_hash72}
            self.contextual_state_count += 1
            self.last_contextual_state_hash72 = state_hash72
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._error_code(exc)
            if isinstance(exc, Pass218I23ContextualStateError):
                raise
            raise Pass218I23ContextualStateError(self.last_error_code) from exc

    def status(self) -> dict[str, Any]:
        i22 = self.i22_control.status()
        ready = (
            bool(i22.get("semantic_graph_candidate_ready"))
            and i22.get("semantic_graph_status")
            == "REVISABLE_SEMANTIC_GRAPH_CANDIDATE"
            and not any(bool(i22.get(field)) for field in self._FORBIDDEN_TRUE)
        )
        return {
            "schema": PASS218_I23_STATUS_SCHEMA,
            "version": PASS218_I23_CONTEXTUAL_STATE_VERSION,
            "contextual_state_candidate_ready": ready,
            "i20_binding_hash72": i22.get("i20_binding_hash72"),
            "wordnet_asset_manifest_hash72": i22.get(
                "wordnet_asset_manifest_hash72"
            ),
            "contextual_state_count": self.contextual_state_count,
            "last_contextual_state_hash72": self.last_contextual_state_hash72,
            "i23_error_code": self.last_error_code,
            "contextual_state_status": "REVISABLE_CONTEXTUAL_STATE_CANDIDATE",
            "contextual_hydration_candidate_ready": ready,
            "narrative_beat_integration_invoked": False,
            "perspective_hydration_invoked": False,
            "grounded_relational_manifold_ready": False,
            "formal_analogical_typing_invoked": False,
            "authoritative_semantic_compression_ready": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }


__all__ = [
    "MAX_I23_ALLOWED_RELATION_FAMILIES",
    "MAX_I23_ATTENTION_RADIUS",
    "MAX_I23_CONTEXT_ID_LENGTH",
    "MAX_I23_HYDRATED_NODES",
    "PASS218_I23_CONTEXTUAL_STATE_SCHEMA",
    "PASS218_I23_CONTEXTUAL_STATE_VERSION",
    "PASS218_I23_STATUS_SCHEMA",
    "Pass218I23ContextQuery",
    "Pass218I23ContextualStateError",
    "Pass218I23ContextualStateHydrator",
]
