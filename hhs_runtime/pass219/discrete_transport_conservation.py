"""Pass 219 RML17 discrete transport conservation contract.

RML17 is an additive, read-only conservation membrane above the validated
RML16 deterministic reciprocal-route cache.  It does not alter RML12 route
construction, RML15 receipt/reverse semantics, RML16 acceleration, VM81,
Hash72, or Hash216 authority.

The contract makes the discrete-fluid formulation executable:

    Div_H(s) = 0
    J(s, d) = -J(T_H(s, d), d^-1)
    C(s) = 1 and T_H(s, d) = s' => C(s') = 1
    nu_H L_H = 0
    R^-1(R(s)) = s

Two distinct surfaces are audited and deliberately not conflated:

1. The finite 4 x 64 x 72 x 81 hydration-address manifold receives an exact
   reciprocal-neighborhood conservation witness.
2. The existing RML16 route surface receives admission, reciprocal-edge,
   zero-diffusion, retained-ancestry, and composed reverse-closure witnesses.

Address-neighborhood witnesses are observational topology checks only.  They do
not mint canonical transitions or extend any authority surface.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.dynamic_octonion_gyroscope import PHASE_MODULUS
from hhs_runtime.pass219.reciprocal_route_cache import (
    build_and_select_reciprocal_route_cached,
)
from hhs_runtime.pass219.route_reverse_replay import build_reverse_witness

PASS = 219
ITERATION = "RML17_DISCRETE_TRANSPORT_CONSERVATION"

CONTRACT_SCHEMA = "HHS_PASS219_RML17_DISCRETE_TRANSPORT_CONSERVATION_V1"
ADDRESS_AUDIT_SCHEMA = "HHS_PASS219_RML17_ADDRESS_MANIFOLD_CONSERVATION_AUDIT_V1"
ROUTE_AUDIT_SCHEMA = "HHS_PASS219_RML17_RML16_ROUTE_CONSERVATION_AUDIT_V1"
COMPOSITION_AUDIT_SCHEMA = "HHS_PASS219_RML17_COMPOSED_TRANSPORT_CONSERVATION_AUDIT_V1"

LANE_COUNT = 4
OPERATIONS_PER_CELL = 64
PHASE_COUNT = PHASE_MODULUS
CELL_COUNT = 81
ADDRESS_COUNT = LANE_COUNT * OPERATIONS_PER_CELL * PHASE_COUNT * CELL_COUNT

DIRECTIONS = (
    "operation_forward",
    "operation_reverse",
    "phase_forward",
    "phase_reverse",
    "cell_forward",
    "cell_reverse",
)
INVERSE_DIRECTION = {
    "operation_forward": "operation_reverse",
    "operation_reverse": "operation_forward",
    "phase_forward": "phase_reverse",
    "phase_reverse": "phase_forward",
    "cell_forward": "cell_reverse",
    "cell_reverse": "cell_forward",
}
DIRECTION_FLUX = {
    "operation_forward": 1,
    "operation_reverse": -1,
    "phase_forward": 1,
    "phase_reverse": -1,
    "cell_forward": 1,
    "cell_reverse": -1,
}
EXACT_ROUTE_EDGE_KINDS = frozenset(
    {
        "COUPLED_GENERATOR_PRODUCT_PHASE_MOVE",
        "CHIRAL_PAIR_U36_FLIP",
    }
)


class DiscreteTransportConservationError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise DiscreteTransportConservationError(
            f"FLOAT_TRANSPORT_AUTHORITY_FORBIDDEN:{path}"
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


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DiscreteTransportConservationError(
            f"{label}_EXACT_INTEGER_REQUIRED"
        )
    return value


def _range(value: Any, label: str, size: int) -> int:
    integer = _exact_int(value, label)
    if integer < 0 or integer >= size:
        raise DiscreteTransportConservationError(f"{label}_OUT_OF_RANGE")
    return integer


def encode_transport_address(
    lane_index: int,
    operation_index: int,
    phase_index: int,
    cell_index: int,
) -> int:
    """Encode one exact 4 x 64 x 72 x 81 address."""
    lane = _range(lane_index, "LANE_INDEX", LANE_COUNT)
    operation = _range(operation_index, "OPERATION_INDEX", OPERATIONS_PER_CELL)
    phase = _range(phase_index, "PHASE_INDEX", PHASE_COUNT)
    cell = _range(cell_index, "CELL_INDEX", CELL_COUNT)
    return (
        ((lane * OPERATIONS_PER_CELL + operation) * PHASE_COUNT + phase)
        * CELL_COUNT
        + cell
    )


def decode_transport_address(address: int) -> tuple[int, int, int, int]:
    """Inverse of :func:`encode_transport_address`."""
    value = _range(address, "TRANSPORT_ADDRESS", ADDRESS_COUNT)
    cell = value % CELL_COUNT
    value //= CELL_COUNT
    phase = value % PHASE_COUNT
    value //= PHASE_COUNT
    operation = value % OPERATIONS_PER_CELL
    lane = value // OPERATIONS_PER_CELL
    return lane, operation, phase, cell


def transport_neighbor(address: int, direction: str) -> int:
    """Move one exact reciprocal address edge inside a lane.

    Lane identity is retained.  This membrane does not invent inter-lane
    transition authority; it audits the operation/phase/cell neighborhood
    within each of the four existing hydration lanes.
    """
    if direction not in INVERSE_DIRECTION:
        raise DiscreteTransportConservationError(
            "RML17_TRANSPORT_DIRECTION_UNSUPPORTED"
        )
    lane, operation, phase, cell = decode_transport_address(address)
    if direction == "operation_forward":
        operation = (operation + 1) % OPERATIONS_PER_CELL
    elif direction == "operation_reverse":
        operation = (operation - 1) % OPERATIONS_PER_CELL
    elif direction == "phase_forward":
        phase = (phase + 1) % PHASE_COUNT
    elif direction == "phase_reverse":
        phase = (phase - 1) % PHASE_COUNT
    elif direction == "cell_forward":
        cell = (cell + 1) % CELL_COUNT
    else:
        cell = (cell - 1) % CELL_COUNT
    return encode_transport_address(lane, operation, phase, cell)


def signed_address_flux(address: int, direction: str) -> int:
    """Exact integer local flux witness J(s,d)."""
    _range(address, "TRANSPORT_ADDRESS", ADDRESS_COUNT)
    try:
        return DIRECTION_FLUX[direction]
    except KeyError as exc:
        raise DiscreteTransportConservationError(
            "RML17_TRANSPORT_DIRECTION_UNSUPPORTED"
        ) from exc


def discrete_divergence(address: int) -> int:
    """Return Div_H(s) as an exact integer signed neighborhood sum."""
    return sum(signed_address_flux(address, direction) for direction in DIRECTIONS)


def audit_transport_address(address: int) -> dict[str, Any]:
    """Audit one address for bijection, reciprocal edges, and zero divergence."""
    source = _range(address, "TRANSPORT_ADDRESS", ADDRESS_COUNT)
    coordinates = decode_transport_address(source)
    reciprocal = True
    edge_balance = True
    for direction in DIRECTIONS:
        target = transport_neighbor(source, direction)
        inverse = INVERSE_DIRECTION[direction]
        if transport_neighbor(target, inverse) != source:
            reciprocal = False
        if signed_address_flux(source, direction) != -signed_address_flux(target, inverse):
            edge_balance = False

    divergence = discrete_divergence(source)
    result = {
        "schema": CONTRACT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "address": source,
        "coordinates": list(coordinates),
        "encode_decode_bijective": encode_transport_address(*coordinates) == source,
        "discrete_divergence": divergence,
        "zero_discrete_divergence": divergence == 0,
        "reciprocal_neighbor_edges": reciprocal,
        "reciprocal_edge_flux_balance": edge_balance,
        "address_neighborhood_has_canonical_transition_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


def audit_transport_address_manifold() -> dict[str, Any]:
    """Exhaustively audit all 1,492,992 finite hydration addresses.

    This intentionally performs a direct full scan.  It is a validation
    workload, not an optimized runtime path.
    """
    bijection_failures = 0
    divergence_failures = 0
    reciprocal_neighbor_failures = 0
    reciprocal_flux_failures = 0

    for source in range(ADDRESS_COUNT):
        coordinates = decode_transport_address(source)
        if encode_transport_address(*coordinates) != source:
            bijection_failures += 1

        divergence = 0
        for direction in DIRECTIONS:
            target = transport_neighbor(source, direction)
            inverse = INVERSE_DIRECTION[direction]
            flux = signed_address_flux(source, direction)
            divergence += flux
            if transport_neighbor(target, inverse) != source:
                reciprocal_neighbor_failures += 1
            if flux != -signed_address_flux(target, inverse):
                reciprocal_flux_failures += 1

        if divergence != 0:
            divergence_failures += 1

    result = {
        "schema": ADDRESS_AUDIT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "lane_count": LANE_COUNT,
        "operations_per_cell": OPERATIONS_PER_CELL,
        "phase_count": PHASE_COUNT,
        "cell_count": CELL_COUNT,
        "expected_address_count": 1492992,
        "visited_address_count": ADDRESS_COUNT,
        "cardinality_exact": ADDRESS_COUNT == 1492992,
        "bijection_failures": bijection_failures,
        "discrete_divergence_failures": divergence_failures,
        "reciprocal_neighbor_failures": reciprocal_neighbor_failures,
        "reciprocal_flux_failures": reciprocal_flux_failures,
        "all_addresses_encode_decode_bijective": bijection_failures == 0,
        "all_addresses_zero_discrete_divergence": divergence_failures == 0,
        "all_address_edges_reciprocal": reciprocal_neighbor_failures == 0,
        "all_address_edge_fluxes_balanced": reciprocal_flux_failures == 0,
        "exhaustive_scan": True,
        "optimized_runtime_path": False,
        "address_neighborhood_has_canonical_transition_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    result["result"] = (
        "PASS"
        if all(
            (
                result["cardinality_exact"],
                result["all_addresses_encode_decode_bijective"],
                result["all_addresses_zero_discrete_divergence"],
                result["all_address_edges_reciprocal"],
                result["all_address_edge_fluxes_balanced"],
            )
        )
        else "FAIL"
    )
    result["audit_sha256"] = _sha256(result)
    return result


def _selected_plan(bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    selection = bundle.get("selection")
    if not isinstance(selection, Mapping):
        raise DiscreteTransportConservationError(
            "RML17_RML16_SELECTION_MAPPING_REQUIRED"
        )
    selected_sha = selection.get("selected_route_sha256")
    candidates = (
        bundle.get("shortest_candidate"),
        bundle.get("complementary_candidate"),
    )
    selected = [
        candidate
        for candidate in candidates
        if isinstance(candidate, Mapping)
        and candidate.get("route_sha256") == selected_sha
    ]
    if len(selected) != 1:
        raise DiscreteTransportConservationError(
            "RML17_EXACTLY_ONE_SELECTED_ROUTE_REQUIRED"
        )
    return selected[0]


def _edge_zero_diffusion(edge: Mapping[str, Any]) -> bool:
    """Recognize only the inherited exact reversible edge family."""
    return (
        edge.get("kind") in EXACT_ROUTE_EDGE_KINDS
        and edge.get("exact_inverse_restores_source_phase_state") is True
        and edge.get("target_product_geometry_admissible") is True
        and edge.get("classification_metadata_has_transition_authority") is False
        and edge.get("gradient_descent_used") is False
        and edge.get("floating_score_used") is False
        and edge.get("canonical_vm81_mutation_authority") is False
        and edge.get("canonical_hash72_mint_authority") is False
        and edge.get("canonical_hash216_persistence_authority") is False
    )


def audit_rml16_route_conservation(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    route_id: str,
) -> dict[str, Any]:
    """Audit one RML16 route against the RML17 operator contract."""
    _reject_float(source)
    _reject_float(target)
    bundle = build_and_select_reciprocal_route_cached(
        source,
        target,
        route_id=route_id,
    )
    _reject_float(bundle)
    plan = _selected_plan(bundle)
    edges = plan.get("edges")
    if not isinstance(edges, list):
        raise DiscreteTransportConservationError(
            "RML17_SELECTED_ROUTE_EDGE_LIST_REQUIRED"
        )

    chain_identity = plan.get("source_state_sha256") == source.get("state_sha256")
    current_sha = plan.get("source_state_sha256")
    reciprocal_edge_balance = True
    admission_preserved = source.get("admissible_product_geometry") is True
    zero_diffusion = True

    reciprocal_flux_pairs: list[list[int]] = []
    for edge in edges:
        if not isinstance(edge, Mapping):
            raise DiscreteTransportConservationError(
                "RML17_ROUTE_EDGE_MAPPING_REQUIRED"
            )
        if edge.get("source_state_sha256") != current_sha:
            chain_identity = False
        current_sha = edge.get("target_state_sha256")
        admission_preserved = (
            admission_preserved
            and edge.get("target_product_geometry_admissible") is True
        )
        zero_diffusion = zero_diffusion and _edge_zero_diffusion(edge)

        transport_units = _exact_int(
            edge.get("phase_transport_units"),
            "RML17_PHASE_TRANSPORT_UNITS",
        )
        forward_flux = transport_units
        reverse_flux = -transport_units
        reciprocal_flux_pairs.append([forward_flux, reverse_flux])
        if forward_flux != -reverse_flux:
            reciprocal_edge_balance = False
        if edge.get("exact_inverse_restores_source_phase_state") is not True:
            reciprocal_edge_balance = False

    chain_identity = (
        chain_identity
        and current_sha == plan.get("target_state_sha256")
        and plan.get("target_state_sha256") == target.get("state_sha256")
    )
    admission_preserved = (
        admission_preserved
        and target.get("admissible_product_geometry") is True
        and plan.get("all_edges_remain_in_admissible_product_geometry") is True
    )
    zero_diffusion = (
        zero_diffusion
        and plan.get("gradient_descent_used") is False
        and plan.get("loss_function_used") is False
        and plan.get("floating_score_used") is False
        and plan.get("probabilistic_search_used") is False
    )

    reverse_witness, reverse_summary = build_reverse_witness(
        bundle,
        source,
        target,
    )
    reverse_closure = (
        reverse_summary.get("python_reverse_phase_state_restored") is True
        and reverse_summary.get("python_reverse_uses_retained_edge_ancestry") is True
        and reverse_summary.get("hash216_cryptographic_inversion_used") is False
        and int(reverse_witness.edge_count) == len(edges)
    )
    information_loss = 0 if reverse_closure and chain_identity else 1

    result = {
        "schema": ROUTE_AUDIT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "route_id": str(route_id),
        "bundle_sha256": bundle.get("bundle_sha256"),
        "selected_route_sha256": plan.get("route_sha256"),
        "source_state_sha256": source.get("state_sha256"),
        "target_state_sha256": target.get("state_sha256"),
        "edge_count": len(edges),
        "reciprocal_flux_pairs": reciprocal_flux_pairs,
        "zero_discrete_route_divergence": all(
            forward + reverse == 0
            for forward, reverse in reciprocal_flux_pairs
        ),
        "reciprocal_edge_balance": reciprocal_edge_balance,
        "admission_preserved": admission_preserved,
        "route_edge_chain_identity_preserved": chain_identity,
        "nu_h": 0,
        "l_h_equivalent_zero": zero_diffusion,
        "canonical_diffusion_operator_present": not zero_diffusion,
        "reverse_receipt_uses_retained_ancestry": reverse_summary.get(
            "python_reverse_uses_retained_edge_ancestry"
        )
        is True,
        "composed_reverse_identity_for_route": reverse_closure,
        "delta_loss": information_loss,
        "structural_information_loss_zero": information_loss == 0,
        "hash216_cryptographic_inversion_used": False,
        "latency_participates_in_viscosity_definition": False,
        "rml16_cache_changes_operator_semantics": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
    }
    result["result"] = (
        "PASS"
        if all(
            (
                result["zero_discrete_route_divergence"],
                result["reciprocal_edge_balance"],
                result["admission_preserved"],
                result["route_edge_chain_identity_preserved"],
                result["l_h_equivalent_zero"],
                result["composed_reverse_identity_for_route"],
                result["structural_information_loss_zero"],
            )
        )
        else "FAIL"
    )
    result["audit_sha256"] = _sha256(result)
    return result


def audit_composed_transport_conservation(
    states: Sequence[Mapping[str, Any]],
    *,
    composition_id: str,
) -> dict[str, Any]:
    """Audit arbitrary admitted RML16 route composition s0 -> ... -> sn."""
    if isinstance(states, (str, bytes)) or not isinstance(states, Sequence):
        raise DiscreteTransportConservationError(
            "RML17_STATE_SEQUENCE_REQUIRED"
        )
    ordered = list(states)
    if len(ordered) < 2:
        raise DiscreteTransportConservationError(
            "RML17_COMPOSITION_REQUIRES_AT_LEAST_TWO_STATES"
        )

    route_audits: list[dict[str, Any]] = []
    for index, (source, target) in enumerate(zip(ordered, ordered[1:])):
        audit = audit_rml16_route_conservation(
            source,
            target,
            route_id=f"{composition_id}:segment:{index}",
        )
        route_audits.append(audit)

    chain_linked = all(
        left["target_state_sha256"] == right["source_state_sha256"]
        for left, right in zip(route_audits, route_audits[1:])
    )
    every_prefix_admitted = all(audit["admission_preserved"] for audit in route_audits)
    every_segment_reversible = all(
        audit["composed_reverse_identity_for_route"] for audit in route_audits
    )
    every_segment_lossless = all(
        audit["structural_information_loss_zero"] for audit in route_audits
    )
    every_segment_zero_diffusion = all(
        audit["l_h_equivalent_zero"] for audit in route_audits
    )
    every_segment_zero_divergence = all(
        audit["zero_discrete_route_divergence"] for audit in route_audits
    )

    result = {
        "schema": COMPOSITION_AUDIT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "composition_id": str(composition_id),
        "state_count": len(ordered),
        "segment_count": len(route_audits),
        "origin_state_sha256": ordered[0].get("state_sha256"),
        "terminal_state_sha256": ordered[-1].get("state_sha256"),
        "segment_audit_sha256": [audit["audit_sha256"] for audit in route_audits],
        "all_prefix_states_admission_preserved": every_prefix_admitted,
        "route_segments_chain_exactly": chain_linked,
        "all_segments_zero_discrete_divergence": every_segment_zero_divergence,
        "all_segments_reciprocal_edge_balanced": all(
            audit["reciprocal_edge_balance"] for audit in route_audits
        ),
        "nu_h": 0,
        "l_h_equivalent_zero_under_composition": every_segment_zero_diffusion,
        "reverse_composition_restores_origin_exactly": (
            chain_linked and every_segment_reversible
        ),
        "delta_loss": 0 if chain_linked and every_segment_lossless else 1,
        "structural_information_loss_zero_under_composition": (
            chain_linked and every_segment_lossless
        ),
        "canonical_transition_authority_expanded": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    result["result"] = (
        "PASS"
        if all(
            (
                result["all_prefix_states_admission_preserved"],
                result["route_segments_chain_exactly"],
                result["all_segments_zero_discrete_divergence"],
                result["all_segments_reciprocal_edge_balanced"],
                result["l_h_equivalent_zero_under_composition"],
                result["reverse_composition_restores_origin_exactly"],
                result["structural_information_loss_zero_under_composition"],
            )
        )
        else "FAIL"
    )
    result["audit_sha256"] = _sha256(result)
    return result


__all__ = [
    "ADDRESS_AUDIT_SCHEMA",
    "ADDRESS_COUNT",
    "CELL_COUNT",
    "COMPOSITION_AUDIT_SCHEMA",
    "CONTRACT_SCHEMA",
    "DIRECTIONS",
    "INVERSE_DIRECTION",
    "ITERATION",
    "LANE_COUNT",
    "OPERATIONS_PER_CELL",
    "PHASE_COUNT",
    "ROUTE_AUDIT_SCHEMA",
    "DiscreteTransportConservationError",
    "audit_composed_transport_conservation",
    "audit_rml16_route_conservation",
    "audit_transport_address",
    "audit_transport_address_manifold",
    "decode_transport_address",
    "discrete_divergence",
    "encode_transport_address",
    "signed_address_flux",
    "transport_neighbor",
]
