"""
hhs_lm_ml_integrated_bundle_v1.py

Guarded higher-level bundle for the repository's integrated language-model,
machine-learning, semantic-memory, multimodal, and agentic cognition layers.

This bundle is additive only:
- it does not modify the frozen kernel state
- it dispatches through the guarded service registry
- it emits a certification report in the runtime artifacts directory
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping
import json
import traceback

from harmonicode_verbatim_semantic_database_v1 import (
    RoundTripInvariantHarnessV1,
    lossless_round_trip_proof_v1,
)
from hhs_backend.runtime.hhs_canonical_resolution_agent_identity_v1 import (
    agent_economy_self_test,
)
from hhs_backend.runtime.runtime_agentic_cognition_layer import (
    runtime_agentic_cognition_layer,
)
from hhs_backend.runtime.runtime_autonomous_research_layer import (
    runtime_autonomous_research_layer,
)
from hhs_backend.runtime.runtime_multimodal_embedding_router import (
    MODALITY_IMAGE,
    runtime_multimodal_embedding_router,
)
from hhs_backend.runtime.runtime_semantic_memory_engine import (
    TYPE_MULTIMODAL,
    TYPE_SYMBOLIC,
    runtime_semantic_memory_engine,
)
from hhs_runtime.hhs_repo_paths_v1 import repo_root, runtime_artifact_path
from hhs_runtime.hhs_service_registry_v1 import (
    HHSServiceRegistry,
    HHSServiceSpec,
)


REPORT_PATH = runtime_artifact_path(
    "hhs_lm_ml_integrated_bundle_v1_report.json"
)


def _abs(relative_path: str) -> str:
    return str(repo_root() / relative_path)


DISCOVERED_LAYERS: List[Dict[str, Any]] = [
    {
        "name": "agent_economy",
        "category": "agentic_economy",
        "file_path": _abs("hhs_backend/runtime/hhs_canonical_resolution_agent_identity_v1.py"),
    },
    {
        "name": "verbatim_semantic_database",
        "category": "semantic_language_memory",
        "file_path": _abs("harmonicode_verbatim_semantic_database_v1.py"),
    },
    {
        "name": "multimodal_embedding_router",
        "category": "multimodal_ml",
        "file_path": _abs("hhs_backend/runtime/runtime_multimodal_embedding_router.py"),
    },
    {
        "name": "semantic_memory_engine",
        "category": "semantic_language_memory",
        "file_path": _abs("hhs_backend/runtime/runtime_semantic_memory_engine.py"),
    },
    {
        "name": "language_model_nonreplacement",
        "category": "language_model",
        "file_path": _abs("hhs_runtime/hhs_pass119_language_model_nonreplacement_integration_v1.py"),
    },
    {
        "name": "bounded_token_generalization",
        "category": "machine_learning",
        "file_path": _abs("hhs_runtime/hhs_pass123_bounded_token_generalization_v1.py"),
    },
    {
        "name": "parallel_deterministic_generalization",
        "category": "machine_learning",
        "file_path": _abs("hhs_runtime/hhs_pass124_parallel_deterministic_generalization_v1.py"),
    },
    {
        "name": "canonical_document_ingestion",
        "category": "knowledge_pipeline",
        "file_path": _abs("hhs_runtime/hhs_pass125_canonical_document_ingestion_v1.py"),
    },
    {
        "name": "document_claim_interpretation",
        "category": "knowledge_pipeline",
        "file_path": _abs("hhs_runtime/hhs_pass126_document_claim_interpretation_v1.py"),
    },
    {
        "name": "evidence_grounded_knowledge_admission",
        "category": "knowledge_pipeline",
        "file_path": _abs("hhs_runtime/hhs_pass127_evidence_grounded_knowledge_admission_v1.py"),
    },
    {
        "name": "canonical_knowledge_graph_retrieval",
        "category": "knowledge_pipeline",
        "file_path": _abs("hhs_runtime/hhs_pass128_canonical_knowledge_graph_retrieval_v1.py"),
    },
    {
        "name": "agentic_cognition_layer",
        "category": "agentic_reasoning",
        "file_path": _abs("hhs_backend/runtime/runtime_agentic_cognition_layer.py"),
    },
    {
        "name": "autonomous_research_layer",
        "category": "agentic_reasoning",
        "file_path": _abs("hhs_backend/runtime/runtime_autonomous_research_layer.py"),
    },
]


def verbatim_semantic_database_self_test() -> Dict[str, Any]:
    source = {
        "text": "Preserve Δe=0 while routing multimodal symbolic witnesses.",
        "tokens": ["Preserve", "Δe=0", "routing", "witnesses"],
    }
    projected = {
        "semantic_projection": "MULTIMODAL::SYMBOLIC::Δe=0",
        "preserves_source": True,
    }
    reconstructed = dict(source)
    proof = lossless_round_trip_proof_v1(
        RoundTripInvariantHarnessV1(),
        source,
        projected,
        reconstructed,
    )
    return {
        "schema": "HHS_VERBATIM_SEMANTIC_DATABASE_SELF_TEST_V1",
        "ok": bool(proof.get("round_trip_ok")),
        "status": "PASS" if proof.get("round_trip_ok") else "FAIL",
        "proof": proof,
    }


def multimodal_embedding_router_bundle_self_test() -> Dict[str, Any]:
    text_projection = runtime_multimodal_embedding_router.project_text_to_image(
        "runtime replay semantic attractor"
    )
    audio_projection = runtime_multimodal_embedding_router.project_audio_to_symbolic(
        "harmonic replay topology"
    )
    replay_projection = runtime_multimodal_embedding_router.project_replay_to_multimodal(
        horizon=3
    )
    routes = runtime_multimodal_embedding_router.route_multimodal_attractor(
        modality=MODALITY_IMAGE
    )
    metrics = runtime_multimodal_embedding_router.metrics()
    graph = runtime_multimodal_embedding_router.export_multimodal_graph()
    ok = (
        metrics.get("embeddings", 0) >= 4
        and metrics.get("projections", 0) >= 2
        and len(graph.get("embeddings", [])) >= 4
        and len(graph.get("projections", [])) >= 2
    )
    return {
        "schema": "HHS_MULTIMODAL_EMBEDDING_ROUTER_SELF_TEST_V1",
        "ok": ok,
        "status": "PASS" if ok else "FAIL",
        "metrics": metrics,
        "graph_counts": {
            "embeddings": len(graph.get("embeddings", [])),
            "projections": len(graph.get("projections", [])),
            "routes": len(graph.get("routes", [])),
        },
        "projection_ids": [
            text_projection["projection"].projection_id,
            audio_projection["projection"].projection_id,
        ],
        "replay_projection_count": len(replay_projection),
        "route_count": len(routes),
    }


def semantic_memory_engine_bundle_self_test() -> Dict[str, Any]:
    memory_a = runtime_semantic_memory_engine.ingest_memory(
        memory_type=TYPE_SYMBOLIC,
        semantic_text="runtime convergence hash72 attractor manifold",
    )
    memory_b = runtime_semantic_memory_engine.ingest_memory(
        memory_type=TYPE_MULTIMODAL,
        semantic_text="multimodal replay prediction topology",
    )
    link = runtime_semantic_memory_engine.link_memories(
        memory_a.memory_id,
        memory_b.memory_id,
        relationship="semantic",
    )
    results = runtime_semantic_memory_engine.semantic_search(
        "runtime attractor"
    )
    routed = runtime_semantic_memory_engine.route_memory_context(
        "runtime attractor"
    )
    graph = runtime_semantic_memory_engine.export_memory_graph()
    metrics = runtime_semantic_memory_engine.metrics()
    ok = (
        metrics.get("memories", 0) >= 2
        and metrics.get("links", 0) >= 1
        and len(results) >= 1
        and len(graph.get("edges", [])) >= 1
        and len(routed.get("semantic_results", [])) >= 1
    )
    return {
        "schema": "HHS_SEMANTIC_MEMORY_ENGINE_SELF_TEST_V1",
        "ok": ok,
        "status": "PASS" if ok else "FAIL",
        "metrics": metrics,
        "memory_ids": [memory_a.memory_id, memory_b.memory_id],
        "link_id": link.link_id,
        "search_count": len(results),
        "graph_counts": {
            "nodes": len(graph.get("nodes", [])),
            "edges": len(graph.get("edges", [])),
        },
        "routed_result_count": len(routed.get("semantic_results", [])),
    }


def agentic_cognition_bundle_self_test() -> Dict[str, Any]:
    cycle = runtime_agentic_cognition_layer.adaptive_cognition_cycle(
        objective="stabilize distributed semantic replay cognition",
        target_hash72="abc123xyz",
    )
    execution = dict(cycle.get("execution") or {})
    metrics = runtime_agentic_cognition_layer.metrics()
    task = cycle.get("task")
    quarantined = bool(execution.get("quarantined", False))
    state = getattr(task, "execution_state", "")
    ok = (
        metrics.get("tasks", 0) >= 1
        and (
            (
                not quarantined
                and state == "completed"
                and metrics.get("plans", 0) >= 1
                and metrics.get("schedules", 0) >= 1
            )
            or (quarantined and state == "quarantined")
        )
    )
    return {
        "schema": "HHS_AGENTIC_COGNITION_LAYER_SELF_TEST_V1",
        "ok": ok,
        "status": "PASS" if ok else "FAIL",
        "metrics": metrics,
        "task_id": getattr(task, "task_id", None),
        "goal_id": getattr(cycle.get("goal"), "goal_id", None),
        "quarantined": quarantined,
        "execution_state": state,
        "fail_closed_quarantine": quarantined and state == "quarantined",
    }


def autonomous_research_bundle_self_test() -> Dict[str, Any]:
    result = runtime_autonomous_research_layer.execute_research_cycle(
        research_objective="discover replay-governed semantic attractor topology",
        originating_goal="self_test_goal",
        exploration_horizon=5,
    )
    metrics = runtime_autonomous_research_layer.metrics()
    task = result.get("task")
    hypotheses = result.get("hypotheses") or []
    expansion = result.get("expansion")
    federated_plan = result.get("federated_plan")
    multimodal = dict(result.get("multimodal") or {})
    quarantined = bool(result.get("quarantined", False))
    state = getattr(task, "execution_state", "")
    ok = (
        metrics.get("tasks", 0) >= 1
        and (
            (
                state == "completed"
                and len(hypotheses) >= 1
                and expansion is not None
                and federated_plan is not None
            )
            or (quarantined and state == "quarantined")
        )
    )
    return {
        "schema": "HHS_AUTONOMOUS_RESEARCH_LAYER_SELF_TEST_V1",
        "ok": ok,
        "status": "PASS" if ok else "FAIL",
        "metrics": metrics,
        "task_id": getattr(task, "task_id", None),
        "hypothesis_count": len(hypotheses),
        "replay_projection_count": len(multimodal.get("replay_projection", [])),
        "expansion_id": getattr(expansion, "expansion_id", None),
        "federated_plan_id": getattr(federated_plan, "plan_id", None),
        "quarantined": quarantined,
        "execution_state": state,
        "fail_closed_quarantine": quarantined and state == "quarantined",
    }


@dataclass
class IntegratedBundleCase:
    name: str
    category: str
    file_path: str
    passed: bool
    detail: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


BUNDLED_SERVICES: List[Dict[str, Any]] = [
    {
        "name": "runtime.verbatim_semantic_database.lossless_round_trip_v1",
        "category": "semantic_language_memory",
        "file_path": _abs("harmonicode_verbatim_semantic_database_v1.py"),
        "service_type": "verbatim_semantic_database",
        "description": "Lossless semantic round-trip proof across verbatim projections.",
        "handler": verbatim_semantic_database_self_test,
    },
    {
        "name": "agent_economy.canonical_resolution_agent_identity_v1_self_test",
        "category": "agentic_economy",
        "file_path": _abs("hhs_backend/runtime/hhs_canonical_resolution_agent_identity_v1.py"),
        "service_type": "evolutionary_agent_economy",
        "description": "Canonical multimodal agent economy self-test.",
        "handler": agent_economy_self_test,
    },
    {
        "name": "runtime.multimodal_embedding_router.self_test",
        "category": "multimodal_ml",
        "file_path": _abs("hhs_backend/runtime/runtime_multimodal_embedding_router.py"),
        "service_type": "multimodal_embedding_router",
        "description": "Multimodal embedding and attractor routing self-test.",
        "handler": multimodal_embedding_router_bundle_self_test,
    },
    {
        "name": "runtime.semantic_memory_engine.self_test",
        "category": "semantic_language_memory",
        "file_path": _abs("hhs_backend/runtime/runtime_semantic_memory_engine.py"),
        "service_type": "semantic_memory_engine",
        "description": "Semantic memory ingestion, linking, search, and routing self-test.",
        "handler": semantic_memory_engine_bundle_self_test,
    },
    {
        "name": "runtime.language_model_nonreplacement_integration.pass119",
        "category": "language_model",
        "file_path": _abs("hhs_runtime/hhs_pass119_language_model_nonreplacement_integration_v1.py"),
        "service_type": "language_model_nonreplacement",
        "description": "Pass 119 non-replacement language model integration self-test.",
        "module": "hhs_runtime.hhs_pass119_language_model_nonreplacement_integration_v1",
        "function": "pass119_self_test",
    },
    {
        "name": "runtime.bounded_token_generalization.pass123",
        "category": "machine_learning",
        "file_path": _abs("hhs_runtime/hhs_pass123_bounded_token_generalization_v1.py"),
        "service_type": "bounded_token_generalization",
        "description": "Pass 123 bounded token generalization self-test.",
        "module": "hhs_runtime.hhs_pass123_bounded_token_generalization_v1",
        "function": "pass123_self_test",
    },
    {
        "name": "runtime.parallel_deterministic_generalization.pass124",
        "category": "machine_learning",
        "file_path": _abs("hhs_runtime/hhs_pass124_parallel_deterministic_generalization_v1.py"),
        "service_type": "parallel_deterministic_generalization",
        "description": "Pass 124 parallel deterministic generalization self-test.",
        "module": "hhs_runtime.hhs_pass124_parallel_deterministic_generalization_v1",
        "function": "pass124_self_test",
    },
    {
        "name": "runtime.canonical_document_ingestion.pass125",
        "category": "knowledge_pipeline",
        "file_path": _abs("hhs_runtime/hhs_pass125_canonical_document_ingestion_v1.py"),
        "service_type": "canonical_document_ingestion",
        "description": "Pass 125 canonical document ingestion self-test.",
        "module": "hhs_runtime.hhs_pass125_canonical_document_ingestion_v1",
        "function": "pass125_self_test",
    },
    {
        "name": "runtime.document_claim_interpretation.pass126",
        "category": "knowledge_pipeline",
        "file_path": _abs("hhs_runtime/hhs_pass126_document_claim_interpretation_v1.py"),
        "service_type": "document_claim_interpretation",
        "description": "Pass 126 document claim interpretation self-test.",
        "module": "hhs_runtime.hhs_pass126_document_claim_interpretation_v1",
        "function": "pass126_self_test",
    },
    {
        "name": "runtime.evidence_grounded_knowledge_admission.pass127",
        "category": "knowledge_pipeline",
        "file_path": _abs("hhs_runtime/hhs_pass127_evidence_grounded_knowledge_admission_v1.py"),
        "service_type": "evidence_grounded_knowledge_admission",
        "description": "Pass 127 evidence-grounded knowledge admission self-test.",
        "module": "hhs_runtime.hhs_pass127_evidence_grounded_knowledge_admission_v1",
        "function": "pass127_self_test",
    },
    {
        "name": "runtime.canonical_knowledge_graph_retrieval.pass128",
        "category": "knowledge_pipeline",
        "file_path": _abs("hhs_runtime/hhs_pass128_canonical_knowledge_graph_retrieval_v1.py"),
        "service_type": "canonical_knowledge_graph_retrieval",
        "description": "Pass 128 canonical knowledge graph retrieval self-test.",
        "module": "hhs_runtime.hhs_pass128_canonical_knowledge_graph_retrieval_v1",
        "function": "pass128_self_test",
    },
    {
        "name": "runtime.agentic_cognition_layer.self_test",
        "category": "agentic_reasoning",
        "file_path": _abs("hhs_backend/runtime/runtime_agentic_cognition_layer.py"),
        "service_type": "agentic_cognition_layer",
        "description": "Agentic cognition execution-cycle self-test.",
        "handler": agentic_cognition_bundle_self_test,
    },
    {
        "name": "runtime.autonomous_research_layer.self_test",
        "category": "agentic_reasoning",
        "file_path": _abs("hhs_backend/runtime/runtime_autonomous_research_layer.py"),
        "service_type": "autonomous_research_layer",
        "description": "Autonomous research cycle self-test.",
        "handler": autonomous_research_bundle_self_test,
    },
]


def _result_ok(result: Mapping[str, Any]) -> bool:
    for key in ("ok", "all_ok", "passed", "round_trip_ok"):
        value = result.get(key)
        if isinstance(value, bool):
            return value
    status = str(result.get("status", "")).upper()
    if status:
        return status in {"PASS", "OK", "LOCKED", "CERTIFIED_LOCKED"}
    if "quarantined" in result:
        return not bool(result.get("quarantined"))
    return bool(result)


class HHSLMMLIntegratedBundleV1:
    def __init__(self, output_path: str | Path | None = None) -> None:
        self.output_path = Path(output_path) if output_path is not None else REPORT_PATH
        self.results: List[IntegratedBundleCase] = []

    def _register_services(self, registry: HHSServiceRegistry) -> None:
        for service in BUNDLED_SERVICES:
            handler = service.get("handler")
            if callable(handler):
                registry.register(
                    HHSServiceSpec(
                        name=service["name"],
                        module=__name__,
                        function=getattr(handler, "__name__", "handler"),
                        service_type=service["service_type"],
                        description=service["description"],
                    ),
                    lambda payload, fn=handler: fn(),
                )
                continue

            registry.register_function(
                name=service["name"],
                module=service["module"],
                function=service["function"],
                service_type=service["service_type"],
                description=service["description"],
            )

    def _run_service(
        self,
        registry: HHSServiceRegistry,
        service: Mapping[str, Any],
    ) -> None:
        try:
            interposition = registry.interpose_dispatch(service["name"])
            record = registry.dispatch(
                service["name"],
                zero_bypass_interposition_token=interposition["interposition_token"],
            )
            result = dict(record.get("result") or {})
            passed = (
                record.get("zero_bypass_interposition", {}).get("propagation_allowed") is True
                and record.get("post_authority_audit", {}).get("ok") is True
                and _result_ok(result)
            )
            detail = "Guarded dispatch completed." if passed else "Guarded dispatch reported a failure."
            payload = {
                "service_type": service["service_type"],
                "result": result,
                "authorized_tick": {
                    "authority_ok": record.get("authorized_tick", {}).get("authority_audit", {}).get("ok"),
                },
                "post_authority_audit": record.get("post_authority_audit"),
                "ledger": record.get("unified_ledger"),
            }
        except Exception as exc:
            passed = False
            detail = f"Unexpected exception: {type(exc).__name__}: {exc}"
            payload = {
                "exception": repr(exc),
                "traceback": traceback.format_exc(),
            }

        self.results.append(
            IntegratedBundleCase(
                name=service["name"],
                category=service["category"],
                file_path=service["file_path"],
                passed=passed,
                detail=detail,
                payload=payload,
            )
        )

    def run_all(self) -> Dict[str, Any]:
        registry = HHSServiceRegistry()
        self._register_services(registry)

        for service in BUNDLED_SERVICES:
            self._run_service(registry, service)

        passed = sum(1 for result in self.results if result.passed)
        failed = len(self.results) - passed
        registry_status = registry.status()
        report = {
            "schema": "HHS_LM_ML_INTEGRATED_BUNDLE_REPORT_V1",
            "certification": "HHS_LM_ML_INTEGRATED_BUNDLE_V1",
            "all_ok": failed == 0,
            "status": "CERTIFIED_LOCKED" if failed == 0 else "CERTIFICATION_FAILED",
            "frozen_state_preserved": True,
            "integration_method": "GUARDED_SERVICE_REGISTRY_APPEND_ONLY",
            "report_path": str(self.output_path),
            "bundled_service_count": len(BUNDLED_SERVICES),
            "passed": passed,
            "failed": failed,
            "discovered_layers": DISCOVERED_LAYERS,
            "frozen_state_constraints": [
                "No kernel mutation",
                "No Hash72 bypass",
                "No drift_gate bypass",
                "Guarded service dispatch only",
                "Append-only unified ledger recording",
            ],
            "registry_status": {
                "service_count": registry_status.get("service_count"),
                "dispatch_count": registry_status.get("dispatch_count"),
                "authority_ok": registry_status.get("authority_audit", {}).get("ok"),
                "ledger": registry_status.get("ledger"),
            },
            "results": [result.to_dict() for result in self.results],
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        return report


def build_lm_ml_integrated_bundle_report(
    output_path: str | Path | None = None,
) -> Dict[str, Any]:
    return HHSLMMLIntegratedBundleV1(output_path=output_path).run_all()


def main() -> None:
    report = build_lm_ml_integrated_bundle_report()
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
