"""Pass 219 I182 canonical public-operation transport bridge.

This module adds no operation engine and no canonical authority.  It loads the
frozen Pass170 operation-record chain, resolves one existing HTTP route, and
invokes that route through the canonical ``hhs_backend.public_api_server:app``
ASGI object.  Python and CLI therefore traverse the same public application
surface rather than reimplementing operation semantics.

Native ABI parity is required only when an operation record declares a native
ABI symbol.  The inherited audio operation retains the I179 native/replay proof.
The single websocket operation remains streaming-only and is not scalarized
into an HTTP/CLI substitute.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

import httpx

SCHEMA = "HHS_PASS219_I182_PUBLIC_OPERATION_TRANSPORT_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I182"
ROOT_INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX_I180.json"
CANONICAL_GATEWAY = "hhs_backend.public_api_server:app"
PYTHON_BINDING = "hhs_runtime.pass219.pass170_public_transport_i182.invoke_public_operation_python"
CLI_BINDING = "python -m hhs_runtime.pass219.pass170_public_transport_i182 invoke"
EXPECTED_AGGREGATE_RECORDS = 59
EXPECTED_HTTP_RECORDS = 58
EXPECTED_STREAMING_RECORDS = 1
AUDIO_OPERATION_ID = "public.audio_language.feedback.run"
AUDIO_NATIVE_SYMBOL = "hhs_pass219_audio_security_admit_v1"

_PATH_PARAMETER = re.compile(r"\{([^}:]+)(?::[^}]+)?\}")


class Pass170I182TransportError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I182TransportError(
            f"PASS170_I182_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(value, dict):
        raise Pass170I182TransportError(f"PASS170_I182_JSON_ROOT_INVALID:{path}")
    return value


def _load_shard_records(root: Path, reference: Mapping[str, Any]) -> list[dict[str, Any]]:
    path = reference.get("path")
    if not isinstance(path, str) or not path:
        raise Pass170I182TransportError("PASS170_I182_SHARD_PATH_INVALID")
    shard = _load_json(root / path)
    records = shard.get("records")
    if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
        raise Pass170I182TransportError(f"PASS170_I182_SHARD_RECORDS_INVALID:{path}")
    return [dict(item) for item in records]


def _load_record_chain(
    root: Path,
    index_path: str,
    *,
    visited: set[str] | None = None,
) -> list[dict[str, Any]]:
    seen = set() if visited is None else visited
    if index_path in seen:
        raise Pass170I182TransportError(f"PASS170_I182_INDEX_CYCLE:{index_path}")
    seen.add(index_path)
    index = _load_json(root / index_path)

    if index.get("schema") == "HHS_PUBLIC_OPERATION_RECORD_INDEX_V1":
        refs = index.get("shards")
        if not isinstance(refs, list):
            raise Pass170I182TransportError("PASS170_I182_ROOT_SHARDS_INVALID")
        records: list[dict[str, Any]] = []
        for ref in refs:
            if not isinstance(ref, dict):
                raise Pass170I182TransportError("PASS170_I182_ROOT_SHARD_REF_INVALID")
            records.extend(_load_shard_records(root, ref))
    else:
        parent = index.get("frozen_parent_index")
        if not isinstance(parent, str) or not parent:
            raise Pass170I182TransportError(f"PASS170_I182_PARENT_INDEX_MISSING:{index_path}")
        records = _load_record_chain(root, parent, visited=seen)

        replacements = index.get("replacement_shards", [])
        if not isinstance(replacements, list):
            raise Pass170I182TransportError("PASS170_I182_REPLACEMENT_SHARDS_INVALID")
        by_id = {str(record.get("operation_id")): record for record in records}
        for ref in replacements:
            if not isinstance(ref, dict):
                raise Pass170I182TransportError("PASS170_I182_REPLACEMENT_REF_INVALID")
            for record in _load_shard_records(root, ref):
                operation_id = record.get("operation_id")
                if not isinstance(operation_id, str) or operation_id not in by_id:
                    raise Pass170I182TransportError(
                        f"PASS170_I182_REPLACEMENT_OPERATION_INVALID:{operation_id}"
                    )
                by_id[operation_id] = record
        records = [by_id[str(record.get("operation_id"))] for record in records]

        extensions = index.get("extension_shards", [])
        if not isinstance(extensions, list):
            raise Pass170I182TransportError("PASS170_I182_EXTENSION_SHARDS_INVALID")
        existing = {str(record.get("operation_id")) for record in records}
        for ref in extensions:
            if not isinstance(ref, dict):
                raise Pass170I182TransportError("PASS170_I182_EXTENSION_REF_INVALID")
            for record in _load_shard_records(root, ref):
                operation_id = record.get("operation_id")
                if not isinstance(operation_id, str) or not operation_id or operation_id in existing:
                    raise Pass170I182TransportError(
                        f"PASS170_I182_EXTENSION_OPERATION_INVALID:{operation_id}"
                    )
                existing.add(operation_id)
                records.append(record)

    declared = index.get("aggregate_record_count")
    if isinstance(declared, int) and declared != len(records):
        raise Pass170I182TransportError(
            f"PASS170_I182_INDEX_COUNT_MISMATCH:{index_path}:{declared}:{len(records)}"
        )
    operation_ids = [record.get("operation_id") for record in records]
    if any(not isinstance(item, str) or not item for item in operation_ids):
        raise Pass170I182TransportError("PASS170_I182_OPERATION_ID_INVALID")
    if len(operation_ids) != len(set(operation_ids)):
        raise Pass170I182TransportError("PASS170_I182_OPERATION_ID_DUPLICATE")
    return records


def operation_records(repository_root: str | Path = ".") -> dict[str, dict[str, Any]]:
    root = Path(repository_root).resolve()
    records = _load_record_chain(root, ROOT_INDEX)
    if len(records) != EXPECTED_AGGREGATE_RECORDS:
        raise Pass170I182TransportError(
            f"PASS170_I182_AGGREGATE_COUNT_INVALID:{len(records)}"
        )
    return {str(record["operation_id"]): record for record in records}


def _reject_float(value: Any, path: str = "payload") -> None:
    if isinstance(value, float):
        raise Pass170I182TransportError(f"PASS170_I182_FLOAT_TRANSPORT_REJECTED:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def _render_path(template: str, path_parameters: Mapping[str, Any]) -> str:
    names = _PATH_PARAMETER.findall(template)
    expected = set(names)
    supplied = set(path_parameters)
    if supplied != expected:
        raise Pass170I182TransportError(
            "PASS170_I182_PATH_PARAMETER_SET_MISMATCH:"
            f"expected={sorted(expected)}:supplied={sorted(supplied)}"
        )
    rendered = template
    for name in names:
        value = path_parameters[name]
        if isinstance(value, (dict, list, tuple, float)) or value is None:
            raise Pass170I182TransportError(f"PASS170_I182_PATH_PARAMETER_INVALID:{name}")
        rendered = re.sub(r"\{" + re.escape(name) + r"(?::[^}]+)?\}", str(value), rendered)
    return rendered


async def invoke_public_operation_python_async(
    operation_id: str,
    *,
    payload: Mapping[str, Any] | None = None,
    path_parameters: Mapping[str, Any] | None = None,
    query_parameters: Mapping[str, Any] | None = None,
    authorization: str | None = None,
    repository_root: str | Path = ".",
) -> dict[str, Any]:
    """Invoke one registered HTTP operation through the canonical ASGI app."""
    records = operation_records(repository_root)
    record = records.get(operation_id)
    if record is None:
        raise Pass170I182TransportError(f"PASS170_I182_OPERATION_NOT_REGISTERED:{operation_id}")
    websocket = record.get("WebSocket_channel")
    method = record.get("HTTP_method")
    template = record.get("HTTP_path")
    if isinstance(websocket, str) and websocket and not method:
        raise Pass170I182TransportError(
            f"PASS170_I182_STREAMING_OPERATION_REQUIRES_WEBSOCKET:{operation_id}"
        )
    if not isinstance(method, str) or not isinstance(template, str):
        raise Pass170I182TransportError(f"PASS170_I182_HTTP_BINDING_MISSING:{operation_id}")

    body = dict(payload or {})
    path_values = dict(path_parameters or {})
    query_values = dict(query_parameters or {})
    _reject_float(body)
    _reject_float(path_values, "path_parameters")
    _reject_float(query_values, "query_parameters")
    path = _render_path(template, path_values)
    headers: dict[str, str] = {}
    if authorization is not None:
        headers["Authorization"] = authorization

    from hhs_backend.public_api_server import app as canonical_app

    transport = httpx.ASGITransport(app=canonical_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://hhs.pass170.local") as client:
        kwargs: dict[str, Any] = {"headers": headers, "params": query_values}
        if method.upper() not in {"GET", "HEAD", "OPTIONS"}:
            kwargs["json"] = body
        response = await client.request(method.upper(), path, **kwargs)

    try:
        response_body: Any = response.json()
    except ValueError:
        response_body = response.text
    return {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "operation_id": operation_id,
        "method": method.upper(),
        "path": path,
        "status_code": response.status_code,
        "response": response_body,
        "canonical_gateway": CANONICAL_GATEWAY,
        "transport": "IN_PROCESS_ASGI_CANONICAL_GATEWAY",
        "python_binding": PYTHON_BINDING,
        "cli_binding": CLI_BINDING,
        "semantic_engine_reimplemented": False,
        "canonical_state_mutated_by_transport_layer": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
    }


def invoke_public_operation_python(
    operation_id: str,
    *,
    payload: Mapping[str, Any] | None = None,
    path_parameters: Mapping[str, Any] | None = None,
    query_parameters: Mapping[str, Any] | None = None,
    authorization: str | None = None,
    repository_root: str | Path = ".",
) -> dict[str, Any]:
    """Synchronous Python binding for the canonical ASGI transport."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(
            invoke_public_operation_python_async(
                operation_id,
                payload=payload,
                path_parameters=path_parameters,
                query_parameters=query_parameters,
                authorization=authorization,
                repository_root=repository_root,
            )
        )
    raise Pass170I182TransportError(
        "PASS170_I182_SYNC_BINDING_CALLED_FROM_RUNNING_EVENT_LOOP:USE_ASYNC_BINDING"
    )


def _json_mapping(text: str | None, label: str) -> dict[str, Any]:
    if text is None:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise Pass170I182TransportError(f"PASS170_I182_{label}_JSON_INVALID") from exc
    if not isinstance(value, dict):
        raise Pass170I182TransportError(f"PASS170_I182_{label}_MAPPING_REQUIRED")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pass170-public-transport-i182")
    sub = parser.add_subparsers(dest="command", required=True)
    invoke = sub.add_parser("invoke")
    invoke.add_argument("--operation-id", required=True)
    invoke.add_argument("--payload-json")
    invoke.add_argument("--path-parameters-json")
    invoke.add_argument("--query-parameters-json")
    invoke.add_argument("--authorization")
    invoke.add_argument("--repository-root", default=".")
    records = sub.add_parser("records")
    records.add_argument("--repository-root", default=".")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "records":
        records = operation_records(args.repository_root)
        print(json.dumps({"count": len(records), "operation_ids": sorted(records)}, sort_keys=True))
        return 0
    result = invoke_public_operation_python(
        args.operation_id,
        payload=_json_mapping(args.payload_json, "PAYLOAD"),
        path_parameters=_json_mapping(args.path_parameters_json, "PATH_PARAMETERS"),
        query_parameters=_json_mapping(args.query_parameters_json, "QUERY_PARAMETERS"),
        authorization=args.authorization,
        repository_root=args.repository_root,
    )
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0 if 200 <= int(result["status_code"]) < 500 else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AUDIO_NATIVE_SYMBOL",
    "AUDIO_OPERATION_ID",
    "CANONICAL_GATEWAY",
    "CLI_BINDING",
    "CONTRACT_ID",
    "EXPECTED_AGGREGATE_RECORDS",
    "EXPECTED_HTTP_RECORDS",
    "EXPECTED_STREAMING_RECORDS",
    "ITERATION",
    "PYTHON_BINDING",
    "Pass170I182TransportError",
    "invoke_public_operation_python",
    "invoke_public_operation_python_async",
    "operation_records",
]
