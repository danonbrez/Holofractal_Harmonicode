"""V2 phase-gear candidate binding to the INHERITED Pass219 VM81 BigInt carrier.

Candidate-only: the four ordered expression components and 64 separate
knowledge-graph addresses remain sidecar provenance. One existing radix-72
72-glyph state is packed through the inherited, redundancy-checked VM81 path.
This is not an encoding of arbitrary 64 tensor expressions into one 448-bit
BigInt, not a new Hash216 identity, and never admits a transition.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    HASH72_DEPTH, bigint_from_glyph_stream, glyph_stream_from_bigint,
    build_pPq_lane_order_surface,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    pack_vm81_binding_words, unpack_vm81_binding_words,
    words_to_raw_le, raw_le_to_words,
)

SCHEMA = "HHS_PASS220_PHASEGEAR_VM81_BIGINT_CANDIDATE_V1"
CONTRACT = Path(__file__).resolve().parents[1] / "contracts/pass220/PASS_220_LANE5_FOUR_COMPONENT_PHASE_GEAR_CIRCUIT_V2.md"


class PhaseGearBindingError(ValueError):
    pass


def _split(source: str) -> tuple[str, ...]:
    if not source.startswith("List(") or not source.endswith(")"):
        raise PhaseGearBindingError("FOUR_PART_LIST_REQUIRED")
    body = source[5:-1]
    stack: list[str] = []
    matching = {")": "(", "]": "[", "}": "{"}
    parts: list[str] = []
    start = 0
    for i, char in enumerate(body):
        if char in "([{":
            stack.append(char)
        elif char in ")]}":
            if not stack or stack.pop() != matching[char]:
                raise PhaseGearBindingError("UNBALANCED_GATE")
        elif char == "," and not stack:
            parts.append(body[start:i])
            start = i + 1
    if stack or start >= len(body):
        raise PhaseGearBindingError("UNBALANCED_GATE")
    parts.append(body[start:])
    if len(parts) != 4 or any(not p for p in parts):
        raise PhaseGearBindingError("FOUR_PART_LIST_REQUIRED")
    return tuple(parts)


def source_locked() -> str:
    text = CONTRACT.read_text(encoding="utf-8")
    return text.split("```wolfram\n", 1)[1].split("\n```", 1)[0].strip()


def bind_candidate(source: str, bigint: int, coordinates: tuple[int, ...],
                   *, lane_index: int = 0) -> dict:
    canonical = source_locked()
    if source != canonical:
        raise PhaseGearBindingError("SOURCE_NOT_CANONICAL")
    parts = _split(source)
    if len(coordinates) != 64 or any(
        type(i) is not int or not 0 <= i < 5184 for i in coordinates
    ) or len(set(coordinates)) != 64:
        raise PhaseGearBindingError("SIXTY_FOUR_UNIQUE_5184_COORDS_REQUIRED")
    if type(bigint) is not int or not 0 <= bigint < 72 ** HASH72_DEPTH:
        raise PhaseGearBindingError("BIGINT_OUTSIDE_DEPTH72")
    lanes = build_pPq_lane_order_surface()["directed_lanes"]
    if type(lane_index) is not int or not 0 <= lane_index < len(lanes):
        raise PhaseGearBindingError("INHERITED_LANE_REQUIRED")
    glyphs = glyph_stream_from_bigint(bigint, HASH72_DEPTH)
    if bigint_from_glyph_stream(glyphs) != bigint:
        raise PhaseGearBindingError("BIGINT_ROUNDTRIP_MISMATCH")
    words = pack_vm81_binding_words(bigint, glyphs, lanes[lane_index])
    raw = words_to_raw_le(words)
    restored = unpack_vm81_binding_words(raw_le_to_words(raw))
    if len(raw) != 648 or restored["bigint"] != bigint or tuple(restored["glyph_stream"]) != glyphs:
        raise PhaseGearBindingError("VM81_FRAME_ROUNDTRIP_MISMATCH")
    return {
        "schema": SCHEMA,
        "source_sha256_candidate": sha256(source.encode("utf-8")).hexdigest(),
        "four_ordered_component_sha256": tuple(sha256(part.encode("utf-8")).hexdigest() for part in parts),
        "linear5184_positions": coordinates,
        "bigint_decimal": str(bigint),
        "inherited_lane_opcode": lanes[lane_index]["opcode"],
        "inherited_vm81_raw_sha256_candidate": sha256(raw).hexdigest(),
        "frame_length": len(raw),
        "candidate_only": True,
        "native_cell_wall_executed": False,
        "signed_vm81_admitted": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
    }
