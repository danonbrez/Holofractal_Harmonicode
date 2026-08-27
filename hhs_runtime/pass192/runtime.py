"""Pass 192 exact cellular Fibonacci tensor runtime.

This module completes the dedicated Pass 192 runtime required by
HHS-P192-LSCFNT-MMD-VM81-H72-H216 while preserving the later Pass 219 1.9
lossless Fibonacci compression ABI as an inherited optimization.

Canonical values are exact integers, exact rational pairs, ordered source
witnesses, and membrane records. Floating point is not used as canonical
authority. Any persistent mutation requires a successful receipt from the
inherited singleton VM81 authority path.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import json
import os
from pathlib import Path
from typing import Any, Mapping, Optional
import unicodedata

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import _validated_authorized_tick
from hhs_runtime.pass219_fibonacci_compression_reference_v1 import (
    MAGNITUDES,
    OUTER_HYDRATION_MODULUS,
    PASS192_MAX_DEPTH,
    build_witness,
    fibonacci_prefix,
)

CONTRACT_ID = "HHS-P192-LSCFNT-MMD-VM81-H72-H216"
VERSION = CONTRACT_ID + "-1.0.0"
CONTRACT_AUTHORIZATION_COMMIT = "c3da7e2b7125754b65f08fb8922a151bf01df2b8"
FROZEN_I133 = "8380d2dbc9cf1b0245f006eaa440b47a921d4901"

CANONICAL_SOURCE = (
    "List(List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5),"
    "(2*List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5)),"
    "(3*List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5)),"
    "(5*List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5)),"
    "(8*List(1==1,1+1==2,1+2==3,1+3==4==2+2==2^2,2+3==5)))"
)
SEED_WITNESSES = (
    "1==1",
    "1+1==2",
    "1+2==3",
    "1+3==4==2+2==2^2",
    "2+3==5",
)
LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))

OPERATION_IDS = {
    "sequence": "P192.FibonacciSequence",
    "ratio": "P192.FibonacciRatio",
    "scale": "P192.CumulativeFibonacciScale",
    "cell": "P192.LoShuCell",
    "create": "P192.CellularFibonacciTensor",
    "materialize": "P192.MaterializeTensorPrefix",
    "membrane": "P192.MembraneWitness",
    "validate": "P192.ValidateTensor",
    "replay": "P192.ReplayTensor",
}

DEFAULT_RUNTIME_ROOT = Path(".hhs_runtime_state") / "pass192"
DEFAULT_MAX_DEPTH = 64
DEFAULT_MAX_NODES = 4096
DEFAULT_MAX_SERIALIZED_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_MEMORY_BYTES = 16 * 1024 * 1024
DEFAULT_MAX_STEPS = 16384
DEFAULT_WORKSPACE_QUOTA = 64 * 1024 * 1024


class Pass192Error(RuntimeError):
    """Fail-closed Pass 192 runtime error."""

    def __init__(self, classification: str, detail: str = "") -> None:
        super().__init__(classification if not detail else f"{classification}: {detail}")
        self.classification = classification
        self.detail = detail


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash72(domain: str, payload: Any) -> str:
    return hash72_digest({"domain": domain, "contract": CONTRACT_ID}, payload)


def _hash216(domain: str, payload: Any) -> str:
    previous = _hash72(domain + ":PREVIOUS", {"genesis": CONTRACT_AUTHORIZATION_COMMIT})
    change = _hash72(domain + ":CHANGE", payload)
    receipt = _hash72(domain + ":RECEIPT", {"previous": previous, "change": change})
    value = previous + change + receipt
    if len(value) != 216:
        raise AssertionError("Hash216 must contain exactly three Hash72 witnesses")
    return value


def _authority_lineage(execution: Mapping[str, Any]) -> tuple[str, str]:
    try:
        validated = _validated_authorized_tick(execution)
    except Exception as exc:
        raise Pass192Error("HHS_P192_VM81_AUTHORITY_REQUIRED") from exc
    receipt = validated["receipt"]
    state_hash72 = receipt["state_hash72"]
    receipt_hash72 = receipt["receipt_hash72"]
    if not validate_hash72(state_hash72) or not validate_hash72(receipt_hash72):
        raise Pass192Error("HHS_P192_VM81_AUTHORITY_HASH72_INVALID")
    return state_hash72, receipt_hash72


def source_invariants() -> dict[str, bool]:
    flattened = [value for row in LO_SHU for value in row]
    line_sums = (
        [sum(row) for row in LO_SHU]
        + [sum(LO_SHU[r][c] for r in range(3)) for c in range(3)]
        + [sum(LO_SHU[i][i] for i in range(3)), sum(LO_SHU[i][2 - i] for i in range(3))]
    )
    return {
        "canonical_source_is_nfc": unicodedata.normalize("NFC", CANONICAL_SOURCE) == CANONICAL_SOURCE,
        "list_boundaries_preserved": CANONICAL_SOURCE.count("List(") == 6,
        "equality_chain_preserved": "1+3==4==2+2==2^2" in CANONICAL_SOURCE,
        "seed_witnesses_preserved": all(CANONICAL_SOURCE.count(witness) == 5 for witness in SEED_WITNESSES),
        "magnitude_order_preserved": tuple(MAGNITUDES) == (1, 2, 3, 5, 8),
        "lo_shu_contains_1_to_9": sorted(flattened) == list(range(1, 10)),
        "lo_shu_all_lines_sum_15": all(value == 15 for value in line_sums),
        "outer_modulus_preserved": OUTER_HYDRATION_MODULUS == 1_259_713,
    }


def fibonacci_sequence(index: int) -> int:
    if not isinstance(index, int) or isinstance(index, bool) or index < 0 or index > PASS192_MAX_DEPTH + 1:
        raise Pass192Error("HHS_P192_DEPTH_INVALID")
    return fibonacci_prefix(index)[index]


def fibonacci_ratio(depth: int) -> Fraction:
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0 or depth > PASS192_MAX_DEPTH:
        raise Pass192Error("HHS_P192_DEPTH_INVALID")
    witness = build_witness(depth)
    return Fraction(witness.f_depth, witness.f_next)


def cumulative_fibonacci_scale(depth: int) -> Fraction:
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0 or depth > PASS192_MAX_DEPTH:
        raise Pass192Error("HHS_P192_DEPTH_INVALID")
    witness = build_witness(depth)
    return Fraction(1, witness.f_depth)


def membrane_witness(
    depth: int,
    *,
    parent_membrane_id: Optional[str],
    tensor_id: str,
) -> dict[str, Any]:
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0 or depth > PASS192_MAX_DEPTH:
        raise Pass192Error("HHS_P192_DEPTH_INVALID")
    payload = {
        "parent_membrane_id": parent_membrane_id,
        "depth": depth,
        "modulus": depth + 1,
        "residue": depth,
        "source_span": [0, len(CANONICAL_SOURCE)],
        "interior_identity": _hash216(
            "HHS-P192-MEMBRANE-INTERIOR",
            {"tensor_id": tensor_id, "depth": depth, "source": CANONICAL_SOURCE},
        ),
        "boundary_policy": "NON_DESTRUCTIVE_DEPTH_MODULUS_METADATA",
        "outer_modulus_applied_locally": False,
    }
    payload["membrane_id"] = _hash216("HHS-P192-MEMBRANE", payload)
    payload["hash216_identity"] = payload["membrane_id"]
    return payload


@dataclass(frozen=True)
class MaterializationBounds:
    max_depth: int = DEFAULT_MAX_DEPTH
    max_nodes: int = DEFAULT_MAX_NODES
    max_serialized_bytes: int = DEFAULT_MAX_SERIALIZED_BYTES
    max_memory_bytes: int = DEFAULT_MAX_MEMORY_BYTES
    max_steps: int = DEFAULT_MAX_STEPS
    timeout_policy: str = "CALLER_ENFORCED_DETERMINISTIC_STEP_BOUND"
    cancellation_policy: str = "EXPLICIT_CANCEL_FLAG"
    workspace_quota: int = DEFAULT_WORKSPACE_QUOTA
    capability_scope: tuple[str, ...] = (
        "P192.CREATE",
        "P192.MATERIALIZE",
        "P192.VALIDATE",
        "P192.REPLAY",
    )

    def validate(self) -> "MaterializationBounds":
        numeric = {
            "max_depth": self.max_depth,
            "max_nodes": self.max_nodes,
            "max_serialized_bytes": self.max_serialized_bytes,
            "max_memory_bytes": self.max_memory_bytes,
            "max_steps": self.max_steps,
            "workspace_quota": self.workspace_quota,
        }
        for name, value in numeric.items():
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise Pass192Error("HHS_P192_BOUNDS_INVALID", name)
        if self.max_depth > PASS192_MAX_DEPTH:
            raise Pass192Error("HHS_P192_BOUNDS_DEPTH_EXCEEDS_CANONICAL_MAX")
        if not self.timeout_policy or not self.cancellation_policy:
            raise Pass192Error("HHS_P192_BOUNDS_POLICY_REQUIRED")
        if not self.capability_scope:
            raise Pass192Error("HHS_P192_CAPABILITY_SCOPE_REQUIRED")
        return self

    @classmethod
    def from_mapping(cls, value: Optional[Mapping[str, Any]]) -> "MaterializationBounds":
        if value is None:
            return cls().validate()
        permitted = set(cls.__dataclass_fields__.keys())
        unknown = sorted(set(value.keys()) - permitted)
        if unknown:
            raise Pass192Error("HHS_P192_BOUNDS_UNKNOWN_FIELD", ",".join(unknown))
        data = dict(value)
        if "capability_scope" in data:
            data["capability_scope"] = tuple(str(x) for x in data["capability_scope"])
        return cls(**data).validate()


class Pass192Runtime:
    """Persistent exact Pass 192 tensor registry."""

    def __init__(self, root: Path | str = DEFAULT_RUNTIME_ROOT) -> None:
        self.root = Path(root)
        self.tensor_root = self.root / "tensors"
        self.materialization_root = self.root / "materializations"
        self.receipt_path = self.root / "receipts.jsonl"
        self.index_path = self.root / "index.json"
        self.tensor_root.mkdir(parents=True, exist_ok=True)
        self.materialization_root.mkdir(parents=True, exist_ok=True)
        if not self.index_path.exists():
            self._write_json(
                self.index_path,
                {
                    "schema": "HHS_PASS192_CELLULAR_FIBONACCI_REGISTRY_V1",
                    "tensors": {},
                    "materializations": {},
                },
            )

    @staticmethod
    def operation_registry() -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_192_OPERATION_REGISTRY_V1",
            "contract": CONTRACT_ID,
            "operation_ids": dict(OPERATION_IDS),
            "vm81_singleton_required_for_mutation": True,
            "hash72_receipts": True,
            "hash216_identity": True,
            "pass219_1_9_compression_inherited": True,
        }

    def status(self) -> dict[str, Any]:
        index = self._read_index()
        return {
            "contract": CONTRACT_ID,
            "version": VERSION,
            "frozen_predecessor_i133": FROZEN_I133,
            "canonical_arithmetic": "EXACT_INTEGER_RATIONAL_ORDERED_SOURCE",
            "float_canonical_authority": False,
            "unbounded_declarative_depth": True,
            "finite_materialization_required": True,
            "outer_hydration_modulus": OUTER_HYDRATION_MODULUS,
            "vm81_singleton_required_for_mutation": True,
            "hash72_receipts": True,
            "hash216_identity": True,
            "pass219_1_9_compression_inherited": True,
            "tensors": len(index["tensors"]),
            "materializations": len(index["materializations"]),
            "operation_registry": self.operation_registry(),
        }

    def lo_shu_cell(self, row: int, column: int) -> dict[str, Any]:
        self._validate_cell(row, column)
        value = LO_SHU[row][column]
        payload = {
            "row": row,
            "column": column,
            "value": value,
            "lo_shu_parent_identity": _hash216("HHS-P192-LO-SHU", {"tensor": LO_SHU}),
            "row_membership": list(LO_SHU[row]),
            "column_membership": [LO_SHU[r][column] for r in range(3)],
            "diagonal_membership": {"main": row == column, "anti": row + column == 2},
        }
        payload["hash216_identity"] = _hash216("HHS-P192-LO-SHU-CELL", payload)
        return payload

    def create_tensor(
        self,
        row: int,
        column: int,
        *,
        materialization_bounds: Optional[Mapping[str, Any]] = None,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        if not all(source_invariants().values()):
            raise Pass192Error("HHS_P192_SOURCE_INVARIANTS_FAILED")
        bounds = MaterializationBounds.from_mapping(materialization_bounds)
        cell = self.lo_shu_cell(row, column)
        seed = {
            "contract_version": "1.0.0",
            "source_identity": _hash216("HHS-P192-SOURCE", {"source": CANONICAL_SOURCE}),
            "canonical_source": CANONICAL_SOURCE,
            "lo_shu_parent_identity": cell["lo_shu_parent_identity"],
            "lo_shu_cell_coordinate": [row, column],
            "lo_shu_cell_value": cell["value"],
            "magnitude_rows": list(MAGNITUDES),
            "seed_columns": list(SEED_WITNESSES),
            "unbounded_declarative_depth": True,
            "outer_hydration_modulus": OUTER_HYDRATION_MODULUS,
            "outer_modulus_applied_locally": False,
            "materialization_bounds": self._bounds_dict(bounds),
            "capabilities": list(bounds.capability_scope),
            "local_constraints": [
                "NO_FLOAT_CANONICAL_AUTHORITY",
                "FINITE_REQUESTED_PREFIX_REQUIRED",
                "OUTER_MODULUS_NON_DESTRUCTIVE_LOCAL",
                "PARENT_ROOT_MEMBRANE_IDENTITY_PRESERVED",
            ],
            "hash72_receipt_policy": "REQUIRED_FOR_PERSISTENT_MUTATION",
            "replay_supported": True,
            "implementation_status": "CANONICAL_EXACT_CELLULAR_FIBONACCI_TENSOR",
        }
        tensor_id = _hash216("HHS-P192-TENSOR", seed)
        manifest = {
            "tensor_id": tensor_id,
            "root_id": tensor_id,
            "parent_id": None,
            "child_slot": None,
            "nesting_depth": 0,
            **seed,
            "hash216_identity": tensor_id,
        }
        path = self._record_path(self.tensor_root, tensor_id)
        if path.exists():
            return json.loads(path.read_text("utf-8"))
        receipt = self._append_receipt("P192.CellularFibonacciTensor", tensor_id, manifest, authority_execution)
        manifest["last_receipt_hash72"] = receipt["receipt_hash72"]
        self._write_json(path, manifest)
        index = self._read_index()
        index["tensors"][tensor_id] = path.name
        self._write_index(index)
        return manifest

    def get_tensor(self, tensor_id: str) -> dict[str, Any]:
        path = self._record_path(self.tensor_root, tensor_id)
        if not path.exists():
            raise Pass192Error("HHS_P192_TENSOR_NOT_FOUND")
        return json.loads(path.read_text("utf-8"))

    def materialize_prefix(
        self,
        tensor_id: str,
        depth: int,
        *,
        materialization_bounds: Optional[Mapping[str, Any]] = None,
        cancelled: bool = False,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        tensor = self.get_tensor(tensor_id)
        if cancelled:
            raise Pass192Error("HHS_P192_MATERIALIZATION_CANCELLED")
        if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0 or depth > PASS192_MAX_DEPTH:
            raise Pass192Error("HHS_P192_DEPTH_INVALID")
        inherited_bounds = MaterializationBounds.from_mapping(tensor["materialization_bounds"])
        bounds = (
            MaterializationBounds.from_mapping(materialization_bounds)
            if materialization_bounds is not None
            else inherited_bounds
        )
        if depth > bounds.max_depth:
            raise Pass192Error("HHS_P192_REQUESTED_DEPTH_EXCEEDS_BOUND")

        node_count = len(MAGNITUDES) * len(SEED_WITNESSES) * (depth + 1)
        if node_count > bounds.max_nodes:
            raise Pass192Error("HHS_P192_NODE_BOUND_EXCEEDED")
        if node_count > bounds.max_steps:
            raise Pass192Error("HHS_P192_STEP_BOUND_EXCEEDED")

        nodes: list[dict[str, Any]] = []
        for magnitude_index, magnitude in enumerate(MAGNITUDES):
            for seed_index, seed_witness in enumerate(SEED_WITNESSES):
                parent_id: Optional[str] = tensor_id
                inherited_membranes: list[str] = []
                parent_membrane_id: Optional[str] = None
                for current_depth in range(depth + 1):
                    witness = build_witness(current_depth)
                    membrane = membrane_witness(
                        current_depth,
                        parent_membrane_id=parent_membrane_id,
                        tensor_id=tensor_id,
                    )
                    node_seed = {
                        "contract_version": "1.0.0",
                        "source_identity": tensor["source_identity"],
                        "lo_shu_parent_identity": tensor["lo_shu_parent_identity"],
                        "lo_shu_cell_coordinate": tensor["lo_shu_cell_coordinate"],
                        "lo_shu_cell_value": tensor["lo_shu_cell_value"],
                        "magnitude_row_index": magnitude_index,
                        "magnitude_multiplier": magnitude,
                        "seed_column_index": seed_index,
                        "seed_witness_identity": seed_witness,
                        "nesting_depth": current_depth,
                        "parent_id": parent_id,
                        "root_id": tensor_id,
                        "child_slot": current_depth,
                        "ratio_numerator": witness.f_depth,
                        "ratio_denominator": witness.f_next,
                        "cumulative_scale_numerator": 1,
                        "cumulative_scale_denominator": witness.f_depth,
                        "membrane_witness": membrane,
                        "inherited_membrane_ids": list(inherited_membranes),
                        "local_constraints": tensor["local_constraints"],
                        "capabilities": tensor["capabilities"],
                        "materialization_bounds": self._bounds_dict(bounds),
                        "hash72_receipt_policy": "MATERIALIZATION_RECEIPT_BINDS_BATCH",
                        "replay_supported": True,
                        "implementation_status": "CANONICAL_EXACT_MATERIALIZED_TENSOR_NODE",
                    }
                    node_id = _hash216("HHS-P192-TENSOR-NODE", node_seed)
                    node = {"tensor_id": node_id, **node_seed, "hash216_identity": node_id}
                    nodes.append(node)
                    parent_id = node_id
                    parent_membrane_id = membrane["membrane_id"]
                    inherited_membranes.append(membrane["membrane_id"])

        payload = {
            "schema": "HHS_PASS192_MATERIALIZED_PREFIX_V1",
            "source_tensor_id": tensor_id,
            "requested_depth": depth,
            "unbounded_declarative_depth": True,
            "finite_requested_prefix": True,
            "materialization_bounds": self._bounds_dict(bounds),
            "node_count": len(nodes),
            "nodes": nodes,
            "outer_hydration_modulus": OUTER_HYDRATION_MODULUS,
            "outer_modulus_applied_locally": False,
        }
        materialization_id = _hash216("HHS-P192-MATERIALIZATION", payload)
        payload["materialization_id"] = materialization_id
        payload["hash216_identity"] = materialization_id

        serialized = _canonical(payload)
        if len(serialized) > bounds.max_serialized_bytes:
            raise Pass192Error("HHS_P192_SERIALIZED_BOUND_EXCEEDED")
        if len(serialized) > bounds.max_memory_bytes:
            raise Pass192Error("HHS_P192_MEMORY_BOUND_EXCEEDED")
        if self._workspace_size() + len(serialized) > bounds.workspace_quota:
            raise Pass192Error("HHS_P192_WORKSPACE_QUOTA_EXCEEDED")

        receipt = self._append_receipt(
            "P192.MaterializeTensorPrefix",
            materialization_id,
            {
                "source_tensor_id": tensor_id,
                "requested_depth": depth,
                "node_count": len(nodes),
                "hash216_identity": materialization_id,
            },
            authority_execution,
        )
        payload["last_receipt_hash72"] = receipt["receipt_hash72"]
        path = self._record_path(self.materialization_root, materialization_id)
        self._write_json(path, payload)
        index = self._read_index()
        index["materializations"][materialization_id] = path.name
        self._write_index(index)
        return payload

    def get_materialization(self, materialization_id: str) -> dict[str, Any]:
        path = self._record_path(self.materialization_root, materialization_id)
        if not path.exists():
            raise Pass192Error("HHS_P192_MATERIALIZATION_NOT_FOUND")
        return json.loads(path.read_text("utf-8"))

    def validate_tensor(self, tensor_id: str) -> dict[str, Any]:
        manifest = self.get_tensor(tensor_id)
        required = {
            "tensor_id",
            "canonical_source",
            "source_identity",
            "lo_shu_cell_coordinate",
            "lo_shu_cell_value",
            "magnitude_rows",
            "seed_columns",
            "materialization_bounds",
            "hash216_identity",
        }
        missing = sorted(required - set(manifest))
        if missing:
            raise Pass192Error("HHS_P192_TENSOR_MANIFEST_INCOMPLETE", ",".join(missing))
        if manifest["canonical_source"] != CANONICAL_SOURCE:
            raise Pass192Error("HHS_P192_SOURCE_DRIFT")
        if tuple(manifest["magnitude_rows"]) != tuple(MAGNITUDES):
            raise Pass192Error("HHS_P192_MAGNITUDE_DRIFT")
        if tuple(manifest["seed_columns"]) != SEED_WITNESSES:
            raise Pass192Error("HHS_P192_SEED_WITNESS_DRIFT")
        row, column = manifest["lo_shu_cell_coordinate"]
        self._validate_cell(row, column)
        if manifest["lo_shu_cell_value"] != LO_SHU[row][column]:
            raise Pass192Error("HHS_P192_LO_SHU_CELL_DRIFT")
        body = {
            key: value
            for key, value in manifest.items()
            if key not in {
                "tensor_id", "root_id", "parent_id", "child_slot",
                "nesting_depth", "hash216_identity", "last_receipt_hash72",
            }
        }
        expected = _hash216("HHS-P192-TENSOR", body)
        if expected != tensor_id or manifest["hash216_identity"] != tensor_id:
            raise Pass192Error("HHS_P192_HASH216_IDENTITY_DRIFT")
        MaterializationBounds.from_mapping(manifest["materialization_bounds"])
        return {"ok": True, "tensor_id": tensor_id, "classification": manifest["implementation_status"]}

    def validate_materialization(self, materialization_id: str) -> dict[str, Any]:
        value = self.get_materialization(materialization_id)
        source = self.get_tensor(value["source_tensor_id"])
        depth = value["requested_depth"]
        expected_nodes = len(MAGNITUDES) * len(SEED_WITNESSES) * (depth + 1)
        if value["node_count"] != expected_nodes or len(value["nodes"]) != expected_nodes:
            raise Pass192Error("HHS_P192_NODE_COUNT_DIVERGENCE")
        if value["outer_modulus_applied_locally"] is not False:
            raise Pass192Error("HHS_P192_OUTER_MODULUS_LOCAL_REDUCTION_FORBIDDEN")
        by_lane: dict[tuple[int, int], list[dict[str, Any]]] = {}
        for node in value["nodes"]:
            lane = (node["magnitude_row_index"], node["seed_column_index"])
            by_lane.setdefault(lane, []).append(node)
            d = node["nesting_depth"]
            witness = build_witness(d)
            if (node["ratio_numerator"], node["ratio_denominator"]) != (witness.f_depth, witness.f_next):
                raise Pass192Error("HHS_P192_RATIO_DIVERGENCE")
            if (
                node["cumulative_scale_numerator"],
                node["cumulative_scale_denominator"],
            ) != (1, witness.f_depth):
                raise Pass192Error("HHS_P192_CUMULATIVE_SCALE_DIVERGENCE")
            membrane = node["membrane_witness"]
            if (membrane["modulus"], membrane["residue"]) != (d + 1, d):
                raise Pass192Error("HHS_P192_MEMBRANE_DIVERGENCE")
            if membrane["outer_modulus_applied_locally"] is not False:
                raise Pass192Error("HHS_P192_OUTER_MODULUS_LOCAL_REDUCTION_FORBIDDEN")
        if len(by_lane) != len(MAGNITUDES) * len(SEED_WITNESSES):
            raise Pass192Error("HHS_P192_LANE_COUNT_DIVERGENCE")
        for lane_nodes in by_lane.values():
            lane_nodes.sort(key=lambda item: item["nesting_depth"])
            parent = source["tensor_id"]
            for node in lane_nodes:
                if node["parent_id"] != parent:
                    raise Pass192Error("HHS_P192_PARENT_CHAIN_DIVERGENCE")
                parent = node["tensor_id"]

        identity_body = {
            key: value[key]
            for key in (
                "schema",
                "source_tensor_id",
                "requested_depth",
                "unbounded_declarative_depth",
                "finite_requested_prefix",
                "materialization_bounds",
                "node_count",
                "nodes",
                "outer_hydration_modulus",
                "outer_modulus_applied_locally",
            )
        }
        expected_id = _hash216("HHS-P192-MATERIALIZATION", identity_body)
        if expected_id != materialization_id or value["hash216_identity"] != materialization_id:
            raise Pass192Error("HHS_P192_MATERIALIZATION_IDENTITY_DRIFT")
        return {"ok": True, "materialization_id": materialization_id, "node_count": expected_nodes}

    def receipts_for(self, object_identity: Optional[str] = None) -> list[dict[str, Any]]:
        if not self.receipt_path.exists():
            return []
        values = []
        for line in self.receipt_path.read_text("utf-8").splitlines():
            if not line:
                continue
            record = json.loads(line)
            if object_identity is None or record["object_identity"] == object_identity:
                values.append(record)
        return values

    def replay(self, object_identity: Optional[str] = None) -> dict[str, Any]:
        records = self.receipts_for()
        previous: Optional[str] = None
        for sequence, record in enumerate(records):
            body = {
                key: record[key]
                for key in (
                    "sequence",
                    "event",
                    "object_identity",
                    "state_hash72",
                    "authority_receipt_hash72",
                    "previous_receipt_hash72",
                    "payload",
                )
            }
            if record["sequence"] != sequence:
                raise Pass192Error("HHS_P192_REPLAY_SEQUENCE_DIVERGENCE")
            if record["previous_receipt_hash72"] != previous:
                raise Pass192Error("HHS_P192_REPLAY_PREVIOUS_RECEIPT_DIVERGENCE")
            if (
                not validate_hash72(record["state_hash72"])
                or not validate_hash72(record["authority_receipt_hash72"])
            ):
                raise Pass192Error("HHS_P192_REPLAY_AUTHORITY_HASH72_INVALID")
            expected = _hash72("HHS-P192-RECEIPT", body)
            if record["receipt_hash72"] != expected:
                raise Pass192Error("HHS_P192_REPLAY_RECEIPT_DIVERGENCE")
            previous = record["receipt_hash72"]
        selected = records if object_identity is None else [
            item for item in records if item["object_identity"] == object_identity
        ]
        return {
            "ok": True,
            "records": len(records),
            "selected_records": len(selected),
            "last_receipt_hash72": previous,
            "object_identity": object_identity,
        }

    def _append_receipt(
        self,
        event: str,
        object_identity: str,
        payload: Any,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        state_hash72, authority_receipt_hash72 = _authority_lineage(authority_execution)
        previous = None
        sequence = 0
        if self.receipt_path.exists():
            existing = [line for line in self.receipt_path.read_text("utf-8").splitlines() if line]
            if existing:
                last = json.loads(existing[-1])
                previous = last["receipt_hash72"]
                sequence = int(last["sequence"]) + 1
        body = {
            "sequence": sequence,
            "event": event,
            "object_identity": object_identity,
            "state_hash72": state_hash72,
            "authority_receipt_hash72": authority_receipt_hash72,
            "previous_receipt_hash72": previous,
            "payload": payload,
        }
        body["receipt_hash72"] = _hash72("HHS-P192-RECEIPT", body)
        self.root.mkdir(parents=True, exist_ok=True)
        with self.receipt_path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical(body).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return body

    @staticmethod
    def _bounds_dict(bounds: MaterializationBounds) -> dict[str, Any]:
        value = asdict(bounds)
        value["capability_scope"] = list(bounds.capability_scope)
        return value

    @staticmethod
    def _validate_cell(row: int, column: int) -> None:
        if (
            not isinstance(row, int)
            or isinstance(row, bool)
            or not isinstance(column, int)
            or isinstance(column, bool)
            or row not in range(3)
            or column not in range(3)
        ):
            raise Pass192Error("HHS_P192_LO_SHU_CELL_INVALID")

    @staticmethod
    def _record_path(root: Path, identity: str) -> Path:
        if not isinstance(identity, str) or len(identity) != 216:
            raise Pass192Error("HHS_P192_HASH216_IDENTITY_INVALID")
        return root / (_hash72("HHS-P192-FILE", {"identity": identity}) + ".json")

    def _read_index(self) -> dict[str, Any]:
        try:
            value = json.loads(self.index_path.read_text("utf-8"))
        except Exception as exc:
            raise Pass192Error("HHS_P192_INDEX_INVALID") from exc
        if value.get("schema") != "HHS_PASS192_CELLULAR_FIBONACCI_REGISTRY_V1":
            raise Pass192Error("HHS_P192_INDEX_SCHEMA_INVALID")
        return value

    def _write_index(self, value: Mapping[str, Any]) -> None:
        if value.get("schema") != "HHS_PASS192_CELLULAR_FIBONACCI_REGISTRY_V1":
            raise Pass192Error("HHS_P192_INDEX_SCHEMA_INVALID")
        self._write_json(self.index_path, value)

    @staticmethod
    def _write_json(path: Path, value: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = _canonical(value) + b"\n"
        temp = path.with_suffix(path.suffix + ".tmp")
        with temp.open("wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)

    def _workspace_size(self) -> int:
        total = 0
        if not self.root.exists():
            return 0
        for path in self.root.rglob("*"):
            if path.is_file():
                total += path.stat().st_size
        return total


__all__ = [
    "CANONICAL_SOURCE",
    "CONTRACT_ID",
    "VERSION",
    "CONTRACT_AUTHORIZATION_COMMIT",
    "FROZEN_I133",
    "LO_SHU",
    "MAGNITUDES",
    "SEED_WITNESSES",
    "OPERATION_IDS",
    "OUTER_HYDRATION_MODULUS",
    "PASS192_MAX_DEPTH",
    "MaterializationBounds",
    "Pass192Error",
    "Pass192Runtime",
    "source_invariants",
    "fibonacci_sequence",
    "fibonacci_ratio",
    "cumulative_fibonacci_scale",
    "membrane_witness",
]
