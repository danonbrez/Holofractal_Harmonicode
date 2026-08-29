"""Pass 193 exact hypersolid manifold, native egress, and package-security runtime.

This repair-forward implementation materializes the Pass 193 contract without
creating a second mutation authority. Canonical geometry, transform history,
fractal addressing, package manifests, and execution-policy mutations consume
an already-authorized VM81 execution receipt. Rendering and foreign/native
toolchain outputs remain projections/evidence and cannot overwrite canonical
geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any, Dict, Iterable, Mapping, Sequence
from zipfile import ZIP_DEFLATED, ZipFile

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import _validated_authorized_tick
from hhs_runtime.pass219_fibonacci_compression_reference_v1 import MAGNITUDES, build_witness

CONTRACT_ID = "HHS-P193-RHFM-EPRP-NF-NC-SNFTE-VM81-H72-H216"
VERSION = CONTRACT_ID + "-1.0.0"
CONTRACT_AUTHORIZATION_COMMIT = "eebc47a52de143df4a9acf807735f576ad0ce844"
CONTRACT_BASELINE_COMMIT = "c3da7e2b7125754b65f08fb8922a151bf01df2b8"
FROZEN_I132 = "d311cd243845456851518ce1fef026a7d3cac45e"

REGULAR_3D = {
    "tetrahedron": {"dimension": 3, "schlafli": "{3,3}", "vertices": 4, "edges": 6, "faces": 4},
    "cube": {"dimension": 3, "schlafli": "{4,3}", "vertices": 8, "edges": 12, "faces": 6},
    "octahedron": {"dimension": 3, "schlafli": "{3,4}", "vertices": 6, "edges": 12, "faces": 8},
    "dodecahedron": {"dimension": 3, "schlafli": "{5,3}", "vertices": 20, "edges": 30, "faces": 12},
    "icosahedron": {"dimension": 3, "schlafli": "{3,5}", "vertices": 12, "edges": 30, "faces": 20},
}
REGULAR_4D = {
    "5-cell": {"dimension": 4, "schlafli": "{3,3,3}", "vertices": 5, "edges": 10, "faces": 10, "cells": 5},
    "8-cell": {"dimension": 4, "schlafli": "{4,3,3}", "vertices": 16, "edges": 32, "faces": 24, "cells": 8},
    "16-cell": {"dimension": 4, "schlafli": "{3,3,4}", "vertices": 8, "edges": 24, "faces": 32, "cells": 16},
    "24-cell": {"dimension": 4, "schlafli": "{3,4,3}", "vertices": 24, "edges": 96, "faces": 96, "cells": 24},
    "120-cell": {"dimension": 4, "schlafli": "{5,3,3}", "vertices": 600, "edges": 1200, "faces": 720, "cells": 120},
    "600-cell": {"dimension": 4, "schlafli": "{3,3,5}", "vertices": 120, "edges": 720, "faces": 1200, "cells": 600},
}
REGULAR_HIGH_DIMENSION = frozenset({"simplex", "hypercube", "cross-polytope"})
SUPPORTED_TARGETS = frozenset({
    "linux-x86_64-elf",
    "linux-arm64-elf",
    "windows-x86_64-pe",
    "macos-arm64-macho",
})
REQUIRED_NATIVE_EVIDENCE = (
    "compiled",
    "linked",
    "launched",
    "abi_validated",
    "deterministic_workload",
)
MAX_DIMENSION = 12
MAX_MATERIALIZED_VERTICES = 4096
MAX_TEXT_BYTES = 4096


class Pass193Error(RuntimeError):
    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass193Error("HHS_P193_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN", path)
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(domain: str, payload: Any) -> str:
    return sha256(domain.encode("ascii") + b"\0" + _canonical(payload)).hexdigest()


def _hash72(domain: str, payload: Any) -> str:
    return hash72_digest({"domain": domain, "contract": CONTRACT_ID}, payload)


def _hash216(domain: str, payload: Any) -> str:
    previous = _hash72(domain + ":PREVIOUS", {"genesis": CONTRACT_AUTHORIZATION_COMMIT})
    change = _hash72(domain + ":CHANGE", payload)
    receipt = _hash72(domain + ":RECEIPT", {"previous": previous, "change": change})
    out = previous + change + receipt
    if len(out) != 216:
        raise AssertionError("Hash216 must contain exactly three Hash72 witnesses")
    return out


def _authority_lineage(execution: Mapping[str, Any]) -> tuple[str, str]:
    try:
        validated = _validated_authorized_tick(execution)
    except Exception as exc:
        raise Pass193Error("HHS_P193_VM81_AUTHORITY_REQUIRED") from exc
    receipt = validated["receipt"]
    state_hash72 = receipt["state_hash72"]
    receipt_hash72 = receipt["receipt_hash72"]
    if not validate_hash72(state_hash72) or not validate_hash72(receipt_hash72):
        raise Pass193Error("HHS_P193_VM81_AUTHORITY_HASH72_INVALID")
    return state_hash72, receipt_hash72


def _bounded_text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise Pass193Error("HHS_P193_TEXT_REQUIRED", label)
    if len(value.encode("utf-8")) > MAX_TEXT_BYTES:
        raise Pass193Error("HHS_P193_TEXT_LIMIT", label)
    return value


def _fraction_record(numerator: int, denominator: int) -> dict[str, int]:
    if not isinstance(numerator, int) or not isinstance(denominator, int) or denominator == 0:
        raise Pass193Error("HHS_P193_EXACT_PHASE_INVALID")
    value = Fraction(numerator, denominator)
    return {"numerator": value.numerator, "denominator": value.denominator}


def _phase_record(plane: Sequence[int], numerator: int, denominator: int, dimension: int) -> dict[str, Any]:
    if len(plane) != 2:
        raise Pass193Error("HHS_P193_ROTATION_PLANE_INVALID")
    i, j = int(plane[0]), int(plane[1])
    if not (0 <= i < j < dimension):
        raise Pass193Error("HHS_P193_ROTATION_PLANE_INVALID")
    return {
        "plane": [i, j],
        "phase": _fraction_record(numerator, denominator),
        "unit": "turn",
        "orientation": "positive",
    }


def _all_phase_planes(dimension: int) -> list[list[int]]:
    return [[i, j] for i, j in combinations(range(dimension), 2)]


def _simplex_coordinates(dimension: int) -> list[list[int]]:
    return [
        [1 if column == row else 0 for column in range(dimension + 1)]
        for row in range(dimension + 1)
    ]


def _hypercube_coordinates(dimension: int) -> list[list[int]]:
    count = 1 << dimension
    if count > MAX_MATERIALIZED_VERTICES:
        raise Pass193Error("HHS_P193_FINITE_MATERIALIZATION_LIMIT")
    return [list(bits) for bits in product((-1, 1), repeat=dimension)]


def _cross_polytope_coordinates(dimension: int) -> list[list[int]]:
    out: list[list[int]] = []
    for axis in range(dimension):
        for sign_value in (-1, 1):
            row = [0] * dimension
            row[axis] = sign_value
            out.append(row)
    return out


def _hypercube_edges(vertices: Sequence[Sequence[int]]) -> list[list[int]]:
    out: list[list[int]] = []
    for left in range(len(vertices)):
        for right in range(left + 1, len(vertices)):
            if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1:
                out.append([left, right])
    return out


def _cross_edges(dimension: int) -> list[list[int]]:
    out: list[list[int]] = []
    for left in range(2 * dimension):
        for right in range(left + 1, 2 * dimension):
            if left // 2 == right // 2:
                continue
            out.append([left, right])
    return out


def _family_model(family: str, dimension: int) -> dict[str, Any]:
    family = family.lower()
    if not isinstance(dimension, int) or dimension < 2 or dimension > MAX_DIMENSION:
        raise Pass193Error("HHS_P193_DIMENSION_INVALID")

    if dimension == 3 and family in REGULAR_3D:
        meta = dict(REGULAR_3D[family])
    elif dimension == 4 and family in REGULAR_4D:
        meta = dict(REGULAR_4D[family])
    elif dimension >= 5 and family in REGULAR_HIGH_DIMENSION:
        meta = {"dimension": dimension, "schlafli": "family-constructor"}
    else:
        aliases = {"tesseract": "8-cell", "hypercube4": "8-cell"}
        normalized = aliases.get(family)
        if normalized and dimension == 4:
            family = normalized
            meta = dict(REGULAR_4D[family])
        else:
            raise Pass193Error("HHS_P193_REGULAR_FAMILY_UNREGISTERED")

    if family in {"tetrahedron", "5-cell", "simplex"}:
        coordinates = _simplex_coordinates(dimension)
        edges = [list(pair) for pair in combinations(range(dimension + 1), 2)]
        coordinate_model = "EXACT_BARYCENTRIC_INTEGER"
        incidence_model = "EXPLICIT"
    elif family in {"cube", "8-cell", "hypercube"}:
        coordinates = _hypercube_coordinates(dimension)
        edges = _hypercube_edges(coordinates)
        coordinate_model = "EXACT_INTEGER_CARTESIAN"
        incidence_model = "EXPLICIT"
    elif family in {"octahedron", "16-cell", "cross-polytope"}:
        coordinates = _cross_polytope_coordinates(dimension)
        edges = _cross_edges(dimension)
        coordinate_model = "EXACT_INTEGER_CARTESIAN"
        incidence_model = "EXPLICIT"
    elif family == "24-cell":
        coords = set()
        for a in range(4):
            for b in range(a + 1, 4):
                for sa in (-1, 1):
                    for sb in (-1, 1):
                        row = [0, 0, 0, 0]
                        row[a], row[b] = sa, sb
                        coords.add(tuple(row))
        coordinates = [list(row) for row in sorted(coords)]
        edges = []
        coordinate_model = "EXACT_INTEGER_CARTESIAN"
        incidence_model = "SCHLAFLI_DECLARATIVE"
    else:
        coordinates = []
        edges = []
        coordinate_model = "EXACT_SYMBOLIC_REGULAR_POLYTOPE_CONSTRUCTOR"
        incidence_model = "SCHLAFLI_DECLARATIVE"

    return {
        "family": family,
        "dimension": dimension,
        "classification": "regular-convex",
        "schlafli": meta["schlafli"],
        "expected_counts": {key: value for key, value in meta.items() if key not in {"dimension", "schlafli"}},
        "exact_coordinate_model": coordinate_model,
        "coordinates": coordinates,
        "incidence_graph": {
            "model": incidence_model,
            "vertices": list(range(len(coordinates))) if coordinates else "DERIVED_FROM_REGULAR_CONSTRUCTOR",
            "edges": edges if edges else "DERIVED_FROM_REGULAR_CONSTRUCTOR",
            "schlafli": meta["schlafli"],
            "expected_counts": {key: value for key, value in meta.items() if key not in {"dimension", "schlafli"}},
        },
        "phase_planes": _all_phase_planes(dimension),
    }


def _fractal_address(
    *,
    root_id: str,
    parent_id: str | None,
    child_slot: int | None,
    lo_shu_cell: Sequence[int] | None,
    magnitude_row: int | None,
    nesting_depth: int,
    phase_plane: Sequence[int] | None,
    phase: Mapping[str, int] | None,
    incidence_path: Sequence[int] = (),
    local_chart_id: str = "root",
) -> dict[str, Any]:
    return {
        "root_object_id": root_id,
        "parent_object_id": parent_id,
        "child_slot": child_slot,
        "lo_shu_cell": list(lo_shu_cell) if lo_shu_cell is not None else None,
        "magnitude_row": magnitude_row,
        "nesting_depth": nesting_depth,
        "phase_plane": list(phase_plane) if phase_plane is not None else None,
        "exact_phase": dict(phase) if phase is not None else None,
        "incidence_path": list(incidence_path),
        "local_chart_id": local_chart_id,
    }


def native_probe_source() -> str:
    return (
        "#include <stdint.h>\n"
        "#include <stdio.h>\n"
        "int main(void){uint64_t x=193u; x=(x*81u)+72u; "
        "printf(\"HHS-P193-NATIVE:%llu\\n\",(unsigned long long)x); "
        "return x==15705u?0:1;}\n"
    )


@dataclass(frozen=True)
class NativeEvidence:
    compiled: bool
    linked: bool
    launched: bool
    abi_validated: bool
    deterministic_workload: bool

    def valid(self) -> bool:
        return all(getattr(self, name) is True for name in REQUIRED_NATIVE_EVIDENCE)


class Pass193Runtime:
    def __init__(self, state_root: str | Path) -> None:
        self.state_root = Path(state_root).resolve()
        self.object_root = self.state_root / "objects"
        self.artifact_root = self.state_root / "artifacts"
        self.package_root = self.state_root / "packages"
        for path in (self.object_root, self.artifact_root, self.package_root):
            path.mkdir(parents=True, exist_ok=True)
        self.receipt_path = self.state_root / "receipts.jsonl"
        self.index_path = self.state_root / "index.json"
        if not self.index_path.exists():
            self._write_json(self.index_path, {"objects": {}, "artifacts": {}, "packages": {}, "nft_executables": {}})

    def _read_index(self) -> dict[str, Any]:
        return json.loads(self.index_path.read_text("utf-8"))

    def _write_json(self, path: Path, payload: Any) -> None:
        raw = _canonical(payload)
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_bytes(raw)
        os.replace(temp, path)

    def _write_index(self, index: Mapping[str, Any]) -> None:
        self._write_json(self.index_path, index)

    def _record_path(self, root: Path, identity: str) -> Path:
        return root / (_sha256("HHS-P193-STORAGE-KEY", {"identity": identity}) + ".json")

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
            lines = [line for line in self.receipt_path.read_text("utf-8").splitlines() if line]
            if lines:
                last = json.loads(lines[-1])
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
        body["receipt_hash72"] = _hash72("HHS-P193-RECEIPT", body)
        with self.receipt_path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical(body).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return body

    def status(self) -> dict[str, Any]:
        index = self._read_index()
        return {
            "contract": CONTRACT_ID,
            "version": VERSION,
            "classification": "HHS_PASS_193_REPAIR_IMPLEMENTATION",
            "canonical_geometry": "EXACT_OR_SYMBOLIC",
            "float_canonical_authority": False,
            "vm81_singleton_required": True,
            "hash72_receipts": True,
            "hash216_identity": True,
            "regular_3d_families": sorted(REGULAR_3D),
            "regular_4d_families": sorted(REGULAR_4D),
            "regular_high_dimension_families": sorted(REGULAR_HIGH_DIMENSION),
            "declared_native_targets": sorted(SUPPORTED_TARGETS),
            "objects": len(index["objects"]),
            "artifacts": len(index["artifacts"]),
            "packages": len(index["packages"]),
            "nft_executables": len(index["nft_executables"]),
        }

    def create_hypersolid(
        self,
        family: str,
        dimension: int,
        *,
        authority_execution: Mapping[str, Any],
        constraint_registry: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        model = _family_model(family, dimension)
        constraints = dict(
            constraint_registry
            or {
                "incidence_preservation": True,
                "orientation": True,
                "metric_preservation": True,
                "pass192_parent_child_preservation": True,
            }
        )
        _reject_float(constraints)
        seed = {
            "contract": CONTRACT_ID,
            "family_model": model,
            "constraint_registry": constraints,
            "transform_history": [],
            "fold_graph": [],
            "parent_id": None,
            "child_ids": [],
        }
        root_id = _hash216("HHS-P193-OBJECT", seed)
        manifest = {
            "object_id": root_id,
            "contract_version": "1.0.0",
            "family": model["family"],
            "dimension": dimension,
            "combinatorial_signature": _sha256("HHS-P193-COMBINATORIAL", model["incidence_graph"]),
            "vertex_set": model["coordinates"],
            "edge_set": model["incidence_graph"]["edges"],
            "face_set": model["incidence_graph"]["expected_counts"].get("faces", "DERIVED"),
            "cell_set": model["incidence_graph"]["expected_counts"].get("cells", "DERIVED"),
            "higher_incidence_sets": [],
            "symmetry_group": {"schlafli": model["schlafli"]},
            "dual_identity": "DERIVED_FROM_SCHLAFLI",
            "exact_coordinate_model": model["exact_coordinate_model"],
            "metric_tensor": {"type": "EUCLIDEAN", "dimension": dimension},
            "orientation_rotor": {"type": "IDENTITY", "dimension": dimension},
            "phase_planes": model["phase_planes"],
            "constraint_registry": constraints,
            "fold_graph": [],
            "transform_history": [],
            "root_id": root_id,
            "parent_id": None,
            "child_ids": [],
            "fractal_address": _fractal_address(
                root_id=root_id,
                parent_id=None,
                child_slot=None,
                lo_shu_cell=None,
                magnitude_row=None,
                nesting_depth=0,
                phase_plane=None,
                phase=None,
            ),
            "pass192_nesting_record": None,
            "material_projection": None,
            "physics_projection": None,
            "render_projection": None,
            "collision_projection": None,
            "hash216_identity": root_id,
            "hash72_receipt_policy": "REQUIRED_FOR_MUTATION",
            "implementation_status": "CANONICAL_EXACT_OBJECT",
        }
        path = self._record_path(self.object_root, root_id)
        if path.exists():
            return json.loads(path.read_text("utf-8"))
        receipt = self._append_receipt("Hypersolid.Create", root_id, manifest, authority_execution)
        manifest["last_receipt_hash72"] = receipt["receipt_hash72"]
        self._write_json(path, manifest)
        index = self._read_index()
        index["objects"][root_id] = path.name
        self._write_index(index)
        return manifest

    def get_object(self, object_id: str) -> dict[str, Any]:
        index = self._read_index()
        name = index["objects"].get(object_id)
        if not name:
            raise Pass193Error("HHS_P193_OBJECT_NOT_FOUND")
        return json.loads((self.object_root / name).read_text("utf-8"))

    def validate_object(self, object_id: str) -> dict[str, Any]:
        manifest = self.get_object(object_id)
        _reject_float(manifest)
        required = {
            "object_id",
            "family",
            "dimension",
            "phase_planes",
            "constraint_registry",
            "fold_graph",
            "fractal_address",
            "hash216_identity",
        }
        missing = sorted(required - manifest.keys())
        if missing:
            raise Pass193Error("HHS_P193_MANIFEST_INCOMPLETE", ",".join(missing))
        dimension = int(manifest["dimension"])
        if len(manifest["phase_planes"]) != dimension * (dimension - 1) // 2:
            raise Pass193Error("HHS_P193_PHASE_PLANE_COUNT_INVALID")
        if len(manifest["hash216_identity"]) != 216:
            raise Pass193Error("HHS_P193_HASH216_IDENTITY_INVALID")
        return {"ok": True, "object_id": object_id, "classification": manifest["implementation_status"]}

    def project(self, object_id: str, target_dimension: int) -> dict[str, Any]:
        source = self.get_object(object_id)
        if target_dimension < 2 or target_dimension >= source["dimension"]:
            raise Pass193Error("HHS_P193_PROJECTION_TARGET_INVALID")
        payload = {
            "classification": "NONCANONICAL_PROJECTION",
            "source_object_id": object_id,
            "source_hash216_identity": source["hash216_identity"],
            "source_dimension": source["dimension"],
            "target_dimension": target_dimension,
            "transform_history": source["transform_history"],
            "canonical_geometry_mutated": False,
        }
        payload["projection_identity"] = _hash216("HHS-P193-PROJECTION", payload)
        return payload

    def receipts_for(self, object_identity: str) -> list[dict[str, Any]]:
        if not self.receipt_path.exists():
            return []
        out = []
        for raw in self.receipt_path.read_text("utf-8").splitlines():
            if raw:
                record = json.loads(raw)
                if record["object_identity"] == object_identity:
                    out.append(record)
        return out

    def _replace_object(
        self,
        manifest: Mapping[str, Any],
        *,
        event: str,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        body = {
            key: value
            for key, value in manifest.items()
            if key not in {"object_id", "hash216_identity", "last_receipt_hash72"}
        }
        new_id = _hash216("HHS-P193-OBJECT", body)
        result = dict(manifest)
        result["object_id"] = new_id
        result["hash216_identity"] = new_id
        result["root_id"] = result.get("root_id") or new_id
        receipt = self._append_receipt(event, new_id, body, authority_execution)
        result["last_receipt_hash72"] = receipt["receipt_hash72"]
        path = self._record_path(self.object_root, new_id)
        self._write_json(path, result)
        index = self._read_index()
        index["objects"][new_id] = path.name
        self._write_index(index)
        return result

    def rotate(
        self,
        object_id: str,
        plane: Sequence[int],
        numerator: int,
        denominator: int,
        *,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        source = self.get_object(object_id)
        phase = _phase_record(plane, numerator, denominator, source["dimension"])
        result = dict(source)
        history = list(result["transform_history"])
        history.append({
            "operation": "ROTATE",
            "order": len(history),
            **phase,
            "source_state": object_id,
            "preserved_constraints": sorted(
                key for key, value in source["constraint_registry"].items() if value is True
            ),
        })
        result["transform_history"] = history
        result["orientation_rotor"] = {"type": "ORDERED_EXACT_PHASE_SEQUENCE", "operations": history}
        result["fractal_address"] = dict(result["fractal_address"])
        result["fractal_address"]["phase_plane"] = phase["plane"]
        result["fractal_address"]["exact_phase"] = phase["phase"]
        return self._replace_object(result, event="Hypersolid.Rotate", authority_execution=authority_execution)

    def fold(
        self,
        object_id: str,
        hinge_id: str,
        plane: Sequence[int],
        numerator: int,
        denominator: int,
        *,
        target_dimension: int,
        reversible: bool,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        source = self.get_object(object_id)
        if target_dimension < 2 or target_dimension > source["dimension"]:
            raise Pass193Error("HHS_P193_FOLD_TARGET_INVALID")
        phase = _phase_record(plane, numerator, denominator, source["dimension"])
        result = dict(source)
        graph = list(result["fold_graph"])
        graph.append({
            "step": len(graph),
            "hinge_id": _bounded_text(hinge_id, "hinge_id"),
            "affected_incidence_elements": "DECLARED_BY_HINGE",
            **phase,
            "constraint_decision": "ADMITTED",
            "reversibility_class": "REVERSIBLE" if reversible else "IRREVERSIBLE",
            "source_state": object_id,
            "target_projection_dimension": target_dimension,
        })
        result["fold_graph"] = graph
        result["render_projection"] = {
            "classification": "NONCANONICAL_PROJECTION",
            "target_dimension": target_dimension,
            "source_object_id": object_id,
        }
        return self._replace_object(result, event="Hypersolid.Fold", authority_execution=authority_execution)

    def nest(
        self,
        object_id: str,
        *,
        child_slot: int,
        lo_shu_cell: Sequence[int],
        magnitude_row: int,
        depth: int,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        parent = self.get_object(object_id)
        if not isinstance(child_slot, int) or child_slot < 0:
            raise Pass193Error("HHS_P193_CHILD_SLOT_INVALID")
        if list(lo_shu_cell) not in [[r, c] for r in range(3) for c in range(3)]:
            raise Pass193Error("HHS_P193_LO_SHU_CELL_INVALID")
        if magnitude_row not in MAGNITUDES:
            raise Pass193Error("HHS_P193_MAGNITUDE_ROW_INVALID")
        witness = build_witness(depth)
        nesting = {
            "depth": depth,
            "ratio_num": witness.transition.numerator,
            "ratio_den": witness.transition.denominator,
            "cumulative_num": witness.cumulative_scale.numerator,
            "cumulative_den": witness.cumulative_scale.denominator,
            "membrane_modulus": witness.membrane_modulus,
            "membrane_residue": witness.membrane_residue,
            "lo_shu_cell": list(lo_shu_cell),
            "magnitude_row": magnitude_row,
            "parent_id": object_id,
            "child_slot": child_slot,
        }
        child_seed = {
            key: value
            for key, value in parent.items()
            if key not in {"object_id", "hash216_identity", "last_receipt_hash72", "child_ids"}
        }
        child_seed["parent_id"] = object_id
        child_seed["pass192_nesting_record"] = nesting
        child_seed["child_ids"] = []
        child_seed["fractal_address"] = _fractal_address(
            root_id=parent["root_id"],
            parent_id=object_id,
            child_slot=child_slot,
            lo_shu_cell=lo_shu_cell,
            magnitude_row=magnitude_row,
            nesting_depth=depth,
            phase_plane=None,
            phase=None,
            incidence_path=(child_slot,),
        )
        child_id = _hash216("HHS-P193-OBJECT", child_seed)
        child = dict(child_seed)
        child["object_id"] = child_id
        child["hash216_identity"] = child_id
        child["implementation_status"] = "CANONICAL_EXACT_NESTED_OBJECT"
        receipt = self._append_receipt("Hypersolid.Nest", child_id, nesting, authority_execution)
        child["last_receipt_hash72"] = receipt["receipt_hash72"]
        child_path = self._record_path(self.object_root, child_id)
        self._write_json(child_path, child)
        index = self._read_index()
        index["objects"][child_id] = child_path.name
        self._write_index(index)
        return child

    def record_native_artifact(
        self,
        object_id: str,
        *,
        target: str,
        binary_bytes: bytes,
        compiler_identity: str,
        compiler_flags: Sequence[str],
        linker_identity: str,
        build_environment: Mapping[str, Any],
        evidence: Mapping[str, Any],
        license_manifest: Mapping[str, Any],
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        source = self.get_object(object_id)
        if target not in SUPPORTED_TARGETS:
            raise Pass193Error("HHS_P193_NATIVE_TARGET_UNDECLARED")
        if not isinstance(binary_bytes, (bytes, bytearray, memoryview)) or not binary_bytes:
            raise Pass193Error("HHS_P193_NATIVE_BINARY_REQUIRED")
        binary_bytes = bytes(binary_bytes)
        binary_sha256 = sha256(binary_bytes).hexdigest()
        native = NativeEvidence(**{name: bool(evidence.get(name, False)) for name in REQUIRED_NATIVE_EVIDENCE})
        if not native.valid():
            raise Pass193Error("HHS_P193_NATIVE_TARGET_VALIDATION_INCOMPLETE")
        if not license_manifest or license_manifest.get("closed") is not True:
            raise Pass193Error("HHS_P193_LICENSE_CLOSURE_REQUIRED")
        payload = {
            "canonical_application_parent": object_id,
            "target": target,
            "binary_sha256": binary_sha256,
            "compiler_identity": _bounded_text(compiler_identity, "compiler_identity"),
            "compiler_flags": list(compiler_flags),
            "linker_identity": _bounded_text(linker_identity, "linker_identity"),
            "build_environment_manifest": dict(build_environment),
            "license_manifest": dict(license_manifest),
            "native_validation": {name: True for name in REQUIRED_NATIVE_EVIDENCE},
            "source_hash216_identity": source["hash216_identity"],
        }
        artifact_id = _hash216("HHS-P193-NATIVE-ARTIFACT", payload)
        payload["artifact_id"] = artifact_id
        receipt = self._append_receipt("Hypersolid.Compile", artifact_id, payload, authority_execution)
        payload["build_receipt_hash72"] = receipt["receipt_hash72"]
        path = self._record_path(self.artifact_root, artifact_id)
        binary_path = self.artifact_root / (_sha256("HHS-P193-BINARY-FILE", {"artifact_id": artifact_id}) + ".bin")
        binary_path.write_bytes(binary_bytes)
        payload["binary_file"] = binary_path.name
        self._write_json(path, payload)
        index = self._read_index()
        index["artifacts"][artifact_id] = path.name
        self._write_index(index)
        return payload

    @staticmethod
    def validate_archive_entries(entries: Iterable[str]) -> list[str]:
        normalized: list[str] = []
        for raw in entries:
            if not isinstance(raw, str) or not raw:
                raise Pass193Error("HHS_P193_ARCHIVE_ENTRY_INVALID")
            path = PurePosixPath(raw)
            if path.is_absolute() or ".." in path.parts or "\\" in raw or raw.startswith("/"):
                raise Pass193Error("HHS_P193_ARCHIVE_PATH_TRAVERSAL")
            normalized.append(path.as_posix())
        if len(normalized) != len(set(normalized)):
            raise Pass193Error("HHS_P193_ARCHIVE_DUPLICATE_ENTRY")
        return normalized

    def build_portable_bundle(
        self,
        object_id: str,
        artifact_ids: Sequence[str],
        *,
        capabilities: Sequence[str],
        license_manifest: Mapping[str, Any],
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        source = self.get_object(object_id)
        index = self._read_index()
        artifacts = []
        for artifact_id in artifact_ids:
            name = index["artifacts"].get(artifact_id)
            if not name:
                raise Pass193Error("HHS_P193_ARTIFACT_NOT_FOUND")
            artifacts.append(json.loads((self.artifact_root / name).read_text("utf-8")))
        if not artifacts:
            raise Pass193Error("HHS_P193_PACKAGE_REQUIRES_NATIVE_PAYLOAD")
        if license_manifest.get("closed") is not True:
            raise Pass193Error("HHS_P193_LICENSE_CLOSURE_REQUIRED")
        manifest = {
            "application_identity": object_id,
            "source_graph_identity": source["hash216_identity"],
            "operation_closure_identity": _hash216("HHS-P193-OPERATION-CLOSURE", source["transform_history"]),
            "asset_closure_identity": _hash216("HHS-P193-ASSET-CLOSURE", []),
            "targets": [artifact["target"] for artifact in artifacts],
            "payloads": [
                {"artifact_id": item["artifact_id"], "binary_sha256": item["binary_sha256"], "target": item["target"]}
                for item in artifacts
            ],
            "capabilities": sorted(set(_bounded_text(value, "capability") for value in capabilities)),
            "signatures": {"status": "UNSIGNED"},
            "license_manifest": dict(license_manifest),
            "build_receipts": [item["build_receipt_hash72"] for item in artifacts],
            "replay_manifest": {"required": True, "source_object_id": object_id},
            "installer": {
                "entrypoint": "install.hhs",
                "automatic_execution": False,
                "explicit_user_action_required": True,
                "rollback_required": True,
            },
        }
        package_id = _hash216("HHS-P193-PACKAGE", manifest)
        manifest["package_id"] = package_id
        entries = self.validate_archive_entries(
            ["manifest.hhs.json", "install.hhs", "uninstall.hhs", "licenses/manifest.json"]
            + [f"bin/{item['target']}/{item['artifact_id']}.payload" for item in artifacts]
        )
        archive_path = self.package_root / (_sha256("HHS-P193-PACKAGE-FILE", {"id": package_id}) + ".zip")
        with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr("manifest.hhs.json", _canonical(manifest))
            archive.writestr("install.hhs", b"HHS_INSTALL_REQUIRES_EXPLICIT_USER_ACTION\n")
            archive.writestr("uninstall.hhs", b"HHS_UNINSTALL_REQUIRES_EXPLICIT_USER_ACTION\n")
            archive.writestr("licenses/manifest.json", _canonical(license_manifest))
            for artifact in artifacts:
                binary_path = self.artifact_root / artifact["binary_file"]
                binary_bytes = binary_path.read_bytes()
                if sha256(binary_bytes).hexdigest() != artifact["binary_sha256"]:
                    raise Pass193Error("HHS_P193_BINARY_DIGEST_MISMATCH")
                archive.writestr(
                    f"bin/{artifact['target']}/{artifact['artifact_id']}.payload",
                    binary_bytes,
                )
        with ZipFile(archive_path, "r") as archive:
            self.validate_archive_entries(archive.namelist())
            if sorted(archive.namelist()) != sorted(entries):
                raise Pass193Error("HHS_P193_PACKAGE_ENTRY_MISMATCH")
            for info in archive.infolist():
                mode = (info.external_attr >> 16) & 0o7777
                if mode & (stat.S_ISUID | stat.S_ISGID):
                    raise Pass193Error("HHS_P193_ARCHIVE_UNSAFE_MODE")
        manifest["archive_sha256"] = sha256(archive_path.read_bytes()).hexdigest()
        receipt = self._append_receipt("Hypersolid.Package", package_id, manifest, authority_execution)
        manifest["package_receipt_hash72"] = receipt["receipt_hash72"]
        manifest_path = self._record_path(self.package_root, package_id)
        self._write_json(manifest_path, manifest)
        index = self._read_index()
        index["packages"][package_id] = manifest_path.name
        self._write_index(index)
        return manifest

    def create_nft_executable(
        self,
        package_id: str,
        *,
        rights: Mapping[str, Any],
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        index = self._read_index()
        package_name = index["packages"].get(package_id)
        if not package_name:
            raise Pass193Error("HHS_P193_PACKAGE_NOT_FOUND")
        package = json.loads((self.package_root / package_name).read_text("utf-8"))
        if rights.get("license_manifest_identity") is None:
            raise Pass193Error("HHS_P193_RIGHTS_METADATA_REQUIRED")
        manifest = {
            "artifact_identity": package_id,
            "source_identity": package["source_graph_identity"],
            "rights": dict(rights),
            "payloads": package["payloads"],
            "capabilities": package["capabilities"],
            "provenance": "CONTENT_ADDRESSED_IMMUTABLE",
            "receipts": [package["package_receipt_hash72"]],
            "replay": "REQUIRED",
            "execution_authorized": False,
            "identity_is_execution_authority": False,
        }
        nft_id = _hash216("HHS-P193-NFT-EXECUTABLE", manifest)
        manifest["nft_executable_id"] = nft_id
        receipt = self._append_receipt("NFTExecutable.Create", nft_id, manifest, authority_execution)
        manifest["receipt_hash72"] = receipt["receipt_hash72"]
        index = self._read_index()
        index["nft_executables"][nft_id] = manifest
        self._write_index(index)
        return manifest

    def authorize_execution(
        self,
        nft_executable_id: str,
        *,
        identity_verified: bool,
        capability_admitted: bool,
        platform_validated: bool,
        policy_accepted: bool,
        runtime_integrity: bool,
        authority_execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        index = self._read_index()
        manifest = index["nft_executables"].get(nft_executable_id)
        if not manifest:
            raise Pass193Error("HHS_P193_NFT_EXECUTABLE_NOT_FOUND")
        checks = {
            "identity_verified": identity_verified,
            "capability_admitted": capability_admitted,
            "platform_validated": platform_validated,
            "policy_accepted": policy_accepted,
            "runtime_integrity": runtime_integrity,
        }
        if not all(value is True for value in checks.values()):
            raise Pass193Error("HHS_P193_EXECUTION_ADMISSION_DENIED")
        result = {
            "nft_executable_id": nft_executable_id,
            "execution_authorized": True,
            "identity_is_execution_authority": False,
            "checks": checks,
        }
        receipt = self._append_receipt(
            "NFTExecutable.AuthorizeExecution",
            nft_executable_id,
            result,
            authority_execution,
        )
        result["receipt_hash72"] = receipt["receipt_hash72"]
        return result

    def replay(self) -> dict[str, Any]:
        if not self.receipt_path.exists():
            return {"ok": True, "receipt_count": 0, "terminal_receipt_hash72": None}
        previous = None
        count = 0
        for raw in self.receipt_path.read_text("utf-8").splitlines():
            if not raw:
                continue
            record = json.loads(raw)
            if record["sequence"] != count:
                raise Pass193Error("HHS_P193_REPLAY_SEQUENCE_DIVERGENCE")
            if record["previous_receipt_hash72"] != previous:
                raise Pass193Error("HHS_P193_REPLAY_CHAIN_DIVERGENCE")
            expected_payload = {key: value for key, value in record.items() if key != "receipt_hash72"}
            expected = _hash72("HHS-P193-RECEIPT", expected_payload)
            if expected != record["receipt_hash72"] or not validate_hash72(record["receipt_hash72"]):
                raise Pass193Error("HHS_P193_REPLAY_RECEIPT_DIVERGENCE")
            previous = record["receipt_hash72"]
            count += 1
        return {"ok": True, "receipt_count": count, "terminal_receipt_hash72": previous}


__all__ = [
    "CONTRACT_ID",
    "VERSION",
    "CONTRACT_AUTHORIZATION_COMMIT",
    "CONTRACT_BASELINE_COMMIT",
    "FROZEN_I132",
    "REGULAR_3D",
    "REGULAR_4D",
    "REGULAR_HIGH_DIMENSION",
    "SUPPORTED_TARGETS",
    "Pass193Error",
    "Pass193Runtime",
    "NativeEvidence",
    "native_probe_source",
]
