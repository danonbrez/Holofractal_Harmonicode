"""Pass 199 durable distributed calibration execution over Pass 190 and Pass 198."""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from hhs_backend.runtime.hhs_pass198_operation_calibration_registry_v1 import (
    Pass198OperationCalibrationRegistry,
)
from hhs_backend.runtime.pass197_exact_v1 import (
    ADDRESS_COUNT,
    CELL_COUNT,
    LANE_COUNT,
    M,
    canonical_json as hhs_canonical_json,
    cell_index,
    compact_gate,
    exact_fraction,
    fraction_payload,
    hash72 as hhs_hash72,
    matrix_power,
    original_gate,
)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_PASS190_PYTHON = _REPOSITORY_ROOT / "native_projects" / "hhs_pass190_operation_fabric" / "python"
if str(_PASS190_PYTHON) not in sys.path:
    sys.path.insert(0, str(_PASS190_PYTHON))

from hhs_pass190 import (  # noqa: E402
    DEFAULT_REGISTRY,
    HHSAuthorityContext,
    HHSOperationError,
    InvocationResult,
    OperationRecord,
    REGISTRY_SCHEMA,
    RegistryValidationError,
    StateConflictError,
    hash72 as pass190_hash72,
    hash216 as pass190_hash216,
)
from hhs_pass190_iteration3_hardening import DEFAULT_DATABASE  # noqa: E402
from hhs_pass190_iteration4 import DEFAULT_LEASE_TTL_NS, DEFAULT_LEASE_WAIT_NS  # noqa: E402
from hhs_pass190_iteration6 import ResourceRegistryStore  # noqa: E402
from hhs_pass190_iteration6_registry import _operation  # noqa: E402
from hhs_pass190_iteration7 import DurableExecutionContext  # noqa: E402
from hhs_pass190_iteration7_registry import Iteration7OperationRegistry  # noqa: E402

VERSION = "HHS_PASS_199_DISTRIBUTED_CALIBRATION_FABRIC_V1"
CONTRACT = "HHS-P199-P198-P190-DCT-WORKER-VM81-H72"
CLASSIFICATION = "HHS_PASS_199_DURABLE_DISTRIBUTED_CALIBRATION_FABRIC_VERIFIED"
REPORT_SCHEMA = "HHS_PASS_199_DISTRIBUTED_CALIBRATION_REPORT_V1"
CANDIDATE_SCHEMA = "HHS_PASS_199_IMMUTABLE_BRANCH_CANDIDATE_V1"
COMMIT_SCHEMA = "HHS_PASS_199_SINGLETON_TREE_COMMIT_V1"
BRANCH_OPERATION_ID = "calibration.evaluate_branch"
COMPLETE_OPERATION_ID = "calibration.complete_claimed"
COMMIT_OPERATION_ID = "calibration.commit_tree"
PASS199_OPERATION_IDS = (BRANCH_OPERATION_ID, COMPLETE_OPERATION_ID, COMMIT_OPERATION_ID)
PASS199_CAPABILITY = "calibration:execute"
PASS199_ADMISSION_CAPABILITY = "calibration:admit"
ZERO_HASH72 = "0" * 72


class Pass199CalibrationError(RuntimeError):
    pass


def _pass199_operation(
    operation_id: str,
    name: str,
    constructor: str,
    capability: str,
    effect_class: str,
    argument_schema: Mapping[str, Any],
    shell_form: str,
) -> dict[str, Any]:
    record = _operation(
        operation_id,
        name,
        constructor,
        capability,
        effect_class,
        argument_schema,
        "object",
        shell_form,
        operation_class="distributed-calibration",
    )
    record.update(
        {
            "introduced_by_pass": 199,
            "constructor_version": "1.0.0",
            "semantic_version": "1.0.0",
            "mutation_class": "singleton-admission" if operation_id == COMMIT_OPERATION_ID else (
                "candidate-receipt" if effect_class == "mutation" else "none"
            ),
            "admission_policy": "pass198-spec-pass190-lease-vm81-singleton",
            "determinism_class": "exact-deterministic",
            "VM81_binding": f"VM81:P199:{operation_id}",
            "implementation_status": "EXECUTABLE_VERIFIED",
        }
    )
    identity = dict(record)
    identity.pop("Hash216_identity", None)
    record["Hash216_identity"] = pass190_hash216("pass190.operation", identity)
    return record


def pass199_operation_records() -> tuple[dict[str, Any], ...]:
    rational = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "numerator": {"type": "integer"},
            "denominator": {"type": "integer"},
        },
        "required": ["numerator", "denominator"],
    }
    exact_ns = {"type": "integer", "minimum": 0, "maximum": 9_223_372_036_854_775_807}
    string = {"type": "string", "maxLength": 256}
    return (
        _pass199_operation(
            BRANCH_OPERATION_ID,
            "Evaluate immutable calibration branch",
            "CalibrationEvaluateBranch",
            PASS199_CAPABILITY,
            "pure",
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "run_id": string,
                    "operation_id": string,
                    "operation_spec_hash72": string,
                    "tree_hash72": string,
                    "ordinal": {"type": "integer", "minimum": 0, "maximum": 49_999},
                    "branch": {"type": "string", "maxLength": 1},
                    "x": rational,
                    "y": rational,
                    "xy_symbol": {"type": "integer", "minimum": -16, "maximum": 16},
                },
                "required": [
                    "run_id", "operation_id", "operation_spec_hash72", "tree_hash72",
                    "ordinal", "branch", "x", "y", "xy_symbol",
                ],
            },
            "calibration-evaluate-branch",
        ),
        _pass199_operation(
            COMPLETE_OPERATION_ID,
            "Commit immutable worker candidate receipt",
            "CalibrationCompleteClaimed",
            "worker:execute",
            "mutation",
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "job_id": string,
                    "worker_id": string,
                    "claim_token_hash72": {"type": "string", "maxLength": 72},
                    "candidate_result": {"type": "object"},
                    "now_ns": exact_ns,
                },
                "required": ["job_id", "worker_id", "claim_token_hash72", "candidate_result", "now_ns"],
            },
            "calibration-complete-claimed",
        ),
        _pass199_operation(
            COMMIT_OPERATION_ID,
            "Admit one completed calibration tree",
            "CalibrationCommitTree",
            PASS199_ADMISSION_CAPABILITY,
            "mutation",
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "run_id": string,
                    "workspace_id": string,
                    "operation_id": string,
                    "operation_spec_hash72": string,
                    "tree_hash72": string,
                    "expected_state_count": {"type": "integer", "minimum": 1, "maximum": 50_000},
                    "vm81_receipt_hash72": {"type": "string", "maxLength": 72},
                    "now_ns": exact_ns,
                },
                "required": [
                    "run_id", "workspace_id", "operation_id", "operation_spec_hash72",
                    "tree_hash72", "expected_state_count", "vm81_receipt_hash72", "now_ns",
                ],
            },
            "calibration-commit-tree",
        ),
    )


PASS199_OPERATION_RECORDS = pass199_operation_records()


class Pass199OperationRegistry(Iteration7OperationRegistry):
    def __init__(self, registry_path: Path = DEFAULT_REGISTRY):
        parent = Iteration7OperationRegistry(registry_path)
        combined = [copy.deepcopy(dict(record.raw)) for record in parent.records]
        combined.extend(copy.deepcopy(record) for record in PASS199_OPERATION_RECORDS)
        identity = {
            "schema": REGISTRY_SCHEMA,
            "contract": CONTRACT,
            "parent_contract": parent.payload.get("contract"),
            "parent_registry_hash216": parent.payload.get("registry_hash216"),
            "pass": 199,
            "operations": combined,
        }
        self.payload = {
            **identity,
            "registry_hash216": pass190_hash216("pass199.operation.registry", identity),
            "native_operation_count": int(parent.payload["native_operation_count"]),
            "governed_operation_count": len(combined),
            "execution_operation_count": int(parent.payload["execution_operation_count"]),
            "distributed_calibration_operation_count": len(PASS199_OPERATION_RECORDS),
        }
        self.records = tuple(OperationRecord(record) for record in combined)
        self.by_id = {}
        self.by_constructor = {}
        self.by_python = {}
        self.by_shell = {}
        self._validate_and_index()
        if tuple(record.operation_id for record in self.records[-3:]) != PASS199_OPERATION_IDS:
            raise RegistryValidationError("Pass 199 operation order mismatch")


def _candidate_body(arguments: Mapping[str, Any], branch: str) -> dict[str, Any]:
    x = exact_fraction(arguments["x"], field="candidate.x")
    y = exact_fraction(arguments["y"], field="candidate.y")
    exponent = arguments["xy_symbol"]
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise ValueError("xy_symbol must be an exact integer")
    if branch not in {"A", "B"}:
        raise ValueError("branch must be A or B")
    coordinate = {
        "ordinal": int(arguments["ordinal"]),
        "x": fraction_payload(x),
        "y": fraction_payload(y),
        "xy_symbol": exponent,
        "x_times_y": fraction_payload(x * y),
    }
    if not x or not y:
        equivalence = {
            **coordinate,
            "status": "DOMAIN_REJECTED",
            "address_count": 0,
            "cell_value_hashes": [],
            "address_witness_root_hash72": pass190_hash72(
                "pass199.address.witness.rejected", coordinate
            ),
        }
        return {
            "schema": CANDIDATE_SCHEMA,
            "run_id": arguments["run_id"],
            "operation_id": arguments["operation_id"],
            "operation_spec_hash72": arguments["operation_spec_hash72"],
            "tree_hash72": arguments["tree_hash72"],
            "branch": branch,
            **coordinate,
            "status": "DOMAIN_REJECTED",
            "address_count": 0,
            "singular_count": 0,
            "distinct_gate_values": 0,
            "cell_value_hashes": [],
            "cell_root_hash72": pass190_hash72("pass199.cells.rejected", coordinate),
            "address_witness_root_hash72": equivalence["address_witness_root_hash72"],
            "equivalence_root_hash72": pass190_hash72("pass199.branch.equivalence", equivalence),
        }

    q = matrix_power(M, -exponent)
    cell_hashes: list[str] = []
    singular_count = 0
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    cell = cell_index(i, j, k, l)
                    try:
                        gate = original_gate(x, y, q, i, j, k, l) if branch == "A" else compact_gate(x, y, q, i, j, k, l)
                        value = {"cell": cell, "indices": [i, j, k, l], "gate": gate.payload()}
                        cell_hashes.append(pass190_hash72("pass199.cell.value", value))
                    except ZeroDivisionError:
                        singular_count += LANE_COUNT
                        cell_hashes.append(pass190_hash72("pass199.cell.singular", {"cell": cell, "indices": [i, j, k, l]}))
    address_witness = [
        {"address": cell * LANE_COUNT + lane, "cell": cell, "lane": lane, "cell_value_hash72": cell_hashes[cell]}
        for cell in range(CELL_COUNT)
        for lane in range(LANE_COUNT)
    ]
    status = "SINGULAR" if singular_count else "ADMITTED"
    cell_root = pass190_hash72("pass199.branch.cells", cell_hashes)
    address_root = pass190_hash72("pass199.address.witness", address_witness)
    equivalence = {
        **coordinate,
        "status": status,
        "address_count": ADDRESS_COUNT,
        "cell_value_hashes": cell_hashes,
        "address_witness_root_hash72": address_root,
    }
    return {
        "schema": CANDIDATE_SCHEMA,
        "run_id": arguments["run_id"],
        "operation_id": arguments["operation_id"],
        "operation_spec_hash72": arguments["operation_spec_hash72"],
        "tree_hash72": arguments["tree_hash72"],
        "branch": branch,
        **coordinate,
        "status": status,
        "address_count": ADDRESS_COUNT,
        "singular_count": singular_count,
        "distinct_gate_values": len(set(cell_hashes)),
        "cell_value_hashes": cell_hashes,
        "cell_root_hash72": cell_root,
        "address_witness_root_hash72": address_root,
        "equivalence_root_hash72": pass190_hash72("pass199.branch.equivalence", equivalence),
    }


def evaluate_branch_candidate(arguments: Mapping[str, Any]) -> dict[str, Any]:
    if arguments.get("operation_id") != "pass197.reciprocal_matrix_gate":
        raise Pass199CalibrationError("no Pass 199 branch adapter for operation")
    body = _candidate_body(arguments, str(arguments.get("branch")))
    return {**body, "candidate_hash72": pass190_hash72("pass199.branch.candidate", body)}


_RESOURCE_IMPLEMENTATIONS = {
    "workspace.create": "_op_workspace_create",
    "workspace.get": "_op_workspace_get",
    "workspace.list": "_op_workspace_list",
    "workspace.update": "_op_workspace_update",
    "workspace.archive": "_op_workspace_archive",
    "artifact.register": "_op_artifact_register",
    "artifact.get": "_op_artifact_get",
    "artifact.list": "_op_artifact_list",
    "provider.register": "_op_provider_register",
    "provider.get": "_op_provider_get",
    "provider.list": "_op_provider_list",
    "provider.set_enabled": "_op_provider_set_enabled",
    "capability.define": "_op_capability_define",
    "capability.get": "_op_capability_get",
    "capability.list": "_op_capability_list",
    "job.submit": "_op_job_submit",
    "job.get": "_op_job_get",
    "job.list": "_op_job_list",
    "job.claim": "_op_job_claim",
    "job.complete": "_op_job_complete",
    "job.fail": "_op_job_fail",
}
_EXECUTION_IMPLEMENTATIONS = {
    "worker.register": "_op_worker_register",
    "worker.get": "_op_worker_get",
    "worker.list": "_op_worker_list",
    "worker.heartbeat": "_op_worker_heartbeat",
    "worker.set_enabled": "_op_worker_set_enabled",
    "job.submit_execution": "_op_job_submit_execution",
    "job.cancel": "_op_job_cancel",
    "job.retry": "_op_job_retry",
    "job.claim_next": "_op_job_claim_next",
    "job.execute_claimed": "_op_job_execute_claimed",
    "scheduler.tick": "_op_scheduler_tick",
}


class Pass199DurableCalibrationContext(DurableExecutionContext):
    """Pass 190 durable authority with Pass 199 out-of-lock candidate computation."""

    def __init__(
        self,
        database_path: Path | str = DEFAULT_DATABASE,
        registry_path: Path = DEFAULT_REGISTRY,
        *,
        holder_id: str | None = None,
        lease_ttl_ns: int = DEFAULT_LEASE_TTL_NS,
        lease_wait_ns: int = DEFAULT_LEASE_WAIT_NS,
        clock_ns: Any = time.time_ns,
        sleeper: Any = time.sleep,
    ) -> None:
        self.holder_id = holder_id or f"pass199:{os.getpid()}:{uuid.uuid4().hex}"
        self.lease_ttl_ns = lease_ttl_ns
        self.lease_wait_ns = lease_wait_ns
        self.store = ResourceRegistryStore(database_path, clock_ns=clock_ns, sleeper=sleeper)
        HHSAuthorityContext.__init__(self, registry_path)
        self.registry = Pass199OperationRegistry(registry_path)
        self._implementations.update({name: getattr(self, method) for name, method in _RESOURCE_IMPLEMENTATIONS.items()})
        self._implementations.update({name: getattr(self, method) for name, method in _EXECUTION_IMPLEMENTATIONS.items()})
        self._implementations.update(
            {
                BRANCH_OPERATION_ID: self._op_calibration_evaluate_branch,
                COMPLETE_OPERATION_ID: self._op_calibration_complete_claimed,
                COMMIT_OPERATION_ID: self._op_calibration_commit_tree,
            }
        )
        if set(self._implementations) != set(self.registry.by_id):
            missing = set(self.registry.by_id) - set(self._implementations)
            extra = set(self._implementations) - set(self.registry.by_id)
            raise RegistryValidationError(f"Pass 199 registry mismatch missing={sorted(missing)} extra={sorted(extra)}")
        self.store.restore_into(self)

    def _op_status(self, _args: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "ok",
            "classification": CLASSIFICATION,
            "contract": CONTRACT,
            "operations": len(self.registry.records),
            "state_root": self._state_root,
            "receipt_index": self._receipt_index,
        }

    def integrity_report(self) -> dict[str, Any]:
        report = super().integrity_report()
        commits = self._state.get("pass199_tree_commits", {})
        return {
            **report,
            "classification": CLASSIFICATION,
            "contract": CONTRACT,
            "pass199_registry_hash216": self.registry.payload["registry_hash216"],
            "distributed_calibration_operation_count": len(PASS199_OPERATION_IDS),
            "tree_commit_count": len(commits) if isinstance(commits, dict) else 0,
            "candidate_workers_are_authority": False,
            "singleton_tree_commit_required": True,
        }

    def _op_calibration_evaluate_branch(self, args: dict[str, Any]) -> dict[str, Any]:
        return evaluate_branch_candidate(args)

    def _op_job_execute_claimed(self, args: dict[str, Any]) -> dict[str, Any]:
        job = self._lookup("jobs", self._identifier(args["job_id"], "job_id"))
        if job.get("operation_id") == BRANCH_OPERATION_ID:
            raise StateConflictError("calibration candidates must compute outside authority and use calibration.complete_claimed")
        return super()._op_job_execute_claimed(args)

    def _validate_candidate_binding(self, job: Mapping[str, Any], candidate: Mapping[str, Any]) -> None:
        supplied_hash = candidate.get("candidate_hash72")
        body = {key: copy.deepcopy(value) for key, value in candidate.items() if key != "candidate_hash72"}
        if supplied_hash != pass190_hash72("pass199.branch.candidate", body):
            raise StateConflictError("candidate Hash72 mismatch")
        arguments = job["arguments"]
        for field in (
            "run_id", "operation_id", "operation_spec_hash72", "tree_hash72",
            "ordinal", "branch", "x", "y", "xy_symbol",
        ):
            if candidate.get(field) != arguments.get(field):
                raise StateConflictError(f"candidate does not bind job field: {field}")
        if candidate.get("schema") != CANDIDATE_SCHEMA:
            raise StateConflictError("candidate schema mismatch")
        if candidate.get("status") not in {"ADMITTED", "DOMAIN_REJECTED", "SINGULAR"}:
            raise StateConflictError("candidate status is invalid")
        if candidate.get("address_count") not in {0, ADDRESS_COUNT}:
            raise StateConflictError("candidate address count is invalid")
        hashes = candidate.get("cell_value_hashes")
        if not isinstance(hashes, list) or len(hashes) not in {0, CELL_COUNT}:
            raise StateConflictError("candidate cell witness count is invalid")

    def _op_calibration_complete_claimed(self, args: dict[str, Any]) -> dict[str, Any]:
        job_id = self._identifier(args["job_id"], "job_id")
        worker_id = self._identifier(args["worker_id"], "worker_id")
        job = self._lookup("jobs", job_id)
        worker = self._worker_lookup(worker_id)
        token = args["claim_token_hash72"]
        now_ns = args["now_ns"]
        if job.get("operation_id") != BRANCH_OPERATION_ID or job.get("status") != "running":
            raise StateConflictError("job is not a running calibration branch")
        if job.get("worker_id") != worker_id or job.get("claim_token_hash72") != token:
            raise StateConflictError("job claim token mismatch")
        if worker.get("current_job_id") != job_id or worker.get("current_claim_token_hash72") != token:
            raise StateConflictError("worker claim token mismatch")
        if now_ns >= int(job["lease_expires_ns"]):
            raise StateConflictError("candidate completion lease expired")
        if not worker["enabled"] or now_ns > int(worker["last_heartbeat_ns"]) + int(worker["lease_timeout_ns"]):
            raise StateConflictError("worker authority expired")
        candidate = copy.deepcopy(args["candidate_result"])
        self._validate_candidate_binding(job, candidate)
        execution = {
            "job_id": job_id,
            "worker_id": worker_id,
            "attempt": job["attempt"],
            "execution_request_hash72": job["execution_request_hash72"],
            "candidate_hash72": candidate["candidate_hash72"],
            "finished_at_ns": now_ns,
        }
        execution_hash = pass190_hash72("pass199.candidate.execution", execution)
        job_payload = self._updated_payload(
            job,
            {
                "status": "completed",
                "result": candidate,
                "error": None,
                "execution_hash72": execution_hash,
                "worker_id": None,
                "claim_token_hash72": None,
                "lease_expires_ns": None,
                "finished_at_ns": now_ns,
            },
        )
        worker_payload = self._updated_payload(
            worker,
            {
                "current_job_id": None,
                "current_claim_token_hash72": None,
                "last_heartbeat_ns": max(int(worker["last_heartbeat_ns"]), now_ns),
                "completed_job_count": int(worker["completed_job_count"]) + 1,
            },
        )
        committed_jobs, _workers = self._commit_execution_records(
            job_payloads={job_id: job_payload}, worker_payloads={worker_id: worker_payload}
        )
        return {
            "executed": True,
            "job": committed_jobs[job_id],
            "candidate_hash72": candidate["candidate_hash72"],
            "execution_hash72": execution_hash,
            "worker_is_canonical_authority": False,
            "state_root": self._state_root,
        }

    @staticmethod
    def _state_from_pair(ordinal: int, left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
        coordinate_fields = ("x", "y", "xy_symbol", "x_times_y")
        coordinate_match = all(left.get(field) == right.get(field) for field in coordinate_fields)
        same_status = left.get("status") == right.get("status")
        same_equivalence = left.get("equivalence_root_hash72") == right.get("equivalence_root_hash72")
        same_cells = left.get("cell_root_hash72") == right.get("cell_root_hash72")
        same_addresses = left.get("address_witness_root_hash72") == right.get("address_witness_root_hash72")
        branch_match = coordinate_match and same_status and same_equivalence and same_cells and same_addresses
        if left.get("status") == "DOMAIN_REJECTED" and branch_match:
            status = "DOMAIN_REJECTED"
        elif left.get("status") == "SINGULAR" or right.get("status") == "SINGULAR":
            status = "SINGULAR"
        else:
            status = "ADMITTED" if branch_match else "MISMATCH"
        address_count = ADDRESS_COUNT if status in {"ADMITTED", "MISMATCH", "SINGULAR"} else 0
        body = {
            "ordinal": ordinal,
            "x": left.get("x"),
            "y": left.get("y"),
            "xy_symbol": left.get("xy_symbol"),
            "x_times_y": left.get("x_times_y"),
            "status": status,
            "branch_match": branch_match,
            "address_count": address_count,
            "exact_match_count": address_count if status == "ADMITTED" else 0,
            "mismatch_count": address_count if status == "MISMATCH" else 0,
            "singular_count": max(int(left.get("singular_count", 0)), int(right.get("singular_count", 0))),
            "distinct_gate_values": max(int(left.get("distinct_gate_values", 0)), int(right.get("distinct_gate_values", 0))),
            "useful_parameter_state": status == "ADMITTED" and int(left.get("distinct_gate_values", 0)) > 1,
            "cell_gate_hash72": hhs_hash72(
                "pass199.admitted.cell.root",
                {"left": left.get("cell_root_hash72"), "right": right.get("cell_root_hash72")},
            ) if status == "ADMITTED" else None,
            "address_witness_root_hash72": left.get("address_witness_root_hash72") if branch_match else None,
            "branch_a_candidate_hash72": left.get("candidate_hash72"),
            "branch_b_candidate_hash72": right.get("candidate_hash72"),
        }
        return {**body, "state_hash72": hhs_hash72("pass199.parameter.state", body)}

    def _op_calibration_commit_tree(self, args: dict[str, Any]) -> dict[str, Any]:
        commits = self._state.get("pass199_tree_commits", {})
        if not isinstance(commits, dict):
            raise StateConflictError("Pass 199 commit registry is invalid")
        existing = commits.get(args["run_id"])
        if existing is not None:
            if existing.get("tree_hash72") != args["tree_hash72"]:
                raise StateConflictError("run identity already committed to another tree")
            return copy.deepcopy(existing)
        jobs = [
            job
            for job in self._resource_registries()["jobs"].values()
            if job.get("workspace_id") == args["workspace_id"]
            and job.get("metadata", {}).get("pass199_run_id") == args["run_id"]
        ]
        expected_jobs = int(args["expected_state_count"]) * 2
        if len(jobs) != expected_jobs:
            raise StateConflictError(f"tree job count mismatch expected={expected_jobs} actual={len(jobs)}")
        if any(job.get("status") != "completed" for job in jobs):
            incomplete = sorted(job["job_id"] for job in jobs if job.get("status") != "completed")
            raise StateConflictError(f"tree contains incomplete jobs: {incomplete[:8]}")
        pairs: dict[int, dict[str, Mapping[str, Any]]] = {}
        for job in jobs:
            candidate = job.get("result")
            if not isinstance(candidate, dict):
                raise StateConflictError("completed calibration job lacks candidate result")
            self._validate_candidate_binding(job, candidate)
            ordinal = int(candidate["ordinal"])
            branch = str(candidate["branch"])
            bucket = pairs.setdefault(ordinal, {})
            if branch in bucket:
                raise StateConflictError("duplicate branch candidate for ordinal")
            bucket[branch] = candidate
        expected_ordinals = list(range(int(args["expected_state_count"])))
        if sorted(pairs) != expected_ordinals or any(set(pairs[ordinal]) != {"A", "B"} for ordinal in expected_ordinals):
            raise StateConflictError("tree ordinal or branch coverage is incomplete")
        states = [self._state_from_pair(ordinal, pairs[ordinal]["A"], pairs[ordinal]["B"]) for ordinal in expected_ordinals]
        admitted = [item for item in states if item["status"] == "ADMITTED"]
        rejected = [item for item in states if item["status"] == "DOMAIN_REJECTED"]
        mismatches = [item for item in states if item["status"] == "MISMATCH"]
        singular = [item for item in states if item["status"] == "SINGULAR"]
        ordered_root = hhs_hash72(
            "pass199.ordered.tree.state.root",
            [{"ordinal": item["ordinal"], "state_hash72": item["state_hash72"]} for item in states],
        )
        closed = not mismatches and not singular and len(states) == int(args["expected_state_count"])
        summary = {
            "evaluated_parameter_states": len(states),
            "admitted_parameter_states": len(admitted),
            "domain_rejected_parameter_states": len(rejected),
            "mismatch_parameter_states": len(mismatches),
            "singular_parameter_states": len(singular),
            "address_comparisons": sum(item["address_count"] for item in states),
            "useful_parameter_states": sum(bool(item["useful_parameter_state"]) for item in states),
            "branch_job_count": len(jobs),
            "canonical_ordinal_serialization": True,
        }
        body = {
            "schema": COMMIT_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "run_id": args["run_id"],
            "workspace_id": args["workspace_id"],
            "operation_id": args["operation_id"],
            "operation_spec_hash72": args["operation_spec_hash72"],
            "tree_hash72": args["tree_hash72"],
            "vm81_receipt_hash72": args["vm81_receipt_hash72"],
            "expected_state_count": args["expected_state_count"],
            "ordered_state_root_hash72": ordered_root,
            "summary": summary,
            "states": states,
            "closed": closed,
            "committed_at_ns": args["now_ns"],
            "candidate_workers_are_authority": False,
            "canonical_mutation_authority": "SINGLETON_VM81_PASS190_ADMISSION",
        }
        record = {**body, "commit_hash72": pass190_hash72("pass199.singleton.tree.commit", body)}
        state = copy.deepcopy(self._state)
        state.setdefault("pass199_tree_commits", {})[args["run_id"]] = copy.deepcopy(record)
        self._state = state
        self._state_root = pass190_hash72("pass190.state", self._state)
        self._validate_resource_state()
        return record

    def tree_commit(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            self.store.restore_into(self)
            commits = self._state.get("pass199_tree_commits", {})
            value = commits.get(run_id) if isinstance(commits, dict) else None
            return copy.deepcopy(value) if isinstance(value, dict) else None

    def find_tree_commit_receipt(self, run_id: str) -> dict[str, Any] | None:
        for receipt in reversed(self.receipts_after(0, 100_000)):
            if receipt.get("operation_id") == COMMIT_OPERATION_ID and receipt.get("arguments", {}).get("run_id") == run_id:
                self._verify_receipt_identity(receipt)
                return copy.deepcopy(receipt)
        return None


class Pass199DistributedCalibrationFabric:
    def __init__(self, *, state_root: str | os.PathLike[str] | None = None) -> None:
        self.state_root = Path(state_root or os.getenv("HHS_PASS199_STATE_ROOT") or ".hhs/pass199").resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "pass199_durable_authority.sqlite3"
        self.report_path = self.state_root / "distributed_calibration_report.json"
        self.pass198 = Pass198OperationCalibrationRegistry(state_root=self.state_root / "pass198_registry")
        self.context = Pass199DurableCalibrationContext(self.database_path, holder_id="pass199-orchestrator")
        self._last_report: dict[str, Any] | None = None

    def close(self) -> None:
        self.context.close()
        self.pass198.close()

    @staticmethod
    def _write(path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            handle.write(hhs_canonical_json(payload) + "\n")
            temporary = Path(handle.name)
        temporary.replace(path)

    @staticmethod
    def _invoke(context: Pass199DurableCalibrationContext, operation_id: str, arguments: Mapping[str, Any], *caps: str) -> InvocationResult:
        return context.invoke(operation_id, arguments, capabilities=caps)

    def _ensure_capability(self, scope: str) -> None:
        try:
            self._invoke(
                self.context,
                "capability.define",
                {"scope": scope, "description": f"Pass 199 governed capability {scope}", "risk_class": "bounded"},
                "capability:admin",
            )
        except StateConflictError:
            pass

    def _ensure_workspace(self, workspace_id: str) -> None:
        try:
            self._invoke(
                self.context,
                "workspace.create",
                {"workspace_id": workspace_id, "name": f"Pass 199 {workspace_id}", "metadata": {"contract": CONTRACT}},
                "workspace:write",
            )
        except StateConflictError:
            pass

    def _ensure_worker(self, worker_id: str, now_ns: int) -> None:
        try:
            self._invoke(
                self.context,
                "worker.register",
                {
                    "worker_id": worker_id,
                    "capabilities": [PASS199_CAPABILITY],
                    "labels": ["pass199", "immutable-candidate"],
                    "lease_timeout_ns": 300_000_000_000,
                    "now_ns": now_ns,
                },
                "worker:admin",
            )
        except StateConflictError:
            worker = self._invoke(self.context, "worker.get", {"worker_id": worker_id}, "worker:read").result
            if not worker["enabled"]:
                self._invoke(self.context, "worker.set_enabled", {"worker_id": worker_id, "enabled": True}, "worker:admin")

    def prepare_tree(self, operation_id: str, config_payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        operation = self.pass198.get_operation(operation_id)
        tree = self.pass198.parameter_tree(operation_id, config_payload)
        run_id = pass190_hash72(
            "pass199.distributed.run",
            {"version": VERSION, "operation_id": operation_id, "spec_hash72": operation["spec_hash72"], "tree_hash72": tree["tree_hash72"]},
        )
        workspace_id = f"calibration.{run_id[:32]}"
        self._ensure_capability(PASS199_CAPABILITY)
        self._ensure_capability(PASS199_ADMISSION_CAPABILITY)
        self._ensure_workspace(workspace_id)
        existing_jobs = {
            item["job_id"]
            for item in self._invoke(self.context, "job.list", {"workspace_id": workspace_id}, "job:read").result
        }
        submitted_at = time.time_ns()
        submitted = 0
        for state in tree["states"]:
            for branch in ("A", "B"):
                job_id = f"p199.{run_id[:20]}.{int(state['ordinal']):05d}.{branch.lower()}"
                if job_id in existing_jobs:
                    continue
                arguments = {
                    "run_id": run_id,
                    "operation_id": operation_id,
                    "operation_spec_hash72": operation["spec_hash72"],
                    "tree_hash72": tree["tree_hash72"],
                    "ordinal": int(state["ordinal"]),
                    "branch": branch,
                    "x": state["x"],
                    "y": state["y"],
                    "xy_symbol": int(state["xy_symbol"]),
                }
                self._invoke(
                    self.context,
                    "job.submit_execution",
                    {
                        "job_id": job_id,
                        "workspace_id": workspace_id,
                        "operation_id": BRANCH_OPERATION_ID,
                        "arguments": arguments,
                        "required_capabilities": [PASS199_CAPABILITY],
                        "submitted_at_ns": submitted_at,
                        "max_attempts": 3,
                        "retry_backoff_ns": 0,
                        "priority": -int(state["ordinal"]),
                        "metadata": {
                            "pass199_run_id": run_id,
                            "ordinal": int(state["ordinal"]),
                            "branch": branch,
                            "tree_hash72": tree["tree_hash72"],
                        },
                    },
                    "job:write",
                )
                submitted += 1
        return {
            "schema": "HHS_PASS_199_PREPARED_TREE_V1",
            "run_id": run_id,
            "workspace_id": workspace_id,
            "operation": operation,
            "tree": tree,
            "expected_job_count": int(tree["state_count"]) * 2,
            "submitted_job_count": submitted,
        }

    def execute_workers(self, prepared: Mapping[str, Any], *, worker_count: int = 4) -> dict[str, Any]:
        if not 1 <= worker_count <= 64:
            raise ValueError("worker_count must be in [1,64]")
        worker_ids = [f"p199.worker.{index:02d}" for index in range(worker_count)]
        now = time.time_ns()
        for worker_id in worker_ids:
            self._ensure_worker(worker_id, now)
        active = 0
        peak = 0
        active_lock = threading.Lock()
        completed: list[str] = []

        def worker_loop(worker_id: str) -> int:
            nonlocal active, peak
            local_count = 0
            while True:
                heartbeat_at = time.time_ns()
                self._invoke(
                    self.context,
                    "worker.heartbeat",
                    {"worker_id": worker_id, "now_ns": heartbeat_at},
                    "worker:execute",
                )
                claim = self._invoke(
                    self.context,
                    "job.claim_next",
                    {"worker_id": worker_id, "workspace_id": prepared["workspace_id"], "now_ns": heartbeat_at, "lease_duration_ns": 300_000_000_000},
                    "worker:execute",
                ).result
                if not claim["claimed"]:
                    return local_count
                job = claim["job"]
                with active_lock:
                    active += 1
                    peak = max(peak, active)
                try:
                    candidate = evaluate_branch_candidate(job["arguments"])
                finally:
                    with active_lock:
                        active -= 1
                finished_at = max(time.time_ns(), heartbeat_at + 1)
                self._invoke(
                    self.context,
                    COMPLETE_OPERATION_ID,
                    {
                        "job_id": job["job_id"],
                        "worker_id": worker_id,
                        "claim_token_hash72": claim["claim_token_hash72"],
                        "candidate_result": candidate,
                        "now_ns": finished_at,
                    },
                    "worker:execute",
                )
                with active_lock:
                    completed.append(job["job_id"])
                local_count += 1

        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            counts = list(pool.map(worker_loop, worker_ids))
        return {
            "worker_count": worker_count,
            "completed_job_count": sum(counts),
            "completed_job_ids": sorted(completed),
            "peak_parallel_candidate_workers": peak,
            "candidate_computation_outside_authority_lock": True,
        }

    def cancel_and_retry(self, job_id: str) -> dict[str, Any]:
        now = time.time_ns()
        cancelled = self._invoke(
            self.context,
            "job.cancel",
            {"job_id": job_id, "reason": {"pass199_test": "cancel-and-retry"}, "now_ns": now},
            "job:write",
        ).result
        retried = self._invoke(
            self.context,
            "job.retry",
            {"job_id": job_id, "now_ns": now + 1, "not_before_ns": now + 1},
            "job:write",
        ).result
        return {"cancelled": cancelled, "retried": retried}

    def recover_stale_claim(self, job_id: str, worker_id: str = "p199.stale.worker") -> dict[str, Any]:
        now = time.time_ns()
        self._ensure_worker(worker_id, now)
        claim = self._invoke(
            self.context,
            "job.claim_next",
            {"worker_id": worker_id, "now_ns": now, "lease_duration_ns": 1, "workspace_id": self._invoke(self.context, "job.get", {"job_id": job_id}, "job:read").result["workspace_id"]},
            "worker:execute",
        ).result
        if not claim["claimed"] or claim["job"]["job_id"] != job_id:
            raise Pass199CalibrationError("requested stale-recovery job was not claimed")
        tick = self._invoke(
            self.context,
            "scheduler.tick",
            {"now_ns": now + 1, "limit": 1000},
            "scheduler:write",
        ).result
        recovered = self._invoke(self.context, "job.get", {"job_id": job_id}, "job:read").result
        return {"claim": claim, "scheduler": tick, "recovered": recovered}

    @staticmethod
    def _assemble_replay(candidates: Sequence[Mapping[str, Any]], state_count: int) -> dict[str, Any]:
        pairs: dict[int, dict[str, Mapping[str, Any]]] = {}
        for candidate in candidates:
            pairs.setdefault(int(candidate["ordinal"]), {})[str(candidate["branch"])] = candidate
        states = [
            Pass199DurableCalibrationContext._state_from_pair(ordinal, pairs[ordinal]["A"], pairs[ordinal]["B"])
            for ordinal in range(state_count)
        ]
        root = hhs_hash72(
            "pass199.ordered.tree.state.root",
            [{"ordinal": item["ordinal"], "state_hash72": item["state_hash72"]} for item in states],
        )
        return {"states": states, "ordered_state_root_hash72": root}

    def _full_replay(self, prepared: Mapping[str, Any], expected_root: str, worker_count: int) -> dict[str, Any]:
        arguments = []
        operation = prepared["operation"]
        for state in prepared["tree"]["states"]:
            for branch in ("A", "B"):
                arguments.append(
                    {
                        "run_id": prepared["run_id"],
                        "operation_id": operation["operation_id"],
                        "operation_spec_hash72": operation["spec_hash72"],
                        "tree_hash72": prepared["tree"]["tree_hash72"],
                        "ordinal": int(state["ordinal"]),
                        "branch": branch,
                        "x": state["x"],
                        "y": state["y"],
                        "xy_symbol": int(state["xy_symbol"]),
                    }
                )
        with ThreadPoolExecutor(max_workers=max(1, worker_count)) as pool:
            candidates = list(pool.map(evaluate_branch_candidate, arguments))
        replay = self._assemble_replay(candidates, int(prepared["tree"]["state_count"]))
        return {
            "full_replay_executed": True,
            "replayed_branch_jobs": len(candidates),
            "replayed_parameter_states": int(prepared["tree"]["state_count"]),
            "replay_root_hash72": replay["ordered_state_root_hash72"],
            "deterministic": replay["ordered_state_root_hash72"] == expected_root,
            "first_replay_mismatch": None if replay["ordered_state_root_hash72"] == expected_root else {
                "expected": expected_root,
                "actual": replay["ordered_state_root_hash72"],
            },
        }

    def _record_pass198_run(self, prepared: Mapping[str, Any], report: Mapping[str, Any]) -> dict[str, Any]:
        operation = prepared["operation"]
        run_id = hhs_hash72(
            "pass198.operation.run.distributed",
            {
                "operation_id": operation["operation_id"],
                "tree_hash72": prepared["tree"]["tree_hash72"],
                "report_hash72": report["report_hash72"],
                "vm81_receipt_hash72": report["authority"]["vm81_receipt_hash72"],
                "execution_mode": "PASS199_DURABLE_DISTRIBUTED",
            },
        )
        body = {
            "schema": "HHS_PASS_198_OPERATION_CALIBRATION_RUN_V1",
            "version": VERSION,
            "run_id": run_id,
            "operation_id": operation["operation_id"],
            "operation_spec_hash72": operation["spec_hash72"],
            "tree_hash72": prepared["tree"]["tree_hash72"],
            "config_hash72": hhs_hash72("pass199.config", prepared["tree"]["config"]),
            "report_hash72": report["report_hash72"],
            "state_root_hash72": report["state_root_hash72"],
            "vm81_receipt_hash72": report["authority"]["vm81_receipt_hash72"],
            "status": "CLOSED" if report["closed"] else "REJECTED",
            "summary": report["summary"],
            "replay": report["replay"],
            "execution_mode": "PASS199_DURABLE_DISTRIBUTED",
            "worker_fabric_hash72": report["worker_fabric_hash72"],
            "created_ns": time.time_ns(),
        }
        registry = self.pass198
        with registry._lock:  # Bound integration into the existing atomic Pass 198 event transaction.
            row = registry._db.execute("SELECT payload_json FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if row:
                return json.loads(row["payload_json"])
            try:
                registry._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = registry._event(
                    registry._db,
                    "DISTRIBUTED_CALIBRATION_RUN_RECORDED",
                    {"run_id": run_id, "operation_id": operation["operation_id"], "status": body["status"], "report_hash72": body["report_hash72"]},
                )
                document = {**body, "event_hash72": event_hash}
                registry._db.execute(
                    "INSERT INTO runs(run_id,operation_id,config_hash72,report_hash72,state_root_hash72,status,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?)",
                    (run_id, body["operation_id"], body["config_hash72"], body["report_hash72"], body["state_root_hash72"], body["status"], hhs_canonical_json(document), event_id),
                )
                if report["closed"]:
                    registry._record_simplifications(operation, document, report)
                registry._db.commit()
                return document
            except Exception:
                registry._db.rollback()
                raise

    def run(
        self,
        operation_id: str = "pass197.reciprocal_matrix_gate",
        config_payload: Mapping[str, Any] | None = None,
        *,
        worker_count: int = 4,
        vm81_receipt_hash72: str | None = None,
        resume: bool = True,
        full_replay: bool = True,
    ) -> dict[str, Any]:
        prepared = self.prepare_tree(operation_id, config_payload)
        if resume and self.report_path.exists():
            prior = json.loads(self.report_path.read_text(encoding="utf-8"))
            expected = hhs_hash72("pass199.report", {key: value for key, value in prior.items() if key != "report_hash72"})
            if prior.get("run_id") == prepared["run_id"] and prior.get("report_hash72") == expected:
                self._last_report = prior
                return copy.deepcopy(prior)
        worker_summary = self.execute_workers(prepared, worker_count=worker_count)
        receipt_value = vm81_receipt_hash72 or ZERO_HASH72
        existing_commit = self.context.tree_commit(prepared["run_id"])
        commit_receipt = self.context.find_tree_commit_receipt(prepared["run_id"]) if existing_commit else None
        if existing_commit is None:
            invocation = self._invoke(
                self.context,
                COMMIT_OPERATION_ID,
                {
                    "run_id": prepared["run_id"],
                    "workspace_id": prepared["workspace_id"],
                    "operation_id": operation_id,
                    "operation_spec_hash72": prepared["operation"]["spec_hash72"],
                    "tree_hash72": prepared["tree"]["tree_hash72"],
                    "expected_state_count": int(prepared["tree"]["state_count"]),
                    "vm81_receipt_hash72": receipt_value,
                    "now_ns": time.time_ns(),
                },
                PASS199_ADMISSION_CAPABILITY,
            )
            commit = invocation.result
            commit_receipt = dict(invocation.receipt)
        else:
            commit = existing_commit
        if commit_receipt is None:
            raise Pass199CalibrationError("singleton tree commit receipt is unavailable")
        self.context._verify_receipt_identity(commit_receipt)
        replay = self._full_replay(prepared, commit["ordered_state_root_hash72"], worker_count) if full_replay else {
            "full_replay_executed": False,
            "replayed_branch_jobs": 0,
            "replayed_parameter_states": 0,
            "replay_root_hash72": commit["ordered_state_root_hash72"],
            "deterministic": True,
            "first_replay_mismatch": None,
        }
        admitted = int(commit["summary"]["admitted_parameter_states"])
        summary = {
            **commit["summary"],
            "original_leaf_evaluations": admitted * ADDRESS_COUNT,
            "factorized_cell_evaluations": admitted * CELL_COUNT,
            "saved_leaf_evaluations": admitted * (ADDRESS_COUNT - CELL_COUNT),
            "saved_fraction": fraction_payload(Fraction(ADDRESS_COUNT - CELL_COUNT, ADDRESS_COUNT)),
            "lossless_simplifications_admitted": bool(commit["closed"] and replay["deterministic"]),
        }
        worker_fabric = {
            **worker_summary,
            "pass190_registry_hash216": self.context.registry.payload["registry_hash216"],
            "durable_database": str(self.database_path),
            "restartable_jobs": True,
            "cancel_retry_supported": True,
            "stale_lease_recovery_supported": True,
        }
        report = {
            "schema": REPORT_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "run_id": prepared["run_id"],
            "operation_id": operation_id,
            "operation_spec_hash72": prepared["operation"]["spec_hash72"],
            "tree_hash72": prepared["tree"]["tree_hash72"],
            "state_root_hash72": commit["ordered_state_root_hash72"],
            "summary": summary,
            "parameter_states": commit["states"],
            "lossless_simplifications": [
                {"name": "ORIGINAL_TO_COMPACT_NUMERATOR", "lossless": summary["lossless_simplifications_admitted"]},
                {"name": "RECIPROCAL_DENOMINATOR_FACTORIZATION", "lossless": summary["lossless_simplifications_admitted"]},
                {"name": "VM81_LANE_BROADCAST", "lossless": summary["lossless_simplifications_admitted"]},
                {"name": "MATRIX_POWER_CACHE_BY_XY_SYMBOL", "lossless": summary["lossless_simplifications_admitted"]},
            ],
            "worker_fabric": worker_fabric,
            "worker_fabric_hash72": hhs_hash72("pass199.worker.fabric", worker_fabric),
            "singleton_commit": {
                "commit_hash72": commit["commit_hash72"],
                "receipt_hash72": commit_receipt["hash72"],
                "receipt_verified": True,
                "canonical_commit_operation_count": 1,
                "candidate_worker_is_authority": False,
            },
            "authority": {
                "canonical_admission": "SINGLETON_VM81_PASS190_ADMISSION",
                "vm81_receipt_hash72": receipt_value,
                "candidate_workers_are_authority": False,
                "api_is_authority": False,
            },
            "replay": replay,
            "closed": bool(commit["closed"] and replay["deterministic"]),
        }
        report["report_hash72"] = hhs_hash72("pass199.report", report)
        report["pass198_run"] = self._record_pass198_run(prepared, report)
        self._write(self.report_path, report)
        self._last_report = copy.deepcopy(report)
        return copy.deepcopy(report)

    def status(self) -> dict[str, Any]:
        report = self._last_report
        if report is None and self.report_path.exists():
            report = json.loads(self.report_path.read_text(encoding="utf-8"))
        body = {
            "schema": "HHS_PASS_199_STATUS_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "state_root": str(self.state_root),
            "scanned": report is not None,
            "closed": bool(report and report.get("closed")),
            "report_hash72": report.get("report_hash72") if report else None,
            "summary": report.get("summary") if report else None,
            "runtime": self.context.integrity_report(),
        }
        return {**body, "status_hash72": hhs_hash72("pass199.status", body)}

    def report(self) -> dict[str, Any]:
        if self._last_report is None:
            if not self.report_path.exists():
                raise Pass199CalibrationError("Pass 199 report unavailable")
            self._last_report = json.loads(self.report_path.read_text(encoding="utf-8"))
        expected = hhs_hash72("pass199.report", {key: value for key, value in self._last_report.items() if key not in {"report_hash72", "pass198_run"}})
        # Historical reports include pass198_run after the report identity was bound.
        if self._last_report.get("report_hash72") != expected:
            alternate = hhs_hash72("pass199.report", {key: value for key, value in self._last_report.items() if key != "report_hash72"})
            if self._last_report.get("report_hash72") != alternate:
                raise Pass199CalibrationError("Pass 199 report integrity verification failed")
        return copy.deepcopy(self._last_report)
