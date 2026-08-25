"""Pass 197 restartable exact A/B hydration calibration over VM81 x 64.

I129 repair-forward: preserve the historical V1 surface while closing the ten
substantive PR #133 review findings. No alternate integrity or mutation authority
is introduced; every persisted parameter branch is audited through the inherited
core-sandbox state admission path before its local branch receipt is committed.
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from hhs_backend.runtime.pass197_exact_v1 import (
    ADDRESS_COUNT, CELL_COUNT, COLUMN_SUMS, EXPECTED_COLUMN_SUMS,
    EXPECTED_INVERSE_ROW_SUMS, HASH_AUTHORITY, INVERSE_ROW_SUMS, LANE_COUNT,
    M, ZERO_HASH72, canonical_json, exact_fraction, fraction_payload, hash72,
    matrix_power,
)
from hhs_backend.runtime.pass197_state_v1 import CalibrationConfig, evaluate_state, state_key
from hhs_runtime.core_sandbox.hhs_state_layer_v1 import HHSStateLayerV1

VERSION = "HHS_PASS_197_AB_HYDRATION_CALIBRATION_V1"
CONTRACT = "HHS-P197-ABTREE-VM81X64-EXACT-LOSSLESS-HYDRATION"
CLASSIFICATION = "HHS_PASS_197_PARAMETER_CALIBRATION_IN_PROGRESS"
REPAIR_SCHEMA = "HHS_PASS_197_I129_REPAIR_V1"
SCHEMA = "HHS_PASS_197_AB_HYDRATION_REPORT_V1"
CHECKPOINT_SCHEMA = "HHS_PASS_197_AB_HYDRATION_CHECKPOINT_V1"


class Pass197CalibrationError(RuntimeError):
    pass


class Pass197ABHydrationCalibration:
    _root_locks_guard = threading.Lock()
    _root_locks: dict[str, threading.RLock] = {}

    def __init__(self, *, state_root: str | os.PathLike[str] | None = None) -> None:
        self.state_root = Path(state_root or os.getenv("HHS_PASS197_STATE_ROOT") or ".hhs/pass197").resolve()
        self.checkpoint_path = self.state_root / "ab_hydration_checkpoint.json"
        self.report_path = self.state_root / "ab_hydration_report.json"
        self._last_report: dict[str, Any] | None = None
        root_key = str(self.state_root)
        with self._root_locks_guard:
            self._run_lock = self._root_locks.setdefault(root_key, threading.RLock())

    @staticmethod
    def _stage(stage: str, payload: Mapping[str, Any], predecessor: str) -> dict[str, Any]:
        body = {"stage": stage, "predecessor_hash72": predecessor, "payload": dict(payload)}
        return {**body, "receipt_hash72": hash72(f"pass197.hydration.{stage.lower()}", body)}

    @staticmethod
    def _write(path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            handle.write(canonical_json(payload) + "\n")
            temporary = Path(handle.name)
        temporary.replace(path)

    def _checkpoint(self, config_hash72: str, resume: bool) -> dict[str, Any]:
        fresh = {
            "schema": CHECKPOINT_SCHEMA,
            "version": VERSION,
            "repair_schema": REPAIR_SCHEMA,
            "config_hash72": config_hash72,
            "completed": {},
            "receipt_tip_hash72": ZERO_HASH72,
        }
        if not resume or not self.checkpoint_path.exists():
            return fresh
        payload = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
        if payload.get("schema") != CHECKPOINT_SCHEMA or payload.get("config_hash72") != config_hash72:
            raise Pass197CalibrationError("checkpoint schema/config mismatch")
        expected = hash72("pass197.checkpoint", {k: v for k, v in payload.items() if k != "checkpoint_hash72"})
        if payload.get("checkpoint_hash72") != expected:
            raise Pass197CalibrationError("checkpoint integrity verification failed")
        completed = payload.get("completed") or {}
        if not isinstance(completed, dict):
            raise Pass197CalibrationError("checkpoint completed-state map is invalid")
        for entry in completed.values():
            if not isinstance(entry, dict) or not entry.get("kernel_audit_receipt_hash72") or not entry.get("kernel_state_hash72"):
                raise Pass197CalibrationError("checkpoint contains a branch without inherited kernel audit evidence")
        return payload

    def _save_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        body = {k: v for k, v in checkpoint.items() if k != "checkpoint_hash72"}
        checkpoint["checkpoint_hash72"] = hash72("pass197.checkpoint", body)
        self._write(self.checkpoint_path, checkpoint)

    @staticmethod
    def _audit_branch(key: str, result: Mapping[str, Any]) -> dict[str, str]:
        """Audit one branch through the inherited state layer before persistence."""
        layer = HHSStateLayerV1(initial_state={"pass197": {"repair_schema": REPAIR_SCHEMA}})
        audit = layer.set(
            "pass197.branch",
            {
                "key": key,
                "state_hash72": result.get("state_hash72"),
                "status": result.get("status"),
                "address_count": result.get("address_count"),
                "mismatch_count": result.get("mismatch_count"),
                "singular_count": result.get("singular_count"),
                "lexical_identity_preserved": result.get("lexical_identity_preserved"),
            },
            pass197_repair_schema=REPAIR_SCHEMA,
        )
        transition = audit.get("transition") or {}
        receipt_hash72 = transition.get("receipt_hash72")
        state_hash72 = transition.get("state_hash72")
        if not audit.get("ok") or not receipt_hash72 or not state_hash72:
            raise Pass197CalibrationError(f"inherited kernel audit quarantined calibration branch: {audit.get('reason', 'unknown')}")
        return {
            "kernel_audit_receipt_hash72": str(receipt_hash72),
            "kernel_state_hash72": str(state_hash72),
        }

    def run(self, payload: Mapping[str, Any] | None = None, *, resume: bool = True, vm81_receipt_hash72: str | None = None) -> dict[str, Any]:
        with self._run_lock:
            return self._run_locked(payload, resume=resume, vm81_receipt_hash72=vm81_receipt_hash72)

    def _run_locked(self, payload: Mapping[str, Any] | None, *, resume: bool, vm81_receipt_hash72: str | None) -> dict[str, Any]:
        config = CalibrationConfig.from_payload(payload)
        config_payload = config.payload()
        config_hash72 = hash72("pass197.config", config_payload)
        checkpoint = self._checkpoint(config_hash72, resume)
        predecessor, receipts = ZERO_HASH72, []
        for stage, data in (
            ("DISCOVER", {"parameter_state_count": len(config.x_values) * len(config.y_values) * len(config.xy_symbol_values)}),
            ("CANONICALIZE", {"exact_rational_only": True, "float_ingress": "REJECTED", "config_hash72": config_hash72}),
            ("INDEX", {"cells": CELL_COUNT, "lanes": LANE_COUNT, "addresses": ADDRESS_COUNT, "formula": "s=64*c+o"}),
            ("LINK", {"column_sums": [fraction_payload(v) for v in COLUMN_SUMS], "inverse_row_sums": [fraction_payload(v) for v in INVERSE_ROW_SUMS]}),
            ("CONSTRAIN", {"x_nonzero": True, "y_nonzero": True, "integer_xy_symbol": True, "noncommutative_order_preserved": True, "kernel_audit_before_persistence": True}),
        ):
            receipt = self._stage(stage, data, predecessor)
            receipts.append(receipt)
            predecessor = receipt["receipt_hash72"]

        powers = {exponent: matrix_power(M, -exponent) for exponent in config.xy_symbol_values}
        completed = dict(checkpoint.get("completed", {}))
        for exponent in config.xy_symbol_values:
            for x in config.x_values:
                for y in config.y_values:
                    if (not x or not y) and not config.include_domain_rejections:
                        continue
                    key = state_key(x, y, exponent)
                    if key in completed:
                        continue
                    result = evaluate_state(x, y, exponent, powers[exponent])
                    kernel_evidence = self._audit_branch(key, result)
                    branch = {
                        "key": key,
                        "predecessor_hash72": checkpoint.get("receipt_tip_hash72", ZERO_HASH72),
                        "kernel_audit_receipt_hash72": kernel_evidence["kernel_audit_receipt_hash72"],
                        "kernel_state_hash72": kernel_evidence["kernel_state_hash72"],
                        "result": result,
                    }
                    branch_hash = hash72("pass197.branch.receipt", branch)
                    completed[key] = {
                        **result,
                        **kernel_evidence,
                        "branch_predecessor_hash72": branch["predecessor_hash72"],
                        "branch_receipt_hash72": branch_hash,
                    }
                    checkpoint.update({"completed": completed, "receipt_tip_hash72": branch_hash})
                    self._save_checkpoint(checkpoint)

        states = [completed[key] for key in sorted(completed)]
        admitted = [s for s in states if s["status"] == "ADMITTED"]
        rejected = [s for s in states if s["status"] == "DOMAIN_REJECTED"]
        singular = [s for s in states if s["status"] == "SINGULAR"]
        mismatches = [s for s in states if s["status"] == "MISMATCH"]
        useful = [s for s in admitted if s["useful_parameter_state"]]
        kernel_audited = [s for s in states if s.get("kernel_audit_receipt_hash72") and s.get("kernel_state_hash72")]
        classes: dict[str, int] = {}
        for state in admitted:
            classes[state["cell_gate_hash72"]] = classes.get(state["cell_gate_hash72"], 0) + 1
        execution = {
            "evaluated_parameter_states": len(states),
            "admitted_parameter_states": len(admitted),
            "domain_rejected_parameter_states": len(rejected),
            "singular_parameter_states": len(singular),
            "mismatch_parameter_states": len(mismatches),
            "kernel_audited_parameter_states": len(kernel_audited),
            "address_comparisons": sum(s["address_count"] for s in states),
        }
        for stage, data in (
            ("ADMIT", {"rule": "all 5184 leaves exact, nonsingular, and pre-persistence kernel audited", **execution}),
            ("EXECUTE", execution),
            ("VERIFY", {"exact_equality": not mismatches, "singular_free": not singular, "address_codec_verified": True, "all_branches_kernel_audited": len(kernel_audited) == len(states)}),
        ):
            receipt = self._stage(stage, data, predecessor)
            receipts.append(receipt)
            predecessor = receipt["receipt_hash72"]

        state_root = hash72(
            "pass197.state.root",
            [
                {
                    "key": key,
                    "state_hash72": completed[key]["state_hash72"],
                    "kernel_audit_receipt_hash72": completed[key]["kernel_audit_receipt_hash72"],
                    "branch_receipt_hash72": completed[key]["branch_receipt_hash72"],
                }
                for key in sorted(completed)
            ],
        )
        simplifications = [
            {"name": "ORIGINAL_TO_COMPACT_NUMERATOR", "lossless": not mismatches},
            {"name": "RECIPROCAL_DENOMINATOR_FACTORIZATION", "lossless": not mismatches},
            {"name": "VM81_LANE_BROADCAST", "lossless": not mismatches},
            {"name": "MATRIX_POWER_CACHE_BY_XY_SYMBOL", "lossless": True},
        ]
        summary = {
            **execution,
            "useful_parameter_states": len(useful),
            "equivalence_class_count": len(classes),
            "largest_equivalence_class": max(classes.values(), default=0),
            "lossless_simplifications_admitted": all(s["lossless"] for s in simplifications),
            "original_leaf_evaluations": len(admitted) * ADDRESS_COUNT,
            "factorized_cell_evaluations": len(admitted) * CELL_COUNT,
            "saved_leaf_evaluations": len(admitted) * (ADDRESS_COUNT - CELL_COUNT),
            "saved_fraction": fraction_payload(Fraction(ADDRESS_COUNT - CELL_COUNT, ADDRESS_COUNT)),
        }
        receipt = self._stage("RECEIPT", {"state_root_hash72": state_root, "summary": summary}, predecessor)
        receipts.append(receipt)
        predecessor = receipt["receipt_hash72"]

        replayed, replay_ok, first_replay_mismatch = 0, True, None
        if config.full_replay:
            for state in states:
                x = exact_fraction(state["x"], field="replay.x")
                y = exact_fraction(state["y"], field="replay.y")
                exponent = state["xy_symbol"]
                if isinstance(exponent, bool) or not isinstance(exponent, int):
                    raise Pass197CalibrationError("replay xy_symbol lost exact integer identity")
                replay = evaluate_state(x, y, exponent, powers[exponent])
                replayed += 1
                if replay["state_hash72"] != state["state_hash72"]:
                    replay_ok = False
                    first_replay_mismatch = {"expected": state["state_hash72"], "actual": replay["state_hash72"], "x": state["x"], "y": state["y"], "xy_symbol": exponent}
                    break
        full_replay_verified = config.full_replay and replay_ok and replayed == len(states)
        replay_root = hash72("pass197.replay.root", [{"state_hash72": s["state_hash72"], "branch_receipt_hash72": s["branch_receipt_hash72"]} for s in states])
        replay_data = {
            "replay_root_hash72": replay_root,
            "deterministic": bool(full_replay_verified),
            "full_replay_executed": config.full_replay,
            "replayed_parameter_states": replayed,
            "first_replay_mismatch": first_replay_mismatch,
        }
        receipt = self._stage("REPLAY", replay_data, predecessor)
        receipts.append(receipt)
        predecessor = receipt["receipt_hash72"]
        closed = (
            not mismatches
            and not singular
            and len(kernel_audited) == len(states)
            and full_replay_verified
            and all(s["lossless"] for s in simplifications)
        )
        receipts.append(self._stage("CLOSE", {"closed": closed, "useful_parameter_states": len(useful)}, predecessor))

        report = {
            "schema": SCHEMA,
            "version": VERSION,
            "repair_schema": REPAIR_SCHEMA,
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "hash_authority": HASH_AUTHORITY,
            "authority": {
                "canonical_admission": "VM81_AUTHORIZED_TICK_AND_HASH72_RECEIPT",
                "vm81_receipt_hash72": vm81_receipt_hash72,
                "branch_pre_persistence_audit": "HHSStateLayerV1/AuditedRunner",
                "api_or_worker_is_authority": False,
            },
            "config": config_payload,
            "config_hash72": config_hash72,
            "hydration_path": ["DISCOVER", "CANONICALIZE", "INDEX", "LINK", "CONSTRAIN", "ADMIT", "EXECUTE", "VERIFY", "RECEIPT", "REPLAY", "CLOSE"],
            "vm81": {"cells": CELL_COUNT, "lanes_per_cell": LANE_COUNT, "addresses": ADDRESS_COUNT, "address_formula": "s=64*c+o", "cell_formula": "c=27*i+9*j+3*k+l"},
            "matrix_invariants": {"column_sums": [fraction_payload(v) for v in COLUMN_SUMS], "inverse_row_sums": [fraction_payload(v) for v in INVERSE_ROW_SUMS], "expected_column_sums_match": COLUMN_SUMS == EXPECTED_COLUMN_SUMS, "expected_inverse_row_sums_match": INVERSE_ROW_SUMS == EXPECTED_INVERSE_ROW_SUMS},
            "analytic_domain_proof": {"scope": "all real nonzero rational x,y and exact integer xy_symbol", "off_diagonal_nonsingular": "real part is -3", "diagonal_nonsingular": "xy=1/3 forces equal signs, so positive r_i*y+c_i*x cannot vanish", "all_real_nonzero_rational_states_nonsingular": all(v > 0 for v in COLUMN_SUMS + INVERSE_ROW_SUMS), "zero_states": "domain-rejected"},
            "summary": summary,
            "lossless_simplifications": simplifications,
            "state_root_hash72": state_root,
            "parameter_states": states,
            "stage_receipts": receipts,
            "replay": replay_data,
            "closed": closed,
        }
        report["report_hash72"] = hash72("pass197.report", report)
        self._write(self.report_path, report)
        self._last_report = report
        return json.loads(canonical_json(report))

    def status(self) -> dict[str, Any]:
        if self._last_report is None and self.report_path.exists():
            try:
                self._last_report = self.report()
            except Pass197CalibrationError as exc:
                return {
                    "schema": "HHS_PASS_197_STATUS_V1",
                    "version": VERSION,
                    "repair_schema": REPAIR_SCHEMA,
                    "scanned": True,
                    "closed": False,
                    "quarantined": True,
                    "reason": "REPORT_INTEGRITY_VERIFICATION_FAILED",
                    "detail": str(exc),
                    "state_root": str(self.state_root),
                }
        if self._last_report is None:
            return {"schema": "HHS_PASS_197_STATUS_V1", "version": VERSION, "repair_schema": REPAIR_SCHEMA, "scanned": False, "closed": False, "state_root": str(self.state_root)}
        return {"schema": "HHS_PASS_197_STATUS_V1", "version": VERSION, "repair_schema": REPAIR_SCHEMA, "scanned": True, "closed": bool(self._last_report.get("closed")), "quarantined": False, "report_hash72": self._last_report.get("report_hash72"), "summary": self._last_report.get("summary"), "state_root": str(self.state_root)}

    def report(self) -> dict[str, Any]:
        if self._last_report is None:
            if not self.report_path.exists():
                raise Pass197CalibrationError("calibration report unavailable")
            self._last_report = json.loads(self.report_path.read_text(encoding="utf-8"))
        expected = hash72("pass197.report", {k: v for k, v in self._last_report.items() if k != "report_hash72"})
        if self._last_report.get("report_hash72") != expected:
            self._last_report = None
            raise Pass197CalibrationError("calibration report integrity verification failed")
        return json.loads(canonical_json(self._last_report))


PASS197_AB_HYDRATION_CALIBRATION = Pass197ABHydrationCalibration()
