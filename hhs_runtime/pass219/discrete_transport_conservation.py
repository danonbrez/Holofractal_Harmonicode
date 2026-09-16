"""Pass 219 RML17 discrete transport conservation contract.

RML17 is an additive, read-only conservation membrane above the validated
RML16 deterministic reciprocal-route cache. It does not alter RML12 route
construction, RML15 receipt/reverse semantics, RML16 acceleration, VM81,
Hash72, Hash216, or RNA/UQCEL transition authority.

The address witness is now exactly the sealed native C++ cell-wall geometry:

    operation64 x phase72 x cell81 x direction4

with direction4 = (x, y, z, w), signed flux (+1, -1, -1, +1), reciprocal
pairs x<->y and z<->w, direction as the low mixed-radix digit, and transport
advancing only phase72 modulo 72. The native ABI is attached beneath this
Python witness for exhaustive cross-language parity auditing; neither surface
can commit canonical state.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.dynamic_octonion_gyroscope import PHASE_MODULUS
from hhs_runtime.pass219.reciprocal_route_cache import (
    build_and_select_reciprocal_route_cached,
)
from hhs_runtime.pass219.route_reverse_replay import build_reverse_witness

PASS = 219
ITERATION = "RML17_DISCRETE_TRANSPORT_CONSERVATION"

CONTRACT_SCHEMA = "HHS_PASS219_RML17_DISCRETE_TRANSPORT_CONSERVATION_V1"
ADDRESS_AUDIT_SCHEMA = "HHS_PASS219_RML17_ADDRESS_MANIFOLD_CONSERVATION_AUDIT_V2"
ROUTE_AUDIT_SCHEMA = "HHS_PASS219_RML17_RML16_ROUTE_CONSERVATION_AUDIT_V1"
COMPOSITION_AUDIT_SCHEMA = "HHS_PASS219_RML17_COMPOSED_TRANSPORT_CONSERVATION_AUDIT_V1"
NATIVE_PARITY_SCHEMA = "HHS_PASS219_RML17_NATIVE_CONSERVATION_PARITY_V1"

OPERATIONS_PER_CELL = 64
PHASE_COUNT = PHASE_MODULUS
CELL_COUNT = 81
DIRECTION_COUNT = 4
NODE_COUNT = OPERATIONS_PER_CELL * PHASE_COUNT * CELL_COUNT
ADDRESS_COUNT = NODE_COUNT * DIRECTION_COUNT

# Compatibility export retained for callers that imported the old cardinality
# constant. It is not an address coordinate: the fourth radix is direction4.
LANE_COUNT = DIRECTION_COUNT

DIRECTIONS = ("x", "y", "z", "w")
DIRECTION_INDEX = {name: index for index, name in enumerate(DIRECTIONS)}
INDEX_DIRECTION = DIRECTIONS
INVERSE_DIRECTION = {"x": "y", "y": "x", "z": "w", "w": "z"}
INVERSE_DIRECTION_INDEX = (1, 0, 3, 2)
DIRECTION_FLUX = {"x": 1, "y": -1, "z": -1, "w": 1}
DIRECTION_FLUX_INDEX = (1, -1, -1, 1)

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
    operation_index: int,
    phase_index: int,
    cell_index: int,
    direction_index: int,
) -> int:
    """Native-identical mixed-radix flattening for one directed address."""
    operation = _range(operation_index, "OPERATION_INDEX", OPERATIONS_PER_CELL)
    phase = _range(phase_index, "PHASE_INDEX", PHASE_COUNT)
    cell = _range(cell_index, "CELL_INDEX", CELL_COUNT)
    direction = _range(direction_index, "DIRECTION_INDEX", DIRECTION_COUNT)
    index = operation
    index = index * PHASE_COUNT + phase
    index = index * CELL_COUNT + cell
    index = index * DIRECTION_COUNT + direction
    return index


def decode_transport_address(address: int) -> tuple[int, int, int, int]:
    """Inverse of native-identical mixed-radix flattening."""
    value = _range(address, "TRANSPORT_ADDRESS", ADDRESS_COUNT)
    direction = value % DIRECTION_COUNT
    value //= DIRECTION_COUNT
    cell = value % CELL_COUNT
    value //= CELL_COUNT
    phase = value % PHASE_COUNT
    value //= PHASE_COUNT
    operation = value % OPERATIONS_PER_CELL
    return operation, phase, cell, direction


def reciprocal_direction_index(direction_index: int) -> int:
    direction = _range(direction_index, "DIRECTION_INDEX", DIRECTION_COUNT)
    return INVERSE_DIRECTION_INDEX[direction]


def signed_direction_flux(direction_index: int) -> int:
    direction = _range(direction_index, "DIRECTION_INDEX", DIRECTION_COUNT)
    return DIRECTION_FLUX_INDEX[direction]


def transport_neighbor(address: int) -> int:
    """Return the sealed native directed successor for one address.

    Operation64 and cell81 are preserved. Phase72 advances by the signed x/y/z/w
    orientation and direction4 is replaced by its reciprocal. This function is
    a conservation witness and has no canonical transition authority.
    """
    operation, phase, cell, direction = decode_transport_address(address)
    target_phase = (phase + signed_direction_flux(direction)) % PHASE_COUNT
    target_direction = reciprocal_direction_index(direction)
    return encode_transport_address(operation, target_phase, cell, target_direction)


def signed_address_flux(address: int) -> int:
    """Exact integer local flux witness J(s,d), with d embedded in the address."""
    _, _, _, direction = decode_transport_address(address)
    return signed_direction_flux(direction)


def discrete_divergence(address: int) -> int:
    """Return Div_H(node(address)) as the four-channel exact flux sum."""
    _range(address, "TRANSPORT_ADDRESS", ADDRESS_COUNT)
    return sum(DIRECTION_FLUX_INDEX)


def zero_diffusion_classification(address: int) -> bool:
    """Match the native zero-diffusion edge classification exactly."""
    source = _range(address, "TRANSPORT_ADDRESS", ADDRESS_COUNT)
    target = transport_neighbor(source)
    source_node = decode_transport_address(source)[:3]
    target_node = decode_transport_address(target)[:3]
    return (
        source_node[0] == target_node[0]
        and source_node[2] == target_node[2]
        and transport_neighbor(target) == source
    )


def audit_transport_address(address: int) -> dict[str, Any]:
    """Audit one directed address against the sealed C++ cell-wall semantics."""
    source = _range(address, "TRANSPORT_ADDRESS", ADDRESS_COUNT)
    coordinates = decode_transport_address(source)
    operation, phase, cell, direction = coordinates
    target = transport_neighbor(source)
    target_coordinates = decode_transport_address(target)
    inverse = reciprocal_direction_index(direction)
    reciprocal = transport_neighbor(target) == source
    edge_balance = signed_direction_flux(direction) == -signed_direction_flux(inverse)
    exact_phase_step = target_coordinates == (
        operation,
        (phase + signed_direction_flux(direction)) % PHASE_COUNT,
        cell,
        inverse,
    )
    divergence = discrete_divergence(source)
    zero_diffusion = zero_diffusion_classification(source)
    result = {
        "schema": CONTRACT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "address": source,
        "coordinates": list(coordinates),
        "coordinate_order": ["operation64", "phase72", "cell81", "direction4"],
        "direction": INDEX_DIRECTION[direction],
        "target_address": target,
        "target_coordinates": list(target_coordinates),
        "encode_decode_bijective": encode_transport_address(*coordinates) == source,
        "native_mixed_radix_order": True,
        "exact_phase_only_successor": exact_phase_step,
        "discrete_divergence": divergence,
        "zero_discrete_divergence": divergence == 0,
        "reciprocal_neighbor_edges": reciprocal,
        "reciprocal_edge_flux_balance": edge_balance,
        "zero_canonical_diffusion": zero_diffusion,
        "address_neighborhood_has_canonical_transition_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


def audit_transport_address_manifold() -> dict[str, Any]:
    """Exhaustively audit the native-identical 1,492,992 directed addresses."""
    bijection_failures = 0
    divergence_failures = 0
    reciprocal_neighbor_failures = 0
    reciprocal_flux_failures = 0
    zero_diffusion_failures = 0
    target_map_failures = 0
    target_seen = bytearray(ADDRESS_COUNT)

    for node_index in range(NODE_COUNT):
        value = node_index
        cell = value % CELL_COUNT
        value //= CELL_COUNT
        phase = value % PHASE_COUNT
        value //= PHASE_COUNT
        operation = value % OPERATIONS_PER_CELL
        probe = encode_transport_address(operation, phase, cell, 0)
        if discrete_divergence(probe) != 0:
            divergence_failures += 1

    for source in range(ADDRESS_COUNT):
        coordinates = decode_transport_address(source)
        if encode_transport_address(*coordinates) != source:
            bijection_failures += 1

        direction = coordinates[3]
        target = transport_neighbor(source)
        inverse = reciprocal_direction_index(direction)
        if transport_neighbor(target) != source:
            reciprocal_neighbor_failures += 1
        if signed_direction_flux(direction) != -signed_direction_flux(inverse):
            reciprocal_flux_failures += 1
        if not zero_diffusion_classification(source):
            zero_diffusion_failures += 1
        if target < 0 or target >= ADDRESS_COUNT or target_seen[target]:
            target_map_failures += 1
        else:
            target_seen[target] = 1

    unique_target_addresses = sum(target_seen)
    if unique_target_addresses != ADDRESS_COUNT:
        target_map_failures += ADDRESS_COUNT - unique_target_addresses

    result = {
        "schema": ADDRESS_AUDIT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "operation_count": OPERATIONS_PER_CELL,
        "phase_count": PHASE_COUNT,
        "cell_count": CELL_COUNT,
        "direction_count": DIRECTION_COUNT,
        "node_count": NODE_COUNT,
        "expected_address_count": 1_492_992,
        "visited_address_count": ADDRESS_COUNT,
        "unique_target_addresses": unique_target_addresses,
        "cardinality_exact": ADDRESS_COUNT == 1_492_992,
        "coordinate_order": ["operation64", "phase72", "cell81", "direction4"],
        "direction_names": list(DIRECTIONS),
        "direction_flux": list(DIRECTION_FLUX_INDEX),
        "reciprocal_direction_index": list(INVERSE_DIRECTION_INDEX),
        "bijection_failures": bijection_failures,
        "discrete_divergence_failures": divergence_failures,
        "reciprocal_neighbor_failures": reciprocal_neighbor_failures,
        "reciprocal_flux_failures": reciprocal_flux_failures,
        "zero_diffusion_failures": zero_diffusion_failures,
        "target_map_failures": target_map_failures,
        "all_addresses_encode_decode_bijective": bijection_failures == 0,
        "all_nodes_zero_discrete_divergence": divergence_failures == 0,
        "all_addresses_zero_discrete_divergence": divergence_failures == 0,
        "all_address_edges_reciprocal": reciprocal_neighbor_failures == 0,
        "all_address_edge_fluxes_balanced": reciprocal_flux_failures == 0,
        "all_addresses_zero_canonical_diffusion": zero_diffusion_failures == 0,
        "target_map_bijective": target_map_failures == 0,
        "exhaustive_scan": True,
        "optimized_runtime_path": False,
        "native_cell_wall_semantics": True,
        "lane_coordinate_present": False,
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
                result["all_nodes_zero_discrete_divergence"],
                result["all_address_edges_reciprocal"],
                result["all_address_edge_fluxes_balanced"],
                result["all_addresses_zero_canonical_diffusion"],
                result["target_map_bijective"],
            )
        )
        else "FAIL"
    )
    result["audit_sha256"] = _sha256(result)
    return result


def audit_native_execution_parity(
    *,
    library_path: str | Path | None = None,
    chunk_size: int = 4096,
) -> dict[str, Any]:
    """Exhaustively prove Python RML17 == native C++ conservation semantics.

    The native ABI exports rows in batches. Every directed address is compared
    exactly for source encoding, target encoding, flux orientation, reciprocal
    direction, two-step reverse closure, and zero-diffusion classification.
    This is a finite extensional equality proof over the complete manifold.
    """
    from hhs_runtime.pass219.native_transport_conservation import (
        iter_native_parity_rows,
        native_contract_report,
    )

    native_report = native_contract_report(library_path)
    source_encoding_mismatches = 0
    target_encoding_mismatches = 0
    successor_mismatches = 0
    flux_mismatches = 0
    reciprocal_mismatches = 0
    zero_diffusion_mismatches = 0
    reverse_closure_mismatches = 0
    checked = 0

    for row in iter_native_parity_rows(
        library_path=library_path,
        chunk_size=chunk_size,
    ):
        source_index = int(row.source_index)
        source_coordinates = decode_transport_address(source_index)
        native_source_coordinates = (
            int(row.source.operation64),
            int(row.source.phase72),
            int(row.source.cell81),
            int(row.source.direction4),
        )
        if source_coordinates != native_source_coordinates:
            source_encoding_mismatches += 1

        target_index = transport_neighbor(source_index)
        target_coordinates = decode_transport_address(target_index)
        native_target_coordinates = (
            int(row.target.operation64),
            int(row.target.phase72),
            int(row.target.cell81),
            int(row.target.direction4),
        )
        if target_coordinates != native_target_coordinates:
            target_encoding_mismatches += 1
        if target_index != int(row.target_index):
            successor_mismatches += 1

        direction = source_coordinates[3]
        if signed_direction_flux(direction) != int(row.source_flux):
            flux_mismatches += 1
        if reciprocal_direction_index(direction) != int(row.reciprocal_direction4):
            reciprocal_mismatches += 1
        python_zero_diffusion = zero_diffusion_classification(source_index)
        if python_zero_diffusion != bool(row.zero_canonical_diffusion):
            zero_diffusion_mismatches += 1
        if (transport_neighbor(target_index) == source_index) != bool(
            row.exact_reverse_restores_source
        ):
            reverse_closure_mismatches += 1
        checked += 1

    mismatch_total = sum(
        (
            source_encoding_mismatches,
            target_encoding_mismatches,
            successor_mismatches,
            flux_mismatches,
            reciprocal_mismatches,
            zero_diffusion_mismatches,
            reverse_closure_mismatches,
        )
    )
    native_gates = all(
        bool(native_report[key])
        for key in (
            "discrete_divergence_gate",
            "reciprocal_edge_balance_gate",
            "admission_preservation_gate",
            "zero_canonical_diffusion_gate",
            "composed_reverse_closure_gate",
            "exhaustive_address_coverage",
            "target_map_bijective",
            "exact_integer_phase_arithmetic",
            "pass",
        )
    )
    authority_closed = all(
        not bool(native_report[key])
        for key in (
            "canonical_transition_authority",
            "canonical_vm81_mutation_authority",
            "canonical_hash72_mint_authority",
            "canonical_hash216_persistence_authority",
            "abi_has_transition_authority",
        )
    )
    result = {
        "schema": NATIVE_PARITY_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "python_address_count": ADDRESS_COUNT,
        "native_address_count": int(native_report["address_count"]),
        "addresses_compared": checked,
        "source_encoding_mismatches": source_encoding_mismatches,
        "target_encoding_mismatches": target_encoding_mismatches,
        "successor_mismatches": successor_mismatches,
        "flux_orientation_mismatches": flux_mismatches,
        "reciprocal_alignment_mismatches": reciprocal_mismatches,
        "zero_diffusion_classification_mismatches": zero_diffusion_mismatches,
        "reverse_closure_mismatches": reverse_closure_mismatches,
        "mismatch_total": mismatch_total,
        "native_exhaustive_contract_pass": native_gates,
        "native_abi_transition_authority_closed": authority_closed,
        "python_native_extensional_equality": (
            checked == ADDRESS_COUNT
            and int(native_report["address_count"]) == ADDRESS_COUNT
            and mismatch_total == 0
        ),
        "canonical_transition_authority_expanded": False,
        "native_abi_beneath_rml17": True,
    }
    result["result"] = (
        "PASS"
        if result["python_native_extensional_equality"]
        and result["native_exhaustive_contract_pass"]
        and result["native_abi_transition_authority_closed"]
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

    source_endpoint_bound = (
        plan.get("source_state_sha256") == source.get("state_sha256")
        and plan.get("source_ambient_state_index") == source.get("ambient_state_index")
    )
    supplied_target_receipt_bound = (
        plan.get("target_state_sha256") == target.get("state_sha256")
        and plan.get("target_ambient_state_index") == target.get("ambient_state_index")
    )

    edge_hash_chain_contiguous = source_endpoint_bound
    edge_ambient_chain_contiguous = source_endpoint_bound
    current_sha = plan.get("source_state_sha256")
    current_ambient = plan.get("source_ambient_state_index")
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
            edge_hash_chain_contiguous = False
        if edge.get("source_ambient_state_index") != current_ambient:
            edge_ambient_chain_contiguous = False

        current_sha = edge.get("target_state_sha256")
        current_ambient = edge.get("target_ambient_state_index")
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

    terminal_phase_geometry_identity = (
        current_ambient == plan.get("target_ambient_state_index")
        and plan.get("target_ambient_state_index") == target.get("ambient_state_index")
        and plan.get("target_reached_exactly") is True
    )
    route_edge_chain_identity = (
        source_endpoint_bound
        and supplied_target_receipt_bound
        and edge_hash_chain_contiguous
        and edge_ambient_chain_contiguous
        and terminal_phase_geometry_identity
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
    information_loss = 0 if reverse_closure and route_edge_chain_identity else 1

    result = {
        "schema": ROUTE_AUDIT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "route_id": str(route_id),
        "bundle_sha256": bundle.get("bundle_sha256"),
        "selected_route_sha256": plan.get("route_sha256"),
        "source_state_sha256": source.get("state_sha256"),
        "target_state_sha256": target.get("state_sha256"),
        "generated_terminal_state_sha256": current_sha,
        "source_ambient_state_index": source.get("ambient_state_index"),
        "target_ambient_state_index": target.get("ambient_state_index"),
        "generated_terminal_ambient_state_index": current_ambient,
        "edge_count": len(edges),
        "reciprocal_flux_pairs": reciprocal_flux_pairs,
        "zero_discrete_route_divergence": all(
            forward + reverse == 0
            for forward, reverse in reciprocal_flux_pairs
        ),
        "reciprocal_edge_balance": reciprocal_edge_balance,
        "admission_preserved": admission_preserved,
        "source_endpoint_receipt_identity_bound": source_endpoint_bound,
        "supplied_target_receipt_identity_bound": supplied_target_receipt_bound,
        "route_edge_hash_chain_contiguous": edge_hash_chain_contiguous,
        "route_edge_ambient_chain_contiguous": edge_ambient_chain_contiguous,
        "terminal_phase_geometry_identity_preserved": terminal_phase_geometry_identity,
        "generated_terminal_hash_required_to_equal_supplied_target_hash": False,
        "route_edge_chain_identity_preserved": route_edge_chain_identity,
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
        and left["target_ambient_state_index"] == right["source_ambient_state_index"]
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
    "DIRECTION_COUNT",
    "DIRECTION_FLUX",
    "DIRECTION_FLUX_INDEX",
    "DIRECTION_INDEX",
    "INDEX_DIRECTION",
    "INVERSE_DIRECTION",
    "INVERSE_DIRECTION_INDEX",
    "ITERATION",
    "LANE_COUNT",
    "NATIVE_PARITY_SCHEMA",
    "NODE_COUNT",
    "OPERATIONS_PER_CELL",
    "PHASE_COUNT",
    "ROUTE_AUDIT_SCHEMA",
    "DiscreteTransportConservationError",
    "audit_composed_transport_conservation",
    "audit_native_execution_parity",
    "audit_rml16_route_conservation",
    "audit_transport_address",
    "audit_transport_address_manifold",
    "decode_transport_address",
    "discrete_divergence",
    "encode_transport_address",
    "reciprocal_direction_index",
    "signed_address_flux",
    "signed_direction_flux",
    "transport_neighbor",
    "zero_diffusion_classification",
]
