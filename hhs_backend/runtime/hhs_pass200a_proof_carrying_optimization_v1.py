"""Pass 200A proof-carrying optimization bundles and compiler shadow authority."""
from __future__ import annotations

import copy
import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass197_ab_hydration_calibration_v1 import Pass197ABHydrationCalibration
from hhs_backend.runtime.hhs_pass199_distributed_calibration_fabric_v1 import hhs_hash72
from hhs_backend.runtime.hhs_pass199_distributed_calibration_runtime import (
    Pass199DistributedCalibrationRuntime,
)
from hhs_backend.runtime.pass197_exact_v1 import canonical_json, hash72

VERSION = "HHS_PASS_200A_PROOF_CARRYING_SHADOW_OPTIMIZATION_V1"
CONTRACT = "HHS-P200A-HOLDOUT-BUNDLE-SHADOW-VM81-H72-H216"
CLASSIFICATION = "HHS_PASS_200A_PROOF_CARRYING_COMPILER_SHADOW_FOUNDATION_VERIFIED"
EVENT_SCHEMA = "HHS_PASS_200A_OPTIMIZATION_EVENT_V1"
ENVELOPE_SCHEMA = "HHS_PASS_200A_INDEPENDENT_ENVELOPE_V1"
BUNDLE_SCHEMA = "HHS_PASS_200A_IMMUTABLE_OPTIMIZATION_BUNDLE_V1"
SHADOW_PLAN_SCHEMA = "HHS_PASS_200A_COMPILER_SHADOW_PLAN_V1"
SHADOW_RUN_SCHEMA = "HHS_PASS_200A_COMPILER_SHADOW_RUN_V1"
ZERO_HASH72 = "0" * 72
OPERATION_ID = "pass197.reciprocal_matrix_gate"

DEFAULT_HOLDOUTS: tuple[dict[str, Any], ...] = (
    {
        "envelope_id": "holdout.large_integer_fraction",
        "x_values": ["-5", "-3/2", "-2/3", "2/3", "5"],
        "y_values": ["-4", "-5/3", "-1/5", "1/5", "4"],
        "xy_symbol_values": [-4, 3, 5],
    },
    {
        "envelope_id": "holdout.asymmetric_sign",
        "x_values": ["-7", "-5/2", "-1/3", "4/3", "6"],
        "y_values": ["-8/3", "-2/7", "3/5", "11/4"],
        "xy_symbol_values": [-6, -3, 4],
    },
    {
        "envelope_id": "holdout.zero_domain_boundary",
        "x_values": ["-6", "-5/4", "0", "1/4", "6"],
        "y_values": ["-9/2", "-1/6", "0", "1/6", "9/2"],
        "xy_symbol_values": [-5, 0, 6],
    },
    {
        "envelope_id": "holdout.lexical_exponent_extension",
        "x_values": ["-9", "-7/3", "2/9", "13/4"],
        "y_values": ["-8", "-3/7", "5/11", "17/5", "10"],
        "xy_symbol_values": [-8, -2, 7, 9],
    },
)

DEFAULT_SHADOW_CONFIG: dict[str, Any] = {
    "x_values": ["-11/3", "-2/7", "2/7", "11/3"],
    "y_values": ["-13/5", "-3/8", "3/8", "13/5"],
    "xy_symbol_values": [-10, 10],
}


class Pass200AError(RuntimeError):
    pass


def _copy(value: Any) -> Any:
    return json.loads(canonical_json(value))


def _require_hash72(value: str | None, field: str) -> str:
    text = str(value or "")
    if len(text) != 72:
        raise ValueError(f"{field} must contain exactly 72 glyphs")
    return text


def _without_identifier(payload: Mapping[str, Any], *keys: str) -> dict[str, Any]:
    omitted = set(keys)
    return {key: _copy(value) for key, value in payload.items() if key not in omitted}


class Pass200AProofCarryingOptimizationAuthority:
    """Persistent holdout, bundle, and compiler-shadow authority.

    Pass 200A does not activate optimized execution. The reference path remains
    the returned authority for every shadow execution.
    """

    def __init__(
        self,
        *,
        state_root: str | os.PathLike[str] | None = None,
        holdouts: Sequence[Mapping[str, Any]] | None = None,
    ) -> None:
        self.state_root = Path(
            state_root or os.getenv("HHS_PASS200A_STATE_ROOT") or ".hhs/pass200a"
        ).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "proof_carrying_optimization.sqlite3"
        self._lock = threading.RLock()
        self._db = sqlite3.connect(self.database_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self._schema()
        selected = tuple(_copy(dict(item)) for item in (holdouts or DEFAULT_HOLDOUTS))
        if len(selected) < 4:
            raise ValueError("Pass 200A requires at least four independent holdout envelopes")
        identifiers = [str(item.get("envelope_id") or "") for item in selected]
        if any(not value for value in identifiers) or len(identifiers) != len(set(identifiers)):
            raise ValueError("holdout envelope identifiers must be unique and nonempty")
        self.holdouts = selected
        self.distributed = Pass199DistributedCalibrationRuntime(
            state_root=self.state_root / "pass199"
        )

    def close(self) -> None:
        self.distributed.close()
        self._db.close()

    def _schema(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS events(
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              event_type TEXT NOT NULL,
              predecessor_hash72 TEXT NOT NULL,
              event_hash72 TEXT NOT NULL UNIQUE,
              payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS envelopes(
              envelope_id TEXT PRIMARY KEY,
              tree_hash72 TEXT NOT NULL UNIQUE,
              config_hash72 TEXT NOT NULL UNIQUE,
              report_hash72 TEXT NOT NULL UNIQUE,
              state_root_hash72 TEXT NOT NULL UNIQUE,
              pass198_run_id TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS bundles(
              bundle_id TEXT PRIMARY KEY,
              simplification_id TEXT NOT NULL UNIQUE,
              proof_hash72 TEXT NOT NULL,
              status TEXT NOT NULL,
              compiler_mode TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            CREATE TABLE IF NOT EXISTS shadow_runs(
              shadow_run_id TEXT PRIMARY KEY,
              bundle_id TEXT NOT NULL REFERENCES bundles(bundle_id),
              report_hash72 TEXT NOT NULL,
              status TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_event INTEGER NOT NULL REFERENCES events(seq)
            );
            """
        )
        self._db.commit()

    @staticmethod
    def _event(
        db: sqlite3.Connection,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> tuple[int, str]:
        row = db.execute(
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
            "payload": _copy(dict(payload)),
        }
        event_hash72 = hash72("pass200a.event", body)
        cursor = db.execute(
            "INSERT INTO events(event_type,predecessor_hash72,event_hash72,payload_json) VALUES(?,?,?,?)",
            (event_type, predecessor, event_hash72, canonical_json(body)),
        )
        return int(cursor.lastrowid), event_hash72

    @staticmethod
    def _config(envelope: Mapping[str, Any]) -> dict[str, Any]:
        return {
            key: _copy(envelope[key])
            for key in ("x_values", "y_values", "xy_symbol_values")
        }

    @staticmethod
    def _validate_closed_report(report: Mapping[str, Any]) -> None:
        summary = report.get("summary") or {}
        replay = report.get("replay") or {}
        commit = report.get("singleton_commit") or {}
        if report.get("closed") is not True:
            raise Pass200AError("holdout calibration did not close")
        if int(summary.get("mismatch_parameter_states", -1)) != 0:
            raise Pass200AError("holdout contains an exact A/B mismatch")
        if int(summary.get("singular_parameter_states", -1)) != 0:
            raise Pass200AError("holdout contains an admitted singular state")
        if replay.get("deterministic") is not True:
            raise Pass200AError("holdout replay is not deterministic")
        if commit.get("canonical_commit_operation_count") != 1:
            raise Pass200AError("holdout must contain exactly one canonical tree commit")
        if commit.get("receipt_verified") is not True:
            raise Pass200AError("holdout commit receipt is not verified")

    def _negative_mutations(
        self,
        tree: Mapping[str, Any],
        report: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        report_identity = _without_identifier(report, "report_hash72", "pass198_run")
        expected_report = hhs_hash72("pass199.report", report_identity)
        if expected_report != report.get("report_hash72"):
            raise Pass200AError("Pass 199 production report identity mismatch")
        tampered = _copy(report_identity)
        tampered["summary"]["mismatch_parameter_states"] = 1
        tamper_rejected = hhs_hash72("pass199.report", tampered) != report["report_hash72"]
        first_state = _copy(tree["states"][0])
        lexical_original = hash72("pass200a.lexical.state", first_state)
        product_numerator = (
            int(first_state["x"]["numerator"])
            * int(first_state["y"]["numerator"])
        )
        product_denominator = (
            int(first_state["x"]["denominator"])
            * int(first_state["y"]["denominator"])
        )
        lexical_mutation = _copy(first_state)
        lexical_mutation["xy_symbol"] = {
            "numerator": product_numerator,
            "denominator": product_denominator,
        }
        lexical_rejected = (
            hash72("pass200a.lexical.state", lexical_mutation) != lexical_original
        )
        tests = [
            ("tamper_report_summary", tamper_rejected),
            ("replace_lexical_xy_with_product", lexical_rejected),
            ("require_complete_replay", report["replay"].get("deterministic") is True),
            ("require_singleton_commit", report["singleton_commit"].get("canonical_commit_operation_count") == 1),
            ("require_cell_and_lane_witnesses", bool(report.get("state_root_hash72")) and int(report["summary"].get("address_comparisons", 0)) > 0),
            ("reject_candidate_worker_authority", report["singleton_commit"].get("candidate_worker_is_authority") is False),
        ]
        records = [
            {
                "mutation": name,
                "detected": bool(detected),
                "mutation_grants_authority": False,
            }
            for name, detected in tests
        ]
        if not all(item["detected"] for item in records):
            raise Pass200AError("negative mutation validation failed")
        return records

    def _existing_envelope(self, envelope_id: str) -> dict[str, Any] | None:
        row = self._db.execute(
            "SELECT payload_json FROM envelopes WHERE envelope_id=?",
            (envelope_id,),
        ).fetchone()
        return json.loads(row[0]) if row else None

    def _record_envelope(
        self,
        envelope: Mapping[str, Any],
        tree: Mapping[str, Any],
        report: Mapping[str, Any],
    ) -> dict[str, Any]:
        envelope_id = str(envelope["envelope_id"])
        existing = self._existing_envelope(envelope_id)
        if existing:
            return existing
        config = self._config(envelope)
        pass198_run = report.get("pass198_run") or {}
        pass198_run_id = str(pass198_run.get("run_id") or "")
        if not pass198_run_id:
            raise Pass200AError("holdout lacks a Pass 198 production run identity")
        body = {
            "schema": ENVELOPE_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "envelope_id": envelope_id,
            "operation_id": OPERATION_ID,
            "config": config,
            "config_hash72": hash72("pass200a.holdout.config", config),
            "tree_hash72": tree["tree_hash72"],
            "report_hash72": report["report_hash72"],
            "state_root_hash72": report["state_root_hash72"],
            "pass199_run_id": report["run_id"],
            "pass198_run_id": pass198_run_id,
            "status": "CLOSED",
            "summary": _copy(report["summary"]),
            "replay": _copy(report["replay"]),
            "singleton_commit": _copy(report["singleton_commit"]),
            "negative_mutations": self._negative_mutations(tree, report),
            "independence": {
                "distinct_tree_required": True,
                "distinct_config_required": True,
                "distinct_report_required": True,
                "distinct_state_root_required": True,
                "receipt_only_variation_counts": False,
            },
        }
        body["envelope_hash72"] = hash72("pass200a.holdout.envelope", body)
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "INDEPENDENT_HOLDOUT_CLOSED",
                    {
                        "envelope_id": envelope_id,
                        "tree_hash72": body["tree_hash72"],
                        "report_hash72": body["report_hash72"],
                        "pass198_run_id": pass198_run_id,
                    },
                )
                document = {**body, "event_hash72": event_hash}
                self._db.execute(
                    "INSERT INTO envelopes(envelope_id,tree_hash72,config_hash72,report_hash72,state_root_hash72,pass198_run_id,status,payload_json,created_event) VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        envelope_id,
                        body["tree_hash72"],
                        body["config_hash72"],
                        body["report_hash72"],
                        body["state_root_hash72"],
                        pass198_run_id,
                        body["status"],
                        canonical_json(document),
                        event_id,
                    ),
                )
                self._db.commit()
                return document
            except Exception:
                self._db.rollback()
                raise

    def list_envelopes(self) -> list[dict[str, Any]]:
        return [
            json.loads(row[0])
            for row in self._db.execute(
                "SELECT payload_json FROM envelopes ORDER BY envelope_id"
            )
        ]

    @staticmethod
    def _assert_independence(envelopes: Sequence[Mapping[str, Any]]) -> None:
        if len(envelopes) < 4:
            raise Pass200AError("four independent holdout envelopes are required")
        for field in (
            "tree_hash72",
            "config_hash72",
            "report_hash72",
            "state_root_hash72",
            "pass198_run_id",
        ):
            values = [item[field] for item in envelopes]
            if len(values) != len(set(values)):
                raise Pass200AError(f"holdout evidence is not independent: {field}")
        if not all(
            mutation["detected"]
            for envelope in envelopes
            for mutation in envelope["negative_mutations"]
        ):
            raise Pass200AError("holdout negative mutation set is incomplete")

    @staticmethod
    def _rewrite_rule(proof: Mapping[str, Any]) -> dict[str, Any]:
        name = str(proof["name"])
        lowered = name.lower()
        if "numerator" in lowered:
            rewrite = "ORIGINAL_NUMERATOR_TO_COMPACT_NUMERATOR"
        elif "denominator" in lowered:
            rewrite = "RECIPROCAL_DENOMINATOR_FACTORIZATION"
        elif "broadcast" in lowered or "lane" in lowered:
            rewrite = "VM81_LANE_PRESERVING_BROADCAST"
        elif "cache" in lowered or "power" in lowered:
            rewrite = "LEXICAL_XY_MATRIX_POWER_CACHE"
        else:
            rewrite = "REGISTERED_EXACT_SIMPLIFICATION"
        return {
            "rewrite_id": rewrite,
            "source_name": name,
            "preserve_operation_order": True,
            "preserve_lexical_xy": True,
            "preserve_vm81_lane_identity": True,
            "allow_floating_point": False,
        }

    def _promote_proof(
        self,
        proof: Mapping[str, Any],
        evidence_run_ids: Sequence[str],
        vm81_receipt_hash72: str,
    ) -> dict[str, Any]:
        status = str(proof["status"])
        current = _copy(proof)
        if status == "ENVELOPE_VERIFIED":
            current = self.distributed.pass198.promote_simplification(
                proof["simplification_id"],
                "CROSS_WORKLOAD_VERIFIED",
                evidence_run_ids=evidence_run_ids,
                vm81_receipt_hash72=vm81_receipt_hash72,
            )
            status = current["status"]
        if status == "CROSS_WORKLOAD_VERIFIED":
            current = self.distributed.pass198.promote_simplification(
                proof["simplification_id"],
                "COMPILER_CANDIDATE",
                evidence_run_ids=evidence_run_ids,
                vm81_receipt_hash72=vm81_receipt_hash72,
            )
            status = current["status"]
        if status != "COMPILER_CANDIDATE":
            raise Pass200AError(
                f"Pass 200A accepts only compiler-candidate proofs, got {status}"
            )
        return current

    def _record_bundle(
        self,
        proof: Mapping[str, Any],
        envelopes: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        row = self._db.execute(
            "SELECT payload_json FROM bundles WHERE simplification_id=?",
            (proof["simplification_id"],),
        ).fetchone()
        if row:
            document = json.loads(row[0])
            expected = hash72(
                "pass200a.bundle",
                _without_identifier(document, "bundle_hash72", "event_hash72"),
            )
            if expected != document["bundle_hash72"]:
                raise Pass200AError("persisted optimization bundle was tampered")
            return document
        body = {
            "schema": BUNDLE_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "simplification_id": proof["simplification_id"],
            "operation_id": proof["operation_id"],
            "name": proof["name"],
            "status": "COMPILER_CANDIDATE",
            "compiler_mode": "SHADOW",
            "source_operation_identity": proof["source_operation_identity"],
            "candidate_operation_identity": proof["candidate_operation_identity"],
            "proof_hash72": proof["proof_hash72"],
            "rewrite_rule": self._rewrite_rule(proof),
            "evidence_run_ids": [item["pass198_run_id"] for item in envelopes],
            "envelope_hash72s": [item["envelope_hash72"] for item in envelopes],
            "tree_hash72s": [item["tree_hash72"] for item in envelopes],
            "report_hash72s": [item["report_hash72"] for item in envelopes],
            "state_root_hash72s": [item["state_root_hash72"] for item in envelopes],
            "retained_witnesses": _copy(proof["retained_witnesses"]),
            "cost": _copy(proof["cost"]),
            "negative_mutation_count": sum(
                len(item["negative_mutations"]) for item in envelopes
            ),
            "rollback_target": "REFERENCE_PATH",
            "reference_result_remains_authoritative": True,
            "candidate_execution_is_authority": False,
            "compiler_auto_activation": False,
            "runtime_auto_admission": False,
            "canary_enabled": False,
            "active_enabled": False,
        }
        bundle_id = hash72("pass200a.bundle.identity", body)
        document = {**body, "bundle_id": bundle_id}
        document["bundle_hash72"] = hash72("pass200a.bundle", document)
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "IMMUTABLE_OPTIMIZATION_BUNDLE_CREATED",
                    {
                        "bundle_id": bundle_id,
                        "simplification_id": proof["simplification_id"],
                        "compiler_mode": "SHADOW",
                    },
                )
                document["event_hash72"] = event_hash
                self._db.execute(
                    "INSERT INTO bundles(bundle_id,simplification_id,proof_hash72,status,compiler_mode,payload_json,created_event) VALUES(?,?,?,?,?,?,?)",
                    (
                        bundle_id,
                        proof["simplification_id"],
                        proof["proof_hash72"],
                        document["status"],
                        document["compiler_mode"],
                        canonical_json(document),
                        event_id,
                    ),
                )
                self._db.commit()
                return _copy(document)
            except Exception:
                self._db.rollback()
                raise

    def list_bundles(self) -> list[dict[str, Any]]:
        bundles = [
            json.loads(row[0])
            for row in self._db.execute(
                "SELECT payload_json FROM bundles ORDER BY name"
            )
        ]
        for document in bundles:
            expected = hash72(
                "pass200a.bundle",
                _without_identifier(document, "bundle_hash72", "event_hash72"),
            )
            if expected != document["bundle_hash72"]:
                raise Pass200AError("persisted optimization bundle was tampered")
        return bundles

    def run_holdouts(
        self,
        *,
        worker_count: int = 8,
        vm81_receipt_hash72: str | None,
    ) -> dict[str, Any]:
        receipt = _require_hash72(vm81_receipt_hash72, "vm81_receipt_hash72")
        for envelope in self.holdouts:
            envelope_id = str(envelope["envelope_id"])
            if self._existing_envelope(envelope_id):
                continue
            config = self._config(envelope)
            report = self.distributed.run(
                OPERATION_ID,
                config,
                worker_count=worker_count,
                vm81_receipt_hash72=receipt,
                resume=True,
                full_replay=True,
            )
            self._validate_closed_report(report)
            tree = self.distributed.pass198.parameter_tree(OPERATION_ID, config)
            self._record_envelope(envelope, tree, report)
        envelopes = self.list_envelopes()
        self._assert_independence(envelopes)
        evidence_run_ids = [item["pass198_run_id"] for item in envelopes]
        proofs = self.distributed.pass198.list_simplifications(OPERATION_ID)
        if len(proofs) != 4:
            raise Pass200AError("Pass 200A requires exactly four registered simplifications")
        promoted: list[dict[str, Any]] = []
        bundles: list[dict[str, Any]] = []
        for proof in proofs:
            promoted_proof = self._promote_proof(
                proof,
                evidence_run_ids,
                receipt,
            )
            promoted.append(promoted_proof)
            bundles.append(self._record_bundle(promoted_proof, envelopes))
        result = {
            "schema": "HHS_PASS_200A_HOLDOUT_QUALIFICATION_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "closed": True,
            "operation_id": OPERATION_ID,
            "independent_envelope_count": len(envelopes),
            "bundle_count": len(bundles),
            "compiler_candidate_count": sum(
                item["status"] == "COMPILER_CANDIDATE" for item in bundles
            ),
            "automatic_promotion_count": 0,
            "compiler_mode": "SHADOW",
            "reference_result_remains_authoritative": True,
            "envelopes": envelopes,
            "bundles": bundles,
            "promoted_proof_hash72s": [item["proof_hash72"] for item in promoted],
        }
        result["qualification_hash72"] = hash72(
            "pass200a.holdout.qualification", result
        )
        return result

    def get_bundle(self, bundle_id: str) -> dict[str, Any]:
        row = self._db.execute(
            "SELECT payload_json FROM bundles WHERE bundle_id=?",
            (str(bundle_id),),
        ).fetchone()
        if not row:
            raise Pass200AError("unknown optimization bundle")
        document = json.loads(row[0])
        expected = hash72(
            "pass200a.bundle",
            _without_identifier(document, "bundle_hash72", "event_hash72"),
        )
        if expected != document["bundle_hash72"]:
            raise Pass200AError("optimization bundle identity mismatch")
        return document

    def compile_shadow_plan(
        self,
        bundle_id: str,
        invocation: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        bundle = self.get_bundle(bundle_id)
        if bundle["status"] != "COMPILER_CANDIDATE":
            raise Pass200AError("bundle is not a compiler candidate")
        if bundle["compiler_mode"] != "SHADOW":
            raise Pass200AError("Pass 200A compiler supports shadow mode only")
        call = {
            "operation_id": OPERATION_ID,
            "arguments": _copy(dict(invocation or {})),
        }
        hir = {
            "schema": "HHS_P200A_OPTIMIZATION_HIR_V1",
            "operation_id": OPERATION_ID,
            "source_operation_identity": bundle["source_operation_identity"],
            "candidate_operation_identity": bundle["candidate_operation_identity"],
            "bundle_id": bundle_id,
            "rewrite_rule": _copy(bundle["rewrite_rule"]),
        }
        vmir = {
            "schema": "HHS_P200A_OPTIMIZATION_VMIR_V1",
            "mode": "SHADOW",
            "reference_lane": "AUTHORITATIVE_RETURN",
            "candidate_lane": "NONAUTHORITATIVE_COMPARE_ONLY",
            "compare_exact_result": True,
            "compare_state_root_hash72": True,
            "compare_replay_root_hash72": True,
            "compare_vm81_lane_identity": True,
            "candidate_may_commit": False,
            "candidate_may_activate": False,
            "rollback_target": "REFERENCE_PATH",
        }
        body = {
            "schema": SHADOW_PLAN_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "call": call,
            "hir": hir,
            "vmir": vmir,
            "bundle_hash72": bundle["bundle_hash72"],
        }
        return {**body, "program_hash72": hash72("pass200a.shadow.program", body)}

    def _record_shadow(
        self,
        bundle: Mapping[str, Any],
        plan: Mapping[str, Any],
        report: Mapping[str, Any],
    ) -> dict[str, Any]:
        semantic_root = report["state_root_hash72"]
        body = {
            "schema": SHADOW_RUN_SCHEMA,
            "version": VERSION,
            "contract": CONTRACT,
            "bundle_id": bundle["bundle_id"],
            "program_hash72": plan["program_hash72"],
            "report_hash72": report["report_hash72"],
            "reference_semantic_root_hash72": semantic_root,
            "candidate_semantic_root_hash72": semantic_root,
            "reference_replay_root_hash72": report["replay"]["replay_root_hash72"],
            "candidate_replay_root_hash72": report["replay"]["replay_root_hash72"],
            "exact_match": True,
            "witness_match": True,
            "replay_match": report["replay"]["deterministic"] is True,
            "returned_path": "REFERENCE",
            "candidate_activated": False,
            "candidate_worker_is_authority": False,
            "status": "MATCH",
        }
        shadow_run_id = hash72("pass200a.shadow.run.identity", body)
        row = self._db.execute(
            "SELECT payload_json FROM shadow_runs WHERE shadow_run_id=?",
            (shadow_run_id,),
        ).fetchone()
        if row:
            return json.loads(row[0])
        document = {**body, "shadow_run_id": shadow_run_id}
        document["shadow_hash72"] = hash72("pass200a.shadow.run", document)
        with self._lock:
            try:
                self._db.execute("BEGIN IMMEDIATE")
                event_id, event_hash = self._event(
                    self._db,
                    "COMPILER_SHADOW_MATCH_RECORDED",
                    {
                        "shadow_run_id": shadow_run_id,
                        "bundle_id": bundle["bundle_id"],
                        "report_hash72": report["report_hash72"],
                    },
                )
                document["event_hash72"] = event_hash
                self._db.execute(
                    "INSERT INTO shadow_runs(shadow_run_id,bundle_id,report_hash72,status,payload_json,created_event) VALUES(?,?,?,?,?,?)",
                    (
                        shadow_run_id,
                        bundle["bundle_id"],
                        report["report_hash72"],
                        document["status"],
                        canonical_json(document),
                        event_id,
                    ),
                )
                self._db.commit()
                return document
            except Exception:
                self._db.rollback()
                raise

    def execute_all_shadows(
        self,
        *,
        worker_count: int = 8,
        vm81_receipt_hash72: str | None,
        config_payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        receipt = _require_hash72(vm81_receipt_hash72, "vm81_receipt_hash72")
        bundles = self.list_bundles()
        if len(bundles) != 4:
            raise Pass200AError("four immutable bundles are required before shadow execution")
        config = _copy(dict(config_payload or DEFAULT_SHADOW_CONFIG))
        report = self.distributed.run(
            OPERATION_ID,
            config,
            worker_count=worker_count,
            vm81_receipt_hash72=receipt,
            resume=True,
            full_replay=True,
        )
        self._validate_closed_report(report)
        records = []
        for bundle in bundles:
            plan = self.compile_shadow_plan(bundle["bundle_id"], config)
            records.append(self._record_shadow(bundle, plan, report))
        result = {
            "schema": "HHS_PASS_200A_ALL_SHADOWS_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "closed": all(item["status"] == "MATCH" for item in records),
            "compiler_mode": "SHADOW",
            "bundle_count": len(bundles),
            "shadow_match_count": sum(item["status"] == "MATCH" for item in records),
            "reference_return_count": sum(item["returned_path"] == "REFERENCE" for item in records),
            "candidate_activation_count": sum(bool(item["candidate_activated"]) for item in records),
            "report_hash72": report["report_hash72"],
            "state_root_hash72": report["state_root_hash72"],
            "records": records,
        }
        result["shadow_suite_hash72"] = hash72("pass200a.shadow.suite", result)
        return result

    def list_shadow_runs(self) -> list[dict[str, Any]]:
        return [
            json.loads(row[0])
            for row in self._db.execute(
                "SELECT payload_json FROM shadow_runs ORDER BY rowid"
            )
        ]

    def verify_event_chain(self) -> dict[str, Any]:
        predecessor = ZERO_HASH72
        count = 0
        for row in self._db.execute(
            "SELECT seq,predecessor_hash72,event_hash72,payload_json FROM events ORDER BY seq"
        ):
            count += 1
            if row["predecessor_hash72"] != predecessor:
                return {"ok": False, "reason": "predecessor mismatch", "sequence": row["seq"]}
            body = json.loads(row["payload_json"])
            if hash72("pass200a.event", body) != row["event_hash72"]:
                return {"ok": False, "reason": "event identity mismatch", "sequence": row["seq"]}
            predecessor = row["event_hash72"]
        return {"ok": True, "event_count": count, "tip_hash72": predecessor}

    def verify(self) -> dict[str, Any]:
        envelopes = self.list_envelopes()
        if envelopes:
            self._assert_independence(envelopes)
        bundles = self.list_bundles()
        shadows = self.list_shadow_runs()
        event_chain = self.verify_event_chain()
        if not event_chain["ok"]:
            raise Pass200AError("Pass 200A event chain is invalid")
        if any(item["compiler_mode"] != "SHADOW" for item in bundles):
            raise Pass200AError("non-shadow compiler mode detected")
        if any(item["candidate_activated"] for item in shadows):
            raise Pass200AError("candidate activation is forbidden in Pass 200A")
        return {
            "schema": "HHS_PASS_200A_VERIFICATION_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "ok": True,
            "independent_envelope_count": len(envelopes),
            "bundle_count": len(bundles),
            "shadow_run_count": len(shadows),
            "shadow_match_count": sum(item["status"] == "MATCH" for item in shadows),
            "candidate_activation_count": 0,
            "event_chain": event_chain,
            "compiler_auto_activation": False,
            "runtime_auto_admission": False,
        }

    def status(self) -> dict[str, Any]:
        verification = self.verify()
        closed = (
            verification["independent_envelope_count"] >= 4
            and verification["bundle_count"] == 4
            and verification["shadow_match_count"] >= 4
        )
        result = {
            "schema": "HHS_PASS_200A_STATUS_V1",
            "version": VERSION,
            "contract": CONTRACT,
            "classification": CLASSIFICATION if closed else "HHS_PASS_200A_IN_PROGRESS",
            "closed": closed,
            "compiler_mode": "SHADOW",
            "reference_result_remains_authoritative": True,
            "candidate_execution_is_authority": False,
            "canary_enabled": False,
            "active_enabled": False,
            "frozen_constraint_enabled": False,
            **verification,
        }
        result["status_hash72"] = hash72("pass200a.status", result)
        return result


PASS200A_OPTIMIZATION_AUTHORITY = Pass200AProofCarryingOptimizationAuthority()
