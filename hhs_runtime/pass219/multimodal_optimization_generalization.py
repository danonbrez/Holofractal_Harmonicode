"""Pass 219 universal multimodal optimization generalization classifier."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Iterable, Mapping, Sequence

CONTRACT_ID = "HHS-P219-MULTIMODAL-OPTIMIZATION-GENERALIZATION"
DESCRIPTOR_SCHEMA_ID = "HHS_PASS_187_OBJECT_DESCRIPTOR_V1"

NOT_APPLICABLE = "NOT_APPLICABLE"
VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
GENERALIZE_REQUIRED = "GENERALIZE_REQUIRED"
LOCAL_EXCEPTION_ALLOWED = "LOCAL_EXCEPTION_ALLOWED"

BOUNDED_EXCEPTIONS = frozenset({
    "UNSAFE",
    "NO_MEANINGFUL_BENEFIT",
    "CONTEXT_SPECIFIC",
    "METADATA_INCOMPATIBLE",
    "OBJECT_INCOMPATIBLE",
    "INTERFACE_ONLY",
    "INGRESS_ONLY",
    "EGRESS_ONLY",
    "EXPLICIT_ONE_OFF",
})


class OptimizationGeneralizationError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise OptimizationGeneralizationError(f"FLOAT_CANONICAL_EVIDENCE_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def _port_types(descriptor: Mapping[str, Any]) -> frozenset[str]:
    values: set[str] = set()
    for kind in ("inputs", "outputs"):
        for port in descriptor.get(kind, []):
            if isinstance(port, Mapping) and isinstance(port.get("type"), str):
                values.add(port["type"])
    return frozenset(values)


def _compatible_object_class(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    optimization: Mapping[str, Any],
) -> bool:
    allowed = tuple(str(v) for v in optimization.get("compatible_object_classes", []))
    if allowed:
        return source.get("object_class") in allowed and target.get("object_class") in allowed
    return source.get("object_class") == target.get("object_class")


def compatibility(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    optimization: Mapping[str, Any],
) -> dict[str, Any]:
    _reject_float(source)
    _reject_float(target)
    _reject_float(optimization)

    source_schema = source.get("descriptor_schema_id", DESCRIPTOR_SCHEMA_ID)
    target_schema = target.get("descriptor_schema_id", DESCRIPTOR_SCHEMA_ID)
    if source_schema != target_schema:
        return {"compatible": False, "reason": "METADATA_INCOMPATIBLE"}

    if source.get("runtime_authority") != target.get("runtime_authority"):
        return {"compatible": False, "reason": "OBJECT_INCOMPATIBLE"}

    if source.get("exactness_domain", "EXACT_SYMBOLIC") != target.get(
        "exactness_domain", "EXACT_SYMBOLIC"
    ):
        return {"compatible": False, "reason": "OBJECT_INCOMPATIBLE"}

    if not _compatible_object_class(source, target, optimization):
        return {"compatible": False, "reason": "OBJECT_INCOMPATIBLE"}

    required_operations = set(str(v) for v in optimization.get("required_operations", []))
    if not required_operations.issubset(set(str(v) for v in target.get("operations", []))):
        return {"compatible": False, "reason": "OBJECT_INCOMPATIBLE"}

    required_ports = set(str(v) for v in optimization.get("required_port_types", []))
    if not required_ports.issubset(_port_types(target)):
        return {"compatible": False, "reason": "OBJECT_INCOMPATIBLE"}

    return {
        "compatible": True,
        "reason": "COMPATIBLE",
        "cross_modality": set(source.get("modality_set", [])) != set(target.get("modality_set", [])),
    }


def classify_target(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    optimization: Mapping[str, Any],
    evidence: Mapping[str, Any] | None,
) -> dict[str, Any]:
    compat = compatibility(source, target, optimization)
    target_id = str(target.get("logical_object_id", "UNKNOWN"))

    if not compat["compatible"]:
        return {
            "target": target_id,
            "classification": NOT_APPLICABLE,
            "reason": compat["reason"],
            "compatible": False,
        }

    row = dict(evidence or {})
    _reject_float(row)

    exception = row.get("bounded_exception")
    if exception is not None:
        if exception not in BOUNDED_EXCEPTIONS:
            raise OptimizationGeneralizationError(f"UNBOUNDED_LOCAL_EXCEPTION:{target_id}")
        if not row.get("exception_evidence"):
            raise OptimizationGeneralizationError(f"LOCAL_EXCEPTION_EVIDENCE_REQUIRED:{target_id}")
        if exception == "UNSAFE":
            if not row.get("validation_executed") or row.get("safe") is not False:
                raise OptimizationGeneralizationError(f"UNSAFE_EXCEPTION_REQUIRES_VALIDATION:{target_id}")
        if exception == "NO_MEANINGFUL_BENEFIT":
            if (
                not row.get("validation_executed")
                or row.get("safe") is not True
                or row.get("benefit") is not False
            ):
                raise OptimizationGeneralizationError(
                    f"NO_BENEFIT_EXCEPTION_REQUIRES_VALIDATION:{target_id}"
                )
        return {
            "target": target_id,
            "classification": LOCAL_EXCEPTION_ALLOWED,
            "reason": exception,
            "compatible": True,
        }

    if not row.get("validation_executed"):
        return {
            "target": target_id,
            "classification": VALIDATION_REQUIRED,
            "reason": "COMPATIBLE_TARGET_NOT_YET_VALIDATED",
            "compatible": True,
        }

    if row.get("safe") is True and row.get("benefit") is True:
        return {
            "target": target_id,
            "classification": GENERALIZE_REQUIRED,
            "reason": "SAFE_BENEFICIAL_COMPATIBLE_TARGET",
            "compatible": True,
        }

    raise OptimizationGeneralizationError(
        f"COMPATIBLE_NEGATIVE_RESULT_REQUIRES_BOUNDED_EXCEPTION:{target_id}"
    )


def generalize_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(manifest)
    source = manifest["source"]
    optimization = manifest["optimization"]
    evidence_by_target = {
        str(row["logical_object_id"]): row
        for row in manifest.get("target_evidence", [])
    }
    decisions = [
        classify_target(
            source,
            target,
            optimization,
            evidence_by_target.get(str(target.get("logical_object_id"))),
        )
        for target in manifest.get("targets", [])
    ]
    return {
        "contract_id": CONTRACT_ID,
        "optimization_id": optimization["optimization_id"],
        "decisions": decisions,
        "generalize_required": sorted(
            row["target"] for row in decisions if row["classification"] == GENERALIZE_REQUIRED
        ),
        "validation_required": sorted(
            row["target"] for row in decisions if row["classification"] == VALIDATION_REQUIRED
        ),
        "local_exceptions": sorted(
            row["target"] for row in decisions if row["classification"] == LOCAL_EXCEPTION_ALLOWED
        ),
    }


def validate_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if manifest.get("schema") != "HHS_PASS_219_OPTIMIZATION_GENERALIZATION_MANIFEST_V1":
        raise OptimizationGeneralizationError("MANIFEST_SCHEMA_MISMATCH")
    if manifest.get("local_only") is True and not manifest.get("target_evidence"):
        raise OptimizationGeneralizationError("LOCAL_ONLY_WITHOUT_EVIDENCE_FORBIDDEN")
    result = generalize_manifest(manifest)
    declared = sorted(str(v) for v in manifest.get("declared_generalize_required", []))
    if declared != result["generalize_required"]:
        raise OptimizationGeneralizationError(
            f"GENERALIZATION_COVERAGE_DRIFT:{declared}!={result['generalize_required']}"
        )
    return result


def canonical_json(value: Any) -> str:
    _reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
