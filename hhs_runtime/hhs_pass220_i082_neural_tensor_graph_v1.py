"""Pass 220 I082: exact 86,805,555,555-neuron tensor graph specification.

This is a lazy, source-bound graph specification on the existing I070
Lane 5 / VM81 candidate bridge, NOT an independent runtime or a claim that
all graph edges or neurons have been materially executed. The original
noncommutative equation is carried verbatim and never scalar-cancelled.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i070_i_tensor_lane5_vm81_bridge_v1 import (
    build_lane5_vm81_candidate,
    global_vm81_address_witness,
    validate_lane5_vm81_candidate,
)

SCHEMA = "HHS_PASS_220_I082_NEURAL_TENSOR_GRAPH_V1"
NEURON_COUNT = 86805555555
VM81_WIDTH = 81 * 64
RAW_TENSOR = "(86805555555*x)/(600000000000000*a^2*x*y)*72^2*b*6==(a^2+b^2+c^2)/(x*y)==5184*z*w^u"
AUTHORITY = {
    "candidate_only": True,
    "native_ordered_closure_proven": False,
    "all_neurons_materialized": False,
    "all_edges_materialized": False,
    "inherited_lane5_i070_vm81": True,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "floating_point_authority": False,
}


class NeuralTensorGraphError(ValueError):
    """Fail-closed native candidate specification error."""


def ordered_ast() -> dict[str, Any]:
    """Operator tree: child order, typed division, powers and equality are retained."""
    atom = lambda name: {"atom": name}
    integer = lambda value: {"integer": value}
    mul = lambda *args: {"ordered_mul": list(args)}
    add = lambda *args: {"ordered_add": list(args)}
    power = lambda a, b: {"ordered_power": [a, b]}
    div = lambda a, b: {"ordered_divide": [a, b]}
    left = mul(
        div(mul(integer(NEURON_COUNT), atom("x")),
            mul(integer(600000000000000), power(atom("a"), integer(2)),
                atom("x"), atom("y"))),
        power(integer(72), integer(2)), atom("b"), integer(6),
    )
    middle = div(
        add(power(atom("a"), integer(2)), power(atom("b"), integer(2)),
            power(atom("c"), integer(2))),
        mul(atom("x"), atom("y")),
    )
    right = mul(integer(5184), atom("z"), power(atom("w"), atom("u")))
    return {"ordered_equality_chain": [left, middle, right]}


def graph_specification() -> dict[str, Any]:
    coefficient = Fraction(NEURON_COUNT * VM81_WIDTH * 6, 600000000000000)
    if coefficient != Fraction(1406249999991, 312500000000):
        raise NeuralTensorGraphError("exact numeric projection diverged")
    vm81 = global_vm81_address_witness()
    if vm81["exact_cover_0_80"] is not True:
        raise NeuralTensorGraphError("I070 VM81 address cover missing")
    return {
        "schema": SCHEMA,
        "neuron_count": NEURON_COUNT,
        "positions_per_neuron": VM81_WIDTH,
        "logical_positions": NEURON_COUNT * VM81_WIDTH,
        "raw_tensor": RAW_TENSOR,
        "ordered_ast": ordered_ast(),
        "exact_numeric_projection": {
            "a_squared_plus_b_squared_plus_c_squared": 6,
            "coefficient_numerator": coefficient.numerator,
            "coefficient_denominator": coefficient.denominator,
        },
        "vm81_address_witness": vm81,
        "neuron_binding": "explicit neuron_id AND native nucleus_index required",
        "edge_binding": "Lane 5 ordered relation witnesses required; not inferred from index",
        "authority": dict(AUTHORITY),
    }


def validate_graph_specification(spec: Mapping[str, Any]) -> bool:
    if dict(spec) != graph_specification():
        raise NeuralTensorGraphError("candidate graph specification diverged")
    return True


def sample_native_neuron(neuron_id: int, nucleus_index: int) -> dict[str, Any]:
    """Resolve a bounded node through I070 without inventing its nucleus/edges."""
    if type(neuron_id) is not int or not 0 <= neuron_id < NEURON_COUNT:
        raise NeuralTensorGraphError("neuron_id outside exact native graph range")
    if type(nucleus_index) is not int or not 0 <= nucleus_index < 9:
        raise NeuralTensorGraphError("explicit native nucleus_index must be 0..8")
    inherited = build_lane5_vm81_candidate(nucleus_index)
    validate_lane5_vm81_candidate(inherited)
    item = {
        "schema": SCHEMA,
        "neuron_id": neuron_id,
        "nucleus_index": nucleus_index,
        "vm81_cell_addresses": inherited["vm81_addresses"],
        "inherited_i070_binding_hash72": inherited["binding_hash72"],
        "inherited_i070_candidate_hash216": inherited["candidate_hash216"],
        "inherited_hydration_exact": inherited["candidate_hydration"]["roundtrip_exact"],
        "edge_relation_witness_status": "NOT_EVALUATED",
        "authority": dict(AUTHORITY),
    }
    if item["inherited_hydration_exact"] is not True:
        raise NeuralTensorGraphError("I070 inherited hydration did not roundtrip")
    item["sample_candidate_hash72"] = hash72(item)
    return item


def validate_sample_native_neuron(item: Mapping[str, Any]) -> bool:
    if item != sample_native_neuron(item.get("neuron_id"), item.get("nucleus_index")):
        raise NeuralTensorGraphError("native neuron sample altered")
    return True


def self_test() -> dict[str, Any]:
    spec = graph_specification()
    first = sample_native_neuron(0, 0)
    last = sample_native_neuron(NEURON_COUNT - 1, 8)
    checks = {
        "exact_count": spec["neuron_count"] == NEURON_COUNT,
        "logical_positions": spec["logical_positions"] == 449999999997120,
        "vm81_exact_cover": spec["vm81_address_witness"]["exact_cover_0_80"],
        "spec_roundtrip": validate_graph_specification(spec),
        "first_native_sample": validate_sample_native_neuron(first),
        "last_native_sample": validate_sample_native_neuron(last),
        "candidate_only": spec["authority"]["candidate_only"],
        "no_implicit_edges": spec["authority"]["all_edges_materialized"] is False,
    }
    return {
        "schema": SCHEMA + "_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "pass_count": sum(bool(x) for x in checks.values()),
        "check_count": len(checks),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), sort_keys=True, indent=2))
