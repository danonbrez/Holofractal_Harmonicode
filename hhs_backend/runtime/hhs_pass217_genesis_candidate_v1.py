"""Pass 217 Iteration 3 deterministic, non-promotional Genesis candidate.

The Pass 217 contract requires a 5,184-bit Genesis image, but the inherited
Pass 215/216 authority gate is still unresolved.  This module therefore builds
and exhaustively verifies candidate bytes and address-map bytes without
selecting them as the canonical ROM, mutating VM81, minting a transition, or
constructing the physical Golay image.

The candidate profile uses only frozen inherited integer identities:

* Pass 175's 64-entry phase table;
* the repository's 3x3 Lo Shu seed tiled over the 9x9 cell plane; and
* the Iteration 2 VM5184 address bijections.

All persisted formats are explicit, exact, and replayable.
"""
from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass217_machine_contracts_v1 import (
    BASE_COMMIT,
    INHERITANCE_HOLD,
    LO_SHU,
    LO_SHU_PHASE_CHANNELS,
    address_record,
    exhaustive_address_root,
)


SCHEMA = "HHS_PASS_217_ITERATION_3_GENESIS_CANDIDATE_BUNDLE_V1"
MANIFEST_SCHEMA = "HHS_PASS_217_ITERATION_3_GENESIS_CANDIDATE_MANIFEST_V1"
REFERENCE_SCHEMA = "HHS_PASS_217_ITERATION_3_GENESIS_CANDIDATE_REFERENCES_V1"
CLASSIFICATION = (
    "HHS_PASS_217_ITERATION_3_NON_PROMOTIONAL_GENESIS_CANDIDATE_VERIFIED"
)
PROFILE_ID = "HHS_P217_I3_LOSHU_PHASE_PARITY_CANDIDATE_V1"
PASS_NUMBER = 217
ITERATION = 3

ITERATION2_REMOTE_COMMIT = "bd20174c78127b0fffe9134bc10eac9a6d5445a2"
ITERATION2_TREE = "f6b5899ae0c77529dcf32400c817b8334e3faf4d"
ITERATION2_BUNDLE_ROOT = (
    "7c26c890eabbe8f4b506186ea738f0a4f2efed3391d02b73477a859edcf031f9"
)

VM81_CELLS = 81
VM81_SIDE = 9
OPERATIONS_PER_CELL = 64
PHASE_SIDE = 8
LOGICAL_BITS = 5_184
LOGICAL_BYTES = 648
HASH72_SIDE = 72
G243_CONTROLS = 243
PROJECTED_ADDRESSES = 1_259_712
ADDRESS_RECORD_WIDTH = 6
ADDRESS_MAP_BYTES = LOGICAL_BITS * ADDRESS_RECORD_WIDTH
BITS_PER_BYTE = 8

# Exact tuple frozen in hhs_runtime/pass175/runtime.py at ITERATION2_REMOTE_COMMIT.
FROZEN_PHASE_TABLE = (
    0, 0, 36, 0, 54, 0, 54, 18, 36, 36, 18, 18, 36, 54, 54, 54,
    54, 54, 36, 36, 54, 36, 18, 54, 54, 0, 36, 0, 18, 36, 36, 0,
    54, 0, 0, 0, 54, 36, 18, 18, 0, 18, 54, 36, 18, 18, 0, 18,
    0, 36, 36, 54, 18, 18, 54, 36, 36, 18, 18, 0, 36, 54, 18, 36,
)

MANIFEST_SCHEMA_PATH = "contracts/pass217/genesis_candidate_manifest.schema.json"
REFERENCE_PATH = "contracts/pass217/genesis_candidate_reference_vectors.json"
CANDIDATE_PATH = (
    "evidence/pass217/PASS_217_ITERATION_3_LOGICAL_GENESIS_CANDIDATE.bin"
)
ADDRESS_MAP_PATH = "evidence/pass217/PASS_217_ITERATION_3_ADDRESS_MAPS.bin"
MANIFEST_PATH = (
    "evidence/pass217/PASS_217_ITERATION_3_GENESIS_CANDIDATE_MANIFEST.json"
)
CHECKSUM_PATH = "evidence/pass217/PASS_217_ITERATION_3_CHECKSUMS.sha256"

PAYLOAD_PATHS = (
    MANIFEST_SCHEMA_PATH,
    REFERENCE_PATH,
    CANDIDATE_PATH,
    ADDRESS_MAP_PATH,
    MANIFEST_PATH,
)
BUNDLE_PATHS = PAYLOAD_PATHS + (CHECKSUM_PATH,)

SOURCE_DECISIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "HHS_PASS_217_GENESIS_HYDRATION_ROM_BINARY_NORMAL_FORM_CONTRACT.md",
        "PASS217_NORMATIVE_CONTRACT",
        "BOUND_NON_PROMOTIONAL_ITERATION3_SCOPE",
        "Requires Genesis and address-map generation but cannot override the predecessor hold.",
    ),
    (
        "contracts/pass217/machine_contract.json",
        "ITERATION2_MACHINE_CONTRACT",
        "REUSE_FROZEN_DIMENSIONS_AND_CLAIM_BOUNDARY",
        "Supplies exact dimensions, address formulas, nucleus identity, and authority separation.",
    ),
    (
        "contracts/pass217/reference_vectors.json",
        "ITERATION2_REFERENCE_VECTORS",
        "REUSE_FROZEN_ADDRESS_AND_PHASE_REFERENCES",
        "Supplies the exhaustive semantic address root and structural references.",
    ),
    (
        "hhs_runtime/pass175/runtime.py",
        "PASS175_PHASE_AND_ADDRESS_IDENTITY",
        "REUSE_EXACT_PHASE_TABLE_AND_VM5184_FORMULAS",
        "Supplies the 64-entry phase table and inherited VM5184/G243 formulas.",
    ),
    (
        "hhs_runtime/hhs_loshu_phase_embedding_v1.py",
        "TILED_LOSHU_ADDRESS_IDENTITY",
        "REUSE_9X9_LOSHU_LIFT_ONLY_REJECT_ALTERNATE_HASH72",
        "Supplies the 3x3-to-9x9 Lo Shu lift; its alternate Hash72 alphabet is not selected.",
    ),
    (
        "hhs_runtime/HARMONICODE_VM_RUNTIME.c",
        "PROTECTED_VM81_RUNTIME",
        "BOUND_UNMODIFIED_NO_RUNTIME_MUTATION",
        "Binds the protected runtime while this candidate remains evidence-only.",
    ),
)


class Pass217Iteration3Error(RuntimeError):
    """Raised when the candidate bundle fails closed validation."""


def canonical_bytes(value: Any) -> bytes:
    """Return canonical JSON bytes without a platform-dependent newline."""

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


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise Pass217Iteration3Error(
            f"PASS217_ITERATION3_GIT_FAILURE:{' '.join(args)}:{detail}"
        )
    return completed.stdout.decode("utf-8", "surrogateescape").strip()


def _git_bytes(root: Path, revision: str, path: str) -> bytes:
    completed = subprocess.run(
        ("git", "-C", str(root), "show", f"{revision}:{path}"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise Pass217Iteration3Error(
            f"PASS217_ITERATION3_BOUND_SOURCE_MISSING:{path}:{detail}"
        )
    return completed.stdout


def _source_record(
    root: Path,
    path: str,
    role: str,
    disposition: str,
    rationale: str,
) -> dict[str, Any]:
    content = _git_bytes(root, ITERATION2_REMOTE_COMMIT, path)
    return {
        "path": path,
        "role": role,
        "disposition": disposition,
        "rationale": rationale,
        "revision": ITERATION2_REMOTE_COMMIT,
        "git_blob": _git(
            root, "rev-parse", f"{ITERATION2_REMOTE_COMMIT}:{path}"
        ),
        "sha256": sha256(content).hexdigest(),
        "size_bytes": len(content),
    }


def source_bindings(repository_root: Path | str) -> list[dict[str, Any]]:
    root = Path(repository_root).resolve()
    return [
        _source_record(root, path, role, disposition, rationale)
        for path, role, disposition, rationale in SOURCE_DECISIONS
    ]


def _exact_index(value: int, name: str, upper: int) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 0 <= value < upper
    ):
        raise Pass217Iteration3Error(
            f"PASS217_ITERATION3_{name.upper()}_OUT_OF_RANGE"
        )
    return value


def lo_shu_cell_value(cell: int) -> int:
    """Return the inherited Lo Shu tile value for one 9x9 cell."""

    exact_cell = _exact_index(cell, "cell", VM81_CELLS)
    row, column = divmod(exact_cell, VM81_SIDE)
    return LO_SHU[row % 3][column % 3]


def candidate_bit(cell: int, operation: int) -> int:
    """Return one candidate bit from exact phase and Lo Shu parity.

    bit(c,o) = ((PHASE_TABLE[o] / 18) + LoShu(c)) mod 2

    Every phase value is an exact multiple of 18.  The inherited phase table
    has 32 even and 32 odd quadrants, so each cell shard is exactly balanced.
    """

    exact_operation = _exact_index(
        operation, "operation", OPERATIONS_PER_CELL
    )
    phase_quadrant = FROZEN_PHASE_TABLE[exact_operation] // 18
    return (phase_quadrant + lo_shu_cell_value(cell)) & 1


def build_candidate_bytes() -> bytes:
    """Build 81 little-bit-order 64-bit shards (648 bytes total)."""

    image = bytearray(LOGICAL_BYTES)
    for cell in range(VM81_CELLS):
        for operation in range(OPERATIONS_PER_CELL):
            if candidate_bit(cell, operation):
                byte_index = cell * 8 + operation // BITS_PER_BYTE
                image[byte_index] |= 1 << (operation % BITS_PER_BYTE)
    return bytes(image)


def candidate_bit_at(image: bytes, linear: int) -> int:
    """Read a candidate bit using the frozen LSB0 serialization."""

    if len(image) != LOGICAL_BYTES:
        raise Pass217Iteration3Error("PASS217_ITERATION3_CANDIDATE_SIZE")
    exact_linear = _exact_index(linear, "linear", LOGICAL_BITS)
    return (image[exact_linear // 8] >> (exact_linear % 8)) & 1


def packed_address_record(linear: int) -> bytes:
    """Encode one position as six unsigned bytes.

    Record order is cell, operation, alpha, beta, Hash72 row, Hash72 column.
    The linear position is the record index and is therefore not duplicated.
    """

    exact_linear = _exact_index(linear, "linear", LOGICAL_BITS)
    record = address_record(exact_linear)
    return bytes(
        (
            record["cell"],
            record["operation"],
            record["alpha"],
            record["beta"],
            record["hash72_row"],
            record["hash72_column"],
        )
    )


def build_address_map_bytes() -> bytes:
    return b"".join(packed_address_record(linear) for linear in range(LOGICAL_BITS))


def decode_address_record(data: bytes, linear: int) -> dict[str, int]:
    if len(data) != ADDRESS_MAP_BYTES:
        raise Pass217Iteration3Error("PASS217_ITERATION3_ADDRESS_MAP_SIZE")
    exact_linear = _exact_index(linear, "linear", LOGICAL_BITS)
    offset = exact_linear * ADDRESS_RECORD_WIDTH
    cell, operation, alpha, beta, row, column = data[
        offset : offset + ADDRESS_RECORD_WIDTH
    ]
    return {
        "linear": exact_linear,
        "cell": cell,
        "operation": operation,
        "alpha": alpha,
        "beta": beta,
        "hash72_row": row,
        "hash72_column": column,
    }


def candidate_shard_root(image: bytes) -> str:
    if len(image) != LOGICAL_BYTES:
        raise Pass217Iteration3Error("PASS217_ITERATION3_CANDIDATE_SIZE")
    rows = [
        {"cell": cell, "shard_hex": image[cell * 8 : cell * 8 + 8].hex()}
        for cell in range(VM81_CELLS)
    ]
    return _domain_digest(b"HHS-P217-I3-CANDIDATE-SHARDS-V1\0", rows)


def _claim_boundary() -> dict[str, bool]:
    return {
        "address_map_artifact_generated": True,
        "authoritative_hash216_transition_minted": False,
        "authoritative_hash72_transition_receipt_minted": False,
        "canonical_authority_promoted": False,
        "canonical_genesis_selected": False,
        "golay_codec_implemented": False,
        "golay_physical_rom_generated": False,
        "iteration3_candidate_build_complete": True,
        "logical_genesis_candidate_generated": True,
        "logical_genesis_rom_generated": False,
        "migration_started": False,
        "pass217_implementation_complete": False,
        "pass219_runtime_implementation_started": False,
        "protected_c_runtime_modified": False,
        "runtime_mutation_performed": False,
    }


def _manifest_schema() -> dict[str, Any]:
    sha_ref = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://hhs.local/contracts/pass217/"
            "genesis_candidate_manifest.schema.json"
        ),
        "title": "HHS Pass 217 Iteration 3 Non-Promotional Genesis Candidate",
        "type": "object",
        "additionalProperties": False,
        "$defs": {"sha256": sha_ref},
        "required": [
            "schema",
            "classification",
            "pass",
            "iteration",
            "base_authority",
            "inheritance_gate",
            "candidate_profile",
            "dimensions",
            "source_bindings",
            "logical_genesis_candidate",
            "address_map",
            "lo_shu_nucleus",
            "artifacts",
            "claim_boundary",
        ],
        "properties": {
            "schema": {"const": MANIFEST_SCHEMA},
            "classification": {"const": CLASSIFICATION},
            "pass": {"const": PASS_NUMBER},
            "iteration": {"const": ITERATION},
            "base_authority": {"type": "object"},
            "inheritance_gate": {
                "type": "object",
                "required": [
                    "status",
                    "predecessor_reconciliation_complete",
                    "canonical_promotion_allowed",
                    "non_promotional_candidate_build_allowed",
                ],
                "properties": {
                    "status": {"const": INHERITANCE_HOLD},
                    "predecessor_reconciliation_complete": {"const": False},
                    "canonical_promotion_allowed": {"const": False},
                    "non_promotional_candidate_build_allowed": {"const": True},
                },
                "additionalProperties": False,
            },
            "candidate_profile": {"type": "object"},
            "dimensions": {"type": "object"},
            "source_bindings": {"type": "array", "minItems": 6, "maxItems": 6},
            "logical_genesis_candidate": {
                "type": "object",
                "required": [
                    "authority_status",
                    "bit_count",
                    "byte_count",
                    "one_bits",
                    "zero_bits",
                    "per_shard_one_bits",
                    "sha256",
                    "shard_root_sha256",
                ],
                "properties": {
                    "authority_status": {
                        "const": "NON_PROMOTIONAL_CANDIDATE_ONLY"
                    },
                    "bit_count": {"const": LOGICAL_BITS},
                    "byte_count": {"const": LOGICAL_BYTES},
                    "one_bits": {"const": LOGICAL_BITS // 2},
                    "zero_bits": {"const": LOGICAL_BITS // 2},
                    "per_shard_one_bits": {"const": OPERATIONS_PER_CELL // 2},
                    "sha256": {"$ref": "#/$defs/sha256"},
                    "shard_root_sha256": {"$ref": "#/$defs/sha256"},
                },
                "additionalProperties": False,
            },
            "address_map": {"type": "object"},
            "lo_shu_nucleus": {"type": "object"},
            "artifacts": {"type": "array", "minItems": 4, "maxItems": 4},
            "claim_boundary": {
                "type": "object",
                "required": list(_claim_boundary()),
                "properties": {
                    key: {"const": value} for key, value in _claim_boundary().items()
                },
                "additionalProperties": False,
            },
        },
    }


def _nucleus_records(image: bytes) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for local_row in range(3):
        for local_column in range(3):
            row = local_row + 3
            column = local_column + 3
            cell = VM81_SIDE * row + column
            channel_value, channel = LO_SHU_PHASE_CHANNELS[local_row][local_column]
            rows.append(
                {
                    "cell": cell,
                    "row": row,
                    "column": column,
                    "value": LO_SHU[local_row][local_column],
                    "phase_channel": channel,
                    "phase_channel_value": channel_value,
                    "shard_hex": image[cell * 8 : cell * 8 + 8].hex(),
                    "shard_one_bits": sum(
                        value.bit_count()
                        for value in image[cell * 8 : cell * 8 + 8]
                    ),
                }
            )
    return rows


def build_reference_vectors(
    image: bytes | None = None,
    address_map: bytes | None = None,
) -> dict[str, Any]:
    candidate = build_candidate_bytes() if image is None else image
    addresses = build_address_map_bytes() if address_map is None else address_map
    boundaries = (0, 1, 7, 8, 63, 64, 71, 72, 511, 512, 5_183)
    vectors = []
    for linear in boundaries:
        record = decode_address_record(addresses, linear)
        cell, operation = divmod(linear, OPERATIONS_PER_CELL)
        vectors.append(
            {
                "linear": linear,
                "candidate_bit": candidate_bit_at(candidate, linear),
                "expected_bit": candidate_bit(cell, operation),
                "candidate_byte_offset": linear // BITS_PER_BYTE,
                "candidate_bit_offset_lsb0": linear % BITS_PER_BYTE,
                "packed_address_hex": packed_address_record(linear).hex(),
                "decoded_address": record,
            }
        )
    distribution = {
        str(phase): FROZEN_PHASE_TABLE.count(phase) for phase in (0, 18, 36, 54)
    }
    return {
        "schema": REFERENCE_SCHEMA,
        "classification": "NON_PROMOTIONAL_CANDIDATE_REFERENCE_ONLY",
        "profile_id": PROFILE_ID,
        "phase_table_degrees": list(FROZEN_PHASE_TABLE),
        "phase_distribution": distribution,
        "boundary_vectors": vectors,
        "nucleus_vectors": _nucleus_records(candidate),
        "candidate_sha256": sha256(candidate).hexdigest(),
        "candidate_shard_root_sha256": candidate_shard_root(candidate),
        "address_map_sha256": sha256(addresses).hexdigest(),
        "iteration2_semantic_address_root_sha256": exhaustive_address_root(),
        "claim_boundary": _claim_boundary(),
    }


def _artifact_record(path: str, content: bytes) -> dict[str, Any]:
    return {
        "path": path,
        "size_bytes": len(content),
        "sha256": sha256(content).hexdigest(),
    }


def build_manifest(
    repository_root: Path | str,
    image: bytes,
    address_map: bytes,
    schema_bytes: bytes,
    reference_bytes: bytes,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    bindings = source_bindings(root)
    source_root = _domain_digest(
        b"HHS-P217-I3-SOURCE-BINDINGS-V1\0", bindings
    )
    nucleus = {
        "values": [list(row) for row in LO_SHU],
        "phase_channels": [
            [list(cell) for cell in row] for row in LO_SHU_PHASE_CHANNELS
        ],
        "fixed_pointwise": True,
    }
    nucleus["root_sha256"] = sha256(canonical_bytes(nucleus)).hexdigest()
    return {
        "schema": MANIFEST_SCHEMA,
        "classification": CLASSIFICATION,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "base_authority": {
            "main_commit": BASE_COMMIT,
            "iteration2_remote_commit": ITERATION2_REMOTE_COMMIT,
            "iteration2_tree": ITERATION2_TREE,
            "iteration2_bundle_root_sha256": ITERATION2_BUNDLE_ROOT,
            "source_bindings_root_sha256": source_root,
        },
        "inheritance_gate": {
            "status": INHERITANCE_HOLD,
            "predecessor_reconciliation_complete": False,
            "canonical_promotion_allowed": False,
            "non_promotional_candidate_build_allowed": True,
        },
        "candidate_profile": {
            "profile_id": PROFILE_ID,
            "cell_layout": "row-major 9x9; Lo Shu local indices are row%3,column%3",
            "phase_table": "Pass 175 PHASE_TABLE; degrees in {0,18,36,54}",
            "bit_rule": "bit(c,o)=((PHASE_TABLE[o]//18)+LoShu(c)) mod 2",
            "serialization": (
                "81 consecutive 64-bit shards; operation o is bit o in LSB0 order"
            ),
            "selection_status": "CANDIDATE_PROFILE_NOT_CANONICAL_SELECTION",
        },
        "dimensions": {
            "vm81_cells": VM81_CELLS,
            "operations_per_cell": OPERATIONS_PER_CELL,
            "logical_bits": LOGICAL_BITS,
            "logical_bytes": LOGICAL_BYTES,
            "hash72_side": HASH72_SIDE,
            "g243_controls": G243_CONTROLS,
            "projected_addresses": PROJECTED_ADDRESSES,
        },
        "source_bindings": bindings,
        "logical_genesis_candidate": {
            "authority_status": "NON_PROMOTIONAL_CANDIDATE_ONLY",
            "bit_count": LOGICAL_BITS,
            "byte_count": len(image),
            "one_bits": sum(value.bit_count() for value in image),
            "zero_bits": LOGICAL_BITS - sum(value.bit_count() for value in image),
            "per_shard_one_bits": OPERATIONS_PER_CELL // 2,
            "sha256": sha256(image).hexdigest(),
            "shard_root_sha256": candidate_shard_root(image),
        },
        "address_map": {
            "record_count": LOGICAL_BITS,
            "record_width_bytes": ADDRESS_RECORD_WIDTH,
            "byte_count": len(address_map),
            "record_order": [
                "cell",
                "operation",
                "alpha",
                "beta",
                "hash72_row",
                "hash72_column",
            ],
            "linear_position_rule": "record index s",
            "cell_operation_rule": "s=64*c+o",
            "phase_pair_rule": "o=8*alpha+beta",
            "hash72_rule": "s=72*r+k",
            "g243_projection_rule": "q=243*s+g; stored formula, not duplicated records",
            "g243_projection_count": PROJECTED_ADDRESSES,
            "sha256": sha256(address_map).hexdigest(),
            "iteration2_semantic_root_sha256": exhaustive_address_root(),
        },
        "lo_shu_nucleus": {
            **nucleus,
            "central_cell_indices": [
                VM81_SIDE * row + column
                for row in range(3, 6)
                for column in range(3, 6)
            ],
            "pointwise_records": _nucleus_records(image),
        },
        "artifacts": [
            _artifact_record(MANIFEST_SCHEMA_PATH, schema_bytes),
            _artifact_record(REFERENCE_PATH, reference_bytes),
            _artifact_record(CANDIDATE_PATH, image),
            _artifact_record(ADDRESS_MAP_PATH, address_map),
        ],
        "claim_boundary": _claim_boundary(),
    }


def build_bundle(repository_root: Path | str) -> dict[str, bytes]:
    image = build_candidate_bytes()
    address_map = build_address_map_bytes()
    schema_bytes = _json_file_bytes(_manifest_schema())
    reference_bytes = _json_file_bytes(build_reference_vectors(image, address_map))
    manifest_bytes = _json_file_bytes(
        build_manifest(
            repository_root,
            image,
            address_map,
            schema_bytes,
            reference_bytes,
        )
    )
    payload = {
        MANIFEST_SCHEMA_PATH: schema_bytes,
        REFERENCE_PATH: reference_bytes,
        CANDIDATE_PATH: image,
        ADDRESS_MAP_PATH: address_map,
        MANIFEST_PATH: manifest_bytes,
    }
    checksum_bytes = "".join(
        f"{sha256(payload[path]).hexdigest()}  {path}\n" for path in PAYLOAD_PATHS
    ).encode("ascii")
    return {**payload, CHECKSUM_PATH: checksum_bytes}


def bundle_root(bundle: Mapping[str, bytes]) -> str:
    rows = [
        {
            "path": path,
            "size_bytes": len(bundle[path]),
            "sha256": sha256(bundle[path]).hexdigest(),
        }
        for path in BUNDLE_PATHS
    ]
    return _domain_digest(b"HHS-P217-I3-CANDIDATE-BUNDLE-V1\0", rows)


def _literal_assignment(source: bytes, name: str) -> Any:
    tree = ast.parse(source.decode("utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                return ast.literal_eval(node.value)
    raise Pass217Iteration3Error(
        f"PASS217_ITERATION3_BOUND_LITERAL_MISSING:{name}"
    )


def _validate_inherited_literals(root: Path) -> None:
    phase_source = _git_bytes(
        root, ITERATION2_REMOTE_COMMIT, "hhs_runtime/pass175/runtime.py"
    )
    observed_phase = tuple(_literal_assignment(phase_source, "PHASE_TABLE"))
    if observed_phase != FROZEN_PHASE_TABLE:
        raise Pass217Iteration3Error("PASS217_ITERATION3_PHASE_TABLE_DRIFT")
    loshu_source = _git_bytes(
        root,
        ITERATION2_REMOTE_COMMIT,
        "hhs_runtime/hhs_loshu_phase_embedding_v1.py",
    )
    observed_loshu = tuple(
        tuple(row) for row in _literal_assignment(loshu_source, "LO_SHU_3X3")
    )
    if observed_loshu != LO_SHU:
        raise Pass217Iteration3Error("PASS217_ITERATION3_LOSHU_DRIFT")


def _validate_address_map(addresses: bytes) -> None:
    if len(addresses) != ADDRESS_MAP_BYTES:
        raise Pass217Iteration3Error("PASS217_ITERATION3_ADDRESS_MAP_SIZE")
    cell_operations: set[tuple[int, int]] = set()
    phase_pairs: set[tuple[int, int, int]] = set()
    hash72_coordinates: set[tuple[int, int]] = set()
    projected_count = 0
    for linear in range(LOGICAL_BITS):
        expected = packed_address_record(linear)
        offset = linear * ADDRESS_RECORD_WIDTH
        if addresses[offset : offset + ADDRESS_RECORD_WIDTH] != expected:
            raise Pass217Iteration3Error(
                f"PASS217_ITERATION3_ADDRESS_RECORD_DRIFT:{linear}"
            )
        row = decode_address_record(addresses, linear)
        if linear != OPERATIONS_PER_CELL * row["cell"] + row["operation"]:
            raise Pass217Iteration3Error("PASS217_ITERATION3_CELL_OPERATION_INVERSE")
        if row["operation"] != PHASE_SIDE * row["alpha"] + row["beta"]:
            raise Pass217Iteration3Error("PASS217_ITERATION3_PHASE_PAIR_INVERSE")
        if linear != HASH72_SIDE * row["hash72_row"] + row["hash72_column"]:
            raise Pass217Iteration3Error("PASS217_ITERATION3_HASH72_INVERSE")
        cell_operations.add((row["cell"], row["operation"]))
        phase_pairs.add((row["cell"], row["alpha"], row["beta"]))
        hash72_coordinates.add((row["hash72_row"], row["hash72_column"]))
        for control in range(G243_CONTROLS):
            projected = G243_CONTROLS * linear + control
            recovered_linear, recovered_control = divmod(projected, G243_CONTROLS)
            if (recovered_linear, recovered_control) != (linear, control):
                raise Pass217Iteration3Error("PASS217_ITERATION3_G243_INVERSE")
            projected_count += 1
    if not all(
        len(view) == LOGICAL_BITS
        for view in (cell_operations, phase_pairs, hash72_coordinates)
    ):
        raise Pass217Iteration3Error("PASS217_ITERATION3_ADDRESS_ALIAS")
    if projected_count != PROJECTED_ADDRESSES:
        raise Pass217Iteration3Error("PASS217_ITERATION3_G243_COUNT")


def _validate_claim_boundary(claims: Mapping[str, Any]) -> None:
    if dict(claims) != _claim_boundary():
        raise Pass217Iteration3Error("PASS217_ITERATION3_CLAIM_BOUNDARY_DRIFT")


def validate_bundle(
    repository_root: Path | str,
    bundle: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    expected = build_bundle(root)
    actual = (
        {path: (root / path).read_bytes() for path in BUNDLE_PATHS}
        if bundle is None
        else dict(bundle)
    )
    if set(actual) != set(expected):
        raise Pass217Iteration3Error("PASS217_ITERATION3_BUNDLE_PATH_SET")
    for path in BUNDLE_PATHS:
        if actual[path] != expected[path]:
            raise Pass217Iteration3Error(
                f"PASS217_ITERATION3_BUNDLE_DRIFT:{path}"
            )

    _validate_inherited_literals(root)
    manifest = json.loads(actual[MANIFEST_PATH])
    references = json.loads(actual[REFERENCE_PATH])
    schema = json.loads(actual[MANIFEST_SCHEMA_PATH])
    image = actual[CANDIDATE_PATH]
    addresses = actual[ADDRESS_MAP_PATH]

    if manifest["schema"] != MANIFEST_SCHEMA or schema["properties"]["schema"]["const"] != MANIFEST_SCHEMA:
        raise Pass217Iteration3Error("PASS217_ITERATION3_MANIFEST_SCHEMA")
    if references["schema"] != REFERENCE_SCHEMA:
        raise Pass217Iteration3Error("PASS217_ITERATION3_REFERENCE_SCHEMA")
    if manifest["classification"] != CLASSIFICATION:
        raise Pass217Iteration3Error("PASS217_ITERATION3_CLASSIFICATION")
    if manifest["inheritance_gate"]["status"] != INHERITANCE_HOLD:
        raise Pass217Iteration3Error("PASS217_ITERATION3_INHERITANCE_GATE")
    if manifest["base_authority"]["iteration2_tree"] != ITERATION2_TREE:
        raise Pass217Iteration3Error("PASS217_ITERATION3_ITERATION2_TREE")

    if len(image) != LOGICAL_BYTES:
        raise Pass217Iteration3Error("PASS217_ITERATION3_CANDIDATE_SIZE")
    one_bits = sum(value.bit_count() for value in image)
    if one_bits != LOGICAL_BITS // 2:
        raise Pass217Iteration3Error("PASS217_ITERATION3_CANDIDATE_BALANCE")
    for cell in range(VM81_CELLS):
        shard = image[cell * 8 : cell * 8 + 8]
        if sum(value.bit_count() for value in shard) != OPERATIONS_PER_CELL // 2:
            raise Pass217Iteration3Error(
                f"PASS217_ITERATION3_SHARD_BALANCE:{cell}"
            )
        for operation in range(OPERATIONS_PER_CELL):
            linear = OPERATIONS_PER_CELL * cell + operation
            if candidate_bit_at(image, linear) != candidate_bit(cell, operation):
                raise Pass217Iteration3Error(
                    f"PASS217_ITERATION3_CANDIDATE_BIT_DRIFT:{linear}"
                )
    candidate_record = manifest["logical_genesis_candidate"]
    if candidate_record["sha256"] != sha256(image).hexdigest():
        raise Pass217Iteration3Error("PASS217_ITERATION3_CANDIDATE_SHA256")
    if candidate_record["shard_root_sha256"] != candidate_shard_root(image):
        raise Pass217Iteration3Error("PASS217_ITERATION3_SHARD_ROOT")

    _validate_address_map(addresses)
    address_record_manifest = manifest["address_map"]
    if address_record_manifest["sha256"] != sha256(addresses).hexdigest():
        raise Pass217Iteration3Error("PASS217_ITERATION3_ADDRESS_SHA256")
    if address_record_manifest["iteration2_semantic_root_sha256"] != exhaustive_address_root():
        raise Pass217Iteration3Error("PASS217_ITERATION3_SEMANTIC_ADDRESS_ROOT")

    for row in manifest["lo_shu_nucleus"]["pointwise_records"]:
        local_row = row["row"] - 3
        local_column = row["column"] - 3
        expected_value, expected_channel = LO_SHU_PHASE_CHANNELS[local_row][local_column]
        if row["value"] != expected_value or row["phase_channel_value"] != expected_value:
            raise Pass217Iteration3Error("PASS217_ITERATION3_NUCLEUS_VALUE")
        if row["phase_channel"] != expected_channel or row["shard_one_bits"] != 32:
            raise Pass217Iteration3Error("PASS217_ITERATION3_NUCLEUS_CHANNEL")

    _validate_claim_boundary(manifest["claim_boundary"])
    _validate_claim_boundary(references["claim_boundary"])
    if manifest["candidate_profile"]["selection_status"] != "CANDIDATE_PROFILE_NOT_CANONICAL_SELECTION":
        raise Pass217Iteration3Error("PASS217_ITERATION3_CANONICAL_OVERCLAIM")

    artifact_rows = {row["path"]: row for row in manifest["artifacts"]}
    for path in (MANIFEST_SCHEMA_PATH, REFERENCE_PATH, CANDIDATE_PATH, ADDRESS_MAP_PATH):
        if artifact_rows[path]["sha256"] != sha256(actual[path]).hexdigest():
            raise Pass217Iteration3Error(
                f"PASS217_ITERATION3_ARTIFACT_SHA256:{path}"
            )
        if artifact_rows[path]["size_bytes"] != len(actual[path]):
            raise Pass217Iteration3Error(
                f"PASS217_ITERATION3_ARTIFACT_SIZE:{path}"
            )

    checksum_lines = actual[CHECKSUM_PATH].decode("ascii").splitlines()
    if len(checksum_lines) != len(PAYLOAD_PATHS):
        raise Pass217Iteration3Error("PASS217_ITERATION3_CHECKSUM_COUNT")
    for line, path in zip(checksum_lines, PAYLOAD_PATHS, strict=True):
        checksum, observed_path = line.split("  ", 1)
        if observed_path != path or checksum != sha256(actual[path]).hexdigest():
            raise Pass217Iteration3Error(
                f"PASS217_ITERATION3_CHECKSUM_MISMATCH:{path}"
            )

    protected = "hhs_runtime/HARMONICODE_VM_RUNTIME.c"
    if _git(root, "diff", "--name-only", BASE_COMMIT, "HEAD", "--", protected):
        raise Pass217Iteration3Error("PASS217_ITERATION3_PROTECTED_RUNTIME_MODIFIED")

    return {
        "classification": CLASSIFICATION,
        "bundle_root_sha256": bundle_root(actual),
        "candidate_sha256": sha256(image).hexdigest(),
        "candidate_shard_root_sha256": candidate_shard_root(image),
        "candidate_bytes": len(image),
        "candidate_one_bits": one_bits,
        "address_map_sha256": sha256(addresses).hexdigest(),
        "address_map_bytes": len(addresses),
        "address_record_count": LOGICAL_BITS,
        "g243_projection_count": PROJECTED_ADDRESSES,
        "inheritance_status": INHERITANCE_HOLD,
        "canonical_authority_promoted": False,
        "golay_physical_rom_generated": False,
        "protected_runtime_modified": False,
    }


def write_bundle(repository_root: Path | str) -> dict[str, bytes]:
    root = Path(repository_root).resolve()
    bundle = build_bundle(root)
    for path, content in bundle.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return bundle


__all__ = [
    "ADDRESS_MAP_BYTES",
    "ADDRESS_MAP_PATH",
    "ADDRESS_RECORD_WIDTH",
    "BUNDLE_PATHS",
    "CANDIDATE_PATH",
    "CHECKSUM_PATH",
    "CLASSIFICATION",
    "FROZEN_PHASE_TABLE",
    "INHERITANCE_HOLD",
    "ITERATION2_REMOTE_COMMIT",
    "ITERATION2_TREE",
    "LOGICAL_BITS",
    "LOGICAL_BYTES",
    "MANIFEST_PATH",
    "MANIFEST_SCHEMA_PATH",
    "PROFILE_ID",
    "Pass217Iteration3Error",
    "REFERENCE_PATH",
    "build_address_map_bytes",
    "build_bundle",
    "build_candidate_bytes",
    "build_reference_vectors",
    "bundle_root",
    "candidate_bit",
    "candidate_bit_at",
    "candidate_shard_root",
    "decode_address_record",
    "lo_shu_cell_value",
    "packed_address_record",
    "source_bindings",
    "validate_bundle",
    "write_bundle",
]
