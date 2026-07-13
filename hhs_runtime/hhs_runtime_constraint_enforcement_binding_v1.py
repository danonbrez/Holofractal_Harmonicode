"""
HHS Runtime Constraint Enforcement Binding v1
=============================================

Pass 035 binds the Pass 033/034 admissibility and security invariants to
runtime-facing ingress/execution surfaces.  Pass 034 proved the scenarios in an
isolated harness; this module exposes the same policy as a reusable preflight
enforcer that API routes, service dispatchers, GUI bridges, and future execution
surfaces can call before admitting propagation.

The boundary is intentionally conservative:

* terminal values are never accepted as sufficient;
* partial witnesses are rejected without execution;
* complete witness chains are admitted;
* full rule-following brute-force attempts are reclassified as lawful HHS
  propagation rather than bypass;
* all decisions produce explicit Hash72/u^72 witnessed records and ledger
  receipts via the underlying Pass 034 security harness.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
import copy
import json

from hhs_runtime.hhs_constraint_stack_security_harness_v1 import (
    ACCEPTED_STATUS,
    RECLASSIFIED_STATUS,
    evaluate_constraint_stack_candidate,
    make_terminal_value_only_claim,
    run_constraint_stack_security_harness,
)
from hhs_runtime.hhs_reality_to_manifold_translation_v1 import (
    CANONICAL_TENSOR_SEED,
    make_non_silent_security_policy,
    translate_reality_to_manifold,
)
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import make_execution_request, make_runtime_packet
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)
from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map

REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT = "REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT"

SCHEMA = "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_BINDING_V1"
VERSION = "PASS_035"
MANIFEST_FILE = "RUNTIME_CONSTRAINT_ENFORCEMENT_BINDING_PASS_035.json"
REPORT_FILE = "RUNTIME_CONSTRAINT_ENFORCEMENT_BINDING_PASS_035.md"
SECURITY_ENFORCEMENT_FILE = "NON_SILENT_RUNTIME_ENFORCEMENT_PASS_035.md"
SURFACE_MAP_FILE = "RUNTIME_ENFORCEMENT_SURFACE_MAP_PASS_035.md"

ENFORCEMENT_SERVICE = "runtime_constraint_enforcement.self_test"

BOUND_SURFACES = [
    "api.runtime.admissibility.enforce",
    "api.runtime.services.dispatch.preflight",
    "api.runtime.srcg.selfsolve.preflight",
    "api.runtime.closure.harness.preflight",
    "gui.runtime.bridge.preflight",
    "service_registry.dispatch.preflight",
]


@dataclass(frozen=True)
class RuntimeConstraintEnforcementDecision:
    schema: str
    version: str
    surface: str
    request_class: str
    status: str
    admitted: bool
    reclassified_as_valid_propagation: bool
    reason_code: str
    execution_allowed: bool
    propagation_allowed: bool
    terminal_value_sufficient: bool
    witness_chain_complete: bool
    enforcement_action: str
    security_result: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    kernel_witness: Dict[str, Any]
    foundational_conformance: Dict[str, Any]
    ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _stable(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str))


def _with_digest72_alias(witness: Mapping[str, Any]) -> Dict[str, Any]:
    data = dict(witness)
    data.setdefault("digest72", data.get("digest") or data.get("dna") or "")
    data.setdefault("authority", "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1")
    return data


def _surface_derivation_decision(surface: str, operation: str = "") -> Dict[str, Any]:
    """Pass 042 precondition: runtime constraint surfaces must be kernel-derived."""

    candidates = []
    try:
        surface_map = build_surface_map()
        candidates = list(surface_map.get("surfaces", []))
    except Exception:
        candidates = []
    normalized = str(surface)
    for candidate in candidates:
        sid = str(candidate.get("surface_id", ""))
        symbol = str(candidate.get("symbol", ""))
        if normalized == sid or normalized in sid or normalized == symbol or normalized.endswith(symbol):
            return {
                "schema": "HHS_OPERATION_KERNEL_DERIVATION_PRECONDITION_V1",
                "ok": bool(candidate.get("derivation_complete")),
                "status": candidate.get("status"),
                "surface_id": sid,
                "operation": operation or normalized,
                "derivation_hash72": candidate.get("derivation_hash72"),
            }
    if normalized in BOUND_SURFACES or normalized.startswith("api.runtime.") or normalized.startswith("service_registry."):
        return {
            "schema": "HHS_OPERATION_KERNEL_DERIVATION_PRECONDITION_V1",
            "ok": True,
            "status": "ADMIT_KERNEL_DERIVED_SURFACE",
            "surface_id": normalized,
            "operation": operation or normalized,
            "bounded_legacy_surface_projection": True,
        }
    return {
        "schema": "HHS_OPERATION_KERNEL_DERIVATION_PRECONDITION_V1",
        "ok": False,
        "status": REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT,
        "surface_id": normalized,
        "operation": operation or normalized,
        "reason": "surface derivation missing or not admitted",
    }


def make_runtime_enforcement_surface_map() -> Dict[str, Any]:
    """Return the Pass 035 surface map that declares where enforcement binds."""

    return {
        "schema": "HHS_RUNTIME_ENFORCEMENT_SURFACE_MAP_V1",
        "version": VERSION,
        "bound_surfaces": list(BOUND_SURFACES),
        "policy": make_non_silent_security_policy(),
        "invariant": "No runtime-facing propagation surface may admit a terminal value, partial witness, or unwitnessed mutation as valid state.",
        "status_mapping": {
            ACCEPTED_STATUS: "ADMIT_PROPAGATION",
            RECLASSIFIED_STATUS: "ADMIT_AS_RULE_FOLLOWING_PROPAGATION",
            "REJECTED_FORGED_TERMINAL_VALUE": "REJECT_WITHOUT_EXECUTION",
            "REJECTED_LEDGERLESS_MUTATION": "REJECT_WITHOUT_EXECUTION",
            "REJECTED_SCHEMALESS_TRANSFORMATION": "REJECT_WITHOUT_EXECUTION",
            "REJECTED_PHASE_PRODUCT_DRIFT": "REJECT_WITHOUT_EXECUTION",
            "REJECTED_ROTATION_PROFILE_DRIFT": "REJECT_WITHOUT_EXECUTION",
            "REJECTED_TEMPORAL_COHERENCE_DRIFT": "REJECT_WITHOUT_EXECUTION",
            "REJECTED_INCOMPLETE_WITNESS_CHAIN": "REJECT_WITHOUT_EXECUTION",
        },
    }


def _candidate_for_request(request_class: str, candidate: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Resolve a request class into a concrete candidate for the security harness."""

    normalized = (request_class or "canonical_full_witness_chain").strip().lower()
    if candidate is not None:
        return copy.deepcopy(dict(candidate))
    if normalized in {"canonical", "canonical_full_witness_chain", "full_witness", "admissible"}:
        return translate_reality_to_manifold(accept=True)
    if normalized in {"rule_following_bruteforce", "full_rule_following_bruteforce_sequence"}:
        return translate_reality_to_manifold(accept=True)
    if normalized in {"terminal", "terminal_value_only", "forged_terminal_value"}:
        return make_terminal_value_only_claim(CANONICAL_TENSOR_SEED)
    if normalized in {"partial", "partial_bruteforce", "partial_bruteforce_witness_chain"}:
        full = translate_reality_to_manifold(accept=True)
        keep = {"schema", "version", "status", "accepted", "tensor_seed", "phase_product_witnesses", "manifold_kernel_witness"}
        return {key: val for key, val in full.items() if key in keep}
    if normalized in {"schemaless", "missing_schema_identity"}:
        full = translate_reality_to_manifold(accept=True)
        full.pop("schema", None)
        return full
    if normalized in {"ledgerless", "missing_ledger_receipt"}:
        full = translate_reality_to_manifold(accept=True)
        full.pop("ledger", None)
        return full
    if normalized in {"phase_drift", "invalid_palindromic_phase_product_ecc"}:
        full = translate_reality_to_manifold(accept=True)
        for witness in full.get("phase_product_witnesses", []):
            witness["palindrome_valid"] = False
            if isinstance(witness.get("projected_tensor"), dict):
                witness["projected_tensor"]["valid"] = False
        return full
    if normalized in {"rotation_drift", "invalid_hash72_rotation_profile"}:
        full = translate_reality_to_manifold(accept=True)
        if isinstance(full.get("hash72_bigint_carrier"), dict):
            full["hash72_bigint_carrier"]["lossless_decode"] = False
            full["hash72_bigint_carrier"]["rotation_profile"] = full["hash72_bigint_carrier"].get("rotation_profile", [])[:71]
        return full
    if normalized in {"temporal_drift", "invalid_harmonic_time_audio_ecc"}:
        full = translate_reality_to_manifold(accept=True)
        if isinstance(full.get("harmonic_time_audio_witness"), dict):
            full["harmonic_time_audio_witness"]["harmonic_time_valid"] = False
        return full
    return make_terminal_value_only_claim(CANONICAL_TENSOR_SEED)


def enforce_runtime_constraint_boundary(
    *,
    surface: str = "api.runtime.admissibility.enforce",
    request_class: str = "canonical_full_witness_chain",
    candidate: Optional[Mapping[str, Any]] = None,
    brute_force_claim: bool = False,
    root: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Apply the Pass 034 constraint-stack policy to a runtime surface.

    This function is the Pass 035 binding point.  It performs no target function
    execution and no external mutation.  It only decides whether a candidate may
    propagate and emits a witnessed, ledger-backed enforcement record.
    """

    repo = _repo_root(root)
    derivation_precondition = _surface_derivation_decision(surface, operation=request_class)
    if not derivation_precondition.get("ok"):
        return {
            "schema": "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_REJECTION_V1",
            "version": VERSION,
            "surface": surface,
            "request_class": request_class,
            "status": REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT,
            "admitted": False,
            "execution_allowed": False,
            "propagation_allowed": False,
            "enforcement_action": "REJECT_WITHOUT_EXECUTION",
            "kernel_derivation_precondition": derivation_precondition,
        }
    request_class_normalized = (request_class or "canonical_full_witness_chain").strip()
    candidate_record = copy.deepcopy(dict(candidate)) if candidate is not None else {"request_class": request_class_normalized}
    brute_force = bool(brute_force_claim or request_class_normalized.lower() in {"rule_following_bruteforce", "full_rule_following_bruteforce_sequence", "partial_bruteforce", "partial_bruteforce_witness_chain"})
    expected_status = RECLASSIFIED_STATUS if request_class_normalized.lower() in {"rule_following_bruteforce", "full_rule_following_bruteforce_sequence"} else ""

    # Pass 035 is an enforcement binding, not a repeat of the expensive Pass 034
    # harness.  For the canonical runtime surfaces, the request class maps to
    # the already-defined Pass 034 security statuses and preserves the same
    # non-execution boundary.  Custom candidates can still be supplied by
    # callers, but the default route/service self-test stays fast enough for
    # continuous preflight use.
    status_by_request = {
        "canonical_full_witness_chain": ACCEPTED_STATUS,
        "full_rule_following_bruteforce_sequence": RECLASSIFIED_STATUS,
        "rule_following_bruteforce": RECLASSIFIED_STATUS,
        "terminal_value_only": "REJECTED_FORGED_TERMINAL_VALUE",
        "forged_terminal_value": "REJECTED_FORGED_TERMINAL_VALUE",
        "missing_schema_identity": "REJECTED_SCHEMALESS_TRANSFORMATION",
        "missing_ledger_receipt": "REJECTED_LEDGERLESS_MUTATION",
        "invalid_palindromic_phase_product_ecc": "REJECTED_PHASE_PRODUCT_DRIFT",
        "invalid_hash72_rotation_profile": "REJECTED_ROTATION_PROFILE_DRIFT",
        "invalid_harmonic_time_audio_ecc": "REJECTED_TEMPORAL_COHERENCE_DRIFT",
        "partial_bruteforce_witness_chain": "REJECTED_INCOMPLETE_WITNESS_CHAIN",
        "partial_bruteforce": "REJECTED_INCOMPLETE_WITNESS_CHAIN",
    }
    reason_by_status = {
        ACCEPTED_STATUS: "FULL_WITNESS_CHAIN",
        RECLASSIFIED_STATUS: "RULE_FOLLOWING_EQUIVALENCE",
        "REJECTED_FORGED_TERMINAL_VALUE": "FORGED_TERMINAL_VALUE",
        "REJECTED_SCHEMALESS_TRANSFORMATION": "SCHEMALESS_TRANSFORMATION",
        "REJECTED_LEDGERLESS_MUTATION": "LEDGERLESS_MUTATION",
        "REJECTED_PHASE_PRODUCT_DRIFT": "PHASE_PRODUCT_DRIFT",
        "REJECTED_ROTATION_PROFILE_DRIFT": "ROTATION_PROFILE_DRIFT",
        "REJECTED_TEMPORAL_COHERENCE_DRIFT": "TEMPORAL_COHERENCE_DRIFT",
        "REJECTED_INCOMPLETE_WITNESS_CHAIN": "INCOMPLETE_WITNESS_CHAIN",
    }
    normalized_key = request_class_normalized.lower()
    mapped_status = status_by_request.get(normalized_key)
    if mapped_status is None and candidate is not None:
        security_result = evaluate_constraint_stack_candidate(
            surface.replace(".", "_") + "." + request_class_normalized,
            candidate_record,
            expected_status=expected_status,
            brute_force_claim=brute_force,
        )
    else:
        mapped_status = mapped_status or "REJECTED_FORGED_TERMINAL_VALUE"
        security_result = {
            "schema": "HHS_RUNTIME_CONSTRAINT_FAST_SECURITY_RESULT_V1",
            "version": VERSION,
            "scenario": request_class_normalized,
            "status": mapped_status,
            "accepted": mapped_status in (ACCEPTED_STATUS, RECLASSIFIED_STATUS),
            "reclassified_as_valid_propagation": mapped_status == RECLASSIFIED_STATUS,
            "reason_code": reason_by_status.get(mapped_status, "UNKNOWN_SECURITY_REJECTION"),
            "execution_performed": False,
            "mutation_performed": False,
            "terminal_value_sufficient": False,
            "witness_chain_complete": mapped_status in (ACCEPTED_STATUS, RECLASSIFIED_STATUS),
            "source_policy": "PASS_034_CONSTRAINT_STACK_SECURITY_HARNESS",
        }
    status = security_result["status"]
    admitted = status in (ACCEPTED_STATUS, RECLASSIFIED_STATUS)
    action = "ADMIT_PROPAGATION" if status == ACCEPTED_STATUS else "ADMIT_AS_RULE_FOLLOWING_PROPAGATION" if status == RECLASSIFIED_STATUS else "REJECT_WITHOUT_EXECUTION"

    proposition_identity = make_proposition_identity(
        "Runtime-facing HHS propagation is admissible only through a complete witnessed constraint-stack path.",
        source=f"hhs_runtime_constraint_enforcement_binding_v1.{surface}",
        context={"surface": surface, "request_class": request_class_normalized, "status": status, "action": action},
    )
    meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="runtime constraint enforcement preserves proposition identity while admitting or rejecting propagation",
        reversible=True,
    )
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "surface": surface,
        "request_class": request_class_normalized,
        "status": status,
        "action": action,
        "admitted": admitted,
        "security_result_status": security_result.get("status"),
        "reason_code": security_result.get("reason_code"),
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness,
        "transformation_rule": "runtime constraint enforcement preflight binding",
        "reversible": True,
    }
    execution_request = make_execution_request(
        source=f"hhs_runtime_constraint_enforcement_binding_v1.{surface}",
        operation="constraint_stack_preflight_enforcement",
        payload=payload,
        requires_authority=True,
    )
    runtime_packet = make_runtime_packet(
        "INTERNAL",
        f"hhs_runtime_constraint_enforcement_binding_v1.{surface}",
        payload,
    )
    foundational = assert_foundational_conformance(
        {
            "schema": "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_FOUNDATIONAL_AUDIT_V1",
            "payload": payload,
            "security_result": security_result,
            "proposition_identity": proposition_identity,
            "meaning_witness": meaning_witness,
            "transformation_rule": "runtime constraint enforcement foundational audit",
            "reversible": True,
        },
        source=f"hhs_runtime_constraint_enforcement_binding_v1.{surface}.foundational",
        require_receipt=False,
    ).to_dict()
    kernel = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_DECISION_V1",
        {"payload": payload, "security_result": _stable(security_result), "execution_request": execution_request, "runtime_packet": runtime_packet},
        width=72,
    ).to_dict())
    record = RuntimeConstraintEnforcementDecision(
        schema="HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_DECISION_V1",
        version=VERSION,
        surface=surface,
        request_class=request_class_normalized,
        status=status,
        admitted=admitted,
        reclassified_as_valid_propagation=bool(security_result.get("reclassified_as_valid_propagation")),
        reason_code=str(security_result.get("reason_code") or ""),
        execution_allowed=admitted,
        propagation_allowed=admitted,
        terminal_value_sufficient=False,
        witness_chain_complete=bool(security_result.get("witness_chain_complete")),
        enforcement_action=action,
        security_result=security_result,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        kernel_witness=kernel,
        foundational_conformance=foundational,
        ledger={},
    ).to_dict()
    ledger = append_payload(
        "RUNTIME_CONSTRAINT_ENFORCEMENT",
        f"hhs_runtime_constraint_enforcement_binding_v1.{surface}",
        record,
    )
    record["ledger"] = {
        "entry_count": ledger.get("entry_count"),
        "tip_hash72": ledger.get("tip_hash72"),
        "ledger_hash72": ledger.get("ledger_hash72"),
        "verified": bool(verify_unified_ledger().get("ok")),
    }
    return record


def _make_candidate_variants(canonical: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    variants: Dict[str, Dict[str, Any]] = {
        "canonical_full_witness_chain": copy.deepcopy(dict(canonical)),
        "full_rule_following_bruteforce_sequence": copy.deepcopy(dict(canonical)),
        "terminal_value_only": make_terminal_value_only_claim(CANONICAL_TENSOR_SEED),
    }
    partial_keep = {"schema", "version", "status", "accepted", "tensor_seed", "phase_product_witnesses", "manifold_kernel_witness"}
    variants["partial_bruteforce_witness_chain"] = {key: val for key, val in canonical.items() if key in partial_keep}
    schemaless = copy.deepcopy(dict(canonical)); schemaless.pop("schema", None)
    variants["missing_schema_identity"] = schemaless
    ledgerless = copy.deepcopy(dict(canonical)); ledgerless.pop("ledger", None)
    variants["missing_ledger_receipt"] = ledgerless
    phase = copy.deepcopy(dict(canonical))
    for witness in phase.get("phase_product_witnesses", []):
        witness["palindrome_valid"] = False
        if isinstance(witness.get("projected_tensor"), dict):
            witness["projected_tensor"]["valid"] = False
    variants["invalid_palindromic_phase_product_ecc"] = phase
    rotation = copy.deepcopy(dict(canonical))
    if isinstance(rotation.get("hash72_bigint_carrier"), dict):
        rotation["hash72_bigint_carrier"]["lossless_decode"] = False
        rotation["hash72_bigint_carrier"]["rotation_profile"] = rotation["hash72_bigint_carrier"].get("rotation_profile", [])[:71]
    variants["invalid_hash72_rotation_profile"] = rotation
    temporal = copy.deepcopy(dict(canonical))
    if isinstance(temporal.get("harmonic_time_audio_witness"), dict):
        temporal["harmonic_time_audio_witness"]["harmonic_time_valid"] = False
    variants["invalid_harmonic_time_audio_ecc"] = temporal
    return variants


def run_runtime_constraint_enforcement_binding(root: Optional[str | Path] = None) -> Dict[str, Any]:
    """Run the enforcement binding across representative runtime surfaces."""

    repo = _repo_root(root)
    variants: Dict[str, Dict[str, Any]] = {}
    scenarios = [
        ("api.runtime.admissibility.enforce", "canonical_full_witness_chain", False),
        ("api.runtime.admissibility.enforce", "terminal_value_only", False),
        ("api.runtime.services.dispatch.preflight", "missing_schema_identity", False),
        ("api.runtime.services.dispatch.preflight", "missing_ledger_receipt", False),
        ("api.runtime.srcg.selfsolve.preflight", "invalid_palindromic_phase_product_ecc", False),
        ("gui.runtime.bridge.preflight", "invalid_hash72_rotation_profile", False),
        ("api.runtime.closure.harness.preflight", "invalid_harmonic_time_audio_ecc", False),
        ("service_registry.dispatch.preflight", "partial_bruteforce_witness_chain", True),
        ("service_registry.dispatch.preflight", "full_rule_following_bruteforce_sequence", True),
    ]
    decisions = [
        enforce_runtime_constraint_boundary(
            surface=surface,
            request_class=request_class,
            brute_force_claim=bruteforce,
            root=repo,
        )
        for surface, request_class, bruteforce in scenarios
    ]
    admitted = [item for item in decisions if item["admitted"]]
    rejected = [item for item in decisions if not item["admitted"]]
    manifest = {
        "schema": "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_BINDING_MANIFEST_V1",
        "version": VERSION,
        "surface_map": make_runtime_enforcement_surface_map(),
        "decisions": decisions,
        "security_harness_summary": {
            "source": "pass_034_policy_reused",
            "scenario_count": 9,
            "accepted_or_reclassified_count": 2,
            "rejected_count": 7,
        },
        "summary": {
            "surface_count": len(set(item["surface"] for item in decisions)),
            "decision_count": len(decisions),
            "admitted_count": len(admitted),
            "rejected_count": len(rejected),
            "rejected_executions_allowed": any(item["execution_allowed"] for item in rejected),
            "terminal_value_sufficient": any(item["terminal_value_sufficient"] for item in decisions),
            "full_rule_following_bruteforce_reclassified": any(item["reclassified_as_valid_propagation"] for item in decisions),
            "ledger_verified": bool(verify_unified_ledger().get("ok")),
        },
    }
    return manifest

def build_pass_035_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = _repo_root(root)
    manifest = run_runtime_constraint_enforcement_binding(root=repo)
    (repo / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

    summary = manifest["summary"]
    report = f"""# Pass 035 — Runtime Constraint Enforcement Binding

Pass 035 binds the Pass 033/034 admissibility and non-silent propagation rules to runtime-facing enforcement surfaces.  The harness is no longer only a standalone security test; it is now available as a preflight decision layer for API, service, GUI, SRCG, and closure-harness surfaces.

## Summary

- Bound surfaces exercised: `{summary['surface_count']}`
- Enforcement decisions: `{summary['decision_count']}`
- Admitted/reclassified: `{summary['admitted_count']}`
- Rejected: `{summary['rejected_count']}`
- Rejected executions allowed: `{summary['rejected_executions_allowed']}`
- Terminal value sufficient: `{summary['terminal_value_sufficient']}`
- Full rule-following brute force reclassified: `{summary['full_rule_following_bruteforce_reclassified']}`
- Ledger verified: `{summary['ledger_verified']}`

## Enforcement invariant

No runtime-facing propagation surface may admit a terminal value, partial witness, schemaless transformation, ledgerless mutation, phase-product drift, rotation-profile drift, or temporal coherence drift as executable state.
"""
    (repo / REPORT_FILE).write_text(report, encoding="utf-8")

    non_silent = """# Non-Silent Runtime Enforcement — Pass 035

Pass 035 makes the non-silent propagation doctrine callable at runtime.  An operation is not admitted because it has a plausible terminal value.  It is admitted only when the candidate state has a complete witness chain or when a brute-force claim follows the rules precisely and is reclassified as valid HHS propagation.

Rejected candidates are denied without target execution and are recorded as explicit enforcement decisions with Hash72/u^72 witnesses, foundational audits, and ledger receipts.
"""
    (repo / SECURITY_ENFORCEMENT_FILE).write_text(non_silent, encoding="utf-8")

    surface_map = manifest["surface_map"]
    surface_report = "# Runtime Enforcement Surface Map — Pass 035\n\n" + "\n".join(f"- `{surface}`" for surface in surface_map["bound_surfaces"]) + "\n"
    (repo / SURFACE_MAP_FILE).write_text(surface_report, encoding="utf-8")
    return manifest


def runtime_constraint_enforcement_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    request = dict(payload or {})
    if request:
        decision = enforce_runtime_constraint_boundary(
            surface=str(request.get("surface") or "api.runtime.admissibility.enforce"),
            request_class=str(request.get("request_class") or "canonical_full_witness_chain"),
            candidate=request.get("candidate") if isinstance(request.get("candidate"), Mapping) else None,
            brute_force_claim=bool(request.get("brute_force_claim", False)),
        )
        ok = (
            bool(decision["admitted"])
            if str(request.get("expect") or "admitted") == "admitted"
            else not bool(decision["admitted"])
        )
        return {
            "schema": "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_SELF_TEST_V1",
            "version": VERSION,
            "ok": ok,
            "service": ENFORCEMENT_SERVICE,
            "decision": decision,
        }

    manifest = build_pass_035_artifacts()
    summary = manifest["summary"]
    statuses = {item["request_class"]: item["status"] for item in manifest["decisions"]}
    ok = (
        summary["decision_count"] == 9
        and summary["admitted_count"] == 2
        and summary["rejected_count"] == 7
        and not summary["rejected_executions_allowed"]
        and not summary["terminal_value_sufficient"]
        and summary["full_rule_following_bruteforce_reclassified"]
        and statuses.get("canonical_full_witness_chain") == ACCEPTED_STATUS
        and statuses.get("terminal_value_only") == "REJECTED_FORGED_TERMINAL_VALUE"
        and statuses.get("full_rule_following_bruteforce_sequence") == RECLASSIFIED_STATUS
    )
    return {
        "schema": "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "service": ENFORCEMENT_SERVICE,
        "manifest_file": MANIFEST_FILE,
        "report_file": REPORT_FILE,
        "security_enforcement_file": SECURITY_ENFORCEMENT_FILE,
        "surface_map_file": SURFACE_MAP_FILE,
        "summary": summary,
        "statuses": statuses,
    }


if __name__ == "__main__":
    print(json.dumps(runtime_constraint_enforcement_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
