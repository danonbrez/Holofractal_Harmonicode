"""Pass 203 universal hydrated-function mainframe public API."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response, runtime_controller
from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import (
    CLASSIFICATION,
    CONTRACT,
    PASS203_MAINFRAME,
    PUBLIC_PREFIX,
    InvocationRejectedError,
    UnknownFunctionError,
)

router = APIRouter(
    prefix=PUBLIC_PREFIX,
    tags=["runtime", "mainframe", "agentic", "interpreter", "compiler", "abi", "pass203"],
)

PASS203_MAINFRAME.configure_authority(lambda source: runtime_controller.authorized_tick(source=source))


class FunctionInvokeRequest(BaseModel):
    function_id: str = Field(min_length=1, max_length=512)
    arguments: Dict[str, Any] = Field(default_factory=dict)
    workspace_id: Optional[str] = Field(default=None, max_length=256)
    project_id: Optional[str] = Field(default=None, max_length=256)
    capabilities: List[str] = Field(default_factory=list, max_length=256)
    idempotency_key: Optional[str] = Field(default=None, max_length=256)
    expected_state: Optional[str] = Field(default=None, max_length=512)
    timeout_seconds: int = Field(default=30, ge=1, le=900)


class OperationInvokeRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=256)
    arguments: Dict[str, Any] = Field(default_factory=dict)
    workspace_id: Optional[str] = Field(default=None, max_length=256)
    project_id: Optional[str] = Field(default=None, max_length=256)
    capabilities: List[str] = Field(default_factory=list, max_length=256)
    idempotency_key: Optional[str] = Field(default=None, max_length=256)
    expected_state: Optional[str] = Field(default=None, max_length=512)


class PlanStep(BaseModel):
    step_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.:-]+$")
    function_id: str = Field(min_length=1, max_length=512)
    arguments: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list, max_length=256)
    timeout_seconds: int = Field(default=30, ge=1, le=900)


class MainframePlanRequest(BaseModel):
    plan_id: Optional[str] = Field(default=None, max_length=256)
    workspace_id: Optional[str] = Field(default=None, max_length=256)
    project_id: Optional[str] = Field(default=None, max_length=256)
    capabilities: List[str] = Field(default_factory=list, max_length=256)
    stop_on_error: bool = True
    steps: List[PlanStep] = Field(min_length=1, max_length=256)


def _detail(schema: str, reason: str, *, retryable: bool, remediation: str, **extra: Any) -> Dict[str, Any]:
    return {
        "schema": schema,
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "ok": False,
        "reason": reason,
        "retryable": retryable,
        "remediation": remediation,
        **extra,
    }


def _raise(exc: Exception) -> None:
    if isinstance(exc, UnknownFunctionError):
        raise HTTPException(
            status_code=404,
            detail=_detail(
                "HHS_PASS_203_UNKNOWN_FUNCTION_V1",
                str(exc),
                retryable=False,
                remediation="Refresh the catalog and select a function_id returned by GET /api/runtime/mainframe/functions.",
            ),
        ) from exc
    if isinstance(exc, InvocationRejectedError):
        raise HTTPException(
            status_code=409,
            detail=_detail(
                "HHS_PASS_203_INVOCATION_REJECTED_V1",
                str(exc),
                retryable=False,
                remediation="Use the function descriptor's execution_mode, required capabilities, workspace binding, or governed adapter.",
            ),
        ) from exc
    raise HTTPException(
        status_code=503,
        detail=_detail(
            "HHS_PASS_203_MAINFRAME_RUNTIME_ERROR_V1",
            f"{exc.__class__.__name__}: {exc}",
            retryable=True,
            remediation="Inspect GET /api/runtime/mainframe/status and retry after the declared runtime dependency is available.",
        ),
    ) from exc


@router.get("/status")
def mainframe_status() -> Dict[str, Any]:
    return _contract_response(f"{PUBLIC_PREFIX}/status", "GET", PASS203_MAINFRAME.status())


@router.post("/refresh")
def mainframe_refresh() -> Dict[str, Any]:
    try:
        result = PASS203_MAINFRAME.invoke("adapter:mainframe.refresh", {})
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{PUBLIC_PREFIX}/refresh", "POST", result)


@router.get("/functions")
def mainframe_functions(
    query: str = Query(default="", max_length=256),
    family: str = Query(default="", max_length=128),
    kind: str = Query(default="", max_length=128),
    callable_only: bool = False,
    hydrated_only: bool = False,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=1000),
) -> Dict[str, Any]:
    result = PASS203_MAINFRAME.list_functions(
        query=query,
        family=family,
        kind=kind,
        callable_only=callable_only,
        hydrated_only=hydrated_only,
        offset=offset,
        limit=limit,
    )
    return _contract_response(f"{PUBLIC_PREFIX}/functions", "GET", result)


@router.get("/functions/{function_id:path}")
def mainframe_function_detail(function_id: str) -> Dict[str, Any]:
    try:
        result = PASS203_MAINFRAME.detail(function_id)
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{PUBLIC_PREFIX}/functions/{{function_id}}", "GET", result)


@router.post("/invoke")
def mainframe_invoke(body: FunctionInvokeRequest) -> Dict[str, Any]:
    try:
        result = PASS203_MAINFRAME.invoke(
            body.function_id,
            body.arguments,
            workspace_id=body.workspace_id,
            project_id=body.project_id,
            capabilities=body.capabilities,
            idempotency_key=body.idempotency_key,
            expected_state=body.expected_state,
            timeout_seconds=body.timeout_seconds,
        )
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{PUBLIC_PREFIX}/invoke", "POST", result)


@router.get("/operations")
def mainframe_operations(
    query: str = Query(default="", max_length=256),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=1000),
) -> Dict[str, Any]:
    return _contract_response(
        f"{PUBLIC_PREFIX}/operations",
        "GET",
        PASS203_MAINFRAME.list_functions(
            query=query,
            kind="GOVERNED_OPERATION",
            callable_only=True,
            hydrated_only=True,
            offset=offset,
            limit=limit,
        ),
    )


@router.post("/operations/invoke")
def mainframe_operation_invoke(body: OperationInvokeRequest) -> Dict[str, Any]:
    request = FunctionInvokeRequest(
        function_id=f"op:{body.operation_id}",
        arguments=body.arguments,
        workspace_id=body.workspace_id,
        project_id=body.project_id,
        capabilities=body.capabilities,
        idempotency_key=body.idempotency_key,
        expected_state=body.expected_state,
    )
    return mainframe_invoke(request)


@router.get("/jobs/runtime")
def mainframe_jobs_runtime() -> Dict[str, Any]:
    try:
        result = PASS203_MAINFRAME._pass190().execution_runtime_report()
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{PUBLIC_PREFIX}/jobs/runtime", "GET", result)


@router.get("/replay/{receipt_hash72}")
def mainframe_replay(receipt_hash72: str) -> Dict[str, Any]:
    try:
        result = PASS203_MAINFRAME.replay(receipt_hash72)
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{PUBLIC_PREFIX}/replay/{{receipt_hash72}}", "GET", result)


def _topological_steps(plan: MainframePlanRequest) -> List[PlanStep]:
    by_id = {step.step_id: step for step in plan.steps}
    if len(by_id) != len(plan.steps):
        raise InvocationRejectedError("plan step_id values must be unique")
    for step in plan.steps:
        missing = set(step.depends_on) - set(by_id)
        if missing:
            raise InvocationRejectedError(f"step {step.step_id} has missing dependencies: {sorted(missing)}")
        if step.step_id in step.depends_on:
            raise InvocationRejectedError(f"step {step.step_id} cannot depend on itself")
        PASS203_MAINFRAME.detail(step.function_id)
    ordered: List[PlanStep] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(step_id: str) -> None:
        if step_id in visited:
            return
        if step_id in visiting:
            raise InvocationRejectedError("plan dependency cycle detected")
        visiting.add(step_id)
        step = by_id[step_id]
        for dependency in step.depends_on:
            visit(dependency)
        visiting.remove(step_id)
        visited.add(step_id)
        ordered.append(step)

    for step in plan.steps:
        visit(step.step_id)
    return ordered


def _path_value(value: Any, path: str) -> Any:
    current = value
    for part in [item for item in path.split(".") if item]:
        if isinstance(current, Mapping):
            current = current[part]
        elif isinstance(current, list):
            current = current[int(part)]
        else:
            raise InvocationRejectedError(f"cannot resolve plan reference path: {path}")
    return current


def _resolve_references(value: Any, completed: Mapping[str, Any]) -> Any:
    if isinstance(value, Mapping):
        if set(value) == {"$step", "path"}:
            step_id = str(value["$step"])
            if step_id not in completed:
                raise InvocationRejectedError(f"plan reference is not complete: {step_id}")
            return _path_value(completed[step_id], str(value["path"]))
        return {str(key): _resolve_references(item, completed) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_references(item, completed) for item in value]
    return value


@router.post("/plans/validate")
def mainframe_plan_validate(plan: MainframePlanRequest) -> Dict[str, Any]:
    try:
        ordered = _topological_steps(plan)
    except Exception as exc:
        _raise(exc)
    identity = {
        "plan_id": plan.plan_id,
        "workspace_id": plan.workspace_id,
        "project_id": plan.project_id,
        "steps": [step.model_dump() if hasattr(step, "model_dump") else step.dict() for step in ordered],
    }
    tick = runtime_controller.authorized_tick(source="api.runtime.mainframe.plan.validate")
    result = {
        "schema": "HHS_PASS_203_PLAN_VALIDATION_V1",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "ok": True,
        "plan_id": plan.plan_id,
        "execution_order": [step.step_id for step in ordered],
        "step_count": len(ordered),
        "plan_hash72": (tick.get("receipt") or {}).get("receipt_hash72"),
        "plan_identity": identity,
        "assistant_plan_is_execution_authority": False,
    }
    return _contract_response(f"{PUBLIC_PREFIX}/plans/validate", "POST", result)


@router.post("/plans/execute")
def mainframe_plan_execute(plan: MainframePlanRequest) -> Dict[str, Any]:
    try:
        ordered = _topological_steps(plan)
        completed: Dict[str, Any] = {}
        failures: List[Dict[str, Any]] = []
        step_results: List[Dict[str, Any]] = []
        for step in ordered:
            arguments = _resolve_references(step.arguments, completed)
            try:
                invocation = PASS203_MAINFRAME.invoke(
                    step.function_id,
                    arguments,
                    workspace_id=plan.workspace_id,
                    project_id=plan.project_id,
                    capabilities=plan.capabilities,
                    idempotency_key=f"{plan.plan_id or 'plan'}:{step.step_id}",
                    timeout_seconds=step.timeout_seconds,
                )
                completed[step.step_id] = invocation
                step_results.append({"step_id": step.step_id, "status": "completed", "invocation": invocation})
            except Exception as step_exc:
                failure = {"step_id": step.step_id, "status": "failed", "error": f"{step_exc.__class__.__name__}: {step_exc}"}
                failures.append(failure)
                step_results.append(failure)
                if plan.stop_on_error:
                    break
        final_tick = runtime_controller.authorized_tick(source="api.runtime.mainframe.plan.execute")
        result = {
            "schema": "HHS_PASS_203_PLAN_EXECUTION_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": not failures,
            "plan_id": plan.plan_id,
            "workspace_id": plan.workspace_id,
            "project_id": plan.project_id,
            "execution_order": [step.step_id for step in ordered],
            "steps": step_results,
            "completed_step_count": len(completed),
            "failure_count": len(failures),
            "final_vm81_receipt_hash72": (final_tick.get("receipt") or {}).get("receipt_hash72"),
            "assistant_plan_is_execution_authority": False,
        }
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{PUBLIC_PREFIX}/plans/execute", "POST", result)


_STUDIO_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HHS Hydrated Mainframe</title><style>
:root{color-scheme:dark;font-family:Inter,system-ui,sans-serif;background:#090b10;color:#edf4ff}body{margin:0}header{padding:18px 22px;border-bottom:1px solid #243047;background:linear-gradient(135deg,#101827,#151021)}main{display:grid;grid-template-columns:360px 1fr;min-height:calc(100vh - 84px)}aside,section{padding:16px}aside{border-right:1px solid #243047}input,select,textarea,button{width:100%;box-sizing:border-box;margin:5px 0;padding:10px;border:1px solid #33435d;border-radius:8px;background:#101827;color:#edf4ff}button{cursor:pointer;background:linear-gradient(135deg,#71e7c2,#7aa8ff);color:#071018;font-weight:800}.list{display:grid;gap:7px;max-height:68vh;overflow:auto}.item{padding:9px;border:1px solid #273752;border-radius:8px;background:#0e1420;cursor:pointer}.item b,.item small{display:block}.item small{color:#96a8c6;margin-top:4px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}pre{white-space:pre-wrap;overflow:auto;background:#070a0f;border:1px solid #25324a;border-radius:10px;padding:12px;min-height:180px}@media(max-width:850px){main{grid-template-columns:1fr}aside{border-right:0;border-bottom:1px solid #243047}.grid{grid-template-columns:1fr}}
</style></head><body><header><h1>HHS Hydrated Mainframe</h1><p>Interpreter · compiler · ABI · workspaces · jobs · artifacts · creative runtime · VM81 receipts</p></header><main><aside><input id="q" placeholder="Search functions"><select id="family"><option value="">All families</option><option>interpreter</option><option>compiler</option><option>abi</option><option>workspace</option><option>job</option><option>graphics</option></select><button id="load">Load hydrated functions</button><div id="list" class="list"></div></aside><section><div class="grid"><div><h2 id="name">Select a function</h2><pre id="detail">Catalog loading…</pre></div><div><h2>Arguments</h2><textarea id="args" rows="12">{}</textarea><button id="invoke">Invoke through authority</button><pre id="result">No invocation yet.</pre></div></div></section></main><script>
const api='/api/runtime/mainframe';let current=null;const out=(id,v)=>document.getElementById(id).textContent=typeof v==='string'?v:JSON.stringify(v,null,2);async function load(){const q=encodeURIComponent(document.getElementById('q').value);const f=encodeURIComponent(document.getElementById('family').value);const r=await fetch(`${api}/functions?hydrated_only=true&limit=500&query=${q}&family=${f}`);const p=await r.json();const root=document.getElementById('list');root.innerHTML='';for(const fn of (p.payload||p).functions||[]){const n=document.createElement('div');n.className='item';n.innerHTML=`<b>${fn.name}</b><small>${fn.kind} · ${fn.family} · ${fn.execution_mode}</small>`;n.onclick=()=>{current=fn;document.getElementById('name').textContent=fn.name;out('detail',fn)};root.append(n)}}document.getElementById('load').onclick=load;document.getElementById('invoke').onclick=async()=>{if(!current)return;let args;try{args=JSON.parse(document.getElementById('args').value)}catch(e){return out('result',e.message)}const r=await fetch(`${api}/invoke`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({function_id:current.function_id,arguments:args})});out('result',await r.json())};load();
</script></body></html>"""


@router.get("/studio", response_class=HTMLResponse, include_in_schema=False)
def mainframe_studio() -> HTMLResponse:
    return HTMLResponse(_STUDIO_HTML, headers={"Cache-Control": "no-store"})
