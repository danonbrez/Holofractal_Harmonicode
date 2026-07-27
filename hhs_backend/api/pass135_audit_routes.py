"""Read-only public API for canonical Pass 135 CEUAC audit artifacts."""
from __future__ import annotations
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

from hhs_runtime.hhs_runtime_contract_v1 import envelope_api_response

router = APIRouter(prefix="/api/audit/ceuac/pass135", tags=["pass135-ceuac"])
ROOT = Path(__file__).resolve().parents[2] / "release_artifacts" / "pass135"


def _read(name: str):
    path = ROOT / name
    if not path.is_file():
        raise HTTPException(status_code=404, detail={"code": "PASS135_AUDIT_ARTIFACT_NOT_FOUND", "artifact": name})
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/status")
def status():
    return envelope_api_response("/api/audit/ceuac/pass135/status", "GET", _read("PASS_135_EFFECTIVE_COMPLETION_VIEW.json"))


@router.get("/record")
def record():
    return envelope_api_response("/api/audit/ceuac/pass135/record", "GET", _read("PASS_135_CANONICAL_CEUAC_AUDIT_RECORD.json"))


@router.get("/scenarios")
def scenarios():
    return envelope_api_response("/api/audit/ceuac/pass135/scenarios", "GET", _read("PASS_135_SCENARIO_REPORT.json"))


@router.get("/verification")
def verification():
    return envelope_api_response("/api/audit/ceuac/pass135/verification", "GET", _read("PASS_135_CEUAC_SCHEMA_VALIDATION.json"))


@router.get("/errata")
def errata():
    return envelope_api_response("/api/audit/ceuac/pass135/errata", "GET", _read("PASS_135_COMPLETION_ERRATUM_001.json"))
