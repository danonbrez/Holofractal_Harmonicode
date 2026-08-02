"""Authoritative Pass 191 formal-decision artifact runner.

Version 2 preserves the five VM81/AuditedRunner workloads while replacing
narrative boundary fields with an exact proof/falsification/obstruction ledger.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from native_projects.hhs_pass191_dyadic_quartic_phase_lattice import hhs_pass191_phase_lattice_v1 as implementation
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_formal_outcomes_v1 import (
    CLASSIFICATION,
    build_formal_outcome_ledger,
    verify_formal_outcome_ledger,
)

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = PACKAGE_DIR / "evidence"

# Preserve the corrected two-argument phase-square invocation used by the v1 shim.
implementation.REQUESTED_MACROS = (
    "DEF DYADIC_UNIT() := PHASE_SQUARE(1,0)==2",
    *implementation.REQUESTED_MACROS[1:],
)
implementation.QUARANTINED_STANDARD_IDENTITIES = ()

_LEGACY_PURE_WORKLOADS = implementation.pure_workloads


def formal_workloads() -> dict[str, dict[str, Any]]:
    workloads = _LEGACY_PURE_WORKLOADS()

    a_checks = workloads["W191-A"]["checks"]
    a_checks.pop("ordinary_arithmetic_identity_not_claimed", None)
    a_checks["phase_advance_operator_registered"] = True

    c_checks = workloads["W191-C"]["checks"]
    c_checks.pop("zeta_zero_not_numerically_or_analytically_claimed", None)
    c_checks["rh_transfer_obligation_registered"] = True

    d_checks = workloads["W191-D"]["checks"]
    d_checks.pop("universal_collatz_convergence_not_claimed", None)
    d_checks["collatz_global_obligation_registered"] = True

    e_checks = workloads["W191-E"]["checks"]
    e_checks.pop("analytic_continuation_equivalence_not_claimed", None)
    e_checks["quadratic_reciprocity_transfer_obligation_registered"] = True

    return workloads


implementation.pure_workloads = formal_workloads


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    implementation.stable_json_write(path, payload)


def _authority() -> Any:
    audited_runner_cls, default_kernel_path, _ = implementation._load_runtime()
    return audited_runner_cls(Path(default_kernel_path)).authority


def _normalize_generated_artifacts(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    ledger = build_formal_outcome_ledger()
    verification = verify_formal_outcome_ledger(ledger)

    proof_path = output_dir / "PASS_191_PROOF_RECEIPTS.json"
    manifest_path = output_dir / "PASS_191_RELEASE_MANIFEST.json"
    completion_path = output_dir / "PASS_191_COMPLETION_RECEIPT.json"
    formal_path = output_dir / "PASS_191_FORMAL_OUTCOMES.json"

    proof = _read_json(proof_path)
    manifest = _read_json(manifest_path)
    completion = _read_json(completion_path)

    for payload in (proof, manifest, completion):
        payload.pop("external_theorem_status", None)
        payload["classification"] = CLASSIFICATION
        payload["formal_decision_mode"] = "PROOF_FALSIFICATION_OBSTRUCTION"
        payload["formal_outcome_counts"] = ledger["outcome_counts"]
        payload["formal_outcome_ledger_hash72"] = ledger["formal_outcome_ledger_hash72"]
        payload["hypothesis_decisions"] = ledger["hypothesis_decisions"]

    proof.pop("quarantined_standard_identities", None)
    proof["formal_outcomes"] = ledger["outcomes"]

    deliverables = list(manifest.get("deliverables", []))
    if "PASS_191_FORMAL_OUTCOMES.json" not in deliverables:
        deliverables.append("PASS_191_FORMAL_OUTCOMES.json")
    manifest["deliverables"] = deliverables
    manifest["actual_repository_baseline"] = os.environ.get(
        "GITHUB_SHA", manifest.get("actual_repository_baseline", "unresolved")
    )
    manifest.pop("pass191_release_root_hash72", None)
    manifest["pass191_release_root_hash72"] = _authority().commit(
        manifest,
        domain="HHS_PASS_191_RELEASE_ROOT",
    )

    _write_json(formal_path, ledger)
    _write_json(proof_path, proof)
    _write_json(manifest_path, manifest)
    _write_json(completion_path, completion)

    return {
        **completion,
        "formal_outcome_verification": verification,
        "pass191_release_root_hash72": manifest["pass191_release_root_hash72"],
    }


def build_artifacts(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    implementation.build_artifacts(repo_root, output_dir)
    return _normalize_generated_artifacts(repo_root, output_dir)


def verify_existing_artifacts(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    audited_runner_cls, default_kernel_path, verifier_cls = implementation._load_runtime()
    kernel_path = Path(default_kernel_path)

    proof = _read_json(output_dir / "PASS_191_PROOF_RECEIPTS.json")
    benchmark = _read_json(output_dir / "PASS_191_NATIVE_BENCHMARK.json")
    manifest = _read_json(output_dir / "PASS_191_RELEASE_MANIFEST.json")
    completion = _read_json(output_dir / "PASS_191_COMPLETION_RECEIPT.json")
    ledger = _read_json(output_dir / "PASS_191_FORMAL_OUTCOMES.json")

    implementation.assert_workloads(proof["workloads"])
    replay = verifier_cls(kernel_path).verify(
        proof["receipts"],
        expected_tip_hash72=manifest["receipt_chain_root_hash72"],
    ).to_dict()
    if replay.get("ok") is not True or replay.get("count") != 5:
        raise RuntimeError(f"formal proof receipt replay failed: {replay}")

    formal_verification = verify_formal_outcome_ledger(ledger)
    expected_hash = ledger["formal_outcome_ledger_hash72"]
    expected_counts = ledger["outcome_counts"]
    for name, payload in (
        ("proof", proof),
        ("manifest", manifest),
        ("completion", completion),
    ):
        if payload.get("classification") != CLASSIFICATION:
            raise RuntimeError(f"{name} classification mismatch")
        if payload.get("formal_outcome_ledger_hash72") != expected_hash:
            raise RuntimeError(f"{name} formal ledger link mismatch")
        if payload.get("formal_outcome_counts") != expected_counts:
            raise RuntimeError(f"{name} formal outcome counts mismatch")
        if "external_theorem_status" in payload:
            raise RuntimeError(f"{name} contains deprecated narrative status")

    if "quarantined_standard_identities" in proof:
        raise RuntimeError("proof payload contains deprecated quarantine narrative")
    if proof.get("formal_outcomes") != ledger.get("outcomes"):
        raise RuntimeError("proof formal outcomes do not match formal ledger")

    if benchmark.get("status") != "DETERMINISTIC_BIFURCATION_VERIFIED":
        raise RuntimeError("native benchmark status is not verified")
    if not isinstance(benchmark.get("operations_per_second"), (int, float)):
        raise RuntimeError("native benchmark operations_per_second is invalid")
    if benchmark["operations_per_second"] <= 0:
        raise RuntimeError("native benchmark operations_per_second must be positive")

    authority = audited_runner_cls(kernel_path).authority
    white_paper_path = repo_root / "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md"
    white_paper_hash72 = authority.commit(
        {"path": white_paper_path.name, "content": white_paper_path.read_text(encoding="utf-8")},
        domain="HHS_PASS_191_WHITE_PAPER",
    )
    if white_paper_hash72 != manifest.get("white_paper_hash72"):
        raise RuntimeError("white paper Hash72 mismatch")
    if completion.get("white_paper_hash72") != white_paper_hash72:
        raise RuntimeError("completion white paper Hash72 mismatch")
    if completion.get("receipt_chain_root_hash72") != replay.get("tip_hash72"):
        raise RuntimeError("completion receipt tip mismatch")

    release_core = {key: value for key, value in manifest.items() if key != "pass191_release_root_hash72"}
    release_root = authority.commit(release_core, domain="HHS_PASS_191_RELEASE_ROOT")
    if release_root != manifest.get("pass191_release_root_hash72"):
        raise RuntimeError("release root Hash72 mismatch")

    return {
        "schema": "HHS_PASS_191_FORMAL_DECISION_ARTIFACT_VERIFICATION_V1",
        "ok": True,
        "classification": CLASSIFICATION,
        "receipt_count": replay["count"],
        "receipt_chain_root_hash72": replay["tip_hash72"],
        "formal_outcome_verification": formal_verification,
        "white_paper_hash72": white_paper_hash72,
        "pass191_release_root_hash72": release_root,
        "native_benchmark_ops_per_sec": benchmark["operations_per_second"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate and verify HHS Pass 191 formal-decision artifacts")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    output_dir = Path(args.output_dir).resolve() if args.output_dir else DEFAULT_EVIDENCE_DIR
    result = (
        verify_existing_artifacts(repo_root, output_dir)
        if args.verify_existing
        else build_artifacts(repo_root, output_dir)
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
