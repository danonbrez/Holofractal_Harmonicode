"""Pass 217 Iteration 2 machine-contract and reference-vector preparation.

This module freezes schemas and deterministic conformance vectors for the
future Pass 217 Genesis ROM.  It deliberately does not generate a logical or
physical ROM, decode Golay words, mutate the VM81 nucleus, admit a state, or
mint an authoritative Hash72/Hash216 transition.  Every reusable identity is
bound to an exact file in the Iteration 1 inherited-main snapshot; unresolved
or incompatible candidates remain explicitly deferred.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import (
    HASH72_ALPHABET,
    HASH72_SYMBOL_COUNT,
    validate_hash72,
)


SCHEMA = "HHS_PASS_217_ITERATION_2_MACHINE_CONTRACT_BUNDLE_V1"
CLASSIFICATION = "HHS_PASS_217_ITERATION_2_SCHEMA_REFERENCE_PROFILE_FROZEN"
PASS_NUMBER = 217
ITERATION = 2
CONTRACT = "HHS-P217-GHR-BNF-H72-H216-G24-VM5184"
BASE_COMMIT = "66c614ae1de0c1b1651451e2c406307a8dee83ed"
BASE_TREE = "4d8c87797d8844b8868f6b412ba45f936731c6c4"
ITERATION1_REMOTE_COMMIT = "d87f84b4171e9e4085014015ccad4d278b992feb"
ITERATION1_TREE = "f5b1c416afe07d6a1f1abe50447142f5a1ca2c26"
ITERATION1_FREEZE_SHA256 = (
    "cfcacc6708697e8b5af3ccd58fca486150e21a1a6bfd115f667700adf96ed4cb"
)
INHERITANCE_HOLD = "HOLD_FOR_PASS_215_216_AUTHORITATIVE_RECONCILIATION"

LOGICAL_BITS = 5_184
LOGICAL_BYTES = 648
VM81_CELLS = 81
POSITIONS_PER_CELL = 64
HASH72_SIDE = 72
PHASE_SIDE = 8
RECIPROCAL_RELATIONS = 6_561
G243_CONTROLS = 243
PROJECTED_ADDRESSES = 1_259_712
GOLAY_PAYLOAD_BITS = 12
GOLAY_CODEWORD_BITS = 24
GOLAY_DISTANCE = 8
GOLAY_WORDS = 432
PHYSICAL_BITS = 10_368
PHYSICAL_BYTES = 1_296
HASH216_SECTIONS = ("previous", "next", "receipt")
ORDERED_PHASE_REGISTRY = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
LO_SHU_PHASE_CHANNELS = (
    ((4, "x"), (9, "y"), (2, "z")),
    ((3, "w"), (5, "1"), (7, "xy")),
    ((8, "yx"), (1, "zw"), (6, "wz")),
)

JSON_ARTIFACT_PATHS = (
    "contracts/pass217/machine_contract.json",
    "contracts/pass217/invariants.json",
    "contracts/pass217/address_map.schema.json",
    "contracts/pass217/hash72.schema.json",
    "contracts/pass217/hash216.schema.json",
    "contracts/pass217/rom_manifest.schema.json",
    "contracts/pass217/golay_profile.schema.json",
    "contracts/pass217/vector_store.schema.json",
    "contracts/pass217/reference_vectors.json",
)
CHECKSUM_PATH = "contracts/pass217/checksums.sha256"
EVIDENCE_PATH = "evidence/pass217/PASS_217_ITERATION_2_MACHINE_CONTRACTS.json"

SOURCE_DECISIONS: tuple[tuple[str, str, str, str], ...] = (
    (
        "HHS_PASS_217_GENESIS_HYDRATION_ROM_BINARY_NORMAL_FORM_CONTRACT.md",
        "PASS217_NORMATIVE_CONTRACT",
        "BOUND_NORMATIVE_SOURCE",
        "Defines Iteration 2 and the required machine-contract artifact set.",
    ),
    (
        "HHS_PASS_219_CPP_COMPOUND_SYMBOLIC_CONSTRAINT_RUNTIME_CONTRACT.md",
        "PASS219_DOWNSTREAM_CONSUMER_CONTRACT",
        "BOUND_DOWNSTREAM_REQUIREMENT",
        "Requires inherited 81x64 phase identity and defers to Pass 217 hydration.",
    ),
    (
        "hhs_runtime/core/hash72_validator_v1.py",
        "CANONICAL_HASH72_FORMAT",
        "REUSE_CANONICAL_FORMAT",
        "Explicitly defines the canonical ordered 72-symbol alphabet and validator.",
    ),
    (
        "hhs_runtime/core/hash72_digest_v1.py",
        "CANONICAL_HASH72_DIGEST",
        "REUSE_REFERENCE_DIGEST",
        "Provides domain-separated Hash72 construction over the canonical alphabet.",
    ),
    (
        "hhs_runtime/pass175/runtime.py",
        "VM5184_G243_ADDRESS_AND_LEGACY_HASH216",
        "REUSE_ADDRESS_DEFER_HASH216_LANE_ADAPTER",
        "The 81x64 and G243 maps are reusable; predecessor/current/successor lanes are not silently relabeled previous/next/receipt.",
    ),
    (
        "hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py",
        "COMPILED_ROM_DIMENSIONS",
        "REUSE_DIMENSION_CONSTANTS_ONLY",
        "Binds 81x64, 5184, and G243 dimensions without promoting a Pass 217 ROM.",
    ),
    (
        "hhs_runtime/core_sandbox/hhs_octonion_digital_dna_u72_table_v1.py",
        "ORDERED_PHASE_BASIS",
        "REUSE_ORDERED_BASIS_CANDIDATE",
        "Preserves x,y,z,w,xy,yx,zw,wz order and directional distinctions.",
    ),
    (
        "hhs_runtime/hhs_loshu_phase_embedding_v1.py",
        "LEGACY_LOSHU_EMBEDDING",
        "COMPATIBILITY_SOURCE_NOT_HASH72_FORMAT_AUTHORITY",
        "Its alternate alphabet and local non-cryptographic receipt are not selected over the canonical Hash72 validator.",
    ),
    (
        "hhs_runtime/core_sandbox/hhs_security_armor_v1.py",
        "LEGACY_GOLAY_STYLE_HOOK",
        "REJECT_AS_GOLAY_IMPLEMENTATION_PLACEHOLDER_ONLY",
        "The source labels its Golay hook a placeholder and supplies no [24,12,8] codec authority.",
    ),
)


class Pass217Iteration2Error(RuntimeError):
    """Raised when the preparatory bundle cannot be reproduced exactly."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


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
        raise Pass217Iteration2Error(
            f"PASS217_ITERATION2_GIT_FAILURE:{' '.join(args)}:{detail}"
        )
    return completed.stdout.decode("utf-8", "surrogateescape").strip()


def _source_record(
    root: Path,
    path: str,
    role: str,
    disposition: str,
    rationale: str,
) -> dict[str, Any]:
    content = subprocess.run(
        ("git", "-C", str(root), "show", f"{BASE_COMMIT}:{path}"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if content.returncode:
        detail = content.stderr.decode("utf-8", "replace").strip()
        raise Pass217Iteration2Error(
            f"PASS217_ITERATION2_BOUND_SOURCE_MISSING:{path}:{detail}"
        )
    return {
        "path": path,
        "role": role,
        "disposition": disposition,
        "rationale": rationale,
        "git_blob": _git(root, "rev-parse", f"{BASE_COMMIT}:{path}"),
        "sha256": sha256(content.stdout).hexdigest(),
        "size_bytes": len(content.stdout),
    }


def source_bindings(repository_root: Path | str) -> list[dict[str, Any]]:
    root = Path(repository_root).resolve()
    return [
        _source_record(root, path, role, disposition, rationale)
        for path, role, disposition, rationale in SOURCE_DECISIONS
    ]


def address_record(linear: int, control: int = 0) -> dict[str, int]:
    if not isinstance(linear, int) or isinstance(linear, bool) or not 0 <= linear < LOGICAL_BITS:
        raise Pass217Iteration2Error("PASS217_ITERATION2_ADDRESS_OUT_OF_RANGE")
    if not isinstance(control, int) or isinstance(control, bool) or not 0 <= control < G243_CONTROLS:
        raise Pass217Iteration2Error("PASS217_ITERATION2_CONTROL_OUT_OF_RANGE")
    cell, operation = divmod(linear, POSITIONS_PER_CELL)
    alpha, beta = divmod(operation, PHASE_SIDE)
    row, column = divmod(linear, HASH72_SIDE)
    return {
        "linear": linear,
        "cell": cell,
        "operation": operation,
        "alpha": alpha,
        "beta": beta,
        "hash72_row": row,
        "hash72_column": column,
        "g243_control": control,
        "projected": G243_CONTROLS * linear + control,
    }


def exhaustive_address_root() -> str:
    rows = [address_record(linear) for linear in range(LOGICAL_BITS)]
    return _domain_digest(b"HHS-P217-I2-ADDRESS-MAP-V1\0", rows)


def _phase_row(row: int) -> str:
    return "".join(HASH72_ALPHABET[(row + column) % HASH72_SIDE] for column in range(HASH72_SIDE))


def hash72_matrix_root() -> str:
    state = sha256(b"HHS-P217-I2-HASH72-MATRIX-V1\0")
    for row in range(HASH72_SIDE):
        state.update(_phase_row(row).encode("ascii"))
    return state.hexdigest()


def orbit_coordinate(direction: str, row: int, column: int, displacement: int) -> tuple[int, int]:
    if direction not in {"x", "y", "z", "w"}:
        raise Pass217Iteration2Error("PASS217_ITERATION2_ORBIT_DIRECTION_INVALID")
    if not 0 <= row < HASH72_SIDE or not 0 <= column < HASH72_SIDE:
        raise Pass217Iteration2Error("PASS217_ITERATION2_ORBIT_COORDINATE_INVALID")
    delta = displacement % HASH72_SIDE
    if direction == "x":
        return row, (column + delta) % HASH72_SIDE
    if direction == "y":
        return (row + delta) % HASH72_SIDE, column
    if direction == "z":
        return (row + delta) % HASH72_SIDE, (column + delta) % HASH72_SIDE
    return (row + delta) % HASH72_SIDE, (column - delta) % HASH72_SIDE


def _schema_header(identifier: str, title: str) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://hhs.local/contracts/pass217/{identifier}",
        "title": title,
        "type": "object",
        "additionalProperties": False,
    }


def build_address_schema() -> dict[str, Any]:
    schema = _schema_header(
        "address_map.schema.json",
        "HHS Pass 217 VM5184 and G243 Address Record",
    )
    schema.update(
        {
            "required": [
                "linear", "cell", "operation", "alpha", "beta",
                "hash72_row", "hash72_column", "g243_control", "projected",
            ],
            "properties": {
                "linear": {"type": "integer", "minimum": 0, "maximum": 5_183},
                "cell": {"type": "integer", "minimum": 0, "maximum": 80},
                "operation": {"type": "integer", "minimum": 0, "maximum": 63},
                "alpha": {"type": "integer", "minimum": 0, "maximum": 7},
                "beta": {"type": "integer", "minimum": 0, "maximum": 7},
                "hash72_row": {"type": "integer", "minimum": 0, "maximum": 71},
                "hash72_column": {"type": "integer", "minimum": 0, "maximum": 71},
                "g243_control": {"type": "integer", "minimum": 0, "maximum": 242},
                "projected": {"type": "integer", "minimum": 0, "maximum": 1_259_711},
            },
        }
    )
    return schema


def build_hash72_schema() -> dict[str, Any]:
    schema = _schema_header("hash72.schema.json", "HHS Pass 217 Hash72 State/Seed Record")
    schema.update(
        {
            "$defs": {
                "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
            "required": [
                "schema", "alphabet_id", "serialized", "phase_indices",
                "parent_seed_sha256", "ordered_path", "bracketing",
                "authority_status",
            ],
            "properties": {
                "schema": {"const": "HHS_PASS_217_HASH72_STATE_SEED_V1"},
                "alphabet_id": {"const": "HHS_CANONICAL_HASH72_ALPHABET_V1"},
                "serialized": {"type": "string", "minLength": 72, "maxLength": 72},
                "phase_indices": {
                    "type": "array", "minItems": 72, "maxItems": 72,
                    "items": {"type": "integer", "minimum": 0, "maximum": 71},
                },
                "parent_seed_sha256": {"$ref": "#/$defs/sha256"},
                "ordered_path": {"type": "array", "items": {"type": "string"}},
                "bracketing": {"type": "string", "minLength": 1},
                "authority_status": {
                    "enum": ["REFERENCE_ONLY", "ADMITTED_BY_VM81_HASH72"]
                },
            },
        }
    )
    return schema


def build_hash216_schema() -> dict[str, Any]:
    schema = _schema_header("hash216.schema.json", "HHS Pass 217 Hash216 Transition Record")
    schema.update(
        {
            "$defs": {
                "hash72": {"type": "string", "minLength": 72, "maxLength": 72},
                "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
            "required": [
                "schema", "previous", "next", "receipt", "combined",
                "position_commitments", "commitments_root_sha256",
                "parent_ancestry_sha256", "authority_status",
            ],
            "properties": {
                "schema": {"const": "HHS_PASS_217_HASH216_TRANSITION_V1"},
                "previous": {"$ref": "#/$defs/hash72"},
                "next": {"$ref": "#/$defs/hash72"},
                "receipt": {"$ref": "#/$defs/hash72"},
                "combined": {"type": "string", "minLength": 216, "maxLength": 216},
                "position_commitments": {
                    "type": "array", "minItems": 216, "maxItems": 216,
                    "items": {"$ref": "#/$defs/sha256"},
                },
                "commitments_root_sha256": {"$ref": "#/$defs/sha256"},
                "parent_ancestry_sha256": {"$ref": "#/$defs/sha256"},
                "authority_status": {
                    "enum": ["REFERENCE_ONLY_NOT_ADMITTED", "AUTHORITATIVE_VM81_TRANSITION"]
                },
            },
        }
    )
    return schema


def build_rom_manifest_schema() -> dict[str, Any]:
    schema = _schema_header("rom_manifest.schema.json", "HHS Pass 217 Hydration ROM Manifest")
    schema.update(
        {
            "$defs": {"sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}},
            "required": [
                "schema", "version", "logical_bytes", "physical_bytes",
                "logical_genesis_sha256", "physical_golay_sha256",
                "address_map_root_sha256", "hash72_matrix_root_sha256",
                "nucleus_root_sha256", "source_manifest_root_sha256",
                "build_status", "signature_status",
            ],
            "properties": {
                "schema": {"const": "HHS_PASS_217_HYDRATION_ROM_MANIFEST_V1"},
                "version": {"type": "string", "minLength": 1},
                "logical_bytes": {"const": 648},
                "physical_bytes": {"const": 1_296},
                "logical_genesis_sha256": {"$ref": "#/$defs/sha256"},
                "physical_golay_sha256": {"$ref": "#/$defs/sha256"},
                "address_map_root_sha256": {"$ref": "#/$defs/sha256"},
                "hash72_matrix_root_sha256": {"$ref": "#/$defs/sha256"},
                "nucleus_root_sha256": {"$ref": "#/$defs/sha256"},
                "source_manifest_root_sha256": {"$ref": "#/$defs/sha256"},
                "build_status": {"enum": ["UNMATERIALIZED", "REPRODUCIBLE_BUILD_VERIFIED"]},
                "signature_status": {"enum": ["UNSIGNED", "VERIFIED"]},
            },
        }
    )
    return schema


def build_golay_schema() -> dict[str, Any]:
    schema = _schema_header("golay_profile.schema.json", "HHS Pass 217 Extended Golay Profile")
    schema.update(
        {
            "required": [
                "schema", "code", "payload_bits", "codeword_bits", "distance",
                "word_count", "logical_bits", "physical_bits", "mixed_bound",
                "decoder_status", "generator_definition_status",
            ],
            "properties": {
                "schema": {"const": "HHS_PASS_217_EXTENDED_GOLAY_PROFILE_V1"},
                "code": {"const": "EXTENDED_BINARY_GOLAY_24_12_8"},
                "payload_bits": {"const": 12},
                "codeword_bits": {"const": 24},
                "distance": {"const": 8},
                "word_count": {"const": 432},
                "logical_bits": {"const": 5_184},
                "physical_bits": {"const": 10_368},
                "mixed_bound": {"const": "2e+s<=7"},
                "decoder_status": {"enum": ["PROFILE_ONLY", "BOUNDED_DECODER_VERIFIED"]},
                "generator_definition_status": {"enum": ["DEFERRED", "FROZEN_AND_VERIFIED"]},
            },
        }
    )
    return schema


def build_vector_store_schema() -> dict[str, Any]:
    schema = _schema_header("vector_store.schema.json", "HHS Pass 217 Authenticated Vector Entry")
    schema.update(
        {
            "$defs": {
                "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "support": {
                    "type": "array", "uniqueItems": True,
                    "items": {"type": "integer", "minimum": 0, "maximum": 5_183},
                },
            },
            "required": [
                "schema", "entry_id_sha256", "parent_state_sha256",
                "candidate_state_sha256", "hash216_transition_sha256",
                "forward_support", "inverse_support", "ordered_path",
                "bracketing", "dependency_frontier", "collision_bucket",
                "admission_status",
            ],
            "properties": {
                "schema": {"const": "HHS_PASS_217_VECTOR_STORE_ENTRY_V1"},
                "entry_id_sha256": {"$ref": "#/$defs/sha256"},
                "parent_state_sha256": {"$ref": "#/$defs/sha256"},
                "candidate_state_sha256": {"$ref": "#/$defs/sha256"},
                "hash216_transition_sha256": {"$ref": "#/$defs/sha256"},
                "forward_support": {"$ref": "#/$defs/support"},
                "inverse_support": {"$ref": "#/$defs/support"},
                "ordered_path": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                "bracketing": {"type": "string", "minLength": 1},
                "dependency_frontier": {"$ref": "#/$defs/support"},
                "collision_bucket": {"type": "integer", "minimum": 0},
                "admission_status": {
                    "enum": ["REFERENCE_ONLY", "CANDIDATE", "VM81_ADMITTED", "QUARANTINED"]
                },
            },
        }
    )
    return schema


def _machine_claim_boundary() -> dict[str, bool]:
    return {
        "schema_and_reference_preparation_complete": True,
        "protected_c_runtime_modified": False,
        "runtime_mutation_performed": False,
        "canonical_authority_promoted": False,
        "logical_genesis_rom_generated": False,
        "golay_physical_rom_generated": False,
        "golay_codec_implemented": False,
        "migration_started": False,
        "authoritative_hash72_transition_receipt_minted": False,
        "authoritative_hash216_transition_minted": False,
        "pass217_implementation_complete": False,
        "pass219_runtime_implementation_started": False,
    }


def build_machine_contract(repository_root: Path | str) -> dict[str, Any]:
    bindings = source_bindings(repository_root)
    nucleus = {
        "values": [list(row) for row in LO_SHU],
        "phase_channels": [[list(cell) for cell in row] for row in LO_SHU_PHASE_CHANNELS],
        "fixed_pointwise": True,
    }
    return {
        "schema": "HHS_PASS_217_ITERATION_2_MACHINE_CONTRACT_V1",
        "classification": CLASSIFICATION,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "base_authority": {
            "main_commit": BASE_COMMIT,
            "main_tree": BASE_TREE,
            "iteration1_remote_commit": ITERATION1_REMOTE_COMMIT,
            "iteration1_tree": ITERATION1_TREE,
            "iteration1_freeze_sha256": ITERATION1_FREEZE_SHA256,
        },
        "inheritance_gate": {
            "status": INHERITANCE_HOLD,
            "schema_reference_preparation_allowed": True,
            "rom_runtime_or_migration_promotion_allowed": False,
        },
        "source_bindings": bindings,
        "dimensions": {
            "logical_bits": LOGICAL_BITS,
            "logical_bytes": LOGICAL_BYTES,
            "vm81_cells": VM81_CELLS,
            "positions_per_cell": POSITIONS_PER_CELL,
            "hash72_side": HASH72_SIDE,
            "phase_side": PHASE_SIDE,
            "reciprocal_ordered_cell_relations": RECIPROCAL_RELATIONS,
            "g243_controls": G243_CONTROLS,
            "projected_addresses": PROJECTED_ADDRESSES,
            "golay_payload_bits": GOLAY_PAYLOAD_BITS,
            "golay_codeword_bits": GOLAY_CODEWORD_BITS,
            "golay_words": GOLAY_WORDS,
            "physical_bits": PHYSICAL_BITS,
            "physical_bytes": PHYSICAL_BYTES,
        },
        "address_contract": {
            "linear": "s",
            "cell_operation": "s=64*c+o",
            "phase_pair": "s=64*c+8*alpha+beta",
            "hash72_matrix": "s=72*r+k",
            "g243_projection": "q=243*s+g",
            "all_5184_positions_exhaustive_round_trip_required": True,
        },
        "ordered_phase_contract": {
            "registry": list(ORDERED_PHASE_REGISTRY),
            "xy_distinct_from_yx": True,
            "zw_distinct_from_wz": True,
            "automatic_commutative_collapse_allowed": False,
        },
        "lo_shu_nucleus": {**nucleus, "nucleus_root_sha256": digest(nucleus)},
        "hash72_contract": {
            "alphabet_id": "HHS_CANONICAL_HASH72_ALPHABET_V1",
            "alphabet": HASH72_ALPHABET,
            "alphabet_symbol_count": HASH72_SYMBOL_COUNT,
            "matrix_rule": "H0[r,c]=alphabet[(r+c) mod 72]",
            "state_seed_duality_required": True,
            "reference_matrix_is_not_logical_genesis_rom": True,
        },
        "hash216_contract": {
            "section_order": list(HASH216_SECTIONS),
            "section_characters": 72,
            "total_characters": 216,
            "legacy_predecessor_current_successor_equivalence_proven": False,
            "legacy_lane_adapter_required": True,
            "positional_commitment": "SHA256(domain,version,context,section,local,absolute,character,parent,genesis,nucleus)",
        },
        "golay_contract": {
            "profile": "EXTENDED_BINARY_GOLAY_24_12_8",
            "mixed_error_erasure_bound": "2e+s<=7",
            "generator_matrix_selected": False,
            "bounded_decoder_implemented": False,
            "legacy_golay_style_placeholder_authoritative": False,
        },
        "vector_store_contract": {
            "similarity_is_candidate_discovery_only": True,
            "exact_payload_disambiguation_required": True,
            "vm81_admission_bypass_allowed": False,
            "parent_ancestry_and_inverse_support_required": True,
        },
        "artifact_paths": {
            "json": list(JSON_ARTIFACT_PATHS),
            "checksums": CHECKSUM_PATH,
            "evidence": EVIDENCE_PATH,
        },
        "claim_boundary": _machine_claim_boundary(),
    }


def build_invariants() -> dict[str, Any]:
    rows = [
        ("P217-I2-001", "81*64=5184=72*72", "EXACT_DIMENSION"),
        ("P217-I2-002", "5184 bits serialize as 648 bytes", "EXACT_DIMENSION"),
        ("P217-I2-003", "all canonical address views are bijective", "ADDRESS"),
        ("P217-I2-004", "the Lo Shu nucleus is fixed pointwise", "NUCLEUS"),
        ("P217-I2-005", "xy and yx remain distinct ordered identities", "ORDER"),
        ("P217-I2-006", "zw and wz remain distinct ordered identities", "ORDER"),
        ("P217-I2-007", "Hash72 uses the inherited canonical ordered alphabet", "HASH72"),
        ("P217-I2-008", "Hash216 section order is previous,next,receipt", "HASH216"),
        ("P217-I2-009", "SHA-256 authentication is not error correction", "LAYERING"),
        ("P217-I2-010", "Golay correction is physical-ROM-only and bounded", "GOLAY"),
        ("P217-I2-011", "vector similarity cannot admit canonical state", "VECTOR_STORE"),
        ("P217-I2-012", "no floating-point canonical authority", "ARITHMETIC"),
        ("P217-I2-013", "protected C VM81 semantics remain unchanged", "AUTHORITY"),
        ("P217-I2-014", "schema/reference vectors do not materialize ROM", "CLAIM_BOUNDARY"),
        ("P217-I2-015", "Pass 219 cannot begin runtime implementation through this bundle", "CLAIM_BOUNDARY"),
    ]
    return {
        "schema": "HHS_PASS_217_ITERATION_2_INVARIANTS_V1",
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "invariants": [
            {"id": identifier, "statement": statement, "family": family, "required": True}
            for identifier, statement, family in rows
        ],
        "claim_boundary": _machine_claim_boundary(),
    }


def _reference_hash216(nucleus_root: str) -> dict[str, Any]:
    previous = HASH72_ALPHABET
    next_value = HASH72_ALPHABET[1:] + HASH72_ALPHABET[:1]
    receipt = hash72_digest(
        {"domain": "HHS-P217-I2-STRUCTURAL-HASH216-REFERENCE-V1"},
        {"previous": previous, "next": next_value, "admitted": False},
    )
    combined = previous + next_value + receipt
    parent = sha256(b"HHS-P217-I2-NO-PARENT-REFERENCE\0").hexdigest()
    genesis = sha256(b"HHS-P217-I2-GENESIS-UNMATERIALIZED\0").hexdigest()
    context = sha256(b"HHS-P217-I2-HASH216-STRUCTURAL-CONTEXT\0").hexdigest()
    commitments: list[str] = []
    for section_index, section in enumerate(HASH216_SECTIONS):
        lane = (previous, next_value, receipt)[section_index]
        for local_position, character in enumerate(lane):
            absolute_position = section_index * HASH72_SIDE + local_position
            commitments.append(
                digest(
                    {
                        "domain": "HHS-P217-I2-POSITION-COMMITMENT-V1",
                        "version": 1,
                        "context_root_sha256": context,
                        "section": section,
                        "local_position": local_position,
                        "absolute_position": absolute_position,
                        "character": character,
                        "parent_ancestry_sha256": parent,
                        "genesis_root_sha256": genesis,
                        "nucleus_root_sha256": nucleus_root,
                    }
                )
            )
    return {
        "schema": "HHS_PASS_217_HASH216_TRANSITION_V1",
        "previous": previous,
        "next": next_value,
        "receipt": receipt,
        "combined": combined,
        "position_commitments": commitments,
        "commitments_root_sha256": sha256(
            b"HHS-P217-I2-POSITION-ROOT-V1\0"
            + b"".join(bytes.fromhex(value) for value in commitments)
        ).hexdigest(),
        "parent_ancestry_sha256": parent,
        "context_root_sha256": context,
        "genesis_root_sha256": genesis,
        "nucleus_root_sha256": nucleus_root,
        "authority_status": "REFERENCE_ONLY_NOT_ADMITTED",
    }


def build_reference_vectors(machine_contract: Mapping[str, Any]) -> dict[str, Any]:
    boundary_addresses = (0, 1, 7, 8, 63, 64, 71, 72, 511, 512, 5_183)
    controls = (0, 1, 242)
    orbit_vectors = []
    for direction in ("x", "y", "z", "w"):
        for row, column in ((0, 0), (0, 71), (35, 36), (71, 0), (71, 71)):
            for displacement in (-72, -1, 0, 1, 72):
                target = orbit_coordinate(direction, row, column, displacement)
                orbit_vectors.append(
                    {
                        "direction": direction,
                        "source": [row, column],
                        "displacement": displacement,
                        "target": list(target),
                    }
                )
    nucleus_root = str(machine_contract["lo_shu_nucleus"]["nucleus_root_sha256"])
    hash216 = _reference_hash216(nucleus_root)
    support = [0, 64, 5_183]
    vector_entry = {
        "schema": "HHS_PASS_217_VECTOR_STORE_ENTRY_V1",
        "entry_id_sha256": digest({"reference": "entry", "support": support}),
        "parent_state_sha256": digest({"reference": "parent", "admitted": False}),
        "candidate_state_sha256": digest({"reference": "candidate", "admitted": False}),
        "hash216_transition_sha256": digest(hash216),
        "forward_support": support,
        "inverse_support": support,
        "ordered_path": ["x", "y", "xy"],
        "bracketing": "((x*y)*xy)",
        "dependency_frontier": support,
        "collision_bucket": 0,
        "admission_status": "REFERENCE_ONLY",
    }
    admissible_bounds = [
        {"unknown_errors": errors, "known_erasures": erasures, "admissible": 2 * errors + erasures <= 7}
        for errors in range(5)
        for erasures in range(9)
    ]
    return {
        "schema": "HHS_PASS_217_ITERATION_2_REFERENCE_VECTORS_V1",
        "classification": "STRUCTURAL_REFERENCE_ONLY_NO_ROM_NO_ADMISSION",
        "address_map": {
            "exhaustive_record_count": LOGICAL_BITS,
            "exhaustive_root_sha256": exhaustive_address_root(),
            "boundary_vectors": [
                address_record(linear, control)
                for linear in boundary_addresses
                for control in controls
            ],
        },
        "ordered_phase": {
            "registry": list(ORDERED_PHASE_REGISTRY),
            "pair_surface": [f"{left}>{right}" for left in ORDERED_PHASE_REGISTRY for right in ORDERED_PHASE_REGISTRY],
            "pair_surface_root_sha256": digest(
                [f"{left}>{right}" for left in ORDERED_PHASE_REGISTRY for right in ORDERED_PHASE_REGISTRY]
            ),
        },
        "hash72": {
            "alphabet": HASH72_ALPHABET,
            "matrix_byte_count": LOGICAL_BITS,
            "matrix_root_sha256": hash72_matrix_root(),
            "selected_rows": {str(row): _phase_row(row) for row in (0, 1, 35, 71)},
            "orbit_vectors": orbit_vectors,
            "logical_genesis_rom_materialized": False,
        },
        "hash216": hash216,
        "golay": {
            "schema": "HHS_PASS_217_EXTENDED_GOLAY_PROFILE_V1",
            "code": "EXTENDED_BINARY_GOLAY_24_12_8",
            "payload_bits": GOLAY_PAYLOAD_BITS,
            "codeword_bits": GOLAY_CODEWORD_BITS,
            "distance": GOLAY_DISTANCE,
            "word_count": GOLAY_WORDS,
            "logical_bits": LOGICAL_BITS,
            "physical_bits": PHYSICAL_BITS,
            "mixed_bound": "2e+s<=7",
            "mixed_bound_vectors": admissible_bounds,
            "decoder_status": "PROFILE_ONLY",
            "generator_definition_status": "DEFERRED",
            "codewords_generated": False,
        },
        "vector_store": vector_entry,
        "claim_boundary": _machine_claim_boundary(),
    }


def build_json_artifacts(repository_root: Path | str) -> dict[str, Any]:
    machine = build_machine_contract(repository_root)
    return {
        "contracts/pass217/machine_contract.json": machine,
        "contracts/pass217/invariants.json": build_invariants(),
        "contracts/pass217/address_map.schema.json": build_address_schema(),
        "contracts/pass217/hash72.schema.json": build_hash72_schema(),
        "contracts/pass217/hash216.schema.json": build_hash216_schema(),
        "contracts/pass217/rom_manifest.schema.json": build_rom_manifest_schema(),
        "contracts/pass217/golay_profile.schema.json": build_golay_schema(),
        "contracts/pass217/vector_store.schema.json": build_vector_store_schema(),
        "contracts/pass217/reference_vectors.json": build_reference_vectors(machine),
    }


def _checksum_manifest(serialized: Mapping[str, bytes]) -> bytes:
    lines = [f"{sha256(serialized[path]).hexdigest()}  {path}" for path in sorted(serialized)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _build_evidence(
    serialized: Mapping[str, bytes],
    checksum_bytes: bytes,
) -> dict[str, Any]:
    rows = [
        {
            "path": path,
            "sha256": sha256(content).hexdigest(),
            "size_bytes": len(content),
        }
        for path, content in sorted({**serialized, CHECKSUM_PATH: checksum_bytes}.items())
    ]
    dispositions = Counter(record[2] for record in SOURCE_DECISIONS)
    references = json.loads(serialized["contracts/pass217/reference_vectors.json"])
    return {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "base_authority": {
            "main_commit": BASE_COMMIT,
            "main_tree": BASE_TREE,
            "iteration1_remote_commit": ITERATION1_REMOTE_COMMIT,
            "iteration1_tree": ITERATION1_TREE,
            "iteration1_freeze_sha256": ITERATION1_FREEZE_SHA256,
        },
        "bundle_files": rows,
        "bundle_root_sha256": digest(rows),
        "source_disposition_counts": dict(sorted(dispositions.items())),
        "reference_roots": {
            "address_map_sha256": references["address_map"]["exhaustive_root_sha256"],
            "hash72_matrix_sha256": references["hash72"]["matrix_root_sha256"],
            "hash216_commitments_sha256": references["hash216"]["commitments_root_sha256"],
            "ordered_phase_surface_sha256": references["ordered_phase"]["pair_surface_root_sha256"],
        },
        "inheritance_gate": {
            "status": INHERITANCE_HOLD,
            "schema_reference_preparation_allowed": True,
            "rom_runtime_or_migration_promotion_allowed": False,
        },
        "claim_boundary": _machine_claim_boundary(),
        "next_action": "Pass 217 Iteration 3 may generate the canonical Genesis candidate and address maps only after the Pass 215/216 authoritative lineage gate is reconciled or an explicit bounded non-promotional authority is recorded.",
    }


def build_bundle(repository_root: Path | str) -> dict[str, bytes]:
    json_objects = build_json_artifacts(repository_root)
    serialized = {path: canonical_bytes(value) + b"\n" for path, value in json_objects.items()}
    checksum_bytes = _checksum_manifest(serialized)
    evidence = canonical_bytes(_build_evidence(serialized, checksum_bytes)) + b"\n"
    return {**serialized, CHECKSUM_PATH: checksum_bytes, EVIDENCE_PATH: evidence}


def write_bundle(repository_root: Path | str) -> dict[str, bytes]:
    root = Path(repository_root).resolve()
    bundle = build_bundle(root)
    for path, content in bundle.items():
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    return bundle


def _validate_address_contract(reference: Mapping[str, Any]) -> None:
    seen_cell_operation: set[tuple[int, int]] = set()
    seen_hash72: set[tuple[int, int]] = set()
    for linear in range(LOGICAL_BITS):
        row = address_record(linear)
        if row["linear"] != 64 * row["cell"] + row["operation"]:
            raise Pass217Iteration2Error("PASS217_ITERATION2_CELL_OPERATION_ROUNDTRIP")
        if row["operation"] != 8 * row["alpha"] + row["beta"]:
            raise Pass217Iteration2Error("PASS217_ITERATION2_PHASE_PAIR_ROUNDTRIP")
        if row["linear"] != 72 * row["hash72_row"] + row["hash72_column"]:
            raise Pass217Iteration2Error("PASS217_ITERATION2_HASH72_ADDRESS_ROUNDTRIP")
        seen_cell_operation.add((row["cell"], row["operation"]))
        seen_hash72.add((row["hash72_row"], row["hash72_column"]))
    if len(seen_cell_operation) != LOGICAL_BITS or len(seen_hash72) != LOGICAL_BITS:
        raise Pass217Iteration2Error("PASS217_ITERATION2_ADDRESS_ALIAS")
    if reference["exhaustive_root_sha256"] != exhaustive_address_root():
        raise Pass217Iteration2Error("PASS217_ITERATION2_ADDRESS_ROOT_MISMATCH")


def _validate_hash72_contract(reference: Mapping[str, Any]) -> None:
    if len(HASH72_ALPHABET) != HASH72_SYMBOL_COUNT or len(set(HASH72_ALPHABET)) != 72:
        raise Pass217Iteration2Error("PASS217_ITERATION2_HASH72_ALPHABET_INVALID")
    if reference["alphabet"] != HASH72_ALPHABET:
        raise Pass217Iteration2Error("PASS217_ITERATION2_HASH72_ALPHABET_DRIFT")
    if reference["matrix_root_sha256"] != hash72_matrix_root():
        raise Pass217Iteration2Error("PASS217_ITERATION2_HASH72_MATRIX_ROOT")
    for direction in ("x", "y", "z", "w"):
        for row in range(HASH72_SIDE):
            for column in range(HASH72_SIDE):
                forward = orbit_coordinate(direction, row, column, 1)
                inverse = orbit_coordinate(direction, *forward, -1)
                closure = orbit_coordinate(direction, row, column, 72)
                if inverse != (row, column) or closure != (row, column):
                    raise Pass217Iteration2Error("PASS217_ITERATION2_ORBIT_CLOSURE")


def _validate_hash216_contract(reference: Mapping[str, Any]) -> None:
    lanes = [reference[name] for name in HASH216_SECTIONS]
    if any(not validate_hash72(lane) for lane in lanes):
        raise Pass217Iteration2Error("PASS217_ITERATION2_HASH216_LANE_INVALID")
    if reference["combined"] != "".join(lanes) or len(reference["combined"]) != 216:
        raise Pass217Iteration2Error("PASS217_ITERATION2_HASH216_SECTION_ORDER")
    commitments = reference["position_commitments"]
    if len(commitments) != 216 or len(set(commitments)) != 216:
        raise Pass217Iteration2Error("PASS217_ITERATION2_POSITION_COMMITMENTS_INVALID")
    expected = sha256(
        b"HHS-P217-I2-POSITION-ROOT-V1\0"
        + b"".join(bytes.fromhex(value) for value in commitments)
    ).hexdigest()
    if expected != reference["commitments_root_sha256"]:
        raise Pass217Iteration2Error("PASS217_ITERATION2_POSITION_ROOT_MISMATCH")
    if reference["authority_status"] != "REFERENCE_ONLY_NOT_ADMITTED":
        raise Pass217Iteration2Error("PASS217_ITERATION2_HASH216_AUTHORITY_OVERCLAIM")


def validate_bundle(
    repository_root: Path | str,
    bundle: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    expected = build_bundle(root)
    actual = dict(bundle) if bundle is not None else {
        path: (root / path).read_bytes() for path in expected
    }
    if set(actual) != set(expected):
        raise Pass217Iteration2Error("PASS217_ITERATION2_BUNDLE_PATH_SET_MISMATCH")
    for path, content in expected.items():
        if actual[path] != content:
            raise Pass217Iteration2Error(f"PASS217_ITERATION2_BUNDLE_DRIFT:{path}")

    machine = json.loads(actual["contracts/pass217/machine_contract.json"])
    invariants = json.loads(actual["contracts/pass217/invariants.json"])
    references = json.loads(actual["contracts/pass217/reference_vectors.json"])
    evidence = json.loads(actual[EVIDENCE_PATH])
    if machine["classification"] != CLASSIFICATION or evidence["schema"] != SCHEMA:
        raise Pass217Iteration2Error("PASS217_ITERATION2_CLASSIFICATION_MISMATCH")
    if machine["base_authority"]["iteration1_freeze_sha256"] != ITERATION1_FREEZE_SHA256:
        raise Pass217Iteration2Error("PASS217_ITERATION2_ITERATION1_BINDING_MISMATCH")
    if machine["inheritance_gate"]["status"] != INHERITANCE_HOLD:
        raise Pass217Iteration2Error("PASS217_ITERATION2_INHERITANCE_GATE_DRIFT")
    if len(invariants["invariants"]) != 15:
        raise Pass217Iteration2Error("PASS217_ITERATION2_INVARIANT_COUNT")

    _validate_address_contract(references["address_map"])
    _validate_hash72_contract(references["hash72"])
    _validate_hash216_contract(references["hash216"])

    golay = references["golay"]
    if GOLAY_WORDS * GOLAY_PAYLOAD_BITS != LOGICAL_BITS:
        raise Pass217Iteration2Error("PASS217_ITERATION2_GOLAY_LOGICAL_SIZE")
    if GOLAY_WORDS * GOLAY_CODEWORD_BITS != PHYSICAL_BITS:
        raise Pass217Iteration2Error("PASS217_ITERATION2_GOLAY_PHYSICAL_SIZE")
    if golay["decoder_status"] != "PROFILE_ONLY" or golay["codewords_generated"]:
        raise Pass217Iteration2Error("PASS217_ITERATION2_GOLAY_AUTHORITY_OVERCLAIM")
    for vector in golay["mixed_bound_vectors"]:
        expected_bound = 2 * vector["unknown_errors"] + vector["known_erasures"] <= 7
        if vector["admissible"] is not expected_bound:
            raise Pass217Iteration2Error("PASS217_ITERATION2_GOLAY_BOUND_VECTOR")

    for claims in (machine["claim_boundary"], invariants["claim_boundary"], references["claim_boundary"], evidence["claim_boundary"]):
        if not claims["schema_and_reference_preparation_complete"]:
            raise Pass217Iteration2Error("PASS217_ITERATION2_PREPARATION_NOT_COMPLETE")
        for key, value in claims.items():
            if key != "schema_and_reference_preparation_complete" and value:
                raise Pass217Iteration2Error(f"PASS217_ITERATION2_AUTHORITY_OVERCLAIM:{key}")

    checksum_lines = actual[CHECKSUM_PATH].decode("utf-8").splitlines()
    if len(checksum_lines) != len(JSON_ARTIFACT_PATHS):
        raise Pass217Iteration2Error("PASS217_ITERATION2_CHECKSUM_COUNT")
    for line in checksum_lines:
        checksum, path = line.split("  ", 1)
        if checksum != sha256(actual[path]).hexdigest():
            raise Pass217Iteration2Error(f"PASS217_ITERATION2_CHECKSUM_MISMATCH:{path}")

    protected = "hhs_runtime/HARMONICODE_VM_RUNTIME.c"
    if _git(root, "diff", "--name-only", BASE_COMMIT, "HEAD", "--", protected):
        raise Pass217Iteration2Error("PASS217_ITERATION2_PROTECTED_RUNTIME_MODIFIED")

    return {
        "classification": CLASSIFICATION,
        "bundle_root_sha256": evidence["bundle_root_sha256"],
        "address_map_root_sha256": references["address_map"]["exhaustive_root_sha256"],
        "hash72_matrix_root_sha256": references["hash72"]["matrix_root_sha256"],
        "hash216_commitments_root_sha256": references["hash216"]["commitments_root_sha256"],
        "source_binding_count": len(machine["source_bindings"]),
        "invariant_count": len(invariants["invariants"]),
        "json_artifact_count": len(JSON_ARTIFACT_PATHS),
        "inheritance_status": INHERITANCE_HOLD,
        "logical_genesis_rom_generated": False,
        "golay_physical_rom_generated": False,
        "authoritative_transition_minted": False,
    }


__all__ = [
    "BASE_COMMIT",
    "BASE_TREE",
    "CHECKSUM_PATH",
    "CLASSIFICATION",
    "EVIDENCE_PATH",
    "HASH216_SECTIONS",
    "INHERITANCE_HOLD",
    "ITERATION1_FREEZE_SHA256",
    "ITERATION1_REMOTE_COMMIT",
    "ITERATION1_TREE",
    "JSON_ARTIFACT_PATHS",
    "LO_SHU",
    "LO_SHU_PHASE_CHANNELS",
    "ORDERED_PHASE_REGISTRY",
    "Pass217Iteration2Error",
    "address_record",
    "build_bundle",
    "build_json_artifacts",
    "build_machine_contract",
    "build_reference_vectors",
    "canonical_bytes",
    "exhaustive_address_root",
    "hash72_matrix_root",
    "orbit_coordinate",
    "source_bindings",
    "validate_bundle",
    "write_bundle",
]
