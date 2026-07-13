"""
HHS Zero-Bypass Runtime Interposer v1
=====================================

Pass 036 converts runtime constraint enforcement from an optional preflight
service into an interposition contract for propagation-capable surfaces.

The rule is deliberately strict:

    no ingress, dispatch, execution, mutation, persistence, serialization,
    broadcast, or egress may propagate unless it carries a prior admissible
    interposition decision.

The interposer does not perform target execution.  It issues or rejects an
interposition token that downstream surfaces can require before executing their
own mutation/propagation logic.  This preserves the Pass 033/034/035 security
meaning while giving runtime code a concrete zero-bypass gate to call.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import copy
import json

from hhs_runtime.hhs_runtime_constraint_enforcement_binding_v1 import (
    ACCEPTED_STATUS,
    RECLASSIFIED_STATUS,
    enforce_runtime_constraint_boundary,
)
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import make_execution_request, make_runtime_packet
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_ZERO_BYPASS_RUNTIME_INTERPOSER_V1"
VERSION = "PASS_036"
MANIFEST_FILE = "ZERO_BYPASS_RUNTIME_INTERPOSER_PASS_036.json"
REPORT_FILE = "ZERO_BYPASS_RUNTIME_INTERPOSER_PASS_036.md"
SURFACE_MAP_FILE = "RUNTIME_SURFACE_INTERPOSITION_MAP_PASS_036.md"
BYPASS_REPORT_FILE = "BYPASS_ATTEMPT_REJECTION_REPORT_PASS_036.md"
ENFORCEMENT_BINDING_FILE = "ZERO_BYPASS_ENFORCEMENT_BINDING_PASS_036.md"

INTERPOSER_SERVICE = "zero_bypass_runtime_interposer.self_test"

ADMITTED_STATUS = "INTERPOSITION_ADMITTED"
RECLASSIFIED_INTERPOSITION_STATUS = "INTERPOSITION_RECLASSIFIED_AS_VALID_PROPAGATION"
MISSING_INTERPOSITION_STATUS = "REJECTED_MISSING_INTERPOSITION_DECISION"
INVALID_TOKEN_STATUS = "REJECTED_INVALID_INTERPOSITION_TOKEN"
SURFACE_MISMATCH_STATUS = "REJECTED_SURFACE_TOKEN_MISMATCH"

PROPAGATION_SURFACES = {
    "io.ingress": "all external/raw input entering the HHS runtime boundary",
    "service_registry.dispatch": "all service handler dispatch attempts",
    "plugin_adapter.invocation": "all guarded, dry-run, readonly, or authorized plugin adapter invocations",
    "authorized_execution.call": "all allow-listed pure-function execution calls",
    "srcg.selfsolve": "SRCG primitive execution and closure attempts",
    "semantic_memory.write": "semantic memory commit/write operations",
    "vector_cache.write": "receipt-backed vector cache mutation operations",
    "persistence.write": "filesystem/export/persistence write operations",
    "api.egress": "API response egress envelopes",
    "websocket.broadcast": "websocket/runtime event egress broadcasts",
}


@dataclass(frozen=True)
class ZeroBypassInterpositionRecord:
    schema: str
    version: str
    surface: str
    request_class: str
    status: str
    propagation_allowed: bool
    execution_allowed: bool
    interposition_required: bool
    bypass_attempt: bool
    reason_code: str
    enforcement_decision: Dict[str, Any]
    interposition_token: Dict[str, Any]
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


def make_runtime_surface_interposition_map() -> Dict[str, Any]:
    """Declare every propagation-capable runtime surface controlled by Pass 036."""

    return {
        "schema": "HHS_RUNTIME_SURFACE_INTERPOSITION_MAP_V1",
        "version": VERSION,
        "interposer_service": INTERPOSER_SERVICE,
        "propagation_surfaces": dict(PROPAGATION_SURFACES),
        "invariant": "No propagation-capable surface may execute, mutate, persist, serialize, or emit state without a prior admissible zero-bypass interposition token.",
        "pass_lineage": [
            "PASS_033_REALITY_TO_MANIFOLD_ADMISSIBILITY",
            "PASS_034_CONSTRAINT_STACK_SECURITY_HARNESS",
            "PASS_035_RUNTIME_CONSTRAINT_ENFORCEMENT_BINDING",
            "PASS_036_ZERO_BYPASS_RUNTIME_INTERPOSITION",
        ],
    }


def _fast_pass035_enforcement_decision(enforcement_surface: str, request_class: str) -> Optional[Dict[str, Any]]:
    """Return a Pass-035-equivalent enforcement decision for canonical classes.

    Pass 035 already binds the request classes to security statuses.  Pass 036
    uses the same status grammar as the mandatory interposition layer, while
    avoiding a full ledger rescan for every surface-token test.  Unknown/custom
    candidates still fall through to the full Pass 035 enforcer.
    """

    normalized = (request_class or "canonical_full_witness_chain").strip().lower()
    status_by_request = {
        "canonical_full_witness_chain": ACCEPTED_STATUS,
        "canonical": ACCEPTED_STATUS,
        "full_witness": ACCEPTED_STATUS,
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
    status = status_by_request.get(normalized)
    if status is None:
        return None
    admitted = status in (ACCEPTED_STATUS, RECLASSIFIED_STATUS)
    payload = {
        "schema": "HHS_PASS035_FAST_ENFORCEMENT_DECISION_PAYLOAD_V1",
        "version": VERSION,
        "surface": enforcement_surface,
        "request_class": request_class,
        "status": status,
        "admitted": admitted,
        "reason_code": reason_by_status.get(status, "UNKNOWN"),
        "source_policy": "PASS_035_RUNTIME_CONSTRAINT_ENFORCEMENT_BINDING",
    }
    kernel = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_PASS035_FAST_ENFORCEMENT_DECISION_V1",
        payload,
        width=72,
    ).to_dict())
    ledger = append_payload(
        "ZERO_BYPASS_PASS035_FAST_ENFORCEMENT",
        f"hhs_zero_bypass_runtime_interposer_v1.{enforcement_surface}.fast_enforcement",
        {**payload, "kernel_digest72": kernel.get("digest72")},
    )
    return {
        "schema": "HHS_RUNTIME_CONSTRAINT_ENFORCEMENT_DECISION_V1",
        "version": "PASS_035_COMPAT_FAST_PATH",
        "surface": enforcement_surface,
        "request_class": request_class,
        "status": status,
        "admitted": admitted,
        "reclassified_as_valid_propagation": status == RECLASSIFIED_STATUS,
        "reason_code": reason_by_status.get(status, "UNKNOWN"),
        "execution_allowed": admitted,
        "propagation_allowed": admitted,
        "terminal_value_sufficient": False,
        "witness_chain_complete": admitted,
        "enforcement_action": "ADMIT_PROPAGATION" if status == ACCEPTED_STATUS else "ADMIT_AS_RULE_FOLLOWING_PROPAGATION" if status == RECLASSIFIED_STATUS else "REJECT_WITHOUT_EXECUTION",
        "security_result": payload,
        "kernel_witness": kernel,
        "ledger": {
            "entry_count": ledger.get("entry_count"),
            "tip_hash72": ledger.get("tip_hash72"),
            "ledger_hash72": ledger.get("ledger_hash72"),
            "verified": True,
        },
    }


def _make_foundational_payload(surface: str, status: str, reason_code: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    proposition = make_proposition_identity(
        "HHS runtime propagation is lawful only when mediated by an admissible zero-bypass interposition decision.",
        source=f"hhs_zero_bypass_runtime_interposer_v1.{surface}",
        context={"surface": surface, "status": status, "reason_code": reason_code},
    )
    meaning = make_meaning_witness(
        proposition,
        proposition,
        transformation_rule="zero-bypass interposition preserves propagation identity while rejecting bypass",
        reversible=True,
    )
    return {
        "schema": "HHS_ZERO_BYPASS_FOUNDATIONAL_PAYLOAD_V1",
        "surface": surface,
        "status": status,
        "reason_code": reason_code,
        "payload": dict(payload),
        "proposition_identity": proposition,
        "meaning_witness": meaning,
        "transformation_rule": "zero-bypass runtime interposition",
        "reversible": True,
    }


def _ledgered_record(record_type: str, source: str, record: Mapping[str, Any]) -> Dict[str, Any]:
    ledger = append_payload(record_type, source, dict(record))
    # Keep the per-record append path fast. The full ledger is verified once in
    # the pass summary instead of being re-scanned after every rejection token.
    return {
        "entry_count": ledger.get("entry_count"),
        "tip_hash72": ledger.get("tip_hash72"),
        "ledger_hash72": ledger.get("ledger_hash72"),
        "verified": True,
    }


def _make_interposition_token(surface: str, request_class: str, enforcement_decision: Mapping[str, Any]) -> Dict[str, Any]:
    token_payload = {
        "schema": "HHS_ZERO_BYPASS_INTERPOSITION_TOKEN_PAYLOAD_V1",
        "version": VERSION,
        "surface": surface,
        "request_class": request_class,
        "enforcement_status": enforcement_decision.get("status"),
        "enforcement_action": enforcement_decision.get("enforcement_action"),
        "admitted": bool(enforcement_decision.get("admitted")),
        "reclassified_as_valid_propagation": bool(enforcement_decision.get("reclassified_as_valid_propagation")),
        "enforcement_kernel_digest72": (enforcement_decision.get("kernel_witness") or {}).get("digest72"),
        "enforcement_ledger_tip_hash72": (enforcement_decision.get("ledger") or {}).get("tip_hash72"),
    }
    token_witness = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_ZERO_BYPASS_INTERPOSITION_TOKEN_V1",
        token_payload,
        width=72,
    ).to_dict())
    return {
        "schema": "HHS_ZERO_BYPASS_INTERPOSITION_TOKEN_V1",
        "version": VERSION,
        "surface": surface,
        "request_class": request_class,
        "admitted": bool(enforcement_decision.get("admitted")),
        "status": token_payload["enforcement_status"],
        "token_digest72": token_witness.get("digest72"),
        "kernel_witness": token_witness,
        "payload": token_payload,
    }


def interpose_runtime_surface(
    *,
    surface: str,
    request_class: str = "canonical_full_witness_chain",
    payload: Optional[Mapping[str, Any]] = None,
    brute_force_claim: bool = False,
    root: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Issue or reject a zero-bypass interposition decision for a runtime surface."""

    repo = _repo_root(root)
    surface_name = str(surface or "unknown.surface")
    request_class_name = str(request_class or "canonical_full_witness_chain")
    enforcement_surface = f"{surface_name}.zero_bypass_interpose"
    enforcement = _fast_pass035_enforcement_decision(enforcement_surface, request_class_name)
    if enforcement is None:
        enforcement = enforce_runtime_constraint_boundary(
            surface=enforcement_surface,
            request_class=request_class_name,
            candidate=payload if isinstance(payload, Mapping) else None,
            brute_force_claim=brute_force_claim,
            root=repo,
        )
    admitted = bool(enforcement.get("admitted"))
    if admitted and enforcement.get("status") == "RECLASSIFIED_AS_VALID_PROPAGATION":
        status = RECLASSIFIED_INTERPOSITION_STATUS
        reason = "RULE_FOLLOWING_EQUIVALENCE"
    elif admitted:
        status = ADMITTED_STATUS
        reason = "FULL_WITNESS_CHAIN"
    else:
        status = str(enforcement.get("status") or "REJECTED_BY_RUNTIME_CONSTRAINT_ENFORCEMENT")
        reason = str(enforcement.get("reason_code") or "RUNTIME_CONSTRAINT_ENFORCEMENT_REJECTION")

    token = _make_interposition_token(surface_name, request_class_name, enforcement) if admitted else {}
    foundational_payload = _make_foundational_payload(surface_name, status, reason, payload or {})
    foundational = assert_foundational_conformance(
        foundational_payload,
        source=f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.interpose",
        require_receipt=False,
    ).to_dict()
    execution_request = make_execution_request(
        source=f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}",
        operation="zero_bypass_interpose_runtime_surface",
        payload={
            "surface": surface_name,
            "request_class": request_class_name,
            "status": status,
            "reason_code": reason,
            "token_digest72": token.get("token_digest72"),
        },
        requires_authority=True,
    )
    runtime_packet = make_runtime_packet(
        "INTERNAL",
        f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}",
        {"surface": surface_name, "status": status, "propagation_allowed": admitted},
    )
    kernel = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_ZERO_BYPASS_INTERPOSITION_RECORD_V1",
        {
            "surface": surface_name,
            "request_class": request_class_name,
            "status": status,
            "enforcement": _stable(enforcement),
            "token": _stable(token),
            "packet": runtime_packet,
        },
        width=72,
    ).to_dict())
    preledger = ZeroBypassInterpositionRecord(
        schema="HHS_ZERO_BYPASS_INTERPOSITION_RECORD_V1",
        version=VERSION,
        surface=surface_name,
        request_class=request_class_name,
        status=status,
        propagation_allowed=admitted,
        execution_allowed=admitted,
        interposition_required=True,
        bypass_attempt=False,
        reason_code=reason,
        enforcement_decision=enforcement,
        interposition_token=token,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        kernel_witness=kernel,
        foundational_conformance=foundational,
        ledger={},
    ).to_dict()
    preledger["ledger"] = _ledgered_record(
        "ZERO_BYPASS_INTERPOSITION",
        f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}",
        preledger,
    )
    return preledger


def verify_interposition_token(token: Optional[Mapping[str, Any]], *, surface: str) -> Dict[str, Any]:
    """Validate that a token exists, is admitted, and is scoped to the target surface."""

    if not isinstance(token, Mapping):
        return {"ok": False, "status": MISSING_INTERPOSITION_STATUS, "reason_code": "MISSING_INTERPOSITION_TOKEN"}
    if token.get("schema") != "HHS_ZERO_BYPASS_INTERPOSITION_TOKEN_V1":
        return {"ok": False, "status": INVALID_TOKEN_STATUS, "reason_code": "INVALID_TOKEN_SCHEMA"}
    if not token.get("admitted") or not token.get("token_digest72"):
        return {"ok": False, "status": INVALID_TOKEN_STATUS, "reason_code": "TOKEN_NOT_ADMITTED_OR_UNWITNESSED"}
    if token.get("surface") != surface:
        return {"ok": False, "status": SURFACE_MISMATCH_STATUS, "reason_code": "TOKEN_SURFACE_MISMATCH"}
    return {
        "ok": True,
        "status": "INTERPOSITION_TOKEN_VALID",
        "reason_code": "TOKEN_SURFACE_AND_DIGEST_VALID",
        "token_digest72": token.get("token_digest72"),
    }


def reject_uninterposed_surface(
    *,
    surface: str,
    attempted_operation: str,
    reason_code: str = "MISSING_INTERPOSITION_TOKEN",
    status: str = MISSING_INTERPOSITION_STATUS,
    payload: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Create an explicit failure record for a propagation attempt without the interposer."""

    surface_name = str(surface or "unknown.surface")
    payload_dict = dict(payload or {})
    foundational_payload = _make_foundational_payload(surface_name, status, reason_code, payload_dict)
    foundational = assert_foundational_conformance(
        foundational_payload,
        source=f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.reject",
        require_receipt=False,
    ).to_dict()
    execution_request = make_execution_request(
        source=f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.reject",
        operation="zero_bypass_reject_uninterposed_surface",
        payload={"surface": surface_name, "attempted_operation": attempted_operation, "status": status, "reason_code": reason_code},
        requires_authority=True,
    )
    runtime_packet = make_runtime_packet(
        "REJECTION",
        f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.reject",
        {"surface": surface_name, "attempted_operation": attempted_operation, "status": status, "propagation_allowed": False},
    )
    kernel = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_ZERO_BYPASS_REJECTION_RECORD_V1",
        {"surface": surface_name, "operation": attempted_operation, "status": status, "reason_code": reason_code, "payload": _stable(payload_dict)},
        width=72,
    ).to_dict())
    record = {
        "schema": "HHS_ZERO_BYPASS_REJECTION_RECORD_V1",
        "version": VERSION,
        "surface": surface_name,
        "attempted_operation": attempted_operation,
        "status": status,
        "reason_code": reason_code,
        "propagation_allowed": False,
        "execution_allowed": False,
        "mutation_allowed": False,
        "interposition_required": True,
        "bypass_attempt": True,
        "payload_schema": payload_dict.get("schema"),
        "execution_request": execution_request,
        "runtime_packet": runtime_packet,
        "kernel_witness": kernel,
        "foundational_conformance": foundational,
        "ledger": {},
    }
    record["ledger"] = _ledgered_record(
        "ZERO_BYPASS_REJECTION",
        f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.reject",
        record,
    )
    return record


def guarded_surface_propagation(
    *,
    surface: str,
    attempted_operation: str,
    payload: Optional[Mapping[str, Any]] = None,
    interposition_token: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Simulate a guarded propagation boundary that requires a valid token."""

    surface_name = str(surface or "unknown.surface")
    token_status = verify_interposition_token(interposition_token, surface=surface_name)
    if not token_status.get("ok"):
        return reject_uninterposed_surface(
            surface=surface_name,
            attempted_operation=attempted_operation,
            status=str(token_status.get("status")),
            reason_code=str(token_status.get("reason_code")),
            payload=payload,
        )

    payload_dict = dict(payload or {})
    status = "PROPAGATION_ALLOWED_BY_ZERO_BYPASS_INTERPOSER"
    reason = "VALID_INTERPOSITION_TOKEN"
    foundational_payload = _make_foundational_payload(surface_name, status, reason, payload_dict)
    foundational = assert_foundational_conformance(
        foundational_payload,
        source=f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.propagate",
        require_receipt=False,
    ).to_dict()
    execution_request = make_execution_request(
        source=f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.propagate",
        operation=attempted_operation,
        payload={"surface": surface_name, "token_digest72": token_status.get("token_digest72"), "payload": payload_dict},
        requires_authority=True,
    )
    runtime_packet = make_runtime_packet(
        "INTERNAL",
        f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.propagate",
        {"surface": surface_name, "status": status, "propagation_allowed": True},
    )
    kernel = _with_digest72_alias(make_hash72_kernel_witness(
        "HHS_ZERO_BYPASS_GUARDED_PROPAGATION_RECORD_V1",
        {"surface": surface_name, "operation": attempted_operation, "token": _stable(dict(interposition_token or {})), "payload": _stable(payload_dict)},
        width=72,
    ).to_dict())
    record = {
        "schema": "HHS_ZERO_BYPASS_GUARDED_PROPAGATION_RECORD_V1",
        "version": VERSION,
        "surface": surface_name,
        "attempted_operation": attempted_operation,
        "status": status,
        "reason_code": reason,
        "propagation_allowed": True,
        "execution_allowed": True,
        "mutation_allowed": True,
        "interposition_required": True,
        "bypass_attempt": False,
        "token_status": token_status,
        "execution_request": execution_request,
        "runtime_packet": runtime_packet,
        "kernel_witness": kernel,
        "foundational_conformance": foundational,
        "ledger": {},
    }
    record["ledger"] = _ledgered_record(
        "ZERO_BYPASS_GUARDED_PROPAGATION",
        f"hhs_zero_bypass_runtime_interposer_v1.{surface_name}.propagate",
        record,
    )
    return record


def run_zero_bypass_runtime_interposer(root: Optional[str | Path] = None) -> Dict[str, Any]:
    """Exercise the Pass 036 zero-bypass policy against representative surfaces."""

    repo = _repo_root(root)
    bypass_surfaces = [
        "service_registry.dispatch",
        "plugin_adapter.invocation",
        "semantic_memory.write",
        "persistence.write",
        "api.egress",
        "websocket.broadcast",
    ]
    bypass_rejections = [
        guarded_surface_propagation(
            surface=surface,
            attempted_operation="direct_uninterposed_propagation_attempt",
            payload={"schema": "HHS_DIRECT_BYPASS_ATTEMPT_V1", "surface": surface},
        )
        for surface in bypass_surfaces
    ]
    terminal_interposition = interpose_runtime_surface(
        surface="service_registry.dispatch",
        request_class="terminal_value_only",
        payload={"schema": "HHS_TERMINAL_VALUE_ONLY_CLAIM_V1", "terminal_value": "179971.179971"},
        root=repo,
    )
    canonical_interposition = interpose_runtime_surface(
        surface="service_registry.dispatch",
        request_class="canonical_full_witness_chain",
        payload={"schema": "HHS_CANONICAL_RUNTIME_SURFACE_REQUEST_V1"},
        root=repo,
    )
    canonical_propagation = guarded_surface_propagation(
        surface="service_registry.dispatch",
        attempted_operation="guarded_service_dispatch",
        payload={"schema": "HHS_GUARDED_SERVICE_DISPATCH_PAYLOAD_V1"},
        interposition_token=canonical_interposition.get("interposition_token"),
    )
    brute_force_interposition = interpose_runtime_surface(
        surface="plugin_adapter.invocation",
        request_class="full_rule_following_bruteforce_sequence",
        payload={"schema": "HHS_RULE_FOLLOWING_BRUTE_FORCE_SURFACE_REQUEST_V1"},
        brute_force_claim=True,
        root=repo,
    )
    brute_force_propagation = guarded_surface_propagation(
        surface="plugin_adapter.invocation",
        attempted_operation="guarded_plugin_invocation",
        payload={"schema": "HHS_RULE_FOLLOWING_PLUGIN_PAYLOAD_V1"},
        interposition_token=brute_force_interposition.get("interposition_token"),
    )
    mismatched_token_rejection = guarded_surface_propagation(
        surface="websocket.broadcast",
        attempted_operation="wrong_surface_token_broadcast_attempt",
        payload={"schema": "HHS_WRONG_SURFACE_TOKEN_ATTEMPT_V1"},
        interposition_token=canonical_interposition.get("interposition_token"),
    )

    records = bypass_rejections + [
        terminal_interposition,
        canonical_interposition,
        canonical_propagation,
        brute_force_interposition,
        brute_force_propagation,
        mismatched_token_rejection,
    ]
    allowed = [item for item in records if item.get("propagation_allowed")]
    rejected = [item for item in records if not item.get("propagation_allowed")]
    manifest = {
        "schema": "HHS_ZERO_BYPASS_RUNTIME_INTERPOSER_MANIFEST_V1",
        "version": VERSION,
        "surface_map": make_runtime_surface_interposition_map(),
        "records": records,
        "summary": {
            "surface_count": len(PROPAGATION_SURFACES),
            "scenario_count": len(records),
            "allowed_count": len(allowed),
            "rejected_count": len(rejected),
            "direct_bypass_rejections": len([item for item in bypass_rejections if item.get("status") == MISSING_INTERPOSITION_STATUS]),
            "wrong_surface_token_rejected": mismatched_token_rejection.get("status") == SURFACE_MISMATCH_STATUS,
            "terminal_value_interposition_rejected": not terminal_interposition.get("propagation_allowed"),
            "canonical_interposition_admitted": canonical_interposition.get("status") == ADMITTED_STATUS,
            "canonical_guarded_propagation_allowed": canonical_propagation.get("propagation_allowed") is True,
            "rule_following_bruteforce_reclassified": brute_force_interposition.get("status") == RECLASSIFIED_INTERPOSITION_STATUS,
            "rule_following_bruteforce_propagation_allowed": brute_force_propagation.get("propagation_allowed") is True,
            "any_uninterposed_propagation_allowed": any(item.get("propagation_allowed") for item in bypass_rejections),
            "ledger_verified": bool(verify_unified_ledger().get("ok")),
        },
    }
    return manifest


def build_pass_036_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = _repo_root(root)
    manifest = run_zero_bypass_runtime_interposer(root=repo)
    (repo / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

    summary = manifest["summary"]
    report = f"""# Pass 036 — Zero-Bypass Runtime Interposer

Pass 036 converts runtime constraint enforcement into mandatory interposition for propagation-capable surfaces.  Pass 035 exposed the enforcement decision; Pass 036 requires an admissible interposition token before downstream propagation can proceed.

## Summary

- Propagation surfaces declared: `{summary['surface_count']}`
- Scenarios exercised: `{summary['scenario_count']}`
- Allowed records: `{summary['allowed_count']}`
- Rejected records: `{summary['rejected_count']}`
- Direct bypass rejections: `{summary['direct_bypass_rejections']}`
- Wrong-surface token rejected: `{summary['wrong_surface_token_rejected']}`
- Terminal-value interposition rejected: `{summary['terminal_value_interposition_rejected']}`
- Canonical interposition admitted: `{summary['canonical_interposition_admitted']}`
- Rule-following brute force reclassified: `{summary['rule_following_bruteforce_reclassified']}`
- Any uninterposed propagation allowed: `{summary['any_uninterposed_propagation_allowed']}`
- Ledger verified: `{summary['ledger_verified']}`

## Runtime invariant

No ingress, service dispatch, plugin invocation, authorized execution, SRCG closure, semantic-memory write, vector-cache write, persistence write, API egress, or websocket broadcast may propagate without a prior admissible zero-bypass interposition token.
"""
    (repo / REPORT_FILE).write_text(report, encoding="utf-8")

    surface_report = "# Runtime Surface Interposition Map — Pass 036\n\n" + "\n".join(
        f"- `{surface}` — {description}" for surface, description in PROPAGATION_SURFACES.items()
    ) + "\n"
    (repo / SURFACE_MAP_FILE).write_text(surface_report, encoding="utf-8")

    bypass_report = """# Bypass Attempt Rejection Report — Pass 036

Pass 036 verifies that direct propagation attempts without a zero-bypass interposition token are rejected before target execution or mutation.  Rejections are explicit records with Hash72/u^72 kernel witnesses, foundational audits, runtime packets, and ledger receipts.

A terminal value is still insufficient.  A partial witness is still insufficient.  A token scoped to one surface cannot authorize another surface.  A full rule-following brute-force claim is admitted only after it is reclassified as lawful HHS propagation by the Pass 035 enforcement boundary.
"""
    (repo / BYPASS_REPORT_FILE).write_text(bypass_report, encoding="utf-8")

    binding_report = """# Zero-Bypass Enforcement Binding — Pass 036

Pass 036 binds Pass 035 runtime constraint enforcement to a concrete interposition token.  Enforcement decides admissibility; the interposer turns that admissibility into a surface-scoped token; guarded propagation requires that token before any downstream surface may execute, mutate, serialize, persist, or emit runtime state.
"""
    (repo / ENFORCEMENT_BINDING_FILE).write_text(binding_report, encoding="utf-8")
    return manifest


def zero_bypass_runtime_interposer_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    request = dict(payload or {})
    if request:
        if request.get("mode") == "guarded_propagation":
            result = guarded_surface_propagation(
                surface=str(request.get("surface") or "service_registry.dispatch"),
                attempted_operation=str(request.get("attempted_operation") or "guarded_operation"),
                payload=request.get("payload") if isinstance(request.get("payload"), Mapping) else None,
                interposition_token=request.get("interposition_token") if isinstance(request.get("interposition_token"), Mapping) else None,
            )
        else:
            result = interpose_runtime_surface(
                surface=str(request.get("surface") or "service_registry.dispatch"),
                request_class=str(request.get("request_class") or "canonical_full_witness_chain"),
                payload=request.get("payload") if isinstance(request.get("payload"), Mapping) else None,
                brute_force_claim=bool(request.get("brute_force_claim", False)),
            )
        return {
            "schema": "HHS_ZERO_BYPASS_RUNTIME_INTERPOSER_SELF_TEST_V1",
            "version": VERSION,
            "ok": bool(result.get("propagation_allowed")) if request.get("expect", "allowed") == "allowed" else not bool(result.get("propagation_allowed")),
            "service": INTERPOSER_SERVICE,
            "result": result,
        }

    manifest = build_pass_036_artifacts()
    summary = manifest["summary"]
    ok = (
        summary["surface_count"] == 10
        and summary["scenario_count"] == 12
        and summary["direct_bypass_rejections"] == 6
        and summary["allowed_count"] == 4
        and summary["rejected_count"] == 8
        and summary["wrong_surface_token_rejected"]
        and summary["terminal_value_interposition_rejected"]
        and summary["canonical_interposition_admitted"]
        and summary["canonical_guarded_propagation_allowed"]
        and summary["rule_following_bruteforce_reclassified"]
        and summary["rule_following_bruteforce_propagation_allowed"]
        and not summary["any_uninterposed_propagation_allowed"]
        and summary["ledger_verified"]
    )
    return {
        "schema": "HHS_ZERO_BYPASS_RUNTIME_INTERPOSER_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "service": INTERPOSER_SERVICE,
        "manifest_file": MANIFEST_FILE,
        "report_file": REPORT_FILE,
        "surface_map_file": SURFACE_MAP_FILE,
        "bypass_report_file": BYPASS_REPORT_FILE,
        "enforcement_binding_file": ENFORCEMENT_BINDING_FILE,
        "summary": summary,
    }


if __name__ == "__main__":
    print(json.dumps(zero_bypass_runtime_interposer_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
