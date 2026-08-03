"""Pass 205 deterministic multimodal continuation public API and visual studio."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from hhs_backend.api.runtime_routes import _contract_response
from hhs_backend.runtime.hhs_pass205_continuation_runtime_v1 import (
    API_PREFIX,
    CLASSIFICATION,
    CONTRACT,
    PASS205_CONTINUATION_RUNTIME,
    ContinuationNotFound,
    ContinuationRejected,
)

router = APIRouter(
    prefix=API_PREFIX,
    tags=["runtime", "continuation", "vm5184", "g243", "gaming", "machine-learning", "pass205"],
)


class DeltaEvent(BaseModel):
    cell: int = Field(ge=0, le=80)
    control_g: int = Field(ge=0, le=242)
    xor_mask: int = Field(gt=0, le=(1 << 64) - 1)


class AdvanceRequest(BaseModel):
    parent_root216: str = Field(min_length=216, max_length=216)
    events: List[DeltaEvent] = Field(min_length=1, max_length=81)
    expected_parent_receipt_hash72: Optional[str] = Field(default=None, min_length=72, max_length=72)
    frontier_cells: Optional[List[int]] = None


class RootRequest(BaseModel):
    continuation_root216: str = Field(min_length=216, max_length=216)


class RetrieveRequest(BaseModel):
    target_state_words: List[int] = Field(min_length=81, max_length=81)
    schema_root216: Optional[str] = Field(default=None, min_length=216, max_length=216)
    constraint_root216: Optional[str] = Field(default=None, min_length=216, max_length=216)
    top_k: int = Field(default=32, ge=1, le=1024)


class HydrateRequest(RetrieveRequest):
    controls_by_cell: Dict[str, int] = Field(default_factory=dict)


def _events(body: AdvanceRequest) -> list[dict[str, int]]:
    return [event.model_dump() if hasattr(event, "model_dump") else event.dict() for event in body.events]


def _raise(exc: Exception) -> None:
    if isinstance(exc, ContinuationNotFound):
        raise HTTPException(
            status_code=404,
            detail={
                "schema": "HHS_PASS_205_CONTINUATION_NOT_FOUND_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "ok": False,
                "reason": str(exc),
                "retryable": False,
            },
        ) from exc
    if isinstance(exc, (ContinuationRejected, ValueError)):
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_PASS_205_CONTINUATION_REJECTED_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "ok": False,
                "reason": str(exc),
                "retryable": False,
            },
        ) from exc
    raise HTTPException(
        status_code=503,
        detail={
            "schema": "HHS_PASS_205_CONTINUATION_RUNTIME_UNAVAILABLE_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": False,
            "reason": f"{exc.__class__.__name__}: {exc}",
            "retryable": True,
        },
    ) from exc


def _response(path: str, method: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    return _contract_response(path, method, dict(payload))


@router.get("/status")
def continuation_status() -> Dict[str, Any]:
    return _response(f"{API_PREFIX}/status", "GET", PASS205_CONTINUATION_RUNTIME.status())


@router.get("/snapshots/{continuation_root216:path}")
def continuation_snapshot(continuation_root216: str) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.snapshot(continuation_root216)
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/snapshots/{{continuation_root216}}", "GET", result)


@router.get("/graph/{continuation_root216:path}")
def continuation_graph(continuation_root216: str) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.graph(continuation_root216)
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/graph/{{continuation_root216}}", "GET", result)


@router.get("/projections/{continuation_root216:path}")
def continuation_projections(continuation_root216: str) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.projections(continuation_root216)
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/projections/{{continuation_root216}}", "GET", result)


@router.post("/advance")
def continuation_advance(body: AdvanceRequest) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.advance(
            parent_root216=body.parent_root216,
            events=_events(body),
            expected_parent_receipt_hash72=body.expected_parent_receipt_hash72,
            frontier_cells=body.frontier_cells,
        )
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/advance", "POST", result)


@router.post("/branch")
def continuation_branch(body: AdvanceRequest) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.branch(
            parent_root216=body.parent_root216,
            events=_events(body),
            expected_parent_receipt_hash72=body.expected_parent_receipt_hash72,
            frontier_cells=body.frontier_cells,
        )
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/branch", "POST", result)


@router.post("/reverse")
def continuation_reverse(body: RootRequest) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.reverse(body.continuation_root216)
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/reverse", "POST", result)


@router.post("/replay")
def continuation_replay(body: RootRequest) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.replay(body.continuation_root216)
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/replay", "POST", result)


@router.post("/verify")
def continuation_verify(body: RootRequest) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.verify(body.continuation_root216)
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/verify", "POST", result)


@router.post("/retrieve")
def continuation_retrieve(body: RetrieveRequest) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.retrieve(
            target_state_words=body.target_state_words,
            schema_root216=body.schema_root216,
            constraint_root216=body.constraint_root216,
            top_k=body.top_k,
        )
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/retrieve", "POST", result)


@router.post("/hydrate")
def continuation_hydrate(body: HydrateRequest) -> Dict[str, Any]:
    try:
        result = PASS205_CONTINUATION_RUNTIME.hydrate_target(
            target_state_words=body.target_state_words,
            controls_by_cell=body.controls_by_cell,
            schema_root216=body.schema_root216,
            constraint_root216=body.constraint_root216,
            top_k=body.top_k,
        )
    except Exception as exc:
        _raise(exc)
    return _response(f"{API_PREFIX}/hydrate", "POST", result)


STUDIO_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HHS Pass 205 Continuation Studio</title>
<style>
:root{color-scheme:dark;background:#080b12;color:#d9f7ff;font:14px/1.4 ui-monospace,SFMono-Regular,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 20% 0,#112538,#080b12 48%);min-height:100vh}
header{padding:18px 22px;border-bottom:1px solid #1f5262;background:#09131dcc;position:sticky;top:0;backdrop-filter:blur(10px)}
h1{font-size:18px;margin:0;color:#7cf4ff}main{display:grid;grid-template-columns:minmax(280px,420px) 1fr;gap:14px;padding:14px}
.panel{border:1px solid #1e5967;background:#0c1620e8;border-radius:8px;padding:14px;box-shadow:0 10px 32px #0007}
label{display:block;margin-top:10px;color:#8bdbe6}input,textarea,button{width:100%;margin-top:5px;border:1px solid #256b78;border-radius:5px;background:#071018;color:#d9f7ff;padding:9px;font:inherit}
textarea{min-height:120px;resize:vertical}button{cursor:pointer;background:#103845;color:#9ff8ff;font-weight:700}button:hover{background:#165364}
.grid{display:grid;grid-template-columns:repeat(9,1fr);gap:3px;margin-top:12px}.cell{aspect-ratio:1;border:1px solid #1d5663;background:#0b2029;color:#65dce8;padding:2px;font-size:10px;overflow:hidden}
pre{white-space:pre-wrap;word-break:break-word;max-height:72vh;overflow:auto;background:#050a0f;border:1px solid #183f49;padding:12px;border-radius:6px}
.status{display:flex;gap:14px;flex-wrap:wrap;color:#77e8c7}.status b{color:#fff}@media(max-width:900px){main{grid-template-columns:1fr}}
</style>
</head>
<body>
<header><h1>PASS 205 · VM5184 × G243 MULTIMODAL CONTINUATION STUDIO</h1><div class="status" id="status">loading runtime…</div></header>
<main>
<section class="panel">
<label>Parent continuation root216<input id="parent" autocomplete="off"></label>
<label>Ordered delta events (JSON)<textarea id="events">[{"cell":0,"control_g":0,"xor_mask":1}]</textarea></label>
<button id="advance">Advance committed state</button>
<button id="verify">Verify selected state</button>
<button id="replay">Replay selected lineage</button>
<button id="reverse">Create inverse continuation</button>
<div class="grid" id="grid"></div>
</section>
<section class="panel"><pre id="output">Select an operation.</pre></section>
</main>
<script>
const base='/api/runtime/continuation';
const out=document.getElementById('output');const parent=document.getElementById('parent');
function show(v){out.textContent=JSON.stringify(v,null,2);const s=v?.snapshot||v;if(s?.continuation_root216){parent.value=s.continuation_root216;render(s.state_words||[])}}
function render(words){const g=document.getElementById('grid');g.innerHTML='';for(let i=0;i<81;i++){const d=document.createElement('div');d.className='cell';d.textContent=i+'\n'+(words[i]??'—');g.appendChild(d)}}
async function call(path,options){const r=await fetch(base+path,options);const v=await r.json();show(v);if(!r.ok)throw new Error(r.status)}
async function boot(){const r=await fetch(base+'/status');const v=await r.json();const p=v.payload||v;document.getElementById('status').innerHTML=`<span><b>${p.state_bits}</b> bits</span><span><b>${p.hydration_projection_count}</b> q</span><span><b>${p.snapshot_count}</b> snapshots</span><span><b>${p.projection_channel_count}</b> channels</span>`;parent.value=p.genesis_root216;const s=await fetch(base+'/snapshots/'+encodeURIComponent(p.genesis_root216));show(await s.json())}
document.getElementById('advance').onclick=()=>call('/advance',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({parent_root216:parent.value,events:JSON.parse(document.getElementById('events').value)})});
for(const op of ['verify','replay','reverse'])document.getElementById(op).onclick=()=>call('/'+op,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({continuation_root216:parent.value})});
boot().catch(e=>out.textContent=String(e));
</script>
</body></html>"""


@router.get("/studio", response_class=HTMLResponse)
def continuation_studio() -> HTMLResponse:
    return HTMLResponse(STUDIO_HTML)
