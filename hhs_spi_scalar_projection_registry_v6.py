"""Pass 219 SPI Scalar Projection Registry v6.

Additive successor to v5.  v6 registers the exact constraint/evolution
learning optimizer lifecycle:

    FORMALIZE -> PROVE -> IMPLEMENT -> OPTIMIZE -> CANONIZE -> ITERATE

The new proof is candidate/projection-only and preserves every v5 proof object
unchanged.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from hhs_spi_constraint_evolution_optimizer_v1 import (
    LIFECYCLE,
    VM5184_ADDRESS_COUNT,
    reference_optimizer_cycle,
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
from hhs_spi_scalar_projection_registry_v5 import (
    AUDITED_MAIN_SHA,
    build_registry_v5,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V6"
VERSION = "6.0.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V6"
OPTIMIZER_PROOF_ID = "SPI-CONSTRAINT-EVOLUTION-LEARNING-OPTIMIZER"


class SPIRegistryV6Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _optimizer_proof() -> ProjectionProof:
    witness = reference_optimizer_cycle()
    return ProjectionProof(
        proof_id=OPTIMIZER_PROOF_ID,
        source_expression=(
            "FORMALIZE->PROVE->IMPLEMENT->OPTIMIZE->CANONIZE->ITERATE; "
            "A={c|Formalized(c)∧Proved(c)∧Implemented(c)}; "
            "c*=argmin_A(unresolved,-reuse,stable_id)"
        ),
        profile="HARMONICODE-CONSTRAINT-EVOLUTION-LEARNING-OPTIMIZER-v1",
        premises=(
            "SPI-TENSOR-TRANSLATION-STACK",
            "81×64=5184 exact VM81 knowledge-coordinate factorization",
            "four hydration lanes retain typed lane identity without independent canonical authority",
            "candidate optimization is exact and subordinate to singleton VM81 admission",
        ),
        domain=(
            "already-proved SPI tensor-translation candidates with exact integer branch/reuse work, "
            "typed four-lane/VM5184 coordinates, and no canonical mutation authority"
        ),
        derivation=(
            "construct candidate only above a closed tensor-translation predecessor receipt",
            "require FORMALIZE, PROVE, and IMPLEMENT gates to pass before optimization",
            "bind one exact address5184=cell81*64+operation64 and one typed hydration-lane coordinate",
            "conserve structural work as unresolved=branch_count-reusable_branch_count",
            "select deterministically by minimum unresolved work, then maximum proved reuse, then stable id",
            "exclude semantic labels and floating-point values from selection authority",
            "emit projection-receipt canonization eligibility and a deterministic next-cycle FORMALIZE seed",
            "retain VM81/Hash72/Hash216/persistence authority outside the optimizer",
        ),
        result={
            "lifecycle": list(LIFECYCLE),
            "vm5184_address_count": VM5184_ADDRESS_COUNT,
            "four_lane_hydration": True,
            "selection_rule": witness["selection_rule"],
            "selected_reference_candidate": witness["selected_candidate_id"],
            "selected_reference_score": witness["selected_score"],
            "semantic_label_used_for_selection": witness["semantic_label_used_for_selection"],
            "empirical_speedup_claimed": witness["empirical_speedup_claimed"],
            "canonization_scope": witness["canonization"]["scope"],
            "next_cycle": witness["iteration_seed"]["next_cycle"],
            "hash216_vector_store_reference_eligible": witness["knowledge_graph"]["hash216_vector_store_reference_eligible"],
            "canonical_hash216_minted": witness["knowledge_graph"]["canonical_hash216_minted"],
            "reference_receipt_sha256": witness["receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "structural branch/reuse score does not encode candidate semantic meaning",
            "VM5184/lane metadata does not itself encode the full native tensor state",
            "projection optimizer canonization eligibility is not repository-main or VM81-state canonization",
            "Hash216 vector-store reference eligibility does not mint canonical Hash216 lineage",
            "no empirical latency/compression result is implied by structural branch reduction",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_INTEGER_CONSTRAINT_EVOLUTION_OPTIMIZATION",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "The lifecycle is executable as a candidate-learning optimizer without creating a second transition authority.",
        ),
    )


def build_registry_v6(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    base = build_registry_v5(repo_root)
    successor = dict(base)
    proof = _optimizer_proof()
    if proof.proof_id in successor:
        raise SPIRegistryV6Error(f"v6 proof id collision: {proof.proof_id}")
    successor[proof.proof_id] = proof
    return successor


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors: list[str] = []
    base = build_registry_v5(repo_root)
    try:
        registry = build_registry_v6(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V6",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }

    new_ids = sorted(set(registry) - set(base))
    if new_ids != [OPTIMIZER_PROOF_ID]:
        errors.append(f"unexpected v6 proof delta: {new_ids}")

    changed = [
        proof_id
        for proof_id in sorted(base)
        if registry[proof_id].to_dict() != base[proof_id].to_dict()
    ]
    if changed:
        errors.append(f"v6 modified predecessor proofs: {changed}")

    proof = registry[OPTIMIZER_PROOF_ID]
    if proof.result.get("vm5184_address_count") != 5184:
        errors.append("VM5184 cardinality drifted")
    if proof.result.get("semantic_label_used_for_selection") is not False:
        errors.append("semantic selection authority drifted")
    if proof.result.get("empirical_speedup_claimed") is not False:
        errors.append("unmeasured empirical speedup claim appeared")
    if proof.result.get("canonical_hash216_minted") is not False:
        errors.append("optimizer minted canonical Hash216")
    if any(item.canonical_admission for item in registry.values()):
        errors.append("v6 registry contains canonical admission authority")

    counts = Counter(item.coverage_state for item in registry.values())
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V6",
        "ok": not errors,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "proof_count": len(registry),
        "new_proof_ids": new_ids,
        "changed_predecessor_proof_ids": changed,
        "lifecycle": list(LIFECYCLE),
        "vm5184_address_count": 5184,
        "semantic_meaning_downstream_of_selection_constraints": True,
        "coverage": dict(sorted(counts.items())),
        "canonical_admission_authority": False,
        "errors": errors,
    }


def coverage_manifest_v6(repo_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_registry_v6(repo_root)
    validation = validation_report(repo_root)
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_format": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V5",
        "transition_policy": "ADDITIVE_SUCCESSOR_CONSTRAINT_EVOLUTION_OPTIMIZER_ONLY",
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "candidate_only": True,
            "semantic_selection_authority": False,
            "vm81_mutation": False,
            "canonical_hash72_hash216_minting": False,
            "canonical_persistence": False,
            "floating_point_authority": False,
            "unmeasured_speedup_claim": False,
        },
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = validation_report() if args.validate else coverage_manifest_v6()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str))
    if args.validate and not payload.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
