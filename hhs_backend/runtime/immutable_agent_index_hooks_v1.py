"""Boot and event bridges for the immutable HHS agent SQL index.

This module attaches append-only evidence capture to existing cognition and
semantic-memory surfaces without giving those generators a protected-log read
or deletion capability.
"""
from __future__ import annotations

import functools
import os
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

from hhs_backend.runtime.immutable_agent_sql_index_v1 import (
    HHSImmutableAgentSQLIndex,
    _data,
    h72,
    immutable_agent_sql_index,
)

_HOOK_VERSION = "HHS_IMMUTABLE_AGENT_INDEX_HOOKS_V1"
_INSTALLED_IDS: set[int] = set()
_SEMANTIC_HOOKED = False


def _mapping(value: Any) -> dict[str, Any]:
    converted = _data(value)
    return dict(converted) if isinstance(converted, Mapping) else {"value": converted}


def _route_inventory(index: HHSImmutableAgentSQLIndex) -> dict[str, Any]:
    routes: list[Any] = []
    try:
        from hhs_backend.api.runtime_routes import router as runtime_router
        routes.extend(list(runtime_router.routes))
    except Exception:
        pass
    server = sys.modules.get("hhs_backend.server")
    app = getattr(server, "app", None) if server is not None else None
    if app is not None:
        routes.extend(list(getattr(app, "routes", ())))
    return index.register_api_routes(routes)


def _pass145_candidates() -> list[Path]:
    values = [
        os.getenv("HHS_PASS145_DB", ""),
        os.getenv("HHS_KNOWLEDGE_DB", ""),
        "data/runtime/hhs_pass145.sqlite3",
        "data/runtime/hhs_knowledge.sqlite3",
        "data/runtime/hhs_knowledge.db",
        "data/hhs_pass145.sqlite3",
        "data/hhs_knowledge.sqlite3",
        "hhs_pass145.sqlite3",
    ]
    result: list[Path] = []
    seen: set[str] = set()
    for value in values:
        if not value:
            continue
        path = Path(value).expanduser().resolve()
        key = str(path)
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def _register_layers(index: HHSImmutableAgentSQLIndex) -> dict[str, Any]:
    layers = [
        ("runtime_state_store", "DETERMINISTIC_RUNTIME_CONTINUITY", "hhs_storage.runtime_state_store_v1", "IN_MEMORY_APPEND_LEDGER", "VM81_RUNTIME_EVIDENCE"),
        ("semantic_memory_engine", "SEMANTIC_VECTOR_MEMORY", "hhs_backend.runtime.runtime_semantic_memory_engine", "IN_MEMORY_GUARDED_VECTOR_INDEX", "SEMANTIC_MEMORY_AUTHORITY"),
        ("runtime_replay_engine", "DETERMINISTIC_REPLAY", "hhs_backend.runtime.runtime_replay_engine", "IN_MEMORY_REPLAY_WINDOW", "REPLAY_EVIDENCE"),
        ("adaptive_goal_engine", "CONSTRAINT_BOUNDED_GOALS", "hhs_backend.runtime.runtime_adaptive_goal_engine", "IN_MEMORY_GOAL_REGISTRY", "NON_OVERRIDE_GOAL_BIAS"),
        ("agentic_cognition_layer", "REPLAY_GOVERNED_COGNITION", "hhs_backend.runtime.runtime_agentic_cognition_layer", "IN_MEMORY_TASK_REGISTRY", "REQUEST_DRIVEN_COGNITION"),
        ("autonomous_research_layer", "BOUNDED_RESEARCH", "hhs_backend.runtime.runtime_autonomous_research_layer", "IN_MEMORY_RESEARCH_REGISTRY", "REQUEST_DRIVEN_RESEARCH"),
        ("recursive_toolchain_layer", "RECURSIVE_TOOLCHAIN", "hhs_backend.runtime.runtime_recursive_toolchain_layer", "IN_MEMORY_TOOLCHAIN_REGISTRY", "REQUEST_DRIVEN_TOOLCHAIN"),
        ("distributed_consensus_runtime", "DISTRIBUTED_CONSENSUS", "hhs_backend.runtime.distributed_consensus_runtime", "IN_MEMORY_CONSENSUS_REGISTRY", "CONSENSUS_EVIDENCE"),
        ("multinode_goal_consensus", "FEDERATED_GOAL_ALIGNMENT", "hhs_backend.runtime.runtime_multinode_goal_consensus", "IN_MEMORY_FEDERATED_REGISTRY", "NO_INVARIANT_OVERRIDE"),
        ("live_cognition_runtime", "LIVE_COGNITION_COORDINATOR", "hhs_backend.runtime.live_cognition_runtime_v1", "BOOT_REACHABLE_COORDINATOR", "COMMITTED_PACKET_OBSERVER_ONLY"),
        ("api_geometry_index", "API_TOPOLOGY", "hhs_backend.runtime.immutable_agent_sql_index_v1", "IMMUTABLE_SQL_GEOMETRY", "GUARDED_API_PROJECTION"),
    ]
    registered = []
    for name, kind, module, storage, authority in layers:
        registered.append(index.register_database_layer(
            name, kind, module, storage, authority,
            schema_id=_HOOK_VERSION, schema_version="1.0.0",
            details={"wired_by": _HOOK_VERSION},
        ))
    backfills = []
    for path in _pass145_candidates():
        if path.is_file() and path != index.path:
            try:
                backfills.append(index.backfill_pass145_constraints(path))
            except Exception as exc:
                backfills.append({"status": "PASS145_BACKFILL_FAILED", "path_hash72": h72("pass145-path", str(path)), "error": f"{type(exc).__name__}:{exc}"})
    return {"layers": registered, "pass145": backfills}


def _install_semantic_hooks(index: HHSImmutableAgentSQLIndex) -> None:
    global _SEMANTIC_HOOKED
    if _SEMANTIC_HOOKED:
        return
    from hhs_backend.runtime.runtime_semantic_memory_engine import runtime_semantic_memory_engine

    original_ingest = runtime_semantic_memory_engine.ingest_memory
    original_link = runtime_semantic_memory_engine.link_memories

    @functools.wraps(original_ingest)
    def ingest_memory(*args: Any, **kwargs: Any) -> Any:
        try:
            result = original_ingest(*args, **kwargs)
            memory_type = kwargs.get("memory_type", args[0] if args else "semantic")
            text = kwargs.get("semantic_text", args[1] if len(args) > 1 else "")
            facts = {
                "status": "SEMANTIC_MEMORY_COMMITTED",
                "memory_id": getattr(result, "memory_id", None),
                "memory_type": memory_type,
                "memory_hash72": getattr(result, "hash72", None),
                "semantic_text_commitment": h72("semantic-text", text),
            }
            index.append_agent_event("SEMANTIC_MEMORY_INGEST", facts, input_payload={"memory_type": memory_type, "semantic_text": text}, output_payload=result)
            return result
        except Exception as exc:
            try:
                index.append_agent_event("AGENT_OPERATION_FAILED", {"status": type(exc).__name__, "operation": "semantic_memory_ingest"}, input_payload={"args": args, "kwargs": kwargs})
            except Exception:
                pass
            raise

    @functools.wraps(original_link)
    def link_memories(*args: Any, **kwargs: Any) -> Any:
        result = original_link(*args, **kwargs)
        facts = {
            "status": "SEMANTIC_MEMORY_LINK_COMMITTED",
            "link_id": getattr(result, "link_id", None),
            "source_memory_id": getattr(result, "source_memory_id", None),
            "target_memory_id": getattr(result, "target_memory_id", None),
            "relationship": getattr(result, "relationship", None),
        }
        index.append_agent_event("SEMANTIC_MEMORY_LINKED", facts, input_payload={"args": args, "kwargs": kwargs}, output_payload=result)
        return result

    runtime_semantic_memory_engine.ingest_memory = ingest_memory
    runtime_semantic_memory_engine.link_memories = link_memories
    _SEMANTIC_HOOKED = True


def _wrap(index: HHSImmutableAgentSQLIndex, obj: Any, name: str, event_type: str,
          facts_builder: Callable[[tuple[Any, ...], dict[str, Any], Any], Mapping[str, Any]]) -> None:
    original = getattr(obj, name)
    if getattr(original, "__hhs_immutable_agent_index_wrapped__", False):
        return

    @functools.wraps(original)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            result = original(*args, **kwargs)
            facts = dict(facts_builder(args, kwargs, result))
            index.append_agent_event(event_type, facts, input_payload={"args": args, "kwargs": kwargs}, output_payload=result)
            return result
        except Exception as exc:
            try:
                index.append_agent_event("AGENT_OPERATION_FAILED", {
                    "status": type(exc).__name__, "operation": name,
                    "error_commitment": h72("agent-error", str(exc)),
                }, input_payload={"args": args, "kwargs": kwargs})
            except Exception:
                pass
            raise

    wrapped.__hhs_immutable_agent_index_wrapped__ = True
    setattr(obj, name, wrapped)


def install_agent_index_hooks(cognition_runtime: Any, *, index: HHSImmutableAgentSQLIndex = immutable_agent_sql_index) -> dict[str, Any]:
    """Install idempotent writer-only bridges onto the live cognition runtime."""
    identity = id(cognition_runtime)
    if identity in _INSTALLED_IDS:
        return index.status()

    original_initialize = cognition_runtime.initialize
    original_status = cognition_runtime.status

    @functools.wraps(original_initialize)
    def initialize(*args: Any, **kwargs: Any) -> Any:
        index.initialize(boot_id=os.getenv("HHS_SERVER_BOOT_ID", "hhs-live-runtime"))
        _register_layers(index)
        _route_inventory(index)
        result = original_initialize(*args, **kwargs)
        index.append_agent_event("AGENT_INDEX_INITIALIZED", {
            "status": "IMMUTABLE_SQL_INDEX_ACTIVE",
            "api_geometry_hash72": h72("api-geometry-inventory", index.status().get("counts", {}).get("api_surfaces", 0)),
        }, output_payload=result)
        return result

    @functools.wraps(original_status)
    def status(*args: Any, **kwargs: Any) -> Any:
        result = original_status(*args, **kwargs)
        payload = dict(result) if isinstance(result, Mapping) else {"status": result}
        summary = index.status()
        payload["immutable_agent_sql_index"] = summary
        layers = dict(payload.get("layers") or {})
        layers["immutable_agent_sql_index"] = summary
        payload["layers"] = layers
        boundary = dict(payload.get("authority_boundary") or {})
        boundary.update({
            "protected_narrative_read": "DENIED_TO_GENERATING_API_TOOLS",
            "protected_narrative_delete": "DENIED_TO_GENERATING_API_TOOLS",
            "protected_narrative_update": "DENIED_TO_GENERATING_API_TOOLS",
            "narrative_evidence_class": "EXECUTION_DERIVED_DECISION_SUMMARY_NOT_PRIVATE_CHAIN_OF_THOUGHT",
        })
        payload["authority_boundary"] = boundary
        return payload

    cognition_runtime.initialize = initialize
    cognition_runtime.status = status

    _install_semantic_hooks(index)

    _wrap(index, cognition_runtime, "process_packet", "COMMITTED_RUNTIME_TICK", lambda a, k, r: {
        "status": r.get("status", "COGNITION_PACKET_PROCESSED") if isinstance(r, Mapping) else "COGNITION_PACKET_PROCESSED",
        "runtime_step": ((a[0].get("runtime") or {}).get("step") if a and isinstance(a[0], Mapping) else None),
        "state_hash72": ((a[0].get("runtime") or {}).get("state_hash72") if a and isinstance(a[0], Mapping) else None),
        "receipt_hash72": ((a[0].get("runtime") or {}).get("receipt_hash72") if a and isinstance(a[0], Mapping) else None),
        "replay_id": r.get("replay_id") if isinstance(r, Mapping) else None,
    })
    _wrap(index, cognition_runtime, "create_goal", "GOAL_REGISTERED", lambda a, k, r: {
        "status": "GOAL_REGISTERED", "goal_id": r.get("goal_id") if isinstance(r, Mapping) else None,
        "target_hash72": r.get("target_hash72") if isinstance(r, Mapping) else None,
        "objective_commitment": h72("goal-objective", a[0] if a else k.get("objective", "")),
    })
    _wrap(index, cognition_runtime, "create_task", "COGNITION_TASK_CREATED", lambda a, k, r: {
        "status": "COGNITION_TASK_CREATED", "task_id": r.get("task_id") if isinstance(r, Mapping) else None,
        "goal_id": r.get("goal_id") if isinstance(r, Mapping) else None,
        "objective_commitment": h72("task-objective", a[0] if a else k.get("objective", "")),
    })
    _wrap(index, cognition_runtime, "execute_task", "COGNITION_TASK_EXECUTED", lambda a, k, r: {
        "status": r.get("execution_state", r.get("status", "EXECUTED")) if isinstance(r, Mapping) else "EXECUTED",
        "task_id": a[0] if a else k.get("task_id"),
    })
    _wrap(index, cognition_runtime, "adapt_goal", "GOAL_ADAPTED", lambda a, k, r: {
        "status": "GOAL_ADAPTED", "goal_id": a[0] if a else k.get("goal_id"),
        "result_commitment": h72("goal-adaptation", r),
    })
    _wrap(index, cognition_runtime, "execute_research", "RESEARCH_EXECUTED", lambda a, k, r: {
        "status": r.get("state", r.get("status", "EXECUTED")) if isinstance(r, Mapping) else "EXECUTED",
        "objective_commitment": h72("research-objective", a[0] if a else k.get("objective", "")),
        "task_id": r.get("task_id") if isinstance(r, Mapping) else None,
    })
    _wrap(index, cognition_runtime, "execute_toolchain", "TOOLCHAIN_EXECUTED", lambda a, k, r: {
        "status": r.get("status", "EXECUTED") if isinstance(r, Mapping) else "EXECUTED",
        "toolchain_id": r.get("toolchain_id") if isinstance(r, Mapping) else None,
        "originating_task": a[0] if a else k.get("originating_task"),
    })
    _wrap(index, cognition_runtime, "generate_prediction", "PREDICTION_GENERATED", lambda a, k, r: {
        "status": "NON_AUTHORITATIVE_PREDICTION", "prediction_commitment": h72("prediction", r),
        "horizon": a[0] if a else k.get("horizon", 10),
    })
    _wrap(index, cognition_runtime, "create_consensus_proposal", "CONSENSUS_PROPOSAL_CREATED", lambda a, k, r: {
        "status": "CONSENSUS_PROPOSAL_CREATED", "proposal_id": r.get("proposal_id") if isinstance(r, Mapping) else None,
        "target_hash72": a[1] if len(a) > 1 else k.get("target_hash72"),
    })
    _wrap(index, cognition_runtime, "submit_consensus_vote", "CONSENSUS_VOTE_SUBMITTED", lambda a, k, r: {
        "status": "CONSENSUS_VOTE_SUBMITTED", "proposal_id": a[0] if a else k.get("proposal_id"),
        "node_id": a[1] if len(a) > 1 else k.get("node_id"),
        "approved": a[2] if len(a) > 2 else k.get("approved"),
    })
    _wrap(index, cognition_runtime, "collect_consensus", "CONSENSUS_COLLECTED", lambda a, k, r: {
        "status": r.get("status", r.get("consensus_state", "COLLECTED")) if isinstance(r, Mapping) else "COLLECTED",
        "proposal_id": a[0] if a else k.get("proposal_id"),
    })
    _wrap(index, cognition_runtime, "register_multinode_goal", "MULTINODE_GOAL_REGISTERED", lambda a, k, r: {
        "status": "MULTINODE_GOAL_REGISTERED", "goal_id": r.get("goal_id") if isinstance(r, Mapping) else None,
        "originating_node": a[0] if a else k.get("originating_node"),
        "target_hash72": a[2] if len(a) > 2 else k.get("target_hash72"),
    })
    _wrap(index, cognition_runtime, "synchronize_multinode_goals", "MULTINODE_GOALS_SYNCHRONIZED", lambda a, k, r: {
        "status": "MULTINODE_GOALS_SYNCHRONIZED", "result_commitment": h72("multinode-sync", r),
    })

    _INSTALLED_IDS.add(identity)
    return index.status()
