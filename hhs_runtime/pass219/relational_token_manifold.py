"""Pass 219 unified relational character-token manifold.

This module implements the additive machine-facing projection described by the
HARMONICODE both-and synthesis contract:

    human surface identity
      <-> character/string identity
      <-> exact relational metadata
      <-> shared graph topology
      <-> deterministic mathematical projection

It does not mint canonical VM81 state, Hash72 receipts, or Hash216 lineage.
It preserves the source string exactly and exposes deterministic, integer-only
metadata that downstream admitted HHS surfaces can hydrate and audit.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_ID = "HHS_PASS_219_RELATIONAL_CHARACTER_TOKEN_V1"
GRAPH_SCHEMA_ID = "HHS_PASS_219_RELATIONAL_TOKEN_GRAPH_V1"

LO_SHU_3X3 = (
    (4, 9, 2),
    (3, 5, 7),
    (8, 1, 6),
)

PRIME_BASIS = (2, 3, 5, 7, 11, 13, 17, 19)


class RelationalTokenError(ValueError):
    """Fail-closed validation error for the relational token manifold."""


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise RelationalTokenError(f"FLOAT_RELATIONAL_METADATA_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def canonical_json(value: Any) -> str:
    _reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _prime_residues(codepoint: int) -> dict[str, int]:
    return {str(prime): codepoint % prime for prime in PRIME_BASIS}


def _lo_shu(index: int) -> tuple[int, int, int]:
    position = index % 9
    row, column = divmod(position, 3)
    return row, column, LO_SHU_3X3[row][column]


def _utf8_bigint(character: str) -> int:
    raw = character.encode("utf-8")
    return int.from_bytes(raw, byteorder="big", signed=False) if raw else 0


@dataclass(frozen=True)
class RelationalCharacterToken:
    schema: str
    token_id: str
    source_id: str
    source_sha256: str
    char_index: int
    character: str
    codepoint: int
    utf8_hex: str
    utf8_bigint: int
    lo_shu_row: int
    lo_shu_column: int
    lo_shu_value: int
    prime_residues: Mapping[str, int]
    recursive_path: tuple[int, ...]
    left_context: str
    right_context: str
    left_context_sha256: str
    right_context_sha256: str
    surface_roles: tuple[str, ...]
    human_identity_preserved: bool
    machine_projection_exact: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["recursive_path"] = list(self.recursive_path)
        data["surface_roles"] = list(self.surface_roles)
        data["prime_residues"] = dict(self.prime_residues)
        return data


@dataclass(frozen=True)
class RelationalGraphEdge:
    source: str
    target: str
    relation: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class RelationalTokenGraph:
    schema: str
    source_id: str
    source_sha256: str
    source_text: str
    surface_roles: tuple[str, ...]
    tokens: tuple[RelationalCharacterToken, ...]
    edges: tuple[RelationalGraphEdge, ...]
    both_and_semantics: bool
    reductionist_collapse_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "source_text": self.source_text,
            "surface_roles": list(self.surface_roles),
            "tokens": [token.to_dict() for token in self.tokens],
            "edges": [edge.to_dict() for edge in self.edges],
            "both_and_semantics": self.both_and_semantics,
            "reductionist_collapse_forbidden": self.reductionist_collapse_forbidden,
        }


def _token_identity_material(
    *,
    source_id: str,
    source_sha256: str,
    char_index: int,
    character: str,
    left_context: str,
    right_context: str,
    surface_roles: Sequence[str],
) -> dict[str, Any]:
    row, column, value = _lo_shu(char_index)
    codepoint = ord(character)
    return {
        "schema": SCHEMA_ID,
        "source_id": source_id,
        "source_sha256": source_sha256,
        "char_index": char_index,
        "character": character,
        "codepoint": codepoint,
        "utf8_hex": character.encode("utf-8").hex(),
        "utf8_bigint": _utf8_bigint(character),
        "lo_shu": [row, column, value],
        "prime_residues": _prime_residues(codepoint),
        "recursive_path": [0, char_index],
        "left_context_sha256": sha256_text(left_context),
        "right_context_sha256": sha256_text(right_context),
        "surface_roles": list(surface_roles),
        "human_identity_preserved": True,
        "machine_projection_exact": True,
    }


def tokenize_string(
    text: str,
    *,
    source_id: str,
    surface_roles: Iterable[str] = ("written_language",),
    context_radius: int = 8,
) -> RelationalTokenGraph:
    """Tokenize an exact Unicode string into character-level relational objects.

    The source string remains a first-class human-readable surface. Each
    character simultaneously receives deterministic mathematical metadata and
    shared knowledge-graph relations. No surface is declared to replace another.
    """
    if not isinstance(text, str):
        raise RelationalTokenError("SOURCE_TEXT_MUST_BE_STRING")
    if not isinstance(source_id, str) or not source_id:
        raise RelationalTokenError("SOURCE_ID_REQUIRED")
    if not isinstance(context_radius, int) or isinstance(context_radius, bool) or context_radius < 0:
        raise RelationalTokenError("CONTEXT_RADIUS_MUST_BE_NONNEGATIVE_INTEGER")

    roles = tuple(dict.fromkeys(str(role) for role in surface_roles if str(role)))
    if not roles:
        raise RelationalTokenError("AT_LEAST_ONE_SURFACE_ROLE_REQUIRED")

    source_sha256 = sha256_text(text)
    tokens: list[RelationalCharacterToken] = []

    for index, character in enumerate(text):
        left = text[max(0, index - context_radius):index]
        right = text[index + 1:index + 1 + context_radius]
        material = _token_identity_material(
            source_id=source_id,
            source_sha256=source_sha256,
            char_index=index,
            character=character,
            left_context=left,
            right_context=right,
            surface_roles=roles,
        )
        token_id = sha256_text(canonical_json(material))
        row, column, value = material["lo_shu"]
        tokens.append(
            RelationalCharacterToken(
                schema=SCHEMA_ID,
                token_id=token_id,
                source_id=source_id,
                source_sha256=source_sha256,
                char_index=index,
                character=character,
                codepoint=material["codepoint"],
                utf8_hex=material["utf8_hex"],
                utf8_bigint=material["utf8_bigint"],
                lo_shu_row=row,
                lo_shu_column=column,
                lo_shu_value=value,
                prime_residues=material["prime_residues"],
                recursive_path=tuple(material["recursive_path"]),
                left_context=left,
                right_context=right,
                left_context_sha256=material["left_context_sha256"],
                right_context_sha256=material["right_context_sha256"],
                surface_roles=roles,
                human_identity_preserved=True,
                machine_projection_exact=True,
            )
        )

    edges: list[RelationalGraphEdge] = []
    for index, token in enumerate(tokens):
        if index > 0:
            edges.append(RelationalGraphEdge(token.token_id, tokens[index - 1].token_id, "previous_character"))
        if index + 1 < len(tokens):
            edges.append(RelationalGraphEdge(token.token_id, tokens[index + 1].token_id, "next_character"))
        edges.append(RelationalGraphEdge(source_sha256, token.token_id, "contains_character"))

    graph = RelationalTokenGraph(
        schema=GRAPH_SCHEMA_ID,
        source_id=source_id,
        source_sha256=source_sha256,
        source_text=text,
        surface_roles=roles,
        tokens=tuple(tokens),
        edges=tuple(edges),
        both_and_semantics=True,
        reductionist_collapse_forbidden=True,
    )
    validate_graph(graph)
    return graph


def hydrate_string(graph: RelationalTokenGraph) -> str:
    ordered = sorted(graph.tokens, key=lambda token: token.char_index)
    if [token.char_index for token in ordered] != list(range(len(ordered))):
        raise RelationalTokenError("CHARACTER_INDEX_CONTINUITY_FAILURE")
    text = "".join(token.character for token in ordered)
    if sha256_text(text) != graph.source_sha256:
        raise RelationalTokenError("SOURCE_REHYDRATION_HASH_MISMATCH")
    return text


def validate_graph(graph: RelationalTokenGraph) -> dict[str, Any]:
    if graph.schema != GRAPH_SCHEMA_ID:
        raise RelationalTokenError("GRAPH_SCHEMA_MISMATCH")
    if not graph.both_and_semantics or not graph.reductionist_collapse_forbidden:
        raise RelationalTokenError("BOTH_AND_SEMANTICS_REQUIRED")
    if sha256_text(graph.source_text) != graph.source_sha256:
        raise RelationalTokenError("SOURCE_SHA256_MISMATCH")

    token_ids: set[str] = set()
    for token in graph.tokens:
        if token.schema != SCHEMA_ID:
            raise RelationalTokenError("TOKEN_SCHEMA_MISMATCH")
        if token.source_id != graph.source_id or token.source_sha256 != graph.source_sha256:
            raise RelationalTokenError("TOKEN_SOURCE_IDENTITY_MISMATCH")
        if len(token.character) != 1:
            raise RelationalTokenError("CHARACTER_TOKEN_WIDTH_MISMATCH")
        if token.codepoint != ord(token.character):
            raise RelationalTokenError("CODEPOINT_MISMATCH")
        if token.utf8_hex != token.character.encode("utf-8").hex():
            raise RelationalTokenError("UTF8_HEX_MISMATCH")
        if token.utf8_bigint != _utf8_bigint(token.character):
            raise RelationalTokenError("UTF8_BIGINT_MISMATCH")
        row, column, value = _lo_shu(token.char_index)
        if (token.lo_shu_row, token.lo_shu_column, token.lo_shu_value) != (row, column, value):
            raise RelationalTokenError("LO_SHU_COORDINATE_MISMATCH")
        if dict(token.prime_residues) != _prime_residues(token.codepoint):
            raise RelationalTokenError("PRIME_MODULAR_FINGERPRINT_MISMATCH")
        if tuple(token.recursive_path) != (0, token.char_index):
            raise RelationalTokenError("RECURSIVE_PATH_MISMATCH")
        if token.left_context_sha256 != sha256_text(token.left_context):
            raise RelationalTokenError("LEFT_CONTEXT_HASH_MISMATCH")
        if token.right_context_sha256 != sha256_text(token.right_context):
            raise RelationalTokenError("RIGHT_CONTEXT_HASH_MISMATCH")
        if tuple(token.surface_roles) != graph.surface_roles:
            raise RelationalTokenError("SURFACE_ROLE_MISMATCH")
        if not token.human_identity_preserved or not token.machine_projection_exact:
            raise RelationalTokenError("DUAL_RESOLUTION_INVARIANT_FAILURE")

        material = _token_identity_material(
            source_id=token.source_id,
            source_sha256=token.source_sha256,
            char_index=token.char_index,
            character=token.character,
            left_context=token.left_context,
            right_context=token.right_context,
            surface_roles=token.surface_roles,
        )
        expected_id = sha256_text(canonical_json(material))
        if token.token_id != expected_id:
            raise RelationalTokenError("TOKEN_ID_MISMATCH")
        if token.token_id in token_ids:
            raise RelationalTokenError("DUPLICATE_TOKEN_ID")
        token_ids.add(token.token_id)

    allowed_sources = token_ids | {graph.source_sha256}
    allowed_targets = token_ids
    allowed_relations = {"previous_character", "next_character", "contains_character"}
    for edge in graph.edges:
        if edge.source not in allowed_sources or edge.target not in allowed_targets:
            raise RelationalTokenError("KNOWLEDGE_GRAPH_EDGE_DANGLING")
        if edge.relation not in allowed_relations:
            raise RelationalTokenError("KNOWLEDGE_GRAPH_RELATION_UNRECOGNIZED")

    hydrated = hydrate_string(graph)
    if hydrated != graph.source_text:
        raise RelationalTokenError("SOURCE_ROUNDTRIP_FAILURE")

    return {
        "schema": GRAPH_SCHEMA_ID,
        "source_sha256": graph.source_sha256,
        "character_count": len(graph.tokens),
        "edge_count": len(graph.edges),
        "roundtrip_exact": True,
        "human_identity_preserved": True,
        "machine_projection_exact": True,
        "both_and_semantics": True,
    }
