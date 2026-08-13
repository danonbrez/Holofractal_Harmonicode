"""Pass 217 Iteration 4 Hash72 manifold and immutable-nucleus validator.

Iteration 4 does not regenerate or promote the Iteration 3 Genesis candidate.
It binds the already-merged Pass 215/216 reconciliation lineage, proves the
72x72 wrapped Hash72 geometry, and validates the central 3x3 Lo Shu/phase
nucleus against the exact frozen Iteration 3 candidate bytes.

Canonical authority remains unchanged: no ROM promotion, Hash72/Hash216
transition minting, Golay materialization, VM81 mutation, or Pass 219 runtime
implementation occurs here.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass217_machine_contracts_v1 import (
    HASH72_ALPHABET,
    HASH72_SIDE,
    LO_SHU,
    LO_SHU_PHASE_CHANNELS,
    hash72_matrix_root,
    orbit_coordinate,
)
from hhs_backend.runtime.hhs_pass217_genesis_candidate_v1 import (
    ADDRESS_MAP_PATH,
    CANDIDATE_PATH,
    LOGICAL_BYTES,
    build_candidate_bytes,
)

PASS_NUMBER = 217
ITERATION = 4
SCHEMA = "HHS_PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS_V1"
CLASSIFICATION = (
    "HHS_PASS_217_ITERATION_4_RECONCILED_HASH72_MANIFOLD_NUCLEUS_VERIFIED"
)

BASE_MAIN_COMMIT = "3b55da5e8aa67491f113d1b9e9c7e481aeb1e18c"
BASE_MAIN_TREE = "a75c87a891d7326a1e01844dd5c7223acbb50940"
PASS216_MERGE_COMMIT = "f10e453c5d7c7467cf5e57f6452958491fe763ad"
ITERATION3_COMMIT = "947be39fd67700f307ff80d96c3a10c3acaa29cc"
ITERATION3_TREE = "f8d0af49e3574ea77657a79507601ae96f75918c"
ITERATION4_RECONCILIATION_COMMIT = "724e91c5fb1009cefc52778c3e73338257b2814c"

EXPECTED_CANDIDATE_SHA256 = (
    "97379c7ae7cdaebd8031a3a3fb58559c967b361b360c7db34ec096acabfc8fe8"
)
EXPECTED_ADDRESS_MAP_SHA256 = (
    "2f8d8a23114b87f2dbe91f3d302ef089b750f9d91f533d744a4524e907717f5f"
)
EXPECTED_HASH72_MATRIX_ROOT = (
    "6c0b2e9e354e8d7eb17a746d01c157b19aa95b58296884126cdf5bef7998e286"
)
EXPECTED_NUCLEUS_IDENTITY_ROOT = (
    "da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164"
)
EXPECTED_ANCHOR_ORBIT_ROOT = (
    "556a7828594f8a56cfec8d8f3af473330fffcae4f24c44ffc37616c681e69f09"
)
EXPECTED_MANIFOLD_ROOT = (
    "c757bae150d9ab94485c680ec3143e715b674d35f445a72c6fb4ea2def6f7884"
)
EXPECTED_NUCLEUS_SUPPORT_ROOT = (
    "ac46211412784990e08e5cf0b80df5db381aad612a7ccd8aa816815a105b0294"
)
EXPECTED_PROTECTED_RUNTIME_BLOB = "362cd6e892ae66024333b111aec83f12023fdce3"

SCHEMA_PATH = (
    "contracts/pass217/PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS.schema.json"
)
EVIDENCE_PATH = (
    "evidence/pass217/PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS.json"
)

DIRECTION_DELTAS: dict[str, tuple[int, int]] = {
    "x": (0, 1),
    "y": (1, 0),
    "z": (1, 1),
    "w": (1, -1),
}
ORBIT_ANCHORS: tuple[tuple[int, int], ...] = (
    (0, 0),
    (0, 71),
    (35, 36),
    (71, 0),
    (71, 71),
)
NUCLEUS_CELLS: tuple[int, ...] = (30, 31, 32, 39, 40, 41, 48, 49, 50)


class Pass217Iteration4Error(RuntimeError):
    """Raised when Iteration 4 fails closed."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _json_file_bytes(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def _domain_digest(domain: bytes, rows: Sequence[Any]) -> str:
    state = sha256(domain)
    for row in rows:
        encoded = canonical_bytes(row)
        state.update(len(encoded).to_bytes(8, "big"))
        state.update(encoded)
    return state.hexdigest()


def _git(root: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise Pass217Iteration4Error(
            f"PASS217_ITERATION4_GIT_FAILURE:{' '.join(args)}:{detail}"
        )
    return completed.stdout.decode("utf-8", "surrogateescape").strip()


def _require_ancestor(root: Path, commit: str, label: str) -> None:
    completed = subprocess.run(
        ("git", "-C", str(root), "merge-base", "--is-ancestor", commit, "HEAD"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise Pass217Iteration4Error(
            f"PASS217_ITERATION4_MISSING_ANCESTRY:{label}:{commit}"
        )


def _file_sha256(root: Path, path: str) -> str:
    target = root / path
    if not target.is_file():
        raise Pass217Iteration4Error(
            f"PASS217_ITERATION4_REQUIRED_FILE_MISSING:{path}"
        )
    return sha256(target.read_bytes()).hexdigest()


def _require_frozen_inputs(root: Path) -> None:
    if _file_sha256(root, CANDIDATE_PATH) != EXPECTED_CANDIDATE_SHA256:
        raise Pass217Iteration4Error("PASS217_ITERATION4_CANDIDATE_DRIFT")
    if _file_sha256(root, ADDRESS_MAP_PATH) != EXPECTED_ADDRESS_MAP_SHA256:
        raise Pass217Iteration4Error("PASS217_ITERATION4_ADDRESS_MAP_DRIFT")
    protected_blob = _git(
        root, "rev-parse", f"HEAD:hhs_runtime/HARMONICODE_VM_RUNTIME.c"
    )
    if protected_blob != EXPECTED_PROTECTED_RUNTIME_BLOB:
        raise Pass217Iteration4Error("PASS217_ITERATION4_PROTECTED_RUNTIME_DRIFT")


def hash72_row(row: int) -> str:
    if not isinstance(row, int) or isinstance(row, bool) or not 0 <= row < HASH72_SIDE:
        raise Pass217Iteration4Error("PASS217_ITERATION4_HASH72_ROW_RANGE")
    return "".join(
        HASH72_ALPHABET[(row + column) % HASH72_SIDE]
        for column in range(HASH72_SIDE)
    )


def direction_order(direction: str) -> int:
    if direction not in DIRECTION_DELTAS:
        raise Pass217Iteration4Error("PASS217_ITERATION4_DIRECTION_INVALID")
    dr, dc = DIRECTION_DELTAS[direction]
    for step in range(1, HASH72_SIDE + 1):
        if (step * dr) % HASH72_SIDE == 0 and (step * dc) % HASH72_SIDE == 0:
            return step
    raise Pass217Iteration4Error("PASS217_ITERATION4_DIRECTION_ORDER")


def _linear(coordinate: tuple[int, int]) -> int:
    row, column = coordinate
    return HASH72_SIDE * row + column


def direction_step_root(direction: str) -> str:
    rows = []
    for row in range(HASH72_SIDE):
        for column in range(HASH72_SIDE):
            target = orbit_coordinate(direction, row, column, 1)
            rows.append(
                {
                    "source": HASH72_SIDE * row + column,
                    "target": _linear(target),
                }
            )
    return _domain_digest(
        f"HHS-P217-I4-HASH72-{direction.upper()}-STEP-V1\0".encode("ascii"),
        rows,
    )


def anchor_orbit_root() -> str:
    rows = []
    for direction in DIRECTION_DELTAS:
        for source in ORBIT_ANCHORS:
            coordinates = [
                list(orbit_coordinate(direction, source[0], source[1], step))
                for step in range(HASH72_SIDE)
            ]
            rows.append(
                {
                    "direction": direction,
                    "source": list(source),
                    "coordinates": coordinates,
                }
            )
    return _domain_digest(b"HHS-P217-I4-HASH72-ANCHOR-ORBITS-V1\0", rows)


def validate_hash72_manifold() -> dict[str, Any]:
    if len(HASH72_ALPHABET) != HASH72_SIDE:
        raise Pass217Iteration4Error("PASS217_ITERATION4_HASH72_ALPHABET_SIZE")
    if len(set(HASH72_ALPHABET)) != HASH72_SIDE:
        raise Pass217Iteration4Error("PASS217_ITERATION4_HASH72_ALPHABET_ALIAS")
    if hash72_matrix_root() != EXPECTED_HASH72_MATRIX_ROOT:
        raise Pass217Iteration4Error("PASS217_ITERATION4_HASH72_MATRIX_ROOT")

    expected_symbols = set(HASH72_ALPHABET)
    for row in range(HASH72_SIDE):
        if set(hash72_row(row)) != expected_symbols:
            raise Pass217Iteration4Error(
                f"PASS217_ITERATION4_HASH72_ROW_NOT_PERMUTATION:{row}"
            )
    for column in range(HASH72_SIDE):
        column_symbols = {
            HASH72_ALPHABET[(row + column) % HASH72_SIDE]
            for row in range(HASH72_SIDE)
        }
        if column_symbols != expected_symbols:
            raise Pass217Iteration4Error(
                f"PASS217_ITERATION4_HASH72_COLUMN_NOT_PERMUTATION:{column}"
            )

    directions = []
    all_coordinates = {
        (row, column)
        for row in range(HASH72_SIDE)
        for column in range(HASH72_SIDE)
    }
    for direction in DIRECTION_DELTAS:
        order = direction_order(direction)
        if order != HASH72_SIDE:
            raise Pass217Iteration4Error(
                f"PASS217_ITERATION4_ORBIT_ORDER:{direction}:{order}"
            )
        targets = {
            orbit_coordinate(direction, row, column, 1)
            for row, column in all_coordinates
        }
        if targets != all_coordinates:
            raise Pass217Iteration4Error(
                f"PASS217_ITERATION4_ORBIT_NOT_BIJECTIVE:{direction}"
            )
        for row, column in all_coordinates:
            source = (row, column)
            if orbit_coordinate(direction, row, column, HASH72_SIDE) != source:
                raise Pass217Iteration4Error(
                    f"PASS217_ITERATION4_ORBIT_NOT_CLOSED:{direction}"
                )
            forward = orbit_coordinate(direction, row, column, 1)
            if orbit_coordinate(direction, forward[0], forward[1], -1) != source:
                raise Pass217Iteration4Error(
                    f"PASS217_ITERATION4_ORBIT_INVERSE:{direction}"
                )
        for source in ORBIT_ANCHORS:
            orbit = {
                orbit_coordinate(direction, source[0], source[1], step)
                for step in range(HASH72_SIDE)
            }
            if len(orbit) != HASH72_SIDE:
                raise Pass217Iteration4Error(
                    f"PASS217_ITERATION4_ANCHOR_ORBIT_ALIAS:{direction}:{source}"
                )
        directions.append(
            {
                "direction": direction,
                "delta": list(DIRECTION_DELTAS[direction]),
                "order": order,
                "one_step_permutation_count": len(targets),
                "one_step_root_sha256": direction_step_root(direction),
            }
        )

    anchors_root = anchor_orbit_root()
    if anchors_root != EXPECTED_ANCHOR_ORBIT_ROOT:
        raise Pass217Iteration4Error("PASS217_ITERATION4_ANCHOR_ORBIT_ROOT")
    manifold_root = _domain_digest(
        b"HHS-P217-I4-HASH72-MANIFOLD-V1\0",
        [
            {"matrix_root_sha256": EXPECTED_HASH72_MATRIX_ROOT},
            *directions,
            {"anchor_orbit_root_sha256": anchors_root},
        ],
    )
    if manifold_root != EXPECTED_MANIFOLD_ROOT:
        raise Pass217Iteration4Error("PASS217_ITERATION4_MANIFOLD_ROOT")
    return {
        "alphabet": HASH72_ALPHABET,
        "symbol_count": HASH72_SIDE,
        "matrix_positions": HASH72_SIDE * HASH72_SIDE,
        "matrix_root_sha256": EXPECTED_HASH72_MATRIX_ROOT,
        "wrapped_directions": directions,
        "anchor_count": len(ORBIT_ANCHORS),
        "anchor_orbit_root_sha256": anchors_root,
        "manifold_root_sha256": manifold_root,
    }


def nucleus_identity_root() -> str:
    payload = {
        "values": [list(row) for row in LO_SHU],
        "phase_channels": [
            [list(cell) for cell in row] for row in LO_SHU_PHASE_CHANNELS
        ],
        "fixed_pointwise": True,
    }
    return sha256(canonical_bytes(payload)).hexdigest()


def nucleus_records(image: bytes) -> list[dict[str, Any]]:
    if len(image) != LOGICAL_BYTES:
        raise Pass217Iteration4Error("PASS217_ITERATION4_CANDIDATE_SIZE")
    rows = []
    for local_row in range(3):
        for local_column in range(3):
            row = local_row + 3
            column = local_column + 3
            cell = 9 * row + column
            value = LO_SHU[local_row][local_column]
            channel_value, channel = LO_SHU_PHASE_CHANNELS[local_row][local_column]
            shard = image[cell * 8 : cell * 8 + 8]
            rows.append(
                {
                    "cell": cell,
                    "row": row,
                    "column": column,
                    "value": value,
                    "phase_channel": channel,
                    "phase_channel_value": channel_value,
                    "shard_hex": shard.hex(),
                    "shard_one_bits": sum(byte.bit_count() for byte in shard),
                }
            )
    return rows


def validate_nucleus_bytes(image: bytes) -> dict[str, Any]:
    if nucleus_identity_root() != EXPECTED_NUCLEUS_IDENTITY_ROOT:
        raise Pass217Iteration4Error("PASS217_ITERATION4_NUCLEUS_IDENTITY_ROOT")
    expected = build_candidate_bytes()
    if len(image) != LOGICAL_BYTES:
        raise Pass217Iteration4Error("PASS217_ITERATION4_CANDIDATE_SIZE")
    records = nucleus_records(image)
    if tuple(row["cell"] for row in records) != NUCLEUS_CELLS:
        raise Pass217Iteration4Error("PASS217_ITERATION4_NUCLEUS_CELL_ORDER")
    for record in records:
        cell = record["cell"]
        observed = image[cell * 8 : cell * 8 + 8]
        expected_shard = expected[cell * 8 : cell * 8 + 8]
        if observed != expected_shard:
            raise Pass217Iteration4Error(
                f"PASS217_ITERATION4_NUCLEUS_SHARD_DRIFT:{cell}"
            )
        if record["shard_one_bits"] != 32:
            raise Pass217Iteration4Error(
                f"PASS217_ITERATION4_NUCLEUS_BALANCE:{cell}"
            )
        local_row = record["row"] - 3
        local_column = record["column"] - 3
        expected_value = LO_SHU[local_row][local_column]
        expected_channel_value, expected_channel = (
            LO_SHU_PHASE_CHANNELS[local_row][local_column]
        )
        if record["value"] != expected_value:
            raise Pass217Iteration4Error("PASS217_ITERATION4_NUCLEUS_VALUE")
        if (
            record["phase_channel_value"] != expected_channel_value
            or record["phase_channel"] != expected_channel
        ):
            raise Pass217Iteration4Error("PASS217_ITERATION4_NUCLEUS_CHANNEL")
    support_root = _domain_digest(
        b"HHS-P217-I4-IMMUTABLE-NUCLEUS-SUPPORT-V1\0", records
    )
    if support_root != EXPECTED_NUCLEUS_SUPPORT_ROOT:
        raise Pass217Iteration4Error("PASS217_ITERATION4_NUCLEUS_SUPPORT_ROOT")
    return {
        "fixed_pointwise": True,
        "central_cell_indices": list(NUCLEUS_CELLS),
        "identity_root_sha256": EXPECTED_NUCLEUS_IDENTITY_ROOT,
        "support_bits": len(NUCLEUS_CELLS) * 64,
        "support_root_sha256": support_root,
        "pointwise_records": records,
    }


def _claim_boundary() -> dict[str, bool]:
    return {
        "authoritative_hash216_transition_minted": False,
        "authoritative_hash72_transition_receipt_minted": False,
        "canonical_authority_promoted": False,
        "canonical_genesis_selected": False,
        "golay_codec_implemented": False,
        "golay_physical_rom_generated": False,
        "hash72_manifold_validated": True,
        "immutable_nucleus_validated": True,
        "logical_genesis_rom_generated": False,
        "migration_started": False,
        "pass217_implementation_complete": False,
        "pass219_runtime_implementation_started": False,
        "predecessor_reconciliation_complete": True,
        "protected_c_runtime_modified": False,
        "runtime_mutation_performed": False,
    }


def build_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://hhs.local/contracts/pass217/"
            "PASS_217_ITERATION_4_HASH72_MANIFOLD_NUCLEUS.schema.json"
        ),
        "title": "HHS Pass 217 Iteration 4 Hash72 Manifold and Immutable Nucleus",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema",
            "classification",
            "pass",
            "iteration",
            "base_authority",
            "inheritance_gate",
            "frozen_inputs",
            "hash72_manifold",
            "immutable_nucleus",
            "claim_boundary",
            "next_action",
            "record_root_sha256",
        ],
        "properties": {
            "schema": {"const": SCHEMA},
            "classification": {"const": CLASSIFICATION},
            "pass": {"const": PASS_NUMBER},
            "iteration": {"const": ITERATION},
            "base_authority": {"type": "object"},
            "inheritance_gate": {"type": "object"},
            "frozen_inputs": {"type": "object"},
            "hash72_manifold": {"type": "object"},
            "immutable_nucleus": {"type": "object"},
            "claim_boundary": {"type": "object"},
            "next_action": {"type": "string", "minLength": 1},
            "record_root_sha256": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
        },
    }


def build_record(repository_root: Path | str) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    _require_ancestor(root, PASS216_MERGE_COMMIT, "PASS216_MERGE")
    _require_ancestor(
        root, ITERATION4_RECONCILIATION_COMMIT, "ITERATION4_RECONCILIATION"
    )
    _require_ancestor(root, BASE_MAIN_COMMIT, "ITERATION4_BASE_MAIN")
    _require_frozen_inputs(root)

    manifold = validate_hash72_manifold()
    candidate = (root / CANDIDATE_PATH).read_bytes()
    nucleus = validate_nucleus_bytes(candidate)
    if candidate != build_candidate_bytes():
        raise Pass217Iteration4Error("PASS217_ITERATION4_CANDIDATE_REBUILD_DRIFT")

    record: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "base_authority": {
            "main_parent_commit": BASE_MAIN_COMMIT,
            "main_parent_tree": BASE_MAIN_TREE,
            "pass216_merge_commit": PASS216_MERGE_COMMIT,
            "iteration3_commit": ITERATION3_COMMIT,
            "iteration3_tree": ITERATION3_TREE,
            "iteration4_reconciliation_commit": ITERATION4_RECONCILIATION_COMMIT,
            "merge_target": "main",
        },
        "inheritance_gate": {
            "status": "RECONCILED_VALIDATION_ONLY_NO_CANONICAL_PROMOTION",
            "predecessor_reconciliation_complete": True,
            "historical_iteration1_3_hold_fields_preserved_as_provenance": True,
            "iteration1_3_artifacts_regenerated": False,
            "canonical_promotion_allowed_by_iteration4": False,
        },
        "frozen_inputs": {
            "logical_genesis_candidate": {
                "path": CANDIDATE_PATH,
                "sha256": EXPECTED_CANDIDATE_SHA256,
                "byte_count": LOGICAL_BYTES,
            },
            "address_map": {
                "path": ADDRESS_MAP_PATH,
                "sha256": EXPECTED_ADDRESS_MAP_SHA256,
            },
            "protected_vm81_runtime": {
                "path": "hhs_runtime/HARMONICODE_VM_RUNTIME.c",
                "git_blob": EXPECTED_PROTECTED_RUNTIME_BLOB,
                "modified": False,
            },
        },
        "hash72_manifold": manifold,
        "immutable_nucleus": nucleus,
        "claim_boundary": _claim_boundary(),
        "next_action": (
            "Continue Pass 217 with the next dependency-scoped implementation "
            "surface without regenerating Iterations 1-3; canonical ROM/admission "
            "remains a separate explicit authority transition."
        ),
    }
    record["record_root_sha256"] = sha256(canonical_bytes(record)).hexdigest()
    return record


def validate_record(
    repository_root: Path | str,
    record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    expected = build_record(root)
    actual = (
        json.loads((root / EVIDENCE_PATH).read_text("utf-8"))
        if record is None
        else dict(record)
    )
    if actual != expected:
        raise Pass217Iteration4Error("PASS217_ITERATION4_EVIDENCE_DRIFT")
    observed_root = actual["record_root_sha256"]
    unsigned = dict(actual)
    del unsigned["record_root_sha256"]
    if observed_root != sha256(canonical_bytes(unsigned)).hexdigest():
        raise Pass217Iteration4Error("PASS217_ITERATION4_RECORD_ROOT")
    if dict(actual["claim_boundary"]) != _claim_boundary():
        raise Pass217Iteration4Error("PASS217_ITERATION4_CLAIM_BOUNDARY")
    schema_bytes = _json_file_bytes(build_schema())
    if (root / SCHEMA_PATH).read_bytes() != schema_bytes:
        raise Pass217Iteration4Error("PASS217_ITERATION4_SCHEMA_DRIFT")
    return {
        "classification": CLASSIFICATION,
        "record_root_sha256": observed_root,
        "hash72_manifold_root_sha256": actual["hash72_manifold"][
            "manifold_root_sha256"
        ],
        "nucleus_support_root_sha256": actual["immutable_nucleus"][
            "support_root_sha256"
        ],
        "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        "predecessor_reconciliation_complete": True,
        "canonical_authority_promoted": False,
    }


def write_record(
    repository_root: Path | str,
    output_path: Path | str = EVIDENCE_PATH,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    record = build_record(root)
    target = root / output_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(_json_file_bytes(record))
    return record


__all__ = [
    "CLASSIFICATION",
    "DIRECTION_DELTAS",
    "EVIDENCE_PATH",
    "ITERATION",
    "NUCLEUS_CELLS",
    "PASS_NUMBER",
    "Pass217Iteration4Error",
    "SCHEMA",
    "SCHEMA_PATH",
    "anchor_orbit_root",
    "build_record",
    "build_schema",
    "direction_order",
    "direction_step_root",
    "hash72_row",
    "nucleus_identity_root",
    "nucleus_records",
    "validate_hash72_manifold",
    "validate_nucleus_bytes",
    "validate_record",
    "write_record",
]
