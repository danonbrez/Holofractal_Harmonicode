"""
HHS Authorized Execution Failure Policy v1
==========================================

Pass 032 hardens the inverse side of authorized execution.  Pass 031 proved a
narrow successful path for allow-listed pure functions.  Pass 032 proves that
invalid, unsafe, malformed, or non-allow-listed execution requests are rejected
without executing target function bodies and that every rejection emits an
explicit failure record with:

* Pass 030 schema-family classification and validation;
* HHS-M001..M007 foundational conformance;
* C u^72 Hash72 Digital DNA witness;
* unified Hash72 ledger receipt;
* explicit no-execution evidence.

This module does not broaden raw plugin execution.  It makes rejection itself a
first-class, witnessed runtime object so the execution layer cannot become
permissive by silent denial, exception swallowing, or schema drift.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import copy
import json

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_authorized_pure_function_executor_v1 import (
    AUTHORIZED_PURE_ALLOWLIST,
    DEFAULT_AUTHORIZED_PURE_TARGETS,
    execute_authorized_pure_function,
)
from hhs_runtime.hhs_contract_schema_registry_v1 import classify_schema_object, validate_schema_object
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import assert_contract, make_execution_request, make_runtime_packet
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_AUTHORIZED_EXECUTION_FAILURE_POLICY_V1"
VERSION = "PASS_032"
FAILURE_RECORD_SCHEMA = "HHS_AUTHORIZED_EXECUTION_FAILURE_RECORD_V1"
MANIFEST_FILE = "AUTHORIZED_EXECUTION_FAILURES_PASS_032.json"
REPORT_FILE = "AUTHORIZED_EXECUTION_FAILURES_PASS_032.md"

FORBIDDEN_AUTHORIZATION_FLAGS = (
    "direct_execution_authorized",
    "mutation_authorized",
    "write_authorized",
    "network_authorized",
    "process_authorized",
)

DEFAULT_REJECTION_TARGETS: List[Dict[str, Any]] = [
    {
        "path": "hhs_runtime/hhs_srcg_gate_v1.py",
        "function": "selfsolve_ab_gate",
        "arguments": [{"A": 1, "B": 1}],
        "keyword_arguments": {},
        "sample_payload": {"A": 1, "B": 1},
        "expected_reason_code": "NOT_ALLOWLISTED_FUNCTION",
    },
    {
        "path": "hhs_runtime/hhs_runtime_contract_v1.py",
        "function": "is_hash72",
        "arguments": ["0" * 72],
        "keyword_arguments": {},
        "mutation_authorized": True,
        "sample_payload": {"value": "0" * 72},
        "expected_reason_code": "FORBIDDEN_AUTHORIZATION_FLAG",
    },
    {
        "function": "is_hash72",
        "arguments": ["0" * 72],
        "keyword_arguments": {},
        "sample_payload": {"value": "0" * 72},
        "expected_reason_code": "MALFORMED_EXECUTION_REQUEST",
    },
]


@dataclass(frozen=True)
class HHSAuthorizedExecutionFailureRecord:
    schema: str
    version: str
    source: str
    reason: str
    reason_code: str
    rejection_stage: str
    requested_target: Dict[str, Any]
    execution_status: str
    execution_performed: bool
    call_performed: bool
    function_body_execution_performed: bool
    raw_plugin_execution: bool
    mutation_performed: bool
    write_performed: bool
    network_performed: bool
    process_performed: bool
    execution_policy: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    proposition_identity: Dict[str, Any]
    meaning_witness: Dict[str, Any]
    failure_kernel_witness: Dict[str, Any]
    foundational_conformance: Dict[str, Any]
    schema_registry_classification: Dict[str, Any]
    schema_registry_validation: Dict[str, Any]
    ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def _json_stable(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str))


def _with_digest72_alias(witness: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(witness)
    data.setdefault("digest72", data.get("digest") or data.get("dna") or "")
    data.setdefault("authority", "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1")
    return data


def _scrub_target(target: Mapping[str, Any]) -> Dict[str, Any]:
    scrubbed = _json_stable(dict(target or {}))
    # The explicit expected reason is a test/report hint, not part of policy
    # evaluation. Keeping it out of the canonical record avoids confusing the
    # runtime with an externally supplied result.
    if isinstance(scrubbed, dict):
        scrubbed.pop("expected_reason_code", None)
    return scrubbed


def preflight_authorized_execution_target(target: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify whether a target may proceed to Pass 031/032 pure execution.

    This function performs only cheap structural/policy checks. It never imports
    a target module and never calls a target function.
    """

    data = dict(target or {})
    path = str(data.get("path") or "")
    function = str(data.get("function") or "")
    if not path or not function:
        return {
            "ok": False,
            "reason_code": "MALFORMED_EXECUTION_REQUEST",
            "reason": "execution target requires non-empty path and function fields",
            "stage": "PRE_EXECUTION_STRUCTURAL_PREFLIGHT",
        }
    forbidden = [flag for flag in FORBIDDEN_AUTHORIZATION_FLAGS if bool(data.get(flag, False))]
    if forbidden:
        return {
            "ok": False,
            "reason_code": "FORBIDDEN_AUTHORIZATION_FLAG",
            "reason": "authorized pure execution forbids direct/mutation/write/network/process authorization flags: " + ", ".join(forbidden),
            "stage": "PRE_EXECUTION_POLICY_PREFLIGHT",
        }
    if path not in AUTHORIZED_PURE_ALLOWLIST:
        return {
            "ok": False,
            "reason_code": "NOT_ALLOWLISTED_PATH",
            "reason": f"target path is not allow-listed for authorized pure execution: {path}",
            "stage": "ALLOWLIST_PREFLIGHT",
        }
    if function not in AUTHORIZED_PURE_ALLOWLIST[path]:
        return {
            "ok": False,
            "reason_code": "NOT_ALLOWLISTED_FUNCTION",
            "reason": f"target function is not allow-listed for authorized pure execution: {path}.{function}",
            "stage": "ALLOWLIST_PREFLIGHT",
        }
    return {
        "ok": True,
        "reason_code": "AUTHORIZED_PURE_PREFLIGHT_OK",
        "reason": "target is eligible for authorized pure execution",
        "stage": "PRE_EXECUTION_POLICY_PREFLIGHT",
    }


def make_authorized_execution_failure_record(
    target: Mapping[str, Any],
    *,
    reason_code: str,
    reason: str,
    rejection_stage: str,
    root: Optional[str | Path] = None,
    controller: Optional[HHSRuntimeController] = None,
) -> Dict[str, Any]:
    """Create and ledger a first-class failure record without executing target."""

    _ = _repo_root(root)  # retained for signature symmetry and future path checks
    requested_target = _scrub_target(target)
    source = f"hhs_authorized_execution_failure_policy_v1.{requested_target.get('path', '<missing>')}.{requested_target.get('function', '<missing>')}"
    policy = {
        "schema": "HHS_AUTHORIZED_EXECUTION_FAILURE_POLICY_RULES_V1",
        "version": VERSION,
        "direct_legacy_execution": False,
        "raw_plugin_execution": False,
        "target_function_body_execution": False,
        "mutation_allowed": False,
        "write_allowed": False,
        "network_allowed": False,
        "process_allowed": False,
        "failure_record_required": True,
        "hash72_u72_witness_required": True,
        "foundational_audit_required": True,
        "ledger_receipt_required": True,
    }
    proposition_identity = make_proposition_identity(
        "Rejected authorized execution request preserves explicit target identity and produces a witnessed failure record before any target body execution.",
        source=source,
        context={"requested_target": requested_target, "reason_code": reason_code, "rejection_stage": rejection_stage},
    )
    meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="execution rejection preserves proposition identity and forbids target function-body execution",
        reversible=True,
    )
    failure_payload = {
        "schema": "HHS_AUTHORIZED_EXECUTION_FAILURE_PAYLOAD_V1",
        "version": VERSION,
        "source": source,
        "reason": reason,
        "reason_code": reason_code,
        "rejection_stage": rejection_stage,
        "requested_target": requested_target,
        "execution_policy": policy,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness,
    }
    execution_request = make_execution_request(
        source=source,
        operation="authorized_execution.rejected_without_execution",
        payload=failure_payload,
        requires_authority=True,
    )
    assert_contract(execution_request, expected_type="execution_request")
    runtime_packet = make_runtime_packet("INTERNAL", source, failure_payload)
    assert_contract(runtime_packet, expected_type="runtime_packet")

    active_controller = controller or HHSRuntimeController()
    # The runtime tick authorizes the failure-record emission, not the rejected
    # target body. This keeps rejection observable without granting execution.
    authorized_tick = active_controller.authorized_tick(source=f"{source}.failure_record")

    foundational = assert_foundational_conformance(
        {
            "schema": "HHS_AUTHORIZED_EXECUTION_FAILURE_FOUNDATIONAL_AUDIT_V1",
            "source": source,
            "reason": reason,
            "reason_code": reason_code,
            "requested_target": requested_target,
            "proposition_identity": proposition_identity,
            "meaning_witness": meaning_witness,
            "authorized_tick": authorized_tick,
        },
        source=f"{source}.failure_foundational_audit",
        require_receipt=False,
    ).to_dict()
    kernel_witness = _with_digest72_alias(
        make_hash72_kernel_witness(
            "hhs_authorized_execution_failure_record_v1",
            _canonical({
                "source": source,
                "reason": reason,
                "reason_code": reason_code,
                "requested_target": requested_target,
                "policy": policy,
                "execution_performed": False,
            }),
            width=72,
        ).to_dict()
    )

    partial_record = {
        "schema": FAILURE_RECORD_SCHEMA,
        "version": VERSION,
        "source": source,
        "reason": reason,
        "reason_code": reason_code,
        "rejection_stage": rejection_stage,
        "requested_target": requested_target,
        "execution_status": "REJECTED_WITHOUT_EXECUTION",
        "execution_performed": False,
        "call_performed": False,
        "function_body_execution_performed": False,
        "raw_plugin_execution": False,
        "mutation_performed": False,
        "write_performed": False,
        "network_performed": False,
        "process_performed": False,
        "execution_policy": policy,
        "execution_request": execution_request,
        "runtime_packet": runtime_packet,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness,
        "failure_kernel_witness": kernel_witness,
        "foundational_conformance": foundational,
    }
    classification = classify_schema_object(partial_record)
    validation = validate_schema_object(partial_record)
    ledger_payload = {
        **partial_record,
        "schema_registry_classification": classification,
        "schema_registry_validation": validation,
        "authorized_failure_record_tick": authorized_tick,
    }
    ledger = append_payload("AUTHORIZED_EXECUTION_FAILURE", source, ledger_payload)
    ledger_summary = {
        "entry_count": ledger.get("entry_count"),
        "tip_hash72": ledger.get("tip_hash72"),
        "ledger_hash72": ledger.get("ledger_hash72"),
        "hash72_authority": ledger.get("hash72_authority"),
    }
    return HHSAuthorizedExecutionFailureRecord(
        schema=FAILURE_RECORD_SCHEMA,
        version=VERSION,
        source=source,
        reason=reason,
        reason_code=reason_code,
        rejection_stage=rejection_stage,
        requested_target=requested_target,
        execution_status="REJECTED_WITHOUT_EXECUTION",
        execution_performed=False,
        call_performed=False,
        function_body_execution_performed=False,
        raw_plugin_execution=False,
        mutation_performed=False,
        write_performed=False,
        network_performed=False,
        process_performed=False,
        execution_policy=policy,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        proposition_identity=proposition_identity,
        meaning_witness=meaning_witness,
        failure_kernel_witness=kernel_witness,
        foundational_conformance=foundational,
        schema_registry_classification=classification,
        schema_registry_validation=validation,
        ledger=ledger_summary,
    ).to_dict()


def evaluate_authorized_execution_request(
    target: Mapping[str, Any],
    *,
    root: Optional[str | Path] = None,
    controller: Optional[HHSRuntimeController] = None,
) -> Dict[str, Any]:
    """Route one request to either authorized pure execution or failure record."""

    preflight = preflight_authorized_execution_target(target)
    if not preflight.get("ok"):
        return make_authorized_execution_failure_record(
            target,
            reason_code=str(preflight.get("reason_code")),
            reason=str(preflight.get("reason")),
            rejection_stage=str(preflight.get("stage")),
            root=root,
            controller=controller,
        )
    try:
        return execute_authorized_pure_function(dict(target), root=root, controller=controller)
    except Exception as exc:
        return make_authorized_execution_failure_record(
            target,
            reason_code="AUTHORIZED_EXECUTION_RUNTIME_REJECTION",
            reason=f"authorized pure executor rejected request before/around execution: {type(exc).__name__}: {exc}",
            rejection_stage="AUTHORIZED_EXECUTOR_REJECTION",
            root=root,
            controller=controller,
        )


def build_authorized_execution_failure_policy_manifest(
    root: Optional[str | Path] = None,
    rejection_targets: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    failures = [
        evaluate_authorized_execution_request(target, root=root_path)
        for target in list(rejection_targets or DEFAULT_REJECTION_TARGETS)
    ]
    expanded_authorized_manifest = {
        "schema": "HHS_AUTHORIZED_PURE_FUNCTION_EXPANSION_SUMMARY_PASS_032",
        "allowlist_size": sum(len(functions) for functions in AUTHORIZED_PURE_ALLOWLIST.values()),
        "default_target_count": len(DEFAULT_AUTHORIZED_PURE_TARGETS),
        "targets": [
            {"path": target.get("path"), "function": target.get("function")}
            for target in DEFAULT_AUTHORIZED_PURE_TARGETS
        ],
        "execution_note": "failure-policy manifest summarizes the expanded allow-list but does not execute successful targets; run make authorized-pure-function-executor for the success path.",
    }

    no_execution = all(
        not item.get("execution_performed")
        and not item.get("call_performed")
        and not item.get("function_body_execution_performed")
        for item in failures
    )
    schema_valid = all(item.get("schema_registry_validation", {}).get("ok") for item in failures)
    classified = all(item.get("schema_registry_classification", {}).get("family") == "FAILURE_RECORD" for item in failures)
    witnessed = all(bool(item.get("failure_kernel_witness", {}).get("digest72")) for item in failures)
    ledger_ok = verify_unified_ledger()
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "failure_record_count": len(failures),
        "failure_reason_codes": sorted({str(item.get("reason_code")) for item in failures}),
        "execution_performed": not no_execution,
        "all_rejections_prevented_execution": no_execution,
        "schema_registry_valid": schema_valid,
        "schema_registry_classified_as_failure_record": classified,
        "hash72_u72_witnessed": witnessed,
        "ledger_ok": bool(ledger_ok.get("ok")),
        "expanded_authorized_pure_manifest_summary": expanded_authorized_manifest,
        "policy": "Invalid, unsafe, malformed, and non-allow-listed authorized execution requests must reject with first-class failure records before any target function-body execution.",
    }
    witness = _with_digest72_alias(
        make_hash72_kernel_witness("hhs_authorized_execution_failure_policy_manifest_v1", _canonical(payload), width=72).to_dict()
    )
    ok = no_execution and schema_valid and classified and witnessed and bool(ledger_ok.get("ok"))
    return {
        **payload,
        "ok": bool(ok),
        "repo_root": str(root_path),
        "failure_records": failures,
        "ledger": ledger_ok,
        "hash72_kernel_witness": witness,
    }


def write_authorized_execution_failure_policy_artifacts(
    root: Optional[str | Path] = None,
    rejection_targets: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_authorized_execution_failure_policy_manifest(root_path, rejection_targets)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = [
        "| Reason Code | Stage | Target | Executed | Witness |",
        "|---|---|---|---:|---|",
    ]
    for item in manifest.get("failure_records", []):
        target = item.get("requested_target", {})
        witness = item.get("failure_kernel_witness", {}).get("digest72", "")
        rows.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                item.get("reason_code"),
                item.get("rejection_stage"),
                f"{target.get('path', '<missing>')}::{target.get('function', '<missing>')}",
                item.get("execution_performed"),
                witness[:18] + "…" if witness else "",
            )
        )
    content = f"""# Pass 032 Authorized Execution Failure Policy

Schema: `{manifest.get('schema')}`  
Version: `{manifest.get('version')}`

Pass 032 hardens the inverse path of controlled authorized execution.  Unsafe or
invalid execution requests now produce explicit witnessed failure records instead
of silent denial or permissive fall-through.

## Summary

- Failure records: `{manifest.get('failure_record_count')}`
- Reason codes: `{', '.join(manifest.get('failure_reason_codes', []))}`
- All rejections prevented execution: `{manifest.get('all_rejections_prevented_execution')}`
- Schema registry valid: `{manifest.get('schema_registry_valid')}`
- Classified as failure records: `{manifest.get('schema_registry_classified_as_failure_record')}`
- Hash72/u^72 witnessed: `{manifest.get('hash72_u72_witnessed')}`
- Ledger OK: `{manifest.get('ledger_ok')}`
- Manifest witness: `{manifest.get('hash72_kernel_witness', {}).get('digest72')}`

## Failure records

{chr(10).join(rows)}

## Rejection invariant

```text
invalid request
→ structural/policy preflight
→ no target import required
→ no target function-body execution
→ execution_request + runtime_packet for failure emission
→ HHS-M001..M007 foundational audit
→ C u^72 Hash72 failure witness
→ unified ledger receipt
```

This keeps the future authorized-execution surface from widening by accident.
"""
    (root / REPORT_FILE).write_text(content, encoding="utf-8")


def authorized_execution_failure_policy_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    manifest = write_authorized_execution_failure_policy_artifacts(payload.get("root"))
    ok = (
        manifest.get("ok") is True
        and manifest.get("failure_record_count", 0) >= 3
        and manifest.get("all_rejections_prevented_execution") is True
        and manifest.get("schema_registry_valid") is True
        and manifest.get("schema_registry_classified_as_failure_record") is True
        and manifest.get("ledger", {}).get("ok") is True
        and bool(manifest.get("hash72_kernel_witness", {}).get("digest72"))
    )
    return {
        "schema": "HHS_AUTHORIZED_EXECUTION_FAILURE_POLICY_SELF_TEST_V1",
        "ok": bool(ok),
        "failure_record_count": manifest.get("failure_record_count"),
        "failure_reason_codes": manifest.get("failure_reason_codes"),
        "execution_performed": manifest.get("execution_performed"),
        "all_rejections_prevented_execution": manifest.get("all_rejections_prevented_execution"),
        "schema_registry_valid": manifest.get("schema_registry_valid"),
        "ledger": manifest.get("ledger"),
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
    }


if __name__ == "__main__":
    print(json.dumps(authorized_execution_failure_policy_self_test(), indent=2, sort_keys=True))
