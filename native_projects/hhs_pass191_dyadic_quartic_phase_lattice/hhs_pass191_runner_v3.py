"""Authoritative integrated Pass 191 artifact runner.

Version 3 retains the dependency-scoped v2 parser/algebra evidence, then runs
the theorem target through the inherited Pass 186 native tensor ABI, Pass 175
Hash216 VM5184 x G243 hydration, Pass 174 singleton VM81 authority, and Hash72
replay.  The integrated result supersedes literal unit outcomes as the theorem
decision surface.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice import hhs_pass191_runner_v2 as legacy_runner
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_proof_engine_v1 import (
    CLASSIFICATION,
    run_integrated_proof_search,
    verify_integrated_proof_search,
)

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = PACKAGE_DIR / "evidence"
DEFAULT_NATIVE_LIBRARY = PACKAGE_DIR / "build" / "libhhs186_vm81_q144.so"
INTEGRATED_ARTIFACT = "PASS_191_INTEGRATED_PROOF_SEARCH.json"
INTEGRATED_COMPLETION = "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    legacy_runner.implementation.stable_json_write(path, payload)


def _completion_payload(
    legacy: dict[str, Any],
    integrated: dict[str, Any],
) -> dict[str, Any]:
    core = {
        "schema": "HHS_PASS_191_INTEGRATED_COMPLETION_RECEIPT_V1",
        "classification": CLASSIFICATION,
        "legacy_dependency_evidence": {
            "classification": legacy.get("classification"),
            "pass191_release_root_hash72": legacy.get("pass191_release_root_hash72"),
            "formal_outcome_verification": legacy.get("formal_outcome_verification"),
            "role": "DEPENDENCY_SCOPED_UNIT_EVIDENCE",
        },
        "integrated_proof_search_hash72": integrated[
            "integrated_proof_search_hash72"
        ],
        "authority_path": integrated["authority_path"],
        "hydrated_cardinality": integrated["cardinality"]["hydrated"],
        "theorem_decision": integrated["theorem_decision"],
        "proved_result": integrated["rh_symmetry_obstruction"]["theorem"],
        "authoritative_decision_surface": INTEGRATED_ARTIFACT,
    }
    return {
        **core,
        "completion_hash72": hash72_digest(
            {"domain": "HHS-PASS-191-INTEGRATED-COMPLETION-V1"}, core
        ),
    }


def build_artifacts(
    repo_root: Path,
    output_dir: Path,
    native_library: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    legacy = legacy_runner.build_artifacts(repo_root, output_dir)
    integrated = run_integrated_proof_search(repo_root, native_library)
    integrated_verification = verify_integrated_proof_search(integrated)
    completion = _completion_payload(legacy, integrated)

    _write_json(output_dir / INTEGRATED_ARTIFACT, integrated)
    _write_json(output_dir / INTEGRATED_COMPLETION, completion)

    return {
        "schema": "HHS_PASS_191_INTEGRATED_ARTIFACT_BUILD_V1",
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
    integrated_verification = verify_integrated_proof_search(integrated)

    native_probe = run_integrated_proof_search(repo_root, native_library)
    if native_probe["native_tensor_witnesses"] != integrated["native_tensor_witnesses"]:
        raise RuntimeError("committed Pass 186 native tensor witnesses do not replay")
    if native_probe["rh_symmetry_obstruction"] != integrated[
        "rh_symmetry_obstruction"
    ]:
        raise RuntimeError("committed reflection obstruction does not replay")
    if native_probe["hydrated_symmetry_search"] != integrated[
        "hydrated_symmetry_search"
    ]:
        raise RuntimeError("committed hydrated symmetry search does not replay")

    completion_core = {
        key: value for key, value in completion.items() if key != "completion_hash72"
    }
    expected_completion_hash = hash72_digest(
        {"domain": "HHS-PASS-191-INTEGRATED-COMPLETION-V1"}, completion_core
    )
    if completion.get("completion_hash72") != expected_completion_hash:
        raise RuntimeError("integrated completion Hash72 mismatch")
    if completion.get("integrated_proof_search_hash72") != integrated.get(
        "integrated_proof_search_hash72"
    ):
        raise RuntimeError("integrated completion search link mismatch")
    if completion.get("classification") != CLASSIFICATION:
        raise RuntimeError("integrated completion classification mismatch")
    if completion.get("authoritative_decision_surface") != INTEGRATED_ARTIFACT:
        raise RuntimeError("integrated decision surface mismatch")

    return {
        "schema": "HHS_PASS_191_INTEGRATED_ARTIFACT_VERIFICATION_V1",
        "ok": True,
        "classification": CLASSIFICATION,
        "legacy": legacy,
        "integrated_verification": integrated_verification,
        "native_replay_hash72": native_probe["integrated_proof_search_hash72"],
        "completion_hash72": expected_completion_hash,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate and verify integrated HHS Pass 191 proof-search artifacts"
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--native-library", default=None)
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

    result = (
        verify_existing_artifacts(repo_root, output_dir, native_library)
        if args.verify_existing
        else build_artifacts(repo_root, output_dir, native_library)
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
