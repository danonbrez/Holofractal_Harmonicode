"""Pass 219 diagnostic binding from exact BigInt qudit assembly to VM81/C++ RNA routing.

The prior nonary/qudit probe established an exact bijection between one depth-72
ordered phase/qudit word and one integer in Z_(72^72).  This cycle binds that
serialized state to the existing 81x64 VM5184 carrier and candidate-only C++ RNA
cell-wall route without creating a second mutation or receipt authority.

VM81 frame layout used only by this diagnostic binding:

    words 0..6   : 448-bit little-endian BigInt limbs
    word 7       : typed binding header
    words 8..79  : 72 exact local glyphs (0..71), one per word
    word 80      : typed six-lane / pq-qp opcode metadata

The redundancy is intentional: the BigInt limbs and the 72 glyph words must
reconstruct each other exactly before native routing is allowed.  The native
route remains candidate-only; receipt ancestry is inherited from the verified
Hash216 transition reference supplied to the existing RNA VM5184 ABI.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.nonary_qudit_bigint_assembly_probe import (
    HASH72_DEPTH,
    GLYPH_RADIX,
    bigint_from_glyph_stream,
    build_pPq_lane_order_surface,
    canonical_lo_shu_assembly_fixture,
    decode_local_glyph,
)
from hhs_runtime.pass219.platonic_multistate_fold_probe import STATE_ORDER

PASS = 219
ITERATION = "VM81_RNA_BIGINT_EXECUTION_BINDING_PROBE_1_0"
SCHEMA = "HHS_PASS219_VM81_RNA_BIGINT_EXECUTION_BINDING_PROBE_V1"

VM81_WORD_COUNT = 81
VM81_WORD_BITS = 64
VM81_FRAME_BYTES = 648
BIGINT_LIMB_COUNT = 7
HEADER_WORD_INDEX = 7
GLYPH_WORD_START = 8
GLYPH_WORD_COUNT = 72
METADATA_WORD_INDEX = 80
HEADER_MAGIC = 0x48485351  # ASCII HHSQ
HEADER_VERSION = 1
MAX_U64 = (1 << 64) - 1


class VM81RNABigIntExecutionBindingProbeError(RuntimeError):
    pass


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise VM81RNABigIntExecutionBindingProbeError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _u64(value: Any, label: str) -> int:
    integer = _exact_int(value, label)
    if integer < 0 or integer > MAX_U64:
        raise VM81RNABigIntExecutionBindingProbeError(f"{label}_U64_REQUIRED")
    return integer


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise VM81RNABigIntExecutionBindingProbeError(
            f"FLOAT_BINDING_AUTHORITY_FORBIDDEN:{path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def bigint_to_u64_limbs(value: int) -> tuple[int, ...]:
    integer = _exact_int(value, "BIGINT")
    if integer < 0 or integer >= (1 << (BIGINT_LIMB_COUNT * VM81_WORD_BITS)):
        raise VM81RNABigIntExecutionBindingProbeError("BIGINT_EXCEEDS_448_BIT_BINDING")
    limbs: list[int] = []
    remainder = integer
    for _ in range(BIGINT_LIMB_COUNT):
        remainder, limb = divmod(remainder, 1 << VM81_WORD_BITS)
        limbs.append(limb)
    if remainder != 0:
        raise AssertionError("BIGINT_LIMB_REMAINDER")
    return tuple(limbs)


def u64_limbs_to_bigint(limbs: Sequence[int]) -> int:
    if len(limbs) != BIGINT_LIMB_COUNT:
        raise VM81RNABigIntExecutionBindingProbeError("SEVEN_BIGINT_LIMBS_REQUIRED")
    value = 0
    for index in range(BIGINT_LIMB_COUNT - 1, -1, -1):
        value = (value << VM81_WORD_BITS) | _u64(limbs[index], f"LIMB_{index}")
    return value


def _header_word() -> int:
    return (HEADER_MAGIC << 32) | (HEADER_VERSION << 16) | HASH72_DEPTH


def _encode_metadata(lane_record: Mapping[str, Any]) -> int:
    opcode = _exact_int(lane_record.get("opcode"), "OPCODE")
    lane = _exact_int(lane_record.get("lane"), "LANE")
    direction = lane_record.get("direction")
    source = lane_record.get("source")
    target = lane_record.get("target")
    if opcode < 0 or opcode > 11:
        raise VM81RNABigIntExecutionBindingProbeError("OPCODE_OUT_OF_RANGE")
    if lane < 0 or lane > 5:
        raise VM81RNABigIntExecutionBindingProbeError("SIX_LANE_ID_OUT_OF_RANGE")
    if opcode // 2 != lane:
        raise VM81RNABigIntExecutionBindingProbeError("OPCODE_LANE_MISMATCH")
    expected_direction = "pq" if opcode % 2 == 0 else "qp"
    if direction != expected_direction:
        raise VM81RNABigIntExecutionBindingProbeError("OPCODE_DIRECTION_MISMATCH")
    if source not in STATE_ORDER or target not in STATE_ORDER or source == target:
        raise VM81RNABigIntExecutionBindingProbeError("STATE_PAIR_INVALID")
    direction_bit = 0 if direction == "pq" else 1
    source_index = STATE_ORDER.index(source)
    target_index = STATE_ORDER.index(target)
    return (
        opcode
        | (lane << 8)
        | (direction_bit << 16)
        | (source_index << 24)
        | (target_index << 32)
    )


def _decode_metadata(word: int) -> dict[str, Any]:
    value = _u64(word, "METADATA_WORD")
    if value >> 40:
        raise VM81RNABigIntExecutionBindingProbeError("METADATA_RESERVED_BITS_NONZERO")
    opcode = value & 0xFF
    lane = (value >> 8) & 0xFF
    direction_bit = (value >> 16) & 0xFF
    source_index = (value >> 24) & 0xFF
    target_index = (value >> 32) & 0xFF
    if opcode > 11 or lane > 5 or opcode // 2 != lane:
        raise VM81RNABigIntExecutionBindingProbeError("METADATA_OPCODE_LANE_INVALID")
    if direction_bit not in (0, 1):
        raise VM81RNABigIntExecutionBindingProbeError("METADATA_DIRECTION_INVALID")
    direction = "pq" if direction_bit == 0 else "qp"
    if direction != ("pq" if opcode % 2 == 0 else "qp"):
        raise VM81RNABigIntExecutionBindingProbeError("METADATA_DIRECTION_OPCODE_INVALID")
    if source_index >= len(STATE_ORDER) or target_index >= len(STATE_ORDER):
        raise VM81RNABigIntExecutionBindingProbeError("METADATA_STATE_INDEX_INVALID")
    source = STATE_ORDER[source_index]
    target = STATE_ORDER[target_index]
    if source == target:
        raise VM81RNABigIntExecutionBindingProbeError("METADATA_STATE_PAIR_DEGENERATE")
    return {
        "opcode": opcode,
        "lane": lane,
        "direction": direction,
        "source": source,
        "target": target,
    }


def pack_vm81_binding_words(
    bigint: int,
    glyph_stream: Sequence[int],
    lane_record: Mapping[str, Any],
) -> tuple[int, ...]:
    if len(glyph_stream) != GLYPH_WORD_COUNT:
        raise VM81RNABigIntExecutionBindingProbeError("EXACT_72_GLYPH_STREAM_REQUIRED")
    glyphs = tuple(_exact_int(value, f"GLYPH_{index}") for index, value in enumerate(glyph_stream))
    if any(value < 0 or value >= GLYPH_RADIX for value in glyphs):
        raise VM81RNABigIntExecutionBindingProbeError("GLYPH_OUT_OF_RANGE")
    integer = _exact_int(bigint, "BIGINT")
    if bigint_from_glyph_stream(glyphs) != integer:
        raise VM81RNABigIntExecutionBindingProbeError("BIGINT_GLYPH_IDENTITY_MISMATCH")
    words = [0] * VM81_WORD_COUNT
    words[:BIGINT_LIMB_COUNT] = bigint_to_u64_limbs(integer)
    words[HEADER_WORD_INDEX] = _header_word()
    words[GLYPH_WORD_START : GLYPH_WORD_START + GLYPH_WORD_COUNT] = glyphs
    words[METADATA_WORD_INDEX] = _encode_metadata(lane_record)
    return tuple(words)


def unpack_vm81_binding_words(words: Sequence[int]) -> dict[str, Any]:
    if len(words) != VM81_WORD_COUNT:
        raise VM81RNABigIntExecutionBindingProbeError("EXACT_81_VM81_WORDS_REQUIRED")
    normalized = tuple(_u64(value, f"WORD_{index}") for index, value in enumerate(words))
    if normalized[HEADER_WORD_INDEX] != _header_word():
        raise VM81RNABigIntExecutionBindingProbeError("VM81_BINDING_HEADER_MISMATCH")
    bigint = u64_limbs_to_bigint(normalized[:BIGINT_LIMB_COUNT])
    glyphs = tuple(
        normalized[index]
        for index in range(GLYPH_WORD_START, GLYPH_WORD_START + GLYPH_WORD_COUNT)
    )
    if any(value >= GLYPH_RADIX for value in glyphs):
        raise VM81RNABigIntExecutionBindingProbeError("VM81_GLYPH_WORD_OUT_OF_RANGE")
    reconstructed = bigint_from_glyph_stream(glyphs)
    if reconstructed != bigint:
        raise VM81RNABigIntExecutionBindingProbeError("VM81_BIGINT_GLYPH_CROSSCHECK_FAILED")
    metadata = _decode_metadata(normalized[METADATA_WORD_INDEX])
    phase_qudit = [decode_local_glyph(value) for value in glyphs]
    return {
        "bigint": bigint,
        "glyph_stream": list(glyphs),
        "phase_digits": [pair[0] for pair in phase_qudit],
        "qudit_digits": [pair[1] for pair in phase_qudit],
        "metadata": metadata,
        "header": normalized[HEADER_WORD_INDEX],
    }


def words_to_raw_le(words: Sequence[int]) -> bytes:
    if len(words) != VM81_WORD_COUNT:
        raise VM81RNABigIntExecutionBindingProbeError("EXACT_81_VM81_WORDS_REQUIRED")
    return b"".join(_u64(value, f"WORD_{index}").to_bytes(8, "little") for index, value in enumerate(words))


def raw_le_to_words(raw: bytes) -> tuple[int, ...]:
    if not isinstance(raw, (bytes, bytearray)) or len(raw) != VM81_FRAME_BYTES:
        raise VM81RNABigIntExecutionBindingProbeError("RAW_VM5184_MUST_BE_648_BYTES")
    return tuple(
        int.from_bytes(raw[index : index + 8], "little")
        for index in range(0, VM81_FRAME_BYTES, 8)
    )


def _parse_native_output(stdout: str) -> dict[str, Any]:
    tokens = stdout.strip().split()
    if not tokens:
        raise VM81RNABigIntExecutionBindingProbeError("NATIVE_PROBE_EMPTY_OUTPUT")
    parsed: dict[str, Any] = {}
    for token in tokens:
        if "=" not in token:
            raise VM81RNABigIntExecutionBindingProbeError("NATIVE_PROBE_TOKEN_INVALID")
        key, value = token.split("=", 1)
        if not key or not value:
            raise VM81RNABigIntExecutionBindingProbeError("NATIVE_PROBE_TOKEN_INVALID")
        parsed[key] = int(value)
    return parsed


def run_native_probe(raw: bytes, native_probe: str) -> dict[str, Any]:
    probe = Path(native_probe)
    if not probe.is_file():
        raise VM81RNABigIntExecutionBindingProbeError("NATIVE_PROBE_EXECUTABLE_REQUIRED")
    with tempfile.NamedTemporaryFile(prefix="hhs-p219-bigint-rna-", suffix=".bin") as handle:
        handle.write(raw)
        handle.flush()
        completed = subprocess.run(
            [str(probe), handle.name],
            check=True,
            capture_output=True,
            text=True,
        )
    return _parse_native_output(completed.stdout)


def build_execution_cases() -> list[dict[str, Any]]:
    fixture = canonical_lo_shu_assembly_fixture()
    bigint = int(fixture["bigint"])
    glyphs = tuple(int(value) for value in fixture["glyph_stream"])
    lane_surface = build_pPq_lane_order_surface()
    cases: list[dict[str, Any]] = []
    for row in lane_surface["directed_lanes"]:
        words = pack_vm81_binding_words(bigint, glyphs, row)
        raw = words_to_raw_le(words)
        restored = unpack_vm81_binding_words(raw_le_to_words(raw))
        cases.append(
            {
                "opcode": row["opcode"],
                "lane": row["lane"],
                "direction": row["direction"],
                "source": row["source"],
                "target": row["target"],
                "bigint": bigint,
                "raw_sha256": sha256(raw).hexdigest(),
                "raw_bytes": raw,
                "restored": restored,
            }
        )
    return cases


def vm81_rna_bigint_execution_binding_probe(native_probe: str | None = None) -> dict[str, Any]:
    cases = build_execution_cases()
    bigint = cases[0]["bigint"]
    native_rows: list[dict[str, Any]] = []
    if native_probe is not None:
        for case in cases:
            first = run_native_probe(case["raw_bytes"], native_probe)
            second = run_native_probe(case["raw_bytes"], native_probe)
            native_rows.append(
                {
                    "opcode": case["opcode"],
                    "lane": case["lane"],
                    "direction": case["direction"],
                    "selected_lane": first["selected_lane"],
                    "graph_signature64": first["graph_signature64"],
                    "tensor_signature64": first["tensor_signature64"],
                    "decision_signature64": first["decision_signature64"],
                    "deterministic_repeat_exact": first == second,
                    "raw_unchanged": first["raw_unchanged"] == 1,
                    "import_export_exact": first["import_export_exact"] == 1,
                    "hash216_reference_verified": first["hash216_reference_verified"] == 1,
                    "transition_identity_preserved": first["transition_identity_preserved"] == 1,
                    "authority_closed": first["authority_closed"] == 1,
                    "word_visits": first["word_visits"],
                    "graph_edge_visits": first["graph_edge_visits"],
                }
            )

    pure_round_trip = all(
        case["restored"]["bigint"] == bigint
        and case["restored"]["metadata"]
        == {
            "opcode": case["opcode"],
            "lane": case["lane"],
            "direction": case["direction"],
            "source": case["source"],
            "target": case["target"],
        }
        for case in cases
    )
    raw_unique = len({case["raw_sha256"] for case in cases}) == len(cases)
    native_green = bool(native_rows) and all(
        row["deterministic_repeat_exact"]
        and row["raw_unchanged"]
        and row["import_export_exact"]
        and row["hash216_reference_verified"]
        and row["transition_identity_preserved"]
        and row["authority_closed"]
        and row["word_visits"] == 81
        and row["graph_edge_visits"] == 1620
        and 0 <= row["selected_lane"] < 4
        for row in native_rows
    )

    report = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "frame_layout": {
            "vm81_words": VM81_WORD_COUNT,
            "vm81_word_bits": VM81_WORD_BITS,
            "vm5184_bytes": VM81_FRAME_BYTES,
            "bigint_limb_words": [0, 1, 2, 3, 4, 5, 6],
            "header_word": HEADER_WORD_INDEX,
            "glyph_words": [GLYPH_WORD_START, GLYPH_WORD_START + GLYPH_WORD_COUNT - 1],
            "metadata_word": METADATA_WORD_INDEX,
        },
        "assembly_identity": {
            "bigint": bigint,
            "bigint_fits_448_bits": bigint < (1 << 448),
            "directed_opcode_count": len(cases),
            "opcodes_dense_0_through_11": [case["opcode"] for case in cases] == list(range(12)),
            "all_typed_frames_round_trip": pure_round_trip,
            "all_typed_frames_have_distinct_raw_identity": raw_unique,
            "same_bigint_preserved_across_twelve_directional_views": len({case["bigint"] for case in cases}) == 1,
        },
        "native_execution": {
            "native_probe_supplied": native_probe is not None,
            "case_count": len(native_rows),
            "all_native_candidate_routes_green": native_green,
            "rows": native_rows,
        },
        "binding_result": {
            "decode_to_vm5184_exact": pure_round_trip,
            "native_rna_candidate_execution_exact": native_green,
            "reencode_preserves_bigint_identity": pure_round_trip and native_green,
            "typed_six_lane_pq_qp_identity_preserved": pure_round_trip and native_green,
            "hash216_receipt_ancestry_preserved": native_green,
            "existing_cpp_rna_route_reused": native_green,
            "new_mutation_primitive_required": False,
            "new_receipt_primitive_required": False,
            "canonical_execution_promotion_claimed": False,
        },
        "authority": {
            "diagnostic_only": True,
            "candidate_route_only": True,
            "canonical_vm81_mutation": False,
            "hash72_minting": False,
            "hash216_persistence": False,
            "canonical_receipt_minting": False,
            "floating_point_authority": False,
            "ordered_pq_qp_collapse": False,
        },
    }
    report["report_sha256"] = _digest(report)
    return report


def main() -> None:
    native_probe = os.environ.get("HHS_PASS219_BIGINT_RNA_NATIVE_PROBE")
    print(
        json.dumps(
            vm81_rna_bigint_execution_binding_probe(native_probe),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
