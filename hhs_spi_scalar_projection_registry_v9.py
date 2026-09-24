"""Pass 219 SPI Scalar Projection Registry v9.

Additive successor to v8.

v9 registers projection-only scalar faces for the newly receipt-bound harmonic
modulus/G72 bridge and names two distinct Delta projection states without
collapsing them into one constructor identity.

Authority boundary
------------------
- Native G72 remains the immutable ordered generator.  v9 does not scalarize
  or replace it; it only registers pi_SigmaScalar(G72)=2^(1/72).
- The HARMONICODE symbol written u^72/u⁷² in the master chain is registered in
  this projection as the closure assignment U72 := 2/ubar^2, not ordinary
  exponentiation ubar^72.
- Sigma_Delta_m and Sigma_Delta_R are distinct projection states.  Cross-state
  substitution is forbidden without an explicit bridge receipt.
- DELTA_P_ROOT remains symbolically registered/open for canonical lowering.
- No VM81, Hash72, Hash216, persistence, or canonical admission authority is
  introduced.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict

from hhs_spi_scalar_projection_registry_v1 import (
    CLOSED,
    IMPLEMENTED,
    NONE,
    NOT_EMITTED,
    NOT_IMPLEMENTED,
    OPEN,
    PARTIAL,
    PROJECTION_ONLY,
    PROVEN,
    SYMBOLIC,
    VERIFIED,
    ProjectionProof,
)
from hhs_spi_scalar_projection_registry_v8 import (
    AUDITED_MAIN_SHA,
    build_registry_v8,
)
from hhs_runtime.hhs_pass220_144cell_epsilon_lo_shu_closure_v1 import (
    g72_generator_descriptor,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V9"
VERSION = "9.0.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V9"

HARMONIC_MODULUS_PROOF_ID = "SPI-HARMONIC-MODULUS-U72-CLOSURE-ASSIGNMENT"
G72_SCALAR_FACE_PROOF_ID = "SPI-G72-SCALAR-PROJECTION-FACE"
DELTA_SIGMA_M_PROOF_ID = "SPI-DELTA-SIGMA-M-CLOSURE-PROJECTION"
DELTA_SIGMA_R_PROOF_ID = "SPI-DELTA-SIGMA-R-ROOT-PHASE-PROJECTION"

NEW_PROOF_IDS = (
    DELTA_SIGMA_M_PROOF_ID,
    DELTA_SIGMA_R_PROOF_ID,
    G72_SCALAR_FACE_PROOF_ID,
    HARMONIC_MODULUS_PROOF_ID,
)


class SPIRegistryV9Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _closed_projection(
    *,
    proof_id: str,
    source_expression: str,
    profile: str,
    premises: tuple[str, ...],
    domain: str,
    derivation: tuple[str, ...],
    result: Any,
    lost_information: tuple[str, ...],
    scalar_type: str,
    reverse_lift_status: str = NONE,
    notes: tuple[str, ...] = (),
) -> ProjectionProof:
    return ProjectionProof(
        proof_id=proof_id,
        source_expression=source_expression,
        profile=profile,
        premises=premises,
        domain=domain,
        derivation=derivation,
        result=result,
        modulus=None,
        residual=Fraction(0),
        lost_information=lost_information,
        reverse_lift_status=reverse_lift_status,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type=scalar_type,
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=notes,
    )


def _harmonic_modulus_projection() -> ProjectionProof:
    return _closed_projection(
        proof_id=HARMONIC_MODULUS_PROOF_ID,
        source_expression="u⁷² := b²/a⁴ = b²x⁴ = 2/ū²",
        profile="HARMONIC-MODULUS-CLOSURE-ASSIGNMENT-SIGMA-SCALAR-v1",
        premises=(
            "licensed scalar face only",
            "b²=2",
            "a²=ū",
            "x²=1/ū",
            "ū>0",
        ),
        domain=(
            "Sigma_scalar with positive algebraic sextic-state symbol ū; "
            "the exact defining sextic polynomial is not reconstructed by this registry entry"
        ),
        derivation=(
            "a⁴=(a²)²=ū² on the licensed scalar face",
            "b²/a⁴=2/ū²",
            "x⁴=(x²)²=1/ū²",
            "b²x⁴=2/ū²",
            "bind the native harmonic-modulus label u⁷² to this closure value",
            "do not rewrite the label as ordinary exponentiation ū^72",
        ),
        result={
            "native_label": "u⁷²",
            "projection_symbol": "U72",
            "projection_value": "2/ū²",
            "equivalent_faces": ("b²/a⁴", "b²x⁴", "2/ū²"),
            "ordinary_power_ubar_72_authorized": False,
            "native_constructor_rewritten": False,
        },
        lost_information=(
            "native phase/lattice ancestry of the u⁷² label",
            "the exact sextic polynomial/root-isolation certificate for ū",
            "ordered source-occurrence identity beyond the retained face list",
        ),
        scalar_type="EXACT_SYMBOLIC_ALGEBRAIC_PROJECTION_FACE",
        notes=(
            "This proof closes the projection assignment, not an ordinary power identity.",
        ),
    )


def _g72_scalar_face_projection() -> ProjectionProof:
    descriptor = g72_generator_descriptor()
    return _closed_projection(
        proof_id=G72_SCALAR_FACE_PROOF_ID,
        source_expression="π_Σscalar(G72)=2^(1/72)",
        profile="G72-NATIVE-GENERATOR-SCALAR-FACE-v1",
        premises=(
            HARMONIC_MODULUS_PROOF_ID,
            "native G72 source_term=2^(1/72)",
            "native G72 immutable_generator=true",
            "native G72 scalar preemption remains forbidden",
        ),
        domain=(
            "projection-only algebraic radical face; native G72 routing remains ordered and unresolved as a runtime operator"
        ),
        derivation=(
            "read the inherited exact source term 2^(1/72) from the native G72 descriptor",
            "register that radical as the Sigma_scalar observation face",
            "preserve the native generator object and route semantics unchanged",
            "the scalar face satisfies (2^(1/72))^72=2",
        ),
        result={
            "native_operator": descriptor["operator"],
            "native_source_term": descriptor["source_term"],
            "native_immutable_generator": descriptor["immutable_generator"],
            "scalar_projection_face": "2^(1/72)",
            "scalar_face_72_power": "2",
            "native_generator_unchanged": True,
            "scalar_preemption_authorized": False,
        },
        lost_information=(
            "native route/tooth occurrence identity",
            "noncommutative ordered transition ancestry",
            "Hash72/Hash216 lineage",
        ),
        scalar_type="EXACT_ALGEBRAIC_RADICAL_PROJECTION_FACE",
        notes=(
            "Projection equality does not identify the native generator with a conventional scalar object.",
        ),
    )


def _delta_sigma_m_projection() -> ProjectionProof:
    return _closed_projection(
        proof_id=DELTA_SIGMA_M_PROOF_ID,
        source_expression=(
            "Σ_Δm: c²P(q-p)/(p+q)=a²+b²=(P²-pq)mc²/Δ"
        ),
        profile="DELTA-CLOSURE-MEMBRANE-SCALAR-PROJECTION-v1",
        premises=(
            "p=P-1",
            "q=P+1",
            "P!=0",
            "P²-pq=1",
            "c²=a²+b²",
            "c²!=0",
            "m!=0",
            "Δ!=0",
            "scalar cancellation licensed only inside this projection",
        ),
        domain=(
            "Sigma_Delta_m closure membrane scalar face; not a native constructor identity"
        ),
        derivation=(
            "(q-p)P/(p+q)=2P/(2P)=1",
            "first face reduces to c²",
            "P²-pq=1 reduces the third face to m c²/Δ",
            "within the licensed nonzero scalar face c²=m c²/Δ iff Δ=m",
        ),
        result={
            "projection_state": "Σ_Δm",
            "delta_evaluation": "m",
            "global_constructor_identity": False,
            "cross_projection_substitution_authorized": False,
        },
        lost_information=(
            "native Delta denominator provenance",
            "non-scalar membrane/address state",
            "other Delta projection evaluations",
        ),
        scalar_type="PARAMETRIC_EXACT_SCALAR_GATE_PROJECTION",
        notes=(
            "Δ=m is a projection evaluation in Σ_Δm only.",
        ),
    )


def _delta_sigma_r_projection() -> ProjectionProof:
    return ProjectionProof(
        proof_id=DELTA_SIGMA_R_PROOF_ID,
        source_expression="Σ_ΔR: Δ/P = Sqrt(pq+U72)^x²",
        profile="DELTA-ROOT-PHASE-PROJECTION-REGISTRATION-v1",
        premises=(
            HARMONIC_MODULUS_PROOF_ID,
            "p=P-1",
            "q=P+1",
            "x²=1/ū on the licensed Genesis scalar face",
        ),
        domain=(
            "named root/phase projection state; exact native DELTA_P_ROOT lowering remains unresolved"
        ),
        derivation=(
            "substitute the registered scalar-face symbols without cross-projecting Delta",
            "record Δ -> P*(Sqrt[(P-1)(P+1)+2/ū²])^(1/ū) as the Sigma_Delta_R face",
            "retain the expression symbolically",
            "forbid substitution of the Sigma_Delta_m value m without a separate bridge receipt",
        ),
        result={
            "projection_state": "Σ_ΔR",
            "delta_evaluation": "P*(Sqrt[(P-1)(P+1)+2/ū²])^(1/ū)",
            "registration_implemented": True,
            "exact_native_delta_p_root_lowering": False,
            "cross_projection_substitution_authorized": False,
        },
        modulus=None,
        residual=None,
        lost_information=(
            "full native DELTA_P_ROOT operator semantics",
            "exact sextic polynomial/root-isolation certificate for ū",
            "any bridge between Σ_ΔR and Σ_Δm",
        ),
        reverse_lift_status=NONE,
        proof_status=OPEN,
        implementation_status=NOT_IMPLEMENTED,
        receipt_status=NOT_EMITTED,
        coverage_state=SYMBOLIC,
        scalar_type="SYMBOLIC_NAMED_PROJECTION_STATE",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "The projection state is registered; the canonical native clause remains fail-closed/unlowered.",
        ),
    )


def build_registry_v9(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    base = build_registry_v8(repo_root)
    successor = dict(base)
    additions = (
        _harmonic_modulus_projection(),
        _g72_scalar_face_projection(),
        _delta_sigma_m_projection(),
        _delta_sigma_r_projection(),
    )
    for proof in additions:
        if proof.proof_id in successor:
            raise SPIRegistryV9Error(f"v9 proof id collision: {proof.proof_id}")
        successor[proof.proof_id] = proof
    return successor


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors: list[str] = []
    base = build_registry_v8(repo_root)
    try:
        registry = build_registry_v9(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V9",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }

    new_ids = sorted(set(registry) - set(base))
    expected = sorted(NEW_PROOF_IDS)
    if new_ids != expected:
        errors.append(f"unexpected v9 proof delta: {new_ids}")

    changed = [
        proof_id
        for proof_id in sorted(base)
        if registry[proof_id].to_dict() != base[proof_id].to_dict()
    ]
    if changed:
        errors.append(f"v9 modified predecessor proofs: {changed}")

    u72 = registry[HARMONIC_MODULUS_PROOF_ID]
    g72 = registry[G72_SCALAR_FACE_PROOF_ID]
    delta_m = registry[DELTA_SIGMA_M_PROOF_ID]
    delta_r = registry[DELTA_SIGMA_R_PROOF_ID]

    if u72.result.get("ordinary_power_ubar_72_authorized") is not False:
        errors.append("U72 projection gained ordinary-power rewrite authority")
    if g72.result.get("native_generator_unchanged") is not True:
        errors.append("G72 native generator was not preserved")
    if g72.result.get("scalar_preemption_authorized") is not False:
        errors.append("G72 scalar preemption became authorized")
    if delta_m.result.get("global_constructor_identity") is not False:
        errors.append("Sigma_Delta_m escaped projection scope")
    if delta_r.proof_status != OPEN or delta_r.coverage_state != SYMBOLIC:
        errors.append("Sigma_Delta_R native lowering was incorrectly closed")
    if delta_r.result.get("cross_projection_substitution_authorized") is not False:
        errors.append("Delta cross-projection substitution became authorized")
    if any(item.canonical_admission for item in registry.values()):
        errors.append("v9 registry contains canonical admission authority")

    counts = Counter(item.coverage_state for item in registry.values())
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V9",
        "ok": not errors,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "proof_count": len(registry),
        "new_proof_ids": new_ids,
        "changed_predecessor_proof_ids": changed,
        "harmonic_modulus_projection_closed": u72.proof_status == CLOSED,
        "g72_scalar_face_closed": g72.proof_status == CLOSED,
        "delta_sigma_m_closed": delta_m.proof_status == CLOSED,
        "delta_sigma_r_named_but_native_lowering_open": (
            delta_r.proof_status == OPEN and delta_r.coverage_state == SYMBOLIC
        ),
        "cross_projection_substitution_authorized": False,
        "coverage": dict(sorted(counts.items())),
        "canonical_admission_authority": False,
        "errors": errors,
    }


def coverage_manifest_v9(repo_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_registry_v9(repo_root)
    validation = validation_report(repo_root)
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_format": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V8",
        "transition_policy": "ADDITIVE_SUCCESSOR_HARMONIC_DELTA_PROJECTION_FACES_ONLY",
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "native_g72_unchanged": True,
            "u72_ordinary_power_rewrite": False,
            "delta_projection_states_distinct": True,
            "cross_projection_substitution": False,
            "delta_p_root_native_lowering_closed": False,
            "vm81_mutation": False,
            "canonical_hash72_hash216_minting": False,
            "canonical_persistence": False,
            "floating_point_authority": False,
        },
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


if __name__ == "__main__":
    report = validation_report()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    raise SystemExit(0 if report.get("ok") else 1)
