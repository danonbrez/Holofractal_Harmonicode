# ============================================================================
# hhs_backend/server.py
# HARMONICODE / HHS
# CANONICAL BACKEND SERVER BOOTSTRAP
#
# PURPOSE
# -------
# Authoritative runtime server process for:
#
#   - FastAPI lifecycle management
#   - router composition
#   - runtime initialization
#   - graph-memory initialization
#   - websocket orchestration
#   - replay infrastructure
#   - middleware registration
#   - deterministic startup ordering
#
# ALL backend execution MUST originate here.
#
# ============================================================================

from __future__ import annotations

import asyncio
import logging
import time
import uuid

from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uvicorn

# ============================================================================
# ROUTES
# ============================================================================

from hhs_backend.api.pass135_audit_routes import router as pass135_audit_router
from hhs_backend.api.pass152_elastic_closure_routes import router as pass152_elastic_closure_router

from hhs_backend.api.runtime_routes import (
    router as runtime_router,

    runtime_controller,

    runtime_emulator,

    runtime_graph
)

from hhs_backend.runtime.runtime_ws import (
    runtime_ws_router,
    runtime_ws_health,
)

from hhs_backend.runtime.live_fastapi_workflow_v1 import (
    LiveFastAPIRuntimeWorkflow,
)
from hhs_backend.runtime.gui_projection_contract_v1 import (
    list_gui_channel_bindings,
    live_gui_projection_contract_self_test,
)

from hhs_backend.runtime.live_gui_command_authority_loop_v1 import (
    LiveGUICommandAuthorityLoop,
)
from hhs_backend.runtime.live_gui_command_contract_v1 import (
    COMMAND_SCHEMA as GUI_COMMAND_SCHEMA,
)
from hhs_backend.runtime.live_gui_command_router_v1 import (
    list_live_gui_command_routes,
)
from hhs_backend.runtime.live_authorized_mutation_contract_v1 import (
    AUTHORIZED_MUTATION_OPERATIONS,
    live_authorized_mutation_contract_self_test,
)
from hhs_backend.runtime.hhs_workspace_authority_loop_v1 import (
    WorkspaceAuthorityLoop,
    workspace_authority_loop_self_test,
)
from hhs_backend.runtime.hhs_workspace_command_router_v1 import (
    list_workspace_command_routes,
)
from hhs_backend.runtime.runtime_workspace_project_v1 import (
    create_workspace_project,
    open_workspace_project,
    fork_workspace_project,
)
from hhs_backend.runtime.hhs_workspace_persistence_v1 import (
    save_workspace_project,
)
from hhs_backend.runtime.hhs_modality_adapter_capability_map_v1 import (
    build_adapter_capability_map,
    modality_adapter_capability_map_self_test,
)
from hhs_backend.runtime.hhs_universal_artifact_pipeline_v1 import (
    run_universal_artifact_pipeline,
    universal_artifact_pipeline_self_test,
)

from hhs_backend.runtime.hhs_runtime_canonical_observer_v1 import (
    canonical_observer_status,
    runtime_canonical_observer_self_test,
)
from hhs_backend.runtime.hhs_capability_contract_v1 import (
    list_capability_contracts,
    capability_contract_self_test,
)
from hhs_backend.runtime.hhs_capability_provider_registry_v1 import (
    build_default_provider_registry,
    capability_provider_registry_self_test,
)
from hhs_backend.runtime.hhs_capability_resolution_v1 import (
    resolve_capability,
    capability_resolution_self_test,
)
from hhs_backend.runtime.hhs_provider_execution_proposal_v1 import (
    build_provider_execution_proposal,
    provider_execution_proposal_self_test,
)
from hhs_backend.runtime.hhs_capability_policy_gate_v1 import (
    evaluate_capability_policy_gate,
    capability_policy_gate_self_test,
)
from hhs_backend.runtime.hhs_provider_invocation_receipt_v1 import (
    invoke_provider_with_receipt,
    provider_invocation_receipt_self_test,
)
from hhs_backend.runtime.hhs_provider_result_ingress_v1 import (
    ingress_provider_result,
    provider_result_ingress_self_test,
)
from hhs_backend.runtime.hhs_capability_fallback_plan_v1 import (
    build_capability_fallback_plan,
    capability_fallback_plan_self_test,
)
from hhs_backend.runtime.hhs_universal_capability_fabric_v1 import (
    capability_fabric_status,
    run_universal_capability_fabric,
    universal_capability_fabric_self_test,
)
from hhs_backend.runtime.hhs_deep_document_perception_pipeline_v1 import (
    deep_document_perception_status,
    run_deep_document_perception,
    deep_document_perception_pipeline_self_test,
)
from hhs_backend.runtime.hhs_document_provider_contract_v1 import (
    document_provider_contract_self_test,
)
from hhs_backend.runtime.hhs_document_structure_fusion_v1 import (
    fuse_document_observations,
    validate_document_fusion,
    document_structure_fusion_self_test,
)

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "[HHS] "
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    )
)

logger = logging.getLogger("HHS")

# ============================================================================
# GLOBAL SERVER STATE
# ============================================================================

SERVER_BOOT_ID = str(uuid.uuid4())

SERVER_START_TIME = time.time()

SERVER_STATE: Dict[str, Any] = {

    "boot_id":
        SERVER_BOOT_ID,

    "started_at":
        SERVER_START_TIME,

    "runtime_initialized":
        False,

    "graph_initialized":
        False,

    "websocket_ready":
        False,

    "live_workflow_ready":
        False,
}

LIVE_WORKFLOW = LiveFastAPIRuntimeWorkflow(
    runtime_emulator=runtime_emulator,
    runtime_graph=runtime_graph,
    interval_seconds=1.0,
    auto_start=True,
)

GUI_COMMAND_LOOP = LiveGUICommandAuthorityLoop(
    live_workflow=LIVE_WORKFLOW,
)

WORKSPACE_AUTHORITY_LOOP = WorkspaceAuthorityLoop()

# ============================================================================
# STARTUP
# ============================================================================

async def initialize_runtime():

    logger.info(
        "Initializing guarded deterministic runtime emulator..."
    )

    boot = runtime_emulator.boot()

    if not boot.get("authority_audit", {}).get("ok"):

        raise RuntimeError(
            "HHS runtime authority audit failed during boot"
        )

    SERVER_STATE["runtime_initialized"] = True
    SERVER_STATE["emulator_boot_id"] = boot.get("boot_id")
    SERVER_STATE["authority_audit"] = boot.get("authority_audit")

    logger.info(
        "Guarded runtime emulator initialized"
    )

# ----------------------------------------------------------------------------

async def initialize_graph():

    logger.info(
        "Initializing graph substrate..."
    )

    runtime_graph.export_graph_summary()

    SERVER_STATE["graph_initialized"] = True

    logger.info(
        "Graph substrate initialized"
    )

# ----------------------------------------------------------------------------

async def initialize_websocket_layer():

    logger.info(
        "Initializing websocket layer..."
    )

    await LIVE_WORKFLOW.start()

    SERVER_STATE["websocket_ready"] = True
    SERVER_STATE["live_workflow_ready"] = True
    SERVER_STATE["live_workflow"] = LIVE_WORKFLOW.status()

    logger.info(
        "Websocket layer initialized with live FastAPI kernel workflow"
    )

# ----------------------------------------------------------------------------

async def startup_sequence():

    logger.info(
        "Starting HHS backend..."
    )

    await initialize_runtime()

    await initialize_graph()

    await initialize_websocket_layer()

    logger.info(
        "HHS backend startup complete"
    )

# ============================================================================
# SHUTDOWN
# ============================================================================

async def shutdown_sequence():

    logger.info(
        "Beginning shutdown sequence..."
    )

    await LIVE_WORKFLOW.stop()

    runtime_controller.halt()

    logger.info(
        "Runtime halted"
    )

# ============================================================================
# FASTAPI LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    await startup_sequence()

    yield

    await shutdown_sequence()

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(

    title="HARMONICODE Runtime Server",

    description=(
        "Deterministic runtime operating environment "
        "for HHS / HARMONICODE"
    ),

    version="0.1.0",

    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(runtime_router)
app.include_router(runtime_ws_router)
app.include_router(pass135_audit_router)
app.include_router(pass152_elastic_closure_router)

# ============================================================================
# HEALTH ROUTES
# ============================================================================

@app.get("/")
async def root():

    return {

        "system":
            "HARMONICODE",

        "status":
            "online",

        "boot_id":
            SERVER_BOOT_ID
    }

# ----------------------------------------------------------------------------

@app.get("/health")
async def health():

    runtime_state = (
        runtime_controller.latest_runtime_state()
    )

    graph_summary = (
        runtime_graph.export_graph_summary()
    )

    return {

        "status":
            "healthy",

        "boot_id":
            SERVER_BOOT_ID,

        "uptime":
            time.time() - SERVER_START_TIME,

        "runtime":
            runtime_state,

        "graph":
            graph_summary,

        "server_state":
            SERVER_STATE,

        "emulator":
            runtime_emulator.status(),

        "websocket":
            runtime_ws_health(),

        "live_workflow":
            LIVE_WORKFLOW.status(),
    }

# ----------------------------------------------------------------------------

@app.get("/health/runtime")
async def runtime_health():

    return runtime_controller.latest_runtime_state()

# ----------------------------------------------------------------------------

@app.get("/health/graph")
async def graph_health():

    return runtime_graph.export_graph_summary()

# ----------------------------------------------------------------------------

@app.get("/api/runtime/live/status")
async def live_runtime_status():

    return LIVE_WORKFLOW.status()

# ----------------------------------------------------------------------------

@app.post("/api/runtime/live/tick")
async def live_runtime_tick():

    return await LIVE_WORKFLOW.tick_once({
        "source": "api.runtime.live.tick"
    })

# ----------------------------------------------------------------------------

@app.get("/api/runtime/gui/projection/status")
async def live_gui_projection_status():

    return {
        "schema": "HHS_LIVE_GUI_PROJECTION_STATUS_ROUTE_V1",
        "bindings": list_gui_channel_bindings(),
        "contract_self_test": live_gui_projection_contract_self_test(),
        "websocket": runtime_ws_health(),
        "live_workflow": LIVE_WORKFLOW.status(),
    }

# ----------------------------------------------------------------------------

@app.post("/api/runtime/gui/command")
async def live_gui_command(command: Dict[str, Any]):

    return await GUI_COMMAND_LOOP.submit(command)

# ----------------------------------------------------------------------------

@app.get("/api/runtime/gui/command/status/{command_id:path}")
async def live_gui_command_status(command_id: str):

    return GUI_COMMAND_LOOP.status(command_id)

# ----------------------------------------------------------------------------

@app.get("/api/runtime/gui/command/history")
async def live_gui_command_history():

    history = GUI_COMMAND_LOOP.history_summary()
    history["routes"] = list_live_gui_command_routes()
    history["command_schema"] = GUI_COMMAND_SCHEMA
    return history

@app.get("/api/runtime/gui/mutation/allowlist")
async def live_gui_mutation_allowlist():

    return {
        "schema": "HHS_LIVE_GUI_MUTATION_ALLOWLIST_STATUS_V1",
        "version": "PASS_048_AUTHORIZED_LIVE_MUTATION_EXECUTION_V1",
        "allowlist": AUTHORIZED_MUTATION_OPERATIONS,
        "contract_self_test": live_authorized_mutation_contract_self_test(),
        "gui_role": "REQUEST_ONLY_NO_DIRECT_RUNTIME_TRUTH",
        "mutation_rule": "EVERY_MUTATION_REQUIRES_PRE_TRANSFORM_POST_RECEIPT_AND_WEBSOCKET_FEEDBACK",
    }

# ----------------------------------------------------------------------------


@app.get("/api/runtime/workspace/status")
async def workspace_status():

    status = WORKSPACE_AUTHORITY_LOOP.status()
    status["command_routes"] = list_workspace_command_routes()
    status["self_test_projection"] = workspace_authority_loop_self_test()
    return status

# ----------------------------------------------------------------------------

@app.post("/api/runtime/workspace/command")
async def workspace_command(command: Dict[str, Any]):

    operation = str(command.get("operation") or command.get("requested_operation") or "")
    payload = dict(command.get("payload") or command)
    return WORKSPACE_AUTHORITY_LOOP.submit(operation, payload)

# ----------------------------------------------------------------------------

@app.post("/api/runtime/workspace/project")
async def workspace_create_project(payload: Dict[str, Any]):

    project = create_workspace_project(str(payload.get("name") or "HHS Workspace"))
    WORKSPACE_AUTHORITY_LOOP.projects[project["project_id"]] = project
    return {"schema": "HHS_WORKSPACE_PROJECT_ROUTE_RESULT_V1", "ok": True, "project": project}

# ----------------------------------------------------------------------------

@app.get("/api/runtime/workspace/project/{project_id:path}")
async def workspace_get_project(project_id: str):

    project = WORKSPACE_AUTHORITY_LOOP.projects.get(project_id)
    if not project:
        return {"schema": "HHS_WORKSPACE_PROJECT_ROUTE_RESULT_V1", "ok": False, "status": "REJECT_WORKSPACE_OBJECT_UNKNOWN", "project_id": project_id}
    return {"schema": "HHS_WORKSPACE_PROJECT_ROUTE_RESULT_V1", "ok": True, "project": project}

# ----------------------------------------------------------------------------

@app.post("/api/runtime/workspace/project/{project_id:path}/open")
async def workspace_open_project(project_id: str):

    project = WORKSPACE_AUTHORITY_LOOP.projects.get(project_id)
    if not project:
        return {"schema": "HHS_WORKSPACE_PROJECT_OPEN_ROUTE_RESULT_V1", "ok": False, "status": "REJECT_WORKSPACE_OBJECT_UNKNOWN", "project_id": project_id}
    return open_workspace_project(project)

# ----------------------------------------------------------------------------

@app.post("/api/runtime/workspace/project/{project_id:path}/save")
async def workspace_save_project(project_id: str):

    project = WORKSPACE_AUTHORITY_LOOP.projects.get(project_id)
    if not project:
        return {"schema": "HHS_WORKSPACE_PROJECT_SAVE_ROUTE_RESULT_V1", "ok": False, "status": "REJECT_WORKSPACE_OBJECT_UNKNOWN", "project_id": project_id}
    return save_workspace_project(project)

# ----------------------------------------------------------------------------

@app.post("/api/runtime/workspace/project/{project_id:path}/fork")
async def workspace_fork_project(project_id: str, payload: Dict[str, Any] | None = None):

    project = WORKSPACE_AUTHORITY_LOOP.projects.get(project_id)
    if not project:
        return {"schema": "HHS_WORKSPACE_PROJECT_FORK_ROUTE_RESULT_V1", "ok": False, "status": "REJECT_WORKSPACE_OBJECT_UNKNOWN", "project_id": project_id}
    result = fork_workspace_project(project, (payload or {}).get("name"))
    if result.get("ok"):
        WORKSPACE_AUTHORITY_LOOP.projects[result["project"]["project_id"]] = result["project"]
    return result

# ----------------------------------------------------------------------------

@app.get("/api/runtime/workspace/commands/history")
async def workspace_commands_history():

    return {
        "schema": "HHS_WORKSPACE_COMMAND_HISTORY_ROUTE_V1",
        "ok": True,
        "history": WORKSPACE_AUTHORITY_LOOP.command_history[-64:],
        "bounded_history": True,
    }

# ----------------------------------------------------------------------------

@app.get("/api/runtime/workspace/modality/adapters")
async def workspace_modality_adapters():

    return {
        "schema": "HHS_WORKSPACE_MODALITY_ADAPTERS_ROUTE_V1",
        "ok": True,
        "capability_map": build_adapter_capability_map(),
        "self_test_projection": modality_adapter_capability_map_self_test(),
        "doctrine": "NO_MODALITY_OWNS_A_PRIVATE_TRUTH_PIPELINE",
    }

# ----------------------------------------------------------------------------

@app.post("/api/runtime/workspace/modality/pipeline")
async def workspace_modality_pipeline(payload: Dict[str, Any]):

    return run_universal_artifact_pipeline(
        project_id=str(payload.get("project_id") or "project:default"),
        source_name=str(payload.get("source_name") or "source.bin"),
        payload=payload.get("source_payload") if "source_payload" in payload else payload.get("payload", ""),
        source_modality=str(payload.get("source_modality") or payload.get("declared_modality") or "TEXT"),
        projection_type=str(payload.get("projection_type") or "TEXT_PROJECTION"),
        target_modality=str(payload.get("target_modality") or "GRAPH_OBJECT"),
        target_artifact_type=str(payload.get("target_artifact_type") or "DERIVED_GRAPH_ARTIFACT"),
    )

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------

@app.get("/api/runtime/canonical-observer/status")
async def runtime_canonical_observer_status():

    return {
        "schema": "HHS_RUNTIME_CANONICAL_OBSERVER_STATUS_ROUTE_V1",
        "ok": True,
        "status": canonical_observer_status(),
        "self_test_projection": runtime_canonical_observer_self_test(),
    }

# ----------------------------------------------------------------------------

@app.get("/api/runtime/capability/status")
async def runtime_capability_status():

    return {
        "schema": "HHS_RUNTIME_CAPABILITY_FABRIC_STATUS_ROUTE_V1",
        "ok": True,
        "fabric": capability_fabric_status(),
        "self_test_projection": universal_capability_fabric_self_test(),
    }

# ----------------------------------------------------------------------------

@app.get("/api/runtime/capability/contracts")
async def runtime_capability_contracts():

    return {
        "schema": "HHS_CAPABILITY_CONTRACTS_ROUTE_V1",
        "ok": True,
        "contracts": list_capability_contracts(),
        "self_test_projection": capability_contract_self_test(),
    }

# ----------------------------------------------------------------------------

@app.get("/api/runtime/capability/providers")
async def runtime_capability_providers():

    return {
        "schema": "HHS_CAPABILITY_PROVIDERS_ROUTE_V1",
        "ok": True,
        "registry": build_default_provider_registry(),
        "self_test_projection": capability_provider_registry_self_test(),
    }

# ----------------------------------------------------------------------------

@app.post("/api/runtime/capability/resolve")
async def runtime_capability_resolve(payload: Dict[str, Any]):

    return resolve_capability(
        str(payload.get("capability_class") or payload.get("capability") or "TEXT_GENERATION"),
        project_id=str(payload.get("project_id") or "project:default"),
        constraints=payload.get("constraints") or {},
    )

# ----------------------------------------------------------------------------

@app.post("/api/runtime/capability/propose")
async def runtime_capability_propose(payload: Dict[str, Any]):

    proposal = build_provider_execution_proposal(
        capability_class=str(payload.get("capability_class") or "TEXT_GENERATION"),
        project_id=str(payload.get("project_id") or "project:default"),
        input_payload=payload.get("input_payload") if "input_payload" in payload else payload.get("payload", {}),
        requested_operation=str(payload.get("requested_operation") or "provider.invoke"),
        constraints=payload.get("constraints") or {},
    )
    return {
        "schema": "HHS_PROVIDER_EXECUTION_PROPOSAL_ROUTE_V1",
        "ok": True,
        "proposal": proposal,
        "self_test_projection": provider_execution_proposal_self_test(),
    }

# ----------------------------------------------------------------------------

@app.post("/api/runtime/capability/execute")
async def runtime_capability_execute(payload: Dict[str, Any]):

    return run_universal_capability_fabric(
        project_id=str(payload.get("project_id") or "project:default"),
        capability_class=str(payload.get("capability_class") or "TEXT_GENERATION"),
        input_payload=payload.get("input_payload") if "input_payload" in payload else payload.get("payload", {}),
        output_modality=str(payload.get("output_modality") or "TEXT"),
        simulated_raw_result=payload.get("simulated_raw_result"),
    )

# ----------------------------------------------------------------------------

@app.post("/api/runtime/capability/fallback")
async def runtime_capability_fallback(payload: Dict[str, Any]):

    return {
        "schema": "HHS_CAPABILITY_FALLBACK_ROUTE_V1",
        "ok": True,
        "fallback_plan": build_capability_fallback_plan(
            str(payload.get("capability_class") or "TEXT_GENERATION"),
            project_id=str(payload.get("project_id") or "project:default"),
            failed_attempts=payload.get("failed_attempts") or [],
        ),
        "self_test_projection": capability_fallback_plan_self_test(),
    }


# ----------------------------------------------------------------------------

@app.get("/api/runtime/document/perception/status")
async def runtime_document_perception_status():

    return {
        "schema": "HHS_DOCUMENT_PERCEPTION_STATUS_ROUTE_V1",
        "ok": True,
        "status": deep_document_perception_status(),
        "provider_contract_self_test": document_provider_contract_self_test(),
        "pipeline_self_test_projection": deep_document_perception_pipeline_self_test(),
    }

# ----------------------------------------------------------------------------

@app.post("/api/runtime/document/perceive")
async def runtime_document_perceive(payload: Dict[str, Any]):

    return run_deep_document_perception(
        project_id=str(payload.get("project_id") or "project:default"),
        source_name=str(payload.get("source_name") or "document.pdf"),
        payload=payload.get("source_payload") if "source_payload" in payload else payload.get("payload", ""),
        declared_modality=str(payload.get("declared_modality") or payload.get("source_modality") or "PDF"),
        page_count_hint=int(payload.get("page_count_hint") or 1),
        ocr_text_hint=str(payload.get("ocr_text_hint") or ""),
    )

# ----------------------------------------------------------------------------

@app.post("/api/runtime/document/fusion")
async def runtime_document_fusion(payload: Dict[str, Any]):

    source_commitment = payload.get("source_commitment") or {"source_root_hash72": str(payload.get("source_root_hash72") or "UNRESOLVED_SOURCE")}
    observations = payload.get("observations") or []
    fusion = fuse_document_observations(source_commitment=source_commitment, observations=observations)
    return {
        "schema": "HHS_DOCUMENT_FUSION_ROUTE_V1",
        "ok": validate_document_fusion(fusion).get("ok"),
        "fusion": fusion,
        "validation": validate_document_fusion(fusion),
        "self_test_projection": document_structure_fusion_self_test(),
    }

@app.get("/api/runtime/workspace/artifact/lineage/{lineage_id:path}")
async def workspace_artifact_lineage(lineage_id: str):

    self_test = universal_artifact_pipeline_self_test()
    return {
        "schema": "HHS_WORKSPACE_ARTIFACT_LINEAGE_ROUTE_V1",
        "ok": True,
        "lineage_id": lineage_id,
        "bounded_projection": True,
        "sample_lineage": self_test["pipeline_runs"][0]["lineage"],
        "doctrine": "SOURCE_NE_PROJECTION_NE_ARTIFACT_NE_EXECUTION_AUTHORITY",
    }

# ============================================================================
# EXCEPTION HANDLING
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request,
    exc
):

    logger.exception(exc)

    return JSONResponse(

        status_code=500,

        content={

            "error":
                str(exc),

            "boot_id":
                SERVER_BOOT_ID
        }
    )

# ============================================================================
# SERVER SELF TEST
# ============================================================================

def server_self_test():

    logger.info(
        "Running server self-test..."
    )

    runtime_controller.run_steps(5)

    packet = (
        runtime_controller.export_multimodal_packet()
    )

    runtime_graph.ingest_runtime_state(packet)

    logger.info(
        "Runtime self-test complete"
    )

    logger.info(
        runtime_graph.export_graph_summary()
    )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    server_self_test()

    uvicorn.run(

        "hhs_backend.server:app",

        host="0.0.0.0",

        port=8000,

        reload=False,

        ws="websockets",

        log_level="info",
    )