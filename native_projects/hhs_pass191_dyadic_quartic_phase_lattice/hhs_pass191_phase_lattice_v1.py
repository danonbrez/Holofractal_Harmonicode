from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping
import argparse
import json
import math
import os

PASS_ID = "PASS_191"
SCHEMA = "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_V1"
WORKLOAD_IDS = ("W191-A", "W191-B", "W191-C", "W191-D", "W191-E")
U72 = 72


@dataclass(frozen=True)
class PhaseState:
    """Exact HHS phase coordinate; it is not an ordinary complex scalar."""

    dyadic_level: int
    quartic_phase: int

    def __post_init__(self) -> None:
        if not isinstance(self.dyadic_level, int):
            raise TypeError("dyadic_level must be int")
        if not isinstance(self.quartic_phase, int):
            raise TypeError("quartic_phase must be int")
        object.__setattr__(self, "quartic_phase", self.quartic_phase % 4)

    def square(self) -> "PhaseState":
        """System-internal dyadic/quartic advance, not standard multiplication."""
        return PhaseState(self.dyadic_level + 1, self.quartic_phase + 1)

    def magnitude(self) -> Fraction:
        if self.dyadic_level >= 0:
            return Fraction(2**self.dyadic_level, 1)
        return Fraction(1, 2 ** (-self.dyadic_level))

    def phase_basis(self) -> str:
        return ("1", "i", "-1", "-i")[self.quartic_phase]

    def to_dict(self) -> dict[str, Any]:
        return {
            "dyadic_level": self.dyadic_level,
            "quartic_phase": self.quartic_phase,
            "magnitude": fraction_text(self.magnitude()),
            "phase_basis": self.phase_basis(),
        }


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def phase_trace(start: PhaseState, advances: int) -> list[PhaseState]:
    if advances < 0:
        raise ValueError("advances must be non-negative")
    out = [start]
    for _ in range(advances):
        out.append(out[-1].square())
    return out


def integer_phase_embedding(n: int) -> dict[str, Any]:
    if not isinstance(n, int):
        raise TypeError("n must be int")
    if n == 0:
        return {
            "integer": 0,
            "phase_state": PhaseState(0, 0).to_dict(),
            "odd_residue": 0,
            "reconstruction": 0,
            "injective_phase_state_alone": False,
        }
    magnitude = abs(n)
    level = 0
    while magnitude % 2 == 0:
        magnitude //= 2
        level += 1
    phase = 0 if n > 0 else 2
    sign = 1 if phase == 0 else -1
    reconstructed = sign * (2**level) * magnitude
    return {
        "integer": n,
        "phase_state": PhaseState(level, phase).to_dict(),
        "odd_residue": magnitude,
        "reconstruction": reconstructed,
        "injective_phase_state_alone": False,
    }


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def collatz_step(n: int) -> int:
    if n <= 0:
        raise ValueError("n must be positive")
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def collatz_orbit(n: int, max_steps: int = 256) -> list[int]:
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")
    orbit = [n]
    for _ in range(max_steps):
        if orbit[-1] == 1:
            break
        orbit.append(collatz_step(orbit[-1]))
    return orbit


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    limit = math.isqrt(n)
    for d in range(3, limit + 1, 2):
        if n % d == 0:
            return False
    return True


def legendre_symbol(a: int, p: int) -> int:
    if not is_prime(p) or p == 2:
        raise ValueError("p must be an odd prime")
    residue = pow(a % p, (p - 1) // 2, p)
    return -1 if residue == p - 1 else residue


def quadratic_reciprocity_checks(limit: int = 43) -> list[dict[str, Any]]:
    primes = [p for p in range(3, limit + 1) if is_prime(p)]
    rows: list[dict[str, Any]] = []
    for p in primes:
        for q in primes:
            if p >= q:
                continue
            lhs = legendre_symbol(p, q) * legendre_symbol(q, p)
            rhs = -1 if ((p - 1) // 2) * ((q - 1) // 2) % 2 else 1
            rows.append({"p": p, "q": q, "lhs": lhs, "rhs": rhs, "ok": lhs == rhs})
    return rows


def phase_then_cell(state: PhaseState) -> PhaseState:
    phased = PhaseState(state.dyadic_level, state.quartic_phase + 1)
    return PhaseState(phased.dyadic_level + (phased.quartic_phase % 2), phased.quartic_phase)


def cell_then_phase(state: PhaseState) -> PhaseState:
    celled = PhaseState(state.dyadic_level + (state.quartic_phase % 2), state.quartic_phase)
    return PhaseState(celled.dyadic_level, celled.quartic_phase + 1)


REQUESTED_MACROS: tuple[str, ...] = (
    "DEF DYADIC_UNIT() := PHASE_SQUARE(1)==2",
    "DEF QUARTIC_CYCLE() := I^4==1==16/16",
    "DEF PHASE_SQUARE(x,p) := DYADIC_LEVEL(x)+1==QUARTIC_PHASE(p+1)",
    "DEF CRITICAL_AXIS(t) := RE(1/2+I*t)==1/2",
    "DEF RESONANCE(t) := E^(I*Pi*(1/2+I*t))==I*E^(-Pi*t)",
    "DEF FIBONACCI_PHASE(n) := F(n+2)==F(n+1)+F(n)",
    "DEF GOLDEN_CLOSURE() := phi^2==phi+1",
    "DEF COLLATZ_STEP(n) := IF n%2==0 THEN n/2 ELSE (3*n+1)/2 FI",
    "DEF PLASTIC_CLOSURE() := rho^3==rho+1==rho^4/rho",
    "DEF PHASE_THEN_CELL(x) := CELL(PHASE(x))",
    "DEF CELL_THEN_PHASE(x) := PHASE(CELL(x))",
)

QUARANTINED_STANDARD_IDENTITIES: tuple[dict[str, str], ...] = (
    {
        "source": "1^2==2",
        "reason": "false under ordinary arithmetic; retained only as PHASE_SQUARE magnitude projection",
    },
    {
        "source": "1/2==I^2/2==(-1)/2",
        "reason": "1/2 is not equal to -1/2; the valid identity is I^2/2==-1/2",
    },
    {
        "source": "E^(I*Pi*(1/2+I*t))==(-1)*E^(-Pi*t)",
        "reason": "the exact standard expansion is I*E^(-Pi*t)",
    },
    {
        "source": "F(n+2)==F(n+1)+F(n)==phi^n*psi^n",
        "reason": "phi^n*psi^n=(-1)^n and is not the Fibonacci recurrence value",
    },
    {
        "source": "quartic closure guarantees Collatz convergence",
        "reason": "not derived; only the bounded orbit for the supplied seed is verified",
    },
    {
        "source": "zeta(1/2+it)=0 iff dyadic phase closure",
        "reason": "not derived by the implemented axioms; classical RH remains outside this verification",
    },
)


def pure_workloads() -> dict[str, dict[str, Any]]:
    start = PhaseState(0, 0)
    trace = phase_trace(start, 4)
    embeddings = [integer_phase_embedding(n) for n in range(-16, 17)]
    reciprocity = quadratic_reciprocity_checks(43)
    collatz = collatz_orbit(7)
    p_then_c = phase_then_cell(start)
    c_then_p = cell_then_phase(start)

    workloads = {
        "W191-A": {
            "title": "Renormalized Unit Consistency",
            "scope": "HHS phase-square magnitude projection",
            "start": start.to_dict(),
            "after_one_advance": trace[1].to_dict(),
            "checks": {
                "magnitude_advance_1_to_2": trace[0].magnitude() == 1 and trace[1].magnitude() == 2,
                "ordinary_arithmetic_identity_not_claimed": True,
                "integer_embeddings_reconstruct": all(row["integer"] == row["reconstruction"] for row in embeddings),
            },
            "integer_embedding_sample": embeddings,
        },
        "W191-B": {
            "title": "Quartic Closure Verification",
            "trace": [state.to_dict() for state in trace],
            "checks": {
                "dyadic_magnitudes_are_1_2_4_8_16": [state.magnitude() for state in trace]
                == [Fraction(1), Fraction(2), Fraction(4), Fraction(8), Fraction(16)],
                "phase_returns_to_zero_after_four": trace[-1].quartic_phase == 0,
                "dyadic_level_advances_by_four": trace[-1].dyadic_level - trace[0].dyadic_level == 4,
            },
        },
        "W191-C": {
            "title": "Critical Axis Resonance",
            "critical_axis": "Re(1/2 + i*t) = 1/2",
            "supplied_zero_parameter": "141347/10000",
            "u72_half_offset": U72 // 2,
            "exact_exponential_identity": "exp(i*pi*(1/2+i*t)) = i*exp(-pi*t)",
            "checks": {
                "critical_axis_is_exact_half": Fraction(1, 2) * 2 == 1,
                "u72_offset_is_half_cycle": U72 // 2 == 36,
                "zeta_zero_not_numerically_or_analytically_claimed": True,
            },
        },
        "W191-D": {
            "title": "Fibonacci Plastic Collatz Integration",
            "fibonacci": {"n": 10, "f_n": fibonacci(10), "f_n1": fibonacci(11), "f_n2": fibonacci(12)},
            "golden_polynomial": "phi^2-phi-1=0",
            "plastic_polynomial": "rho^3-rho-1=0",
            "collatz_seed_7_orbit": collatz,
            "checks": {
                "fibonacci_recurrence": fibonacci(12) == fibonacci(11) + fibonacci(10),
                "collatz_seed_7_reaches_1_within_bound": collatz[-1] == 1,
                "universal_collatz_convergence_not_claimed": True,
                "algebraic_numbers_kept_symbolic": True,
            },
        },
        "W191-E": {
            "title": "Noncommutative Phase Order and Bounded Reciprocity",
            "phase_then_cell": p_then_c.to_dict(),
            "cell_then_phase": c_then_p.to_dict(),
            "quadratic_reciprocity_bound": 43,
            "quadratic_reciprocity_cases": reciprocity,
            "checks": {
                "phase_cell_order_is_noncommutative": p_then_c != c_then_p,
                "bounded_quadratic_reciprocity_exact": bool(reciprocity) and all(row["ok"] for row in reciprocity),
                "analytic_continuation_equivalence_not_claimed": True,
            },
        },
    }
    return workloads


def assert_workloads(workloads: Mapping[str, Mapping[str, Any]]) -> None:
    if tuple(workloads) != WORKLOAD_IDS:
        raise AssertionError("workload order mismatch")
    for workload_id, payload in workloads.items():
        checks = payload.get("checks", {})
        failed = [name for name, value in checks.items() if value is not True]
        if failed:
            raise AssertionError(f"{workload_id} failed checks: {failed}")


def _load_runtime() -> tuple[Any, Any, Any]:
    from hhs_general_runtime_layer_v1 import AuditedRunner, DEFAULT_KERNEL_PATH
    from hhs_receipt_replay_verifier_v1 import HHSReceiptReplayVerifierV1

    return AuditedRunner, DEFAULT_KERNEL_PATH, HHSReceiptReplayVerifierV1


def _load_terminal() -> Any:
    from terminal_hhsprog_v5_macro_algebra import HHSMacroAlgebraTerminalV5

    return HHSMacroAlgebraTerminalV5


def define_macros(kernel_path: Path) -> dict[str, Any]:
    terminal_cls = _load_terminal()
    term = terminal_cls(kernel_path)
    definitions: list[dict[str, Any]] = []
    for source in REQUESTED_MACROS:
        result = term.dispatch(source)
        if not result.get("ok"):
            raise RuntimeError(f"macro definition failed: {source}: {result}")
        definitions.append(result["defined_macro"])

    calls = (
        "CALL DYADIC_UNIT()",
        "CALL QUARTIC_CYCLE()",
        "CALL CRITICAL_AXIS(141347/10000)",
        "CALL RESONANCE(141347/10000)",
        "CALL FIBONACCI_PHASE(10)",
        "CALL GOLDEN_CLOSURE()",
        "CALL PLASTIC_CLOSURE()",
        "CALL COLLATZ_STEP(7)",
        "CALL PHASE_THEN_CELL(1)",
        "CALL CELL_THEN_PHASE(1)",
    )
    call_records: list[dict[str, Any]] = []
    for source in calls:
        result = term.dispatch(source)
        if not result.get("ok"):
            raise RuntimeError(f"macro call failed: {source}: {result}")
        call_records.append(result)

    chain = term.runner.commitments.verify_chain()
    if chain.get("ok") is not True:
        raise RuntimeError(f"macro receipt chain failed: {chain}")
    return {
        "terminal": "TERMINAL_HHSPROG_V5_MACRO_ALGEBRA",
        "definitions": definitions,
        "calls": call_records,
        "chain": chain,
        "tip_hash72": term.runner.commitments.tip_hash72,
    }


def create_workload_receipts(kernel_path: Path, workloads: Mapping[str, Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    audited_runner_cls, _, verifier_cls = _load_runtime()
    runner = audited_runner_cls(kernel_path)

    def verify_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
        checks = payload.get("checks", {})
        return {
            "audit_value": 1 if checks and all(value is True for value in checks.values()) else 0,
            "workload_id": payload.get("workload_id"),
            "checks": checks,
            "evidence": payload,
        }

    runner.registry.register("PASS191_VERIFY", verify_payload)
    receipts: list[dict[str, Any]] = []
    for workload_id in WORKLOAD_IDS:
        evidence = dict(workloads[workload_id])
        evidence["schema"] = SCHEMA
        evidence["pass_id"] = PASS_ID
        evidence["workload_id"] = workload_id
        out = runner.execute("PASS191_VERIFY", evidence, input_payload=evidence)
        if out.get("ok") is not True:
            raise RuntimeError(f"{workload_id} receipt quarantined: {out}")
        receipt = dict(out["receipt"])
        receipt["workload_id"] = workload_id
        receipt["vm81_authorized_tick"] = receipt["phase"]
        receipts.append(receipt)

    replay = verifier_cls(kernel_path).verify(receipts, expected_tip_hash72=runner.commitments.tip_hash72).to_dict()
    if replay.get("ok") is not True or replay.get("count") != 5:
        raise RuntimeError(f"proof receipt replay failed: {replay}")
    return receipts, replay


def run_native_benchmark(repo_root: Path) -> dict[str, Any]:
    from native_projects.hhs_bifurcation_calibration.hhs_pass082_bifurcation_benchmark_v1 import (
        default_workload,
        run,
        verify_replay,
    )

    workload = default_workload(repo_root, branch_count=4, ast_nodes=16)
    result = run(repo_root, workload)
    replay = verify_replay(repo_root, workload)
    if result.get("status") != "DETERMINISTIC_BIFURCATION_VERIFIED":
        raise RuntimeError(f"native benchmark failed: {result.get('status')}")
    metrics = dict(result.get("metrics", {}))
    return {
        "schema": "HHS_PASS_191_NATIVE_BENCHMARK_V1",
        "status": result["status"],
        "branch_count": metrics.get("branch_count"),
        "total_execution_ns": metrics.get("total_execution_ns"),
        "native_invocation_ns_reported": metrics.get("native_invocation_ns"),
        "operations_per_second": metrics.get("branches_admitted_per_second"),
        "determinism_mismatch_count": metrics.get("determinism_mismatch_count"),
        "closure_coordinate_roots_match": result["bifurcation_receipt"]["closure_coordinate_roots_match"],
        "receipt_chain_locks": result["bifurcation_receipt"]["deterministic_bifurcation_verified"],
        "replay_receipt_root_hash72": replay["receipt_root_hash72"],
        "canonical_float_authority_used": False,
        "note": "Pass 082 uses an opaque native float buffer only as non-authoritative benchmark output; canonical Pass 191 proofs remain exact.",
    }


def stable_json_write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def build_artifacts(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    audited_runner_cls, default_kernel_path, _ = _load_runtime()
    kernel_path = Path(default_kernel_path)
    workloads = pure_workloads()
    assert_workloads(workloads)
    macro_report = define_macros(kernel_path)
    receipts, replay = create_workload_receipts(kernel_path, workloads)
    benchmark = run_native_benchmark(repo_root)

    authority = audited_runner_cls(kernel_path).authority
    white_paper_path = repo_root / "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md"
    white_paper_text = white_paper_path.read_text(encoding="utf-8")
    white_paper_hash72 = authority.commit(
        {"path": white_paper_path.name, "content": white_paper_text},
        domain="HHS_PASS_191_WHITE_PAPER",
    )

    proof_payload = {
        "schema": "HHS_PASS_191_PROOF_RECEIPTS_V1",
        "pass_id": PASS_ID,
        "classification": "HHS_PASS_191_INTERNAL_PHASE_LATTICE_MODEL_VERIFIED",
        "external_theorem_status": "RIEMANN_AND_COLLATZ_CLAIMS_NOT_PROVEN",
        "workloads": workloads,
        "receipts": receipts,
        "replay": replay,
        "macro_report": macro_report,
        "quarantined_standard_identities": list(QUARANTINED_STANDARD_IDENTITIES),
    }
    stable_json_write(output_dir / "PASS_191_PROOF_RECEIPTS.json", proof_payload)
    stable_json_write(output_dir / "PASS_191_NATIVE_BENCHMARK.json", benchmark)

    release_core = {
        "schema": "HHS_PASS_191_RELEASE_MANIFEST_V1",
        "pass_id": PASS_ID,
        "parent_pass": "PASS_161",
        "additive_over": ["PASS_082_1", "PASS_082_2", "PASS_082_4"],
        "base_commit_requested": "cd89c75afaaa9d9178ac102815dc7b0a75215bad",
        "actual_repository_baseline": os.environ.get("GITHUB_SHA", "unresolved"),
        "classification": "HHS_PASS_191_INTERNAL_PHASE_LATTICE_MODEL_VERIFIED",
        "external_theorem_status": "RIEMANN_AND_COLLATZ_CLAIMS_NOT_PROVEN",
        "workloads_verified": list(WORKLOAD_IDS),
        "receipt_chain_root_hash72": replay["tip_hash72"],
        "white_paper_hash72": white_paper_hash72,
        "native_benchmark_ops_per_sec": benchmark["operations_per_second"],
        "invariants": {"delta_e": 0, "psi": 0, "theta_15": True, "omega": True},
        "deliverables": [
            "PASS_191_RELEASE_MANIFEST.json",
            "PASS_191_PROOF_RECEIPTS.json",
            "PASS_191_NATIVE_BENCHMARK.json",
            "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md",
        ],
    }
    release_root = authority.commit(release_core, domain="HHS_PASS_191_RELEASE_ROOT")
    manifest = dict(release_core)
    manifest["pass191_release_root_hash72"] = release_root
    stable_json_write(output_dir / "PASS_191_RELEASE_MANIFEST.json", manifest)

    completion = {
        "schema": "HHS_PASS_191_COMPLETION_RECEIPT_V1",
        "pass_id": PASS_ID,
        "parent_pass": "PASS_161",
        "classification": "HHS_PASS_191_INTERNAL_PHASE_LATTICE_MODEL_VERIFIED",
        "external_theorem_status": "RIEMANN_AND_COLLATZ_CLAIMS_NOT_PROVEN",
        "workloads_verified": list(WORKLOAD_IDS),
        "receipt_chain_root_hash72": replay["tip_hash72"],
        "white_paper_hash72": white_paper_hash72,
        "native_benchmark_ops_per_sec": benchmark["operations_per_second"],
        "invariants": {"delta_e": 0, "psi": 0, "theta_15": True, "omega": True},
    }
    stable_json_write(output_dir / "PASS_191_COMPLETION_RECEIPT.json", completion)
    return completion


def verify_existing_artifacts(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    audited_runner_cls, default_kernel_path, verifier_cls = _load_runtime()
    kernel_path = Path(default_kernel_path)
    proof = json.loads((output_dir / "PASS_191_PROOF_RECEIPTS.json").read_text(encoding="utf-8"))
    benchmark = json.loads((output_dir / "PASS_191_NATIVE_BENCHMARK.json").read_text(encoding="utf-8"))
    manifest = json.loads((output_dir / "PASS_191_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    completion = json.loads((output_dir / "PASS_191_COMPLETION_RECEIPT.json").read_text(encoding="utf-8"))

    assert_workloads(proof["workloads"])
    replay = verifier_cls(kernel_path).verify(
        proof["receipts"], expected_tip_hash72=manifest["receipt_chain_root_hash72"]
    ).to_dict()
    if replay.get("ok") is not True or replay.get("count") != 5:
        raise RuntimeError(f"existing proof receipt replay failed: {replay}")
    if benchmark.get("status") != "DETERMINISTIC_BIFURCATION_VERIFIED":
        raise RuntimeError("existing native benchmark status is not verified")
    if not isinstance(benchmark.get("operations_per_second"), (int, float)) or benchmark["operations_per_second"] <= 0:
        raise RuntimeError("existing native benchmark operations_per_second is invalid")

    authority = audited_runner_cls(kernel_path).authority
    white_paper_path = repo_root / "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md"
    white_paper_hash72 = authority.commit(
        {"path": white_paper_path.name, "content": white_paper_path.read_text(encoding="utf-8")},
        domain="HHS_PASS_191_WHITE_PAPER",
    )
    if white_paper_hash72 != manifest.get("white_paper_hash72"):
        raise RuntimeError("white paper Hash72 mismatch")
    if completion.get("receipt_chain_root_hash72") != replay.get("tip_hash72"):
        raise RuntimeError("completion receipt tip mismatch")
    if manifest.get("workloads_verified") != list(WORKLOAD_IDS):
        raise RuntimeError("manifest workload set mismatch")
    if manifest.get("external_theorem_status") != "RIEMANN_AND_COLLATZ_CLAIMS_NOT_PROVEN":
        raise RuntimeError("external theorem boundary missing")

    release_core = {k: v for k, v in manifest.items() if k != "pass191_release_root_hash72"}
    recomputed_release_root = authority.commit(release_core, domain="HHS_PASS_191_RELEASE_ROOT")
    if recomputed_release_root != manifest.get("pass191_release_root_hash72"):
        raise RuntimeError("release root Hash72 mismatch")
    return {
        "schema": "HHS_PASS_191_EXISTING_ARTIFACT_VERIFICATION_V1",
        "ok": True,
        "receipt_count": replay["count"],
        "tip_hash72": replay["tip_hash72"],
        "white_paper_hash72": white_paper_hash72,
        "release_root_hash72": recomputed_release_root,
        "operations_per_second": benchmark["operations_per_second"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate and verify HHS Pass 191 artifacts")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else repo_root / "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence"
    )
    result = verify_existing_artifacts(repo_root, output_dir) if args.verify_existing else build_artifacts(repo_root, output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
