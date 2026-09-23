"""Pass 220 I027 quantum-collapse -> Pass 213 VM81 admission bridge.

T_QM-03B binds an exact I026 collapse candidate to the existing Pass 213
parametric VM81 admission authority.

This module intentionally stops before canonical runtime mutation. The current
Pass 213 native dispatch registry has no quantum-collapse opcode. A successful
I027 result therefore proves authenticated admission binding and fail-closed
dispatch readiness; it does not mint a second mutation authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CompiledROMEntry,
    TimestampBoundary,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_native_dispatch_common_v1 import (
    _NATIVE_DISPATCH_IDS,
)
from hhs_backend.runtime.hhs_pass213_parametric_delta_v1 import (
    ParametricConstraint,
    ParametricFieldSpec,
    ParametricROMAdmission,
    ParametricROMTemplate,
    create_parametric_admission,
)
from hhs_runtime.hhs_pass220_144cell_epsilon_lo_shu_closure_v1 import (
    ZERO_CENTERED_LO_SHU,
    sgn3,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    LO_SHU,
    LO_SHU_FLAT,
    VM81_CELLS,
)

SCHEMA = "HHS_PASS_220_I027_QUANTUM_COLLAPSE_ADMISSION_BRIDGE_V1"
PROFILE = "PASS220-I027-QUANTUM-COLLAPSE-ADMISSION-BRIDGE-v1"

I026_COLLAPSE_SCHEMA = "HHS_PASS_220_I026_COLLAPSE_CANDIDATE_V1"
STATE_SPACE = "Q(zeta72)^9"
SEMANTIC_DOMAIN = "HHS_QUANTUM_COLLAPSE_V1"
LO_SHU_ORDERING = "ROW_MAJOR_3X3"
ADMISSION_PROFILE = "PASS213_PARAMETRIC_VM81"
QUANTUM_NATIVE_DISPATCH_ID = "hhs.native.quantum.collapse.v1"

CANONICAL_MUTATION_AUTHORITY = False
HASH72_MINT_AUTHORITY = False
HASH216_PERSISTENCE_AUTHORITY = False
PASS213_PARAMETRIC_ADMISSION_AUTHORITY = True
GOVERNED_DISPATCH_REQUIRED = True


class Pass220I027CollapseAdmissionError(ValueError):
    pass


@dataclass(frozen=True)
class CollapseAddress:
    outcome: int
    nucleus_index: int
    row: int
    column: int
    lo_shu_value: int
    zero_centered_value: int
    trinary_sign: int
    vm81_cell_id: int


def _exact_index(value: Any, name: str, *, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I027CollapseAdmissionError(
            f"{name} must be an exact integer"
        )
    if not 0 <= value < upper:
        raise Pass220I027CollapseAdmissionError(
            f"{name} must satisfy 0 <= {name} < {upper}"
        )
    return value


def _hex64(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass220I027CollapseAdmissionError(
            f"{name} must be 64 hex characters"
        )
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass220I027CollapseAdmissionError(
            f"{name} must be lowercase/uppercase hexadecimal"
        ) from exc
    return value.lower()


def _receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return {
        **dict(payload),
        "receipt_sha256": sha256(
            encoded.encode("utf-8")
        ).hexdigest(),
    }


def collapse_address(
    outcome: int,
    nucleus_index: int,
) -> CollapseAddress:
    k = _exact_index(outcome, "outcome", upper=9)
    nucleus = _exact_index(
        nucleus_index, "nucleus_index", upper=9
    )
    row, column = divmod(k, 3)
    vm81_cell_id = nucleus * 9 + k
    if not 0 <= vm81_cell_id < VM81_CELLS:
        raise Pass220I027CollapseAdmissionError(
            "derived VM81 cell escaped canonical 0..80 range"
        )
    lo_shu_value = LO_SHU[row][column]
    zero_centered_value = ZERO_CENTERED_LO_SHU[row][column]
    return CollapseAddress(
        outcome=k,
        nucleus_index=nucleus,
        row=row,
        column=column,
        lo_shu_value=lo_shu_value,
        zero_centered_value=zero_centered_value,
        trinary_sign=sgn3(zero_centered_value),
        vm81_cell_id=vm81_cell_id,
    )


def quantum_operation_id(address: CollapseAddress) -> str:
    return (
        "HHS_QUANTUM_COLLAPSE_"
        f"N{address.nucleus_index}_K{address.outcome}_V1"
    )


def quantum_canonical_operation(
    address: CollapseAddress,
) -> dict[str, Any]:
    return {
        "semantic_domain": SEMANTIC_DOMAIN,
        "source_schema": I026_COLLAPSE_SCHEMA,
        "state_space": STATE_SPACE,
        "lo_shu_ordering": LO_SHU_ORDERING,
        "admission_profile": ADMISSION_PROFILE,
        "outcome": address.outcome,
        "nucleus_index": address.nucleus_index,
        "lo_shu_row": address.row,
        "lo_shu_column": address.column,
        "lo_shu_value": address.lo_shu_value,
        "zero_centered_value": address.zero_centered_value,
        "trinary_sign": address.trinary_sign,
        "vm81_cell_id": address.vm81_cell_id,
        "requested_mutation": "QUANTUM_COLLAPSE_COMMIT",
    }


def validate_quantum_compiled_entry(
    entry: CompiledROMEntry,
    address: CollapseAddress,
) -> None:
    if not isinstance(entry, CompiledROMEntry):
        raise Pass220I027CollapseAdmissionError(
            "base entry must be a Pass213 CompiledROMEntry"
        )
    entry.validate()
    if entry.operation_id != quantum_operation_id(address):
        raise Pass220I027CollapseAdmissionError(
            "quantum operation id does not match collapse address"
        )
    if entry.vm81_cell_id != address.vm81_cell_id:
        raise Pass220I027CollapseAdmissionError(
            "compiled entry VM81 cell does not match Lo Shu address"
        )
    if entry.native_dispatch_id != QUANTUM_NATIVE_DISPATCH_ID:
        raise Pass220I027CollapseAdmissionError(
            "compiled entry is not the quantum-collapse native dispatch id"
        )
    expected = quantum_canonical_operation(address)
    actual = dict(entry.canonical_operation)
    for key, value in expected.items():
        if actual.get(key) != value:
            raise Pass220I027CollapseAdmissionError(
                f"compiled quantum semantic mismatch:{key}"
            )


def _zero_hash() -> str:
    return "0" * 64


def _baseline_candidate(
    address: CollapseAddress,
) -> dict[str, Any]:
    return {
        "operands": {
            "outcome": address.outcome,
            "nucleus_index": address.nucleus_index,
            "vm81_cell_id": address.vm81_cell_id,
            "lo_shu_row": address.row,
            "lo_shu_column": address.column,
            "lo_shu_value": address.lo_shu_value,
            "zero_centered_value": address.zero_centered_value,
            "trinary_sign": address.trinary_sign,
        },
        "context": {
            "semantic_domain": SEMANTIC_DOMAIN,
            "state_space": STATE_SPACE,
            "source_schema": I026_COLLAPSE_SCHEMA,
            "collapse_candidate_receipt_sha256": _zero_hash(),
            "measurement_receipt_sha256": _zero_hash(),
            "source_state_receipt_sha256": _zero_hash(),
            "projected_state_root_hash216": _zero_hash(),
            "normalization_root_hash216": _zero_hash(),
        },
    }


def quantum_collapse_template(
    entry: CompiledROMEntry,
    address: CollapseAddress,
) -> ParametricROMTemplate:
    validate_quantum_compiled_entry(entry, address)
    immutable_ints = (
        ("operands.outcome", address.outcome),
        ("operands.nucleus_index", address.nucleus_index),
        ("operands.vm81_cell_id", address.vm81_cell_id),
        ("operands.lo_shu_row", address.row),
        ("operands.lo_shu_column", address.column),
        ("operands.lo_shu_value", address.lo_shu_value),
        (
            "operands.zero_centered_value",
            address.zero_centered_value,
        ),
        ("operands.trinary_sign", address.trinary_sign),
    )
    fields = [
        ParametricFieldSpec(path, "integer", False)
        for path, _ in immutable_ints
    ]
    fields.extend(
        (
            ParametricFieldSpec(
                "context.semantic_domain", "string", False
            ),
            ParametricFieldSpec(
                "context.state_space", "string", False
            ),
            ParametricFieldSpec(
                "context.source_schema", "string", False
            ),
            ParametricFieldSpec(
                "context.collapse_candidate_receipt_sha256",
                "hex",
                True,
            ),
            ParametricFieldSpec(
                "context.measurement_receipt_sha256",
                "hex",
                True,
            ),
            ParametricFieldSpec(
                "context.source_state_receipt_sha256",
                "hex",
                True,
            ),
            ParametricFieldSpec(
                "context.projected_state_root_hash216",
                "hex",
                True,
            ),
            ParametricFieldSpec(
                "context.normalization_root_hash216",
                "hex",
                True,
            ),
        )
    )

    constraints = [
        ParametricConstraint(
            f"lock_{path.replace('.', '_')}",
            "INT_RANGE",
            (path,),
            {"minimum": value, "maximum": value},
        )
        for path, value in immutable_ints
    ]
    constraints.extend(
        (
            ParametricConstraint(
                "semantic_domain",
                "ENUM",
                ("context.semantic_domain",),
                {"allowed": [SEMANTIC_DOMAIN]},
            ),
            ParametricConstraint(
                "state_space",
                "ENUM",
                ("context.state_space",),
                {"allowed": [STATE_SPACE]},
            ),
            ParametricConstraint(
                "source_schema",
                "ENUM",
                ("context.source_schema",),
                {"allowed": [I026_COLLAPSE_SCHEMA]},
            ),
        )
    )
    for name in (
        "collapse_candidate_receipt_sha256",
        "measurement_receipt_sha256",
        "source_state_receipt_sha256",
        "projected_state_root_hash216",
        "normalization_root_hash216",
    ):
        constraints.append(
            ParametricConstraint(
                f"{name}_length",
                "LENGTH_RANGE",
                (f"context.{name}",),
                {"minimum": 64, "maximum": 64},
            )
        )

    return ParametricROMTemplate.create(
        template_id=(
            "PASS220_I027_"
            f"N{address.nucleus_index}_K{address.outcome}"
        ),
        base_entry_hash216=entry.entry_hash216,
        operation_id=entry.operation_id,
        field_specs=tuple(fields),
        baseline_candidate=_baseline_candidate(address),
        constraints=tuple(constraints),
    )


def _collapse_candidate_payload(
    collapse: Mapping[str, Any],
    address: CollapseAddress,
) -> dict[str, Any]:
    if collapse.get("schema") != I026_COLLAPSE_SCHEMA:
        raise Pass220I027CollapseAdmissionError(
            "collapse candidate schema mismatch"
        )
    if collapse.get("outcome") != address.outcome:
        raise Pass220I027CollapseAdmissionError(
            "collapse outcome does not match Lo Shu address"
        )
    if collapse.get("canonical_state_mutated") is not False:
        raise Pass220I027CollapseAdmissionError(
            "I026 candidate must not already claim canonical mutation"
        )
    if collapse.get("canonical_admission_authority") is not False:
        raise Pass220I027CollapseAdmissionError(
            "I026 candidate must not already claim admission authority"
        )
    projected = collapse.get("projected_state")
    normalization = collapse.get("normalization_carrier")
    if not isinstance(projected, list) or not isinstance(
        normalization, Mapping
    ):
        raise Pass220I027CollapseAdmissionError(
            "collapse candidate exact state carriers are missing"
        )

    collapse_sha = _hex64(
        collapse.get("receipt_sha256"),
        "collapse_candidate_receipt_sha256",
    )
    measurement_sha = _hex64(
        collapse.get("measurement_receipt_sha256"),
        "measurement_receipt_sha256",
    )
    source_state_sha = _hex64(
        collapse.get("source_state_receipt_sha256"),
        "source_state_receipt_sha256",
    )

    projected_root = hash216(
        "pass220-i027-projected-state",
        canonical_bytes(projected),
    )
    normalization_root = hash216(
        "pass220-i027-normalization-carrier",
        canonical_bytes(dict(normalization)),
    )

    candidate = _baseline_candidate(address)
    candidate["context"].update(
        {
            "collapse_candidate_receipt_sha256": collapse_sha,
            "measurement_receipt_sha256": measurement_sha,
            "source_state_receipt_sha256": source_state_sha,
            "projected_state_root_hash216": projected_root,
            "normalization_root_hash216": normalization_root,
        }
    )
    return candidate


def create_quantum_collapse_admission(
    *,
    collapse_candidate: Mapping[str, Any],
    nucleus_index: int,
    base_entry: CompiledROMEntry,
    opening_boundary: TimestampBoundary,
    validation_key: bytes,
) -> tuple[ParametricROMAdmission, dict[str, Any]]:
    outcome = _exact_index(
        collapse_candidate.get("outcome"),
        "outcome",
        upper=9,
    )
    address = collapse_address(outcome, nucleus_index)
    validate_quantum_compiled_entry(base_entry, address)

    template = quantum_collapse_template(base_entry, address)
    candidate = _collapse_candidate_payload(
        collapse_candidate, address
    )
    admission = create_parametric_admission(
        template=template,
        base_entry=base_entry,
        candidate=candidate,
        opening_boundary=opening_boundary,
        validation_key=validation_key,
    )
    admission.validate(
        validation_key,
        template,
        base_entry,
        opening_boundary,
    )

    if admission.vm81_cell_id != address.vm81_cell_id:
        raise Pass220I027CollapseAdmissionError(
            "Pass213 admission returned wrong VM81 cell"
        )
    if admission.parent_hash216 != opening_boundary.parent_hash216:
        raise Pass220I027CollapseAdmissionError(
            "Pass213 admission parent lineage mismatch"
        )

    dispatch_registered = (
        QUANTUM_NATIVE_DISPATCH_ID in _NATIVE_DISPATCH_IDS
    )
    status = (
        "ADMISSION_BOUND_DISPATCH_READY"
        if dispatch_registered
        else "ADMISSION_BOUND_DISPATCH_BLOCKED"
    )

    binding = _receipt(
        {
            "schema": SCHEMA,
            "profile": PROFILE,
            "status": status,
            "outcome": address.outcome,
            "nucleus_index": address.nucleus_index,
            "lo_shu_row": address.row,
            "lo_shu_column": address.column,
            "lo_shu_value": address.lo_shu_value,
            "zero_centered_value": (
                address.zero_centered_value
            ),
            "trinary_sign": address.trinary_sign,
            "vm81_cell_id": address.vm81_cell_id,
            "operation_id": base_entry.operation_id,
            "native_dispatch_id": (
                base_entry.native_dispatch_id
            ),
            "pass213_template_hash216": (
                template.template_hash216
            ),
            "pass213_candidate_hash216": (
                admission.candidate_hash216
            ),
            "pass213_delta_root_hash216": (
                admission.delta_root_hash216
            ),
            "pass213_vm81_admission_root_hash216": (
                admission.vm81_admission_root_hash216
            ),
            "opening_boundary_hash216": (
                opening_boundary.boundary_hash216
            ),
            "parent_hash216": admission.parent_hash216,
            "pass213_parametric_admission_validated": True,
            "pass213_parametric_admission_authority_used": True,
            "row_major_lo_shu_binding_verified": True,
            "native_quantum_dispatch_registered": (
                dispatch_registered
            ),
            "governed_dispatch_required": True,
            "canonical_runtime_mutated": False,
            "canonical_collapse_commit_closed": (
                dispatch_registered
            ),
            "new_mutation_authority_created": False,
            "hash72_minted": False,
            "hash216_persisted": False,
        }
    )
    return admission, binding


def bridge_contract_descriptor() -> dict[str, Any]:
    return _receipt(
        {
            "schema": SCHEMA,
            "profile": PROFILE,
            "outcome_address_rule": (
                "row=outcome//3,column=outcome%3"
            ),
            "lo_shu_ordering": LO_SHU_ORDERING,
            "lo_shu_flat": LO_SHU_FLAT,
            "vm81_address_rule": (
                "vm81_cell_id=9*nucleus_index+outcome"
            ),
            "vm81_cell_range": [0, 80],
            "pass213_admission": (
                "create_parametric_admission + validate"
            ),
            "quantum_native_dispatch_id": (
                QUANTUM_NATIVE_DISPATCH_ID
            ),
            "native_quantum_dispatch_registered": (
                QUANTUM_NATIVE_DISPATCH_ID
                in _NATIVE_DISPATCH_IDS
            ),
            "canonical_mutation_authority": (
                CANONICAL_MUTATION_AUTHORITY
            ),
            "hash72_mint_authority": HASH72_MINT_AUTHORITY,
            "hash216_persistence_authority": (
                HASH216_PERSISTENCE_AUTHORITY
            ),
            "pass213_parametric_admission_authority": (
                PASS213_PARAMETRIC_ADMISSION_AUTHORITY
            ),
            "governed_dispatch_required": (
                GOVERNED_DISPATCH_REQUIRED
            ),
        }
    )
