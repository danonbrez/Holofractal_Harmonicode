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

from hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1 import (
    Pass197ABHydrationCalibration,
)
from hhs_backend.runtime.pass197_exact_v1 import (
    ADDRESS_COUNT,
    canonical_json,
    hash72,
)
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

OPERATION_STATES = {"REGISTERED", "DISABLED", "REVOKED"}
SIMPLIFICATION_STATES = {
    "OBSERVED",
    "ENVELOPE_VERIFIED",
    "CROSS_WORKLOAD_VERIFIED",
    "COMPILER_CANDIDATE",
    "RUNTIME_ADMITTED",
    "FROZEN_CONSTRAINT",
    "REVOKED",
}
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


def _require_string(value: Any, field: str, *, maximum: int = 256) -> str:
    text = str(value or "").strip()
    if not text or len(text) > maximum:
        raise ValueError(f"{field} must be a nonempty string of at most {maximum} characters")
    return text


def _require_string_list(value: Any, field: str, *, minimum: int = 1) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{field} must be an array")
    items = tuple(_require_string(item, field) for item in value)
    if len(items) < minimum or len(items) != len(set(items)):
        raise ValueError(f"{field} must contain at least {minimum} unique values")
    return items


def _canonical_copy(value: Any) -> Any:
    return json.loads(canonical_json(value))


@dataclass(frozen=True)
class OperationSpec:
    schema: str
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
        operation_id = _require_string(payload.get("operation_id"), "operation_id")
        version = int(payload.get("version", 1))
        if version < 1 or version > 1_000_000:
            raise ValueError("version must be in [1,1000000]")
        display_name = _require_string(payload.get("display_name"), "display_name")
        adapter = _require_string(payload.get("adapter"), "adapter")
        input_schema = dict(payload.get("input_schema") or {})
        parameter_axes = dict(payload.get("parameter_axes") or {})
        if not parameter_axes or any(not isinstance(values, list) or not values for values in parameter_axes.values()):
            raise ValueError("parameter_axes must contain nonempty arrays")
        domain_constraints = _require_string_list(payload.get("domain_constraints") or (), "domain_constraints")
        invariants = _require_string_list(payload.get("invariants") or (), "invariants")
        retained_witnesses = _require_string_list(payload.get("retained_witnesses") or (), "retained_witnesses")
        negative_mutations = _require_string_list(payload.get("negative_mutations") or (), "negative_mutations")
        branch_a = dict(payload.get("branch_a") or {})
        branch_b = dict(payload.get("branch_b") or {})
        cost_model = dict(payload.get("cost_model") or {})
        replay_policy = dict(payload.get("replay_policy") or {})
        if not branch_a or not branch_b or not cost_model or not replay_policy:
            raise ValueError("branch_a, branch_b, cost_model, and replay_policy are required")
        status = str(payload.get("status", "REGISTERED")).upper()
        if status not in OPERATION_STATES:
            raise ValueError(f"unsupported operation status: {status}")
        core = {
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
            **core,
            domain_constraints=domain_constraints,
            invariants=invariants,
            retained_witnesses=retained_witnesses,
            negative_mutations=negative_mutations,
            spec_hash72=hash72("pass198.operation.spec", core),
        )

    def payload(self) -> dict[str, Any]:
        return _canonical_copy(asdict(self))


BUILTIN_PASS197_SPEC = OperationSpec.create(
    {
        "operation_id": "pass197.reciprocal_matrix_gate",
        "version": 1,
        "display_name": "Pass 197 reciprocal matrix gate",
        "adapter": "hhs.pass197.reciprocal_matrix_gate.v1",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "x_values": {"type": "array", "items": {"type": ["integer", "string", "object"]}},
                "y_values": {"type": "array", "items": {"type": ["integer", "string", "object"]}},
                "xy_symbol_values": {"type": "array", "items": {"type": "integer"}},
                "include_domain_rejections": {"type": "boolean"},
                "full_replay": {"type": "boolean"},
            },
        },
        "parameter_axes": {
            "x_values": ["-3", "-2", "-1", "-1/2", "0", "1/2", "1", "2", "3"],
            "y_values": ["-3", "-2", "-1", "-1/2", "0", "1/2", "1", "2", "3"],
            "xy_symbol_values": [-2, -1, 0, 1, 2],
        },
        "domain_constraints": [
            "x and y must remain exact rationals",
            "x=0 or y=0 is a preserved reciprocal-domain rejection",
            "xy is a lexical matrix-power exponent and is not x*y",
            "matrix operation order is preserved",
        ],
        "branch_a": {
            "name": "original reciprocal leaf gate",
            "implementation": "pass197_exact_v1.original_gate",
        },
        "branch_b": {
            "name": "factorized compact gate",
            "implementation": "pass197_exact_v1.compact_gate",
        },
        "invariants": [
            "all admitted VM5184 addresses compare exactly",
            "no admitted denominator is singular",
            "VM81 cell and lane address round-trip is exact",
            "full replay reproduces the state root",
        ],
        "retained_witnesses": [
            "i",
            "j",
            "k",
            "l",
            "lane",
            "lexical xy exponent",
            "x*y product",
            "state Hash72",
            "branch receipt Hash72",
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
    """Persistent exact operation registry and proof-carrying simplification ledger."""

    def __init__(self, *, state_root: str | os.PathLike[str] | None = None) -> None:
        self.state_root = Path(
            state_root
            or os.getenv("HHS_PASS198_STATE_ROOT")
            or ".hhs/pass198"
        ).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "operation_calibration_registry.sqlite3"
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._create_schema()
        self.register_operation(BUILTIN_PASS197_SPEC.payload(), source="builtin", idempotent=True)

    def close(self) -> None:
        self._connection.close()

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                predecessor_hash72 TEXT NOT NULL,
                event_hash72 TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS operations (
                operation_id TEXT PRIMARY KEY,
                version INTEGER NOT NULL,
                status TEXT NOT NULL,
                spec_hash72 TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL,
                created_event INTEGER NOT NULL REFERENCES events(seq),
                updated_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                operation_id TEXT NOT NULL REFERENCES operations(operation_id),
                config_hash72 TEXT NOT NULL,
                report_hash72 TEXT NOT NULL,
                state_root_hash72 TEXT NOT NULL,
                status TEXT NOT NULL,
                vm81_receipt_hash72 TEXT,
                payload_json TEXT NOT NULL,
                created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS simplifications (
                simplification_id TEXT PRIMARY KEY,
                operation_id TEXT NOT NULL REFERENCES operations(operation_id),
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                proof_hash72 TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_event INTEGER NOT NULL REFERENCES events(seq),
                updated_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS simplification_runs (
                simplification_id TEXT NOT NULL REFERENCES simplifications(simplification_id),
                run_id TEXT NOT NULL REFERENCES runs(run_id),
                PRIMARY KEY(simplification_id, run_id)
            );
            """
        )
        self._connection.execute(
            "INSERT OR IGNORE INTO metadata(key,value) VALUES('schema',?)",
            (REGISTRY_SCHEMA,),
        )
        self._connection.commit()

    @staticmethod
    def _append_event(
        connection: sqlite3.Connection,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> tuple[int, str]:
        row = connection.execute(
            "SELECT seq,event_hash72 FROM events ORDER BY seq DESC LIMIT 1"
        ).fetchone()
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
        cursor = connection.execute(
            "INSERT INTO events(event_type,predecessor_hash72,event_hash72,payload_json) VALUES(?,?,?,?)",
            (event_type, predecessor, event_hash72, canonical_json(body)),
        )
        return int(cursor.lastrowid), event_hash72

    def register_operation(
        self,
        payload: Mapping[str, Any],
        *,
        source: str = "api",
        idempotent: bool = False,
    ) -> dict[str, Any]:
        spec = OperationSpec.create(payload)
        with self._lock:
            row = self._connection.execute(
                "SELECT spec_hash72,payload_json FROM operations WHERE operation_id=?",
                (spec.operation_id,),
            ).fetchone()
            if row:
                if row["spec_hash72"] == spec.spec_hash72 and idempotent:
                    return json.loads(row["payload_json"])
                raise Pass198RegistryError(
                    f"operation already registered with different identity: {spec.operation_id}"
                )
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._append_event(
                    self._connection,
                    "OPERATION_REGISTERED",
                    {
                        "operation_id": spec.operation_id,
                        "spec_hash72": spec.spec_hash72,
                        "source": source,
                    },
                )
                document = {
                    **spec.payload(),
                    "registration_event_hash72": event_hash,
                }
                self._connection.execute(
                    "INSERT INTO operations(operation_id,version,status,spec_hash72,payload_json,created_event,updated_event) VALUES(?,?,?,?,?,?,?)",
                    (
                        spec.operation_id,
                        spec.version,
                        spec.status,
                        spec.spec_hash72,
                        canonical_json(document),
                        event_id,
                        event_id,
                    ),
                )
                self._connection.commit()
                return document
            except Exception:
                self._connection.rollback()
                raise

    def get_operation(self, operation_id: str) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT payload_json FROM operations WHERE operation_id=?",
            (_require_string(operation_id, "operation_id"),),
        ).fetchone()
        if not row:
            raise Pass198RegistryError(f"unknown calibration operation: {operation_id}")
        return json.loads(row["payload_json"])

    def list_operations(self) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            "SELECT payload_json FROM operations ORDER BY operation_id"
        ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def parameter_tree(
        self,
        operation_id: str,
        overrides: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        operation = self.get_operation(operation_id)
        if operation["status"] != "REGISTERED":
            raise Pass198RegistryError("operation is not enabled for calibration")
        payload = dict(overrides or {})
        axes = dict(operation["parameter_axes"])
        for key in ("x_values", "y_values", "xy_symbol_values"):
            if key not in payload and key in axes:
                payload[key] = axes[key]
        config = CalibrationConfig.from_payload(payload)
        states: list[dict[str, Any]] = []
        for exponent in config.xy_symbol_values:
            for x in config.x_values:
                for y in config.y_values:
                    domain = "RECIPROCAL_ZERO_REJECTED" if not x or not y else "ELIGIBLE"
                    states.append(
                        {
                            "ordinal": len(states),
                            "x": {"numerator": x.numerator, "denominator": x.denominator},
                            "y": {"numerator": y.numerator, "denominator": y.denominator},
                            "xy_symbol": exponent,
                            "domain_class": domain,
                            "sign_class": (
                                "ZERO"
                                if not x or not y
                                else "SAME_SIGN"
                                if (x > 0) == (y > 0)
                                else "OPPOSITE_SIGN"
                            ),
                        }
                    )
        body = {
            "schema": TREE_SCHEMA,
            "version": VERSION,
            "operation_id": operation_id,
            "operation_spec_hash72": operation["spec_hash72"],
            "config": config.payload(),
            "state_count": len(states),
            "eligible_state_count": sum(item["domain_class"] == "ELIGIBLE" for item in states),
            "rejected_state_count": sum(item["domain_class"] != "ELIGIBLE" for item in states),
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
            raise Pass198RegistryError(
                f"no executable adapter registered for {operation['adapter']}"
            )
        tree = self.parameter_tree(operation_id, config_payload)
        provisional_run_id = hash72(
            "pass198.run.provisional",
            {
                "operation_id": operation_id,
                "tree_hash72": tree["tree_hash72"],
                "vm81_receipt_hash72": vm81_receipt_hash72,
            },
        )
        runtime = Pass197ABHydrationCalibration(
            state_root=self.state_root / "runs" / provisional_run_id
        )
        report = runtime.run(
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
        run_body = {
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
            existing = self._connection.execute(
                "SELECT payload_json FROM runs WHERE run_id=?",
                (run_id,),
            ).fetchone()
            if existing:
                return json.loads(existing["payload_json"])
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._append_event(
                    self._connection,
                    "CALIBRATION_RUN_RECORDED",
                    {
                        "run_id": run_id,
                        "operation_id": operation_id,
                        "status": run_body["status"],
                        "report_hash72": report["report_hash72"],
                    },
                )
                run_document = {**run_body, "event_hash72": event_hash}
                self._connection.execute(
                    "INSERT INTO runs(run_id,operation_id,config_hash72,report_hash72,state_root_hash72,status,vm81_receipt_hash72,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        run_id,
                        operation_id,
                        report["config_hash72"],
                        report["report_hash72"],
                        report["state_root_hash72"],
                        run_body["status"],
                        vm81_receipt_hash72,
                        canonical_json(run_document),
                        event_id,
                    ),
                )
                if report["closed"]:
                    self._record_simplifications(
                        self._connection,
                        operation,
                        run_document,
                        report,
                    )
                self._connection.commit()
                return run_document
            except Exception:
                self._connection.rollback()
                raise

    def _record_simplifications(
        self,
        connection: sqlite3.Connection,
        operation: Mapping[str, Any],
        run: Mapping[str, Any],
        report: Mapping[str, Any],
    ) -> None:
        for item in report["lossless_simplifications"]:
            name = str(item["name"])
            identity = {
                "operation_id": operation["operation_id"],
                "name": name,
                "source_branch": operation["branch_a"],
                "candidate_branch": operation["branch_b"],
                "operation_spec_hash72": operation["spec_hash72"],
            }
            simplification_id = hash72("pass198.simplification.identity", identity)
            proof = {
                "schema": SIMPLIFICATION_SCHEMA,
                "version": VERSION,
                "simplification_id": simplification_id,
                "operation_id": operation["operation_id"],
                "name": name,
                "status": "ENVELOPE_VERIFIED",
                "source_operation_identity": operation["spec_hash72"],
                "candidate_operation_identity": hash72(
                    "pass198.simplification.candidate",
                    {"operation": operation["operation_id"], "name": name},
                ),
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
                    "any exact counterexample",
                    "replay root mismatch",
                    "retained witness loss",
                    "operation spec identity change",
                    "domain expansion without new verification",
                ],
                "run_ids": [run["run_id"]],
            }
            proof_hash72 = hash72("pass198.simplification.proof", proof)
            row = connection.execute(
                "SELECT payload_json FROM simplifications WHERE simplification_id=?",
                (simplification_id,),
            ).fetchone()
            if row:
                existing = json.loads(row["payload_json"])
                run_ids = sorted(set(existing.get("run_ids", [])) | {run["run_id"]})
                existing["run_ids"] = run_ids
                existing["verification_run_count"] = len(run_ids)
                existing["proof_hash72"] = hash72(
                    "pass198.simplification.proof.aggregate", existing
                )
                event_id, event_hash = self._append_event(
                    connection,
                    "SIMPLIFICATION_REVERIFIED",
                    {
                        "simplification_id": simplification_id,
                        "run_id": run["run_id"],
                        "verification_run_count": len(run_ids),
                    },
                )
                existing["updated_event_hash72"] = event_hash
                connection.execute(
                    "UPDATE simplifications SET proof_hash72=?,payload_json=?,updated_event=? WHERE simplification_id=?",
                    (
                        existing["proof_hash72"],
                        canonical_json(existing),
                        event_id,
                        simplification_id,
                    ),
                )
            else:
                event_id, event_hash = self._append_event(
                    connection,
                    "SIMPLIFICATION_ENVELOPE_VERIFIED",
                    {
                        "simplification_id": simplification_id,
                        "operation_id": operation["operation_id"],
                        "run_id": run["run_id"],
                    },
                )
                document = {
                    **proof,
                    "proof_hash72": proof_hash72,
                    "verification_run_count": 1,
                    "created_event_hash72": event_hash,
                    "updated_event_hash72": event_hash,
                }
                connection.execute(
                    "INSERT INTO simplifications(simplification_id,operation_id,name,status,proof_hash72,payload_json,created_event,updated_event) VALUES(?,?,?,?,?,?,?,?)",
                    (
                        simplification_id,
                        operation["operation_id"],
                        name,
                        "ENVELOPE_VERIFIED",
                        proof_hash72,
                        canonical_json(document),
                        event_id,
                        event_id,
                    ),
                )
            connection.execute(
                "INSERT OR IGNORE INTO simplification_runs(simplification_id,run_id) VALUES(?,?)",
                (simplification_id, run["run_id"]),
            )

    def list_runs(self, operation_id: str | None = None) -> list[dict[str, Any]]:
        if operation_id:
            rows = self._connection.execute(
                "SELECT payload_json FROM runs WHERE operation_id=? ORDER BY rowid",
                (_require_string(operation_id, "operation_id"),),
            ).fetchall()
        else:
            rows = self._connection.execute(
                "SELECT payload_json FROM runs ORDER BY rowid"
            ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def list_simplifications(
        self,
        operation_id: str | None = None,
    ) -> list[dict[str, Any]]:
        if operation_id:
            rows = self._connection.execute(
                "SELECT payload_json FROM simplifications WHERE operation_id=? ORDER BY name",
                (_require_string(operation_id, "operation_id"),),
            ).fetchall()
        else:
            rows = self._connection.execute(
                "SELECT payload_json FROM simplifications ORDER BY operation_id,name"
            ).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def promote_simplification(
        self,
        simplification_id: str,
        target_status: str,
        *,
        evidence_run_ids: Sequence[str],
        vm81_receipt_hash72: str | None = None,
    ) -> dict[str, Any]:
        target = str(target_status).upper()
        if target not in SIMPLIFICATION_STATES or target == "REVOKED":
            raise ValueError("invalid promotion target")
        row = self._connection.execute(
            "SELECT status,payload_json FROM simplifications WHERE simplification_id=?",
            (_require_string(simplification_id, "simplification_id"),),
        ).fetchone()
        if not row:
            raise Pass198RegistryError("unknown simplification")
        document = json.loads(row["payload_json"])
        current = row["status"]
        if current == "REVOKED":
            raise Pass198RegistryError("revoked simplification cannot be promoted")
        current_index = PROMOTION_ORDER.index(current)
        target_index = PROMOTION_ORDER.index(target)
        if target_index != current_index + 1:
            raise Pass198RegistryError("promotion must advance exactly one stage")
        known_runs = set(document.get("run_ids", []))
        supplied = set(_require_string_list(evidence_run_ids, "evidence_run_ids"))
        if not supplied.issubset(known_runs):
            raise Pass198RegistryError("promotion evidence includes unknown run identity")
        requirements = {
            "CROSS_WORKLOAD_VERIFIED": 2,
            "COMPILER_CANDIDATE": 2,
            "RUNTIME_ADMITTED": 3,
            "FROZEN_CONSTRAINT": 4,
        }
        required = requirements.get(target, 1)
        if len(supplied) < required:
            raise Pass198RegistryError(
                f"{target} requires at least {required} verified run identities"
            )
        with self._lock:
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._append_event(
                    self._connection,
                    "SIMPLIFICATION_PROMOTED",
                    {
                        "simplification_id": simplification_id,
                        "from": current,
                        "to": target,
                        "evidence_run_ids": sorted(supplied),
                        "vm81_receipt_hash72": vm81_receipt_hash72,
                    },
                )
                document.update(
                    {
                        "status": target,
                        "promotion_evidence_run_ids": sorted(supplied),
                        "promotion_vm81_receipt_hash72": vm81_receipt_hash72,
                        "updated_event_hash72": event_hash,
                    }
                )
                document["proof_hash72"] = hash72(
                    "pass198.simplification.proof.promoted", document
                )
                self._connection.execute(
                    "UPDATE simplifications SET status=?,proof_hash72=?,payload_json=?,updated_event=? WHERE simplification_id=?",
                    (
                        target,
                        document["proof_hash72"],
                        canonical_json(document),
                        event_id,
                        simplification_id,
                    ),
                )
                self._connection.commit()
                return _canonical_copy(document)
            except Exception:
                self._connection.rollback()
                raise

    def revoke_simplification(
        self,
        simplification_id: str,
        reason: Mapping[str, Any],
        *,
        vm81_receipt_hash72: str | None = None,
    ) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT payload_json FROM simplifications WHERE simplification_id=?",
            (_require_string(simplification_id, "simplification_id"),),
        ).fetchone()
        if not row:
            raise Pass198RegistryError("unknown simplification")
        document = json.loads(row["payload_json"])
        with self._lock:
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._append_event(
                    self._connection,
                    "SIMPLIFICATION_REVOKED",
                    {
                        "simplification_id": simplification_id,
                        "reason": dict(reason),
                        "vm81_receipt_hash72": vm81_receipt_hash72,
                    },
                )
                document.update(
                    {
                        "status": "REVOKED",
                        "revocation_reason": dict(reason),
                        "revocation_vm81_receipt_hash72": vm81_receipt_hash72,
                        "updated_event_hash72": event_hash,
                    }
                )
                document["proof_hash72"] = hash72(
                    "pass198.simplification.revocation", document
                )
                self._connection.execute(
                    "UPDATE simplifications SET status='REVOKED',proof_hash72=?,payload_json=?,updated_event=? WHERE simplification_id=?",
                    (
                        document["proof_hash72"],
                        canonical_json(document),
                        event_id,
                        simplification_id,
                    ),
                )
                self._connection.commit()
                return _canonical_copy(document)
            except Exception:
                self._connection.rollback()
                raise

    def verify_event_chain(self) -> dict[str, Any]:
        rows = self._connection.execute(
            "SELECT seq,event_type,predecessor_hash72,event_hash72,payload_json FROM events ORDER BY seq"
        ).fetchall()
        predecessor = ZERO_HASH72
        for row in rows:
            if row["predecessor_hash72"] != predecessor:
                return {
                    "ok": False,
                    "reason": "predecessor mismatch",
                    "sequence": row["seq"],
                }
            body = json.loads(row["payload_json"])
            expected = hash72("pass198.registry.event", body)
            if expected != row["event_hash72"]:
                return {
                    "ok": False,
                    "reason": "event identity mismatch",
                    "sequence": row["seq"],
                }
            predecessor = row["event_hash72"]
        return {
            "ok": True,
            "event_count": len(rows),
            "event_tip_hash72": predecessor,
        }

    def status(self) -> dict[str, Any]:
        operation_count = int(
            self._connection.execute("SELECT COUNT(*) FROM operations").fetchone()[0]
        )
        run_count = int(
            self._connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        )
        rows = self._connection.execute(
            "SELECT status,COUNT(*) AS count FROM simplifications GROUP BY status"
        ).fetchall()
        simplification_counts = {row["status"]: int(row["count"]) for row in rows}
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
            "generic_adapter_count": 1,
            "compiler_auto_promotion": False,
            "runtime_auto_admission": False,
            "ok": chain["ok"] and operation_count >= 1,
        }
        return {**body, "registry_status_hash72": hash72("pass198.registry.status", body)}


PASS198_OPERATION_CALIBRATION_REGISTRY = Pass198OperationCalibrationRegistry()
