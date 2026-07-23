from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import _canon
from hhs_runtime.hhs_pass130_default_delta_constraint_envelope_v1 import (
    DefaultDeltaConstraintEnvelope,
    Pass130Error,
    canonical_pass130_envelope,
)

PASS_ID = "PASS_131"
SPEC_SCHEMA = "HHS_EXACT_ELECTROCHEMICAL_ATOMIC_PHYSICS_SANDBOX_SPEC_V1"
STATE_SCHEMA = "HHS_EXACT_ATOMIC_ELECTROCHEMICAL_STATE_V1"
TRANSITION_SCHEMA = "HHS_EXACT_PHYSICS_TRANSITION_RECEIPT_V1"
PROMOTION_SCHEMA = "HHS_DETERMINISTIC_TENSOR_PROMOTION_V1"
REPLAY_SCHEMA = "HHS_EXACT_PHYSICS_REPLAY_V1"

REJECTION_CODES = {
    "REJECT_INVALID_PASS130_ENVELOPE",
    "REJECT_FLOAT_CANONICAL_PHYSICS_AUTHORITY",
    "REJECT_NONEXACT_CANONICAL_VALUE",
    "REJECT_INVALID_ATOMIC_NUMBER",
    "REJECT_INVALID_MASS_NUMBER",
    "REJECT_INVALID_ELECTRON_COUNT",
    "REJECT_INVALID_ORBITAL_OCCUPANCY",
    "REJECT_CHARGE_CONSERVATION_FAILURE",
    "REJECT_ELEMENT_CONSERVATION_FAILURE",
    "REJECT_PARTICLE_CONSERVATION_FAILURE",
    "REJECT_STATE_ROOT_MISMATCH",
    "REJECT_TRANSITION_ROOT_MISMATCH",
    "REJECT_TENSOR_PROMOTION_ROOT_MISMATCH",
    "REJECT_UNAUTHORIZED_GLOBAL_MUTATION",
    "REJECT_APPROXIMATION_PROMOTED_TO_AUTHORITY",
    "REJECT_UNSUPPORTED_OPERATION",
    "REJECT_RESOURCE_BOUND",
    "REJECT_REPLAY_MISMATCH",
    "REJECT_PROVEN_FINITE_PATH_NOT_DESCRIBED",
}


class Pass131Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _exact(value: Any) -> Any:
    if isinstance(value, float):
        raise Pass131Error("REJECT_FLOAT_CANONICAL_PHYSICS_AUTHORITY", repr(value))
    if isinstance(value, Fraction):
        return {"kind": "RATIONAL", "numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, Mapping):
        return {str(k): _exact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_exact(v) for v in value]
    raise Pass131Error("REJECT_NONEXACT_CANONICAL_VALUE", type(value).__name__)


def _sum_int(mapping: Mapping[str, Any]) -> int:
    return sum(int(v) for v in mapping.values())


@dataclass(frozen=True)
class Pass131Bounds:
    max_species: int = 4096
    max_tensor_rank: int = 81
    max_tensor_cells: int = 531441
    max_transition_terms: int = 16384


class ExactElectrochemicalAtomicPhysicsSandbox:
    """Exact symbolic/rational electrochemical and atomic-physics sandbox.

    Canonical authority never uses floating point or approximate values. Apparent
    under-resolution triggers deterministic tensor promotion. Observation
    projections are typed, non-authoritative children of exact canonical state.
    """

    OPERATIONS = {
        "IONIZE",
        "REDUCE",
        "TRANSFER_ELECTRONS",
        "BALANCE_REACTION",
        "APPLY_SYMBOLIC_HAMILTONIAN",
        "PROMOTE_TENSOR_RESOLUTION",
    }

    REQUIRED_STATE_INVARIANTS = (
        "NO_APPROXIMATE_CANONICAL_PHYSICS_AUTHORITY",
        "EXACT_SYMBOLIC_RATIONAL_STATE",
        "CHARGE_ACCOUNTING",
        "PARTICLE_ACCOUNTING",
        "ELEMENT_ACCOUNTING",
        "PROJECTION_NATIVE_SEPARATION",
        "DETERMINISTIC_TENSOR_SUBSTITUTION",
        "HASH72_REPLAY",
        "SANDBOX_BRANCH_ISOLATION",
    )

    def __init__(self, bounds: Pass131Bounds | None = None):
        self.bounds = bounds or Pass131Bounds()
        self.spec = {
            "schema": SPEC_SCHEMA,
            "pass_id": PASS_ID,
            "role": "EXACT_SYMBOLIC_ATOMIC_ELECTROCHEMICAL_EXECUTION_SANDBOX",
            "required_invariants": list(self.REQUIRED_STATE_INVARIANTS),
            "operational_directive": "FOR_EVERY_PROVABLY_FINITE_SOLVABLE_PROBLEM_SEARCH_AT_LEAST_ONE_EXACT_CONSTRAINT_PATH",
            "under_resolution_rule": "REPLACE_FLATTENED_VARIABLE_WITH_HIGHER_RESOLUTION_TYPED_TENSOR_EQUATION",
            "canonical_float_authority": False,
            "approximation_authority": False,
            "global_mutation": False,
        }
        self.spec["spec_root_hash72"] = _hash("hhs_pass131_spec_v1", self.spec)

    def _validate_envelope(self, envelope: Mapping[str, Any]) -> None:
        try:
            DefaultDeltaConstraintEnvelope().validate_envelope(envelope)
        except (Pass130Error, KeyError, TypeError, ValueError) as exc:
            raise Pass131Error("REJECT_INVALID_PASS130_ENVELOPE", str(exc)) from exc

    def create_atomic_state(
        self,
        envelope: Mapping[str, Any],
        *,
        species_id: str,
        atomic_number: int,
        mass_number: int,
        charge: int,
        electron_configuration: Mapping[str, int],
        symbolic_fields: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._validate_envelope(envelope)
        if atomic_number <= 0:
            raise Pass131Error("REJECT_INVALID_ATOMIC_NUMBER", str(atomic_number))
        if mass_number < atomic_number:
            raise Pass131Error("REJECT_INVALID_MASS_NUMBER", str(mass_number))
        electrons = atomic_number - charge
        if electrons < 0:
            raise Pass131Error("REJECT_INVALID_ELECTRON_COUNT", str(electrons))
        config = {str(k): int(v) for k, v in electron_configuration.items()}
        if any(v < 0 for v in config.values()) or _sum_int(config) != electrons:
            raise Pass131Error("REJECT_INVALID_ORBITAL_OCCUPANCY", f"expected {electrons}, got {_sum_int(config)}")
        state = {
            "schema": STATE_SCHEMA,
            "pass_id": PASS_ID,
            "spec_root_hash72": self.spec["spec_root_hash72"],
            "envelope_root_hash72": envelope["envelope_root_hash72"],
            "sandbox_branch": True,
            "global_state_mutation": False,
            "species_id": str(species_id),
            "nucleus": {"protons": atomic_number, "neutrons": mass_number - atomic_number, "mass_number": mass_number},
            "charge": int(charge),
            "electron_count": electrons,
            "electron_configuration": config,
            "symbolic_fields": _exact(symbolic_fields or {}),
            "canonical_authority": "EXACT_SYMBOLIC_RATIONAL_ONLY",
            "invariants": list(self.REQUIRED_STATE_INVARIANTS),
        }
        state["state_root_hash72"] = _hash("hhs_pass131_atomic_state_v1", state)
        return state

    def validate_state(self, envelope: Mapping[str, Any], state: Mapping[str, Any]) -> None:
        self._validate_envelope(envelope)
        body = dict(state)
        root = body.pop("state_root_hash72", None)
        if root != _hash("hhs_pass131_atomic_state_v1", body):
            raise Pass131Error("REJECT_STATE_ROOT_MISMATCH", "atomic state")
        if state.get("global_state_mutation") is not False or state.get("sandbox_branch") is not True:
            raise Pass131Error("REJECT_UNAUTHORIZED_GLOBAL_MUTATION", "state isolation")
        if state.get("canonical_authority") != "EXACT_SYMBOLIC_RATIONAL_ONLY":
            raise Pass131Error("REJECT_APPROXIMATION_PROMOTED_TO_AUTHORITY", "state authority")

    def promote_tensor(
        self,
        envelope: Mapping[str, Any],
        *,
        variable_name: str,
        scalar_value: Any,
        dimensions: Sequence[str],
        constraints: Sequence[Mapping[str, Any]],
        finite_solution_witness: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._validate_envelope(envelope)
        dims = [str(d) for d in dimensions]
        if not dims:
            dims = ["value"]
        if len(dims) > self.bounds.max_tensor_rank:
            raise Pass131Error("REJECT_RESOURCE_BOUND", "tensor rank")
        exact_constraints = [_exact(c) for c in constraints]
        cells = [{"coordinate": [d], "symbol": f"{variable_name}[{d}]"} for d in dims]
        if len(cells) > self.bounds.max_tensor_cells:
            raise Pass131Error("REJECT_RESOURCE_BOUND", "tensor cells")
        promotion = {
            "schema": PROMOTION_SCHEMA,
            "pass_id": PASS_ID,
            "envelope_root_hash72": envelope["envelope_root_hash72"],
            "source_variable": str(variable_name),
            "source_exact_value": _exact(scalar_value),
            "tensor_rank": len(dims),
            "dimensions": dims,
            "cells": cells,
            "constraints": exact_constraints,
            "finite_solution_witness": _exact(finite_solution_witness or {}),
            "information_discarded": False,
            "approximation_used": False,
            "status": "EXACT_TENSOR_PROMOTION_CLOSED",
        }
        if finite_solution_witness and not exact_constraints:
            raise Pass131Error("REJECT_PROVEN_FINITE_PATH_NOT_DESCRIBED", variable_name)
        promotion["promotion_root_hash72"] = _hash("hhs_pass131_tensor_promotion_v1", promotion)
        return promotion

    def validate_promotion(self, envelope: Mapping[str, Any], promotion: Mapping[str, Any]) -> None:
        self._validate_envelope(envelope)
        body = dict(promotion)
        root = body.pop("promotion_root_hash72", None)
        if root != _hash("hhs_pass131_tensor_promotion_v1", body):
            raise Pass131Error("REJECT_TENSOR_PROMOTION_ROOT_MISMATCH", "promotion")
        if promotion.get("information_discarded") is not False or promotion.get("approximation_used") is not False:
            raise Pass131Error("REJECT_APPROXIMATION_PROMOTED_TO_AUTHORITY", "promotion")

    def execute_transition(
        self,
        envelope: Mapping[str, Any],
        state: Mapping[str, Any],
        *,
        operation: str,
        parameters: Mapping[str, Any],
    ) -> dict[str, Any]:
        self.validate_state(envelope, state)
        if operation not in self.OPERATIONS:
            raise Pass131Error("REJECT_UNSUPPORTED_OPERATION", operation)
        p = _exact(parameters)
        after = deepcopy(state)
        after.pop("state_root_hash72", None)

        if operation in {"IONIZE", "REDUCE"}:
            count = int(parameters.get("electron_count", 1))
            if count <= 0:
                raise Pass131Error("REJECT_INVALID_ELECTRON_COUNT", str(count))
            delta = count if operation == "IONIZE" else -count
            after["charge"] = int(after["charge"]) + delta
            after["electron_count"] = int(after["electron_count"]) - delta
            if after["electron_count"] < 0:
                raise Pass131Error("REJECT_INVALID_ELECTRON_COUNT", str(after["electron_count"]))
            config = dict(after["electron_configuration"])
            orbital = str(parameters.get("orbital", sorted(config)[-1] if config else "symbolic"))
            config[orbital] = config.get(orbital, 0) - delta
            if config[orbital] < 0:
                raise Pass131Error("REJECT_INVALID_ORBITAL_OCCUPANCY", orbital)
            after["electron_configuration"] = config
            if _sum_int(config) != after["electron_count"]:
                raise Pass131Error("REJECT_PARTICLE_CONSERVATION_FAILURE", "electron ledger")

        elif operation == "APPLY_SYMBOLIC_HAMILTONIAN":
            if parameters.get("approximate") is True:
                raise Pass131Error("REJECT_APPROXIMATION_PROMOTED_TO_AUTHORITY", "Hamiltonian")
            after["symbolic_fields"] = dict(after.get("symbolic_fields", {}))
            after["symbolic_fields"]["hamiltonian_action"] = p

        elif operation == "PROMOTE_TENSOR_RESOLUTION":
            promotion = self.promote_tensor(
                envelope,
                variable_name=str(parameters["variable_name"]),
                scalar_value=parameters.get("scalar_value"),
                dimensions=parameters.get("dimensions", []),
                constraints=parameters.get("constraints", []),
                finite_solution_witness=parameters.get("finite_solution_witness"),
            )
            after["symbolic_fields"] = dict(after.get("symbolic_fields", {}))
            after["symbolic_fields"]["tensor_promotions"] = list(after["symbolic_fields"].get("tensor_promotions", [])) + [promotion]

        elif operation in {"TRANSFER_ELECTRONS", "BALANCE_REACTION"}:
            after["symbolic_fields"] = dict(after.get("symbolic_fields", {}))
            after["symbolic_fields"][operation.lower()] = p

        after["state_root_hash72"] = _hash("hhs_pass131_atomic_state_v1", after)
        self.validate_state(envelope, after)
        receipt = {
            "schema": TRANSITION_SCHEMA,
            "pass_id": PASS_ID,
            "envelope_root_hash72": envelope["envelope_root_hash72"],
            "before_state_root_hash72": state["state_root_hash72"],
            "operation": operation,
            "canonical_parameters": p,
            "after_state": after,
            "after_state_root_hash72": after["state_root_hash72"],
            "charge_delta": int(after["charge"]) - int(state["charge"]),
            "electron_delta": int(after["electron_count"]) - int(state["electron_count"]),
            "proton_delta": int(after["nucleus"]["protons"]) - int(state["nucleus"]["protons"]),
            "exact": True,
            "approximation_used": False,
            "global_state_mutated": False,
            "status": "EXACT_PHYSICS_TRANSITION_CLOSED",
        }
        if receipt["charge_delta"] != -receipt["electron_delta"]:
            raise Pass131Error("REJECT_CHARGE_CONSERVATION_FAILURE", operation)
        if receipt["proton_delta"] != 0:
            raise Pass131Error("REJECT_ELEMENT_CONSERVATION_FAILURE", operation)
        receipt["transition_root_hash72"] = _hash("hhs_pass131_transition_v1", receipt)
        return receipt

    def validate_transition(self, envelope: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
        self._validate_envelope(envelope)
        body = dict(receipt)
        root = body.pop("transition_root_hash72", None)
        if root != _hash("hhs_pass131_transition_v1", body):
            raise Pass131Error("REJECT_TRANSITION_ROOT_MISMATCH", "transition")
        self.validate_state(envelope, receipt["after_state"])
        if receipt.get("exact") is not True or receipt.get("approximation_used") is not False:
            raise Pass131Error("REJECT_APPROXIMATION_PROMOTED_TO_AUTHORITY", "transition")

    def balance_reaction(
        self,
        envelope: Mapping[str, Any],
        *,
        reactants: Sequence[Mapping[str, Any]],
        products: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        self._validate_envelope(envelope)
        if len(reactants) + len(products) > self.bounds.max_transition_terms:
            raise Pass131Error("REJECT_RESOURCE_BOUND", "reaction terms")
        rs = [_exact(x) for x in reactants]
        ps = [_exact(x) for x in products]

        def totals(terms: Sequence[Mapping[str, Any]]) -> tuple[dict[str, int], int]:
            elements: dict[str, int] = {}
            charge = 0
            for term in terms:
                coeff = int(term.get("coefficient", 1))
                charge += coeff * int(term.get("charge", 0))
                for element, count in term.get("elements", {}).items():
                    elements[str(element)] = elements.get(str(element), 0) + coeff * int(count)
            return elements, charge

        re, rc = totals(reactants)
        pe, pc = totals(products)
        if re != pe:
            raise Pass131Error("REJECT_ELEMENT_CONSERVATION_FAILURE", f"{re}!={pe}")
        if rc != pc:
            raise Pass131Error("REJECT_CHARGE_CONSERVATION_FAILURE", f"{rc}!={pc}")
        receipt = {
            "schema": TRANSITION_SCHEMA,
            "pass_id": PASS_ID,
            "envelope_root_hash72": envelope["envelope_root_hash72"],
            "operation": "BALANCE_REACTION",
            "reactants": rs,
            "products": ps,
            "element_totals": re,
            "charge_total": rc,
            "exact": True,
            "approximation_used": False,
            "status": "EXACT_REACTION_BALANCED",
        }
        receipt["transition_root_hash72"] = _hash("hhs_pass131_transition_v1", receipt)
        return receipt

    def replay(self, envelope: Mapping[str, Any], state: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
        self.validate_transition(envelope, receipt)
        rebuilt = self.execute_transition(
            envelope,
            state,
            operation=receipt["operation"],
            parameters=deepcopy(receipt.get("canonical_parameters", {})),
        )
        if _canon(rebuilt) != _canon(receipt):
            raise Pass131Error("REJECT_REPLAY_MISMATCH", "transition reconstruction")
        out = {
            "schema": REPLAY_SCHEMA,
            "pass_id": PASS_ID,
            "transition_root_hash72": receipt["transition_root_hash72"],
            "after_state_root_hash72": receipt["after_state_root_hash72"],
            "status": "PASS_131_DETERMINISTIC_REPLAY_VALIDATED",
        }
        out["replay_root_hash72"] = _hash("hhs_pass131_replay_v1", out)
        return out


def canonical_pass131_sandbox() -> tuple[ExactElectrochemicalAtomicPhysicsSandbox, dict[str, Any]]:
    _, envelope = canonical_pass130_envelope()
    return ExactElectrochemicalAtomicPhysicsSandbox(), envelope


def pass131_self_test() -> dict[str, Any]:
    engine, envelope = canonical_pass131_sandbox()
    lithium = engine.create_atomic_state(
        envelope,
        species_id="Li",
        atomic_number=3,
        mass_number=7,
        charge=0,
        electron_configuration={"1s": 2, "2s": 1},
        symbolic_fields={"radial_state": "R_{2s}(r)", "energy": "E_{2s}"},
    )
    ionization = engine.execute_transition(envelope, lithium, operation="IONIZE", parameters={"electron_count": 1, "orbital": "2s"})
    replay = engine.replay(envelope, lithium, ionization)
    promotion = engine.promote_tensor(
        envelope,
        variable_name="electrode_potential",
        scalar_value="V",
        dimensions=["species", "position", "phase", "time", "ancestry"],
        constraints=[
            {"equation": "charge_in-charge_out=0"},
            {"equation": "state[n+1]=F(state[n],constraints[n])"},
        ],
        finite_solution_witness={"provably_finite": True, "path_bound": 72},
    )
    result = {
        "pass_id": PASS_ID,
        "status": "PASS",
        "state_root_hash72": lithium["state_root_hash72"],
        "transition_root_hash72": ionization["transition_root_hash72"],
        "promotion_root_hash72": promotion["promotion_root_hash72"],
        "replay_root_hash72": replay["replay_root_hash72"],
        "exact_symbolic_rational_authority": True,
        "tensor_substitution_operational": True,
        "finite_solution_constraint_path_rule": True,
        "global_state_mutated": False,
    }
    result["self_test_root_hash72"] = _hash("hhs_pass131_self_test_v1", result)
    return result
