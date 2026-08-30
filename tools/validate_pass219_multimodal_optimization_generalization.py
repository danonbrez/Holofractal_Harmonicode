from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hhs_runtime.pass219.multimodal_optimization_generalization import (  # noqa: E402
    GENERALIZE_REQUIRED,
    LOCAL_EXCEPTION_ALLOWED,
    NOT_APPLICABLE,
    VALIDATION_REQUIRED,
    validate_manifest,
)

CONTRACT = ROOT / "contracts/pass219/PASS_219_MULTIMODAL_OPTIMIZATION_GENERALIZATION_1_0.json"
GLOBAL = ROOT / "contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json"
REFERENCE = ROOT / "contracts/pass219/optimization_generalization/PASS_219_OPTIMIZATION_GENERALIZATION_REFERENCE_V1.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    contract = read_json(CONTRACT)
    global_contract = read_json(GLOBAL)
    reference = read_json(REFERENCE)

    inv = contract["invariant"]
    required = [
        inv["all_optimizations_multimodal_by_default"],
        inv["locality_is_exception_not_default"],
        inv["compatible_targets_discovered_automatically"],
        inv["compatible_untested_targets_are_validation_obligations"],
        inv["safe_beneficial_compatible_targets_are_generalization_obligations"],
        inv["no_new_user_directive_required_per_compatible_modality"],
        inv["applies_to_existing_and_future_objects"],
        inv["repair_forward_required"],
    ]
    if not all(required):
        raise SystemExit("MULTIMODAL_OPTIMIZATION_INVARIANT_DISABLED")

    if contract["canonical_object_metadata"]["primary_descriptor_schema"] != "HHS_PASS_187_OBJECT_DESCRIPTOR_V1":
        raise SystemExit("PASS187_DESCRIPTOR_BINDING_MISSING")
    if contract["canonical_object_metadata"]["modality_name_alone_is_sufficient"]:
        raise SystemExit("MODALITY_NAME_ONLY_COMPATIBILITY_FORBIDDEN")

    audit = contract.get("initial_repair_forward_audit", {})
    seeds = audit.get("seeds", [])
    required_seed_ids = {
        "PASS192_FIBONACCI_COMPRESSION",
        "PASS207_DETERMINISTIC_BATCH_CACHE",
        "PASS208_CANDIDATE_BRANCH_EXPANSION",
        "PASS219B_PHASE_LOCALITY",
        "PASS219B_SELECTIVE_PROJECTION",
        "PASS219B_SPARSE_DIRTY_PROJECTION",
    }
    if audit.get("status") != "REQUIRED" or {row.get("id") for row in seeds} != required_seed_ids:
        raise SystemExit("INITIAL_MULTIMODAL_GENERALIZATION_AUDIT_SEEDS_MISSING")
    if any(row.get("local_only") is True or row.get("classification") != "GENERALIZATION_AUDIT_REQUIRED" for row in seeds):
        raise SystemExit("INITIAL_GENERALIZATION_AUDIT_SEED_SCOPE_INVALID")


    mm = global_contract.get("multimodal_optimization_generalization", {})
    if mm.get("contract_id") != contract["contract_id"]:
        raise SystemExit("GLOBAL_DEFAULT_CONTRACT_NOT_BOUND_TO_MULTIMODAL_GENERALIZATION")
    if not mm.get("mandatory") or not mm.get("automatic_compatible_target_discovery"):
        raise SystemExit("GLOBAL_DEFAULT_MULTIMODAL_GENERALIZATION_NOT_MANDATORY")

    result = validate_manifest(reference)
    decisions = {row["target"]: row["classification"] for row in result["decisions"]}
    expected = {
        "target-vector": GENERALIZE_REQUIRED,
        "target-calibration": VALIDATION_REQUIRED,
        "target-interface": LOCAL_EXCEPTION_ALLOWED,
        "target-other-schema": NOT_APPLICABLE,
    }
    if decisions != expected:
        raise SystemExit(f"REFERENCE_DECISION_DRIFT:{decisions}")

    exact_h = (ROOT / "hhs_runtime/include/hhs_runtime_exact_abi.h").read_text(encoding="utf-8")
    exact_c = (ROOT / "hhs_runtime/c/hhs_runtime_exact_abi.c").read_text(encoding="utf-8")
    prior_h = "hhs_pass219_global_canonical_defaults_1_0.h"
    prior_c = "hhs_pass219_global_canonical_defaults_1_0.inc"
    new_h = "hhs_pass219_multimodal_optimization_generalization_1_0.h"
    new_c = "hhs_pass219_multimodal_optimization_generalization_1_0.inc"
    if not (exact_h.index(prior_h) < exact_h.index(new_h)):
        raise SystemExit("MULTIMODAL_POLICY_HEADER_ORDER_INVALID")
    if not (exact_c.index(prior_c) < exact_c.index(new_c)):
        raise SystemExit("MULTIMODAL_POLICY_SOURCE_ORDER_INVALID")

    required_paths = [
        ROOT / "docs/architecture/HHS_MULTIMODAL_OPTIMIZATION_GENERALIZATION.md",
        ROOT / "schemas/pass219/HHS_PASS_219_OPTIMIZATION_GENERALIZATION_MANIFEST_V1.schema.json",
        ROOT / "hhs_runtime/pass219/multimodal_optimization_generalization.py",
        ROOT / "hhs_runtime/include/hhs_pass219_multimodal_optimization_generalization_1_0.h",
        ROOT / "hhs_runtime/include/hhs_pass219_multimodal_optimization_generalization_1_0.hpp",
        ROOT / "hhs_runtime/c/hhs_pass219_multimodal_optimization_generalization_1_0.inc",
        ROOT / "tools/hhs_multimodal_optimization_generalizer.py",
        ROOT / "tests/pass219/test_pass219_multimodal_optimization_generalization.py",
        ROOT / "tests/pass219/test_pass219_multimodal_optimization_generalization_1_0.c",
        ROOT / "tests/pass219/test_pass219_multimodal_optimization_generalization_1_0.cpp",
        ROOT / ".github/workflows/pass219-multimodal-optimization-generalization.yml",
    ]
    for path in required_paths:
        if not path.is_file():
            raise SystemExit(f"REQUIRED_MULTIMODAL_POLICY_SURFACE_MISSING:{path}")

    subprocess.run(
        [sys.executable, "-m", "py_compile",
         str(ROOT / "hhs_runtime/pass219/multimodal_optimization_generalization.py"),
         str(ROOT / "tools/hhs_multimodal_optimization_generalizer.py")],
        check=True,
    )

    print(json.dumps({
        "classification":"HHS_PASS219_MULTIMODAL_OPTIMIZATION_GENERALIZATION_ENFORCED",
        "reference_generalize_required":result["generalize_required"],
        "reference_validation_required":result["validation_required"],
        "reference_local_exceptions":result["local_exceptions"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
