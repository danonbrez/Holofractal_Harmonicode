from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.testclient import TestClient
from hhs_backend.api import probability_hydration_routes as routes
from hhs_runtime.pass183 import ADAPTER_EQUATIONS,ProbabilityHydrationJobStore,ProbabilityHydrationRuntime

class LocalAuthority:
    def __init__(self):self.epoch=0
    def status(self):return{"classification":"LOCAL_VM81","vmrc":{"epoch":self.epoch}}
    def execute(self,**kwargs):self.epoch+=1;return{"classification":"LOCAL_COMMIT","path":"DIRECT_RUNTIME","operation_key":sha256(repr(sorted(kwargs.items())).encode()).hexdigest(),"receipt":{"receipt_sha256":sha256(str(self.epoch).encode()).hexdigest()}}
    def replay(self):return{"classification":"LOCAL_REPLAY","deterministic_replay":True,"epoch":self.epoch}

def client(tmp_path:Path)->TestClient:
    runtime=ProbabilityHydrationRuntime(authority=LocalAuthority());routes._runtime=runtime;routes._jobs=ProbabilityHydrationJobStore(runtime,tmp_path/"jobs");app=FastAPI();app.include_router(routes.router);return TestClient(app)

def request():return{"adapter":"independent_intersection","equation":ADAPTER_EQUATIONS["independent_intersection"],"manifest":{"p_a":"1/2","p_b":"1/3","p_a_and_b":"1/6"},"seed_class":"DETERMINISTIC_ENUMERATION","modulus":1_259_713,"timeout_ms":30_000}

def test_status_adapters_parse_validate_and_hydrate(tmp_path):
    api=client(tmp_path);status=api.get("/api/v1/probability/status");assert status.status_code==200 and status.json()["singleton_vm81_authority"] is True
    adapters=api.get("/api/v1/probability/adapters").json()["adapters"];assert {item["adapter"] for item in adapters}==set(ADAPTER_EQUATIONS)
    parsed=api.post("/api/v1/probability/parse",json=request());assert parsed.status_code==200 and parsed.json()["membrane_count"]==3
    validated=api.post("/api/v1/probability/validate",json=request());assert validated.status_code==200 and validated.json()["source_equation_true"] is True
    hydrated=api.post("/api/v1/probability/hydrate",json=request());assert hydrated.status_code==200 and hydrated.json()["mutation_authority"] is False and hydrated.json()["evaluation"]["closure_exact"]=="1"

def test_execute_job_status_replay_and_websocket(tmp_path):
    api=client(tmp_path);job=api.post("/api/v1/probability/execute",json=request()).json();assert job["state"]=="SUCCEEDED";job_id=job["job_id"]
    observed=api.get(f"/api/v1/probability/jobs/{job_id}");assert observed.status_code==200 and observed.json()["checkpoint"]=="RECEIPT_COMMITTED"
    with api.websocket_connect(f"/api/v1/probability/jobs/{job_id}/events") as websocket:event=websocket.receive_json()
    assert event["terminal"] is True and event["events"][-1]["state"]=="SUCCEEDED"
    replay=api.post("/api/v1/probability/replay");assert replay.status_code==200 and replay.json()["receipt_chain_valid"] is True

def test_failed_job_can_retry_and_cancel_is_finite(tmp_path):
    api=client(tmp_path);bad=request();bad["manifest"]={"p_a":"1/2","p_b":"1/2","p_a_and_b":"1/3"};failed=api.post("/api/v1/probability/execute",json=bad).json();assert failed["state"]=="FAILED"
    retry=api.post(f"/api/v1/probability/jobs/{failed['job_id']}/retry");assert retry.status_code==200 and retry.json()["attempt"]==2
    queued=routes._jobs.create(request());cancelled=api.post(f"/api/v1/probability/jobs/{queued.job_id}/cancel");assert cancelled.status_code==200 and cancelled.json()["state"]=="CANCELLED"

def test_human_studio_has_required_workflow_surfaces():
    root=Path(__file__).resolve().parents[1]/"applications"/"probability_hydration_studio";html=(root/"index.html").read_text();script=(root/"app.js").read_text()
    assert "Probability Equation Hydration" in html
    for label in("Exact source equation","Nested membranes","Forward lane","Reciprocal lane","Zero bypass","Outer residue","Hash72 receipt","Hash216 identity"):assert label in html
    for endpoint in("parse","validate","hydrate","execute","replay"):assert endpoint in script
