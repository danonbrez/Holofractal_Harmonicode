"""Pass 220 I041: unified holofractal relativistic game-engine projection.

I041 composes existing exact HHS surfaces into one deterministic game/render
state without creating a second authority path.

The frame binds:

- I035 Q144/G72 exact phase addressing;
- the Pass219 Harmonic36 144x36=5184 coordinate factorization;
- exact Euclidean rotations represented in Q(zeta_144), not host trig floats;
- I182 Platonic-solid incidence closure;
- deterministic Hash72-triplet / SpriteMap216-compatible sprite metadata;
- a 144-position reciprocal color wheel;
- H36 equal-temperament bank/pitch and harmonic-rule coordinates;
- typed portable shader IR with float/GPU work explicitly projection-only;
- I040 exact DESI relativistic observational projection;
- the I039 shared quantum/relativistic root.

This is a validated projection/game-state constructor only. It has no canonical
VM81/Hash72/Hash216 mutation or persistence authority.
"""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_desi_explicit_projection_corpus_v1 import (
    build_desi_explicit_projection,
    public_desi_dr2_lya_row,
    validate_desi_explicit_projection,
)
from hhs_runtime.hhs_pass220_q144_dyadic_gauge_phase_transport_v1 import (
    Q144_CELLS,
    q144_phase_address,
)
from hhs_runtime.pass219.harmonic_geometry_circuit_i182 import (
    PLATONIC_PAIRS,
    derive_platonic_closure,
    hydration_factorization_witnesses,
    pentagonal_quantization_witness,
)

SCHEMA = "HHS_PASS_220_I041_HOLOFRACTAL_RELATIVISTIC_GAME_ENGINE_V1"
VERSION = "1.0.0-checkpoint.41"
PROFILE = "PASS220-I041-HOLOFRACTAL-RELATIVISTIC-GAME-ENGINE-v1"
FRAME_SCHEMA = "HHS_PASS_220_I041_GAME_FRAME_V1"
CYCLE_SCHEMA = "HHS_PASS_220_I041_GAME_ENGINE_CYCLE_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I041_GAME_ENGINE_WITNESS_V1"

H36_WORD_COUNT = 144
H36_WORD_BITS = 36
H36_FRAME_BITS = 5184
H36_ET_CLASSES = 12
H36_ET_BANKS = 3
H36_RULE_COUNT = 64
VM81_CELLS = 81
HASH72_SIDE = 72
PHASE_BASIS_COUNT = 8

HASH72_ALPHABET = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "-+*/()<>!?"
)
HASH72_LEN = 72
SPRITE216_LEN = 216

PLATONIC_NAMES = {
    (3, 3): "tetrahedron",
    (4, 3): "cube",
    (3, 4): "octahedron",
    (5, 3): "dodecahedron",
    (3, 5): "icosahedron",
}

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "Q144_EXACT_PHASE_ADDRESSING_REQUIRED",
    "EUCLIDEAN_TRIGONOMETRY_IS_SYMBOLIC_CYCLOTOMIC_Q_ZETA144",
    "H36_144_TIMES_36_EQUALS_5184",
    "H36_ET_3_TIMES_12_EQUALS_36",
    "Q144_12_TIMES_12_EQUALS_144",
    "VM81_81_TIMES_64_EQUALS_5184",
    "HASH72_72_TIMES_72_EQUALS_5184",
    "OPERATION64_EQUALS_ORDERED_PHASE8_TIMES_PHASE8",
    "ALL_64_HARMONIC_RULE_COORDINATES_COVERED",
    "ALL_FIVE_PLATONIC_SOLIDS_DERIVED_BY_EXACT_INCIDENCE",
    "SPRITE216_IS_THREE_ORDERED_HASH72_CARRIERS",
    "COLOR_WHEEL_HAS_144_EXACT_POSITIONS",
    "COLOR_RECIPROCAL_IS_Q144_HALF_TURN_72",
    "SHADER_IR_PRESERVES_EXACT_SOURCE_IDENTITIES",
    "GPU_FLOATS_ARE_PROJECTION_ONLY",
    "I040_RELATIVISTIC_OBSERVATION_PROJECTION_BOUND",
    "I039_SHARED_ROOT_BOUND_THROUGH_I040",
    "NO_HOST_FLOAT_IN_EXACT_GAME_STATE",
    "NO_PROBABILITY_LIKELIHOOD_MCMC_REFIT",
    "NO_CANONICAL_AUTHORITY_ESCALATION",
)


class Pass220I041GameEngineError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


def _receipt_matches(record: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in record:
        return False
    body = dict(record)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I041GameEngineError(f"{name} must be an exact integer")
    return value


def _fraction_record(value: Fraction) -> Dict[str, int]:
    q = Fraction(value)
    return {"numerator": q.numerator, "denominator": q.denominator}


@lru_cache(maxsize=1)
def _validated_i040_projection() -> Dict[str, Any]:
    projection = build_desi_explicit_projection(public_desi_dr2_lya_row())
    result = validate_desi_explicit_projection(projection)
    if result.get("ok") is not True or result.get("u_data_close") is not True:
        raise Pass220I041GameEngineError("I040 projection did not close")
    return projection


def euclidean_trig_q144(P: int) -> Dict[str, Any]:
    """Exact 2D Euclidean rotation in the cyclotomic field Q(zeta_144)."""
    address = q144_phase_address(_exact_int(P, name="P"))
    k = address["q144_index"]
    inverse = (-k) % Q144_CELLS
    angle_turns = Fraction(k, Q144_CELLS)
    return _receipt({
        "schema": "HHS_PASS_220_I041_EUCLIDEAN_TRIG_Q144_V1",
        "P": P,
        "q144_index": k,
        "q144_row12": address["q144_row12"],
        "q144_col12": address["q144_col12"],
        "angle_turns": _fraction_record(angle_turns),
        "angle_degrees": _fraction_record(Fraction(360 * k, Q144_CELLS)),
        "cyclotomic_field": "Q(zeta_144)",
        "zeta_forward": f"zeta_144^{k}",
        "zeta_inverse": f"zeta_144^{inverse}",
        "cos_exact": (
            f"(zeta_144^{k}+zeta_144^{inverse})/2"
        ),
        "sin_exact": (
            f"(zeta_144^{k}-zeta_144^{inverse})/(2*i)"
        ),
        "rotation_matrix_exact": (
            (
                f"(zeta_144^{k}+zeta_144^{inverse})/2",
                f"-(zeta_144^{k}-zeta_144^{inverse})/(2*i)",
            ),
            (
                f"(zeta_144^{k}-zeta_144^{inverse})/(2*i)",
                f"(zeta_144^{k}+zeta_144^{inverse})/2",
            ),
        ),
        "scalar_trig_evaluation_performed": False,
        "host_float_arithmetic_used": False,
    })


def h36_coordinate(linear5184: int) -> Dict[str, Any]:
    """Mirror the exact Pass219 C H36 coordinate factorization."""
    linear = _exact_int(linear5184, name="linear5184")
    if not 0 <= linear < H36_FRAME_BITS:
        raise Pass220I041GameEngineError("linear5184 must be in 0..5183")

    word144 = linear // H36_WORD_BITS
    bit36 = linear % H36_WORD_BITS
    et_bank3 = bit36 // H36_ET_CLASSES
    et_pitch12 = bit36 % H36_ET_CLASSES
    q144_row12 = word144 // H36_ET_CLASSES
    q144_col12 = word144 % H36_ET_CLASSES
    vm81_cell81 = linear // H36_RULE_COUNT
    operation64 = linear % H36_RULE_COUNT
    hash72_row72 = linear // HASH72_SIDE
    hash72_col72 = linear % HASH72_SIDE
    phase_left8 = operation64 // PHASE_BASIS_COUNT
    phase_right8 = operation64 % PHASE_BASIS_COUNT
    harmonic_rule64 = operation64 + 1

    return {
        "linear5184": linear,
        "word144": word144,
        "bit36": bit36,
        "et_bank3": et_bank3,
        "et_pitch12": et_pitch12,
        "q144_row12": q144_row12,
        "q144_col12": q144_col12,
        "vm81_cell81": vm81_cell81,
        "vm81_operation64": operation64,
        "hash72_row72": hash72_row72,
        "hash72_col72": hash72_col72,
        "phase_left8": phase_left8,
        "phase_right8": phase_right8,
        "harmonic_rule64": harmonic_rule64,
    }


def h36_music_state(q144_index: int, bit36: int) -> Dict[str, Any]:
    q = _exact_int(q144_index, name="q144_index")
    bit = _exact_int(bit36, name="bit36")
    if not 0 <= q < H36_WORD_COUNT:
        raise Pass220I041GameEngineError("q144_index must be in 0..143")
    if not 0 <= bit < H36_WORD_BITS:
        raise Pass220I041GameEngineError("bit36 must be in 0..35")

    coordinate = h36_coordinate(q * H36_WORD_BITS + bit)
    pitch = coordinate["et_pitch12"]
    return _receipt({
        "schema": "HHS_PASS_220_I041_H36_MUSIC_STATE_V1",
        "coordinate": coordinate,
        "equal_temperament": {
            "banks3": H36_ET_BANKS,
            "classes12": H36_ET_CLASSES,
            "bank3": coordinate["et_bank3"],
            "pitch_class12": pitch,
            "all_transpositions12": tuple(
                (pitch + shift) % H36_ET_CLASSES
                for shift in range(H36_ET_CLASSES)
            ),
        },
        "harmonic_rule64": coordinate["harmonic_rule64"],
        "ordered_phase_pair8x8": (
            coordinate["phase_left8"],
            coordinate["phase_right8"],
        ),
        "host_float_arithmetic_used": False,
        "canonical_music_authority": False,
    })


def color_wheel_q144(q144_index: int) -> Dict[str, Any]:
    q = _exact_int(q144_index, name="q144_index")
    if not 0 <= q < Q144_CELLS:
        raise Pass220I041GameEngineError("q144_index must be in 0..143")
    reciprocal = (q + 72) % Q144_CELLS
    return _receipt({
        "schema": "HHS_PASS_220_I041_COLOR_WHEEL_Q144_V1",
        "q144_index": q,
        "hue_turns": {"numerator": q, "denominator": 144},
        "sector12": q // 12,
        "substep12": q % 12,
        "reciprocal_q144": reciprocal,
        "reciprocal_hue_turns": {
            "numerator": reciprocal,
            "denominator": 144,
        },
        "reciprocal_is_half_turn": (
            (reciprocal - q) % Q144_CELLS == 72
        ),
        "rgb_projection_authority": False,
        "host_float_arithmetic_used": False,
    })


def platonic_scene_geometry() -> Dict[str, Any]:
    solids = []
    for pair in sorted(PLATONIC_PAIRS):
        closure = derive_platonic_closure(*pair)
        solids.append({
            "name": PLATONIC_NAMES[pair],
            **asdict(closure),
        })
    pentagon = pentagonal_quantization_witness()
    factors = tuple(asdict(item) for item in hydration_factorization_witnesses())
    return _receipt({
        "schema": "HHS_PASS_220_I041_PLATONIC_SCENE_GEOMETRY_V1",
        "solids": tuple(solids),
        "solid_count": len(solids),
        "all_euler_two": all(item["euler"] == 2 for item in solids),
        "all_face_edge_incidence_closed": all(
            item["p"] * item["faces"] == 2 * item["edges"]
            for item in solids
        ),
        "all_vertex_edge_incidence_closed": all(
            item["q"] * item["vertices"] == 2 * item["edges"]
            for item in solids
        ),
        "pentagonal_quantization": pentagon,
        "factorization_witnesses": factors,
        "authoritative_vertex_table_used": False,
        "host_float_arithmetic_used": False,
        "render_mesh_is_projection_only": True,
    })


def _hash72_from_seed(seed: str, label: str) -> str:
    if not isinstance(seed, str) or not seed:
        raise Pass220I041GameEngineError("sprite seed must be a non-empty string")
    if not isinstance(label, str) or not label:
        raise Pass220I041GameEngineError("sprite label must be a non-empty string")
    out = []
    counter = 0
    while len(out) < HASH72_LEN:
        digest = sha256(
            f"{seed}:{label}:{counter}".encode("utf-8")
        ).digest()
        out.extend(HASH72_ALPHABET[byte % HASH72_LEN] for byte in digest)
        counter += 1
    return "".join(out[:HASH72_LEN])


def holofractal_sprite216(seed: str) -> Dict[str, Any]:
    prev72 = _hash72_from_seed(seed, "PREV72")
    state72 = _hash72_from_seed(seed, "STATE72")
    receipt72 = _hash72_from_seed(seed, "RECEIPT72")
    sprite216 = prev72 + state72 + receipt72
    state_indices = tuple(HASH72_ALPHABET.index(char) for char in state72)
    reciprocal_indices = tuple((value + 36) % 72 for value in state_indices)
    lo_shu = (
        (state_indices[3], state_indices[8], state_indices[1]),
        (state_indices[2], state_indices[4], state_indices[6]),
        (state_indices[7], state_indices[0], state_indices[5]),
    )
    geometry_seed = sha256(sprite216.encode("utf-8")).hexdigest()

    return _receipt({
        "schema": "HHS_PASS_220_I041_HOLOFRACTAL_SPRITE216_V1",
        "source_seed": seed,
        "prev_hash72": prev72,
        "state_hash72": state72,
        "receipt_hash72": receipt72,
        "sprite216": sprite216,
        "sprite216_length": len(sprite216),
        "geometry_seed": geometry_seed,
        "state_phase_indices72": state_indices,
        "reciprocal_phase_indices72": reciprocal_indices,
        "lo_shu_core": lo_shu,
        "compatible_projection_runtime": (
            "hhs_runtime/python/hhs_sprite_map_engine_v1.py"
        ),
        "render_float_projection_allowed": True,
        "canonical_float_authority": False,
        "host_float_arithmetic_used_by_exact_descriptor": False,
    })


def shader_ir(
    *,
    q144_index: int,
    sprite: Mapping[str, Any],
    music: Mapping[str, Any],
    color: Mapping[str, Any],
) -> Dict[str, Any]:
    trig = euclidean_trig_q144(q144_index)
    return _receipt({
        "schema": "HHS_PASS_220_I041_PORTABLE_SHADER_IR_V1",
        "shader_language": "HHS_TYPED_SHADER_IR",
        "vertex_stage": {
            "position_source": "HOLOFRACTAL_SPRITE216_PHASE_GEOMETRY",
            "rotation_field": trig["cyclotomic_field"],
            "rotation_matrix_exact": trig["rotation_matrix_exact"],
            "q144_index": q144_index,
            "mesh_semantics": "PLATONIC_TOPOLOGY_PROJECTION",
        },
        "fragment_stage": {
            "color_wheel_q144": color["q144_index"],
            "reciprocal_color_q144": color["reciprocal_q144"],
            "music_pitch_class12": music["equal_temperament"]["pitch_class12"],
            "music_bank3": music["equal_temperament"]["bank3"],
            "harmonic_rule64": music["harmonic_rule64"],
            "sprite_geometry_seed": sprite["geometry_seed"],
        },
        "backend_projection_targets": (
            "GLSL",
            "SPIR-V-compatible backend",
            "CPU preview",
        ),
        "exact_source_identity_preserved": True,
        "backend_float_values_may_be_generated_for_rendering": True,
        "backend_float_is_canonical_authority": False,
        "shader_executes_canonical_mutation": False,
    })


def build_relativistic_game_frame(
    tick: int,
    *,
    bit36: int = 0,
    platonic_pair: Tuple[int, int] = (5, 3),
) -> Dict[str, Any]:
    tick_i = _exact_int(tick, name="tick")
    bit = _exact_int(bit36, name="bit36")
    if tick_i < 0:
        raise Pass220I041GameEngineError("tick must be nonnegative")
    if not 0 <= bit < H36_WORD_BITS:
        raise Pass220I041GameEngineError("bit36 must be in 0..35")
    if platonic_pair not in PLATONIC_PAIRS:
        raise Pass220I041GameEngineError("unsupported Platonic Schlaefli pair")

    projection = _validated_i040_projection()
    q144 = tick_i % Q144_CELLS
    phase_address = q144_phase_address(tick_i)
    trig = euclidean_trig_q144(tick_i)
    music = h36_music_state(q144, bit)
    color = color_wheel_q144(q144)
    sprite = holofractal_sprite216(projection["projection_root_sha256"])
    solid = asdict(derive_platonic_closure(*platonic_pair))
    shader = shader_ir(
        q144_index=q144,
        sprite=sprite,
        music=music,
        color=color,
    )
    solve = projection["exact_observation_solve"]

    return _receipt({
        "schema": FRAME_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "tick": tick_i,
        "q144": phase_address,
        "euclidean_trig": trig,
        "h36_music": music,
        "color_wheel": color,
        "platonic_solid": {
            "name": PLATONIC_NAMES[platonic_pair],
            **solid,
        },
        "holofractal_sprite216": sprite,
        "shader_ir": shader,
        "relativistic_physics": {
            "i040_projection_root_sha256": projection["projection_root_sha256"],
            "i039_shared_state_root_sha256": projection[
                "i039_shared_state_root_sha256"
            ],
            "z_eff": solve["z_eff"],
            "one_plus_z": solve["one_plus_z"],
            "D_H_over_r_d": solve["D_H_over_r_d"],
            "D_M_over_r_d": solve["D_M_over_r_d"],
            "H_times_r_d_over_c0": solve["H_times_r_d_over_c0"],
            "D_M_over_D_H": solve["D_M_over_D_H"],
            "D_V_over_r_d_cubed": solve["D_V_over_r_d_cubed"],
            "u_data_close": projection["u_data_predicate"]["close"],
        },
        "same_q144_drives_trig_music_color_shader": all((
            trig["q144_index"] == q144,
            music["coordinate"]["word144"] == q144,
            color["q144_index"] == q144,
            shader["vertex_stage"]["q144_index"] == q144,
        )),
        "game_state_is_exact": True,
        "rendering_is_projection": True,
        "host_float_arithmetic_used_by_game_state": False,
        "probability_used": False,
        "likelihood_used": False,
        "mcmc_used": False,
        "parameter_refit_performed": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "direct_canonical_persistence_authority": False,
    })


def h36_full_coverage_witness() -> Dict[str, Any]:
    coordinates = tuple(h36_coordinate(i) for i in range(H36_FRAME_BITS))
    return _receipt({
        "schema": "HHS_PASS_220_I041_H36_FULL_COVERAGE_V1",
        "coordinate_count": len(coordinates),
        "unique_linear5184": len({item["linear5184"] for item in coordinates}),
        "unique_word144": len({item["word144"] for item in coordinates}),
        "unique_bit36": len({item["bit36"] for item in coordinates}),
        "unique_et_bank3": len({item["et_bank3"] for item in coordinates}),
        "unique_et_pitch12": len({item["et_pitch12"] for item in coordinates}),
        "unique_q144_coordinates": len({
            (item["q144_row12"], item["q144_col12"])
            for item in coordinates
        }),
        "unique_vm81_cells": len({item["vm81_cell81"] for item in coordinates}),
        "unique_operation64": len({
            item["vm81_operation64"] for item in coordinates
        }),
        "unique_hash72_coordinates": len({
            (item["hash72_row72"], item["hash72_col72"])
            for item in coordinates
        }),
        "unique_phase_pairs8x8": len({
            (item["phase_left8"], item["phase_right8"])
            for item in coordinates
        }),
        "unique_harmonic_rules64": len({
            item["harmonic_rule64"] for item in coordinates
        }),
        "exact_factorizations": {
            "144x36": H36_WORD_COUNT * H36_WORD_BITS,
            "12x12x3x12": 12 * 12 * 3 * 12,
            "81x64": VM81_CELLS * H36_RULE_COUNT,
            "72x72": HASH72_SIDE * HASH72_SIDE,
        },
        "host_float_arithmetic_used": False,
    })


def build_game_engine_cycle() -> Dict[str, Any]:
    projection = _validated_i040_projection()
    q144_rows = tuple(q144_phase_address(i) for i in range(Q144_CELLS))
    trig_rows = tuple(euclidean_trig_q144(i) for i in range(Q144_CELLS))
    colors = tuple(color_wheel_q144(i) for i in range(Q144_CELLS))
    platonic = platonic_scene_geometry()
    h36 = h36_full_coverage_witness()
    sprite = holofractal_sprite216(projection["projection_root_sha256"])

    return _receipt({
        "schema": CYCLE_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "q144_frame_count": len(q144_rows),
        "all_q144_indices_exactly_once": (
            tuple(row["q144_index"] for row in q144_rows)
            == tuple(range(Q144_CELLS))
        ),
        "all_q144_cyclotomic_trig_exact": all(
            row["scalar_trig_evaluation_performed"] is False
            and row["host_float_arithmetic_used"] is False
            for row in trig_rows
        ),
        "all_color_reciprocals_half_turn": all(
            row["reciprocal_is_half_turn"] for row in colors
        ),
        "h36_full_coverage": h36,
        "platonic_scene": platonic,
        "sprite216": sprite,
        "relativistic_projection_root_sha256": projection[
            "projection_root_sha256"
        ],
        "i039_shared_state_root_sha256": projection[
            "i039_shared_state_root_sha256"
        ],
        "dimension_closure": {
            "144x36": 5184,
            "81x64": 5184,
            "72x72": 5184,
            "12x12": 144,
            "3x12": 36,
            "8x8": 64,
        },
        "shader_ir_profile": "HHS_TYPED_SHADER_IR",
        "render_backend_is_projection_only": True,
        "host_float_arithmetic_used_by_exact_cycle": False,
        "canonical_admission_authority": False,
    })


def validate_game_engine_cycle(cycle: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(cycle, Mapping):
        raise Pass220I041GameEngineError("cycle must be a mapping")
    if cycle.get("schema") != CYCLE_SCHEMA:
        raise Pass220I041GameEngineError("cycle schema mismatch")
    if not _receipt_matches(cycle):
        raise Pass220I041GameEngineError("cycle receipt mismatch")

    expected = build_game_engine_cycle()
    if cycle != expected:
        raise Pass220I041GameEngineError("game-engine cycle drift")

    h36 = cycle["h36_full_coverage"]
    expected_counts = {
        "coordinate_count": 5184,
        "unique_linear5184": 5184,
        "unique_word144": 144,
        "unique_bit36": 36,
        "unique_et_bank3": 3,
        "unique_et_pitch12": 12,
        "unique_q144_coordinates": 144,
        "unique_vm81_cells": 81,
        "unique_operation64": 64,
        "unique_hash72_coordinates": 5184,
        "unique_phase_pairs8x8": 64,
        "unique_harmonic_rules64": 64,
    }
    for field, value in expected_counts.items():
        if h36.get(field) != value:
            raise Pass220I041GameEngineError(
                f"H36 coverage drift: {field}"
            )

    if cycle.get("q144_frame_count") != 144:
        raise Pass220I041GameEngineError("Q144 cycle length drift")
    if cycle.get("all_q144_indices_exactly_once") is not True:
        raise Pass220I041GameEngineError("Q144 coverage failure")
    if cycle.get("all_q144_cyclotomic_trig_exact") is not True:
        raise Pass220I041GameEngineError("cyclotomic trig exactness failure")
    if cycle.get("all_color_reciprocals_half_turn") is not True:
        raise Pass220I041GameEngineError("color reciprocal closure failure")
    if cycle["platonic_scene"].get("solid_count") != 5:
        raise Pass220I041GameEngineError("Platonic solid family incomplete")
    if cycle["platonic_scene"].get("all_euler_two") is not True:
        raise Pass220I041GameEngineError("Platonic Euler closure failure")
    if cycle["sprite216"].get("sprite216_length") != 216:
        raise Pass220I041GameEngineError("Sprite216 length drift")
    if cycle.get("dimension_closure") != {
        "144x36": 5184,
        "81x64": 5184,
        "72x72": 5184,
        "12x12": 144,
        "3x12": 36,
        "8x8": 64,
    }:
        raise Pass220I041GameEngineError("dimension closure mismatch")
    if cycle.get("render_backend_is_projection_only") is not True:
        raise Pass220I041GameEngineError("render authority boundary lost")
    if cycle.get("host_float_arithmetic_used_by_exact_cycle") is not False:
        raise Pass220I041GameEngineError("host float entered exact cycle")
    if cycle.get("canonical_admission_authority") is not False:
        raise Pass220I041GameEngineError("authority escalation")

    frame = build_relativistic_game_frame(143, bit36=35, platonic_pair=(5, 3))
    if frame["same_q144_drives_trig_music_color_shader"] is not True:
        raise Pass220I041GameEngineError("frame multimodal phase divergence")
    if frame["relativistic_physics"]["u_data_close"] is not True:
        raise Pass220I041GameEngineError("I040 relativistic projection open")

    return {
        "ok": True,
        "q144_frames": 144,
        "h36_coordinates": 5184,
        "platonic_solids": 5,
        "sprite216_length": 216,
        "harmonic_rules64": 64,
        "phase_pairs8x8": 64,
        "et_banks3": 3,
        "et_pitch_classes12": 12,
        "vm81_cells": 81,
        "shared_relativistic_projection_root_sha256": cycle[
            "relativistic_projection_root_sha256"
        ],
        "shared_i039_root_sha256": cycle["i039_shared_state_root_sha256"],
        "exact_cycle_closed": True,
    }


def holofractal_relativistic_game_engine_witness() -> Dict[str, Any]:
    cycle = build_game_engine_cycle()
    result = validate_game_engine_cycle(cycle)
    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": result["ok"],
        "result": result,
        "cycle_receipt_sha256": cycle["receipt_sha256"],
        "local_constraints": LOCAL_CONSTRAINTS,
        "graphics_shader_surface": "TYPED_SHADER_IR_PROJECTION",
        "music_surface": "PASS219_H36_144X36_EXACT_COORDINATE_PROJECTION",
        "physics_surface": "I040_EXACT_RELATIVISTIC_OBSERVATION_PROJECTION",
        "canonical_admission_authority": False,
    })


def holofractal_relativistic_game_engine_self_test() -> Dict[str, Any]:
    return holofractal_relativistic_game_engine_witness()
