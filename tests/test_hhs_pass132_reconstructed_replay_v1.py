from pathlib import Path
import subprocess

import pytest

from hhs_runtime.hhs_pass132_reconstructed_replay_v1 import (
    IdentityMismatchError,
    Pass132ReconstructedReplayService,
    WorkloadNotFoundError,
)


def service():
    return Pass132ReconstructedReplayService(run_authority_probes=True)


def test_all_18_workloads_replay_and_compare():
    s = service()
    report = s.self_test()
    assert report["ok"] is True
    assert report["workload_count"] == 18
    assert report["original_source_bytes_recovered"] is False


def test_runtime_root_mismatch_rejected():
    s = service()
    workload = s.available_workloads()[0]
    with pytest.raises(IdentityMismatchError):
        s.execute({"workload_id": workload, "runtime_root": "wrong-root"})


def test_unknown_workload_rejected():
    s = service()
    with pytest.raises(WorkloadNotFoundError):
        s.execute({"workload_id": "not-a-workload"})


def test_nine_api_routes_exposed():
    from hhs_backend.api.pass132_consequence_routes import router
    paths = {route.path for route in router.routes}
    assert paths == {
        "/api/runtime/consequences/execute",
        "/api/runtime/consequences/replay",
        "/api/runtime/consequences/compare",
        "/api/runtime/consequences/foreign-model",
        "/api/runtime/consequences/{execution_root:path}",
        "/api/runtime/consequences/{execution_root:path}/graph",
        "/api/runtime/consequences/{execution_root:path}/logical",
        "/api/runtime/consequences/{execution_root:path}/computational",
        "/api/runtime/consequences/{execution_root:path}/receipts",
    }


def test_reconstructed_c_backend_compiles(tmp_path):
    root = Path(__file__).resolve().parents[1]
    source = root / "hhs_runtime" / "native" / "pass132_ieee_control.c"
    output = tmp_path / "libpass132_reconstructed.so"
    subprocess.run([
        "gcc", "-O0", "-fno-fast-math", "-ffp-contract=off", "-frounding-math",
        "-shared", "-fPIC", str(source), "-lm", "-o", str(output)
    ], check=True)
    assert output.is_file()


def test_hash72_root_with_reserved_characters_routes_end_to_end():
    from urllib.parse import quote
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from hhs_backend.api.pass132_consequence_routes import router
    s = service()
    result = s.execute({"workload_id": s.available_workloads()[0]})
    root = result["execution_root"]
    app = FastAPI(); app.include_router(router)
    response = TestClient(app).get("/api/runtime/consequences/" + quote(root, safe=""))
    assert response.status_code == 200
    assert response.json()["execution_root"] == root
    assert response.json()["zero_bypass_interposition"]["status"] == "INTERPOSITION_ADMITTED"
