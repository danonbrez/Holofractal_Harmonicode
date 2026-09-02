from __future__ import annotations
from fastapi import APIRouter
from typing import Any, Dict

from hhs_runtime.pass178.runtime import PASS178_PHYSICS, PhysicsAuthorityError, contract_corpus_identity
from hhs_runtime.pass178.templates import relativistic_lab_template, quantum_lab_template, harmonicode_lab_template

router=APIRouter(prefix="/api/runtime/pass178-physics",tags=["pass178","physics","vm81","exact"])

def _reject(e: Exception)->Dict[str,Any]:
    return {"schema":"HHS_PASS_178_ROUTE_RESULT_V1","ok":False,"status":"REJECT_PASS178_REQUEST","reason":str(e)}

@router.get("/status")
def status():
    s=PASS178_PHYSICS.status()
    s["constraint_corpus"]=contract_corpus_identity()
    s["physics_studio"]="/physics-studio/"
    return s

@router.get("/templates")
def templates():
    return {"relativity":relativistic_lab_template(),"quantum":quantum_lab_template(),"harmonicode":harmonicode_lab_template()}

@router.post("/source/{source_id}")
def ingest_source(source_id:str,payload:Dict[str,Any]):
    try:
        source=str(payload.get("source") or "").encode("utf-8")
        return PASS178_PHYSICS.ingest_source(source_id,source)
    except Exception as e: return _reject(e)

@router.post("/model/register")
def register_model(payload:Dict[str,Any]):
    try:
        return PASS178_PHYSICS.register_model(
            model_id=str(payload["model_id"]),
            model_kind=str(payload["model_kind"]),
            source_id=str(payload["source_id"]),
            parameters=payload.get("parameters") or {},
        )
    except Exception as e: return _reject(e)

@router.post("/model/{model_id}/initial")
def initial(model_id:str,payload:Dict[str,Any]):
    try: return PASS178_PHYSICS.admit_initial_state(model_id,payload)
    except Exception as e: return _reject(e)

@router.post("/model/{model_id}/step")
def step(model_id:str):
    try:
        c=PASS178_PHYSICS.step_candidate(model_id)
        if c.get("ok") is not True: return c
        return PASS178_PHYSICS.commit_step(model_id,c)
    except Exception as e: return _reject(e)

@router.get("/model/{model_id}/replay")
def replay(model_id:str):
    try: return PASS178_PHYSICS.replay(model_id)
    except Exception as e: return _reject(e)

@router.get("/model/{model_id}/render-packet")
def render_packet(model_id:str):
    try: return PASS178_PHYSICS.project_render_packet(model_id)
    except Exception as e: return _reject(e)
