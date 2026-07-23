from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterable, Mapping
import json
import os

from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root
from hhs_runtime.hhs_pass106_hash72_capability_truth_v1 import (
    CapabilityAdmissionError,
    CapabilityClaim,
    Hash72CapabilityLedger,
    execute_production_workload,
)

PASS_ID = "PASS_107"
FAILURE_SCHEMA = "HHS_OBSERVED_DEPENDENCY_FAILURE_V1"
CAUSE_SCHEMA = "HHS_DEPENDENCY_ROOT_CAUSE_RECEIPT_V1"
OBLIGATION_SCHEMA = "HHS_CAPABILITY_REPAIR_OBLIGATION_V1"
PROPOSAL_SCHEMA = "HHS_WITNESSED_REPAIR_PROPOSAL_V1"
MUTATION_SCHEMA = "HHS_WITNESSED_REPAIR_MUTATION_V1"
CLOSURE_SCHEMA = "HHS_WITNESSED_REPAIR_CLOSURE_V1"

REJECTION_CODES = {
    "REJECT_REPAIR_WITHOUT_OBSERVED_FAILURE",
    "REJECT_UNPROVEN_ROOT_CAUSE",
    "REJECT_SYMPTOM_PATCH_AS_ROOT_REPAIR",
    "REJECT_REPAIR_OUTSIDE_CAUSAL_PATH",
    "REJECT_UNAUTHORIZED_REPAIR_MUTATION",
    "REJECT_REPAIR_SCOPE_EXPANSION",
    "REJECT_RECLASSIFICATION_AS_REPAIR",
    "REJECT_UNPROVEN_SUPERSESSION",
    "REJECT_REPAIR_WITHOUT_ROLLBACK_BOUNDARY",
    "REJECT_REPAIR_WITHOUT_PRODUCTION_VALIDATION",
    "REJECT_REPAIR_THAT_WEAKENS_NEGATIVE_BOUNDARY",
    "REJECT_FAILED_REPAIR_WITHOUT_ROLLBACK",
    "REJECT_OBLIGATION_CLOSED_WITHOUT_NEW_ADMISSION",
    "REJECT_NONDETERMINISTIC_REPAIR_REPLAY",
}


class RepairError(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
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


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(_canonical(value), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


@dataclass(frozen=True)
class RepairLease:
    lease_id: str
    allowed_target: str
    allowed_operation: str
    maximum_mutations: int = 1
    rollback_required: bool = True

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass107_repair_lease_v1", asdict(self))


@dataclass(frozen=True)
class CanonicalDependencyContract:
    capability_id: str
    module: str
    function: str
    claim: str

    @property
    def entrypoint(self) -> str:
        return f"{self.module}.{self.function}"

    @property
    def contract_root_hash72(self) -> str:
        return _hash("hhs_pass107_dependency_contract_v1", asdict(self))


class WitnessedDependencyRepairAgent:
    """Production repair agent for rooted dependency-binding failures.

    It does not implement the target capability. It observes the real bound
    production entrypoint, traces the binding back to its canonical contract,
    mutates only an explicitly leased binding file, validates by executing the
    real target workload, and readmits the repaired capability through Pass 106.
    """

    def __init__(self, contract: CanonicalDependencyContract) -> None:
        self.contract = contract
        self.state = "IDLE"
        self._failure: dict[str, Any] | None = None
        self._cause: dict[str, Any] | None = None
        self._obligation: dict[str, Any] | None = None

    def observe_failure(self, binding_path: Path) -> dict[str, Any]:
        binding = _read_json(binding_path)
        module = str(binding.get("module", ""))
        function = str(binding.get("function", ""))
        observed_error: str | None = None
        observed_code: str | None = None
        try:
            execute_production_workload(module, function)
        except Exception as exc:  # the actual production invocation failed
            observed_error = str(exc)
            observed_code = getattr(exc, "code", type(exc).__name__)
        if observed_error is None:
            raise RepairError("REJECT_REPAIR_WITHOUT_OBSERVED_FAILURE", "bound production dependency is functioning")
        failure = {
            "schema": FAILURE_SCHEMA,
            "capability_id": self.contract.capability_id,
            "binding_path": str(binding_path.resolve()),
            "observed_entrypoint": f"{module}.{function}",
            "expected_entrypoint": self.contract.entrypoint,
            "failure_code": observed_code,
            "failure_message": observed_error,
            "binding_snapshot_root_hash72": _hash("hhs_pass107_broken_binding_snapshot_v1", binding),
            "status": "FAILURE_OBSERVED",
        }
        failure["failure_receipt_root_hash72"] = _hash("hhs_pass107_observed_dependency_failure_v1", failure)
        self._failure = failure
        self.state = "FAILURE_OBSERVED"
        return failure

    def trace_dependencies(self, binding_path: Path) -> dict[str, Any]:
        if not self._failure:
            raise RepairError("REJECT_REPAIR_WITHOUT_OBSERVED_FAILURE", "trace requires an observed failure")
        binding = _read_json(binding_path)
        path = [
            {
                "source": self._failure["failure_receipt_root_hash72"],
                "relation": "FAILED_THROUGH",
                "target": _hash("hhs_pass107_binding_file_v1", binding),
            },
            {
                "source": _hash("hhs_pass107_binding_file_v1", binding),
                "relation": "SHOULD_BIND",
                "target": self.contract.contract_root_hash72,
            },
            {
                "source": self.contract.contract_root_hash72,
                "relation": "IMPLEMENTED_BY",
                "target": _hash("hhs_pass107_expected_entrypoint_v1", self.contract.entrypoint),
            },
        ]
        mismatch = f"{binding.get('module', '')}.{binding.get('function', '')}" != self.contract.entrypoint
        if not mismatch:
            raise RepairError("REJECT_UNPROVEN_ROOT_CAUSE", "binding matches contract; no causal mismatch proven")
        cause = {
            "schema": CAUSE_SCHEMA,
            "failure_receipt_root_hash72": self._failure["failure_receipt_root_hash72"],
            "ordered_dependency_path": path,
            "root_cause_class": "BROKEN_DEPENDENCY_BINDING",
            "root_cause_root_hash72": _hash(
                "hhs_pass107_root_cause_v1",
                {"actual": binding, "expected_entrypoint": self.contract.entrypoint},
            ),
            "affected_capability_roots": [self.contract.contract_root_hash72],
            "localization_confidence": "PROVEN_BY_BINDING_CONTRACT_MISMATCH",
            "status": "ROOT_CAUSE_LOCALIZED",
        }
        cause["localization_receipt_root_hash72"] = _hash("hhs_pass107_dependency_root_cause_receipt_v1", cause)
        self._cause = cause
        self.state = "ROOT_CAUSE_LOCALIZED"
        return cause

    def open_obligation(self) -> dict[str, Any]:
        if not self._cause:
            raise RepairError("REJECT_UNPROVEN_ROOT_CAUSE", "obligation requires localized root cause")
        obligation = {
            "schema": OBLIGATION_SCHEMA,
            "capability_id": self.contract.capability_id,
            "claimed_behavior_root_hash72": _hash("hhs_pass107_claimed_behavior_v1", self.contract.claim),
            "observed_defect_root_hash72": self._cause["root_cause_root_hash72"],
            "required_disposition": "REPAIR_OR_PROVEN_SUPERSESSION",
            "repair_status": "OPEN",
            "replacement_capability_root_hash72": None,
            "production_test_receipt_root_hash72": None,
            "closure_receipt_root_hash72": None,
        }
        obligation["repair_obligation_root_hash72"] = _hash("hhs_pass107_capability_repair_obligation_v1", obligation)
        self._obligation = obligation
        self.state = "REPAIR_OBLIGATION_OPEN"
        return obligation

    def propose(self, binding_path: Path) -> dict[str, Any]:
        if not self._obligation:
            raise RepairError("REJECT_UNPROVEN_ROOT_CAUSE", "proposal requires open obligation")
        proposal = {
            "schema": PROPOSAL_SCHEMA,
            "repair_obligation_root_hash72": self._obligation["repair_obligation_root_hash72"],
            "root_cause_root_hash72": self._cause["root_cause_root_hash72"] if self._cause else None,
            "repair_class": "RECONNECT_EXISTING_ADMITTED_DEPENDENCY",
            "target_path": str(binding_path.resolve()),
            "proposed_binding": {
                "schema": "HHS_RUNTIME_DEPENDENCY_BINDING_V1",
                "capability_id": self.contract.capability_id,
                "module": self.contract.module,
                "function": self.contract.function,
            },
            "reused_capability_roots": [self.contract.contract_root_hash72],
            "new_implementation_required": False,
            "rollback_required": True,
            "status": "REPAIR_PROPOSED",
        }
        proposal["repair_proposal_root_hash72"] = _hash("hhs_pass107_witnessed_repair_proposal_v1", proposal)
        self.state = "REPAIR_PROPOSED"
        return proposal

    def execute(self, proposal: Mapping[str, Any], lease: RepairLease) -> dict[str, Any]:
        target = Path(str(proposal["target_path"])).resolve()
        if lease.allowed_target != str(target) or lease.allowed_operation != "REPLACE_DEPENDENCY_BINDING":
            raise RepairError("REJECT_UNAUTHORIZED_REPAIR_MUTATION", "lease does not authorize exact target and operation")
        if lease.maximum_mutations != 1 or not lease.rollback_required:
            raise RepairError("REJECT_REPAIR_SCOPE_EXPANSION", "repair must be one mutation with rollback")
        before_text = target.read_text(encoding="utf-8")
        before = json.loads(before_text)
        proposed = dict(proposal["proposed_binding"])
        _write_json_atomic(target, proposed)
        mutation = {
            "schema": MUTATION_SCHEMA,
            "repair_proposal_root_hash72": proposal["repair_proposal_root_hash72"],
            "repair_lease_root_hash72": lease.root_hash72,
            "target_path": str(target),
            "target_root_before_hash72": _hash("hhs_pass107_repair_target_before_v1", before),
            "mutation_operation": "REPLACE_DEPENDENCY_BINDING",
            "target_root_after_hash72": _hash("hhs_pass107_repair_target_after_v1", proposed),
            "rollback_snapshot": before,
            "status": "REPAIR_EXECUTED_PENDING_VALIDATION",
        }
        mutation["mutation_receipt_root_hash72"] = _hash("hhs_pass107_witnessed_repair_mutation_v1", mutation)
        self.state = "REPAIR_EXECUTING"
        return mutation

    def validate_or_rollback(self, mutation: Mapping[str, Any], *, negative_evidence_roots: Iterable[str]) -> dict[str, Any]:
        target = Path(str(mutation["target_path"]))
        binding = _read_json(target)
        try:
            evidence = execute_production_workload(str(binding["module"]), str(binding["function"]))
            ledger = Hash72CapabilityLedger()
            claim = CapabilityClaim(
                capability_id=self.contract.capability_id,
                implementation_class="NATIVE_VERIFIED",
                module=self.contract.module,
                function=self.contract.function,
                claim=self.contract.claim,
            )
            admission = ledger.admit_native(
                claim,
                positive_evidence=evidence,
                negative_evidence_roots=list(negative_evidence_roots),
                reachability_root_hash72=_hash("hhs_pass107_repaired_reachability_v1", {"entrypoint": self.contract.entrypoint, "reachable": True}),
                conformance_root_hash72=_hash("hhs_pass107_repaired_conformance_v1", {"invariants": ["HHS-I002", "HHS-I003", "HHS-I005", "HHS-I011", "HHS-I012", "HHS-I014", "HHS-I015"]}),
            )
            invocation = ledger.verify_invocation(self.contract.capability_id)
        except Exception as exc:
            _write_json_atomic(target, mutation["rollback_snapshot"])
            rollback = {
                "schema": "HHS_FAILED_REPAIR_ROLLBACK_V1",
                "mutation_receipt_root_hash72": mutation["mutation_receipt_root_hash72"],
                "failure": str(exc),
                "restored_root_hash72": _hash("hhs_pass107_rollback_restored_v1", mutation["rollback_snapshot"]),
                "repair_status": "ROLLED_BACK",
                "obligation_remains_open": True,
            }
            rollback["rollback_receipt_root_hash72"] = _hash("hhs_pass107_failed_repair_rollback_v1", rollback)
            self.state = "ROLLED_BACK"
            return rollback

        if not self._obligation:
            raise RepairError("REJECT_REPAIR_WITHOUT_OBSERVED_FAILURE", "missing repair obligation")
        closure = {
            "schema": CLOSURE_SCHEMA,
            "repair_obligation_root_hash72": self._obligation["repair_obligation_root_hash72"],
            "root_cause_receipt_root_hash72": self._cause["localization_receipt_root_hash72"] if self._cause else None,
            "mutation_receipt_roots": [mutation["mutation_receipt_root_hash72"]],
            "original_failure_replay_root_hash72": self._failure["failure_receipt_root_hash72"] if self._failure else None,
            "repaired_execution_receipt_root_hash72": evidence["execution_receipt_root_hash72"],
            "negative_attack_receipt_roots": list(negative_evidence_roots),
            "new_capability_admission_root_hash72": admission["capability_admission_root_hash72"],
            "invocation_admission_root_hash72": invocation["invocation_admission_root_hash72"],
            "repair_status": "REPAIRED_AND_PRODUCTION_VALIDATED",
            "parallel_repair_implementation_used": False,
            "mock_components": [],
        }
        closure["repair_closure_root_hash72"] = _hash("hhs_pass107_witnessed_repair_closure_v1", closure)
        self._obligation["repair_status"] = "REPAIRED_AND_PRODUCTION_VALIDATED"
        self._obligation["production_test_receipt_root_hash72"] = evidence["execution_receipt_root_hash72"]
        self._obligation["closure_receipt_root_hash72"] = closure["repair_closure_root_hash72"]
        self.state = "REPAIRED"
        return closure

    def background_scan(self, binding_paths: Iterable[Path]) -> dict[str, Any]:
        records: list[dict[str, Any]] = []
        for path in binding_paths:
            try:
                binding = _read_json(path)
                execute_production_workload(str(binding.get("module", "")), str(binding.get("function", "")))
                records.append({"path": str(path), "status": "HEALTHY"})
            except Exception as exc:
                records.append({"path": str(path), "status": "BROKEN_DEPENDENCY_OBSERVED", "failure": str(exc)})
        out = {
            "schema": "HHS_PASS107_BACKGROUND_DEPENDENCY_SCAN_V1",
            "records": records,
            "broken_count": sum(1 for r in records if r["status"] == "BROKEN_DEPENDENCY_OBSERVED"),
            "mutation_performed": False,
        }
        out["scan_root_hash72"] = _hash("hhs_pass107_background_dependency_scan_v1", out)
        return out


def _committed_negative_roots(repo_root: Path) -> list[str]:
    path = repo_root / "PASS_105_4_PRODUCTION_NEGATIVE_ATTACK_REGISTRY.json"
    data = _read_json(path)
    roots: list[str] = []
    for group in data.get("groups", []):
        for record in group.get("records", []):
            value = record.get("attack_receipt_root_hash72")
            if record.get("passed") and value:
                roots.append(str(value))
    if not roots:
        # Alternate top-level layout retained for compatibility with release artifacts.
        for record in data.get("records", []):
            value = record.get("attack_receipt_root_hash72")
            if record.get("passed") and value:
                roots.append(str(value))
    if not roots:
        raise RepairError("REJECT_REPAIR_WITHOUT_PRODUCTION_VALIDATION", "no committed production negative evidence")
    return roots


def run_pass107_workload(repo_root: str | Path | None = None) -> dict[str, Any]:
    root_path = Path(repo_root or Path(__file__).resolve().parents[1])
    contract = CanonicalDependencyContract(
        capability_id="hhs:pass105_6:real_c_asm_backend",
        module="hhs_runtime.hhs_pass105_6_real_c_asm_backend_closure_v1",
        function="pass105_6_self_test",
        claim="Compile and execute generated C11 and x86-64 assembly artifacts through real toolchains.",
    )
    negative_roots = _committed_negative_roots(root_path)[:2]

    with TemporaryDirectory(prefix="hhs-pass107-") as temp_dir:
        binding_path = Path(temp_dir) / "dependency_binding.json"
        broken = {
            "schema": "HHS_RUNTIME_DEPENDENCY_BINDING_V1",
            "capability_id": contract.capability_id,
            "module": "hhs_runtime.hhs_pass105_6_real_c_asm_backend_closure_v1",
            "function": "missing_backend_entrypoint",
        }
        _write_json_atomic(binding_path, broken)
        agent = WitnessedDependencyRepairAgent(contract)
        background = agent.background_scan([binding_path])
        failure = agent.observe_failure(binding_path)
        cause = agent.trace_dependencies(binding_path)
        obligation = agent.open_obligation()
        proposal = agent.propose(binding_path)
        lease = RepairLease(
            lease_id="pass107:repair:binding:001",
            allowed_target=str(binding_path.resolve()),
            allowed_operation="REPLACE_DEPENDENCY_BINDING",
        )
        bad_proposal = dict(proposal)
        bad_proposal["proposed_binding"] = dict(proposal["proposed_binding"])
        bad_proposal["proposed_binding"]["function"] = "still_missing_backend_entrypoint"
        bad_proposal["repair_proposal_root_hash72"] = _hash("hhs_pass107_failed_repair_proposal_v1", bad_proposal)
        failed_mutation = agent.execute(bad_proposal, lease)
        failed_repair_rollback = agent.validate_or_rollback(failed_mutation, negative_evidence_roots=negative_roots)
        if failed_repair_rollback.get("repair_status") != "ROLLED_BACK":
            raise RepairError("REJECT_FAILED_REPAIR_WITHOUT_ROLLBACK", "invalid repair did not roll back")
        if _read_json(binding_path) != broken:
            raise RepairError("REJECT_FAILED_REPAIR_WITHOUT_ROLLBACK", "rollback did not restore the original broken binding")
        mutation = agent.execute(proposal, lease)
        closure = agent.validate_or_rollback(mutation, negative_evidence_roots=negative_roots)
        repaired_binding = _read_json(binding_path)

    if closure.get("repair_status") != "REPAIRED_AND_PRODUCTION_VALIDATED":
        raise RepairError("REJECT_REPAIR_WITHOUT_PRODUCTION_VALIDATION", "production repair did not close")
    out = {
        "schema": "HHS_PASS107_WITNESSED_DEPENDENCY_REPAIR_CLOSURE_V1",
        "pass_id": PASS_ID,
        "background_scan": background,
        "observed_failure": failure,
        "root_cause": cause,
        "repair_obligation": obligation,
        "repair_proposal": proposal,
        "failed_repair_rollback": failed_repair_rollback,
        "repair_mutation": mutation,
        "repair_closure": closure,
        "repaired_binding": repaired_binding,
        "agent_final_state": agent.state,
        "real_production_workload_executed": True,
        "new_capability_admission_created": True,
        "parallel_repair_implementation_used": False,
        "mock_components": [],
        "status": "PASS",
    }
    out["closure_root_hash72"] = _hash("hhs_pass107_witnessed_dependency_repair_closure_v1", out)
    return out


def pass107_self_test() -> dict[str, Any]:
    return run_pass107_workload()
