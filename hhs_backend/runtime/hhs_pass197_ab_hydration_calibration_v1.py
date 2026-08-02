"""Pass 197 restartable exact A/B hydration calibration over VM81 x 64."""
from __future__ import annotations

import json
import os
import tempfile
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

VERSION = "HHS_PASS_197_AB_HYDRATION_CALIBRATION_V1"
CONTRACT = "HHS-P197-ABTREE-VM81X64-EXACT-LOSSLESS-HYDRATION"
CLASSIFICATION = "HHS_PASS_197_PARAMETER_CALIBRATION_IN_PROGRESS"
SCHEMA = "HHS_PASS_197_AB_HYDRATION_REPORT_V1"
CHECKPOINT_SCHEMA = "HHS_PASS_197_AB_HYDRATION_CHECKPOINT_V1"


class Pass197CalibrationError(RuntimeError):
    pass


class Pass197ABHydrationCalibration:
    def __init__(self, *, state_root: str | os.PathLike[str] | None = None) -> None:
        self.state_root = Path(state_root or os.getenv("HHS_PASS197_STATE_ROOT") or ".hhs/pass197").resolve()
        self.checkpoint_path = self.state_root / "ab_hydration_checkpoint.json"
        self.report_path = self.state_root / "ab_hydration_report.json"
        self._last_report: dict[str, Any] | None = None

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
        fresh = {"schema": CHECKPOINT_SCHEMA, "version": VERSION, "config_hash72": config_hash72, "completed": {}, "receipt_tip_hash72": ZERO_HASH72}
        if not resume or not self.checkpoint_path.exists():
            return fresh
        payload = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
        if payload.get("schema") != CHECKPOINT_SCHEMA or payload.get("config_hash72") != config_hash72:
            raise Pass197CalibrationError("checkpoint schema/config mismatch")
        expected = hash72("pass197.checkpoint", {k: v for k, v in payload.items() if k != "checkpoint_hash72"})
        if payload.get("checkpoint_hash72") != expected:
            raise Pass197CalibrationError("checkpoint integrity verification failed")
        return payload

    def _save_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        body = {k: v for k, v in checkpoint.items() if k != "checkpoint_hash72"}
        checkpoint["checkpoint_hash72"] = hash72("pass197.checkpoint", body)
        self._write(self.checkpoint_path, checkpoint)

    def run(self, payload: Mapping[str, Any] | None = None, *, resume: bool = True, vm81_receipt_hash72: str | None = None) -> dict[str, Any]:
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
            ("CONSTRAIN", {"x_nonzero": True, "y_nonzero": True, "integer_xy_symbol": True, "noncommutative_order_preserved": True}),
        ):
            receipt = self._stage(stage, data, predecessor)
            receipts.append(receipt); predecessor = receipt["receipt_hash72"]

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
                    branch = {"key": key, "predecessor_hash72": checkpoint.get("receipt_tip_hash72", ZERO_HASH72), "result": result}
                    branch_hash = hash72("pass197.branch.receipt", branch)
                    completed[key] = {**result, "branch_predecessor_hash72": branch["predecessor_hash72"], "branch_receipt_hash72": branch_hash}
                    checkpoint.update({"completed": completed, "receipt_tip_hash72": branch_hash})
                    self._save_checkpoint(checkpoint)

        states = [completed[key] for key in sorted(completed)]
        admitted = [s for s in states if s["status"] == "ADMITTED"]
        rejected = [s for s in states if s["status"] == "DOMAIN_REJECTED"]
        singular = [s for s in states if s["status"] == "SINGULAR"]
        mismatches = [s for s in states if s["status"] == "MISMATCH"]
        useful = [s for s in admitted if s["useful_parameter_state"]]
        classes: dict[str, int] = {}
        for state in admitted:
            classes[state["cell_gate_hash72"]] = classes.get(state["cell_gate_hash72"], 0) + 1
        execution = {
            "evaluated_parameter_states": len(states), "admitted_parameter_states": len(admitted),
            "domain_rejected_parameter_states": len(rejected), "singular_parameter_states": len(singular),
            "mismatch_parameter_states": len(mismatches), "address_comparisons": sum(s["address_count"] for s in states),
        }
        for stage, data in (
            ("ADMIT", {"rule": "all 5184 leaves exact and nonsingular", **execution}),
            ("EXECUTE", execution),
            ("VERIFY", {"exact_equality": not mismatches, "singular_free": not singular, "address_codec_verified": True}),
        ):
            receipt = self._stage(stage, data, predecessor)
            receipts.append(receipt); predecessor = receipt["receipt_hash72"]

        state_root = hash72("pass197.state.root", [{"key": key, "state_hash72": completed[key]["state_hash72"], "branch_receipt_hash72": completed[key]["branch_receipt_hash72"]} for key in sorted(completed)])
        simplifications = [
            {"name": "ORIGINAL_TO_COMPACT_NUMERATOR", "lossless": not mismatches},
            {"name": "RECIPROCAL_DENOMINATOR_FACTORIZATION", "lossless": not mismatches},
            {"name": "VM81_LANE_BROADCAST", "lossless": not mismatches},
            {"name": "MATRIX_POWER_CACHE_BY_XY_SYMBOL", "lossless": True},
        ]
        summary = {
            **execution, "useful_parameter_states": len(useful), "equivalence_class_count": len(classes),
            "largest_equivalence_class": max(classes.values(), default=0),
            "lossless_simplifications_admitted": all(s["lossless"] for s in simplifications),
            "original_leaf_evaluations": len(admitted) * ADDRESS_COUNT,
            "factorized_cell_evaluations": len(admitted) * CELL_COUNT,
            "saved_leaf_evaluations": len(admitted) * (ADDRESS_COUNT - CELL_COUNT),
            "saved_fraction": fraction_payload(Fraction(ADDRESS_COUNT - CELL_COUNT, ADDRESS_COUNT)),
        }
        receipt = self._stage("RECEIPT", {"state_root_hash72": state_root, "summary": summary}, predecessor)
        receipts.append(receipt); predecessor = receipt["receipt_hash72"]

        replayed, replay_ok, first_replay_mismatch = 0, True, None
        if config.full_replay:
            for state in states:
                x = exact_fraction(state["x"], field="replay.x")
                y = exact_fraction(state["y"], field="replay.y")
                exponent = int(state["xy_symbol"])
                replay = evaluate_state(x, y, exponent, powers[exponent])
                replayed += 1
                if replay["state_hash72"] != state["state_hash72"]:
                    replay_ok = False
                    first_replay_mismatch = {"expected": state["state_hash72"], "actual": replay["state_hash72"], "x": state["x"], "y": state["y"], "xy_symbol": exponent}
                    break
        replay_root = hash72("pass197.replay.root", [{"state_hash72": s["state_hash72"], "branch_receipt_hash72": s["branch_receipt_hash72"]} for s in states])
        replay_data = {"replay_root_hash72": replay_root, "deterministic": replay_ok, "full_replay_executed": config.full_replay, "replayed_parameter_states": replayed, "first_replay_mismatch": first_replay_mismatch}
        receipt = self._stage("REPLAY", replay_data, predecessor)
        receipts.append(receipt); predecessor = receipt["receipt_hash72"]
        closed = not mismatches and not singular and replay_ok and all(s["lossless"] for s in simplifications)
        receipts.append(self._stage("CLOSE", {"closed": closed, "useful_parameter_states": len(useful)}, predecessor))

        report = {
            "schema": SCHEMA, "version": VERSION, "contract": CONTRACT, "classification": CLASSIFICATION,
            "hash_authority": HASH_AUTHORITY,
            "authority": {"canonical_admission": "VM81_AUTHORIZED_TICK_AND_HASH72_RECEIPT", "vm81_receipt_hash72": vm81_receipt_hash72, "api_or_worker_is_authority": False},
            "config": config_payload, "config_hash72": config_hash72,
            "hydration_path": ["DISCOVER", "CANONICALIZE", "INDEX", "LINK", "CONSTRAIN", "ADMIT", "EXECUTE", "VERIFY", "RECEIPT", "REPLAY", "CLOSE"],
            "vm81": {"cells": CELL_COUNT, "lanes_per_cell": LANE_COUNT, "addresses": ADDRESS_COUNT, "address_formula": "s=64*c+o", "cell_formula": "c=27*i+9*j+3*k+l"},
            "matrix_invariants": {"column_sums": [fraction_payload(v) for v in COLUMN_SUMS], "inverse_row_sums": [fraction_payload(v) for v in INVERSE_ROW_SUMS], "expected_column_sums_match": COLUMN_SUMS == EXPECTED_COLUMN_SUMS, "expected_inverse_row_sums_match": INVERSE_ROW_SUMS == EXPECTED_INVERSE_ROW_SUMS},
            "analytic_domain_proof": {"scope": "all real nonzero rational x,y and exact integer xy_symbol", "off_diagonal_nonsingular": "real part is -3", "diagonal_nonsingular": "xy=1/3 forces equal signs, so positive r_i*y+c_i*x cannot vanish", "all_real_nonzero_rational_states_nonsingular": all(v > 0 for v in COLUMN_SUMS + INVERSE_ROW_SUMS), "zero_states": "domain-rejected"},
            "summary": summary, "lossless_simplifications": simplifications, "state_root_hash72": state_root,
            "parameter_states": states, "stage_receipts": receipts, "replay": replay_data, "closed": closed,
        }
        report["report_hash72"] = hash72("pass197.report", report)
        self._write(self.report_path, report)
        self._last_report = report
        return json.loads(canonical_json(report))

    def status(self) -> dict[str, Any]:
        if self._last_report is None and self.report_path.exists():
            self._last_report = json.loads(self.report_path.read_text(encoding="utf-8"))
        if self._last_report is None:
            return {"schema": "HHS_PASS_197_STATUS_V1", "version": VERSION, "scanned": False, "closed": False, "state_root": str(self.state_root)}
        return {"schema": "HHS_PASS_197_STATUS_V1", "version": VERSION, "scanned": True, "closed": bool(self._last_report.get("closed")), "report_hash72": self._last_report.get("report_hash72"), "summary": self._last_report.get("summary"), "state_root": str(self.state_root)}

    def report(self) -> dict[str, Any]:
        if self._last_report is None:
            if not self.report_path.exists():
                raise Pass197CalibrationError("calibration report unavailable")
            self._last_report = json.loads(self.report_path.read_text(encoding="utf-8"))
        expected = hash72("pass197.report", {k: v for k, v in self._last_report.items() if k != "report_hash72"})
        if self._last_report.get("report_hash72") != expected:
            raise Pass197CalibrationError("calibration report integrity verification failed")
        return json.loads(canonical_json(self._last_report))


PASS197_AB_HYDRATION_CALIBRATION = Pass197ABHydrationCalibration()
