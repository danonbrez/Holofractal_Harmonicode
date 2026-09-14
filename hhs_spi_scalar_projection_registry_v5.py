"""Pass 219 SPI Scalar Projection Registry v5.

Additive successor to v4.  v5 registers the tensor-pair translation stack:

1. same-sized equal-sum tensor equation normalization at a²=1;
2. exact Fibonacci/Pythagorean square-state scaling with symbolic Golden limit;
3. three-set cubic pair normalization t³=t+a², equivalently t³-t=a²=∆=1;
4. composition of all three surfaces without native tensor identity collapse.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from hhs_spi_equal_sum_tensor_translation_rule_v1 import lo_shu_translation_witness
from hhs_spi_equal_sum_tensor_translation_rule_v2 import full_sudoku_translation_witness
from hhs_spi_fibonacci_pythagorean_scaling_rule_v1 import (
    pythagorean_base_witness,
    scale_ladder_witness,
)
from hhs_spi_tensor_pair_cubic_normalization_rule_v1 import (
    SOURCE_RELATION as CUBIC_RELATION,
    RESIDUAL_RELATION as CUBIC_RESIDUAL_RELATION,
    tensor_pair_cubic_witness,
)
from hhs_spi_tensor_pair_translation_stack_v1 import (
    lo_shu_translation_stack,
    sudoku_translation_stack,
)
from hhs_spi_scalar_projection_registry_v1 import (
    CLOSED,
    IMPLEMENTED,
    NONE,
    PROJECTION_ONLY,
    PROVEN,
    VERIFIED,
    ProjectionProof,
)
from hhs_spi_scalar_projection_registry_v4 import (
    AUDITED_MAIN_SHA,
    HIERARCHY_PROOF_ID,
    build_registry_v4,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V5"
VERSION = "5.0.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V5"
EQUAL_SUM_PROOF_ID = "SPI-TENSOR-EQUAL-SUM-A2"
FIBONACCI_SCALE_PROOF_ID = "SPI-TENSOR-FIB-PYTH-GOLDEN"
CUBIC_THREESET_PROOF_ID = "SPI-TENSOR-CUBIC-THREESET"
STACK_PROOF_ID = "SPI-TENSOR-TRANSLATION-STACK"


class SPIRegistryV5Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _equal_sum_proof() -> ProjectionProof:
    loshu = lo_shu_translation_witness()
    sudoku = full_sudoku_translation_witness()
    return ProjectionProof(
        proof_id=EQUAL_SUM_PROOF_ID,
        source_expression="same_shape(Ts,Tt) ∧ SumEq(Ts)=SumEq(Tt)=S ⇒ N_a²(Ts)=N_a²(Tt)=1",
        profile="EQUAL-SUM-SAME-SHAPE-TENSOR-A2-NORMALIZATION-v2",
        premises=(
            "SPI-LAW1-A2-LOCAL-SCALE: pi_L(a²)=1",
            "Pass171 Lo Shu nucleus: every row/column/principal diagonal sum is 15",
            "Pass171 Sudoku group closure: each 1..9 group has exact sum 45",
        ),
        domain="same-sized tensors with matching exact nonzero invariant-sum equation family and explicit symmetry/provenance",
        derivation=(
            "bind exact source and target tensor shapes",
            "verify every declared source and target sum equation equals the same exact nonzero S",
            "normalize each equation by S and multiply by local scale pi_L(a²)=1",
            "obtain exact unit for each declared equation on both tensors",
            "authorize equation-level translation only; retain all native tensor cell/order/provenance identity",
        ),
        result={
            "local_scale": "a²=1",
            "lo_shu_sum": 15,
            "lo_shu_equation_count": loshu["sum_equation_count"],
            "sudoku_sum": 45,
            "sudoku_equation_count": sudoku["complete_sudoku_equation_count"],
            "same_shape_required": True,
            "cellwise_tensor_identity_authorized": False,
            "lo_shu_receipt_sha256": loshu["receipt_sha256"],
            "sudoku_receipt_sha256": sudoku["receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "normalized unit equations do not encode tensor cell values or coordinate order",
            "equal sums do not imply native tensor equality",
            "symmetry orientation and source provenance must remain attached",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_TENSOR_SUM_NORMALIZATION",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=("Translation is between normalized sum equations, not native tensors.",),
    )


def _fibonacci_scale_proof() -> ProjectionProof:
    base = pythagorean_base_witness()
    ladder = scale_ladder_witness(9)
    return ProjectionProof(
        proof_id=FIBONACCI_SCALE_PROOF_ID,
        source_expression="a²=1,b²=2,c²=a²+b²=3; Q[n+1]=Q[n]+Q[n-1]; lambda[n]=Q[n+1]/Q[n]",
        profile="FIBONACCI-PYTHAGOREAN-GOLDEN-TENSOR-SCALE-v1",
        premises=(
            "SPI-PROJ-0001: pi(a²)=1",
            "SPI-PROJ-0002: pi(b²)=2",
            "SPI-T6: a²+b²=c²",
            "Pass152 GFCC exact Fibonacci recurrence and symbolic Golden limit",
        ),
        domain="equal-sum tensor projection layers after a² normalization; exact rational finite stages only",
        derivation=(
            "seed square-state scale with a²=1 and b²=2",
            "close c²=a²+b²=3",
            "iterate exact Fibonacci recurrence Q[n+1]=Q[n]+Q[n-1]",
            "use exact finite stage ratio lambda[n]=Q[n+1]/Q[n] for adjacent scale translation",
            "retain Phi only as positive symbolic root Phi²-Phi-1=0 and never substitute a floating approximation",
        ),
        result={
            "pythagorean_seed": "a²+b²=c²",
            "base_square_states": [1, 2, 3, 5, 8],
            "finite_ratios_exact": True,
            "golden_limit": "Phi²-Phi-1=0; positive root",
            "finite_ratio_replaced_by_phi": False,
            "base_receipt_sha256": base["receipt_sha256"],
            "ladder_receipt_sha256": ladder["receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "a scalar scale coordinate does not encode tensor cells",
            "finite stage index and recurrence ancestry must remain attached",
            "symbolic Golden limit does not replace exact finite ratios",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_FIBONACCI_SCALE_WITH_SYMBOLIC_LIMIT",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=("No floating-point Golden ratio is authoritative.",),
    )


def _cubic_three_set_proof() -> ProjectionProof:
    witness = tensor_pair_cubic_witness(
        pair_layer_id="REGISTRY:GENERIC-SAME-SHAPE-EQUAL-SUM-PAIR",
        source_tensor_id="Ts",
        target_tensor_id="Tt",
        source_shape=(3, 3),
        target_shape=(3, 3),
        equal_sum_normalized=True,
    )
    return ProjectionProof(
        proof_id=CUBIC_THREESET_PROOF_ID,
        source_expression=CUBIC_RELATION,
        profile="TENSOR-PAIR-THREE-SET-CUBIC-NORMALIZATION-v1",
        premises=(
            EQUAL_SUM_PROOF_ID,
            "SPI-LAW1-0008-T3MINUST: pi(t³-t)=1",
            "SPI-LAW1-0001-A2: pi(a²)=1",
            "SPI-LAW1-DELTA-UNIVERSAL-DENOMINATOR: pi(∆)=1",
        ),
        domain="same-sized tensor pair after equal-sum a² normalization",
        derivation=(
            "preserve native t³, t, a², and ∆ nodes without solving native t",
            "use pi(t³-t)=1 and pi(a²)=1",
            "close pi(t³-t-a²)=1-1=0",
            "bind the same unit to pi(∆)=1",
            "record the three-set relation t³=t+a² at the tensor-pair projection layer",
        ),
        result={
            "three_set": ["t³", "t", "a²"],
            "relation": CUBIC_RELATION,
            "residual_relation": CUBIC_RESIDUAL_RELATION,
            "native_t_solved": False,
            "witness_receipt_sha256": witness["receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "the residual unit does not determine native t",
            "tensor topology is not represented by the cubic relation",
            "native t³/t/a²/∆ identity remains typed and source-bound",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_CUBIC_RESIDUAL_NORMALIZATION",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=("t³=t+a² is a tensor-pair scalar projection constraint, not a scalar solution for t.",),
    )


def _stack_proof() -> ProjectionProof:
    loshu = lo_shu_translation_stack(4)
    sudoku = sudoku_translation_stack(4)
    return ProjectionProof(
        proof_id=STACK_PROOF_ID,
        source_expression="EqualSum_a² ∘ FibonacciPythagoreanScale ∘ CubicThreeSet",
        profile="HARMONICODE-TENSOR-PAIR-TRANSLATION-STACK-v1",
        premises=(EQUAL_SUM_PROOF_ID, FIBONACCI_SCALE_PROOF_ID, CUBIC_THREESET_PROOF_ID, HIERARCHY_PROOF_ID),
        domain="admitted same-sized equal-sum tensor pairs with exact scale-stage and projection ancestry",
        derivation=(
            "close equal-sum tensor equations at local scale a²=1",
            "assign the shared exact Fibonacci square-state scale coordinate",
            "apply exact adjacent finite-stage ratios for cross-scale translation",
            "close each tensor pair with t³=t+a² and universal ∆=1 denominator normalization",
            "retain native tensor identities and canonical VM81 authority outside the projection membrane",
        ),
        result={
            "ordered_layers": [
                "EQUAL_SUM_A2_NORMALIZATION",
                "FIBONACCI_PYTHAGOREAN_SCALE",
                "TENSOR_PAIR_CUBIC_THREE_SET",
            ],
            "local_scale": "a²=1",
            "universal_denominator": "∆=1",
            "cubic_three_set": "t³=t+a²",
            "pythagorean_scale_seed": "a²+b²=c²",
            "golden_limit_symbolic": True,
            "lo_shu_stack_receipt_sha256": loshu["receipt_sha256"],
            "sudoku_stack_receipt_sha256": sudoku["receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "composite projection does not reconstruct native tensor cell states",
            "scale stage and source ancestry are required for reverse interpretation",
            "native t is not solved by cubic normalization",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_TENSOR_TRANSLATION_COMPOSITE_PROJECTION",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=("Composite layer supports translation/normalization but does not create a second execution authority.",),
    )


def build_registry_v5(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    base = build_registry_v4(repo_root)
    successor = dict(base)
    for proof in (_equal_sum_proof(), _fibonacci_scale_proof(), _cubic_three_set_proof(), _stack_proof()):
        if proof.proof_id in successor:
            raise SPIRegistryV5Error(f"v5 proof id collision: {proof.proof_id}")
        successor[proof.proof_id] = proof
    return successor


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors = []
    base = build_registry_v4(repo_root)
    try:
        registry = build_registry_v5(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V5",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }
    expected = sorted((EQUAL_SUM_PROOF_ID, FIBONACCI_SCALE_PROOF_ID, CUBIC_THREESET_PROOF_ID, STACK_PROOF_ID))
    new_ids = sorted(set(registry) - set(base))
    if new_ids != expected:
        errors.append(f"unexpected v5 proof delta: {new_ids}")
    changed = [proof_id for proof_id in sorted(base) if registry[proof_id].to_dict() != base[proof_id].to_dict()]
    if changed:
        errors.append(f"v5 modified predecessor proofs: {changed}")
    if registry[CUBIC_THREESET_PROOF_ID].result.get("relation") != "t³=t+a²":
        errors.append("cubic three-set relation drifted")
    if registry[STACK_PROOF_ID].result.get("pythagorean_scale_seed") != "a²+b²=c²":
        errors.append("tensor scale seed drifted")
    if any(proof.canonical_admission for proof in registry.values()):
        errors.append("v5 registry contains canonical admission authority")
    counts = Counter(proof.coverage_state for proof in registry.values())
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V5",
        "ok": not errors,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "proof_count": len(registry),
        "new_proof_ids": new_ids,
        "changed_predecessor_proof_ids": changed,
        "tensor_pair_three_set": "t³=t+a²",
        "tensor_scaling_law": "a²+b²=c² -> Fibonacci square-state recurrence -> symbolic Golden limit",
        "coverage": dict(sorted(counts.items())),
        "canonical_admission_authority": False,
        "errors": errors,
    }


def coverage_manifest_v5(repo_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_registry_v5(repo_root)
    validation = validation_report(repo_root)
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_format": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V4",
        "transition_policy": "ADDITIVE_SUCCESSOR_TENSOR_TRANSLATION_STACK_ONLY",
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "native_tensor_identity": False,
            "native_t_solved": False,
            "finite_ratio_replaced_by_phi": False,
            "vm81_mutation": False,
            "canonical_hash72_hash216_minting": False,
            "canonical_persistence": False,
            "floating_point_authority": False,
        },
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true")
    group.add_argument("--manifest", action="store_true")
    args = parser.parse_args(argv)
    if args.validate:
        report = validation_report()
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, default=str))
        return 0 if report["ok"] else 1
    print(json.dumps(coverage_manifest_v5(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
