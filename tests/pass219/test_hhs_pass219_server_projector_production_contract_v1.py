from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_heavy_projector_dependencies_are_isolated_from_canonical_backend_venv():
    main_requirements = read("requirements.txt")
    projector_requirements = read("requirements-pass219-projector.txt")
    installer = read("tools/install_pass219_projector_runtime.sh")
    guarded_installer = read("deployment/digitalocean/guarded_auto_update/install.sh")

    assert "sentence-transformers" not in main_requirements
    assert "sentence-transformers==5.1.1" in projector_requirements
    assert "PROJECTOR_VENV=${HHS_P219_PROJECTOR_VENV:-/opt/hhs/pass219-projector-venv}" in installer
    assert "HHS_PASS219_PROJECTOR_WARM_CACHE_VERIFIED=1" in installer
    assert "/opt/hhs/pass219-projector-venv" not in guarded_installer
    assert "requirements-pass219-projector.txt" not in guarded_installer


def test_production_service_points_only_to_isolated_projector_runtime_and_durable_cache():
    service = read("deploy/digitalocean/hhs-pass196-integrated-environment.service")
    required = [
        "ExecStart=/opt/hhs/venv/bin/python -m uvicorn",
        "Environment=HHS_P219_PROJECTOR_PYTHON=/opt/hhs/pass219-projector-venv/bin/python",
        "Environment=HHS_P219_PROJECTOR_TIMEOUT_SECONDS=900",
        "Environment=HHS_P219_PROJECTOR_DEVICE=cpu",
        "Environment=HF_HOME=/var/lib/hhs/models/huggingface",
        "Environment=HF_HUB_DISABLE_TELEMETRY=1",
        "Environment=TOKENIZERS_PARALLELISM=false",
        "ReadWritePaths=/var/lib/hhs",
    ]
    for token in required:
        assert token in service


def test_server_execution_api_is_verify_first_single_fetch_single_model_then_replay():
    bridge = read("hhs_backend/pass219_server_projector_execution.py")
    routes = read("hhs_backend/api/pass219_acquisition_routes.py")
    panel = read("hhs_gui/runtime_os/workspace/OpenSourceAcquisitionPanel.tsx")

    for token in [
        "worker.execute_live(spec, projector)",
        "_StaticVerifiedTransport(capture.response)",
        '"projector_id": "EXTERNAL_EVIDENCE_V1"',
        '"network_fetch_count": 1',
        '"external_model_execution_count": 1',
        '"persistence_network_fetch_count": 0',
        '"persistence_external_model_execution_count": 0',
        '"vm81_commit_invoked": False',
        '"canonical_hash216_minted": False',
    ]:
        assert token in bridge

    execute_route = '@router.post("/jobs/execute")'
    dynamic_route = '@router.get("/jobs/{job_id}")'
    assert execute_route in routes
    assert routes.index(execute_route) < routes.index(dynamic_route)
    assert "/api/v1/pass174/acquisition/jobs/execute" in panel
    assert "SERVER_APPROVED_EXECUTION_V1" in panel
    assert "Acquire + run approved model" in panel
    assert "Exact receipt / diagnostic JSON" in panel


def test_production_workflow_runs_only_after_exact_main_and_proves_real_replay():
    workflow = read(".github/workflows/pass219-server-projector-production-v1.yml")
    for token in [
        "workflow_run:",
        "workflows: ['DigitalOcean Production Exact Main']",
        "github.event.workflow_run.conclusion == 'success'",
        "TARGET_SHA: ${{ github.event.workflow_run.head_sha }}",
        'test "$(git -C "$APP_ROOT" rev-parse HEAD)" = "$TARGET_SHA"',
        "HHS_P219_PROJECTOR_WARM_CACHE=1",
        "HHS_PASS219_PROJECTOR_RUNTIME_HOST_READY=1",
        "/api/v1/pass174/acquisition/jobs/execute",
        "network_fetch_count",
        "external_model_execution_count",
        "persistence_network_fetch_count",
        "persistence_external_model_execution_count",
        "TRANSLATION_INVARIANT_CANDIDATE",
        "REPLAY_VERIFIED",
        "network_fetch_performed",
        "external_model_execution_performed",
        "HHS_PASS219_PUBLIC_SERVER_PROJECTOR_READY=1",
        "StrictHostKeyChecking=yes",
    ]:
        assert token in workflow


def test_cross_modal_profile_remains_blocked_in_server_execution():
    bridge = read("hhs_backend/pass219_server_projector_execution.py")
    projector = read("hhs_runtime/hhs_pass219_approved_projector_execution_v1.py")
    assert 'APPROVED_PROFILE = "MULTILINGUAL_MPNET_TEXT_V1"' in bridge
    assert "P219_SPE_PROFILE_NOT_PRODUCTION_APPROVED" in bridge
    assert '"profile_id": "MULTILINGUAL_CLIP_IMAGE_TEXT_V1"' in projector
    assert '"production_approved": False' in projector
