"""Pass 220 I037: mandatory 24D noncommutative constraint-spacetime constructor.

This constructor binds the full local equation/lemma bundle to each of three
complete 24-position phase-qutrit manifolds.  The three manifolds are redundant
copies of the same information at -, 0, and + trinary phase orientation.

The 24-position carrier is the exact 3 x 8 product of:
- three Lo Shu relational axes; and
- the inherited ordered phase registry x,y,z,w,xy,yx,zw,wz.

The Pass-217 Golay [24,12,8] profile supplies the frozen 24-position carrier
cardinality only.  The repository explicitly does not yet provide an
authoritative Golay codec/decoder, so I037 does not claim one.

Native equations are retained as ordered typed constructor sources.  They are
not flattened into ordinary scalar equalities.  Exact finite/cardinality and
Genesis projection lemmas are proved independently where licensed.

This is a validated-operation constructor only.  It cannot create/enforce
canonical constraints, mutate VM81, mint Hash72/Hash216 authority, or persist
canonical state directly.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_backend.runtime.hhs_pass217_machine_contracts_v1 import (
    GOLAY_CODEWORD_BITS,
    GOLAY_DISTANCE,
    GOLAY_PAYLOAD_BITS,
    HASH72_SIDE,
    LOGICAL_BITS,
    ORDERED_PHASE_REGISTRY,
    POSITIONS_PER_CELL,
    VM81_CELLS,
)
from hhs_runtime.hhs_pass220_genesis_reverse_offset_holographic_nucleus_v1 import (
    nucleus_layers_witness,
    vm81_holographic_frame_witness,
)
from hhs_runtime.hhs_pass220_multidimensional_constraint_manifold_v1 import (
    VERBATIM_CONSTRAINT_EQUATIONS,
)
from hhs_runtime.hhs_phase_inverted_pythagorean_geometry_v1 import (
    A2,
    B2,
    C2,
    C4,
    P4_COLLAPSE,
)

SCHEMA = "HHS_PASS_220_I037_24D_MANDATORY_CONSTRAINT_SPACETIME_V1"
VERSION = "1.0.0-checkpoint.37"
PROFILE = "PASS220-I037-24D-MANDATORY-CONSTRAINT-SPACETIME-v1"
CONSTRUCTOR_SCHEMA = "HHS_PASS_220_I037_24D_SPACETIME_CONSTRUCTOR_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I037_24D_SPACETIME_WITNESS_V1"

TRINARY_LABELS: Tuple[str, ...] = ("-", "0", "+")
TRINARY_VALUES: Tuple[int, ...] = (-1, 0, 1)
LO_SHU_RELATIONAL_AXES: Tuple[str, ...] = (
    "LO_SHU_RELATIONAL_AXIS_0",
    "LO_SHU_RELATIONAL_AXIS_1",
    "LO_SHU_RELATIONAL_AXIS_2",
)
PHASE8: Tuple[str, ...] = tuple(ORDERED_PHASE_REGISTRY)
DIMENSIONS_PER_QUTRIT_MANIFOLD = len(LO_SHU_RELATIONAL_AXES) * len(PHASE8)
QUTRIT_MANIFOLD_COUNT = len(TRINARY_LABELS)
PHASE_COVER_DIMENSIONS = DIMENSIONS_PER_QUTRIT_MANIFOLD * QUTRIT_MANIFOLD_COUNT
LO_SHU_NUCLEUS_CELLS = 9
VM5184 = VM81_CELLS * POSITIONS_PER_CELL

TRINARY_PHASE_TENSOR: Tuple[Tuple[str, ...], ...] = (
    ("yx", "y+x", "xy"),
    (
        "yx-wz",
        "x+y-z-w+xy+yx-zw-wz",
        "zw-xy",
    ),
    ("wz", "z+w", "zw"),
)

DIRECT_EXCHANGE_FRAME = {
    "A:B": "A:B",
    "a:b": "a:b",
    "p:q": "p:q",
    "z:w": "z:w",
}
FLIPPED_EXCHANGE_FRAME = {
    "A:B": "B:A",
    "a:b": "b:a",
    "p:q": "q:p",
    "z:w": "w:z",
}

MANDATORY_NATIVE_EQUATIONS: Tuple[Tuple[str, str, str], ...] = (
    (
        "I037-E001-TRINARY-PHASE-TENSOR",
        "(-1,0,+1)={yx,y+x,xy},{yx-wz,(x+y-z-w+xy+yx-zw-wz),zw-xy},{wz,z+w,zw}",
        "ORDERED_NONCOMMUTATIVE_PHASE_TENSOR",
    ),
    (
        "I037-E002-P4-INVARIANT",
        "P⁴=AB=c⁴=(a²+b²)²",
        "ORDERED_MAGNITUDE_AND_PRODUCT_CLOSURE",
    ),
    (
        "I037-E003-PYTHAGOREAN-INVARIANT",
        "a²+b²=c²",
        "GENESIS_MAGNITUDE_CLOSURE",
    ),
    (
        "I037-E004-P8-TRINARY-FRACTAL-SCALE",
        "A²+B²=P⁸={-,0,+}/∆",
        "THREE_COPY_TRINARY_FRACTAL_SCALE",
    ),
    (
        "I037-E005-VARIABLE-EXCHANGE",
        "(A:B,a:b,p:q,z:w)↔(B:A,b:a,q:p,w:z)",
        "RECIPROCAL_ORIENTATION_INVOLUTION",
    ),
    (
        "I037-E006-P2-RELATIONAL-CLOSURE",
        "P²=P+(p+q)=pq=a²+b²+c²",
        "ORDERED_TYPED_EQUALITY_CHAIN",
    ),
    (
        "I037-E007-C2-PHASE-OFFSET-CHAIN",
        "c²=P⁴/(a²+b²)=a²+b²+c²=a²b²c²; c²-t³=a²",
        "ORDERED_TYPED_PHASE_OFFSET_CHAIN",
    ),
    (
        "I037-E008-GENESIS-REVERSE-OFFSET",
        "epsilon=m-5; m=epsilon+5; r=5+2*epsilon=2*m-5",
        "HOLOGRAPHIC_NUCLEUS_COORDINATE_EQUIVALENCE",
    ),
    (
        "I037-E009-BOUNDARY-NESTING",
        "(72*72):(Bx⁵¹⁸⁴) 72⁷²:81⁸¹!",
        "NESTED_MODULAR_BOUNDARY_CONDITION_SOURCE",
    ),
)

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "ALL_NATIVE_EQUATIONS_ARE_MANDATORY_CONSTRUCTORS",
    "ALL_PROOF_LEMMAS_ARE_MANDATORY_CONSTRUCTORS",
    "THREE_COMPLETE_24D_QUTRIT_MANIFOLDS",
    "THREE_TIMES_24_EQUALS_72_PHASE_COVER",
    "24D_EQUALS_THREE_LO_SHU_RELATIONAL_AXES_TIMES_EIGHT_ORDERED_PHASE_CHANNELS",
    "TRINARY_PHASE_TENSOR_SOURCE_IDENTITY_PRESERVED",
    "VARIABLE_EXCHANGE_IS_INVOLUTIVE",
    "DIRECT_AND_FLIPPED_FRAMES_CO_RESIDENT",
    "P4_ORDERED_INVARIANT_SOURCE_PRESERVED",
    "P8_TRINARY_FRACTAL_SCALE_SOURCE_PRESERVED",
    "A2_PLUS_B2_EQUALS_C2_GENESIS_PROJECTION",
    "P4_EQUALS_C4_EQUALS_A2_PLUS_B2_SQUARED_ON_GENESIS_PROJECTION",
    "EPSILON_RESIDUE_CARRIERS_RETAIN_RAW_PHASE_EXPRESSION",
    "EPSILON_RESIDUE_CARRIERS_RETAIN_EXCHANGE_FRAME",
    "EPSILON_RESIDUE_CARRIERS_RETAIN_NORMALIZED_PHASE",
    "EACH_QUTRIT_COPY_CONTAINS_FULL_EQUATION_AND_LEMMA_BUNDLE",
    "GOLAY24_IS_PROFILE_CARRIER_ONLY_NO_CODEC_AUTHORITY",
    "GENESIS_REVERSE_OFFSET_HOLOGRAPHIC_NUCLEUS_RETAINED",
    "72_PLUS_9_EQUALS_81",
    "81_TIMES_64_EQUALS_72_SQUARED_EQUALS_5184",
    "NO_HOST_FLOAT_ARITHMETIC",
    "NO_COMMUTATIVE_REORDERING_AUTHORIZED",
)


class Pass220I037SpacetimeError(ValueError):
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
        raise Pass220I037SpacetimeError(f"{name} must be an exact integer")
    return value


def _phase_index(label: str) -> int:
    if label not in TRINARY_LABELS:
        raise Pass220I037SpacetimeError("phase label must be one of -,0,+")
    return TRINARY_LABELS.index(label)


def variable_exchange_frame(*, flipped: bool = False) -> Dict[str, str]:
    return dict(FLIPPED_EXCHANGE_FRAME if flipped else DIRECT_EXCHANGE_FRAME)


def flip_variable_exchange_frame(frame: Mapping[str, str]) -> Dict[str, str]:
    current = dict(frame)
    if current == DIRECT_EXCHANGE_FRAME:
        return dict(FLIPPED_EXCHANGE_FRAME)
    if current == FLIPPED_EXCHANGE_FRAME:
        return dict(DIRECT_EXCHANGE_FRAME)
    raise Pass220I037SpacetimeError("unknown variable-exchange frame")


def mandatory_equation_constructors() -> Tuple[Dict[str, Any], ...]:
    constructors = []
    for equation_id, source, semantics in MANDATORY_NATIVE_EQUATIONS:
        constructors.append(_receipt({
            "schema": "HHS_PASS_220_I037_MANDATORY_EQUATION_CONSTRUCTOR_V1",
            "equation_id": equation_id,
            "source": source,
            "semantics": semantics,
            "mandatory": True,
            "constructor": True,
            "ordered_source_identity_preserved": True,
            "commutative_reordering_authorized": False,
            "host_scalar_reduction_authorized": (
                equation_id in {
                    "I037-E003-PYTHAGOREAN-INVARIANT",
                    "I037-E008-GENESIS-REVERSE-OFFSET",
                }
            ),
        }))

    for index, source in enumerate(VERBATIM_CONSTRAINT_EQUATIONS, start=1):
        constructors.append(_receipt({
            "schema": "HHS_PASS_220_I037_INHERITED_EQUATION_CONSTRUCTOR_V1",
            "equation_id": f"I037-INHERITED-I017-E{index:03d}",
            "source": source,
            "semantics": "INHERITED_I017_TYPED_CONSTRAINT_SURFACE",
            "mandatory": True,
            "constructor": True,
            "ordered_source_identity_preserved": True,
            "commutative_reordering_authorized": False,
            "host_scalar_reduction_authorized": False,
        }))

    return tuple(constructors)


def mandatory_proof_lemmas() -> Tuple[Dict[str, Any], ...]:
    nucleus = nucleus_layers_witness()
    lemmas = (
        (
            "I037-L001-24D-FACTOR",
            "3*8=24",
            DIMENSIONS_PER_QUTRIT_MANIFOLD == 24,
            "EXACT_FINITE_CARDINALITY",
        ),
        (
            "I037-L002-TRINARY-COVER",
            "3*24=72",
            PHASE_COVER_DIMENSIONS == 72,
            "EXACT_FINITE_CARDINALITY",
        ),
        (
            "I037-L003-QUDIT-CLOSURE",
            "72+9=81",
            PHASE_COVER_DIMENSIONS + LO_SHU_NUCLEUS_CELLS == VM81_CELLS,
            "EXACT_FINITE_CARDINALITY",
        ),
        (
            "I037-L004-VM5184-CROSSWALK",
            "81*64=72^2=5184",
            (
                VM81_CELLS * POSITIONS_PER_CELL
                == HASH72_SIDE * HASH72_SIDE
                == LOGICAL_BITS
                == 5184
            ),
            "EXACT_FINITE_CARDINALITY",
        ),
        (
            "I037-L005-GENESIS-PYTHAGOREAN",
            "a²+b²=c²",
            A2 + B2 == C2 == 3,
            "EXACT_GENESIS_SCALAR_PROJECTION",
        ),
        (
            "I037-L006-P4-GENESIS-PROJECTION",
            "P⁴=c⁴=(a²+b²)²",
            P4_COLLAPSE == C4 == (A2 + B2) ** 2 == 9,
            "EXACT_GENESIS_SCALAR_PROJECTION",
        ),
        (
            "I037-L007-VARIABLE-EXCHANGE-INVOLUTION",
            "R(R(frame))=frame",
            (
                flip_variable_exchange_frame(
                    flip_variable_exchange_frame(DIRECT_EXCHANGE_FRAME)
                )
                == DIRECT_EXCHANGE_FRAME
            ),
            "EXACT_SYMBOLIC_INVOLUTION",
        ),
        (
            "I037-L008-TRINARY-TENSOR-SHAPE",
            "3 rows * 3 ordered trinary positions",
            (
                len(TRINARY_PHASE_TENSOR) == 3
                and all(len(row) == 3 for row in TRINARY_PHASE_TENSOR)
            ),
            "EXACT_FINITE_STRUCTURE",
        ),
        (
            "I037-L009-NUCLEUS-THREE-VIEW-RECONSTRUCTION",
            "Genesis, magnitude, reverse-offset views reconstruct one Lo Shu nucleus",
            (
                nucleus["genesis_reconstructs_lo_shu"]
                and nucleus["reverse_reconstructs_lo_shu"]
                and nucleus["all_three_layers_same_cell_addresses"]
            ),
            "EXACT_INHERITED_I036_PROOF",
        ),
        (
            "I037-L010-GOLAY24-CARRIER-CARDINALITY",
            "Golay profile codeword_bits=24",
            GOLAY_CODEWORD_BITS == 24,
            "EXACT_INHERITED_PROFILE",
        ),
        (
            "I037-L011-GOLAY-CLAIM-BOUNDARY",
            "Golay 24-position carrier does not imply codec authority",
            True,
            "CLAIM_BOUNDARY",
        ),
        (
            "I037-L012-TRINARY-BALANCED-PROJECTION",
            "-1+0+1=0",
            sum(TRINARY_VALUES) == 0,
            "EXACT_NORMALIZED_PHASE_PROJECTION",
        ),
        (
            "I037-L013-PHASE-ORDER",
            "xy!=yx and zw!=wz remain ordered identities",
            (
                PHASE8.index("xy") != PHASE8.index("yx")
                and PHASE8.index("zw") != PHASE8.index("wz")
            ),
            "EXACT_ORDERED_IDENTITY_REGISTRY",
        ),
    )
    return tuple(_receipt({
        "schema": "HHS_PASS_220_I037_MANDATORY_PROOF_LEMMA_V1",
        "lemma_id": lemma_id,
        "statement": statement,
        "verified": bool(verified),
        "proof_mode": proof_mode,
        "mandatory": True,
        "constructor": True,
    }) for lemma_id, statement, verified, proof_mode in lemmas)


def constructor_bundle_root() -> str:
    payload = {
        "equations": mandatory_equation_constructors(),
        "lemmas": mandatory_proof_lemmas(),
    }
    return sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def epsilon_phase_residue_carrier(
    *,
    trinary_phase: str,
    lo_shu_axis: int,
    phase_channel: str,
) -> Dict[str, Any]:
    phase_idx = _phase_index(trinary_phase)
    axis = _exact_int(lo_shu_axis, name="lo_shu_axis")
    if not 0 <= axis < len(LO_SHU_RELATIONAL_AXES):
        raise Pass220I037SpacetimeError("lo_shu_axis must be in 0..2")
    if phase_channel not in PHASE8:
        raise Pass220I037SpacetimeError("unknown ordered phase channel")

    channel_index = PHASE8.index(phase_channel)
    golay_position = axis * len(PHASE8) + channel_index
    raw_expression = TRINARY_PHASE_TENSOR[axis][phase_idx]

    payload = {
        "schema": "HHS_PASS_220_I037_EPSILON_PHASE_RESIDUE_CARRIER_V1",
        "trinary_phase": trinary_phase,
        "trinary_scalar_projection": TRINARY_VALUES[phase_idx],
        "lo_shu_axis": axis,
        "lo_shu_axis_id": LO_SHU_RELATIONAL_AXES[axis],
        "ordered_phase_channel": phase_channel,
        "ordered_phase_channel_index8": channel_index,
        "golay24_profile_position": golay_position,
        "raw_phase_expression": raw_expression,
        "direct_exchange_frame": variable_exchange_frame(flipped=False),
        "flipped_exchange_frame": variable_exchange_frame(flipped=True),
        "variable_exchange_source": (
            "(A:B,a:b,p:q,z:w)↔(B:A,b:a,q:p,w:z)"
        ),
        "p4_invariant_source": "P⁴=AB=c⁴=(a²+b²)²",
        "p8_fractal_scale_source": "A²+B²=P⁸={-,0,+}/∆",
        "delta_normalized_phase_source": f"{trinary_phase}/∆",
        "epsilon_residue_source": (
            "RESIDUE("
            + raw_expression
            + ";phase="
            + trinary_phase
            + ";axis="
            + str(axis)
            + ";channel="
            + phase_channel
            + ")"
        ),
        "normalization_erases_raw_expression": False,
        "normalization_erases_exchange_provenance": False,
        "normalization_erases_phase_identity": False,
        "golay_profile_only": True,
        "golay_codec_authority": False,
        "mandatory_constructor_bundle_root_sha256": constructor_bundle_root(),
    }
    return _receipt(payload)


def build_24d_qutrit_manifold(trinary_phase: str) -> Dict[str, Any]:
    _phase_index(trinary_phase)
    carriers = tuple(
        epsilon_phase_residue_carrier(
            trinary_phase=trinary_phase,
            lo_shu_axis=axis,
            phase_channel=phase_channel,
        )
        for axis in range(len(LO_SHU_RELATIONAL_AXES))
        for phase_channel in PHASE8
    )
    positions = tuple(
        carrier["golay24_profile_position"]
        for carrier in carriers
    )
    equations = mandatory_equation_constructors()
    lemmas = mandatory_proof_lemmas()
    return _receipt({
        "schema": "HHS_PASS_220_I037_24D_QUTRIT_MANIFOLD_V1",
        "trinary_phase": trinary_phase,
        "normalized_phase_value": TRINARY_VALUES[_phase_index(trinary_phase)],
        "dimensions": len(carriers),
        "expected_dimensions": 24,
        "lo_shu_relational_axis_count": len(LO_SHU_RELATIONAL_AXES),
        "ordered_phase_channel_count": len(PHASE8),
        "factorization": "3*8=24",
        "golay_profile": {
            "code": "EXTENDED_BINARY_GOLAY_24_12_8",
            "payload_bits": GOLAY_PAYLOAD_BITS,
            "codeword_bits": GOLAY_CODEWORD_BITS,
            "distance": GOLAY_DISTANCE,
            "profile_position_count": GOLAY_CODEWORD_BITS,
            "profile_only": True,
            "codec_implemented_by_i037": False,
            "decoder_implemented_by_i037": False,
        },
        "carrier_positions": positions,
        "carriers": carriers,
        "mandatory_equation_constructors": equations,
        "mandatory_proof_lemmas": lemmas,
        "mandatory_constructor_bundle_root_sha256": constructor_bundle_root(),
        "full_information_copy": True,
        "partial_information_slice": False,
        "p4_invariant_source": "P⁴=AB=c⁴=(a²+b²)²",
        "p8_fractal_scale_source": "A²+B²=P⁸={-,0,+}/∆",
        "phase_specific_scale_source": f"A²+B²=P⁸={trinary_phase}/∆",
        "variable_exchange_involution_carried": True,
        "epsilon_residue_carriers_present": True,
        "host_float_arithmetic_used": False,
    })


def build_24d_constraint_spacetime_constructor() -> Dict[str, Any]:
    manifolds = tuple(
        build_24d_qutrit_manifold(phase)
        for phase in TRINARY_LABELS
    )
    nucleus = nucleus_layers_witness()
    vm81 = vm81_holographic_frame_witness()
    equations = mandatory_equation_constructors()
    lemmas = mandatory_proof_lemmas()
    return _receipt({
        "schema": CONSTRUCTOR_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "constructor_kind": "VALIDATED_OPERATION_CONSTRUCTOR",
        "contains_constraints": True,
        "local_constraints": LOCAL_CONSTRAINTS,
        "constraint_authority": "CONSTRUCTOR_LOCAL_ONLY",
        "canonical_service": False,
        "canonical_constraint_creation_authority": False,
        "canonical_constraint_enforcement_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "direct_canonical_persistence_authority": False,
        "geometry_name": "24D_NONCOMMUTATIVE_QUANTUM_RELATIVISTIC_COMPUTATIONAL_SPACETIME",
        "geometry_scope": "HHS_INTERNAL_COMPUTATIONAL_QUDIT_GEOMETRY",
        "physical_quantum_entanglement_claimed": False,
        "dimensions_per_qutrit_manifold": DIMENSIONS_PER_QUTRIT_MANIFOLD,
        "qutrit_manifold_count": QUTRIT_MANIFOLD_COUNT,
        "phase_cover_dimensions": PHASE_COVER_DIMENSIONS,
        "trinary_phase_tensor": TRINARY_PHASE_TENSOR,
        "direct_exchange_frame": variable_exchange_frame(flipped=False),
        "flipped_exchange_frame": variable_exchange_frame(flipped=True),
        "variable_exchange_involutive": (
            flip_variable_exchange_frame(
                flip_variable_exchange_frame(DIRECT_EXCHANGE_FRAME)
            )
            == DIRECT_EXCHANGE_FRAME
        ),
        "mandatory_equation_constructors": equations,
        "mandatory_proof_lemmas": lemmas,
        "mandatory_constructor_bundle_root_sha256": constructor_bundle_root(),
        "qutrit_manifolds": manifolds,
        "i036_holographic_nucleus": nucleus,
        "i036_vm81_frame": vm81,
        "dimension_closure": {
            "3*8": DIMENSIONS_PER_QUTRIT_MANIFOLD,
            "3*24": PHASE_COVER_DIMENSIONS,
            "72+9": PHASE_COVER_DIMENSIONS + LO_SHU_NUCLEUS_CELLS,
            "81*64": VM81_CELLS * POSITIONS_PER_CELL,
            "72^2": HASH72_SIDE * HASH72_SIDE,
            "5184": VM5184,
        },
        "p4_invariant_source": "P⁴=AB=c⁴=(a²+b²)²",
        "p8_fractal_scale_source": "A²+B²=P⁸={-,0,+}/∆",
        "pythagorean_invariant_source": "a²+b²=c²",
        "genesis_projection": {
            "a²": A2,
            "b²": B2,
            "c²": C2,
            "c⁴": C4,
            "P⁴": P4_COLLAPSE,
            "a²+b²=c²": A2 + B2 == C2,
            "P⁴=c⁴=(a²+b²)²": (
                P4_COLLAPSE == C4 == (A2 + B2) ** 2
            ),
        },
        "golay24_claim_boundary": {
            "carrier_positions": GOLAY_CODEWORD_BITS,
            "profile": "EXTENDED_BINARY_GOLAY_24_12_8",
            "profile_only": True,
            "codec_authority": False,
            "decoder_authority": False,
            "physical_rom_authority": False,
        },
        "all_three_qutrit_copies_full_information": all(
            manifold["full_information_copy"]
            and not manifold["partial_information_slice"]
            for manifold in manifolds
        ),
        "all_three_qutrit_copies_share_constructor_root": (
            len({
                manifold["mandatory_constructor_bundle_root_sha256"]
                for manifold in manifolds
            }) == 1
        ),
        "all_epsilon_residue_carriers_present": all(
            manifold["epsilon_residue_carriers_present"]
            and len(manifold["carriers"]) == 24
            for manifold in manifolds
        ),
        "host_float_arithmetic_used": False,
        "commutative_reordering_authorized": False,
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
    })


def validate_24d_constraint_spacetime_constructor(
    constructor: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(constructor, Mapping):
        raise Pass220I037SpacetimeError("constructor must be a mapping")
    if constructor.get("schema") != CONSTRUCTOR_SCHEMA:
        raise Pass220I037SpacetimeError("constructor schema mismatch")
    if not _receipt_matches(constructor):
        raise Pass220I037SpacetimeError("constructor receipt mismatch")
    if tuple(constructor.get("local_constraints", ())) != LOCAL_CONSTRAINTS:
        raise Pass220I037SpacetimeError("local constraint set mismatch")

    equations = tuple(constructor.get("mandatory_equation_constructors", ()))
    lemmas = tuple(constructor.get("mandatory_proof_lemmas", ()))
    if equations != mandatory_equation_constructors():
        raise Pass220I037SpacetimeError("mandatory equation constructor drift")
    if lemmas != mandatory_proof_lemmas():
        raise Pass220I037SpacetimeError("mandatory proof lemma drift")
    if not equations or not all(
        item.get("mandatory") is True and item.get("constructor") is True
        for item in equations
    ):
        raise Pass220I037SpacetimeError("equation constructor is not mandatory")
    if not lemmas or not all(
        item.get("mandatory") is True
        and item.get("constructor") is True
        and item.get("verified") is True
        for item in lemmas
    ):
        raise Pass220I037SpacetimeError("proof lemma closure failed")

    expected_root = constructor_bundle_root()
    if constructor.get("mandatory_constructor_bundle_root_sha256") != expected_root:
        raise Pass220I037SpacetimeError("mandatory constructor bundle root mismatch")

    manifolds = tuple(constructor.get("qutrit_manifolds", ()))
    if len(manifolds) != 3:
        raise Pass220I037SpacetimeError("three complete qutrit manifolds required")
    if tuple(item.get("trinary_phase") for item in manifolds) != TRINARY_LABELS:
        raise Pass220I037SpacetimeError("trinary phase order mismatch")

    for phase, manifold in zip(TRINARY_LABELS, manifolds):
        expected = build_24d_qutrit_manifold(phase)
        if manifold != expected:
            raise Pass220I037SpacetimeError(
                f"{phase} 24D manifold mismatch"
            )
        if manifold["dimensions"] != 24:
            raise Pass220I037SpacetimeError("24D manifold cardinality mismatch")
        if tuple(manifold["carrier_positions"]) != tuple(range(24)):
            raise Pass220I037SpacetimeError("Golay24 carrier coverage mismatch")
        if manifold["mandatory_constructor_bundle_root_sha256"] != expected_root:
            raise Pass220I037SpacetimeError("qutrit constructor root mismatch")
        if len(manifold["mandatory_equation_constructors"]) != len(equations):
            raise Pass220I037SpacetimeError("qutrit equation-copy loss")
        if len(manifold["mandatory_proof_lemmas"]) != len(lemmas):
            raise Pass220I037SpacetimeError("qutrit lemma-copy loss")
        if not all(
            carrier["mandatory_constructor_bundle_root_sha256"] == expected_root
            and carrier["normalization_erases_raw_expression"] is False
            and carrier["normalization_erases_exchange_provenance"] is False
            and carrier["normalization_erases_phase_identity"] is False
            and carrier["golay_codec_authority"] is False
            for carrier in manifold["carriers"]
        ):
            raise Pass220I037SpacetimeError("epsilon residue carrier loss")

    closure = constructor.get("dimension_closure")
    if closure != {
        "3*8": 24,
        "3*24": 72,
        "72+9": 81,
        "81*64": 5184,
        "72^2": 5184,
        "5184": 5184,
    }:
        raise Pass220I037SpacetimeError("dimension closure mismatch")

    genesis = constructor.get("genesis_projection")
    if genesis != {
        "a²": 1,
        "b²": 2,
        "c²": 3,
        "c⁴": 9,
        "P⁴": 9,
        "a²+b²=c²": True,
        "P⁴=c⁴=(a²+b²)²": True,
    }:
        raise Pass220I037SpacetimeError("Genesis invariant projection mismatch")

    golay = constructor.get("golay24_claim_boundary")
    if not isinstance(golay, Mapping):
        raise Pass220I037SpacetimeError("Golay24 claim boundary missing")
    if golay.get("carrier_positions") != 24:
        raise Pass220I037SpacetimeError("Golay24 carrier cardinality mismatch")
    if golay.get("profile_only") is not True:
        raise Pass220I037SpacetimeError("Golay profile-only boundary lost")
    for key in ("codec_authority", "decoder_authority", "physical_rom_authority"):
        if golay.get(key) is not False:
            raise Pass220I037SpacetimeError(f"Golay authority escalation: {key}")

    if constructor.get("all_three_qutrit_copies_full_information") is not True:
        raise Pass220I037SpacetimeError("full-copy redundancy lost")
    if constructor.get("all_three_qutrit_copies_share_constructor_root") is not True:
        raise Pass220I037SpacetimeError("constructor-root redundancy lost")
    if constructor.get("all_epsilon_residue_carriers_present") is not True:
        raise Pass220I037SpacetimeError("epsilon residue carrier coverage lost")
    if constructor.get("variable_exchange_involutive") is not True:
        raise Pass220I037SpacetimeError("variable-exchange involution failed")
    if constructor.get("host_float_arithmetic_used") is not False:
        raise Pass220I037SpacetimeError("host floating arithmetic forbidden")
    if constructor.get("commutative_reordering_authorized") is not False:
        raise Pass220I037SpacetimeError("commutative reorder authorization forbidden")

    for field in (
        "canonical_service",
        "canonical_constraint_creation_authority",
        "canonical_constraint_enforcement_authority",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "direct_canonical_persistence_authority",
    ):
        if constructor.get(field) is not False:
            raise Pass220I037SpacetimeError(f"authority escalation: {field}")

    return {
        "ok": True,
        "dimensions_per_qutrit_manifold": 24,
        "qutrit_manifold_count": 3,
        "phase_cover_dimensions": 72,
        "vm81_cells": 81,
        "vm5184": 5184,
        "equation_constructor_count": len(equations),
        "proof_lemma_count": len(lemmas),
        "epsilon_residue_carrier_count": sum(
            len(manifold["carriers"]) for manifold in manifolds
        ),
        "mandatory_constructor_bundle_root_sha256": expected_root,
        "golay_profile_only": True,
        "full_copy_redundancy": True,
    }


def twentyfour_d_constraint_spacetime_witness() -> Dict[str, Any]:
    constructor = build_24d_constraint_spacetime_constructor()
    result = validate_24d_constraint_spacetime_constructor(constructor)
    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": result["ok"],
        "result": result,
        "constructor_receipt_sha256": constructor["receipt_sha256"],
        "trinary_phase_tensor": TRINARY_PHASE_TENSOR,
        "mandatory_equation_ids": tuple(
            item["equation_id"]
            for item in constructor["mandatory_equation_constructors"]
        ),
        "mandatory_lemma_ids": tuple(
            item["lemma_id"]
            for item in constructor["mandatory_proof_lemmas"]
        ),
        "all_three_full_copies": constructor[
            "all_three_qutrit_copies_full_information"
        ],
        "all_epsilon_residue_carriers_present": constructor[
            "all_epsilon_residue_carriers_present"
        ],
        "golay24_profile_only": True,
        "canonical_admission_authority": False,
    })


def twentyfour_d_constraint_spacetime_self_test() -> Dict[str, Any]:
    return twentyfour_d_constraint_spacetime_witness()
