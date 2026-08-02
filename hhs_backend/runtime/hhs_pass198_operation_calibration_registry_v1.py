"""Pass 198 persistent operation-calibration and proof-carrying simplification registry."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1 import Pass197ABHydrationCalibration
from hhs_backend.runtime.pass197_exact_v1 import ADDRESS_COUNT, canonical_json, hash72
from hhs_backend.runtime.pass197_state_v1 import CalibrationConfig

VERSION = "HHS_PASS_198_OPERATION_CALIBRATION_REGISTRY_V1"
CONTRACT = "HHS-P198-OCR-PROOF-SIMPLIFICATION-VM81-H72"
CLASSIFICATION = "HHS_PASS_198_GENERIC_CALIBRATION_REGISTRY_FOUNDATION_VERIFIED"
REGISTRY_SCHEMA = "HHS_PASS_198_OPERATION_CALIBRATION_REGISTRY_V1"
SPEC_SCHEMA = "HHS_PASS_198_OPERATION_SPEC_V1"
TREE_SCHEMA = "HHS_PASS_198_PARAMETER_TREE_V1"
RUN_SCHEMA = "HHS_PASS_198_OPERATION_CALIBRATION_RUN_V1"
SIMPLIFICATION_SCHEMA = "HHS_PASS_198_PROOF_CARRYING_SIMPLIFICATION_V1"
EVENT_SCHEMA = "HHS_PASS_198_REGISTRY_EVENT_V1"
ZERO_HASH72 = "0" * 72
PROMOTION_ORDER = (
    "OBSERVED",
    "ENVELOPE_VERIFIED",
    "CROSS_WORKLOAD_VERIFIED",
    "COMPILER_CANDIDATE",
    "RUNTIME_ADMITTED",
    "FROZEN_CONSTRAINT",
)


class Pass198RegistryError(RuntimeError):
    pass


def _string(value: Any, field: str, maximum: int = 256) -> str:
    text = str(value or "").strip()
    if not text or len(text) > maximum:
        raise ValueError(f"{field} must be nonempty and at most {maximum} characters")
    return text


def _strings(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{field} must be an array")
    result = tuple(_string(item, field) for item in value)
    if not result or len(result) != len(set(result)):
        raise ValueError(f"{field} must contain unique values")
    return result


def _copy(value: Any) -> Any:
    return json.loads(canonical_json(value))


@dataclass(frozen=True)
class OperationSpec:
    operation_id: str
    version: int
    display_name: str
    adapter: str
    input_schema: dict[str, Any]
    parameter_axes: dict[str, list[Any]]
    domain_constraints: tuple[str, ...]
    branch_a: dict[str, Any]
    branch_b: dict[str, Any]
    invariants: tuple[str, ...]
    retained_witnesses: tuple[str, ...]
    cost_model: dict[str, Any]
    negative_mutations: tuple[str, ...]
    replay_policy: dict[str, Any]
    status: str
    spec_hash72: str

    @classmethod
    def create(cls, payload: Mapping[str, Any]) -> "OperationSpec":
        operation_id = _string(payload.get("operation_id"), "operation_id")
        version = int(payload.get("version", 1))
        if not 1 <= version <= 1_000_000:
            raise ValueError("version must be in [1,1000000]")
        display_name = _string(payload.get("display_name"), "display_name")
        adapter = _string(payload.get("adapter"), "adapter")
        input_schema = dict(payload.get("input_schema") or {})
        parameter_axes = dict(payload.get("parameter_axes") or {})
        if not parameter_axes or any(not isinstance(v, list) or not v for v in parameter_axes.values()):
            raise ValueError("parameter_axes must contain nonempty arrays")
        domain_constraints = _strings(payload.get("domain_constraints") or (), "domain_constraints")
        invariants = _strings(payload.get("invariants") or (), "invariants")
        retained_witnesses = _strings(payload.get("retained_witnesses") or (), "retained_witnesses")
        negative_mutations = _strings(payload.get("negative_mutations") or (), "negative_mutations")
        branch_a = dict(payload.get("branch_a") or {})
        branch_b = dict(payload.get("branch_b") or {})
        cost_model = dict(payload.get("cost_model") or {})
        replay_policy = dict(payload.get("replay_policy") or {})
        if not all((input_schema, branch_a, branch_b, cost_model, replay_policy)):
            raise ValueError("input_schema, branches, cost_model, and replay_policy are required")
        status = str(payload.get("status", "REGISTERED")).upper()
        if status not in {"REGISTERED", "DISABLED", "REVOKED"}:
            raise ValueError("unsupported operation status")
        identity = {
            "schema": SPEC_SCHEMA,
            "operation_id": operation_id,
            "version": version,
            "display_name": display_name,
            "adapter": adapter,
            "input_schema": input_schema,
            "parameter_axes": parameter_axes,
            "domain_constraints": list(domain_constraints),
            "branch_a": branch_a,
            "branch_b": branch_b,
            "invariants": list(invariants),
            "retained_witnesses": list(retained_witnesses),
            "cost_model": cost_model,
            "negative_mutations": list(negative_mutations),
            "replay_policy": replay_policy,
            "status": status,
        }
        return cls(
            operation_id=operation_id,
            version=version,
            display_name=display_name,
            adapter=adapter,
            input_schema=input_schema,
            parameter_axes=parameter_axes,
            domain_constraints=domain_constraints,
            branch_a=branch_a,
            branch_b=branch_b,
            invariants=invariants,
            retained_witnesses=retained_witnesses,
            cost_model=cost_model,
            negative_mutations=negative_mutations,
            replay_policy=replay_policy,
            status=status,
            spec_hash72=hash72("pass198.operation.spec", identity),
        )

    def payload(self) -> dict[str, Any]:
        return {"schema": SPEC_SCHEMA, **_copy(asdict(self))}


BUILTIN_PASS197_SPEC = OperationSpec.create(
    {
        "operation_id": "pass197.reciprocal_matrix_gate",
        "display_name": "Pass 197 reciprocal matrix gate",
        "adapter": "hhs.pass197.reciprocal_matrix_gate.v1",
        "input_schema": {"type": "object", "additionalProperties": False},
        "parameter_axes": {
            "x_values": ["-3", "-2", "-1", "-1/2", "0", "1/2", "1", "2", "3"],
            "y_values": ["-3", "-2", "-1", "-1/2", "0", "1/2", "1", "2", "3"],
            "xy_symbol_values": [-2, -1, 0, 1, 2],
        },
        "domain_constraints": [
            "x and y are exact rationals",
            "zero reciprocal states are rejected without normalization",
            "lexical xy remains distinct from x*y",
            "matrix operation order is preserved",
        ],
        "branch_a": {"name": "original reciprocal leaf gate", "implementation": "pass197_exact_v1.original_gate"},
        "branch_b": {"name": "factorized compact gate", "implementation": "pass197_exact_v1.compact_gate"},
        "invariants": [
            "all admitted VM5184 addresses compare exactly",
            "no admitted denominator is singular",
            "address round-trip is exact",
            "full replay reproduces the state root",
        ],
        "retained_witnesses": [
            "i", "j", "k", "l", "lane", "lexical xy exponent", "x*y product", "state Hash72", "branch receipt Hash72"
        ],
        "cost_model": {
            "original_leaf_evaluations_per_state": ADDRESS_COUNT,
            "factorized_cell_evaluations_per_state": 81,
            "lane_identity_retained": True,
        },
        "negative_mutations": [
            "replace xy with x*y",
            "admit floating-point ingress",
            "reverse matrix product order",
            "strip VM81 lane identity",
            "admit zero reciprocal domain",
            "tamper checkpoint receipt tip",
        ],
        "replay_policy": {
            "full_replay_required": True,
            "checkpoint_integrity_required": True,
            "mutation_counterexamples_required": True,
        },
    }
)


class Pass198OperationCalibrationRegistry:
    def __init__(self, *, state_root: str | os.PathLike[str] | None = None) -> None:
        self.state_root = Path(state_root or os.getenv("HHS_PASS198_STATE_ROOT") or ".hhs/pass198").resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "operation_calibration_registry.sqlite3"
        self._lock = threading.RLock()
        self._db = sqlite3.connect(self.database_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self._schema()
        self.register_operation(BUILTIN_PASS197_SPEC.payload(), source="builtin", idempotent=True)

    def close(self) -> None:
        self._db.close()

    def _schema(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT NOT NULL,predecessor_hash72 TEXT NOT NULL,event_hash72 TEXT NOT NULL UNIQUE,payload_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS operations(operation_id TEXT PRIMARY KEY,status TEXT NOT NULL,spec_hash72 TEXT NOT NULL UNIQUE,payload_json TEXT NOT NULL,created_event INTEGER NOT NULL REFERENCES events(seq),updated_event INTEGER NOT NULL REFERENCES events(seq));
            CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY,operation_id TEXT NOT NULL REFERENCES operations(operation_id),config_hash72 TEXT NOT NULL,report_hash72 TEXT NOT NULL,state_root_hash72 TEXT NOT NULL,status TEXT NOT NULL,payload_json TEXT NOT NULL,created_event INTEGER NOT NULL REFERENCES events(seq));
            CREATE TABLE IF NOT EXISTS simplifications(simplification_id TEXT PRIMARY KEY,operation_id TEXT NOT NULL REFERENCES operations(operation_id),name TEXT NOT NULL,status TEXT NOT NULL,proof_hash72 TEXT NOT NULL,payload_json TEXT NOT NULL,created_event INTEGER NOT NULL REFERENCES events(seq),updated_event INTEGER NOT NULL REFERENCES events(seq));
            CREATE TABLE IF NOT EXISTS simplification_runs(simplification_id TEXT NOT NULL REFERENCES simplifications(simplification_id),run_id TEXT NOT NULL REFERENCES runs(run_id),PRIMARY KEY(simplification_id,run_id));
            """
        )
        self._db.commit()

    @staticmethod
    def _event(db: sqlite3.Connection, event_type: str, payload: Mapping[str, Any]) -> tuple[int, str]:
        row = db.execute("SELECT seq,event_hash72 FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        predecessor = row["event_hash72"] if row else ZERO_HASH72
        sequence = int(row["seq"]) + 1 if row else 1
        body = {
            "schema": EVENT_SCHEMA,
            "contract": CONTRACT,
            "sequence": sequence,
            "event_type": event_type,
            "predecessor_hash72": predecessor,
            "payload": dict(payload),
        }
        event_hash72 = hash72("pass198.registry.event", body)
        cursor = db.execute(
            "INSERT INTO events(event_type,predecessor_hash72,event_hash72,payload_json) VALUES(?,?,?,?)",
            (event_type, predecessor, event_hash72, canonical_json(body)),
        )
        return int(cursor.lastrowid), event_hash72

    def register_operation(self, payload: Mapping[str, Any], *, source: str = "api", idempotent: bool = False) -> dict[str, Any]:
        spec = OperationSpec.create(payload)
        with self._lock:
            row = self._db.execute("SELECT spec_hash72,payload_json FROM operations WHERE operation_id=?", (spec.operation_id,)).fetchone()
            if row:
                if idempotent and row["spec_hash72"] == spec.spec_hash72:
                    return json.loads(row["payload_json"])
                raise Pass198RegistryError(f"operation identity already exists: {spec.operation_id}")
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "OPERATION_REGISTERED",
                    {"operation_id": spec.operation_id, "spec_hash72": spec.spec_hash72, "source": source},
                )
                document = {**spec.payload(), "registration_event_hash72": event_hash}
                self._db.execute(
                    "INSERT INTO operations(operation_id,status,spec_hash72,payload_json,created_event,updated_event) VALUES(?,?,?,?,?,?)",
                    (spec.operation_id, spec.status, spec.spec_hash72, canonical_json(document), event_id, event_id),
                )
                self._db.commit()
                return document
            except Exception:
                self._db.rollback()
                raise

    def get_operation(self, operation_id: str) -> dict[str, Any]:
        row = self._db.execute("SELECT payload_json FROM operations WHERE operation_id=?", (_string(operation_id, "operation_id"),)).fetchone()
        if not row:
            raise Pass198RegistryError(f"unknown calibration operation: {operation_id}")
        return json.loads(row["payload_json"])

    def list_operations(self) -> list[dict[str, Any]]:
        return [json.loads(row[0]) for row in self._db.execute("SELECT payload_json FROM operations ORDER BY operation_id")]

    def parameter_tree(self, operation_id: str, overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
        operation = self.get_operation(operation_id)
        if operation["status"] != "REGISTERED":
            raise Pass198RegistryError("operation is not enabled")
        payload = dict(overrides or {})
        for key, values in operation["parameter_axes"].items():
            payload.setdefault(key, values)
        config = CalibrationConfig.from_payload(payload)
        states: list[dict[str, Any]] = []
        for exponent in config.xy_symbol_values:
            for x in config.x_values:
                for y in config.y_values:
                    rejected = not x or not y
                    states.append(
                        {
                            "ordinal": len(states),
                            "x": {"numerator": x.numerator, "denominator": x.denominator},
                            "y": {"numerator": y.numerator, "denominator": y.denominator},
                            "xy_symbol": exponent,
                            "domain_class": "RECIPROCAL_ZERO_REJECTED" if rejected else "ELIGIBLE",
                            "sign_class": "ZERO" if rejected else "SAME_SIGN" if (x > 0) == (y > 0) else "OPPOSITE_SIGN",
                        }
                    )
        body = {
            "schema": TREE_SCHEMA,
            "version": VERSION,
            "operation_id": operation_id,
            "operation_spec_hash72": operation["spec_hash72"],
            "config": config.payload(),
            "state_count": len(states),
            "eligible_state_count": sum(s["domain_class"] == "ELIGIBLE" for s in states),
            "rejected_state_count": sum(s["domain_class"] != "ELIGIBLE" for s in states),
            "states": states,
        }
        return {**body, "tree_hash72": hash72("pass198.parameter.tree", body)}

    def run_operation(
        self,
        operation_id: str,
        config_payload: Mapping[str, Any] | None = None,
        *,
        resume: bool = True,
        vm81_receipt_hash72: str | None = None,
    ) -> dict[str, Any]:
        operation = self.get_operation(operation_id)
        if operation["adapter"] != "hhs.pass197.reciprocal_matrix_gate.v1":
            raise Pass198RegistryError(f"no executable adapter for {operation['adapter']}")
        tree = self.parameter_tree(operation_id, config_payload)
        provisional = hash72(
            "pass198.run.provisional",
            {"operation_id": operation_id, "tree_hash72": tree["tree_hash72"], "vm81_receipt_hash72": vm81_receipt_hash72},
        )
        report = Pass197ABHydrationCalibration(state_root=self.state_root / "runs" / provisional).run(
            config_payload,
            resume=resume,
            vm81_receipt_hash72=vm81_receipt_hash72,
        )
        run_id = hash72(
            "pass198.operation.run",
            {
                "operation_id": operation_id,
                "tree_hash72": tree["tree_hash72"],
                "report_hash72": report["report_hash72"],
                "vm81_receipt_hash72": vm81_receipt_hash72,
            },
        )
        body = {
            "schema": RUN_SCHEMA,
            "version": VERSION,
            "run_id": run_id,
            "operation_id": operation_id,
            "operation_spec_hash72": operation["spec_hash72"],
            "tree_hash72": tree["tree_hash72"],
            "config_hash72": report["config_hash72"],
            "report_hash72": report["report_hash72"],
            "state_root_hash72": report["state_root_hash72"],
            "vm81_receipt_hash72": vm81_receipt_hash72,
            "status": "CLOSED" if report["closed"] else "REJECTED",
            "summary": report["summary"],
            "replay": report["replay"],
            "created_ns": time.time_ns(),
        }
        with self._lock:
            row = self._db.execute("SELECT payload_json FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if row:
                return json.loads(row["payload_json"])
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "CALIBRATION_RUN_RECORDED",
                    {"run_id": run_id, "operation_id": operation_id, "status": body["status"], "report_hash72": body["report_hash72"]},
                )
                document = {**body, "event_hash72": event_hash}
                self._db.execute(
                    "INSERT INTO runs(run_id,operation_id,config_hash72,report_hash72,state_root_hash72,status,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?)",
                    (run_id, operation_id, body["config_hash72"], body["report_hash72"], body["state_root_hash72"], body["status"], canonical_json(document), event_id),
                )
                if report["closed"]:
                    self._record_simplifications(operation, document, report)
                self._db.commit()
                return document
            except Exception:
                self._db.rollback()
                raise

    def _record_simplifications(self, operation: Mapping[str, Any], run: Mapping[str, Any], report: Mapping[str, Any]) -> None:
        for item in report["lossless_simplifications"]:
            name = str(item["name"])
            simplification_id = hash72(
                "pass198.simplification.identity",
                {"operation_id": operation["operation_id"], "name": name, "spec_hash72": operation["spec_hash72"]},
            )
            existing = self._db.execute("SELECT payload_json FROM simplifications WHERE simplification_id=?", (simplification_id,)).fetchone()
            if existing:
                document = json.loads(existing["payload_json"])
                run_ids = sorted(set(document["run_ids"]) | {run["run_id"]})
                document["run_ids"] = run_ids
                document["verification_run_count"] = len(run_ids)
                event_id, event_hash = self._event(
                    self._db,
                    "SIMPLIFICATION_REVERIFIED",
                    {"simplification_id": simplification_id, "run_id": run["run_id"], "verification_run_count": len(run_ids)},
                )
                document["updated_event_hash72"] = event_hash
                document["proof_hash72"] = hash72("pass198.simplification.aggregate", document)
                self._db.execute(
                    "UPDATE simplifications SET proof_hash72=?,payload_json=?,updated_event=? WHERE simplification_id=?",
                    (document["proof_hash72"], canonical_json(document), event_id, simplification_id),
                )
            else:
                proof = {
                    "schema": SIMPLIFICATION_SCHEMA,
                    "version": VERSION,
                    "simplification_id": simplification_id,
                    "operation_id": operation["operation_id"],
                    "name": name,
                    "status": "ENVELOPE_VERIFIED",
                    "source_operation_identity": operation["spec_hash72"],
                    "candidate_operation_identity": hash72("pass198.simplification.candidate", {"operation_id": operation["operation_id"], "name": name}),
                    "tested_parameter_envelope_hash72": run["tree_hash72"],
                    "exact_equivalence_root_hash72": report["state_root_hash72"],
                    "counterexample_search": {
                        "mismatch_parameter_states": report["summary"]["mismatch_parameter_states"],
                        "singular_parameter_states": report["summary"]["singular_parameter_states"],
                        "negative_mutations": operation["negative_mutations"],
                    },
                    "retained_witnesses": operation["retained_witnesses"],
                    "cost": {
                        "before": report["summary"]["original_leaf_evaluations"],
                        "after": report["summary"]["factorized_cell_evaluations"],
                        "saved": report["summary"]["saved_leaf_evaluations"],
                        "saved_fraction": report["summary"]["saved_fraction"],
                    },
                    "replay_receipt": report["replay"],
                    "revocation_conditions": [
                        "exact counterexample",
                        "replay root mismatch",
                        "retained witness loss",
                        "operation identity change",
                        "unverified domain expansion",
                    ],
                    "run_ids": [run["run_id"]],
                    "verification_run_count": 1,
                }
                proof_hash72 = hash72("pass198.simplification.proof", proof)
                event_id, event_hash = self._event(
                    self._db,
                    "SIMPLIFICATION_ENVELOPE_VERIFIED",
                    {"simplification_id": simplification_id, "run_id": run["run_id"]},
                )
                document = {**proof, "proof_hash72": proof_hash72, "created_event_hash72": event_hash, "updated_event_hash72": event_hash}
                self._db.execute(
                    "INSERT INTO simplifications(simplification_id,operation_id,name,status,proof_hash72,payload_json,created_event,updated_event) VALUES(?,?,?,?,?,?,?,?)",
                    (simplification_id, operation["operation_id"], name, "ENVELOPE_VERIFIED", proof_hash72, canonical_json(document), event_id, event_id),
                )
            self._db.execute("INSERT OR IGNORE INTO simplification_runs(simplification_id,run_id) VALUES(?,?)", (simplification_id, run["run_id"]))

    def list_runs(self, operation_id: str | None = None) -> list[dict[str, Any]]:
        if operation_id:
            rows = self._db.execute("SELECT payload_json FROM runs WHERE operation_id=? ORDER BY rowid", (_string(operation_id, "operation_id"),))
        else:
            rows = self._db.execute("SELECT payload_json FROM runs ORDER BY rowid")
        return [json.loads(row[0]) for row in rows]

    def list_simplifications(self, operation_id: str | None = None) -> list[dict[str, Any]]:
        if operation_id:
            rows = self._db.execute("SELECT payload_json FROM simplifications WHERE operation_id=? ORDER BY name", (_string(operation_id, "operation_id"),))
        else:
            rows = self._db.execute("SELECT payload_json FROM simplifications ORDER BY operation_id,name")
        return [json.loads(row[0]) for row in rows]

    def promote_simplification(
        self,
        simplification_id: str,
        target_status: str,
        *,
        evidence_run_ids: Sequence[str],
        vm81_receipt_hash72: str | None = None,
    ) -> dict[str, Any]:
        target = str(target_status).upper()
        if target not in PROMOTION_ORDER:
            raise ValueError("invalid promotion target")
        row = self._db.execute("SELECT status,payload_json FROM simplifications WHERE simplification_id=?", (_string(simplification_id, "simplification_id"),)).fetchone()
        if not row:
            raise Pass198RegistryError("unknown simplification")
        current = row["status"]
        if current == "REVOKED" or target != PROMOTION_ORDER[PROMOTION_ORDER.index(current) + 1]:
            raise Pass198RegistryError("promotion must advance exactly one stage")
        document = json.loads(row["payload_json"])
        supplied = set(_strings(evidence_run_ids, "evidence_run_ids"))
        if not supplied.issubset(set(document["run_ids"])):
            raise Pass198RegistryError("unknown promotion evidence run")
        required = {"CROSS_WORKLOAD_VERIFIED": 2, "COMPILER_CANDIDATE": 2, "RUNTIME_ADMITTED": 3, "FROZEN_CONSTRAINT": 4}.get(target, 1)
        if len(supplied) < required:
            raise Pass198RegistryError(f"{target} requires {required} verified runs")
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "SIMPLIFICATION_PROMOTED",
                    {"simplification_id": simplification_id, "from": current, "to": target, "evidence_run_ids": sorted(supplied), "vm81_receipt_hash72": vm81_receipt_hash72},
                )
                document.update({
                    "status": target,
                    "promotion_evidence_run_ids": sorted(supplied),
                    "promotion_vm81_receipt_hash72": vm81_receipt_hash72,
                    "updated_event_hash72": event_hash,
                })
                document["proof_hash72"] = hash72("pass198.simplification.promoted", document)
                self._db.execute(
                    "UPDATE simplifications SET status=?,proof_hash72=?,payload_json=?,updated_event=? WHERE simplification_id=?",
                    (target, document["proof_hash72"], canonical_json(document), event_id, simplification_id),
                )
                self._db.commit()
                return _copy(document)
            except Exception:
                self._db.rollback()
                raise

    def revoke_simplification(self, simplification_id: str, reason: Mapping[str, Any], *, vm81_receipt_hash72: str | None = None) -> dict[str, Any]:
        row = self._db.execute("SELECT payload_json FROM simplifications WHERE simplification_id=?", (_string(simplification_id, "simplification_id"),)).fetchone()
        if not row:
            raise Pass198RegistryError("unknown simplification")
        document = json.loads(row["payload_json"])
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "SIMPLIFICATION_REVOKED",
                    {"simplification_id": simplification_id, "reason": dict(reason), "vm81_receipt_hash72": vm81_receipt_hash72},
                )
                document.update({
                    "status": "REVOKED",
                    "revocation_reason": dict(reason),
                    "revocation_vm81_receipt_hash72": vm81_receipt_hash72,
                    "updated_event_hash72": event_hash,
                })
                document["proof_hash72"] = hash72("pass198.simplification.revoked", document)
                self._db.execute(
                    "UPDATE simplifications SET status='REVOKED',proof_hash72=?,payload_json=?,updated_event=? WHERE simplification_id=?",
                    (document["proof_hash72"], canonical_json(document), event_id, simplification_id),
                )
                self._db.commit()
                return _copy(document)
            except Exception:
                self._db.rollback()
                raise

    def verify_event_chain(self) -> dict[str, Any]:
        predecessor = ZERO_HASH72
        count = 0
        for row in self._db.execute("SELECT seq,predecessor_hash72,event_hash72,payload_json FROM events ORDER BY seq"):
            count += 1
            if row["predecessor_hash72"] != predecessor:
                return {"ok": False, "reason": "predecessor mismatch", "sequence": row["seq"]}
            body = json.loads(row["payload_json"])
            if hash72("pass198.registry.event", body) != row["event_hash72"]:
                return {"ok": False, "reason": "event identity mismatch", "sequence": row["seq"]}
            predecessor = row["event_hash72"]
        return {"ok": True, "event_count": count, "event_tip_hash72": predecessor}

    def status(self) -> dict[str, Any]:
        operation_count = int(self._db.execute("SELECT COUNT(*) FROM operations").fetchone()[0])
        run_count = int(self._db.execute("SELECT COUNT(*) FROM runs").fetchone()[0])
        simplification_counts = {row[0]: int(row[1]) for row in self._db.execute("SELECT status,COUNT(*) FROM simplifications GROUP BY status")}
        chain = self.verify_event_chain()
        body = {
            "schema": REGISTRY_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "state_root": str(self.state_root),
            "operation_count": operation_count,
            "run_count": run_count,
            "simplification_counts": simplification_counts,
            "event_chain": chain,
            "executable_adapter_count": 1,
            "compiler_auto_promotion": False,
            "runtime_auto_admission": False,
            "ok": chain["ok"] and operation_count >= 1,
        }
        return {**body, "registry_status_hash72": hash72("pass198.registry.status", body)}


PASS198_OPERATION_CALIBRATION_REGISTRY = Pass198OperationCalibrationRegistry()
