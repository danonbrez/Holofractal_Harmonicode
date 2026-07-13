"""HHS Modality Reconstruction Recipe v1."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional
import time
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
AUTHORITY = "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1"

def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"

def _now_ms() -> int:
    return int(time.time() * 1000)

def _list(values: Optional[Iterable[Any]]) -> List[str]:
    return sorted(dict.fromkeys(str(v) for v in (values or []) if str(v)))

RECONSTRUCTION_RECIPE_SCHEMA = "HHS_MODALITY_RECONSTRUCTION_RECIPE_V1"


def build_modality_reconstruction_recipe(*, source_root_hash72: str, projection_roots: Optional[Iterable[str]] = None, artifact_root_hash72: str = "", operations: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    recipe = {
        "schema": RECONSTRUCTION_RECIPE_SCHEMA,
        "version": VERSION,
        "recipe_id": _unique("modality-recipe"),
        "source_root_hash72": source_root_hash72,
        "projection_roots": _list(projection_roots),
        "artifact_root_hash72": artifact_root_hash72,
        "operations": [dict(o) for o in (operations or [])],
        "expanded_metadata_retained": False,
        "reconstruction_strategy": "SOURCE_ROOT_PLUS_TYPED_PROJECTION_STEPS_PLUS_ARTIFACT_LINEAGE",
        "authority": AUTHORITY,
    }
    recipe["recipe_root_hash72"] = hash72(RECONSTRUCTION_RECIPE_SCHEMA, recipe)
    return recipe


def validate_modality_reconstruction_recipe(recipe: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if recipe.get("schema") != RECONSTRUCTION_RECIPE_SCHEMA:
        reasons.append("REJECT_CROSS_MODAL_PLAN_WITHOUT_RECONSTRUCTION")
    if not recipe.get("source_root_hash72"):
        reasons.append("REJECT_TRANSFORMATION_WITHOUT_SOURCE_COMMITMENT")
    if recipe.get("expanded_metadata_retained"):
        reasons.append("REJECT_WORKSPACE_PERSISTENCE_EXPANDED_METADATA")
    if not recipe.get("recipe_root_hash72"):
        reasons.append("REJECT_CROSS_MODAL_PLAN_WITHOUT_RECONSTRUCTION")
    ok = not reasons
    return {
        "schema": "HHS_MODALITY_RECONSTRUCTION_RECIPE_VALIDATION_V1",
        "version": VERSION,
        "ok": ok,
        "status": "ADMIT_MODALITY_RECONSTRUCTION_RECIPE" if ok else "REJECT_MODALITY_RECONSTRUCTION_RECIPE",
        "reasons": sorted(dict.fromkeys(reasons)),
        "recipe_id": recipe.get("recipe_id"),
    }


def modality_reconstruction_recipe_self_test() -> Dict[str, Any]:
    recipe = build_modality_reconstruction_recipe(source_root_hash72="hash:source", projection_roots=["hash:projection"])
    invalid = dict(recipe, expanded_metadata_retained=True)
    valid = validate_modality_reconstruction_recipe(recipe)
    rejected = validate_modality_reconstruction_recipe(invalid)
    return {"schema": "HHS_MODALITY_RECONSTRUCTION_RECIPE_SELF_TEST_V1", "version": VERSION, "ok": bool(valid["ok"] and not rejected["ok"]), "valid": valid, "rejected": rejected}

if __name__ == "__main__":
    import json
    print(json.dumps(modality_reconstruction_recipe_self_test(), indent=2, sort_keys=True))
