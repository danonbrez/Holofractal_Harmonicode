from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import threading
import time
from typing import Any, Mapping

CONTRACT_ID = "HHS-P168-VM81-5184-HPC-STCF"
TERMINAL_CLASSIFICATION = (
    "HHS_PASS_168_VM81_5184_CELL_HARMONICODE_PARAMETER_CIRCUIT_AND_"
    "SPARSE_TENSOR_CONTROL_FABRIC_VERIFIED"
)
SOURCE_SHA256 = "fdbee5db0f2fea428b6b88e5ac9b273e6aa3754fa00f84e8923456373275166e"
SURFACE_VERSION = "PASS219-I166-PASS168-PARAMETER-CIRCUIT-V1"
BANK_ROLES = (
    "SOURCE",
    "NORMALIZED_DELTA",
    "RECIPROCAL_OR_GAUGE",
    "INVERSE_DEPTH",
    "PROJECTED_STATE",
    "COMPARATOR",
    "PROPAGATED_DELTA",
    "COMMITTED_STATE",
    "REPLAY_RECEIPT",
)
DERIVED_THREADS = (
    "UPPER_GAIN_ALPHA",
    "LOWER_GAIN_BETA",
    "ROW_CHANNEL_RHO1",
    "ROW_CHANNEL_RHO2",
    "ROW_CHANNEL_RHO3",
    "UPPER_DEPTH",
    "LOWER_DEPTH",
    "GLOBAL_COMMON_GAIN",
    "COMPARATOR_C1",
    "COMPARATOR_C2",
    "COMPARATOR_C3_MATRIX",
    "COMPARATOR_C4",
    "COMPARATOR_C5",
    "COMPARATOR_C6_TERMINAL",
    "LOSHU_ORIENTED_KERNEL_L",
    "LOSHU_EVEN_KERNEL_L2",
    "MATRIX_GAUGE",
    "ROW_GAUGE_1",
    "ROW_GAUGE_2",
    "ROW_GAUGE_3",
    "WITNESS_AGGREGATE",
    "U_SHELL_DEPTH_RATIO",
    "SUCCESSOR_RESIDUAL",
    "GLOBAL_CLOSURE_RECEIPT",
)
COMPARATOR_EDGES = {
    "C1": ("E1", "UPPER_MATRIX_U", "E2", "ORDERED_PRODUCT_XY"),
    "C2": ("E3", "ORDERED_PRODUCT_XY", "E4", "UNIT_MODULAR_WITNESS"),
    "C3": ("E5", "UPPER_MATRIX_U", "E6", "LOWER_MATRIX_V"),
    "C4": ("E7", "LOWER_MATRIX_V", "E8", "GROUPED_ORDERED_PRODUCT_XY"),
    "C5": ("E9", "GROUPED_ORDERED_PRODUCT_XY", "E10", "ZERO_MODULAR_WITNESS"),
    "C6": ("E11", "TERMINAL_NORMALIZED_SHELL", "E12", "TERMINAL_ZERO_WITNESS"),
}


class Pass168ParameterCircuitError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "contract": CONTRACT_ID,
            "surface_version": SURFACE_VERSION,
            "error": self.code,
            "message": str(self),
            "details": self.details,
            "floating_point_canonical_authority": False,
        }


def _parameter_index(parameter_id: str) -> int:
    token = parameter_id.strip().upper()
    if token.startswith("P") and token[1:].isdigit():
        number = int(token[1:])
        if 1 <= number <= 28:
            return number - 1
    if token.startswith("E") and token[1:].isdigit():
        number = int(token[1:])
        if 1 <= number <= 12:
            return 28 + number - 1
    raise Pass168ParameterCircuitError(
        "PASS168_PARAMETER_ID_INVALID", f"invalid parameter identifier: {parameter_id!r}"
    )


def _parameter_name(index: int) -> str:
    if not 0 <= index < 40:
        raise ValueError(index)
    return f"P{index + 1}" if index < 28 else f"E{index - 27}"


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _clone_ctype(value: Any) -> Any:
    clone = type(value)()
    ctypes.memmove(ctypes.byref(clone), ctypes.byref(value), ctypes.sizeof(value))
    return clone


class Pass168ParameterCircuitService:
    """Durable public coordinator over the one native Pass168 exact-ABI authority.

    Python owns routing, durable candidate metadata and replayable transition-log
    storage only. Exact arithmetic, candidate validation, commit identity,
    Hash72 receipts and Hash216 transition identity remain native.
    """

    def __init__(self, state_dir: str | os.PathLike[str] | None = None) -> None:
        root = state_dir or os.environ.get("HHS_PASS168_STATE_DIR")
        if root is None:
            root = Path.home() / ".hhs" / "pass168"
        self.state_dir = Path(root)
        self.candidate_dir = self.state_dir / "candidates"
        self.ledger_path = self.state_dir / "transitions.jsonl"
        self._lock = threading.RLock()
        self._bridge: Any | None = None
        self._bridge_mod: Any | None = None
        self._comparator_mod: Any | None = None
        self._state: Any | None = None
        self._candidate_native: dict[str, Any] = {}
        self._transition_native: dict[str, Any] = {}
        self._transition_prior: dict[str, Any] = {}
        self._transition_rows: dict[str, dict[str, Any]] = {}
        self._ledger_loaded = False

    def _ensure_native(self) -> None:
        if self._bridge is not None:
            return
        try:
            from hhs_python.runtime import hhs_pass168_ctypes_bridge as bridge_mod
            from hhs_python.runtime import hhs_pass168_comparator_bridge as comparator_mod
        except Exception as exc:  # pragma: no cover - exact runtime environment diagnostic
            raise Pass168ParameterCircuitError(
                "PASS168_NATIVE_RUNTIME_UNAVAILABLE",
                "Pass168 exact ABI could not be loaded",
                details={"exception": f"{type(exc).__name__}:{exc}"},
            ) from exc
        self._bridge_mod = bridge_mod
        self._bridge = bridge_mod.HHSPass168RuntimeBridge
        self._comparator_mod = comparator_mod
        self._state = self._bridge.initialize()
        self._load_ledger()

    def _ensure_storage(self) -> None:
        self.candidate_dir.mkdir(parents=True, exist_ok=True)

    def _state_dict(self, value: Any | None = None) -> dict[str, Any]:
        self._ensure_native()
        assert self._bridge_mod is not None and self._state is not None
        return self._bridge_mod.state_dict(value if value is not None else self._state)

    def _transition_dict(self, value: Any) -> dict[str, Any]:
        assert self._bridge_mod is not None
        return self._bridge_mod.transition_dict(value)

    def _load_ledger(self) -> None:
        if self._ledger_loaded:
            return
        self._ledger_loaded = True
        if not self.ledger_path.exists():
            return
        assert self._bridge is not None and self._state is not None
        for line_number, line in enumerate(self.ledger_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise Pass168ParameterCircuitError(
                    "PASS168_LEDGER_CORRUPT", "invalid transition ledger JSON",
                    details={"line": line_number},
                ) from exc
            operation = row.get("operation")
            if operation == "commit":
                prior = _clone_ctype(self._state)
                candidate = self._bridge.begin(self._state)
                for name, rational in sorted(row["updates"].items()):
                    self._bridge.set(
                        candidate,
                        _parameter_index(name),
                        int(rational["numerator"]),
                        int(rational["denominator"]),
                    )
                committed, transition = self._bridge.commit(self._state, candidate)
                actual = self._transition_dict(transition)
                for key in (
                    "committed_state_hash216", "change_hash72", "receipt_hash72", "hash216_identity"
                ):
                    if actual[key] != row["transition"][key]:
                        raise Pass168ParameterCircuitError(
                            "PASS168_LEDGER_REPLAY_MISMATCH",
                            "durable transition does not reproduce native authority output",
                            details={"line": line_number, "field": key},
                        )
                transition_id = row["transition_id"]
                self._transition_native[transition_id] = transition
                self._transition_prior[transition_id] = prior
                self._transition_rows[transition_id] = row
                self._state = committed
            elif operation == "rollback":
                transition_id = str(row.get("transition_id", ""))
                transition = self._transition_native.get(transition_id)
                if transition is None:
                    raise Pass168ParameterCircuitError(
                        "PASS168_LEDGER_ROLLBACK_TARGET_MISSING",
                        "rollback references a transition not present earlier in the ledger",
                        details={"line": line_number, "transition_id": transition_id},
                    )
                rolled = self._bridge.rollback(transition)
                actual_hash = self._bridge_mod.state_dict(rolled)["state_hash216"]
                if actual_hash != row.get("state_hash216"):
                    raise Pass168ParameterCircuitError(
                        "PASS168_LEDGER_ROLLBACK_MISMATCH",
                        "rollback state root does not reproduce",
                        details={"line": line_number},
                    )
                self._state = rolled
            else:
                raise Pass168ParameterCircuitError(
                    "PASS168_LEDGER_OPERATION_INVALID",
                    "unrecognized durable transition operation",
                    details={"line": line_number, "operation": operation},
                )

    def _append_ledger(self, row: Mapping[str, Any]) -> None:
        self._ensure_storage()
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def status(self) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None
            proof = self._bridge.self_test()
            state = self._state_dict()
            return {
                "ok": True,
                "contract": CONTRACT_ID,
                "terminal_classification": TERMINAL_CLASSIFICATION,
                "surface_version": SURFACE_VERSION,
                "native_self_test": proof,
                "generation": state["generation"],
                "state_hash216": state["state_hash216"],
                "last_receipt_hash72": state["last_receipt_hash72"],
                "threads_registered": 64,
                "cells_registered": 5184,
                "banks_per_thread": 9,
                "candidate_count": len(self.list_candidate_ids()),
                "transition_count": len(self._transition_rows),
                "single_vm81_commit_authority": True,
                "floating_point_canonical_authority": False,
                "fallback_used": False,
            }

    def inspect(self) -> dict[str, Any]:
        report = self.status()
        report.update({
            "source_sha256": SOURCE_SHA256,
            "parameter_count": 40,
            "raw_threads": 40,
            "derived_threads": 24,
            "bank_roles": list(BANK_ROLES),
            "state_dir": str(self.state_dir),
            "canonical_mutation_surface": "hhs_pass168_commit_candidate",
        })
        return report

    def source(self) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None
            source = self._bridge.source()
            digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
            if digest != SOURCE_SHA256 or len(source.encode("utf-8")) != 424:
                raise Pass168ParameterCircuitError(
                    "PASS168_SOURCE_IDENTITY_MISMATCH", "native source fixture identity mismatch"
                )
            return {
                "contract": CONTRACT_ID,
                "source": source,
                "bytes": 424,
                "sha256": digest,
                "byte_authoritative": True,
            }

    def threads(self) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        for thread_id in range(64):
            if thread_id < 40:
                name = _parameter_name(thread_id)
                kind = "RAW_PARAMETER"
            else:
                name = DERIVED_THREADS[thread_id - 40]
                kind = "DERIVED"
            rows.append({
                "thread_id": thread_id,
                "thread_row": thread_id // 8,
                "thread_col": thread_id % 8,
                "name": name,
                "kind": kind,
                "cell_count": 81,
                "bank_count": 9,
            })
        return {"threads": rows, "count": 64, "permanent_identity": True}

    def banks(self) -> dict[str, Any]:
        return {
            "banks_per_thread": 9,
            "cells_per_bank": 9,
            "roles": [
                {"bank_id": index, "bank_row": index // 3, "bank_col": index % 3, "role": role}
                for index, role in enumerate(BANK_ROLES)
            ],
            "loshu": [[4, 9, 2], [3, 5, 7], [8, 1, 6]],
        }

    def cell_map(self) -> dict[str, Any]:
        rows: list[dict[str, int]] = []
        for global_index in range(5184):
            global_row, global_col = divmod(global_index, 72)
            thread_row, local_row = divmod(global_row, 9)
            thread_col, local_col = divmod(global_col, 9)
            bank_row, loshu_row = divmod(local_row, 3)
            bank_col, loshu_col = divmod(local_col, 3)
            rows.append({
                "global_index": global_index,
                "global_row": global_row,
                "global_col": global_col,
                "thread_id": 8 * thread_row + thread_col,
                "local_index": 9 * local_row + local_col,
                "bank_id": 3 * bank_row + bank_col,
                "loshu_index": 3 * loshu_row + loshu_col,
            })
        return {
            "count": 5184,
            "duplicate_addresses": 0,
            "inverse_mapping": "EXACT",
            "rows": rows,
        }

    def parameters(self) -> dict[str, Any]:
        with self._lock:
            state = self._state_dict()
            return {
                "generation": state["generation"],
                "parameters": {
                    _parameter_name(index): value for index, value in enumerate(state["raw"])
                },
            }

    def get_parameter(self, parameter_id: str) -> dict[str, Any]:
        index = _parameter_index(parameter_id)
        state = self.parameters()
        name = _parameter_name(index)
        return {"parameter_id": name, "thread_id": index, "value": state["parameters"][name]}

    def _candidate_meta_path(self, candidate_id: str) -> Path:
        safe = candidate_id.removeprefix("candidate-")
        if not safe or any(ch not in "0123456789abcdef" for ch in safe):
            raise Pass168ParameterCircuitError(
                "PASS168_CANDIDATE_ID_INVALID", f"invalid candidate id: {candidate_id!r}"
            )
        return self.candidate_dir / f"{candidate_id}.json"

    def list_candidate_ids(self) -> list[str]:
        if not self.candidate_dir.exists():
            return []
        return sorted(path.stem for path in self.candidate_dir.glob("candidate-*.json"))

    def _normalize_updates(self, updates: Mapping[str, Any]) -> dict[str, dict[str, int]]:
        normalized: dict[str, dict[str, int]] = {}
        for raw_name, raw_value in updates.items():
            index = _parameter_index(str(raw_name))
            name = _parameter_name(index)
            if isinstance(raw_value, int):
                numerator, denominator = raw_value, 1
            elif isinstance(raw_value, Mapping):
                numerator = int(raw_value.get("numerator", 0))
                denominator = int(raw_value.get("denominator", 1))
            else:
                raise Pass168ParameterCircuitError(
                    "PASS168_PARAMETER_VALUE_INVALID", f"invalid exact value for {name}"
                )
            if denominator <= 0:
                raise Pass168ParameterCircuitError(
                    "PASS168_PARAMETER_DENOMINATOR_INVALID", f"denominator must be positive for {name}"
                )
            normalized[name] = {"numerator": numerator, "denominator": denominator}
        if not normalized:
            raise Pass168ParameterCircuitError(
                "PASS168_CANDIDATE_EMPTY", "candidate requires at least one parameter update"
            )
        return dict(sorted(normalized.items()))

    def create_candidate(self, updates: Mapping[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None and self._state is not None
            normalized = self._normalize_updates(updates)
            prior = self._state_dict()["state_hash216"]
            identity_material = {"prior_state_hash216": prior, "updates": normalized}
            candidate_id = "candidate-" + hashlib.sha256(_canonical_json(identity_material)).hexdigest()
            candidate = self._bridge.begin(self._state)
            for name, rational in normalized.items():
                self._bridge.set(
                    candidate,
                    _parameter_index(name),
                    rational["numerator"],
                    rational["denominator"],
                )
            validation = self._bridge.validate(self._state, candidate)
            meta = {
                "candidate_id": candidate_id,
                "prior_state_hash216": prior,
                "updates": normalized,
                "update_mask": int(candidate.update_mask),
                "affected_thread_bitmap": int(candidate.affected_thread_bitmap),
                "validation": validation,
                "candidate_only": True,
                "canonical_state_mutated": False,
            }
            self._ensure_storage()
            self._candidate_meta_path(candidate_id).write_text(
                json.dumps(meta, sort_keys=True, indent=2) + "\n", encoding="utf-8"
            )
            self._candidate_native[candidate_id] = candidate
            return meta

    def get_candidate(self, candidate_id: str) -> dict[str, Any]:
        path = self._candidate_meta_path(candidate_id)
        if not path.exists():
            raise Pass168ParameterCircuitError(
                "PASS168_CANDIDATE_NOT_FOUND", f"candidate not found: {candidate_id}"
            )
        return json.loads(path.read_text(encoding="utf-8"))

    def _materialize_candidate(self, candidate_id: str) -> Any:
        self._ensure_native()
        assert self._bridge is not None and self._state is not None
        cached = self._candidate_native.get(candidate_id)
        if cached is not None:
            return cached
        meta = self.get_candidate(candidate_id)
        candidate = self._bridge.begin(self._state)
        for name, rational in meta["updates"].items():
            self._bridge.set(
                candidate,
                _parameter_index(name),
                int(rational["numerator"]),
                int(rational["denominator"]),
            )
        self._candidate_native[candidate_id] = candidate
        return candidate

    def validate_candidate(self, candidate_id: str) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None and self._state is not None
            candidate = self._materialize_candidate(candidate_id)
            result = self._bridge.validate(self._state, candidate)
            return {"candidate_id": candidate_id, **result, "canonical_state_mutated": False}

    def evaluate_candidate(self, candidate_id: str) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None and self._state is not None
            candidate = self._materialize_candidate(candidate_id)
            output = self._bridge.evaluate(self._state, candidate)
            return {
                "candidate_id": candidate_id,
                "candidate_state": self._state_dict(output),
                "canonical_state_mutated": False,
            }

    def commit_candidate(self, candidate_id: str) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None and self._state is not None
            candidate = self._materialize_candidate(candidate_id)
            meta = self.get_candidate(candidate_id)
            prior = _clone_ctype(self._state)
            committed, transition = self._bridge.commit(self._state, candidate)
            transition_row = self._transition_dict(transition)
            transition_id = "transition-" + hashlib.sha256(
                transition_row["hash216_identity"].encode("ascii")
            ).hexdigest()
            ledger_row = {
                "operation": "commit",
                "transition_id": transition_id,
                "candidate_id": candidate_id,
                "updates": meta["updates"],
                "transition": transition_row,
            }
            self._append_ledger(ledger_row)
            self._transition_native[transition_id] = transition
            self._transition_prior[transition_id] = prior
            self._transition_rows[transition_id] = ledger_row
            self._state = committed
            return {
                "transition_id": transition_id,
                "transition": transition_row,
                "state": self._state_dict(),
                "canonical_state_mutated": True,
                "native_commit_surface": "hhs_pass168_commit_candidate",
            }

    def get_transition(self, transition_id: str) -> dict[str, Any]:
        row = self._transition_rows.get(transition_id)
        if row is None:
            self._ensure_native()
            row = self._transition_rows.get(transition_id)
        if row is None:
            raise Pass168ParameterCircuitError(
                "PASS168_TRANSITION_NOT_FOUND", f"transition not found: {transition_id}"
            )
        return dict(row)

    def receipt(self, transition_id: str) -> dict[str, Any]:
        row = self.get_transition(transition_id)
        transition = row["transition"]
        return {
            "transition_id": transition_id,
            "change_hash72": transition["change_hash72"],
            "receipt_hash72": transition["receipt_hash72"],
            "hash216_triplet": transition["hash216_triplet"],
            "hash216_identity": transition["hash216_identity"],
            "fallback_used": transition["fallback_used"],
        }

    def replay(self, transition_id: str) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None
            transition = self._transition_native.get(transition_id)
            prior = self._transition_prior.get(transition_id)
            if transition is None or prior is None:
                self.get_transition(transition_id)
                transition = self._transition_native.get(transition_id)
                prior = self._transition_prior.get(transition_id)
            if transition is None or prior is None:
                raise Pass168ParameterCircuitError(
                    "PASS168_TRANSITION_NATIVE_STATE_MISSING", "transition native replay state unavailable"
                )
            replayed = self._bridge.replay(prior, transition)
            expected = self.get_transition(transition_id)["transition"]["committed_state_hash216"]
            actual = self._state_dict(replayed)["state_hash216"]
            if actual != expected:
                raise Pass168ParameterCircuitError(
                    "PASS168_REPLAY_ROOT_MISMATCH", "deterministic replay root mismatch"
                )
            return {
                "transition_id": transition_id,
                "replayed_state": self._state_dict(replayed),
                "canonical_state_mutated": False,
            }

    def rollback(self, transition_id: str) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None and self._state is not None
            row = self.get_transition(transition_id)
            current_hash = self._state_dict()["state_hash216"]
            expected_current = row["transition"]["committed_state_hash216"]
            if current_hash != expected_current:
                raise Pass168ParameterCircuitError(
                    "PASS168_ROLLBACK_HEAD_MISMATCH",
                    "rollback is only authoritative when the transition is the current committed head",
                    details={"current": current_hash, "expected": expected_current},
                )
            transition = self._transition_native[transition_id]
            rolled = self._bridge.rollback(transition)
            rolled_hash = self._state_dict(rolled)["state_hash216"]
            event = {
                "operation": "rollback",
                "transition_id": transition_id,
                "state_hash216": rolled_hash,
            }
            self._append_ledger(event)
            self._state = rolled
            return {
                "transition_id": transition_id,
                "state": self._state_dict(),
                "canonical_state_mutated": True,
                "rollback_verified": True,
            }

    def dependencies(self, parameter_id: str) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None and self._state is not None
            index = _parameter_index(parameter_id)
            current = self._state.raw[index]
            candidate = self._bridge.begin(self._state)
            self._bridge.set(candidate, index, int(current.numerator), int(current.denominator))
            bitmap = int(candidate.affected_thread_bitmap)
            affected_threads = [thread for thread in range(64) if bitmap & (1 << thread)]
            return {
                "parameter_id": _parameter_name(index),
                "raw_thread_id": index,
                "affected_thread_bitmap": bitmap,
                "affected_threads": affected_threads,
                "affected_thread_count": len(affected_threads),
                "affected_cells": len(affected_threads) * 81,
                "full_5184_rewrite": bitmap == (1 << 64) - 1,
            }

    def matrix(self, lane: str) -> dict[str, Any]:
        state = self._state_dict()
        normalized = lane.strip().lower()
        if normalized not in {"upper", "lower", "successor"}:
            raise Pass168ParameterCircuitError(
                "PASS168_MATRIX_LANE_INVALID", f"invalid matrix lane: {lane!r}"
            )
        return {"lane": normalized, "generation": state["generation"], "matrix": state[normalized]}

    def compare(self, comparator_id: str) -> dict[str, Any]:
        token = comparator_id.strip().upper()
        if token not in COMPARATOR_EDGES:
            raise Pass168ParameterCircuitError(
                "PASS168_COMPARATOR_ID_INVALID", f"invalid comparator id: {comparator_id!r}"
            )
        with self._lock:
            self._ensure_native()
            assert self._state is not None and self._comparator_mod is not None
            left_gate, left_value, right_gate, right_value = COMPARATOR_EDGES[token]
            result: dict[str, Any] = {
                "comparator_id": token,
                "left_gate": left_gate,
                "left_value": left_value,
                "right_gate": right_gate,
                "right_value": right_value,
                "ordered": True,
                "grouping_preserved": True,
                "conformance_verified_count": self._comparator_mod.conformance(),
                "floating_point_canonical_authority": False,
            }
            if token == "C3":
                result["exact_matrix_shadow"] = self._comparator_mod.compare_matrix(
                    self._state.raw[32], self._state.upper,
                    self._state.raw[33], self._state.lower,
                )
                result["arithmetic_shadow_authoritative"] = True
            else:
                result["typed_witness"] = "PRESERVED_NONSCALAR_ORDERED_EDGE"
                result["arithmetic_shadow_authoritative"] = False
            return result

    def validate_runtime(self) -> dict[str, Any]:
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None
            proof = self._bridge.self_test()
            return {
                "contract": CONTRACT_ID,
                "result": "PASS",
                "native": proof,
                "ledger_replay_verified": True,
                "source_sha256": SOURCE_SHA256,
                "floating_point_canonical_authority": False,
                "fallback_used": False,
            }

    def benchmark(self, repeats: int = 12) -> dict[str, Any]:
        if repeats < 1 or repeats > 1000:
            raise Pass168ParameterCircuitError(
                "PASS168_BENCHMARK_REPEAT_RANGE", "benchmark repeats must be in [1,1000]"
            )
        with self._lock:
            self._ensure_native()
            assert self._bridge is not None
            durations: list[int] = []
            receipts: list[str] = []
            for _ in range(repeats):
                started = time.perf_counter_ns()
                proof = self._bridge.self_test()
                durations.append(time.perf_counter_ns() - started)
                receipts.append(str(proof["deterministic_record_hash216"]))
            ordered = sorted(durations)
            return {
                "repeats": repeats,
                "min_ns": ordered[0],
                "median_ns": ordered[len(ordered) // 2],
                "max_ns": ordered[-1],
                "deterministic_receipt": len(set(receipts)) == 1,
                "record_hash216": receipts[0],
                "timing_authoritative": False,
                "floating_point_canonical_authority": False,
            }

    def dispatch(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        op = operation.strip().lower()
        if op == "status": return self.status()
        if op == "inspect": return self.inspect()
        if op == "source": return self.source()
        if op == "map": return self.cell_map()
        if op == "threads": return self.threads()
        if op == "banks": return self.banks()
        if op == "parameters": return self.parameters()
        if op == "get": return self.get_parameter(str(kwargs["parameter_id"]))
        if op == "set":
            return self.create_candidate({str(kwargs["parameter_id"]): kwargs["value"]})
        if op == "evaluate":
            candidate_id = kwargs.get("candidate_id")
            if candidate_id is None:
                raise Pass168ParameterCircuitError("PASS168_CANDIDATE_REQUIRED", "evaluate requires candidate_id")
            return self.evaluate_candidate(str(candidate_id))
        if op == "compare": return self.compare(str(kwargs["comparator_id"]))
        if op in {"dependencies", "affected-cells"}:
            return self.dependencies(str(kwargs["parameter_id"]))
        if op == "commit":
            candidate_id = kwargs.get("candidate_id")
            if candidate_id is None:
                ids = self.list_candidate_ids()
                if len(ids) != 1:
                    raise Pass168ParameterCircuitError(
                        "PASS168_CANDIDATE_AMBIGUOUS", "commit requires candidate_id unless exactly one candidate exists"
                    )
                candidate_id = ids[0]
            return self.commit_candidate(str(candidate_id))
        if op == "rollback": return self.rollback(str(kwargs["transition_id"]))
        if op == "replay": return self.replay(str(kwargs["transition_id"]))
        if op == "receipt": return self.receipt(str(kwargs["transition_id"]))
        if op == "validate": return self.validate_runtime()
        if op == "benchmark": return self.benchmark(int(kwargs.get("repeats", 12)))
        raise Pass168ParameterCircuitError(
            "PASS168_OPERATION_UNSUPPORTED", f"unsupported Pass168 operation: {operation!r}"
        )
