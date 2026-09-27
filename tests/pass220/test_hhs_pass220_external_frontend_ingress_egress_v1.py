from __future__ import annotations

import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / "hhs_gui/runtime_os/workspace/ProductionMobileControlCenter.tsx"
QUICK_BUILD = ROOT / "hhs_gui/runtime_os/workspace/MobileQuickBuildPanel.tsx"
PASS165 = ROOT / "hhs_runtime/pass165/ingestion.py"
PASS174_ROUTES = ROOT / "hhs_backend/api/pass174_runtime_routes.py"
LIFECYCLE = ROOT / "hhs_backend/api/development_lifecycle_routes.py"
WARM = ROOT / "hhs_backend/runtime_os_pass220_lane5_tool_hydration.py"


def _python_mib_constant(path: Path, name: str) -> int:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        rf"^{re.escape(name)}\\s*=\\s*(\\d+)\\s*\\*\\s*1024\\s*\\*\\s*1024\\s*$",
        source,
        flags=re.MULTILINE,
    )
    if not match:
        raise AssertionError(f"{name} MiB constant not found in {path}")
    return int(match.group(1)) * 1024 * 1024


def test_external_frontend_ingress_bound_matches_canonical_pass165_limit() -> None:
    control = CONTROL.read_text(encoding="utf-8")
    canonical = _python_mib_constant(PASS165, "MAX_SOURCE_BYTES")
    match = re.search(
        r"const\s+MAX_INGRESS_BYTES\s*=\s*(\d+)\s*\*\s*1024\s*\*\s*1024",
        control,
    )
    assert match, "Runtime OS external file ingress bound missing"
    frontend = int(match.group(1)) * 1024 * 1024
    assert frontend == canonical == 16 * 1024 * 1024
    assert "canonical Pass 165 limit of 16 MB" in control


def test_external_frontend_reads_exact_file_bytes_and_uses_pass174_pipeline() -> None:
    control = CONTROL.read_text(encoding="utf-8")
    for token in (
        "selected.arrayBuffer()",
        "new Uint8Array",
        "bytesToBase64(bytes)",
        '"/api/v1/pass174/sdlc/run"',
        '"/api/v1/pass174/hash216/query"',
        "source_size_bytes: selected.size",
        "frontend",
        "Hydrate vector store",
        "Read persisted vector",
    ):
        assert token in control
    assert "selected.text()" in control  # preview only
    # Exact ingress uses arrayBuffer; text preview is not the transport authority.
    assert control.index("selected.arrayBuffer()") < control.index(
        'requestJson("/api/v1/pass174/sdlc/run"'
    )


def test_quick_build_is_stricter_than_canonical_ingress_not_wider() -> None:
    quick = QUICK_BUILD.read_text(encoding="utf-8")
    assert "const MAX_SOURCE_BYTES = 4 * 1024 * 1024" in quick
    assert '"/api/v1/pass174/sdlc/run"' in quick
    assert "bytesToBase64(encoded)" in quick


def test_pass174_public_pipeline_preserves_exact_source_into_inherited_egress() -> None:
    routes = PASS174_ROUTES.read_text(encoding="utf-8")
    lifecycle = LIFECYCLE.read_text(encoding="utf-8")
    for token in (
        "source_bytes = _source_bytes(payload[\"source_payload\"])",
        "source_b64=b64encode(source_bytes).decode(\"ascii\")",
        "inherited = run_development_lifecycle(lifecycle_request)",
        '"frontend_result_fabricated": False',
        "PASS174_ENCRYPTED_HASH216_VECTOR_STORE",
        "PASS174_VM81_WHOLE_FRAME_CONTINUATION",
    ):
        assert token in routes

    for token in (
        '"source_b64": request.source_b64',
        '"source_sha256": source_hash',
        '"snapshot_bits": vm_snapshot["snapshot_bits"]',
        '"snapshot_bytes": vm_snapshot["snapshot_bytes"]',
        '"projection_b64": vm_snapshot["projection_b64"]',
        '"original_source_preserved": True',
        '"projection_replaces_source": False',
        '"frontend_result_fabricated": False',
    ):
        assert token in lifecycle


def test_lane5_tool_warming_is_post_start_nonblocking_and_fail_closed() -> None:
    source = WARM.read_text(encoding="utf-8")
    assert "asyncio.create_task(" in source
    assert "asyncio.to_thread(lifecycle.startup)" in source
    assert "WARMING_NONBLOCKING" in source
    assert '"available_to_lane5": False' in source
    assert '"lane5_selection_changed": False' in source
    assert '"candidate_only": True' in source
    assert "await warm_task" in source


def test_contract_requires_lossless_roundtrip_and_nonblocking_browser_gate() -> None:
    contract = (
        ROOT
        / "contracts/pass220/PASS_220_EXTERNAL_FRONTEND_INGRESS_EGRESS_LOSSLESS_NONBLOCKING_V1.md"
    ).read_text(encoding="utf-8")
    for token in (
        "Base64Decode(egress.manifest.source_b64)",
        "snapshot_bits  = 5184",
        "snapshot_bytes = 648",
        "browser animation-frame heartbeat continues",
        "multiple concurrent browser-originated ingress requests",
        "rejected by the frontend before",
        "I149 raw5184 public frame ingress/egress hydration",
        "Lane 5 selector files remain unchanged",
    ):
        assert token in contract
