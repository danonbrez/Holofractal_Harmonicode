from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_production_entrypoint_serves_integrated_visual_ide() -> None:
    procfile = read("Procfile")
    server = read("hhs_backend/production_ide_server.py")
    assert "hhs_backend.production_ide_server:app" in procfile
    assert "from hhs_backend import production_server as production" in server
    assert "app = production.app" in server
    assert 'name="hhs-production-harmonizer"' in server
    assert "/api/runtime/multimodal-ingress" in server
    assert "/api/runtime/development" in server


def test_pass165_snapshot_is_exact_and_hash216_indexed() -> None:
    routes = read("hhs_backend/api/pass165_multimodal_ingress_routes.py")
    assert '"snapshot_bits": len(projection) * 8' in routes
    assert '"snapshot_bytes": len(projection)' in routes
    assert '"vm81_cells": 81' in routes
    assert '"bits_per_cell": 64' in routes
    assert '"hash216_lane_count": 3' in routes
    assert '"hash216_lane_width": 72' in routes
    assert '"ingestion_positions_hash216": positions' in routes
    assert '"frontend_mutation_authority": False' in routes


def test_lifecycle_composes_existing_authorities() -> None:
    routes = read("hhs_backend/api/development_lifecycle_routes.py")
    for operation in (
        '"ingress.register"',
        '"interpret.execute"',
        '"compile.execute"',
        '"emulator.create"',
        '"emulator.run"',
        '"emulator.snapshot"',
    ):
        assert operation in routes
    assert "SERVICE.ingest_source" in routes
    assert "snapshot_payload(source_hash)" in routes
    assert "Hash216Genome.positions" in routes
    assert "Hash216Genome.root" in routes
    assert "hash72_digest" in routes
    assert '"original_source_preserved": True' in routes
    assert '"projection_replaces_source": False' in routes
    assert '"frontend_result_fabricated": False' in routes


def test_emulator_initial_state_is_bound_to_exact_vm_snapshot() -> None:
    authority = read("hhs_backend/runtime/hhs_workspace_authority_loop_v1.py")
    lifecycle = read("hhs_backend/api/development_lifecycle_routes.py")
    assert 'initial_state=payload_dict.get("initial_state")' in authority
    assert '"projection_b64": vm_snapshot["projection_b64"]' in lifecycle
    assert '"hash216_positions": vm_snapshot["ingestion_positions_hash216"]' in lifecycle
    assert '"source_b64": request.source_b64' in lifecycle
