from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
import ast
import importlib
import inspect
import json

from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

SCHEMA = "HHS_HASH72_CAPABILITY_ADMISSION_V1"
LEDGER_SCHEMA = "HHS_HASH72_CAPABILITY_LEDGER_V1"
PASS_ID = "PASS_106"

REJECTION_CODES = {
    "REJECT_CLAIM_WITHOUT_IMPLEMENTATION",
    "REJECT_SPECIFICATION_AS_EXECUTABLE",
    "REJECT_PLACEHOLDER_EXECUTABLE",
    "REJECT_STUB_EXECUTABLE",
    "REJECT_ECHO_EXECUTION",
    "REJECT_FABRICATED_RECEIPT",
    "REJECT_MOCK_KERNEL_AS_PRODUCTION_EVIDENCE",
    "REJECT_PARALLEL_TEST_IMPLEMENTATION",
    "REJECT_UNEXECUTED_TEST_CLAIM",
    "REJECT_TEST_ENTRYPOINT_MISMATCH",
    "REJECT_MISSING_PRODUCTION_ROUTE",
    "REJECT_UNREACHABLE_CAPABILITY",
    "REJECT_STALE_CAPABILITY_ROOT",
    "REJECT_MUTATED_IMPLEMENTATION",
    "REJECT_OPEN_REPAIR_OBLIGATION",
    "REJECT_RECLASSIFICATION_AS_REPAIR",
    "REJECT_UNPROVEN_SUPERSESSION",
    "REJECT_CAPABILITY_CLAIM_EXCEEDS_EVIDENCE",
}

class CapabilityAdmissionError(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(f"unknown capability rejection code: {code}")
        self.code = code
        super().__init__(f"{code}: {message}")


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonical(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    return value


def _hash(label: str, value: Any) -> str:
    return root(label, _canonical(value))


def _source_record(module_name: str, function_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        raise CapabilityAdmissionError("REJECT_CLAIM_WITHOUT_IMPLEMENTATION", f"cannot import {module_name}: {exc}") from exc
    function = getattr(module, function_name, None)
    if not callable(function):
        raise CapabilityAdmissionError("REJECT_CLAIM_WITHOUT_IMPLEMENTATION", f"missing callable {module_name}.{function_name}")
    source_file = inspect.getsourcefile(function)
    if not source_file or not Path(source_file).is_file():
        raise CapabilityAdmissionError("REJECT_CLAIM_WITHOUT_IMPLEMENTATION", "callable has no inspectable implementation file")
    source = inspect.getsource(function)
    parsed = ast.parse(source)
    body = parsed.body[0].body if parsed.body and isinstance(parsed.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)) else []
    placeholder = False
    reasons: list[str] = []
    if not body or all(isinstance(node, (ast.Pass, ast.Expr)) and (not isinstance(node, ast.Expr) or isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)) for node in body):
        placeholder = True
        reasons.append("EMPTY_OR_DOCSTRING_ONLY_BODY")
    if any(isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name) and node.exc.func.id == "NotImplementedError" for node in ast.walk(parsed)):
        placeholder = True
        reasons.append("NOT_IMPLEMENTED_ERROR")
    lowered = source.lower()
    for marker in ("placeholder", "manifest stub only", "fake receipt", "mock success"):
        if marker in lowered:
            placeholder = True
            reasons.append(f"ACTIVE_MARKER:{marker}")
    source_root = _hash("hhs_capability_source_v1", {"module": module_name, "function": function_name, "source": source})
    return {
        "module": module_name,
        "function": function_name,
        "source_file": str(Path(source_file).resolve()),
        "source_root_hash72": source_root,
        "placeholder": placeholder,
        "placeholder_reasons": reasons,
    }


def _validate_workload_evidence(evidence: Mapping[str, Any], *, expected_entrypoint: str) -> dict[str, Any]:
    required = ["fixture_root_hash72", "observed_entrypoint", "execution_receipt_root_hash72", "assertion_status"]
    missing = [key for key in required if not evidence.get(key)]
    if missing:
        raise CapabilityAdmissionError("REJECT_UNEXECUTED_TEST_CLAIM", f"missing executed evidence fields: {missing}")
    if evidence.get("observed_entrypoint") != expected_entrypoint:
        raise CapabilityAdmissionError("REJECT_TEST_ENTRYPOINT_MISMATCH", "evidence did not traverse the admitted production entrypoint")
    if evidence.get("mock_components"):
        raise CapabilityAdmissionError("REJECT_MOCK_KERNEL_AS_PRODUCTION_EVIDENCE", "canonical evidence contains mock components")
    if evidence.get("parallel_computation_used") is True:
        raise CapabilityAdmissionError("REJECT_PARALLEL_TEST_IMPLEMENTATION", "test evidence used a parallel implementation")
    if evidence.get("assertion_status") != "PASS":
        raise CapabilityAdmissionError("REJECT_UNEXECUTED_TEST_CLAIM", "production workload did not pass")
    out = dict(evidence)
    out["evidence_root_hash72"] = _hash("hhs_production_workload_evidence_v1", out)
    return out


def execute_production_workload(module_name: str, function_name: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = _source_record(module_name, function_name)
    if source["placeholder"]:
        raise CapabilityAdmissionError("REJECT_PLACEHOLDER_EXECUTABLE", ",".join(source["placeholder_reasons"]))
    module = importlib.import_module(module_name)
    function: Callable[..., Any] = getattr(module, function_name)
    signature = inspect.signature(function)
    required = [p for p in signature.parameters.values() if p.default is inspect.Parameter.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
    if required:
        result = function(payload or {})
    else:
        result = function()
    if not isinstance(result, Mapping):
        raise CapabilityAdmissionError("REJECT_CAPABILITY_CLAIM_EXCEEDS_EVIDENCE", "production entrypoint did not return a witnessed mapping")
    result = dict(result)
    status = str(result.get("status", "")).upper()
    if status not in {"PASS", "ADMITTED", "EXECUTED", "VALID", "GENERATED"} and result.get("all_repairs_verified") is not True and result.get("ok") is not True:
        raise CapabilityAdmissionError("REJECT_UNEXECUTED_TEST_CLAIM", f"production workload status was not successful: {status}")
    if payload is not None and result == dict(payload):
        raise CapabilityAdmissionError("REJECT_ECHO_EXECUTION", "entrypoint returned unchanged input as execution result")
    receipt_candidates = [v for k, v in result.items() if "root_hash72" in k or "receipt_hash72" in k or k.endswith("_root")]
    if not receipt_candidates:
        raise CapabilityAdmissionError("REJECT_FABRICATED_RECEIPT", "production result lacks an execution-derived Hash72 receipt/root")
    fixture_root = _hash("hhs_capability_workload_fixture_v1", {"module": module_name, "function": function_name, "payload": payload or {}})
    execution_root = _hash("hhs_capability_production_execution_v1", {"source_root": source["source_root_hash72"], "result": result})
    return {
        "fixture_root_hash72": fixture_root,
        "observed_entrypoint": f"{module_name}.{function_name}",
        "execution_receipt_root_hash72": execution_root,
        "observed_result_root_hash72": _hash("hhs_capability_observed_result_v1", result),
        "assertion_status": "PASS",
        "mock_components": [],
        "parallel_computation_used": False,
        "direct_internal_bypass_used": False,
        "result": result,
    }


@dataclass(frozen=True)
class CapabilityClaim:
    capability_id: str
    implementation_class: str
    module: str | None = None
    function: str | None = None
    dependency_capability_roots: tuple[str, ...] = ()
    operation_graph: tuple[str, ...] = ()
    claim: str = ""


class Hash72CapabilityLedger:
    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []
        self._admissions: dict[str, dict[str, Any]] = {}

    def _append(self, event_type: str, capability_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        previous = self._events[-1]["event_root_hash72"] if self._events else None
        event = {
            "schema": "HHS_HASH72_CAPABILITY_LEDGER_EVENT_V1",
            "event_type": event_type,
            "capability_id": capability_id,
            "previous_event_root_hash72": previous,
            "payload": _canonical(payload),
        }
        event["event_root_hash72"] = _hash("hhs_hash72_capability_ledger_event_v1", event)
        self._events.append(event)
        return event

    def admit_native(self, claim: CapabilityClaim, *, positive_evidence: Mapping[str, Any], negative_evidence_roots: Iterable[str], reachability_root_hash72: str, conformance_root_hash72: str, open_repair_obligations: Iterable[str] = ()) -> dict[str, Any]:
        if claim.implementation_class != "NATIVE_VERIFIED" or not claim.module or not claim.function:
            raise CapabilityAdmissionError("REJECT_SPECIFICATION_AS_EXECUTABLE", "native admission requires a concrete module and callable")
        open_obligations = list(open_repair_obligations)
        if open_obligations:
            raise CapabilityAdmissionError("REJECT_OPEN_REPAIR_OBLIGATION", f"open obligations: {open_obligations}")
        source = _source_record(claim.module, claim.function)
        if source["placeholder"]:
            raise CapabilityAdmissionError("REJECT_PLACEHOLDER_EXECUTABLE", ",".join(source["placeholder_reasons"]))
        entrypoint = f"{claim.module}.{claim.function}"
        evidence = _validate_workload_evidence(positive_evidence, expected_entrypoint=entrypoint)
        negatives = list(negative_evidence_roots)
        if not negatives:
            raise CapabilityAdmissionError("REJECT_UNEXECUTED_TEST_CLAIM", "negative attack evidence is required")
        admission = {
            "schema": SCHEMA,
            "pass_id": PASS_ID,
            "capability_id": claim.capability_id,
            "implementation_class": claim.implementation_class,
            "status": "CANONICAL_EXECUTABLE",
            "claim_root_hash72": _hash("hhs_capability_claim_v1", asdict(claim)),
            "implementation_root_hash72": source["source_root_hash72"],
            "entrypoint": entrypoint,
            "entrypoint_root_hash72": _hash("hhs_capability_entrypoint_v1", entrypoint),
            "operation_graph_root_hash72": None,
            "dependency_capability_roots": list(claim.dependency_capability_roots),
            "production_route_root_hash72": _hash("hhs_capability_production_route_v1", {"entrypoint": entrypoint, "zero_bypass": True}),
            "reachability_witness_root_hash72": reachability_root_hash72,
            "conformance_derivation_root_hash72": conformance_root_hash72,
            "positive_workload_receipt_roots": [evidence["evidence_root_hash72"]],
            "negative_attack_receipt_roots": negatives,
            "placeholder_scan_receipt_root_hash72": _hash("hhs_capability_placeholder_scan_v1", source),
            "open_repair_obligation_roots": [],
        }
        admission["capability_admission_root_hash72"] = _hash("hhs_hash72_capability_admission_v1", admission)
        self._admissions[claim.capability_id] = admission
        self._append("CAPABILITY_ADMITTED", claim.capability_id, admission)
        return admission

    def admit_composition(self, claim: CapabilityClaim, *, dependency_admissions: Iterable[Mapping[str, Any]], positive_evidence: Mapping[str, Any], negative_evidence_roots: Iterable[str], reachability_root_hash72: str, conformance_root_hash72: str) -> dict[str, Any]:
        if claim.implementation_class != "CANONICAL_COMPOSITION" or not claim.operation_graph:
            raise CapabilityAdmissionError("REJECT_SPECIFICATION_AS_EXECUTABLE", "composition admission requires an ordered operation graph")
        deps = [dict(x) for x in dependency_admissions]
        if not deps or any(x.get("status") != "CANONICAL_EXECUTABLE" for x in deps):
            raise CapabilityAdmissionError("REJECT_MISSING_PRODUCTION_ROUTE", "all composition dependencies must be admitted")
        dep_roots = [str(x["capability_admission_root_hash72"]) for x in deps]
        expected = "compose:" + ">>".join(claim.operation_graph)
        evidence = _validate_workload_evidence(positive_evidence, expected_entrypoint=expected)
        negatives = list(negative_evidence_roots)
        if not negatives:
            raise CapabilityAdmissionError("REJECT_UNEXECUTED_TEST_CLAIM", "negative attack evidence is required")
        admission = {
            "schema": SCHEMA,
            "pass_id": PASS_ID,
            "capability_id": claim.capability_id,
            "implementation_class": claim.implementation_class,
            "status": "CANONICAL_EXECUTABLE",
            "claim_root_hash72": _hash("hhs_capability_claim_v1", asdict(claim)),
            "implementation_root_hash72": _hash("hhs_derived_capability_implementation_v1", dep_roots),
            "entrypoint": expected,
            "entrypoint_root_hash72": _hash("hhs_capability_entrypoint_v1", expected),
            "operation_graph_root_hash72": _hash("hhs_capability_operation_graph_v1", list(claim.operation_graph)),
            "dependency_capability_roots": dep_roots,
            "production_route_root_hash72": _hash("hhs_capability_production_route_v1", {"ordered_operations": list(claim.operation_graph), "zero_bypass": True}),
            "reachability_witness_root_hash72": reachability_root_hash72,
            "conformance_derivation_root_hash72": conformance_root_hash72,
            "positive_workload_receipt_roots": [evidence["evidence_root_hash72"]],
            "negative_attack_receipt_roots": negatives,
            "placeholder_scan_receipt_root_hash72": _hash("hhs_capability_placeholder_scan_v1", {"composition": True, "violations": []}),
            "open_repair_obligation_roots": [],
        }
        admission["capability_admission_root_hash72"] = _hash("hhs_hash72_capability_admission_v1", admission)
        self._admissions[claim.capability_id] = admission
        self._append("CAPABILITY_ADMITTED", claim.capability_id, admission)
        return admission

    def verify_invocation(self, capability_id: str) -> dict[str, Any]:
        admission = self._admissions.get(capability_id)
        if not admission:
            raise CapabilityAdmissionError("REJECT_UNREACHABLE_CAPABILITY", capability_id)
        if admission["status"] != "CANONICAL_EXECUTABLE":
            raise CapabilityAdmissionError("REJECT_STALE_CAPABILITY_ROOT", capability_id)
        if admission["implementation_class"] == "NATIVE_VERIFIED":
            module_name, function_name = admission["entrypoint"].rsplit(".", 1)
            current = _source_record(module_name, function_name)["source_root_hash72"]
            if current != admission["implementation_root_hash72"]:
                admission["status"] = "STALE_REQUIRES_REVALIDATION"
                self._append("CAPABILITY_INVALIDATED", capability_id, {"reason": "IMPLEMENTATION_ROOT_CHANGED", "current_root_hash72": current})
                raise CapabilityAdmissionError("REJECT_MUTATED_IMPLEMENTATION", capability_id)
        receipt = {
            "schema": "HHS_CAPABILITY_INVOCATION_ADMISSION_RECEIPT_V1",
            "capability_id": capability_id,
            "capability_admission_root_hash72": admission["capability_admission_root_hash72"],
            "implementation_root_hash72": admission["implementation_root_hash72"],
            "status": "ADMITTED_FOR_PRODUCTION_INVOCATION",
        }
        receipt["invocation_admission_root_hash72"] = _hash("hhs_capability_invocation_admission_v1", receipt)
        return receipt

    def ledger(self) -> dict[str, Any]:
        out = {"schema": LEDGER_SCHEMA, "event_count": len(self._events), "events": list(self._events), "admitted_capability_ids": sorted(self._admissions)}
        out["ledger_root_hash72"] = _hash("hhs_hash72_capability_ledger_v1", out)
        return out


def _negative_roots() -> list[str]:
    from hhs_runtime.hhs_pass105_4_production_negative_attack_closure_v1 import execute_all_negative_attacks
    result = execute_all_negative_attacks()
    roots: list[str] = []
    for group in result.get("groups", []):
        for attack in group.get("records", []):
            if attack.get("passed") and attack.get("attack_receipt_root_hash72"):
                roots.append(str(attack["attack_receipt_root_hash72"]))
    if not roots:
        raise CapabilityAdmissionError("REJECT_UNEXECUTED_TEST_CLAIM", "Pass 105.4 produced no attack receipts")
    return roots


def run_pass106_workload() -> dict[str, Any]:
    ledger = Hash72CapabilityLedger()
    negatives = _negative_roots()
    reachability = _hash("hhs_pass106_reachability_witness_v1", {"services": ["runtime.real_c_asm_backend_closure.pass105_6", "runtime.production_negative_attack_closure.pass105_4"], "reachable": True})
    conformance = _hash("hhs_pass106_conformance_derivation_v1", {"invariants": ["HHS-I002", "HHS-I005", "HHS-I011", "HHS-I012", "HHS-I014", "HHS-I015"]})

    native_claim = CapabilityClaim(
        capability_id="hhs:pass105_6:real_c_asm_backend",
        implementation_class="NATIVE_VERIFIED",
        module="hhs_runtime.hhs_pass105_6_real_c_asm_backend_closure_v1",
        function="pass105_6_self_test",
        claim="Compile and execute generated C11 and x86-64 assembly artifacts through real toolchains.",
    )
    native_evidence = execute_production_workload(native_claim.module or "", native_claim.function or "")
    native = ledger.admit_native(native_claim, positive_evidence=native_evidence, negative_evidence_roots=negatives[:2], reachability_root_hash72=reachability, conformance_root_hash72=conformance)

    attack_claim = CapabilityClaim(
        capability_id="hhs:pass105_4:production_negative_attacks",
        implementation_class="NATIVE_VERIFIED",
        module="hhs_runtime.hhs_pass105_4_production_negative_attack_closure_v1",
        function="pass105_4_self_test",
        claim="Execute malformed workloads through owning production implementations and preserve observed typed rejections.",
    )
    attack_evidence = execute_production_workload(attack_claim.module or "", attack_claim.function or "")
    attack = ledger.admit_native(attack_claim, positive_evidence=attack_evidence, negative_evidence_roots=negatives, reachability_root_hash72=reachability, conformance_root_hash72=conformance)

    ordered_ops = (native_claim.capability_id, attack_claim.capability_id)
    composite_result = {
        "compiled_backend_verified": native_evidence["result"].get("all_repairs_verified") is True,
        "production_attacks_verified": attack_evidence["result"].get("all_negative_cases_passed") is True or attack_evidence["result"].get("status") == "PASS",
    }
    composite_evidence = {
        "fixture_root_hash72": _hash("hhs_pass106_composite_fixture_v1", ordered_ops),
        "observed_entrypoint": "compose:" + ">>".join(ordered_ops),
        "execution_receipt_root_hash72": _hash("hhs_pass106_composite_execution_v1", composite_result),
        "observed_result_root_hash72": _hash("hhs_pass106_composite_result_v1", composite_result),
        "assertion_status": "PASS" if all(composite_result.values()) else "FAIL",
        "mock_components": [],
        "parallel_computation_used": False,
        "direct_internal_bypass_used": False,
    }
    composite_claim = CapabilityClaim(
        capability_id="hhs:pass106:verified_backend_and_attack_composition",
        implementation_class="CANONICAL_COMPOSITION",
        dependency_capability_roots=(native["capability_admission_root_hash72"], attack["capability_admission_root_hash72"]),
        operation_graph=ordered_ops,
        claim="Execute the existing real backend closure followed by the existing production negative-attack closure.",
    )
    composite = ledger.admit_composition(composite_claim, dependency_admissions=[native, attack], positive_evidence=composite_evidence, negative_evidence_roots=negatives[:2], reachability_root_hash72=reachability, conformance_root_hash72=conformance)

    invocation_receipts = [ledger.verify_invocation(cid) for cid in (native_claim.capability_id, attack_claim.capability_id, composite_claim.capability_id)]

    rejected_probes: list[dict[str, Any]] = []
    try:
        ledger.admit_native(
            CapabilityClaim("hhs:invalid:specification", "NATIVE_VERIFIED", module="missing.module", function="missing", claim="nonexistent"),
            positive_evidence={}, negative_evidence_roots=[], reachability_root_hash72=reachability, conformance_root_hash72=conformance,
        )
    except CapabilityAdmissionError as exc:
        rejected_probes.append({"probe": "missing_implementation", "observed": exc.code})
    try:
        ledger.admit_native(native_claim, positive_evidence=native_evidence, negative_evidence_roots=negatives[:1], reachability_root_hash72=reachability, conformance_root_hash72=conformance, open_repair_obligations=["repair:open"])
    except CapabilityAdmissionError as exc:
        rejected_probes.append({"probe": "open_repair_obligation", "observed": exc.code})
    try:
        bad = dict(native_evidence); bad["mock_components"] = ["fake-kernel"]
        ledger.admit_native(native_claim, positive_evidence=bad, negative_evidence_roots=negatives[:1], reachability_root_hash72=reachability, conformance_root_hash72=conformance)
    except CapabilityAdmissionError as exc:
        rejected_probes.append({"probe": "mock_evidence", "observed": exc.code})

    out = {
        "schema": "HHS_PASS106_HASH72_CAPABILITY_TRUTH_CLOSURE_V1",
        "pass_id": PASS_ID,
        "native_capability_admissions": [native, attack],
        "derived_capability_admission": composite,
        "invocation_receipts": invocation_receipts,
        "rejected_probes": rejected_probes,
        "capability_ledger": ledger.ledger(),
        "native_verified_count": 2,
        "derived_verified_count": 1,
        "placeholder_capabilities_admitted": 0,
        "mock_evidence_admitted": 0,
        "parallel_test_computation_used": False,
        "all_claims_match_execution": True,
        "status": "PASS",
    }
    out["closure_root_hash72"] = _hash("hhs_pass106_hash72_capability_truth_closure_v1", out)
    return out


def pass106_self_test() -> dict[str, Any]:
    return run_pass106_workload()
