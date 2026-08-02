"""Authoritative Pass 191 unified-manifold artifact runner.

Version 4 retains dependency-scoped parser and algebra evidence from v2, then
executes the complete Pass 189 contextual fabric through the exact Pass 191
manifold residual kernel. The retained frontier is hydrated through Pass 175,
singleton VM81 authority, and deterministic Hash72 replay.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice import (
    hhs_pass191_integrated_proof_engine_v1 as inherited_engine,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice import (
    hhs_pass191_runner_v2 as legacy_runner,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_manifold_engine_v2 import (
    CLASSIFICATION,
    run_integrated_manifold_search,
    verify_integrated_manifold_search,
)

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = PACKAGE_DIR / "evidence"
DEFAULT_NATIVE_LIBRARY = PACKAGE_DIR / "build" / "libhhs186_vm81_q144.so"
DEFAULT_MANIFOLD_SCANNER = PACKAGE_DIR / "build" / "hhs191_manifold_scan"
INTEGRATED_ARTIFACT = "PASS_191_INTEGRATED_PROOF_SEARCH.json"
INTEGRATED_COMPLETION = "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    legacy_runner.implementation.stable_json_write(path, payload)


def _strip_nonauthoritative(value: Any) -> None:
    if isinstance(value, dict):
        for key in list(value):
            lowered = key.lower()
            if "elapsed" in lowered or "nonauthoritative_timing" in lowered:
                value.pop(key, None)
            else:
                _strip_nonauthoritative(value[key])
    elif isinstance(value, list):
        for item in value:
            _strip_nonauthoritative(item)


def _normalize_integrated(payload: dict[str, Any]) -> dict[str, Any]:
    hydration = payload["vm81_hash216_frontier_hydration"]
    _strip_nonauthoritative(hydration)
    hydration_core = {
        key: value
        for key, value in hydration.items()
        if key != "frontier_hydration_hash72"
    }
    hydration["frontier_hydration_hash72"] = hash72_digest(
        {"domain": "HHS-PASS-191-MANIFOLD-FRONTIER-HYDRATION-V1"},
        hydration_core,
    )
    integrated_core = {
        key: value
        for key, value in payload.items()
        if key != "integrated_manifold_search_hash72"
    }
    payload["integrated_manifold_search_hash72"] = hash72_digest(
        {"domain": "HHS-PASS-191-INTEGRATED-MANIFOLD-SEARCH-V2"},
        integrated_core,
    )
    return payload


def _completion_payload(
    legacy: dict[str, Any], integrated: dict[str, Any]
) -> dict[str, Any]:
    manifold = integrated["unified_manifold_epoch"]
    verification = integrated["unified_manifold_verification"]
    core = {
        "schema": "HHS_PASS_191_UNIFIED_MANIFOLD_COMPLETION_RECEIPT_V2",
        "classification": CLASSIFICATION,
        "legacy_dependency_evidence": {
            "classification": legacy.get("classification"),
            "pass191_release_root_hash72": legacy.get(
                "pass191_release_root_hash72"
            ),
            "formal_outcome_verification": legacy.get(
                "formal_outcome_verification"
            ),
            "role": "DEPENDENCY_SCOPED_PARSER_AND_ALGEBRA_EVIDENCE",
        },
        "integrated_manifold_search_hash72": integrated[
            "integrated_manifold_search_hash72"
        ],
        "manifold_epoch_hash72": manifold["manifold_epoch_hash72"],
        "authority_path": integrated["authority_path"],
        "projected_cardinality": integrated["cardinality"]["projected"],
        "contextual_cardinality": integrated["cardinality"]["contextual"],
        "outer_envelope_modulus": integrated["cardinality"][
            "outer_envelope_modulus"
        ],
        "visited": verification["visited"],
        "exact_chain_hits": verification["exact_chain_hits"],
        "manifold_checksum_fnv1a64": verification["checksum_fnv1a64"],
        "frontier_size": verification["frontier_size"],
        "snapshot": integrated["continuation"]["snapshot"],
        "theorem_decision": integrated["theorem_decision"],
        "authoritative_decision_surface": INTEGRATED_ARTIFACT,
    }
    return {
        **core,
        "completion_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-UNIFIED-MANIFOLD-COMPLETION-V2"},
            core,
        ),
    }


def build_artifacts(
    repo_root: Path,
    output_dir: Path,
    native_library: Path,
    manifold_scanner: Path,
    *,
    epoch: int = 0,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    legacy = legacy_runner.build_artifacts(repo_root, output_dir)
    integrated = _normalize_integrated(
        run_integrated_manifold_search(
            repo_root,
            native_library,
            manifold_scanner,
            epoch=epoch,
        )
    )
    integrated_verification = verify_integrated_manifold_search(integrated)
    completion = _completion_payload(legacy, integrated)
    _write_json(output_dir / INTEGRATED_ARTIFACT, integrated)
    _write_json(output_dir / INTEGRATED_COMPLETION, completion)
    return {
        "schema": "HHS_PASS_191_UNIFIED_MANIFOLD_ARTIFACT_BUILD_V2",
        "ok": True,
        "classification": CLASSIFICATION,
        "legacy": legacy,
        "integrated_verification": integrated_verification,
        "completion": completion,
    }


def verify_existing_artifacts(
    repo_root: Path,
    output_dir: Path,
    native_library: Path,
) -> dict[str, Any]:
    legacy = legacy_runner.verify_existing_artifacts(repo_root, output_dir)
    integrated = _read_json(output_dir / INTEGRATED_ARTIFACT)
    completion = _read_json(output_dir / INTEGRATED_COMPLETION)
    integrated_verification = verify_integrated_manifold_search(integrated)

    native = inherited_engine.Pass186NativeABI(native_library)
    native_probe = inherited_engine.native_tensor_witnesses(native)
    obstruction_probe = inherited_engine.exact_reflection_obstruction()
    symmetry_probe = inherited_engine.hydrated_symmetry_search(native)
    if native_probe != integrated["native_tensor_witnesses"]:
        raise RuntimeError("committed Pass 186 native witnesses do not replay")
    if obstruction_probe != integrated["reflection_obstruction"]:
        raise RuntimeError("committed reflection obstruction does not replay")
    committed_symmetry = dict(integrated["symmetric_grid_diagnostic"])
    committed_symmetry.pop("role", None)
    if symmetry_probe != committed_symmetry:
        raise RuntimeError("committed symmetry diagnostic does not replay")

    completion_core = {
        key: value
        for key, value in completion.items()
        if key != "completion_hash72"
    }
    expected_completion_hash = hash72_digest(
        {"domain": "HHS-PASS-191-UNIFIED-MANIFOLD-COMPLETION-V2"},
        completion_core,
    )
    if completion.get("completion_hash72") != expected_completion_hash:
        raise RuntimeError("unified manifold completion Hash72 mismatch")
    if completion.get("integrated_manifold_search_hash72") != integrated.get(
        "integrated_manifold_search_hash72"
    ):
        raise RuntimeError("completion-to-search link mismatch")
    if completion.get("manifold_epoch_hash72") != integrated.get(
        "unified_manifold_epoch", {}
    ).get("manifold_epoch_hash72"):
        raise RuntimeError("completion-to-manifold link mismatch")
    if completion.get("classification") != CLASSIFICATION:
        raise RuntimeError("completion classification mismatch")
    if completion.get("authoritative_decision_surface") != INTEGRATED_ARTIFACT:
        raise RuntimeError("authoritative decision surface mismatch")
    return {
        "schema": "HHS_PASS_191_UNIFIED_MANIFOLD_ARTIFACT_VERIFICATION_V2",
        "ok": True,
        "classification": CLASSIFICATION,
        "legacy": legacy,
        "integrated_verification": integrated_verification,
        "completion_hash72": expected_completion_hash,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate and verify unified HHS Pass 191 manifold artifacts"
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--native-library", default=None)
    parser.add_argument("--manifold-scanner", default=None)
    parser.add_argument("--epoch", type=int, default=0)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args(argv)

    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parents[2]
    )
    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else DEFAULT_EVIDENCE_DIR
    )
    native_library = (
        Path(args.native_library).resolve()
        if args.native_library
        else DEFAULT_NATIVE_LIBRARY
    )
    manifold_scanner = (
        Path(args.manifold_scanner).resolve()
        if args.manifold_scanner
        else DEFAULT_MANIFOLD_SCANNER
    )
    result = (
        verify_existing_artifacts(repo_root, output_dir, native_library)
        if args.verify_existing
        else build_artifacts(
            repo_root,
            output_dir,
            native_library,
            manifold_scanner,
            epoch=args.epoch,
        )
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
