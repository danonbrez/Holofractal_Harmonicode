"""Manifest-backed registry for mandatory Pass 219 optimization reachability.

The repository's optimization-generalization manifests are the authoritative
machine-readable statement of which compatible targets are proven safe and
beneficial.  This registry validates every such manifest with the inherited
multimodal generalization classifier and exposes all ``GENERALIZE_REQUIRED``
targets to the Lane 5 latency/composition agent.

A malformed manifest or declared/derived coverage mismatch fails closed.  A
``NOT_APPLICABLE`` or ``VALIDATION_REQUIRED`` decision is preserved as typed
metadata and is never silently promoted to a mandatory execution path.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.multimodal_optimization_generalization import (
    OptimizationGeneralizationError,
    canonical_json,
    validate_manifest,
)

SCHEMA = "HHS_PASS219_LANE5_MANDATORY_OPTIMIZATION_REGISTRY_V1"
MANIFEST_SCHEMA = "HHS_PASS_219_OPTIMIZATION_GENERALIZATION_MANIFEST_V1"


class Lane5MandatoryOptimizationRegistryError(RuntimeError):
    pass


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def manifest_root(root: str | Path | None = None) -> Path:
    base = Path(root).resolve() if root is not None else repository_root()
    return base / "contracts" / "pass219" / "optimization_generalization"


def build_mandatory_optimization_registry(
    root: str | Path | None = None,
) -> dict[str, Any]:
    directory = manifest_root(root)
    if not directory.is_dir():
        raise Lane5MandatoryOptimizationRegistryError(
            f"LANE5_OPTIMIZATION_MANIFEST_ROOT_MISSING:{directory}"
        )

    records: list[dict[str, Any]] = []
    generalize_pairs: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for path in sorted(directory.glob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise Lane5MandatoryOptimizationRegistryError(
                f"LANE5_OPTIMIZATION_MANIFEST_UNREADABLE:{path.name}:{exc}"
            ) from exc

        # The directory may retain non-generalization support JSON in the
        # future. Only the canonical schema participates in this registry.
        if raw.get("schema") != MANIFEST_SCHEMA:
            continue

        try:
            validated = validate_manifest(raw)
        except (OptimizationGeneralizationError, KeyError, TypeError) as exc:
            raise Lane5MandatoryOptimizationRegistryError(
                f"LANE5_OPTIMIZATION_MANIFEST_INVALID:{path.name}:{exc}"
            ) from exc

        optimization_id = str(validated["optimization_id"])
        if not optimization_id or optimization_id in seen_ids:
            raise Lane5MandatoryOptimizationRegistryError(
                f"LANE5_OPTIMIZATION_ID_DUPLICATE_OR_EMPTY:{optimization_id}"
            )
        seen_ids.add(optimization_id)

        required_targets = tuple(str(v) for v in validated["generalize_required"])
        validation_targets = tuple(str(v) for v in validated["validation_required"])
        exception_targets = tuple(str(v) for v in validated["local_exceptions"])
        manifest_digest = sha256(canonical_json(raw).encode("utf-8")).hexdigest()

        for target in required_targets:
            generalize_pairs.append(
                {"optimization_id": optimization_id, "target": target}
            )

        records.append(
            {
                "path": path.relative_to(repository_root()).as_posix()
                if root is None
                else path.name,
                "optimization_id": optimization_id,
                "generalize_required": list(required_targets),
                "validation_required": list(validation_targets),
                "local_exceptions": list(exception_targets),
                "manifest_sha256": manifest_digest,
            }
        )

    if not records:
        raise Lane5MandatoryOptimizationRegistryError(
            "LANE5_OPTIMIZATION_GENERALIZATION_MANIFESTS_EMPTY"
        )

    generalize_pairs.sort(key=lambda row: (row["optimization_id"], row["target"]))
    records.sort(key=lambda row: row["optimization_id"])
    snapshot = {
        "schema": SCHEMA,
        "manifest_schema": MANIFEST_SCHEMA,
        "manifest_count": len(records),
        "generalize_required_count": len(generalize_pairs),
        "generalize_required": generalize_pairs,
        "manifests": records,
        "typed_applicability_preserved": True,
        "unvalidated_targets_are_not_promoted": True,
        "bounded_local_exceptions_preserved": True,
        "canonical_authority_granted": False,
    }
    snapshot["registry_sha256"] = sha256(
        canonical_json(snapshot).encode("utf-8")
    ).hexdigest()
    return snapshot


__all__ = [
    "Lane5MandatoryOptimizationRegistryError",
    "MANIFEST_SCHEMA",
    "SCHEMA",
    "build_mandatory_optimization_registry",
    "manifest_root",
    "repository_root",
]
