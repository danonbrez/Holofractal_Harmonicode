"""Pass 220 cross-layer priority offset information-preserving translation.

This successor to the NumPy1 four-phase A/B experiment tests whether the compact
scalar/control-symbol + offset-permutation representation can be the priority
default across compatible HHS layers.

Promotion is information-first.  Speed is supporting evidence only.

A candidate is promotable only when the dense reference arm and compact arm
preserve the same complete tagged state through:
- U9 ordered permutation and inverse recovery,
- fixed-width 5184 serialization,
- RNA/Hash72/Digital-DNA ordered phase binding,
- canonical 81-cell qudit serialization/reconstruction,
- supplied circuit-tensor U9 closure,
- HNAN ordered Lo Shu + explicit zero/EmptySet/HNAN center identity,
- residual xy+epsilon projection preservation.

No layer gains VM81 mutation, Hash72 mint, or Hash216 persistence authority.
"""
from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass115_canonical_qudit_serialization_v1 import (
    CanonicalQuditSerializationEngine,
    ManifoldContract,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    VM81_CELLS,
    deserialize_offsets_5184,
    serialize_offsets_5184,
)
from hhs_runtime.hhs_pass220_numpy_four_phase_ab_v1 import (
    CHANNELS,
    CHANNEL_LABELS,
    PHASE_PLAN,
    supplied_tensor_u9_acceptance,
    supplied_tensor_u9_witness,
)
from hhs_runtime.hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1 import (
    phase_locked_state_witness,
)
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_CENTER_EXPRESSION,
    HNAN_TERMINAL_SOURCE,
    HNAN_ZERO_CLOSURE_SOURCE,
    hnan_loshu_resolution_receipt,
    invariant_receipt as hnan_invariant_receipt,
)
from hhs_runtime.pass219.lane5_genesis_orientation_u9_qe_bridge import (
    apply_permutation,
)

SCHEMA = "HHS_PASS220_PRIORITY_OFFSET_INFORMATION_TRANSLATION_V1"
PERFORMANCE_SCHEMA = "HHS_PASS220_PRIORITY_OFFSET_PERFORMANCE_SUPPORT_V1"
VERSION = "1.0.0"
BLOCK_WIDTH = 9
BLOCK_COUNT = VM81_CELLS // BLOCK_WIDTH
PRIORITY_DEFAULT = "SCALAR_SYMBOL_PERMUTATION_CONTROL_PLUS_OFFSET_VECTORIZATION"
REFERENCE_FALLBACK = "DENSE_SUBSTITUTION_TENSOR_REFERENCE"
HNAN_ZERO_EMPTYSET_CENTER_SOURCE = (
    "0=∅=HNAN=" + HNAN_CENTER_EXPRESSION
)


class HHSInformationTranslationError(ValueError):
    pass


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=list,
    )


def _sha(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _source_offsets(offsets: Sequence[int] | None = None) -> tuple[int, ...]:
    values = (
        tuple(index % 9 for index in range(VM81_CELLS))
        if offsets is None
        else tuple(offsets)
    )
    if len(values) != VM81_CELLS:
        raise HHSInformationTranslationError(
            "information translation requires exactly 81 offsets"
        )
    if any(
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 <= value <= 8
        for value in values
    ):
        raise HHSInformationTranslationError(
            "information translation offsets must be exact digits 0..8"
        )
    return values


def _source_tagged_state(
    offsets: Sequence[int] | None = None,
) -> tuple[tuple[int, int, int, int], ...]:
    values = _source_offsets(offsets)
    phases = tuple((index * 8) % 72 for index in range(VM81_CELLS))
    rotations = tuple(index % 4 for index in range(VM81_CELLS))
    return tuple(
        (values[index], phases[index], rotations[index], index)
        for index in range(VM81_CELLS)
    )


def _blocks(
    state: Sequence[tuple[int, int, int, int]],
) -> tuple[tuple[tuple[int, int, int, int], ...], ...]:
    values = tuple(state)
    if len(values) != VM81_CELLS:
        raise HHSInformationTranslationError("tagged state width drift")
    return tuple(
        values[start : start + BLOCK_WIDTH]
        for start in range(0, VM81_CELLS, BLOCK_WIDTH)
    )


def _dense_apply(
    block: Sequence[Any],
    permutation: Sequence[int],
) -> tuple[Any, ...]:
    source = tuple(block)
    perm = tuple(int(value) for value in permutation)
    if len(source) != BLOCK_WIDTH or len(perm) != BLOCK_WIDTH:
        raise HHSInformationTranslationError("U9 block width drift")
    matrix = [[0] * BLOCK_WIDTH for _ in range(BLOCK_WIDTH)]
    for column, row in enumerate(perm, start=1):
        matrix[row - 1][column - 1] = 1
    output = []
    for row in matrix:
        selected = [
            source[index]
            for index, coefficient in enumerate(row)
            if coefficient == 1
        ]
        if len(selected) != 1:
            raise HHSInformationTranslationError(
                "dense U9 selection must preserve one complete tagged cell"
            )
        output.append(selected[0])
    return tuple(output)


def _translate_tagged(
    state: Sequence[tuple[int, int, int, int]],
    channel: str,
    *,
    dense: bool,
    inverse: bool = False,
) -> tuple[tuple[int, int, int, int], ...]:
    if channel not in CHANNELS:
        raise HHSInformationTranslationError("unknown ordered phase channel")
    output = []
    for block, plan in zip(_blocks(state), PHASE_PLAN, strict=True):
        control = plan["channels"][channel]
        permutation = (
            control["inverse_permutation"]
            if inverse
            else control["permutation"]
        )
        translated = (
            _dense_apply(block, permutation)
            if dense
            else apply_permutation(block, permutation)
        )
        output.extend(translated)
    return tuple(output)


def _state_components(
    state: Sequence[tuple[int, int, int, int]],
) -> dict[str, tuple[int, ...]]:
    cells = tuple(state)
    return {
        "values": tuple(cell[0] for cell in cells),
        "phases": tuple(cell[1] for cell in cells),
        "rotations": tuple(cell[2] for cell in cells),
        "source_indices": tuple(cell[3] for cell in cells),
    }


def _zero_provenance(
    state: Sequence[tuple[int, int, int, int]],
) -> tuple[int, ...]:
    return tuple(
        source_index
        for value, _, _, source_index in state
        if value == 0
    )


def _qudit_witness(
    state: Sequence[tuple[int, int, int, int]],
) -> dict[str, Any]:
    components = _state_components(state)
    engine = CanonicalQuditSerializationEngine()
    manifold = engine.serialize(
        components["values"],
        contract=ManifoldContract(),
        phases=components["phases"],
        rotations=components["rotations"],
    )
    engine.validate(manifold)
    reconstructed = engine.reconstruct(manifold)
    exact = (
        tuple(reconstructed["values"]) == components["values"]
        and tuple(reconstructed["phases"]) == components["phases"]
        and tuple(reconstructed["rotations"]) == components["rotations"]
    )
    return {
        "serialization_root_hash72": manifold["serialization_root_hash72"],
        "source_manifold_root_hash72": manifold[
            "source_manifold_root_hash72"
        ],
        "position_coordinate_bijection_root_hash72": manifold[
            "position_coordinate_bijection_root_hash72"
        ],
        "topology_derivation_root_hash72": manifold[
            "topology_derivation_root_hash72"
        ],
        "exact_reconstruction": exact,
        "reconstructed_values": tuple(reconstructed["values"]),
        "reconstructed_phases": tuple(reconstructed["phases"]),
        "reconstructed_rotations": tuple(reconstructed["rotations"]),
    }


def hnan_information_gate_witness() -> dict[str, Any]:
    invariant = hnan_invariant_receipt()
    loshu = hnan_loshu_resolution_receipt()
    checks = {
        "invariant_pass": invariant["status"] == "PASS",
        "loshu_pass": loshu["status"] == "PASS",
        "terminal_xy_plus_epsilon": (
            loshu["terminal_source"] == HNAN_TERMINAL_SOURCE == "xy+epsilon"
        ),
        "bare_xy_forbidden": loshu["bare_xy_terminal_authorized"] is False,
        "epsilon_elision_forbidden": (
            loshu["epsilon_elision_authorized"] is False
        ),
        "commutation_forbidden": (
            loshu["ordered_product_commutation_authorized"] is False
        ),
        "host_scalar_epsilon_forbidden": (
            loshu["host_scalar_epsilon_authorized"] is False
        ),
        "center_expression_bound": (
            loshu["center_expression"]
            == invariant["hnan_center_expression"]
            == HNAN_CENTER_EXPRESSION
        ),
        "explicit_zero_emptyset_hnan_center_identity": (
            HNAN_ZERO_EMPTYSET_CENTER_SOURCE
            == "0=∅=HNAN=x+y-z-w+xy+yx-zw-wz"
        ),
        "explicit_hnan_center_matches_receipt_center": (
            HNAN_ZERO_EMPTYSET_CENTER_SOURCE.split("HNAN=", 1)[1]
            == loshu["center_expression"]
        ),
        "inherited_ab_over_p4_zero_closure_preserved": (
            invariant["hnan_zero_closure_source"]
            == HNAN_ZERO_CLOSURE_SOURCE
            == "0=∅=AB/P⁴∅=HNAN"
        ),
    }
    body = {
        "schema": "HHS_PASS220_PRIORITY_OFFSET_HNAN_INFORMATION_GATE_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "hnan_invariant_receipt_sha256": invariant["receipt_sha256"],
        "hnan_loshu_receipt_sha256": loshu["receipt_sha256"],
        "explicit_zero_emptyset_hnan_center_source": (
            HNAN_ZERO_EMPTYSET_CENTER_SOURCE
        ),
        "inherited_ab_over_p4_zero_closure_source": (
            HNAN_ZERO_CLOSURE_SOURCE
        ),
        "center_expression": HNAN_CENTER_EXPRESSION,
        "terminal_source": loshu["terminal_source"],
        "bare_xy_terminal_authorized": loshu[
            "bare_xy_terminal_authorized"
        ],
        "epsilon_elision_authorized": loshu[
            "epsilon_elision_authorized"
        ],
        "ordered_product_commutation_authorized": loshu[
            "ordered_product_commutation_authorized"
        ],
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }
    return {**body, "witness_sha256": _sha(body)}


def channel_information_translation_witness(
    channel: str,
    offsets: Sequence[int] | None = None,
) -> dict[str, Any]:
    source = _source_tagged_state(offsets)
    arm_a = _translate_tagged(source, channel, dense=True)
    arm_b = _translate_tagged(source, channel, dense=False)
    recovered = _translate_tagged(
        arm_b,
        channel,
        dense=False,
        inverse=True,
    )

    source_components = _state_components(source)
    a_components = _state_components(arm_a)
    b_components = _state_components(arm_b)
    recovered_components = _state_components(recovered)

    serialized_a = serialize_offsets_5184(a_components["values"])
    serialized_b = serialize_offsets_5184(b_components["values"])
    serialized_source = serialize_offsets_5184(source_components["values"])
    recovered_serialized = serialize_offsets_5184(
        recovered_components["values"]
    )

    rna_a = phase_locked_state_witness(serialized_a)
    rna_b = phase_locked_state_witness(serialized_b)
    qudit_a = _qudit_witness(arm_a)
    qudit_b = _qudit_witness(arm_b)

    source_zero_provenance = _zero_provenance(source)
    translated_zero_a = _zero_provenance(arm_a)
    translated_zero_b = _zero_provenance(arm_b)
    recovered_zero_provenance = _zero_provenance(recovered)

    checks = {
        "complete_tagged_state_equal": arm_a == arm_b,
        "payload_values_equal": a_components["values"] == b_components["values"],
        "phase_history_equal": a_components["phases"] == b_components["phases"],
        "rotation_history_equal": (
            a_components["rotations"] == b_components["rotations"]
        ),
        "source_provenance_equal": (
            a_components["source_indices"] == b_components["source_indices"]
        ),
        "inverse_recovers_complete_tagged_source": recovered == source,
        "inverse_values_exact": (
            recovered_components["values"] == source_components["values"]
        ),
        "inverse_phases_exact": (
            recovered_components["phases"] == source_components["phases"]
        ),
        "inverse_rotations_exact": (
            recovered_components["rotations"]
            == source_components["rotations"]
        ),
        "inverse_provenance_exact": (
            recovered_components["source_indices"]
            == source_components["source_indices"]
        ),
        "zero_provenance_equal_between_arms": (
            translated_zero_a == translated_zero_b
        ),
        "zero_provenance_inverse_exact": (
            recovered_zero_provenance == source_zero_provenance
        ),
        "serialized_5184_equal": serialized_a == serialized_b,
        "serialized_5184_width_exact": (
            len(serialized_a) == len(serialized_b) == 5184
        ),
        "serialized_5184_inverse_exact": (
            recovered_serialized == serialized_source
        ),
        "serialized_deserialize_exact": (
            deserialize_offsets_5184(serialized_b)
            == b_components["values"]
        ),
        "rna_phase_locked_both": (
            rna_a["phase_locked"] is True
            and rna_b["phase_locked"] is True
        ),
        "rna_state_identity_equal": (
            rna_a["state_root_sha256"] == rna_b["state_root_sha256"]
        ),
        "rna_ordered_phase_binding_equal": (
            rna_a["digital_dna"][
                "serialized_operand_phase_binding"
            ]["complete_binding_root_sha256"]
            == rna_b["digital_dna"][
                "serialized_operand_phase_binding"
            ]["complete_binding_root_sha256"]
        ),
        "rna_ordered_products_not_collapsed": (
            rna_a["digital_dna"]["ordered_products_collapsed"] is False
            and rna_b["digital_dna"]["ordered_products_collapsed"] is False
        ),
        "rna_xy_yx_zw_wz_exact": (
            rna_a["digital_dna"]["q_minus_one_ordered_products"]
            == rna_b["digital_dna"]["q_minus_one_ordered_products"]
            == (
                ("xy", 1),
                ("yx", -1),
                ("zw", 1),
                ("wz", -1),
            )
        ),
        "qudit_serialization_identity_equal": (
            qudit_a["serialization_root_hash72"]
            == qudit_b["serialization_root_hash72"]
        ),
        "qudit_source_manifold_identity_equal": (
            qudit_a["source_manifold_root_hash72"]
            == qudit_b["source_manifold_root_hash72"]
        ),
        "qudit_position_bijection_equal": (
            qudit_a["position_coordinate_bijection_root_hash72"]
            == qudit_b["position_coordinate_bijection_root_hash72"]
        ),
        "qudit_topology_equal": (
            qudit_a["topology_derivation_root_hash72"]
            == qudit_b["topology_derivation_root_hash72"]
        ),
        "qudit_reconstruction_exact": (
            qudit_a["exact_reconstruction"]
            and qudit_b["exact_reconstruction"]
        ),
    }

    body = {
        "schema": "HHS_PASS220_PRIORITY_OFFSET_CHANNEL_TRANSLATION_V1",
        "channel": channel,
        "phase_label": CHANNEL_LABELS[channel],
        "source_identity_sha256": _sha(source),
        "dense_translation_identity_sha256": _sha(arm_a),
        "compact_translation_identity_sha256": _sha(arm_b),
        "inverse_identity_sha256": _sha(recovered),
        "checks": checks,
        "information_preserved": all(checks.values()),
        "source_zero_provenance": source_zero_provenance,
        "translated_zero_provenance": translated_zero_b,
        "source_5184_sha256": sha256(
            serialized_source.encode("utf-8")
        ).hexdigest(),
        "translated_5184_sha256": sha256(
            serialized_b.encode("utf-8")
        ).hexdigest(),
        "rna_state_root_sha256": rna_b["state_root_sha256"],
        "rna_binding_root_sha256": rna_b["digital_dna"][
            "serialized_operand_phase_binding"
        ]["complete_binding_root_sha256"],
        "qudit_serialization_root_hash72": qudit_b[
            "serialization_root_hash72"
        ],
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }
    return {**body, "witness_sha256": _sha(body)}


def build_cross_layer_information_witness(
    offsets: Sequence[int] | None = None,
) -> dict[str, Any]:
    channels = {
        channel: channel_information_translation_witness(channel, offsets)
        for channel in CHANNELS
    }
    hnan = hnan_information_gate_witness()
    circuit = supplied_tensor_u9_witness()
    circuit_ok = supplied_tensor_u9_acceptance(circuit)
    all_channels = all(
        witness["information_preserved"]
        for witness in channels.values()
    )

    checks = {
        "all_four_ordered_channels_information_preserved": all_channels,
        "hnan_information_gate_pass": hnan["status"] == "PASS",
        "hnan_explicit_zero_emptyset_center_identity": (
            hnan["explicit_zero_emptyset_hnan_center_source"]
            == "0=∅=HNAN=x+y-z-w+xy+yx-zw-wz"
        ),
        "hnan_inherited_ab_over_p4_zero_closure": (
            hnan["inherited_ab_over_p4_zero_closure_source"]
            == "0=∅=AB/P⁴∅=HNAN"
        ),
        "hnan_terminal_xy_plus_epsilon": (
            hnan["terminal_source"] == "xy+epsilon"
        ),
        "hnan_bare_xy_rejected": (
            hnan["bare_xy_terminal_authorized"] is False
        ),
        "hnan_epsilon_elision_rejected": (
            hnan["epsilon_elision_authorized"] is False
        ),
        "hnan_commutation_rejected": (
            hnan["ordered_product_commutation_authorized"] is False
        ),
        "supplied_u9_circuit_tensor_pass": circuit_ok,
        "u9_power_9_identity": circuit["u9_power_9_is_identity"] is True,
        "u9_payload_verbatim": (
            circuit["payload_verbatim_all_powers"] is True
        ),
        "u9_slot_provenance_preserved": (
            circuit["slot_provenance_preserved_all_powers"] is True
        ),
        "no_vm81_authority_escalation": True,
        "no_hash72_authority_escalation": True,
        "no_hash216_authority_escalation": True,
    }
    body = {
        "schema": SCHEMA,
        "version": VERSION,
        "priority_candidate": PRIORITY_DEFAULT,
        "reference_fallback": REFERENCE_FALLBACK,
        "information_preservation_is_primary_gate": True,
        "speed_is_supporting_evidence_only": True,
        "channels": channels,
        "hnan_gate": hnan,
        "supplied_u9_circuit_tensor_sha256": circuit[
            "supplied_circuit_tensor_sha256"
        ],
        "checks": checks,
        "information_preservation_closed": all(checks.values()),
        "priority_default_eligible": all(checks.values()),
        "fallback_required_on_any_information_failure": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }
    return {**body, "witness_sha256": _sha(body)}


def performance_support_witness(
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    if (
        evidence.get("schema")
        != "HHS_PASS220_NUMPY1_FOUR_PHASE_AB_MEASURED_RESULT_V1"
    ):
        raise HHSInformationTranslationError(
            "measured A/B evidence schema mismatch"
        )
    medians = evidence.get("channel_medians_ns") or {}
    channels_present = tuple(sorted(medians)) == tuple(sorted(CHANNELS))
    faster = all(
        row.get("scalar_offset_vector", 0)
        < row.get("dense_substitution", 0)
        for row in medians.values()
    ) if channels_present else False
    semantic = evidence.get("semantic_identity") is True
    u9 = evidence.get("supplied_u9_circuit_tensor") or {}
    u9_ok = all(
        (
            u9.get("u9_power_9_is_identity") is True,
            u9.get("nine_distinct_preclosure_positional_states") is True,
            u9.get("full_orbit_returns_tagged_source_exactly") is True,
            u9.get("dense_vector_u9_identity_all_powers") is True,
            u9.get("inverse_roundtrip_all_powers") is True,
            u9.get("payload_verbatim_all_powers") is True,
        )
    )
    selected = (
        (evidence.get("candidate_selection") or {}).get("selected")
        == PRIORITY_DEFAULT
    )
    body = {
        "schema": PERFORMANCE_SCHEMA,
        "measured_evidence_schema": evidence.get("schema"),
        "experiment_head": evidence.get("experiment_head"),
        "semantic_identity": semantic,
        "all_four_channels_present": channels_present,
        "all_four_channels_compact_faster_on_median": faster,
        "u9_measured_information_preservation": u9_ok,
        "selected_candidate_matches_priority_default": selected,
        "timing_is_canonical": False,
        "supports_priority_default": all(
            (semantic, channels_present, faster, u9_ok, selected)
        ),
    }
    return {**body, "witness_sha256": _sha(body)}


def priority_default_decision(
    information_witness: Mapping[str, Any],
    performance_witness: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    information_ok = (
        information_witness.get("schema") == SCHEMA
        and information_witness.get("information_preservation_closed") is True
        and information_witness.get("priority_default_eligible") is True
        and information_witness.get(
            "information_preservation_is_primary_gate"
        )
        is True
    )
    performance_ok = (
        performance_witness is not None
        and performance_witness.get("schema") == PERFORMANCE_SCHEMA
        and performance_witness.get("supports_priority_default") is True
    )
    selected = information_ok and performance_ok
    return {
        "schema": "HHS_PASS220_PRIORITY_OFFSET_PROMOTION_DECISION_V1",
        "status": (
            "PROMOTE_PRIORITY_DEFAULT"
            if selected
            else (
                "INFORMATION_PRESERVED_PERFORMANCE_PENDING"
                if information_ok
                else "FALL_BACK_TO_DENSE_REFERENCE"
            )
        ),
        "selected_representation": (
            PRIORITY_DEFAULT if selected else REFERENCE_FALLBACK
        ),
        "information_preservation_pass": information_ok,
        "performance_support_pass": performance_ok,
        "information_preservation_is_primary_gate": True,
        "speed_alone_can_promote": False,
        "fallback_on_information_loss": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }


__all__ = [
    "PERFORMANCE_SCHEMA",
    "PRIORITY_DEFAULT",
    "REFERENCE_FALLBACK",
    "SCHEMA",
    "HNAN_ZERO_EMPTYSET_CENTER_SOURCE",
    "HHSInformationTranslationError",
    "build_cross_layer_information_witness",
    "channel_information_translation_witness",
    "hnan_information_gate_witness",
    "performance_support_witness",
    "priority_default_decision",
]
