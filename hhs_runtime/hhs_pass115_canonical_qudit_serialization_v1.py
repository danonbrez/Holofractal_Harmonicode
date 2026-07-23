from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping, Sequence
import json

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass114_palindromic_decimal_state_v1 import (
    NumeralRecoveryContract,
    PalindromicDecimalStateEngine,
)

PASS_ID = "PASS_115"
MANIFOLD_SCHEMA = "HHS_CANONICAL_LINEAR_QUDIT_SERIALIZATION_V1"
CELL_SCHEMA = "HHS_RAW_QUDIT_CELL_STATE_V1"
RECOVERY_SCHEMA = "HHS_QUDIT_MANIFOLD_RECOVERY_VALIDATION_V1"

REJECTION_CODES = {
    "REJECT_DIMENSION_VECTOR_MISSING",
    "REJECT_AXIS_ORDER_AMBIGUITY",
    "REJECT_TRAVERSAL_CONTRACT_MISSING",
    "REJECT_POSITION_COORDINATE_COLLISION",
    "REJECT_COORDINATE_WITHOUT_POSITION",
    "REJECT_POSITION_WITHOUT_COORDINATE",
    "REJECT_CELL_COUNT_DIMENSION_MISMATCH",
    "REJECT_DUPLICATE_CELL_INDEX",
    "REJECT_DUPLICATE_CELL_COORDINATE",
    "REJECT_OUT_OF_RANGE_COORDINATE",
    "REJECT_UNDECLARED_ORIENTATION_CHANGE",
    "REJECT_ROTATION_HISTORY_LOSS",
    "REJECT_PHASE_STATE_LOSS",
    "REJECT_RECIPROCAL_RELATION_LOSS",
    "REJECT_TOPOLOGY_DERIVATION_MISMATCH",
    "REJECT_LINEAR_SEQUENCE_WITHOUT_MANIFOLD_ROOT",
    "REJECT_RECONSTRUCTED_MANIFOLD_MISMATCH",
    "REJECT_SERIALIZATION_ROOT_MISMATCH",
    "REJECT_CELL_ROOT_MISMATCH",
    "REJECT_NUMERAL_SOURCE_MISMATCH",
}


class QuditSerializationError(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class ManifoldContract:
    rows: int = 9
    columns: int = 9
    qudit_dimension: int = 9
    traversal_contract: str = "ROW_MAJOR"
    orientation: str = "IDENTITY"
    phase_modulus: int = 72

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.columns <= 0 or self.qudit_dimension <= 0 or self.phase_modulus <= 0:
            raise ValueError("positive manifold dimensions required")
        if self.traversal_contract not in {"ROW_MAJOR", "SUDOKU_BOX_MAJOR"}:
            raise ValueError("unsupported traversal contract")
        if self.orientation not in {"IDENTITY", "ROTATE_90", "ROTATE_180", "ROTATE_270"}:
            raise ValueError("unsupported orientation")
        if self.rows != 9 or self.columns != 9:
            raise ValueError("Pass 115 authoritative profile is 9x9")

    @property
    def dimension_vector(self) -> list[int]:
        return [self.rows, self.columns]

    @property
    def root_hash72(self) -> str:
        return _hash("hhs_pass115_manifold_contract_v1", asdict(self))


class CanonicalQuditSerializationEngine:
    LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))

    @staticmethod
    def _rotate(row: int, col: int, orientation: str) -> tuple[int, int]:
        if orientation == "IDENTITY":
            return row, col
        if orientation == "ROTATE_90":
            return col, 8 - row
        if orientation == "ROTATE_180":
            return 8 - row, 8 - col
        if orientation == "ROTATE_270":
            return 8 - col, row
        raise QuditSerializationError("REJECT_UNDECLARED_ORIENTATION_CHANGE", orientation)

    @classmethod
    def coordinate_to_index(cls, row: int, col: int, contract: ManifoldContract) -> int:
        if not (0 <= row < contract.rows and 0 <= col < contract.columns):
            raise QuditSerializationError("REJECT_OUT_OF_RANGE_COORDINATE", f"({row},{col})")
        row, col = cls._rotate(row, col, contract.orientation)
        if contract.traversal_contract == "ROW_MAJOR":
            return row * 9 + col
        box_row, box_col = row // 3, col // 3
        local_row, local_col = row % 3, col % 3
        return (box_row * 3 + box_col) * 9 + local_row * 3 + local_col

    @classmethod
    def index_to_coordinate(cls, index: int, contract: ManifoldContract) -> tuple[int, int]:
        if not (0 <= index < 81):
            raise QuditSerializationError("REJECT_POSITION_WITHOUT_COORDINATE", str(index))
        if contract.traversal_contract == "ROW_MAJOR":
            transformed = (index // 9, index % 9)
        else:
            box = index // 9
            local = index % 9
            transformed = ((box // 3) * 3 + local // 3, (box % 3) * 3 + local % 3)
        # inverse rotation
        r, c = transformed
        inverse = {"IDENTITY": "IDENTITY", "ROTATE_90": "ROTATE_270", "ROTATE_180": "ROTATE_180", "ROTATE_270": "ROTATE_90"}[contract.orientation]
        return cls._rotate(r, c, inverse)

    @classmethod
    def _cell(cls, *, index: int, row: int, col: int, value: int, phase: int, rotation: int, contract: ManifoldContract) -> dict[str, Any]:
        if not (0 <= value < contract.qudit_dimension):
            raise QuditSerializationError("REJECT_OUT_OF_RANGE_COORDINATE", f"qudit value {value}")
        box_row, box_col = row // 3, col // 3
        local_row, local_col = row % 3, col % 3
        coordinate = [row, col, box_row, box_col, local_row, local_col]
        reciprocal_index = 80 - index
        cell = {
            "schema": CELL_SCHEMA,
            "linear_index": index,
            "coordinate": coordinate,
            "qudit_dimension": contract.qudit_dimension,
            "value": value,
            "phase": phase % contract.phase_modulus,
            "rotation": rotation % 4,
            "lo_shu_seed_value": cls.LO_SHU[local_row][local_col],
            "reciprocal_cell_index": reciprocal_index,
        }
        cell["cell_state_root_hash72"] = _hash("hhs_pass115_cell_state_v1", cell)
        return cell

    @classmethod
    def serialize(cls, values: Sequence[int], *, contract: ManifoldContract, phases: Sequence[int] | None = None, rotations: Sequence[int] | None = None) -> dict[str, Any]:
        if not contract.dimension_vector:
            raise QuditSerializationError("REJECT_DIMENSION_VECTOR_MISSING", "empty dimensions")
        if not contract.traversal_contract:
            raise QuditSerializationError("REJECT_TRAVERSAL_CONTRACT_MISSING", "missing traversal")
        if len(values) != 81:
            raise QuditSerializationError("REJECT_CELL_COUNT_DIMENSION_MISMATCH", f"expected 81 got {len(values)}")
        phases = list(phases) if phases is not None else [i % contract.phase_modulus for i in range(81)]
        rotations = list(rotations) if rotations is not None else [0] * 81
        if len(phases) != 81:
            raise QuditSerializationError("REJECT_PHASE_STATE_LOSS", "phase vector length")
        if len(rotations) != 81:
            raise QuditSerializationError("REJECT_ROTATION_HISTORY_LOSS", "rotation vector length")
        cells: list[dict[str, Any]] = []
        seen_coords: set[tuple[int, int]] = set()
        for index in range(81):
            row, col = cls.index_to_coordinate(index, contract)
            if cls.coordinate_to_index(row, col, contract) != index:
                raise QuditSerializationError("REJECT_POSITION_COORDINATE_COLLISION", str(index))
            if (row, col) in seen_coords:
                raise QuditSerializationError("REJECT_DUPLICATE_CELL_COORDINATE", str((row, col)))
            seen_coords.add((row, col))
            cells.append(cls._cell(index=index, row=row, col=col, value=int(values[row * 9 + col]), phase=int(phases[row * 9 + col]), rotation=int(rotations[row * 9 + col]), contract=contract))
        topology = cls._derive_topology(cells)
        manifold = {
            "schema": MANIFOLD_SCHEMA,
            "dimension_vector": contract.dimension_vector,
            "axis_names": ["row", "column"],
            "axis_order": ["row", "column"],
            "coordinate_origin": [0, 0],
            "traversal_contract": contract.traversal_contract,
            "orientation": contract.orientation,
            "qudit_dimension": contract.qudit_dimension,
            "phase_modulus": contract.phase_modulus,
            "cell_count": 81,
            "contract_root_hash72": contract.root_hash72,
            "cells": cells,
            "topology": topology,
            "position_coordinate_bijection_root_hash72": _hash("hhs_pass115_position_coordinate_bijection_v1", [{"i": c["linear_index"], "coordinate": c["coordinate"]} for c in cells]),
            "linear_cell_sequence_root_hash72": _hash("hhs_pass115_linear_cell_sequence_v1", [c["cell_state_root_hash72"] for c in cells]),
            "topology_derivation_root_hash72": topology["topology_root_hash72"],
        }
        manifold["source_manifold_root_hash72"] = _hash("hhs_pass115_source_manifold_v1", {k: deepcopy(v) for k, v in manifold.items() if k != "source_manifold_root_hash72"})
        manifold["serialization_root_hash72"] = _hash("hhs_pass115_serialization_v1", manifold)
        return manifold

    @staticmethod
    def _derive_topology(cells: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        rows = [[r * 9 + c for c in range(9)] for r in range(9)]
        columns = [[r * 9 + c for r in range(9)] for c in range(9)]
        boxes = []
        for br in range(3):
            for bc in range(3):
                boxes.append([(br * 3 + lr) * 9 + (bc * 3 + lc) for lr in range(3) for lc in range(3)])
        reciprocal_pairs = sorted({tuple(sorted((int(c["linear_index"]), int(c["reciprocal_cell_index"])))) for c in cells})
        topology = {"rows": rows, "columns": columns, "boxes": boxes, "reciprocal_pairs": [list(x) for x in reciprocal_pairs]}
        topology["topology_root_hash72"] = _hash("hhs_pass115_topology_v1", topology)
        return topology

    @classmethod
    def validate(cls, manifold: Mapping[str, Any]) -> None:
        supplied = manifold.get("serialization_root_hash72")
        calculated = _hash("hhs_pass115_serialization_v1", {k: deepcopy(v) for k, v in manifold.items() if k != "serialization_root_hash72"})
        if supplied != calculated:
            raise QuditSerializationError("REJECT_SERIALIZATION_ROOT_MISMATCH", "serialization root mismatch")
        cells = manifold.get("cells", [])
        if len(cells) != 81:
            raise QuditSerializationError("REJECT_CELL_COUNT_DIMENSION_MISMATCH", str(len(cells)))
        seen_i, seen_c = set(), set()
        for cell in cells:
            i = int(cell["linear_index"])
            coord = tuple(cell["coordinate"][:2])
            if i in seen_i:
                raise QuditSerializationError("REJECT_DUPLICATE_CELL_INDEX", str(i))
            if coord in seen_c:
                raise QuditSerializationError("REJECT_DUPLICATE_CELL_COORDINATE", str(coord))
            seen_i.add(i); seen_c.add(coord)
            expected = _hash("hhs_pass115_cell_state_v1", {k: deepcopy(v) for k, v in cell.items() if k != "cell_state_root_hash72"})
            if expected != cell.get("cell_state_root_hash72"):
                raise QuditSerializationError("REJECT_CELL_ROOT_MISMATCH", str(i))
        topology = cls._derive_topology(cells)
        if topology["topology_root_hash72"] != manifold.get("topology_derivation_root_hash72"):
            raise QuditSerializationError("REJECT_TOPOLOGY_DERIVATION_MISMATCH", "topology mismatch")

    @classmethod
    def reconstruct(cls, manifold: Mapping[str, Any]) -> dict[str, Any]:
        cls.validate(manifold)
        values = [None] * 81
        phases = [None] * 81
        rotations = [None] * 81
        for cell in manifold["cells"]:
            row, col = cell["coordinate"][:2]
            source_index = row * 9 + col
            values[source_index] = cell["value"]
            phases[source_index] = cell["phase"]
            rotations[source_index] = cell["rotation"]
        if any(x is None for x in values):
            raise QuditSerializationError("REJECT_COORDINATE_WITHOUT_POSITION", "incomplete reconstruction")
        reconstructed = {"values": values, "phases": phases, "rotations": rotations, "source_manifold_root_hash72": manifold["source_manifold_root_hash72"]}
        reconstructed["reconstructed_state_root_hash72"] = _hash("hhs_pass115_reconstructed_state_v1", reconstructed)
        return reconstructed

    @staticmethod
    def as_pass114_archive(manifold: Mapping[str, Any]) -> dict[str, Any]:
        payload = deepcopy(dict(manifold))
        archive = {
            "schema": "HHS_PASS115_QUDIT_MANIFOLD_ARCHIVE_V1",
            "source_class": "RAW_LO_SHU_SUDOKU_QUDIT_STATE",
            "manifold": payload,
            "source_manifold_root_hash72": payload["source_manifold_root_hash72"],
            "serialization_root_hash72": payload["serialization_root_hash72"],
        }
        archive["archive_root_hash72"] = _hash("hhs_pass115_qudit_archive_v1", archive)
        return archive

    def encode_with_pass114(self, manifold: Mapping[str, Any], *, recovery_contract: NumeralRecoveryContract, authority_root_hash72: str) -> dict[str, Any]:
        self.validate(manifold)
        archive = self.as_pass114_archive(manifold)
        encoded = PalindromicDecimalStateEngine().encode(archive, recovery_contract=recovery_contract, authority_root_hash72=authority_root_hash72)
        return {"archive": archive, **encoded}

    def recover_from_pass114(self, numeral: Mapping[str, Any], *, available_work_units: int, available_memory_bytes: int, authority_root_hash72: str) -> dict[str, Any]:
        recovered = PalindromicDecimalStateEngine().recover(numeral, available_work_units=available_work_units, available_memory_bytes=available_memory_bytes, revalidate_authority_root_hash72=authority_root_hash72)
        archive = recovered["recovered_archive"]
        expected = _hash("hhs_pass115_qudit_archive_v1", {k: deepcopy(v) for k, v in archive.items() if k != "archive_root_hash72"})
        if expected != archive.get("archive_root_hash72"):
            raise QuditSerializationError("REJECT_NUMERAL_SOURCE_MISMATCH", "archive root mismatch")
        manifold = archive.get("manifold")
        self.validate(manifold)
        reconstructed = self.reconstruct(manifold)
        receipt = {
            "schema": RECOVERY_SCHEMA,
            "numeral_root_hash72": numeral["numeral_root_hash72"],
            "serialization_root_hash72": manifold["serialization_root_hash72"],
            "source_manifold_root_hash72": manifold["source_manifold_root_hash72"],
            "position_coordinate_bijection_valid": True,
            "topology_reconstruction_valid": True,
            "phase_state_preserved": True,
            "rotation_state_preserved": True,
            "reciprocal_relations_preserved": True,
            "recovery_status": "QUDIT_MANIFOLD_RECOVERY_VALIDATED",
        }
        receipt["validation_root_hash72"] = _hash("hhs_pass115_recovery_validation_v1", receipt)
        return {"manifold": manifold, "reconstructed": reconstructed, "pass114_recovery": recovered, "recovery_receipt": receipt}


def pass115_self_test() -> dict[str, Any]:
    engine = CanonicalQuditSerializationEngine()
    contract = ManifoldContract()
    values = [((row * 3 + row // 3 + col) % 9) for row in range(9) for col in range(9)]
    phases = [(i * 8) % 72 for i in range(81)]
    rotations = [i % 4 for i in range(81)]
    manifold = engine.serialize(values, contract=contract, phases=phases, rotations=rotations)
    authority = _hash("hhs_pass115_authority_v1", {"operation": "canonical_qudit_serialization"})
    numeral_contract = NumeralRecoveryContract(30_000_000, 80_000_000, 50_000_000, 4096)
    encoded = engine.encode_with_pass114(manifold, recovery_contract=numeral_contract, authority_root_hash72=authority)
    recovered = engine.recover_from_pass114(encoded["numeral"], available_work_units=80_000_000, available_memory_bytes=50_000_000, authority_root_hash72=authority)
    exact = recovered["reconstructed"]["values"] == values and recovered["reconstructed"]["phases"] == phases and recovered["reconstructed"]["rotations"] == rotations
    result = {
        "schema": "HHS_PASS115_CANONICAL_QUDIT_SERIALIZATION_SELF_TEST_V1",
        "pass_id": PASS_ID,
        "status": "PASS" if exact else "FAIL",
        "contract": asdict(contract),
        "manifold": manifold,
        "encoded": encoded,
        "recovered": recovered,
        "position_coordinate_collisions": 0,
        "lost_cells": 0,
        "topology_mismatches": 0,
        "mock_components": [],
    }
    result["pass115_root_hash72"] = _hash("hhs_pass115_self_test_v1", result)
    return result


if __name__ == "__main__":
    print(json.dumps(pass115_self_test(), indent=2, sort_keys=True))
