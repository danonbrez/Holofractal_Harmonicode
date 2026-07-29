"""Governed read-only HHS API tools for the production assistant.

The gateway exposes canonical HHS API route functions and bounded repository
knowledge retrieval without allowing a model-generated call to cross a mutation
boundary. Every result is returned in a Hash72-witnessed envelope.
"""
from __future__ import annotations

import asyncio
import inspect
import re
import time
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Mapping

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "HHS_ASSISTANT_API_TOOL_GATEWAY_V1"
AUTHORITY = "HHS_ASSISTANT_READ_ONLY_API_TOOL_AUTHORITY_V1"
TOOL_RECEIPT_SCHEMA = "HHS_ASSISTANT_API_TOOL_RECEIPT_V1"
TOOL_REGISTRY_SCHEMA = "HHS_ASSISTANT_API_TOOL_REGISTRY_V1"
REPOSITORY_SEARCH_SCHEMA = "HHS_BOUNDED_REPOSITORY_KNOWLEDGE_SEARCH_V1"

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_ALLOWED_SUFFIXES = {".md", ".txt", ".json", ".py", ".c", ".h", ".ts", ".tsx", ".js", ".mjs"}
_EXCLUDED_PARTS = {
    ".git", "node_modules", "dist", "build", "builds", "__pycache__",
    ".pytest_cache", ".venv", "venv", "release_artifacts", "evidence",
}
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "the", "to", "what",
    "when", "where", "which", "who", "why", "with",
}

ToolCallable = Callable[..., Any]


def _now_ms() -> int:
    return int(time.time() * 1000)


def _function_tool(
    name: str,
    description: str,
    properties: Dict[str, Any] | None = None,
    required: List[str] | None = None,
) -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


DEFAULT_HHS_ASSISTANT_TOOLS: List[Dict[str, Any]] = [
    _function_tool(
        "hhs_runtime_state",
        "Read the latest guarded HHS/VM81 runtime state through the canonical runtime API.",
    ),
    _function_tool(
        "hhs_runtime_services",
        "List services registered on the canonical HHS runtime API.",
    ),
    _function_tool(
        "hhs_runtime_service_status",
        "Read status for all registered HHS runtime services.",
    ),
    _function_tool(
        "hhs_kernel_invariants",
        "List the active kernel conformance invariants and their Hash72-governed definitions.",
    ),
    _function_tool(
        "hhs_kernel_conformance_status",
        "Read the current kernel invariant and conformance-surface status.",
    ),
    _function_tool(
        "hhs_pass152_status",
        "Read the current Pass 152 elastic-closure status and latest execution projection.",
    ),
    _function_tool(
        "hhs_pass152_capabilities",
        "Read the Pass 152 lifecycle, dependency, authority, and control-vector capabilities.",
    ),
    _function_tool(
        "hhs_repository_search",
        "Search bounded repository source and documentation for query-specific HHS evidence.",
        properties={
            "query": {"type": "string", "minLength": 2},
            "limit": {"type": "integer", "minimum": 1, "maximum": 8},
        },
        required=["query"],
    ),
]


async def _runtime_state(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import get_runtime_state
    return await get_runtime_state()


async def _runtime_services(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import list_runtime_services
    return await list_runtime_services()


async def _runtime_service_status(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import runtime_services_status
    return await runtime_services_status()


async def _kernel_invariants(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import list_kernel_conformance_invariants
    return await list_kernel_conformance_invariants()


async def _kernel_conformance_status(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.runtime_routes import kernel_conformance_status
    return await kernel_conformance_status()


async def _pass152_status(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.pass152_elastic_closure_routes import pass152_status
    result = pass152_status()
    return await result if inspect.isawaitable(result) else result


async def _pass152_capabilities(_: Mapping[str, Any]) -> Dict[str, Any]:
    from hhs_backend.api.pass152_elastic_closure_routes import pass152_capabilities
    result = pass152_capabilities()
    return await result if inspect.isawaitable(result) else result


def _query_terms(query: str) -> List[str]:
    terms: List[str] = []
    for token in re.findall(r"[A-Za-z0-9_ΔΩΘΨΦΓΛ]+", query.casefold()):
        if len(token) < 2 or token in _STOP_WORDS or token in terms:
            continue
        terms.append(token)
    return terms[:12]


def _eligible_file(path: Path) -> bool:
    try:
        relative = path.relative_to(_REPOSITORY_ROOT)
    except ValueError:
        return False
    if any(part in _EXCLUDED_PARTS or part.startswith(".") for part in relative.parts):
        return False
    if path.suffix.casefold() not in _ALLOWED_SUFFIXES:
        return False
    try:
        return 0 < path.stat().st_size <= 384_000
    except OSError:
        return False


def _snippet(text: str, terms: List[str]) -> str:
    folded = text.casefold()
    positions = [folded.find(term) for term in terms if folded.find(term) >= 0]
    start = max(0, (min(positions) if positions else 0) - 180)
    end = min(len(text), start + 720)
    excerpt = re.sub(r"\s+", " ", text[start:end]).strip()
    if start:
        excerpt = "…" + excerpt
    if end < len(text):
        excerpt += "…"
    return excerpt


def _search_repository_sync(query: str, limit: int) -> Dict[str, Any]:
    normalized = str(query or "").strip()
    if len(normalized) < 2:
        raise ValueError("repository search query must contain at least two characters")
    bounded_limit = max(1, min(8, int(limit or 5)))
    terms = _query_terms(normalized)
    if not terms:
        terms = [normalized.casefold()]

    candidates: List[Dict[str, Any]] = []
    scanned = 0
    for path in _REPOSITORY_ROOT.rglob("*"):
        if scanned >= 2400:
            break
        if not path.is_file() or not _eligible_file(path):
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        folded = text.casefold()
        relative = path.relative_to(_REPOSITORY_ROOT).as_posix()
        filename = relative.casefold()
        score = 0
        matched: List[str] = []
        for term in terms:
            count = folded.count(term)
            if count:
                matched.append(term)
                score += min(count, 24)
            if term in filename:
                score += 12
        if normalized.casefold() in folded:
            score += 18
        if not score:
            continue
        candidates.append({
            "path": relative,
            "score": score,
            "matched_terms": matched,
            "snippet": _snippet(text, matched or terms),
        })

    candidates.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
    results = candidates[:bounded_limit]
    return {
        "schema": REPOSITORY_SEARCH_SCHEMA,
        "ok": True,
        "query": normalized,
        "terms": terms,
        "result_count": len(results),
        "results": results,
        "files_scanned": scanned,
        "file_scan_limit": 2400,
        "bounded": True,
        "read_only": True,
        "runtime_mutation_admitted": False,
    }


async def _repository_search(arguments: Mapping[str, Any]) -> Dict[str, Any]:
    return await asyncio.to_thread(
        _search_repository_sync,
        str(arguments.get("query") or ""),
        int(arguments.get("limit") or 5),
    )


_READ_ONLY_EXECUTORS: Dict[str, Callable[[Mapping[str, Any]], Awaitable[Dict[str, Any]]]] = {
    "hhs_runtime_state": _runtime_state,
    "hhs_runtime_services": _runtime_services,
    "hhs_runtime_service_status": _runtime_service_status,
    "hhs_kernel_invariants": _kernel_invariants,
    "hhs_kernel_conformance_status": _kernel_conformance_status,
    "hhs_pass152_status": _pass152_status,
    "hhs_pass152_capabilities": _pass152_capabilities,
    "hhs_repository_search": _repository_search,
}


def assistant_api_tool_registry() -> Dict[str, Any]:
    registry = {
        "schema": TOOL_REGISTRY_SCHEMA,
        "version": VERSION,
        "tools": DEFAULT_HHS_ASSISTANT_TOOLS,
        "tool_names": sorted(_READ_ONLY_EXECUTORS),
        "read_only": True,
        "model_self_authorization_allowed": False,
        "mutating_tool_execution_allowed": False,
        "authority": AUTHORITY,
    }
    registry["tool_registry_root_hash72"] = hash72(TOOL_REGISTRY_SCHEMA, registry)
    return registry


async def execute_hhs_assistant_api_tool(
    tool_name: str,
    arguments: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    name = str(tool_name or "")
    args = dict(arguments or {})
    executor = _READ_ONLY_EXECUTORS.get(name)
    if executor is None:
        receipt = {
            "schema": TOOL_RECEIPT_SCHEMA,
            "version": VERSION,
            "ok": False,
            "status": "REJECT_HHS_ASSISTANT_API_TOOL_CALL",
            "tool_name": name,
            "arguments": args,
            "reason": "tool is not registered as a read-only HHS assistant API surface",
            "read_only": True,
            "runtime_mutation_admitted": False,
            "model_self_authorized": False,
            "created_at_unix_ms": _now_ms(),
            "authority": AUTHORITY,
        }
        receipt["tool_receipt_root_hash72"] = hash72(TOOL_RECEIPT_SCHEMA, receipt)
        return receipt

    try:
        response = await executor(args)
        ok = True
        status = "ADMIT_READ_ONLY_HHS_ASSISTANT_API_TOOL_RESULT"
        error = None
    except Exception as exc:
        response = None
        ok = False
        status = "HHS_ASSISTANT_API_TOOL_EXECUTION_ERROR"
        error = f"{type(exc).__name__}: {exc}"

    receipt = {
        "schema": TOOL_RECEIPT_SCHEMA,
        "version": VERSION,
        "ok": ok,
        "status": status,
        "tool_name": name,
        "arguments": args,
        "response": response,
        "error": error,
        "read_only": True,
        "runtime_mutation_admitted": False,
        "model_self_authorized": False,
        "created_at_unix_ms": _now_ms(),
        "authority": AUTHORITY,
    }
    receipt["tool_receipt_root_hash72"] = hash72(TOOL_RECEIPT_SCHEMA, receipt)
    return receipt


async def assistant_api_tool_gateway_self_test() -> Dict[str, Any]:
    registry = assistant_api_tool_registry()
    status_receipt = await execute_hhs_assistant_api_tool("hhs_pass152_status", {})
    search_receipt = await execute_hhs_assistant_api_tool(
        "hhs_repository_search",
        {"query": "HARMONICODE language service", "limit": 2},
    )
    rejected = await execute_hhs_assistant_api_tool("hhs_runtime_halt", {})
    ok = bool(
        registry.get("tool_registry_root_hash72")
        and status_receipt.get("ok")
        and search_receipt.get("ok")
        and search_receipt.get("response", {}).get("results")
        and not status_receipt.get("runtime_mutation_admitted")
        and not rejected.get("ok")
        and rejected.get("status") == "REJECT_HHS_ASSISTANT_API_TOOL_CALL"
    )
    return {
        "schema": "HHS_ASSISTANT_API_TOOL_GATEWAY_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "registry": registry,
        "status_receipt": status_receipt,
        "search_receipt": search_receipt,
        "rejected_mutation_attempt": rejected,
    }
