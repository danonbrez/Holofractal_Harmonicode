"""Pass 219 I169 / Pass 170 public-authority inventory gate.

This module is intentionally read-only.  It inventories repository-visible public
application constructors and ingress surfaces, verifies the frozen Pass 169
terminal parent receipt, and reports the exact Pass 170 authority blockers that
must be repaired next.  It does not create a FastAPI application, runtime,
receipt authority, or canonical state mutation path.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "HHS_PASS219_I169_PASS170_PUBLIC_AUTHORITY_INVENTORY_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I169"
BASE_MAIN = "8a25c30201428fcddf94437d62a16655785e3d22"
PASS169_RECEIPT = "HHS_PASS_169_COMPLETION_RECEIPT.json"
CANONICAL_GATEWAY = "hhs_backend/public_api_server.py"
PUBLIC_OPERATION_REGISTRY = "HHS_PUBLIC_OPERATION_REGISTRY.json"
PUBLIC_NETWORK_PORT_REGISTRY = "HHS_PUBLIC_NETWORK_PORT_REGISTRY.json"

_EXCLUDED_PARTS = {
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "artifacts",
    "build",
    "builds",
    "dist",
    "docs",
    "node_modules",
    "site-packages",
    "tests",
    "vendor",
    "venv",
}
_ROUTE_METHODS = {"delete", "get", "head", "options", "patch", "post", "put", "trace", "websocket"}
_PUBLIC_TOKENS = ("FastAPI(", "uvicorn.run", ".websocket(", ".get(", ".post(", ".put(", ".patch(", ".delete(")


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _iter_python_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.py")):
        rel_parts = path.relative_to(root).parts
        if any(part in _EXCLUDED_PARTS for part in rel_parts[:-1]):
            continue
        yield path


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _constant_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _location(path: Path, root: Path, node: ast.AST, **extra: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": _relative(path, root),
        "line": int(getattr(node, "lineno", 0) or 0),
    }
    record.update(extra)
    return record


def _scan_python_file(path: Path, root: Path) -> dict[str, list[dict[str, Any]]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    result: dict[str, list[dict[str, Any]]] = {
        "fastapi_constructors": [],
        "route_decorators": [],
        "uvicorn_run_sites": [],
        "socket_bind_sites": [],
        "parse_errors": [],
    }
    try:
        tree = ast.parse(text, filename=_relative(path, root))
    except SyntaxError as exc:
        if any(token in text for token in _PUBLIC_TOKENS):
            result["parse_errors"].append(
                {
                    "path": _relative(path, root),
                    "line": int(exc.lineno or 0),
                    "message": str(exc.msg),
                }
            )
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node.func)
            leaf = name.rsplit(".", 1)[-1]
            if leaf == "FastAPI":
                result["fastapi_constructors"].append(_location(path, root, node, call=name))
            elif name == "uvicorn.run" or name.endswith(".uvicorn.run"):
                result["uvicorn_run_sites"].append(_location(path, root, node, call=name))
            elif leaf == "bind" and isinstance(node.func, ast.Attribute):
                base = _call_name(node.func.value)
                if "socket" in base.lower() or base.lower().endswith(("sock", "server_socket")):
                    result["socket_bind_sites"].append(_location(path, root, node, call=name))

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                    continue
                method = decorator.func.attr.lower()
                if method not in _ROUTE_METHODS:
                    continue
                route = _constant_string(decorator.args[0]) if decorator.args else None
                result["route_decorators"].append(
                    _location(
                        path,
                        root,
                        decorator,
                        method=method.upper(),
                        route=route,
                        function=node.name,
                        owner=_call_name(decorator.func.value),
                    )
                )
    return result


def _verify_pass169_parent(root: Path) -> dict[str, Any]:
    path = root / PASS169_RECEIPT
    if not path.is_file():
        return {
            "receipt_path": PASS169_RECEIPT,
            "present": False,
            "verified": False,
            "terminal_verified": False,
            "classification": None,
            "blockers": ["PASS169_TERMINAL_PARENT_RECEIPT_ABSENT"],
        }
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "receipt_path": PASS169_RECEIPT,
            "present": True,
            "verified": False,
            "terminal_verified": False,
            "classification": None,
            "blockers": ["PASS169_TERMINAL_PARENT_RECEIPT_INVALID"],
            "error": f"{type(exc).__name__}:{exc}",
        }

    blockers: list[str] = []
    if receipt.get("contract_id") != "HHS-P169-HSAE-VM81-ESCPR":
        blockers.append("PASS169_TERMINAL_PARENT_CONTRACT_MISMATCH")
    if receipt.get("verified") is not True or receipt.get("terminal_verified") is not True:
        blockers.append("PASS169_TERMINAL_PARENT_NOT_VERIFIED")
    if receipt.get("terminal_blockers") not in ([], None):
        blockers.append("PASS169_TERMINAL_PARENT_HAS_BLOCKERS")
    forbidden_true = [
        key
        for key in (
            "new_vm81_authority",
            "new_hash72_mint_authority",
            "hash216_persistence_authority",
            "floating_point_canonical_authority",
            "fallback_used",
        )
        if receipt.get(key) is True
    ]
    if forbidden_true:
        blockers.append("PASS169_TERMINAL_PARENT_AUTHORITY_INVARIANT_VIOLATION")

    return {
        "receipt_path": PASS169_RECEIPT,
        "present": True,
        "verified": not blockers,
        "terminal_verified": receipt.get("terminal_verified") is True,
        "classification": receipt.get("classification"),
        "operation_verified_mask": receipt.get("operation_verified_mask"),
        "forbidden_true": forbidden_true,
        "blockers": blockers,
    }


def build_i169_pass170_public_authority_inventory(repository_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repository_root).resolve()
    parent = _verify_pass169_parent(root)

    aggregate: dict[str, list[dict[str, Any]]] = {
        "fastapi_constructors": [],
        "route_decorators": [],
        "uvicorn_run_sites": [],
        "socket_bind_sites": [],
        "parse_errors": [],
    }
    python_files_considered = 0
    for path in _iter_python_files(root):
        python_files_considered += 1
        scanned = _scan_python_file(path, root)
        for key in aggregate:
            aggregate[key].extend(scanned[key])

    for key in aggregate:
        aggregate[key] = sorted(
            aggregate[key],
            key=lambda item: (item.get("path", ""), int(item.get("line", 0)), json.dumps(item, sort_keys=True)),
        )

    required = {
        "canonical_gateway": {"path": CANONICAL_GATEWAY, "present": (root / CANONICAL_GATEWAY).is_file()},
        "public_operation_registry": {
            "path": PUBLIC_OPERATION_REGISTRY,
            "present": (root / PUBLIC_OPERATION_REGISTRY).is_file(),
        },
        "public_network_port_registry": {
            "path": PUBLIC_NETWORK_PORT_REGISTRY,
            "present": (root / PUBLIC_NETWORK_PORT_REGISTRY).is_file(),
        },
    }

    blockers = list(parent["blockers"])
    if aggregate["parse_errors"]:
        blockers.append("PASS170_PUBLIC_SURFACE_PARSE_ERRORS")
    if not required["canonical_gateway"]["present"]:
        blockers.append("PASS170_CANONICAL_PUBLIC_GATEWAY_ABSENT")
    if not required["public_operation_registry"]["present"]:
        blockers.append("PASS170_PUBLIC_OPERATION_REGISTRY_ABSENT")
    if not required["public_network_port_registry"]["present"]:
        blockers.append("PASS170_PUBLIC_NETWORK_PORT_REGISTRY_ABSENT")
    if len(aggregate["fastapi_constructors"]) > 1:
        blockers.append("PASS170_MULTIPLE_FASTAPI_CONSTRUCTORS_PRESENT")

    blockers = sorted(set(blockers))
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "repository_root_classification": "READ_ONLY_SCAN_ROOT",
        "parent_pass169": parent,
        "required_surfaces": required,
        "inventory": {
            "python_files_considered": python_files_considered,
            "fastapi_constructor_count": len(aggregate["fastapi_constructors"]),
            "route_decorator_count": len(aggregate["route_decorators"]),
            "uvicorn_run_site_count": len(aggregate["uvicorn_run_sites"]),
            "socket_bind_site_count": len(aggregate["socket_bind_sites"]),
            **aggregate,
        },
        "blockers": blockers,
        "inventory_evidence_verified": parent["verified"] and not aggregate["parse_errors"],
        "pass170_terminal_contract_verified": False,
        "canonical_state_mutated": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "next_boundary": (
            "PASS170_CANONICAL_GATEWAY_AND_REGISTRY_REPAIR"
            if blockers
            else "PASS170_OPERATION_REGISTRY_AND_ROUTE_PARITY"
        ),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_root", nargs="?", default=".")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = build_i169_pass170_public_authority_inventory(args.repository_root)
    rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
