from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import re

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import (
    ContractError,
    product_root,
    stable,
)

SCHEMA = "HHS_HASH72_HASH216_NATIVE_BINDING_REGISTRY_V1"
BINDING_SCHEMA = "HHS_HASH_NATIVE_ABI_BINDING_V1"
EXPECTED_SYMBOLS = (
    "hhs_hash72_clear",
    "hhs_hash216_clear",
    "hhs_hash72_compute",
    "hhs_hash216_compute",
    "hhs_hash72_reciprocal",
    "hhs_hash216_reciprocal",
    "hhs_hash72_equal",
    "hhs_hash216_equal",
)

PROTOTYPE_RE = re.compile(
    r"(?ms)^(?P<return>void|int)\s+"
    r"(?P<name>hhs_hash(?:72|216)_[A-Za-z0-9_]+)\s*"
    r"\((?P<args>.*?)\)\s*;"
)


def _opcode(symbol: str) -> str:
    return "NATIVE_" + symbol.upper().removeprefix("HHS_")


def _schemas(symbol: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    width = 216 if "216" in symbol else 72
    if symbol.endswith("_clear"):
        return (
            {
                "type": "object",
                "required": ["caller_owned_output"],
                "additionalProperties": False,
            },
            {
                "type": "object",
                "required": ["cleared", "symbol_count"],
                "properties": {
                    "cleared": {"const": True},
                    "symbol_count": {"const": width},
                },
            },
            "CALLER_OWNED_OUTPUT_MUTATION_ONLY",
        )
    if symbol.endswith("_compute"):
        return (
            {
                "type": "object",
                "required": ["canonical_bytes", "byte_length"],
                "additionalProperties": False,
                "properties": {
                    "byte_length": {"type": "integer", "minimum": 0},
                },
            },
            {
                "type": "object",
                "required": ["canonical_hash", "symbol_count"],
                "properties": {"symbol_count": {"const": width}},
            },
            "CALLER_OWNED_OUTPUT_MUTATION_ONLY",
        )
    if symbol.endswith("_reciprocal"):
        return (
            {
                "type": "object",
                "required": ["canonical_hash"],
                "additionalProperties": False,
            },
            {
                "type": "object",
                "required": ["reciprocal_hash", "symbol_count"],
                "properties": {"symbol_count": {"const": width}},
            },
            "CALLER_OWNED_OUTPUT_MUTATION_ONLY",
        )
    if symbol.endswith("_equal"):
        return (
            {
                "type": "object",
                "required": ["left", "right"],
                "additionalProperties": False,
            },
            {"type": "integer", "enum": [0, 1]},
            "READ_ONLY",
        )
    raise ContractError(f"REJECT_UNCLASSIFIED_HASH_ABI_SYMBOL:{symbol}")


def build_registry(repo: Path) -> dict[str, Any]:
    header_path = repo / "hhs_runtime/include/hhs_hash216.h"
    if not header_path.is_file():
        raise ContractError("REJECT_MISSING_HASH216_PUBLIC_HEADER")
    header = header_path.read_text(encoding="utf-8")
    signatures = {
        match.group("name"): " ".join(
            f"{match.group('return')} {match.group('name')}({match.group('args')})".split()
        )
        for match in PROTOTYPE_RE.finditer(header)
    }
    observed = tuple(sorted(signatures))
    expected = tuple(sorted(EXPECTED_SYMBOLS))
    if observed != expected:
        raise ContractError(
            "REJECT_HASH_ABI_SURFACE_MISMATCH:"
            f"expected={expected}:observed={observed}"
        )

    entries: list[dict[str, Any]] = []
    for symbol in EXPECTED_SYMBOLS:
        input_schema, output_schema, mutation_class = _schemas(symbol)
        width = 216 if "216" in symbol else 72
        body = stable(
            {
                "schema": BINDING_SCHEMA,
                "semantic_operation_identity": f"vm81.native.{symbol}",
                "native_opcode": _opcode(symbol),
                "abi_symbol": symbol,
                "abi_signature": signatures[symbol],
                "abi_disposition": "ADMITTED_EXISTING_DIRECT_ABI",
                "callable": True,
                "input_schema": input_schema,
                "output_schema": output_schema,
                "symbol_count": width,
                "memory_ownership": "CALLER_OWNS_INPUT_AND_OUTPUT_NATIVE_FUNCTION_HAS_NO_ORDINARY_VM81_MUTATION_AUTHORITY",
                "buffer_bounds": f"EXACT_{width}_SYMBOL_CANONICAL_OBJECT_OR_DECLARED_INPUT_BYTE_LENGTH",
                "mutation_class": mutation_class,
                "authority_scope": "HASH_IDENTITY_INTEGRITY_AND_PROJECTION_ONLY_NOT_ORDINARY_RUNTIME_TRANSITION_AUTHORITY",
                "numeric_policy": "EXACT_BYTE_AND_INTEGER_ONLY_NO_FLOATS",
                "failure_semantics": [
                    "REJECT_NULL_REQUIRED_POINTER_AT_GOVERNED_WRAPPER",
                    "REJECT_NONCANONICAL_HASH_OBJECT",
                    "REJECT_DECLARED_LENGTH_MISMATCH",
                    "REJECT_AUTHORITY_SCOPE_MISMATCH",
                ],
                "receipt_policy": "HASH216_OBJECT_COMMITMENT_DOES_NOT_REPLACE_REQUIRED_HASH72_TRANSITION_RECEIPT",
                "compiler_may_synthesize": False,
            }
        )
        body["binding_root_hash72"] = product_root(
            "hhs_hash_native_abi_binding_v1", body
        )
        entries.append(stable(body))

    result = stable(
        {
            "schema": SCHEMA,
            "binding_schema": BINDING_SCHEMA,
            "contract_id": "HHS-VM81-H216-NATIVE-DEV-ELASTIC-MEMORY",
            "source_header": "hhs_runtime/include/hhs_hash216.h",
            "registered_bindings": len(entries),
            "expected_bindings": len(EXPECTED_SYMBOLS),
            "all_expected_bindings_present": len(entries) == len(EXPECTED_SYMBOLS),
            "entries": entries,
        }
    )
    result["registry_root_hash72"] = product_root(
        "hhs_hash72_hash216_native_binding_registry_v1", result
    )
    return stable(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(build_registry(args.repo), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
