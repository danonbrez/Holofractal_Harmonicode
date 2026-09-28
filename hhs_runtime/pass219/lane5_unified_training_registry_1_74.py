"""Repository binding validator for the Pass 219 Lane 5 1.74 unified training registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "training_specimens/HHS_LANE5_UNIFIED_TRAINING_REGISTRY_1_74.json"
SCHEMA = "HHS_PASS219_LANE5_UNIFIED_TRAINING_REGISTRY_1_74"

EXPECTED_METHOD_IDS = (
    "REALTIME_HASH216",
    "WOLFRAM_FORMALIZATION",
    "EXTERNAL_LIBRARY_RECONSTRUCTION",
    "PALINDROMIC_ROUND_TRIP",
    "PULL_REQUEST_HYDRATION",
    "MULTIMODAL_INGRESS",
    "LINGUISTIC_OPERATOR",
    "ETHICAL_TEXT",
    "RNA_CELL_WALL_ALIGNMENT",
    "CURRICULUM",
    "CALLABLE_CORPUS",
    "CANONICAL_CORPUS",
    "WORKLOAD_CALIBRATION",
    "ANTI_FORGETTING_REPLAY",
    "AB_HYDRATION_CALIBRATION",
    "PROJECTION_CORPUS",
    "INVERSE_RENDER_HYDRATION",
    "REPOSITORY_HYDRATION",
    "BOUNDED_TOKEN_GENERALIZATION",
)


class UnifiedTrainingRegistryError(ValueError):
    pass


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != SCHEMA:
        raise UnifiedTrainingRegistryError("registry schema mismatch")
    return value


def validate_registry(
    registry: Mapping[str, Any] | None = None,
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    value = dict(registry or load_registry())
    methods = list(value.get("methods") or [])

    if value.get("method_count") != len(EXPECTED_METHOD_IDS):
        raise UnifiedTrainingRegistryError("method_count mismatch")
    if len(methods) != len(EXPECTED_METHOD_IDS):
        raise UnifiedTrainingRegistryError("methods length mismatch")

    observed_ids = tuple(str(item.get("method_id")) for item in methods)
    if observed_ids != EXPECTED_METHOD_IDS:
        raise UnifiedTrainingRegistryError("method ordering/id mismatch")

    observed_modes = tuple(int(item.get("mode", -1)) for item in methods)
    if observed_modes != tuple(range(1, len(EXPECTED_METHOD_IDS) + 1)):
        raise UnifiedTrainingRegistryError("mode numbering mismatch")

    if len(set(observed_ids)) != len(observed_ids):
        raise UnifiedTrainingRegistryError("duplicate method_id")
    if len(set(observed_modes)) != len(observed_modes):
        raise UnifiedTrainingRegistryError("duplicate mode")

    missing_producers: list[str] = []
    language_required: list[str] = []
    supervisor_count = 0

    for item in methods:
        producer = str(item.get("producer") or "")
        if not producer or not (root / producer).is_file():
            missing_producers.append(producer or f"<missing:{item.get('method_id')}>")

        policy = str(item.get("natural_language_policy") or "")
        if policy not in {"REQUIRED", "CONTENT_SENSITIVE"}:
            raise UnifiedTrainingRegistryError(
                f"invalid natural_language_policy:{item.get('method_id')}"
            )
        if policy == "REQUIRED":
            language_required.append(str(item["method_id"]))
        if item.get("ethical_text_supervisor") is True:
            supervisor_count += 1
            if item.get("method_id") != "ETHICAL_TEXT":
                raise UnifiedTrainingRegistryError("unexpected ethical supervisor")

    if missing_producers:
        raise UnifiedTrainingRegistryError(
            "missing producer paths:" + ",".join(sorted(missing_producers))
        )
    if tuple(language_required) != ("LINGUISTIC_OPERATOR", "ETHICAL_TEXT"):
        raise UnifiedTrainingRegistryError("intrinsic language method mismatch")
    if supervisor_count != 1:
        raise UnifiedTrainingRegistryError("ethical supervisor cardinality mismatch")

    supervisor = dict(value.get("natural_language_supervisor") or {})
    if (
        supervisor.get("method_id") != "ETHICAL_TEXT"
        or supervisor.get("required_for_all_natural_language_training") is not True
        or supervisor.get("content_sensitive") is not True
    ):
        raise UnifiedTrainingRegistryError("natural-language supervisor contract mismatch")

    authority = dict(value.get("authority") or {})
    if authority.get("candidate_only") is not True:
        raise UnifiedTrainingRegistryError("candidate-only authority lost")
    for key in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "canonical_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if authority.get(key) is not False:
            raise UnifiedTrainingRegistryError(f"authority escalation:{key}")

    return {
        "schema": SCHEMA + "_VALIDATION_RECEIPT",
        "method_count": len(methods),
        "method_ids": list(observed_ids),
        "producer_count": len({str(item["producer"]) for item in methods}),
        "all_producers_exist": True,
        "intrinsic_natural_language_methods": language_required,
        "ethical_text_supervisor": "ETHICAL_TEXT",
        "candidate_only": True,
    }


def registry_by_method_id(
    registry: Mapping[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    value = dict(registry or load_registry())
    validate_registry(value)
    return {
        str(item["method_id"]): dict(item)
        for item in value["methods"]
    }


__all__ = [
    "EXPECTED_METHOD_IDS",
    "REGISTRY_PATH",
    "SCHEMA",
    "UnifiedTrainingRegistryError",
    "load_registry",
    "registry_by_method_id",
    "validate_registry",
]
