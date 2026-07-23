from __future__ import annotations
import json
from pathlib import Path
from hhs_runtime.hhs_pass135_ceuac_audit_v1 import EvidenceStore, build_interpretations, verify_audit


def test_evidence_interpretation_authority_separation(tmp_path: Path):
    store=EvidenceStore(tmp_path)
    e=store.add(authority_level="A1",classification="OBSERVED_WORKING",domain="TEST",operation="build_native_runtime",interface="CLI",request={},response={"ok":True},success=True,started_ns=1,ended_ns=2)
    store.add(authority_level="A1",classification="OBSERVED_WORKING",domain="TEST",operation="start_public_server",interface="CLI",request={},response={"ok":True},success=True,started_ns=2,ended_ns=3)
    store.add(authority_level="A2",classification="OBSERVED_WORKING",domain="TEST",operation="health_probe",interface="HTTP",request={},response={"ok":True},success=True,started_ns=3,ended_ns=4)
    interpretations, conclusions=build_interpretations(store.records,{"ancestry_closed":False,"runtime_progressed":False,"consequence_routes_exposed":False,"zero_bypass_closed":False})
    assert all(row["authority_level"] in {"A1","A2"} for row in store.records)
    assert all(row["authority_level"] == "A3" for row in interpretations)
    assert [row for row in conclusions if row["authority_level"]=="A4"][0]["classification"]=="NOT_ASSESSED"
    assert verify_audit(tmp_path,store.records,interpretations,conclusions)["ok"]


def test_verifier_detects_raw_evidence_mutation(tmp_path: Path):
    store=EvidenceStore(tmp_path)
    row=store.add(authority_level="A1",classification="OBSERVED_WORKING",domain="TEST",operation="x",interface="CLI",request={},response={"ok":True},success=True,started_ns=1,ended_ns=2)
    raw=tmp_path/row["raw_artifact_path"]
    raw.write_text("tampered",encoding="utf-8")
    result=verify_audit(tmp_path,store.records,[],[])
    assert not result["ok"]
    assert any("hash mismatch" in x for x in result["failures"])


def test_a4_promotion_is_rejected(tmp_path: Path):
    result=verify_audit(tmp_path,[],[],[{"authority_level":"A4","classification":"OBSERVED_WORKING","interpretation_id":None,"evidence_ids":[]}])
    assert not result["ok"]
    assert "unauthorized A4 conclusion" in result["failures"]
