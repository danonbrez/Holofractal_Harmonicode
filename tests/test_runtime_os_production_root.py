from __future__ import annotations

from pathlib import Path


def test_runtime_os_build_is_repository_visible():
    root = Path("hhs_gui/dist").resolve()
    index = root / "index.html"
    assets = root / "assets"

    assert index.is_file()
    assert assets.is_dir()

    html = index.read_text(encoding="utf-8")
    assert "HHS Visual Runtime OS Workspace" in html
    assert "/assets/index-" in html


def test_digitalocean_gateway_selects_runtime_os_projection_by_source():
    source = Path("hhs_backend/production_visual_server.py").read_text(encoding="utf-8")

    assert "from hhs_backend.runtime_os_visual_server import app as authoritative_app" in source
    assert "from hhs_backend.visual_server import app as authoritative_app" not in source
    assert "Pass Runtime OS HTML/assets through unchanged" in source


def test_procfile_selects_full_runtime_os_application_projection():
    procfile = Path("Procfile").read_text(encoding="utf-8")
    application_source = Path("hhs_backend/runtime_os_application_server.py").read_text(
        encoding="utf-8"
    )

    assert "hhs_backend.runtime_os_application_server:app" in procfile
    assert "hhs_backend.application_ide_server:app" not in procfile
    assert "from hhs_backend.application_ide_server import app as inherited_app" in application_source
    assert "install_pass218_i18_terminal_closure_control_plane" in application_source
    assert "project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)" in application_source


def test_runtime_os_projection_replaces_only_legacy_public_root():
    from hhs_backend import runtime_os_visual_server
    from hhs_backend.runtime_os_projection import LEGACY_PUBLIC_ROOT_NAMES

    assert runtime_os_visual_server.RUNTIME_OS_ROOT == Path("hhs_gui/dist").resolve()
    assert runtime_os_visual_server.RUNTIME_OS_INDEX.is_file()
    assert runtime_os_visual_server.RUNTIME_OS_ASSETS.is_dir()

    routes = list(runtime_os_visual_server.app.router.routes)
    route_names = {str(getattr(route, "name", "")) for route in routes}
    route_paths = {str(getattr(route, "path", "")) for route in routes}

    assert runtime_os_visual_server.PUBLIC_MOUNT_NAME in route_names
    assert "hhs-visual-home" not in route_names
    assert "/api/interface/status" in route_paths

    root_mounts = [
        route
        for route in routes
        if getattr(route, "name", None) in LEGACY_PUBLIC_ROOT_NAMES
    ]
    assert len(root_mounts) == 1
    assert root_mounts[0].name == runtime_os_visual_server.PUBLIC_MOUNT_NAME

    root_index = next(
        index
        for index, route in enumerate(routes)
        if getattr(route, "name", None) == runtime_os_visual_server.PUBLIC_MOUNT_NAME
    )

    for required in {
        "/api/system/status",
        "/api/assistant/status",
        "/api/runtime/installation/status",
        "/api/runtime/integration/status",
        "/api/public/status",
    }:
        assert required in route_paths
        route_index = next(
            index
            for index, route in enumerate(routes)
            if str(getattr(route, "path", "")) == required
        )
        assert route_index < root_index


def test_runtime_os_application_installs_pass218_i18_terminal_closure_membrane():
    from hhs_backend import runtime_os_application_server

    routes = list(runtime_os_application_server.app.router.routes)
    route_paths = {str(getattr(route, "path", "")) for route in routes}
    for required in {
        "/api/runtime/pass218/authority/maintenance-consumption/status",
        "/api/runtime/pass218/authority/maintenance-consumption/claim",
        "/api/runtime/pass218/authority/maintenance-consumption/attest",
        "/api/runtime/pass218/authority/maintenance-consumption/reconcile",
        "/api/runtime/pass218/authority/maintenance-consumption/distributed/status",
        "/api/runtime/pass218/authority/maintenance-consumption/distributed/synchronize",
        "/api/runtime/pass218/authority/maintenance-execution/status",
        "/api/runtime/pass218/authority/maintenance-closure/status",
        "/api/runtime/pass218/authority/maintenance-closure/synchronize",
    }:
        assert required in route_paths

    assert (
        runtime_os_application_server.PASS218_I15_CONSUMPTION_CONTROL_PLANE
        is runtime_os_application_server.PASS218_I16_CONSUMPTION_CONTROL_PLANE
        is runtime_os_application_server.PASS218_I17_EXECUTION_CONTROL_PLANE
        is runtime_os_application_server.PASS218_I18_CLOSURE_CONTROL_PLANE
    )
    status = runtime_os_application_server.PASS218_I18_CLOSURE_CONTROL_PLANE.status()
    assert status["browser_executes_maintenance"] is False
    assert status["redispatch_after_unknown_forbidden"] is True
    assert status["successor_recovery_only"] is True
    assert status["successor_repairs_terminal_evidence_without_redispatch"] is True
    assert status["legacy_attest_route_rebound_to_distributed_i17_result"] is status["distributed_closure_configured"]
    assert status["legacy_reconcile_route_rebound_to_distributed_closure"] is status["distributed_closure_configured"]
    assert status["canonical_authority_minted"] is False
    assert status["canonical_mutation_permitted"] is False
    assert status["action_authority_minted"] is False


def test_pass218_i16_failover_anti_replay_smoke():
    from hhs_runtime.core.hash72_digest_v1 import hash72_digest
    from hhs_runtime.pass218.distributed_consumption_i16 import (
        Pass218DistributedConsumptionReplayRejected,
        Pass218InMemoryDistributedConsumptionLedger,
        synchronize_distributed_claims_to_local,
    )
    from hhs_runtime.pass218.distributed_ownership import (
        Pass218InMemoryConsensusHarness,
        Pass218InMemoryDistributedAuthority,
    )
    from hhs_runtime.pass218.execution_i15 import (
        Pass218ReleaseConsumptionJournal,
        seal_release_claim,
    )
    import tempfile

    def h72(label: str) -> str:
        return hash72_digest({"domain": "HHS-P218-I16-PRODUCTION-ROOT-SMOKE"}, {"label": label})

    harness = Pass218InMemoryConsensusHarness()
    first = Pass218InMemoryDistributedAuthority(
        harness,
        owner_id="i16-smoke-owner-a",
        host_id="i16-smoke-host-a",
        lease_ttl_seconds=9,
    )
    first_record = first.acquire()
    assert first_record is not None and first_record["fence_epoch"] == 1

    action_hash = h72("action")
    release = {
        "schema": "HHS-P218-I14-MAINTENANCE-RELEASE-V1",
        "version": "HHS-P218-MULTI-PARTY-MAINTENANCE-APPROVAL-I14-V1",
        "policy_hash72": h72("policy"),
        "action_record_hash72": action_hash,
        "action": "PREPARE_CREDENTIAL_ROTATION",
        "prepared_by_operator_id": "prep",
        "preparer_message_hash72": h72("prep"),
        "approver_operator_ids": ["alice", "bob"],
        "approval_message_hash72s": [h72("alice"), h72("bob")],
        "executor_operator_id": "exec",
        "executor_message_hash72": h72("exec"),
        "required_distinct_approvers": 2,
        "valid_distinct_approvers": 2,
        "distributed_fence_epoch": 1,
        "current_status_hash72": h72("status"),
        "released_epoch_seconds": 1_800_000_000,
        "expires_epoch_seconds": 1_800_000_600,
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "pass146_statement_integrity_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "external_maintenance_preconditions_satisfied": True,
        "maintenance_remains_external": True,
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
    }
    release["record_hash72"] = hash72_digest({"domain": release["schema"]}, release)
    preflight = {
        "schema": "HHS-P218-I14-MAINTENANCE-PREFLIGHT-V1",
        "ok": True,
        "release_record_hash72": release["record_hash72"],
        "action_record_hash72": action_hash,
        "distributed_fence_epoch": 1,
        "current_status_hash72": h72("preflight"),
        "approval_quorum_satisfied": True,
        "separation_of_duties_satisfied": True,
        "current_quorum_satisfied": True,
        "current_writer_fence_satisfied": True,
        "recorded_revocations_rechecked": True,
        "maintenance_remains_external": True,
    }
    claim = seal_release_claim(
        release=release,
        preflight=preflight,
        claimed_epoch_ns=1_800_000_000_000_000_000,
    )
    Pass218InMemoryDistributedConsumptionLedger(first).consume_claim(claim)

    harness.expire_owner()
    replacement = Pass218InMemoryDistributedAuthority(
        harness,
        owner_id="i16-smoke-owner-b",
        host_id="i16-smoke-host-b",
        lease_ttl_seconds=9,
    )
    replacement_record = replacement.acquire()
    assert replacement_record is not None and replacement_record["fence_epoch"] == 2
    replacement_ledger = Pass218InMemoryDistributedConsumptionLedger(replacement)

    with tempfile.TemporaryDirectory() as directory:
        journal = Pass218ReleaseConsumptionJournal(directory)
        assert synchronize_distributed_claims_to_local(journal, replacement_ledger) == 1
        restored = journal.claim_for_release(release["record_hash72"])
        assert restored is not None
        assert restored["record_hash72"] == claim["record_hash72"]

    second_release = dict(release)
    second_release["distributed_fence_epoch"] = 2
    second_release["policy_hash72"] = h72("policy-2")
    second_release["current_status_hash72"] = h72("status-2")
    second_release["record_hash72"] = hash72_digest(
        {"domain": second_release["schema"]},
        {key: value for key, value in second_release.items() if key != "record_hash72"},
    )
    second_preflight = dict(preflight)
    second_preflight["release_record_hash72"] = second_release["record_hash72"]
    second_preflight["distributed_fence_epoch"] = 2
    second_preflight["current_status_hash72"] = h72("preflight-2")
    second_claim = seal_release_claim(
        release=second_release,
        preflight=second_preflight,
        claimed_epoch_ns=1_800_000_000_000_000_001,
    )
    try:
        replacement_ledger.consume_claim(second_claim)
    except Pass218DistributedConsumptionReplayRejected:
        pass
    else:
        raise AssertionError("I16 failed to preserve prepared-action anti-replay across failover")


def test_digitalocean_service_uses_one_versioned_runtime_os_release():
    service = Path("deploy/digitalocean/hhs-pass196-integrated-environment.service").read_text(
        encoding="utf-8"
    )
    validator = Path(
        "deployment/digitalocean/guarded_auto_update/validate-candidate.sh"
    ).read_text(encoding="utf-8")
    builder = Path(
        "deployment/digitalocean/guarded_auto_update/build-runtime-os.sh"
    ).read_text(encoding="utf-8")

    assert "Environment=HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/current" in service
    assert "Environment=HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/dist" not in service
    assert "Environment=HHS_RUNTIME_OS_ROOT=" not in service

    assert 'HHS_RUNTIME_OS_ASSET_ROOT="$RUNTIME_OS_ROOT"' in validator
    assert 'env -u HHS_RUNTIME_OS_ROOT' in validator
    assert 'HHS_RUNTIME_OS_ROOT="$RUNTIME_OS_ROOT"' not in validator

    assert 'LIVE_ROOT=$(realpath -m "$ROOT")' in builder
    assert 'OUTPUT_ROOT=/var/lib/hhs/runtime-os/dist' in builder


def test_legacy_harmonizer_remains_inherited_source_not_public_authority():
    legacy_root = Path("applications/holofractal_harmonizer")
    assert (legacy_root / "index.html").is_file()

    projection = Path("hhs_backend/runtime_os_projection.py").read_text(encoding="utf-8")
    assert '"legacy_harmonizer_is_public_root": False' in projection
    assert 'os.environ.get("HHS_RUNTIME_OS_ASSET_ROOT")' in projection
    assert 'RUNTIME_OS_SOURCE_ROOT = ROOT_DIR / "hhs_gui"' in projection


def test_pass185_production_runtime_authority_route_wins_first_match_and_preserves_inherited_alias():
    from hhs_backend import runtime_os_application_server

    routes = list(runtime_os_application_server.app.router.routes)
    authority_matches = [
        route
        for route in routes
        if str(getattr(route, "path", "")) == "/api/runtime/authority/status"
        and "GET" in (getattr(route, "methods", None) or set())
    ]
    assert authority_matches
    assert getattr(authority_matches[0], "endpoint", None).__name__ == "production_runtime_authority_status"

    inherited_alias = [
        route
        for route in routes
        if str(getattr(route, "path", "")) == "/api/runtime/inherited-authority/status"
        and "GET" in (getattr(route, "methods", None) or set())
    ]
    assert len(inherited_alias) == 1
    assert getattr(inherited_alias[0], "endpoint", None).__name__ == "production_inherited_runtime_authority_status"


def test_pass185_production_auto_tick_profile_is_bound_to_live_workflow():
    source = Path("hhs_backend/server.py").read_text(encoding="utf-8")

    assert 'HHS_COGNITION_AUTO_TICK' in source
    assert 'LIVE_WORKFLOW_AUTO_START = _environment_flag_enabled(' in source
    assert 'auto_start=LIVE_WORKFLOW_AUTO_START' in source
    assert '"live_workflow_auto_start":' in source


def test_pass185_runtime_step_yields_asgi_loop_without_parallel_step_authority():
    source = Path("hhs_backend/api/runtime_routes.py").read_text(encoding="utf-8")

    assert "runtime_step_lock = asyncio.Lock()" in source
    assert "async with runtime_step_lock:" in source
    assert "await asyncio.to_thread(" in source
    assert "_execute_runtime_step_sync" in source
