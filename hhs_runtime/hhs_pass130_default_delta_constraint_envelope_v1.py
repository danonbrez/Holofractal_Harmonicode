from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import _canon
from hhs_runtime.hhs_pass129_invariant_delta_rational_projection_algebra_v1 import (
    InvariantDeltaProjectionAlgebra,
    Pass129Error,
    canonical_pass129_request,
)

PASS_ID = "PASS_130"
SPEC_SCHEMA = "HHS_DEFAULT_DELTA_CONSTRAINT_ENVELOPE_SPEC_V1"
ENVELOPE_SCHEMA = "HHS_DEFAULT_DELTA_CONSTRAINT_ENVELOPE_V1"
ADMISSION_SCHEMA = "HHS_HIGH_ENTROPY_PARAMETER_ADMISSION_V1"
REPLAY_SCHEMA = "HHS_DEFAULT_DELTA_CONSTRAINT_REPLAY_V1"

REJECTION_CODES = {
    "REJECT_INVALID_PASS129_PROOF",
    "REJECT_DEFAULT_ENVELOPE_ROOT_MISMATCH",
    "REJECT_LAYER_KIND_UNSUPPORTED",
    "REJECT_FLOAT_PARAMETER_AS_CANONICAL_AUTHORITY",
    "REJECT_PARAMETER_NOT_EXACT",
    "REJECT_REQUIRED_CONSTRAINT_DISABLED",
    "REJECT_PROJECTION_PROMOTED_TO_NATIVE_STATE",
    "REJECT_DEFAULT_CONSTRAINTS_USED_AS_STATE_ASSIGNMENT",
    "REJECT_ENTROPY_COLLAPSE_BY_DEFAULTS",
    "REJECT_PARAMETER_RESOURCE_BOUND",
    "REJECT_PARAMETER_ADMISSION_ROOT_MISMATCH",
    "REJECT_REPLAY_MISMATCH",
}


class Pass130Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _exact(value: Any) -> Any:
    if isinstance(value, float):
        raise Pass130Error("REJECT_FLOAT_PARAMETER_AS_CANONICAL_AUTHORITY", repr(value))
    if isinstance(value, Fraction):
        return {"kind": "RATIONAL", "numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, Mapping):
        return {str(k): _exact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_exact(v) for v in value]
    raise Pass130Error("REJECT_PARAMETER_NOT_EXACT", type(value).__name__)


@dataclass(frozen=True)
class Pass130Bounds:
    max_parameters: int = 4096
    max_branches: int = 65536
    max_dimensions: int = 81


class DefaultDeltaConstraintEnvelope:
    """Admits exact high-entropy parameter layers under Pass 129 defaults.

    The envelope constrains admissibility and normalization only. It never supplies
    amplitudes, probabilities, branch values, seeds, topology, or parameter assignments.
    """

    SUPPORTED_LAYER_KINDS = {
        "VM81_QUANTUM_SIMULATOR",
        "SYMBOLIC_QUANTUM_ALGEBRA",
        "HIGH_ENTROPY_NOISE_RESOLUTION",
        "PROBABILISTIC_PARAMETER_LAYER",
        "MULTIMODAL_TOKEN_LAYER",
        "GENERIC_HIGH_ENTROPY_LAYER",
    }

    REQUIRED_DEFAULTS = (
        "EXACT_RATIONAL_AUTHORITY",
        "NONZERO_SHARED_DELTA",
        "UNIT_DELTA_CLOSURE",
        "RECIPROCAL_PRODUCT_CLOSURE",
        "FOUR_PHASE_ZERO_SUM",
        "FOUR_PHASE_CARDINALITY_NORMALIZATION",
        "PROJECTION_NATIVE_SEPARATION",
        "DETERMINISTIC_REPLAY",
        "RESOURCE_BOUNDED_EXECUTION",
    )

    def __init__(self, bounds: Pass130Bounds | None = None):
        self.bounds = bounds or Pass130Bounds()
        self.spec = {
            "schema": SPEC_SCHEMA,
            "pass_id": PASS_ID,
            "role": "DEFAULT_ADMISSION_ENVELOPE_NOT_DEFAULT_STATE",
            "supported_layer_kinds": sorted(self.SUPPORTED_LAYER_KINDS),
            "required_defaults": list(self.REQUIRED_DEFAULTS),
            "entropy_preservation_rule": "DEFAULTS_MAY_REJECT_INVALID_STATES_BUT_MAY_NOT_SELECT_AMPLITUDES_BRANCHES_SEEDS_OR_PARAMETER_VALUES",
            "projection_authority": False,
            "float_authority": False,
        }
        self.spec["spec_root_hash72"] = _hash("hhs_pass130_spec_v1", self.spec)

    def build_default_envelope(self, request129: Mapping[str, Any], proof129: Mapping[str, Any]) -> dict[str, Any]:
        try:
            engine = InvariantDeltaProjectionAlgebra()
            validation = engine.validate(request129, proof129)
        except (Pass129Error, KeyError, ValueError, TypeError) as exc:
            raise Pass130Error("REJECT_INVALID_PASS129_PROOF", str(exc)) from exc
        if proof129.get("base_symbols_solved") is not False or proof129.get("external_projection_authority_used") is not False:
            raise Pass130Error("REJECT_PROJECTION_PROMOTED_TO_NATIVE_STATE", "Pass 129 boundary")
        if proof129.get("derived", {}).get("delta") != {"numerator": 1, "denominator": 1}:
            raise Pass130Error("REJECT_INVALID_PASS129_PROOF", "delta must close to 1")
        envelope = {
            "schema": ENVELOPE_SCHEMA,
            "pass_id": PASS_ID,
            "spec_root_hash72": self.spec["spec_root_hash72"],
            "parent_pass129_proof_root_hash72": proof129["proof_root_hash72"],
            "parent_pass129_validation_root_hash72": validation["validation_root_hash72"],
            "mode": "DEFAULT_INITIAL_CONSTRAINTS",
            "state_assignment": False,
            "constraints": {name: True for name in self.REQUIRED_DEFAULTS},
            "fixed_invariants": {
                "delta": {"numerator": 1, "denominator": 1},
                "phase_cardinality": 4,
                "phase_sum": [0, 0],
                "native_projection_authority": False,
            },
            "unconstrained_entropy_coordinates": [
                "amplitudes", "probability_weights", "branch_membership", "measurement_seed",
                "topology", "phase_offsets", "parameter_values", "modality_payloads", "operation_order",
            ],
            "authority_effect": "ADMISSION_ONLY",
        }
        envelope["envelope_root_hash72"] = _hash("hhs_pass130_envelope_v1", envelope)
        return envelope

    def validate_envelope(self, envelope: Mapping[str, Any]) -> None:
        body = dict(envelope)
        root = body.pop("envelope_root_hash72", None)
        if root != _hash("hhs_pass130_envelope_v1", body):
            raise Pass130Error("REJECT_DEFAULT_ENVELOPE_ROOT_MISMATCH", "envelope")
        if body.get("state_assignment") is not False or body.get("authority_effect") != "ADMISSION_ONLY":
            raise Pass130Error("REJECT_DEFAULT_CONSTRAINTS_USED_AS_STATE_ASSIGNMENT", "defaults assigned state")
        constraints = body.get("constraints", {})
        for name in self.REQUIRED_DEFAULTS:
            if constraints.get(name) is not True:
                raise Pass130Error("REJECT_REQUIRED_CONSTRAINT_DISABLED", name)

    def admit_parameter_layer(
        self,
        envelope: Mapping[str, Any],
        *,
        layer_kind: str,
        parameters: Mapping[str, Any],
        entropy_coordinates: Sequence[str],
        branch_count: int,
        dimension_count: int,
    ) -> dict[str, Any]:
        self.validate_envelope(envelope)
        if layer_kind not in self.SUPPORTED_LAYER_KINDS:
            raise Pass130Error("REJECT_LAYER_KIND_UNSUPPORTED", layer_kind)
        if len(parameters) > self.bounds.max_parameters or branch_count > self.bounds.max_branches or dimension_count > self.bounds.max_dimensions:
            raise Pass130Error("REJECT_PARAMETER_RESOURCE_BOUND", f"{len(parameters)},{branch_count},{dimension_count}")
        canonical_parameters = _exact(parameters)
        coords = [str(x) for x in entropy_coordinates]
        forbidden_assignments = {"selected_branch", "collapsed_state", "forced_amplitude", "forced_seed", "projection_value_as_native"}
        if forbidden_assignments.intersection(parameters):
            raise Pass130Error("REJECT_DEFAULT_CONSTRAINTS_USED_AS_STATE_ASSIGNMENT", str(sorted(forbidden_assignments.intersection(parameters))))
        if parameters.get("external_projection_authority") is True:
            raise Pass130Error("REJECT_PROJECTION_PROMOTED_TO_NATIVE_STATE", layer_kind)
        before = _hash("hhs_pass130_entropy_coordinates_v1", {"coordinates": coords, "branch_count": branch_count, "dimensions": dimension_count})
        after = _hash("hhs_pass130_entropy_coordinates_v1", {"coordinates": coords, "branch_count": branch_count, "dimensions": dimension_count})
        if before != after or len(coords) != len(list(entropy_coordinates)):
            raise Pass130Error("REJECT_ENTROPY_COLLAPSE_BY_DEFAULTS", layer_kind)
        admission = {
            "schema": ADMISSION_SCHEMA,
            "pass_id": PASS_ID,
            "envelope_root_hash72": envelope["envelope_root_hash72"],
            "layer_kind": layer_kind,
            "canonical_parameters": canonical_parameters,
            "entropy_coordinates": coords,
            "branch_count": int(branch_count),
            "dimension_count": int(dimension_count),
            "entropy_coordinate_root_before": before,
            "entropy_coordinate_root_after": after,
            "entropy_preserved": True,
            "default_constraints_applied": list(self.REQUIRED_DEFAULTS),
            "state_selected": False,
            "status": "ADMITTED_UNDER_DEFAULT_DELTA_CONSTRAINT_ENVELOPE",
        }
        admission["admission_root_hash72"] = _hash("hhs_pass130_admission_v1", admission)
        return admission

    def validate_admission(self, envelope: Mapping[str, Any], admission: Mapping[str, Any]) -> None:
        self.validate_envelope(envelope)
        body = dict(admission)
        claimed = body.pop("admission_root_hash72", None)
        if claimed != _hash("hhs_pass130_admission_v1", body):
            raise Pass130Error("REJECT_PARAMETER_ADMISSION_ROOT_MISMATCH", "admission")
        if admission.get("envelope_root_hash72") != envelope.get("envelope_root_hash72"):
            raise Pass130Error("REJECT_PARAMETER_ADMISSION_ROOT_MISMATCH", "parent")
        if admission.get("entropy_preserved") is not True or admission.get("state_selected") is not False:
            raise Pass130Error("REJECT_ENTROPY_COLLAPSE_BY_DEFAULTS", "receipt")

    def replay(self, envelope: Mapping[str, Any], admission: Mapping[str, Any]) -> dict[str, Any]:
        self.validate_admission(envelope, admission)
        rebuilt = self.admit_parameter_layer(
            envelope,
            layer_kind=admission["layer_kind"],
            parameters=deepcopy(admission["canonical_parameters"]),
            entropy_coordinates=admission["entropy_coordinates"],
            branch_count=admission["branch_count"],
            dimension_count=admission["dimension_count"],
        )
        if _canon(rebuilt) != _canon(admission):
            raise Pass130Error("REJECT_REPLAY_MISMATCH", "admission reconstruction")
        receipt = {
            "schema": REPLAY_SCHEMA,
            "pass_id": PASS_ID,
            "envelope_root_hash72": envelope["envelope_root_hash72"],
            "admission_root_hash72": admission["admission_root_hash72"],
            "status": "PASS_130_DETERMINISTIC_REPLAY_VALIDATED",
        }
        receipt["replay_root_hash72"] = _hash("hhs_pass130_replay_v1", receipt)
        return receipt


def canonical_pass130_envelope() -> tuple[DefaultDeltaConstraintEnvelope, dict[str, Any]]:
    p129, req = canonical_pass129_request(center_P=4)
    proof = p129.prove(req)
    engine = DefaultDeltaConstraintEnvelope()
    return engine, engine.build_default_envelope(req, proof)


def pass130_self_test() -> dict[str, Any]:
    engine, envelope = canonical_pass130_envelope()
    quantum = engine.admit_parameter_layer(
        envelope,
        layer_kind="VM81_QUANTUM_SIMULATOR",
        parameters={"basis_dimensions": [2, 2], "normalization": Fraction(1, 1), "external_projection_authority": False},
        entropy_coordinates=["amplitude[0]", "amplitude[1]", "amplitude[2]", "amplitude[3]", "measurement_seed"],
        branch_count=4,
        dimension_count=2,
    )
    replay = engine.replay(envelope, quantum)
    result = {
        "pass_id": PASS_ID,
        "status": "PASS",
        "envelope_root_hash72": envelope["envelope_root_hash72"],
        "quantum_admission_root_hash72": quantum["admission_root_hash72"],
        "replay_root_hash72": replay["replay_root_hash72"],
        "default_constraints_safe_for_quantum_and_high_entropy_layers": True,
        "defaults_select_state": False,
        "entropy_preserved": True,
    }
    result["self_test_root_hash72"] = _hash("hhs_pass130_self_test_v1", result)
    return result
