"""Authoritative Pass 191 formal-decision artifact runner.

Version 2 preserves the five VM81/AuditedRunner workloads while replacing
narrative boundary fields with an exact proof/falsification/obstruction ledger.
Committed authority evidence excludes volatile wall-clock benchmark fields and
is rooted to the authorized Pass 191 mainline baseline.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from native_projects.hhs_pass191_dyadic_quartic_phase_lattice import hhs_pass191_phase_lattice_v1 as implementation
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_formal_outcomes_v1 import (
    CLASSIFICATION,
    build_formal_outcome_ledger,
    verify_formal_outcome_ledger,
)

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = PACKAGE_DIR / "evidence"
AUTHORIZED_REPOSITORY_BASELINE = "992b4e92a54d4656d66af4edfab7e03922addca6"
VOLATILE_BENCHMARK_FIELDS = (
    "total_execution_ns",
    "native_invocation_ns_reported",
    "operations_per_second",
)
BENCHMARK_TIMING_CLASSIFICATION = (
    "NONAUTHORITATIVE_WALL_CLOCK_MEASUREMENT_EXECUTED_NOT_COMMITTED"
)

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


def normalize_benchmark_artifact(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Remove non-authoritative runtime timing while preserving benchmark proof state."""

    normalized = dict(payload)
    for field in VOLATILE_BENCHMARK_FIELDS:
        normalized.pop(field, None)
    normalized["timing_classification"] = BENCHMARK_TIMING_CLASSIFICATION
    normalized["volatile_fields_excluded_from_authority"] = list(
        VOLATILE_BENCHMARK_FIELDS
    )
    return normalized


def _verify_normalized_benchmark(benchmark: Mapping[str, Any]) -> None:
    if benchmark.get("status") != "DETERMINISTIC_BIFURCATION_VERIFIED":
        raise RuntimeError("native benchmark status is not verified")
    if benchmark.get("determinism_mismatch_count") != 0:
        raise RuntimeError("native benchmark determinism mismatch count is nonzero")
    if benchmark.get("closure_coordinate_roots_match") is not True:
        raise RuntimeError("native benchmark closure roots do not match")
    if benchmark.get("receipt_chain_locks") is not True:
        raise RuntimeError("native benchmark receipt chain is not locked")
    if benchmark.get("timing_classification") != BENCHMARK_TIMING_CLASSIFICATION:
        raise RuntimeError("native benchmark timing classification mismatch")
    if benchmark.get("volatile_fields_excluded_from_authority") != list(
        VOLATILE_BENCHMARK_FIELDS
    ):
        raise RuntimeError("native benchmark volatile-field registry mismatch")
    retained = [field for field in VOLATILE_BENCHMARK_FIELDS if field in benchmark]
    if retained:
        raise RuntimeError(
            f"native benchmark retained non-authoritative timing fields: {retained}"
        )


def _normalize_generated_artifacts(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    del repo_root
    ledger = build_formal_outcome_ledger()
    verification = verify_formal_outcome_ledger(ledger)

    proof_path = output_dir / "PASS_191_PROOF_RECEIPTS.json"
    benchmark_path = output_dir / "PASS_191_NATIVE_BENCHMARK.json"
    manifest_path = output_dir / "PASS_191_RELEASE_MANIFEST.json"
    completion_path = output_dir / "PASS_191_COMPLETION_RECEIPT.json"
    formal_path = output_dir / "PASS_191_FORMAL_OUTCOMES.json"

    proof = _read_json(proof_path)
    benchmark = normalize_benchmark_artifact(_read_json(benchmark_path))
    manifest = _read_json(manifest_path)
    completion = _read_json(completion_path)
    _verify_normalized_benchmark(benchmark)

    for payload in (proof, manifest, completion):
        payload.pop("external_theorem_status", None)
        payload["classification"] = CLASSIFICATION
        payload["formal_decision_mode"] = "PROOF_FALSIFICATION_OBSTRUCTION"
        payload["formal_outcome_counts"] = ledger["outcome_counts"]
        payload["formal_outcome_ledger_hash72"] = ledger[
            "formal_outcome_ledger_hash72"
        ]
        payload["hypothesis_decisions"] = ledger["hypothesis_decisions"]

    proof.pop("quarantined_standard_identities", None)
    proof["formal_outcomes"] = ledger["outcomes"]

    deliverables = list(manifest.get("deliverables", []))
    if "PASS_191_FORMAL_OUTCOMES.json" not in deliverables:
        deliverables.append("PASS_191_FORMAL_OUTCOMES.json")
    manifest["deliverables"] = deliverables
    manifest["actual_repository_baseline"] = AUTHORIZED_REPOSITORY_BASELINE
    manifest.pop("native_benchmark_ops_per_sec", None)
    manifest["native_benchmark_authority"] = {
        "artifact": "PASS_191_NATIVE_BENCHMARK.json",
        "status": benchmark["status"],
        "timing_classification": BENCHMARK_TIMING_CLASSIFICATION,
    }
    completion.pop("native_benchmark_ops_per_sec", None)
    completion["native_benchmark_authority"] = manifest[
        "native_benchmark_authority"
    ]

    manifest.pop("pass191_release_root_hash72", None)
    manifest["pass191_release_root_hash72"] = _authority().commit(
        manifest,
        domain="HHS_PASS_191_RELEASE_ROOT",
    )

    _write_json(formal_path, ledger)
    _write_json(proof_path, proof)
    _write_json(benchmark_path, benchmark)
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

    _verify_normalized_benchmark(benchmark)
    if manifest.get("actual_repository_baseline") != AUTHORIZED_REPOSITORY_BASELINE:
        raise RuntimeError("authorized repository baseline mismatch")
    expected_benchmark_authority = {
        "artifact": "PASS_191_NATIVE_BENCHMARK.json",
        "status": benchmark["status"],
        "timing_classification": BENCHMARK_TIMING_CLASSIFICATION,
    }
    if manifest.get("native_benchmark_authority") != expected_benchmark_authority:
        raise RuntimeError("manifest native benchmark authority mismatch")
    if completion.get("native_benchmark_authority") != expected_benchmark_authority:
        raise RuntimeError("completion native benchmark authority mismatch")
    if "native_benchmark_ops_per_sec" in manifest or "native_benchmark_ops_per_sec" in completion:
        raise RuntimeError("committed authority contains volatile benchmark throughput")

    authority = audited_runner_cls(kernel_path).authority
    white_paper_path = repo_root / "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md"
    white_paper_hash72 = authority.commit(
        {
            "path": white_paper_path.name,
            "content": white_paper_path.read_text(encoding="utf-8"),
        },
        domain="HHS_PASS_191_WHITE_PAPER",
    )
    if white_paper_hash72 != manifest.get("white_paper_hash72"):
        raise RuntimeError("white paper Hash72 mismatch")
    if completion.get("white_paper_hash72") != white_paper_hash72:
        raise RuntimeError("completion white paper Hash72 mismatch")
    if completion.get("receipt_chain_root_hash72") != replay.get("tip_hash72"):
        raise RuntimeError("completion receipt tip mismatch")

    release_core = {
        key: value
        for key, value in manifest.items()
        if key != "pass191_release_root_hash72"
    }
    release_root = authority.commit(release_core, domain="HHS_PASS_191_RELEASE_ROOT")
    if release_root != manifest.get("pass191_release_root_hash72"):
        raise RuntimeError("release root Hash72 mismatch")

    return {
        "schema": "HHS_PASS_191_FORMAL_DECISION_ARTIFACT_VERIFICATION_V2",
        "ok": True,
        "classification": CLASSIFICATION,
        "receipt_count": replay["count"],
        "receipt_chain_root_hash72": replay["tip_hash72"],
        "formal_outcome_verification": formal_verification,
        "white_paper_hash72": white_paper_hash72,
        "pass191_release_root_hash72": release_root,
        "native_benchmark_status": benchmark["status"],
        "benchmark_timing_classification": BENCHMARK_TIMING_CLASSIFICATION,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate and verify HHS Pass 191 formal-decision artifacts"
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
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
    result = (
        verify_existing_artifacts(repo_root, output_dir)
        if args.verify_existing
        else build_artifacts(repo_root, output_dir)
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
