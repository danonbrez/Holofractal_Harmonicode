"""Pass 213 iteration 4: dependency-scoped parametric compiled-ROM admission.

A parametric template binds one immutable compiled-ROM transformation to a
canonical operand/context schema and a finite deterministic constraint set.
Candidate invocations validate their complete typed shape, compute the exact
changed-field delta, re-evaluate only constraints that depend on those fields,
reuse authenticated baseline witnesses for unaffected constraints, and mint a
boundary-bound VM81 admission proof. Templates and admissions can be retained
only in sealed native arenas through :class:`NativeParametricCompiledROMStore`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import hmac
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CompiledROMEntry,
    Pass213ValidationError,
    TimestampBoundary,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore,
)
from hhs_backend.runtime.hhs_pass213_secure_memory_v1 import (
    NativeSecureArena,
    Pass213SecureMemoryError,
    SecureMemoryReceipt,
)

ITERATION = 4
RUNTIME_CLASSIFICATION = "HHS_PASS_213_PARAMETRIC_DELTA_ADMISSION_ITERATION4"
_ALLOWED_SCOPES = {"operands", "context"}
_ALLOWED_TYPES = {"bigint", "integer", "boolean", "string", "hex", "list", "mapping"}
_ALLOWED_CONSTRAINTS = {
    "INT_RANGE",
    "MAX_BITS",
    "ENUM",
    "NONZERO",
    "EQUAL",
    "NOT_EQUAL",
    "ORDERED_LE",
    "LENGTH_RANGE",
    "SUM_MAX_BITS",
}


class Pass213ParametricValidationError(Pass213ValidationError):
    """Raised when a parametric template or invocation is inadmissible."""


def _validate_hash216(value: str, code: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass213ParametricValidationError(f"PASS213_{code}_LENGTH_INVALID")
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213ParametricValidationError(f"PASS213_{code}_FORMAT_INVALID") from exc


def _authenticate(key: bytes, domain: str, payload: Mapping[str, Any]) -> str:
    if not isinstance(key, bytes) or len(key) < 32:
        raise Pass213ParametricValidationError("PASS213_PARAMETRIC_KEY_TOO_SHORT")
    domain_bytes = domain.encode("utf-8")
    message = (
        b"HHS-P213-PARAMETRIC-HMAC-V1\0"
        + len(domain_bytes).to_bytes(2, "big")
        + domain_bytes
        + canonical_bytes(payload)
    )
    return hmac.new(key, message, sha256).hexdigest()


def _path_parts(path: str) -> tuple[str, str]:
    if not isinstance(path, str) or path.count(".") != 1:
        raise Pass213ParametricValidationError("PASS213_PARAMETRIC_FIELD_PATH_INVALID")
    scope, name = path.split(".", 1)
    if scope not in _ALLOWED_SCOPES or not name or "." in name:
        raise Pass213ParametricValidationError("PASS213_PARAMETRIC_FIELD_PATH_INVALID")
    return scope, name


def _candidate_sections(candidate: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    if not isinstance(candidate, Mapping) or set(candidate) != _ALLOWED_SCOPES:
        raise Pass213ParametricValidationError("PASS213_PARAMETRIC_CANDIDATE_SECTIONS_INVALID")
    operands = candidate["operands"]
    context = candidate["context"]
    if not isinstance(operands, Mapping) or not isinstance(context, Mapping):
        raise Pass213ParametricValidationError("PASS213_PARAMETRIC_CANDIDATE_SECTION_TYPE_INVALID")
    return operands, context


def _get_path(candidate: Mapping[str, Any], path: str) -> Any:
    scope, name = _path_parts(path)
    operands, context = _candidate_sections(candidate)
    section = operands if scope == "operands" else context
    try:
        return section[name]
    except KeyError as exc:
        raise Pass213ParametricValidationError(
            f"PASS213_PARAMETRIC_FIELD_MISSING:{path}"
        ) from exc


def _validate_value_type(value: Any, type_name: str, path: str) -> None:
    if type_name in {"bigint", "integer"}:
        valid = isinstance(value, int) and not isinstance(value, bool)
    elif type_name == "boolean":
        valid = isinstance(value, bool)
    elif type_name == "string":
        valid = isinstance(value, str)
    elif type_name == "hex":
        valid = isinstance(value, str) and len(value) % 2 == 0
        if valid:
            try:
                bytes.fromhex(value)
            except ValueError:
                valid = False
    elif type_name == "list":
        valid = isinstance(value, list)
    elif type_name == "mapping":
        valid = isinstance(value, Mapping)
    else:
        valid = False
    if not valid:
        raise Pass213ParametricValidationError(
            f"PASS213_PARAMETRIC_FIELD_TYPE_INVALID:{path}:{type_name}"
        )
    canonical_bytes(value)


@dataclass(frozen=True)
class ParametricFieldSpec:
    path: str
    value_type: str
    mutable: bool = True

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "path": self.path,
            "value_type": self.value_type,
            "mutable": self.mutable,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ParametricFieldSpec":
        return cls(
            path=str(value["path"]),
            value_type=str(value["value_type"]),
            mutable=bool(value["mutable"]),
        )

    def validate(self) -> None:
        _path_parts(self.path)
        if self.value_type not in _ALLOWED_TYPES:
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_FIELD_TYPE_NAME_INVALID"
            )
        if not isinstance(self.mutable, bool):
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_FIELD_MUTABILITY_INVALID"
            )


@dataclass(frozen=True)
class ParametricConstraint:
    constraint_id: str
    kind: str
    dependencies: tuple[str, ...]
    arguments: Mapping[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "kind": self.kind,
            "dependencies": list(self.dependencies),
            "arguments": dict(self.arguments),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ParametricConstraint":
        return cls(
            constraint_id=str(value["constraint_id"]),
            kind=str(value["kind"]),
            dependencies=tuple(str(item) for item in value["dependencies"]),
            arguments=dict(value.get("arguments", {})),
        )

    def validate(self, field_paths: set[str]) -> None:
        if not self.constraint_id:
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_CONSTRAINT_ID_INVALID"
            )
        if self.kind not in _ALLOWED_CONSTRAINTS:
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_CONSTRAINT_KIND_INVALID"
            )
        if not self.dependencies or len(set(self.dependencies)) != len(self.dependencies):
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_CONSTRAINT_DEPENDENCIES_INVALID"
            )
        if not set(self.dependencies) <= field_paths:
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_CONSTRAINT_DEPENDENCY_UNKNOWN"
            )
        canonical_bytes(self.arguments)
        expected_counts = {
            "INT_RANGE": {1}, "MAX_BITS": {1}, "ENUM": {1}, "NONZERO": {1},
            "EQUAL": {2}, "NOT_EQUAL": {2}, "ORDERED_LE": {2},
            "LENGTH_RANGE": {1},
        }
        allowed = expected_counts.get(self.kind)
        if allowed is not None and len(self.dependencies) not in allowed:
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_CONSTRAINT_ARITY_INVALID"
            )
        if self.kind == "SUM_MAX_BITS" and len(self.dependencies) < 2:
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_CONSTRAINT_ARITY_INVALID"
            )

    def evaluate(self, candidate: Mapping[str, Any]) -> str:
        values = tuple(_get_path(candidate, path) for path in self.dependencies)
        ok = False
        if self.kind == "INT_RANGE":
            value = values[0]
            minimum = self.arguments.get("minimum")
            maximum = self.arguments.get("maximum")
            ok = (
                isinstance(value, int) and not isinstance(value, bool)
                and (minimum is None or value >= int(minimum))
                and (maximum is None or value <= int(maximum))
            )
        elif self.kind == "MAX_BITS":
            value = values[0]
            maximum = int(self.arguments["max_bits"])
            ok = isinstance(value, int) and not isinstance(value, bool) and abs(value).bit_length() <= maximum
        elif self.kind == "ENUM":
            allowed = self.arguments.get("allowed")
            ok = isinstance(allowed, list) and any(value == values[0] for value in allowed)
        elif self.kind == "NONZERO":
            ok = values[0] != 0
        elif self.kind == "EQUAL":
            ok = values[0] == values[1]
        elif self.kind == "NOT_EQUAL":
            ok = values[0] != values[1]
        elif self.kind == "ORDERED_LE":
            try:
                ok = values[0] <= values[1]
            except TypeError:
                ok = False
        elif self.kind == "LENGTH_RANGE":
            minimum = int(self.arguments.get("minimum", 0))
            maximum = self.arguments.get("maximum")
            try:
                length = len(values[0])
            except TypeError:
                length = -1
            ok = length >= minimum and (maximum is None or length <= int(maximum))
        elif self.kind == "SUM_MAX_BITS":
            maximum = int(self.arguments["max_bits"])
            ok = all(isinstance(value, int) and not isinstance(value, bool) for value in values)
            if ok:
                ok = abs(sum(values)).bit_length() <= maximum
        if not ok:
            raise Pass213ParametricValidationError(
                f"PASS213_PARAMETRIC_CONSTRAINT_FAILED:{self.constraint_id}"
            )
        witness_payload = {
            "constraint": self.to_mapping(),
            "dependency_values": {
                path: _get_path(candidate, path) for path in self.dependencies
            },
            "result": True,
        }
        return hash216("parametric-constraint-witness", canonical_bytes(witness_payload))


def _validate_candidate_shape(
    candidate: Mapping[str, Any],
    field_specs: Sequence[ParametricFieldSpec],
) -> None:
    operands, context = _candidate_sections(candidate)
    expected_operands = {
        spec.path.split(".", 1)[1]
        for spec in field_specs if spec.path.startswith("operands.")
    }
    expected_context = {
        spec.path.split(".", 1)[1]
        for spec in field_specs if spec.path.startswith("context.")
    }
    if set(operands) != expected_operands or set(context) != expected_context:
        raise Pass213ParametricValidationError(
            "PASS213_PARAMETRIC_CANDIDATE_FIELD_SET_INVALID"
        )
    for spec in field_specs:
        _validate_value_type(_get_path(candidate, spec.path), spec.value_type, spec.path)
    canonical_bytes(candidate)


@dataclass(frozen=True)
class ParametricROMTemplate:
    template_id: str
    base_entry_hash216: str
    operation_id: str
    field_specs: tuple[ParametricFieldSpec, ...]
    baseline_candidate: Mapping[str, Any]
    constraints: tuple[ParametricConstraint, ...]
    baseline_constraint_witnesses: Mapping[str, str]
    template_hash216: str = ""

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "template_id": self.template_id,
            "base_entry_hash216": self.base_entry_hash216,
            "operation_id": self.operation_id,
            "field_specs": [spec.to_mapping() for spec in self.field_specs],
            "baseline_candidate": self.baseline_candidate,
            "constraints": [constraint.to_mapping() for constraint in self.constraints],
            "baseline_constraint_witnesses": dict(self.baseline_constraint_witnesses),
        }

    def to_mapping(self) -> Mapping[str, Any]:
        return {**self.unsigned_payload(), "template_hash216": self.template_hash216}

    @classmethod
    def create(
        cls,
        *,
        template_id: str,
        base_entry_hash216: str,
        operation_id: str,
        field_specs: Sequence[ParametricFieldSpec],
        baseline_candidate: Mapping[str, Any],
        constraints: Sequence[ParametricConstraint],
    ) -> "ParametricROMTemplate":
        provisional = cls(
            template_id=template_id,
            base_entry_hash216=base_entry_hash216,
            operation_id=operation_id,
            field_specs=tuple(field_specs),
            baseline_candidate=baseline_candidate,
            constraints=tuple(constraints),
            baseline_constraint_witnesses={},
        )
        provisional._validate_structure(require_witnesses=False)
        witnesses = {
            constraint.constraint_id: constraint.evaluate(baseline_candidate)
            for constraint in provisional.constraints
        }
        with_witnesses = cls(
            template_id=template_id,
            base_entry_hash216=base_entry_hash216,
            operation_id=operation_id,
            field_specs=tuple(field_specs),
            baseline_candidate=baseline_candidate,
            constraints=tuple(constraints),
            baseline_constraint_witnesses=witnesses,
        )
        return cls(
            template_id=template_id,
            base_entry_hash216=base_entry_hash216,
            operation_id=operation_id,
            field_specs=tuple(field_specs),
            baseline_candidate=baseline_candidate,
            constraints=tuple(constraints),
            baseline_constraint_witnesses=witnesses,
            template_hash216=hash216(
                "parametric-rom-template",
                canonical_bytes(with_witnesses.unsigned_payload()),
            ),
        )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ParametricROMTemplate":
        return cls(
            template_id=str(value["template_id"]),
            base_entry_hash216=str(value["base_entry_hash216"]),
            operation_id=str(value["operation_id"]),
            field_specs=tuple(
                ParametricFieldSpec.from_mapping(item) for item in value["field_specs"]
            ),
            baseline_candidate=dict(value["baseline_candidate"]),
            constraints=tuple(
                ParametricConstraint.from_mapping(item) for item in value["constraints"]
            ),
            baseline_constraint_witnesses=dict(value["baseline_constraint_witnesses"]),
            template_hash216=str(value["template_hash216"]),
        )

    def _validate_structure(self, *, require_witnesses: bool) -> None:
        if not self.template_id or not self.operation_id:
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_TEMPLATE_IDENTITY_INVALID"
            )
        _validate_hash216(self.base_entry_hash216, "PARAMETRIC_BASE_ENTRY_HASH216")
        if not self.field_specs:
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_TEMPLATE_FIELDS_EMPTY"
            )
        paths = [spec.path for spec in self.field_specs]
        if len(paths) != len(set(paths)):
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_FIELD_DUPLICATE"
            )
        for spec in self.field_specs:
            spec.validate()
        _validate_candidate_shape(self.baseline_candidate, self.field_specs)
        constraint_ids = [constraint.constraint_id for constraint in self.constraints]
        if len(constraint_ids) != len(set(constraint_ids)):
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_CONSTRAINT_DUPLICATE"
            )
        field_paths = set(paths)
        for constraint in self.constraints:
            constraint.validate(field_paths)
        if require_witnesses:
            if set(self.baseline_constraint_witnesses) != set(constraint_ids):
                raise Pass213ParametricValidationError(
                    "PASS213_PARAMETRIC_BASELINE_WITNESS_SET_INVALID"
                )
            for constraint in self.constraints:
                expected = constraint.evaluate(self.baseline_candidate)
                if not hmac.compare_digest(
                    str(self.baseline_constraint_witnesses[constraint.constraint_id]),
                    expected,
                ):
                    raise Pass213ParametricValidationError(
                        "PASS213_PARAMETRIC_BASELINE_WITNESS_MISMATCH"
                    )

    def validate(self) -> None:
        self._validate_structure(require_witnesses=True)
        _validate_hash216(self.template_hash216, "PARAMETRIC_TEMPLATE_HASH216")
        expected = hash216(
            "parametric-rom-template",
            canonical_bytes(self.unsigned_payload()),
        )
        if not hmac.compare_digest(self.template_hash216, expected):
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_TEMPLATE_HASH_MISMATCH"
            )


@dataclass(frozen=True)
class ParametricROMAdmission:
    template_hash216: str
    base_entry_hash216: str
    operation_id: str
    candidate: Mapping[str, Any]
    candidate_hash216: str
    changed_paths: tuple[str, ...]
    affected_constraint_ids: tuple[str, ...]
    reused_constraint_ids: tuple[str, ...]
    evaluated_constraint_witnesses: Mapping[str, str]
    reused_constraint_root_hash216: str
    delta_root_hash216: str
    opening_boundary_hash216: str
    genesis_epoch: int
    group_sequence: int
    parent_hash216: str
    vm81_cell_id: int
    operation_slot: int
    g243_control_id: int
    native_dispatch_id: str
    kernel_policy_hash216: str
    vm81_admission_root_hash216: str
    authentication_tag: str

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "template_hash216": self.template_hash216,
            "base_entry_hash216": self.base_entry_hash216,
            "operation_id": self.operation_id,
            "candidate": self.candidate,
            "candidate_hash216": self.candidate_hash216,
            "changed_paths": list(self.changed_paths),
            "affected_constraint_ids": list(self.affected_constraint_ids),
            "reused_constraint_ids": list(self.reused_constraint_ids),
            "evaluated_constraint_witnesses": dict(self.evaluated_constraint_witnesses),
            "reused_constraint_root_hash216": self.reused_constraint_root_hash216,
            "delta_root_hash216": self.delta_root_hash216,
            "opening_boundary_hash216": self.opening_boundary_hash216,
            "genesis_epoch": self.genesis_epoch,
            "group_sequence": self.group_sequence,
            "parent_hash216": self.parent_hash216,
            "vm81_cell_id": self.vm81_cell_id,
            "operation_slot": self.operation_slot,
            "g243_control_id": self.g243_control_id,
            "native_dispatch_id": self.native_dispatch_id,
            "kernel_policy_hash216": self.kernel_policy_hash216,
            "vm81_admission_root_hash216": self.vm81_admission_root_hash216,
        }

    def to_mapping(self) -> Mapping[str, Any]:
        return {**self.unsigned_payload(), "authentication_tag": self.authentication_tag}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ParametricROMAdmission":
        return cls(
            template_hash216=str(value["template_hash216"]),
            base_entry_hash216=str(value["base_entry_hash216"]),
            operation_id=str(value["operation_id"]),
            candidate=dict(value["candidate"]),
            candidate_hash216=str(value["candidate_hash216"]),
            changed_paths=tuple(str(item) for item in value["changed_paths"]),
            affected_constraint_ids=tuple(str(item) for item in value["affected_constraint_ids"]),
            reused_constraint_ids=tuple(str(item) for item in value["reused_constraint_ids"]),
            evaluated_constraint_witnesses=dict(value["evaluated_constraint_witnesses"]),
            reused_constraint_root_hash216=str(value["reused_constraint_root_hash216"]),
            delta_root_hash216=str(value["delta_root_hash216"]),
            opening_boundary_hash216=str(value["opening_boundary_hash216"]),
            genesis_epoch=int(value["genesis_epoch"]),
            group_sequence=int(value["group_sequence"]),
            parent_hash216=str(value["parent_hash216"]),
            vm81_cell_id=int(value["vm81_cell_id"]),
            operation_slot=int(value["operation_slot"]),
            g243_control_id=int(value["g243_control_id"]),
            native_dispatch_id=str(value["native_dispatch_id"]),
            kernel_policy_hash216=str(value["kernel_policy_hash216"]),
            vm81_admission_root_hash216=str(value["vm81_admission_root_hash216"]),
            authentication_tag=str(value["authentication_tag"]),
        )

    def validate(
        self,
        validation_key: bytes,
        template: ParametricROMTemplate,
        base_entry: CompiledROMEntry,
        opening_boundary: TimestampBoundary,
    ) -> None:
        expected = create_parametric_admission(
            template=template,
            base_entry=base_entry,
            candidate=self.candidate,
            opening_boundary=opening_boundary,
            validation_key=validation_key,
        )
        if canonical_bytes(self.to_mapping()) != canonical_bytes(expected.to_mapping()):
            raise Pass213ParametricValidationError(
                "PASS213_PARAMETRIC_ADMISSION_MISMATCH"
            )


def serialize_parametric_template(template: ParametricROMTemplate) -> bytes:
    template.validate()
    return canonical_bytes({"schema": "HHS_PASS_213_PARAMETRIC_TEMPLATE_V1", **template.to_mapping()})


def deserialize_parametric_template(payload: bytes) -> ParametricROMTemplate:
    import json
    try:
        value = json.loads(bytes(payload).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Pass213ParametricValidationError(
            "PASS213_PARAMETRIC_TEMPLATE_DESERIALIZATION_FAILED"
        ) from exc
    if value.pop("schema", None) != "HHS_PASS_213_PARAMETRIC_TEMPLATE_V1":
        raise Pass213ParametricValidationError(
            "PASS213_PARAMETRIC_TEMPLATE_SCHEMA_INVALID"
        )
    template = ParametricROMTemplate.from_mapping(value)
    template.validate()
    return template


def serialize_parametric_admission(admission: ParametricROMAdmission) -> bytes:
    return canonical_bytes({"schema": "HHS_PASS_213_PARAMETRIC_ADMISSION_V1", **admission.to_mapping()})


def deserialize_parametric_admission(payload: bytes) -> ParametricROMAdmission:
    import json
    try:
        value = json.loads(bytes(payload).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Pass213ParametricValidationError(
            "PASS213_PARAMETRIC_ADMISSION_DESERIALIZATION_FAILED"
        ) from exc
    if value.pop("schema", None) != "HHS_PASS_213_PARAMETRIC_ADMISSION_V1":
        raise Pass213ParametricValidationError(
            "PASS213_PARAMETRIC_ADMISSION_SCHEMA_INVALID"
        )
    return ParametricROMAdmission.from_mapping(value)


def create_parametric_admission(
    *,
    template: ParametricROMTemplate,
    base_entry: CompiledROMEntry,
    candidate: Mapping[str, Any],
    opening_boundary: TimestampBoundary,
    validation_key: bytes,
) -> ParametricROMAdmission:
    template.validate()
    base_entry.validate()
    opening_boundary.validate()
    if opening_boundary.kind != "open":
        raise Pass213ParametricValidationError(
            "PASS213_PARAMETRIC_OPENING_BOUNDARY_REQUIRED"
        )
    if (
        base_entry.entry_hash216 != template.base_entry_hash216
        or base_entry.operation_id != template.operation_id
    ):
        raise Pass213ParametricValidationError(
            "PASS213_PARAMETRIC_BASE_ENTRY_MISMATCH"
        )
    _validate_candidate_shape(candidate, template.field_specs)

    changed: list[str] = []
    mutable_by_path = {spec.path: spec.mutable for spec in template.field_specs}
    for spec in template.field_specs:
        before = _get_path(template.baseline_candidate, spec.path)
        after = _get_path(candidate, spec.path)
        if canonical_bytes(before) != canonical_bytes(after):
            if not mutable_by_path[spec.path]:
                raise Pass213ParametricValidationError(
                    f"PASS213_PARAMETRIC_IMMUTABLE_FIELD_CHANGED:{spec.path}"
                )
            changed.append(spec.path)
    changed_paths = tuple(sorted(changed))
    affected_constraints = tuple(sorted(
        constraint.constraint_id
        for constraint in template.constraints
        if set(constraint.dependencies) & set(changed_paths)
    ))
    reused_constraints = tuple(sorted(
        constraint.constraint_id
        for constraint in template.constraints
        if constraint.constraint_id not in affected_constraints
    ))
    evaluated = {
        constraint.constraint_id: constraint.evaluate(candidate)
        for constraint in template.constraints
        if constraint.constraint_id in affected_constraints
    }
    reused_witnesses = {
        constraint_id: template.baseline_constraint_witnesses[constraint_id]
        for constraint_id in reused_constraints
    }
    reused_root = hash216(
        "parametric-reused-constraint-root",
        canonical_bytes(reused_witnesses),
    )
    candidate_hash = hash216("parametric-candidate", canonical_bytes(candidate))
    delta_payload = {
        "template_hash216": template.template_hash216,
        "base_entry_hash216": base_entry.entry_hash216,
        "candidate_hash216": candidate_hash,
        "changed": {
            path: {
                "before_hash216": hash216(
                    "parametric-field-before", canonical_bytes(_get_path(template.baseline_candidate, path))
                ),
                "after": _get_path(candidate, path),
            }
            for path in changed_paths
        },
        "affected_constraint_ids": list(affected_constraints),
        "reused_constraint_ids": list(reused_constraints),
        "evaluated_constraint_witnesses": evaluated,
        "reused_constraint_root_hash216": reused_root,
    }
    delta_root = hash216("parametric-delta", canonical_bytes(delta_payload))
    admission_payload = {
        "template_hash216": template.template_hash216,
        "base_entry_hash216": base_entry.entry_hash216,
        "operation_id": base_entry.operation_id,
        "candidate": candidate,
        "candidate_hash216": candidate_hash,
        "changed_paths": list(changed_paths),
        "affected_constraint_ids": list(affected_constraints),
        "reused_constraint_ids": list(reused_constraints),
        "evaluated_constraint_witnesses": evaluated,
        "reused_constraint_root_hash216": reused_root,
        "delta_root_hash216": delta_root,
        "opening_boundary_hash216": opening_boundary.boundary_hash216,
        "genesis_epoch": opening_boundary.genesis_epoch,
        "group_sequence": opening_boundary.group_sequence,
        "parent_hash216": opening_boundary.parent_hash216,
        "vm81_cell_id": base_entry.vm81_cell_id,
        "operation_slot": base_entry.operation_slot,
        "g243_control_id": base_entry.g243_control_id,
        "native_dispatch_id": base_entry.native_dispatch_id,
        "kernel_policy_hash216": base_entry.kernel_policy_hash216,
    }
    vm81_root = hash216(
        "parametric-vm81-admission",
        canonical_bytes(admission_payload),
    )
    complete = {**admission_payload, "vm81_admission_root_hash216": vm81_root}
    tag = _authenticate(validation_key, "PARAMETRIC-VM81-ADMISSION", complete)
    return ParametricROMAdmission(
        template_hash216=template.template_hash216,
        base_entry_hash216=base_entry.entry_hash216,
        operation_id=base_entry.operation_id,
        candidate=candidate,
        candidate_hash216=candidate_hash,
        changed_paths=changed_paths,
        affected_constraint_ids=affected_constraints,
        reused_constraint_ids=reused_constraints,
        evaluated_constraint_witnesses=evaluated,
        reused_constraint_root_hash216=reused_root,
        delta_root_hash216=delta_root,
        opening_boundary_hash216=opening_boundary.boundary_hash216,
        genesis_epoch=opening_boundary.genesis_epoch,
        group_sequence=opening_boundary.group_sequence,
        parent_hash216=opening_boundary.parent_hash216,
        vm81_cell_id=base_entry.vm81_cell_id,
        operation_slot=base_entry.operation_slot,
        g243_control_id=base_entry.g243_control_id,
        native_dispatch_id=base_entry.native_dispatch_id,
        kernel_policy_hash216=base_entry.kernel_policy_hash216,
        vm81_admission_root_hash216=vm81_root,
        authentication_tag=tag,
    )


@dataclass(frozen=True)
class ProtectedParametricTemplateRecord:
    template_id: str
    template_hash216: str
    base_entry_hash216: str
    operation_id: str
    arena_id_hash216: str
    payload_length: int
    final_memory_receipt_hash216: str


@dataclass(frozen=True)
class ProtectedParametricAdmissionRecord:
    vm81_admission_root_hash216: str
    template_hash216: str
    base_entry_hash216: str
    candidate_hash216: str
    delta_root_hash216: str
    changed_path_count: int
    affected_constraint_count: int
    arena_id_hash216: str
    payload_length: int
    final_memory_receipt_hash216: str


class NativeParametricCompiledROMStore:
    """Sealed native template and transient VM81 admission store."""

    def __init__(
        self,
        *,
        base_store: NativeProtectedCompiledROMStore,
        library_path: str | Path,
        validation_key: bytes,
        memory_root_key: bytes,
        owner_id: str,
    ) -> None:
        if not isinstance(validation_key, bytes) or len(validation_key) < 32:
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_VALIDATION_KEY_TOO_SHORT")
        if not isinstance(memory_root_key, bytes) or len(memory_root_key) < 32:
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_MEMORY_KEY_TOO_SHORT")
        if not owner_id:
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_OWNER_INVALID")
        self._base_store = base_store
        self._library_path = str(Path(library_path))
        self._validation_key = validation_key
        self._memory_root_key = memory_root_key
        self._owner_id = owner_id
        self._allocation_sequence = 0
        self._template_arenas: dict[str, NativeSecureArena] = {}
        self._template_records: dict[str, ProtectedParametricTemplateRecord] = {}
        self._template_id_index: dict[str, str] = {}
        self._admission_arenas: dict[str, NativeSecureArena] = {}
        self._admission_records: dict[str, ProtectedParametricAdmissionRecord] = {}
        self._closed = False

    def _require_open(self) -> None:
        if self._closed:
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_STORE_CLOSED")

    def _new_arena(self, payload: bytes, identity: str) -> NativeSecureArena:
        self._allocation_sequence += 1
        arena = NativeSecureArena(
            library_path=self._library_path,
            requested_size=len(payload),
            owner_id=f"{self._owner_id}:{identity}",
            root_key=self._memory_root_key,
            allocation_sequence=self._allocation_sequence,
        )
        arena.write(payload)
        arena.seal()
        return arena

    def register_template(
        self,
        template: ParametricROMTemplate,
    ) -> ProtectedParametricTemplateRecord:
        self._require_open()
        if not isinstance(template, ParametricROMTemplate):
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_TEMPLATE_REQUIRED")
        template.validate()
        base_entry = self._base_store.lookup_hash216(template.base_entry_hash216)
        if base_entry.operation_id != template.operation_id:
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_TEMPLATE_BASE_OPERATION_MISMATCH")
        existing_hash = self._template_id_index.get(template.template_id)
        if existing_hash is not None:
            if existing_hash != template.template_hash216:
                raise Pass213SecureMemoryError("PASS213_PARAMETRIC_TEMPLATE_ID_CONFLICT")
            return self._template_records[existing_hash]
        payload = serialize_parametric_template(template)
        arena = self._new_arena(payload, f"template:{template.template_hash216}")
        try:
            recovered = deserialize_parametric_template(
                arena.read_internal(offset=0, length=len(payload))
            )
            if recovered.template_hash216 != template.template_hash216:
                raise Pass213SecureMemoryError("PASS213_PARAMETRIC_TEMPLATE_POST_WRITE_MISMATCH")
            record = ProtectedParametricTemplateRecord(
                template_id=template.template_id,
                template_hash216=template.template_hash216,
                base_entry_hash216=template.base_entry_hash216,
                operation_id=template.operation_id,
                arena_id_hash216=arena.arena_id_hash216,
                payload_length=len(payload),
                final_memory_receipt_hash216=arena.receipts[-1].receipt_hash216,
            )
            self._template_arenas[template.template_hash216] = arena
            self._template_records[template.template_hash216] = record
            self._template_id_index[template.template_id] = template.template_hash216
            return record
        except Exception:
            arena.close()
            raise

    def _load_template(self, template_id: str) -> ParametricROMTemplate:
        try:
            template_hash = self._template_id_index[template_id]
            record = self._template_records[template_hash]
            arena = self._template_arenas[template_hash]
        except KeyError as exc:
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_TEMPLATE_NOT_FOUND") from exc
        template = deserialize_parametric_template(
            arena.read_internal(offset=0, length=record.payload_length)
        )
        if template.template_hash216 != record.template_hash216:
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_TEMPLATE_LOOKUP_MISMATCH")
        return template

    def admit_candidate(
        self,
        *,
        template_id: str,
        candidate: Mapping[str, Any],
        opening_boundary: TimestampBoundary,
    ) -> ProtectedParametricAdmissionRecord:
        self._require_open()
        template = self._load_template(template_id)
        base_entry = self._base_store.lookup_hash216(template.base_entry_hash216)
        admission = create_parametric_admission(
            template=template,
            base_entry=base_entry,
            candidate=candidate,
            opening_boundary=opening_boundary,
            validation_key=self._validation_key,
        )
        existing = self._admission_records.get(admission.vm81_admission_root_hash216)
        if existing is not None:
            return existing
        payload = serialize_parametric_admission(admission)
        arena = self._new_arena(payload, f"admission:{admission.vm81_admission_root_hash216}")
        try:
            recovered = deserialize_parametric_admission(
                arena.read_internal(offset=0, length=len(payload))
            )
            recovered.validate(
                self._validation_key,
                template,
                base_entry,
                opening_boundary,
            )
            record = ProtectedParametricAdmissionRecord(
                vm81_admission_root_hash216=admission.vm81_admission_root_hash216,
                template_hash216=admission.template_hash216,
                base_entry_hash216=admission.base_entry_hash216,
                candidate_hash216=admission.candidate_hash216,
                delta_root_hash216=admission.delta_root_hash216,
                changed_path_count=len(admission.changed_paths),
                affected_constraint_count=len(admission.affected_constraint_ids),
                arena_id_hash216=arena.arena_id_hash216,
                payload_length=len(payload),
                final_memory_receipt_hash216=arena.receipts[-1].receipt_hash216,
            )
            self._admission_arenas[admission.vm81_admission_root_hash216] = arena
            self._admission_records[admission.vm81_admission_root_hash216] = record
            return record
        except Exception:
            arena.close()
            raise

    def lookup_admission(
        self,
        vm81_admission_root_hash216: str,
        opening_boundary: TimestampBoundary,
    ) -> ParametricROMAdmission:
        self._require_open()
        try:
            record = self._admission_records[vm81_admission_root_hash216]
            arena = self._admission_arenas[vm81_admission_root_hash216]
        except KeyError as exc:
            raise Pass213SecureMemoryError("PASS213_PARAMETRIC_ADMISSION_NOT_FOUND") from exc
        template = next(
            self._load_template(template_id)
            for template_id, template_hash in self._template_id_index.items()
            if template_hash == record.template_hash216
        )
        base_entry = self._base_store.lookup_hash216(record.base_entry_hash216)
        admission = deserialize_parametric_admission(
            arena.read_internal(offset=0, length=record.payload_length)
        )
        admission.validate(
            self._validation_key,
            template,
            base_entry,
            opening_boundary,
        )
        return admission

    def inventory_root(self) -> str:
        self._require_open()
        payload = {
            "runtime_classification": RUNTIME_CLASSIFICATION,
            "templates": [record.__dict__ for _, record in sorted(self._template_records.items())],
            "admissions": [record.__dict__ for _, record in sorted(self._admission_records.items())],
        }
        return hash216("parametric-native-inventory", canonical_bytes(payload))

    def close(self) -> tuple[SecureMemoryReceipt, ...]:
        if self._closed:
            return ()
        receipts: list[SecureMemoryReceipt] = []
        for arenas in (self._admission_arenas, self._template_arenas):
            for identity in sorted(arenas):
                receipt = arenas[identity].close()
                if receipt is not None:
                    receipts.append(receipt)
            arenas.clear()
        self._template_records.clear()
        self._template_id_index.clear()
        self._admission_records.clear()
        self._closed = True
        return tuple(receipts)

    def __len__(self) -> int:
        return len(self._admission_records)

    def __enter__(self) -> "NativeParametricCompiledROMStore":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


__all__ = [
    "ITERATION",
    "RUNTIME_CLASSIFICATION",
    "Pass213ParametricValidationError",
    "ParametricFieldSpec",
    "ParametricConstraint",
    "ParametricROMTemplate",
    "ParametricROMAdmission",
    "ProtectedParametricTemplateRecord",
    "ProtectedParametricAdmissionRecord",
    "NativeParametricCompiledROMStore",
    "serialize_parametric_template",
    "deserialize_parametric_template",
    "serialize_parametric_admission",
    "deserialize_parametric_admission",
    "create_parametric_admission",
]
