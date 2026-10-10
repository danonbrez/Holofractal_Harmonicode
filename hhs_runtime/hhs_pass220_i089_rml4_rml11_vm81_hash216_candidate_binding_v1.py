"""Pass 220 I089: original RML4->RML11->I070 VM81->I065 Hash216 candidate.

Executes original, independently registered services and proves the
finite *eight-channel / u^18 quarter-turn* fidelity witness connecting
I088's Cl(0,8) quotient to the original RML4 gyroscope's typed
phase source. Also binds this proof to an actual original I070
VM81 nucleus candidate, three 72-glyph Hash216 planes and I065
lossless hydration. No new native full-tensor embedding, 5184-byte
canonical carrier, signed VM81 mutation or canonical Hash72 mint.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i088_exact_clifford_word_inverse_v1 import (
    prove_i088_word_inverse,
)
from hhs_runtime.hhs_pass220_i086_ordered_3x3_vm5184_hash72_matrix_v1 import (
    SOURCE as I086_MATRIX_SOURCE,
    MATRIX as I086_MATRIX,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    hash72 as original_candidate_hash72,
)
from hhs_runtime.hhs_pass220_i070_i_tensor_lane5_vm81_bridge_v1 import (
    build_lane5_vm81_candidate, validate_lane5_vm81_candidate,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
)
from hhs_runtime.hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 import (
    PHASE_BASIS,
    build_nucleus_qudit_surface, encode_phase_slot,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS, PRODUCTS, PRODUCT_RELATIONS,
    build_gyroscope_state, expected_product_phase,
)
from hhs_runtime.pass219.phase_clifford_intertwiner import (
    QUARTER_CYCLE_STEPS,
    _channel_action_matrices, _matrix_hash, _matmul, _identity,
    build_phase_transport_clifford_lift,
    build_one_gyroscope_clifford_channel_actions,
)

SCHEMA="HHS_PASS220_I089_ORIGINAL_RML4_RML11_VM81_HASH216_CANDIDATE_V1"
PHASE8=("x","y","z","w","xy","yx","zw","wz")
ORDERED_WX="wx"
SINGLE_QUARTER_STEPS=18
INITIAL_PRIMITIVE_PHASES={"x":7,"y":19,"z":31,"w":43}
ORIGINAL_SIGNED_PAIRS={"xy":1,"yx":-1,"zw":1,"wz":-1}
MATRIX_SOURCE=I086_MATRIX_SOURCE
REMAINING_NATIVE_PROOFS=(
    "native-RNA-VM81:faithful-semantic-extension-beyond-exact-u18-Cl08-subalgebra",
    "wx:w-times-x-original-native-composite-address-and-phase-registration",
    "native-I088-quotient:left-right-Division-under-global-Delta-tensor",
    "VM81-81x64:full-native-cell-payload-BigInt-replay-beyond-sparse-Cl08",
    "Hash72:inherited-signed-canonical-ledger-mint-not-candidate-fingerprint",
    "Hash216:environmental-previous-state-verified-before-signed-mutation",
    "Lean-I051-ethical-E01-E18:real-candidate-admission-before-user-egress",
)


class I089CandidateBindingError(ValueError):
    pass


def _json(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=False,allow_nan=False).encode("utf-8")


def _strict_index(value:Any,upper:int,label:str)->int:
    if isinstance(value,bool) or not isinstance(value,int) or not 0<=value<upper:
        raise I089CandidateBindingError(f"{label}:exact-bounded-integer-required")
    return value


def _state():
    phases=dict(INITIAL_PRIMITIVE_PHASES)
    for name in ("xy","yx","zw","wz"):
        relation=PRODUCT_RELATIONS[name]
        phases[name]=expected_product_phase(
            phases[relation["generator"]], ORIGINAL_SIGNED_PAIRS[name]
        )
    state=build_gyroscope_state(
        phases, dict(ORIGINAL_SIGNED_PAIRS),
        state_id="PASS220:I089:I086-exact-ordered-source",
        ancestry_root_sha256=sha256(MATRIX_SOURCE.encode("utf-8")).hexdigest(),
    )
    if (
        state["admissible_product_geometry"] is not True
        or state["canonical_vm81_mutation_authority"] is not False
        or tuple(state["phases"])!=PHASE8
    ):
        raise I089CandidateBindingError("inherited RML4 state is not admissible")
    return state


@lru_cache(maxsize=1)
def _original_i088_receipt()->dict[str,Any]:
    r=prove_i088_word_inverse()
    required=(
        "exact_clifford_word_inverse_left",
        "exact_clifford_word_inverse_right",
        "exact_clifford_word_5184_quotient_left",
        "exact_clifford_word_5184_quotient_right",
    )
    if any(r.get(v) is not True for v in required):
        raise I089CandidateBindingError("original I088 exact inverse not closed")
    if (
        r.get("exact_clifford_word_inverse_nonzero_terms")!=52
        or r.get("canonical_hash72_from_clifford_candidate_admitted") is not False
    ):
        raise I089CandidateBindingError("I088 sparse proof or authority diverged")
    return r


def _eight_original_quarter_channel_bindings(state:Mapping[str,Any]):
    source=build_one_gyroscope_clifford_channel_actions()
    actions=_channel_action_matrices()
    if (
        tuple(source["channel_order"])!=PHASE8
        or tuple(CHANNELS)!=PHASE8
        or tuple(PHASE_BASIS)!=PHASE8
        or tuple(actions)!=PHASE8
    ):
        raise I089CandidateBindingError("original RML4/RML11/I071 phase order drift")
    if source.get("canonical_vm81_mutation_authority") is not False:
        raise I089CandidateBindingError("original Clifford source claims mutation")
    rows=[]
    identity=_identity(16)
    for channel in PHASE8:
        steps={s:0 for s in PHASE8}
        steps[channel]=SINGLE_QUARTER_STEPS
        native_transport=build_phase_transport_clifford_lift(
            state, steps,transport_id=f"I089:{channel}:quarter:u18"
        )
        if (
            native_transport["complete_clifford_lift"] is not True
            or native_transport["residual_u72_phase_preserved"] is not False
            or native_transport["ordered_reverse_factor_inverse_verified"] is not True
            or native_transport["quarter_component_matrix_sha256"]!=_matrix_hash(actions[channel])
            or native_transport["canonical_vm81_mutation_authority"] is not False
        ):
            raise I089CandidateBindingError("original RML11 quarter phase mismatch")
        for factor in native_transport["factors"]:
            expected=1 if factor["channel"]==channel else 0
            if (
                factor["signed_quarter_units"]!=expected
                or factor["residual_phase_steps"]!=0
            ):
                raise I089CandidateBindingError("quarter phase residue/order drift")
        if _matmul(actions[channel],actions[channel])!=tuple(
            tuple(-v for v in row) for row in identity
        ):
            raise I089CandidateBindingError("original RML11 u18 action square drift")
        row={
            "channel":channel,
            "phase_slot_order":PHASE8.index(channel),
            "phase_from_original_state":state["phases"][channel],
            "original_phase_transport_sha256":native_transport["transport_sha256"],
            "actual_original_clifford_matrix_sha256":_matrix_hash(actions[channel]),
            "quarter_turn_phase_steps":SINGLE_QUARTER_STEPS,
            "exact_quarter_turn_complete":True,
            "reverse_original_order_inverse_verified":True,
            "phase_residual":0,
            "native_full_u72_lift_proven":False,
        }
        if channel in PRODUCTS:
            relation=PRODUCT_RELATIONS[channel]
            if _matmul(actions[relation["generator"]],
                       actions[relation["reciprocal"]])!=actions[channel]:
                raise I089CandidateBindingError("source ordered reciprocal product drift")
            row["ordered_generator"]=relation["generator"]
            row["ordered_reciprocal"]=relation["reciprocal"]
            row["source_half_phase_sign"]=ORIGINAL_SIGNED_PAIRS[channel]
        rows.append(row)
    return source,rows


def bind_i089_original_phase_vm81_candidate(
    nucleus_index:int=0,*,
    phase_channel:int=0,
    residual_probe_steps:int=19,
)->dict[str,Any]:
    """Read-only source-bound continuation, exact source/phase/Hash216 replay."""
    nucleus=_strict_index(nucleus_index,9,"nucleus")
    channel=_strict_index(phase_channel,8,"phase_channel")
    if (
        isinstance(residual_probe_steps,bool)
        or not isinstance(residual_probe_steps,int)
        or residual_probe_steps not in (18,19)
    ):
        raise I089CandidateBindingError("bounded exact 18/19 transport probe required")
    i088=_original_i088_receipt()
    state=_state()
    original_clifford,action_rows=_eight_original_quarter_channel_bindings(state)

    residual_steps={name:0 for name in PHASE8}
    residual_steps[PHASE8[channel]]=residual_probe_steps
    residual=build_phase_transport_clifford_lift(
        state,residual_steps,transport_id=f"I089:residual:{channel}:{residual_probe_steps}"
    )
    q,residual_exact=divmod(residual_probe_steps,18)
    if (
        residual["complete_clifford_lift"] is not (residual_exact==0)
        or residual["residual_u72_phase_preserved"] is not (residual_exact!=0)
    ):
        raise I089CandidateBindingError("RML11 residual 72-phase loss")

    i070=build_lane5_vm81_candidate(nucleus)
    if validate_lane5_vm81_candidate(i070) is not True:
        raise I089CandidateBindingError("original VM81 I070 candidate invalid")
    if (
        i070["nucleus_index"]!=nucleus
        or len(i070["candidate_hash216"])!=216
        or i070["authority"]["canonical_vm81_mutation_authority"] is not False
    ):
        raise I089CandidateBindingError("original I070 authority/source changed")
    surface=build_nucleus_qudit_surface(
        shared_root_sha256=sha256(MATRIX_SOURCE.encode("utf-8")).hexdigest(),
        nucleus_index=nucleus,
    )
    if len(surface)!=72:
        raise I089CandidateBindingError("original I071 Lo Shu phase surface incomplete")
    for slot,geometry in enumerate(surface):
        basis,outcome=divmod(slot,9)
        if (
            geometry.phase_slot!=slot
            or geometry.phase_symbol!=PHASE8[basis]
            or geometry.vm81_cell_id!=nucleus*9+outcome
        ):
            raise I089CandidateBindingError("original I071 cell/phase address mismatch")

    # The actual source-bound transition joins earlier I070 candidate
    # ancestry with I088's exact sparse quotient and RML11 transport.
    # Its three original 72-character planes are rehydrated by I065.
    source={
        "schema":SCHEMA,
        "i086_literal_matrix":MATRIX_SOURCE,
        "i088_exact_clifford_quotient_sha256":i088[
            "exact_clifford_word_quotient_coefficient_sha256"],
        "i088_52term_quotient_source_candidate_hash72":i088[
            "i069_72_character_candidate_hash72_from_actual_clifford_quotient"],
        "original_RML4_phase_state_sha256":state["state_sha256"],
        "original_RML11_channel_witness_sha256":original_clifford["witness_sha256"],
        "original_RML11_quarter_channels":action_rows,
        "original_RML11_bounded_probe_sha256":residual["transport_sha256"],
        "original_I070_binding_hash72":i070["binding_hash72"],
        "original_I070_parent_candidate_hash216":i070["candidate_hash216"],
        "original_I071_nucleus":nucleus,
        "original_I071_phase_channel":channel,
        "original_I071_phase_slot":encode_phase_slot(channel,4),
        "source_result_authority":"CANDIDATE_ONLY",
    }
    preceding=i070["binding_hash72"]  # prior whole-candidate identity, not a change lane
    transition=original_candidate_hash72(source)
    receipt=original_candidate_hash72({
        "schema":SCHEMA,
        "previous_hash72":preceding,
        "change_hash72":transition,
        "source_bound":source,
        "original_i070_receipt_hash72":i070["candidate_receipt_hash72"],
        "original_i070_authority":i070["authority"],
    })
    candidate216=preceding+transition+receipt
    if any(len(v)!=72 for v in (preceding,transition,receipt)):
        raise I089CandidateBindingError("original three candidate Hash72 words malformed")
    hydration=hydrate_hash216_geometry(candidate216)
    if hydration["roundtrip_exact"] is not True or len(candidate216)!=216:
        raise I089CandidateBindingError("inherited I065 three-plane hydration failed")
    return {
        "schema":SCHEMA,
        "i086_literal_source":MATRIX_SOURCE,
        "i088_exact_word_quotient_sha256":source["i088_exact_clifford_quotient_sha256"],
        "i088_52term_original_clifford_quotient_replayed":True,
        "original_rml4_state_sha256":state["state_sha256"],
        "original_rml4_u72_state":dict(state["phases"]),
        "original_rml11_channel_witness_sha256":original_clifford["witness_sha256"],
        "original_eight_quarter_turn_channel_receipts":action_rows,
        "rml11_exact_u18_channel_action_fidelity_all8_proven":True,
        "rml11_residual_probe":{
            "channel":PHASE8[channel],
            "steps":residual_probe_steps,
            "quarter_units":q,
            "residual_steps":residual_exact,
            "complete_clifford_lift":residual["complete_clifford_lift"],
            "remaining_native_u72_phase_preserved":
                residual["residual_u72_phase_preserved"],
            "original_transport_sha256":residual["transport_sha256"],
        },
        "original_i070_vm81_candidate_binding_hash72":i070["binding_hash72"],
        "original_i070_candidate_hash216":i070["candidate_hash216"],
        "original_i071_exact_phase_slots":72,
        "original_i071_nucleus":nucleus,
        "original_i071_phase_slot_for_center":encode_phase_slot(channel,4),
        "source_bound_previous_hash72":preceding,
        "source_bound_change_hash72":transition,
        "source_bound_receipt_hash72":receipt,
        "source_bound_candidate_hash216":candidate216,
        "original_i065_three_plane_hydration_roundtrip":True,
        "original_i065_hydration_plane_count":len(hydration["planes"]),
        "candidate_source_identity_sha256":sha256(_json(source)).hexdigest(),
        "native_obligations_still_held":list(REMAINING_NATIVE_PROOFS),
        "complete_vm81_to_clifford_algebra_faithfulness_proven":False,
        "complete_u72_root_transport_proven":False,
        "native_wx_vm81_operator_registered":False,
        "native_full_matrix_division_admitted":False,
        "canonical_hash72_minted":False,
        "canonical_hash216_transition_committed":False,
        "signed_vm81_mutation":False,
        "candidate_only":True,
        "floating_point_authority":False,
    }
