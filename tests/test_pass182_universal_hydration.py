from __future__ import annotations

import os
from pathlib import Path
import tempfile

import pytest

from hhs_runtime.pass182.cli import COMMANDS, TREE_COMMANDS, build_parser
from hhs_runtime.pass182.runtime import HydrationError, UniversalHydrationCompiler


def make_tree(root: Path) -> None:
    (root / "src").mkdir()
    (root / "docs").mkdir()
    (root / "assets").mkdir()
    (root / "tests").mkdir()
    (root / "src" / "app.py").write_text(
        "import json\n"
        "def build(value):\n"
        "    return json.dumps(value)\n",
        encoding="utf-8",
    )
    (root / "tests" / "test_app.py").write_text(
        "from src.app import build\n"
        "def test_build():\n"
        "    assert build({'x': 1})\n",
        encoding="utf-8",
    )
    (root / "docs" / "README.md").write_text("# Demo\nExact hydration evidence.\n", encoding="utf-8")
    (root / "duplicate.txt").write_text("same bytes\n", encoding="utf-8")
    (root / "copy.txt").write_text("same bytes\n", encoding="utf-8")
    (root / ".env").write_text("API_KEY=super-secret-value-123456\n", encoding="utf-8")
    (root / "assets" / "tone.wav").write_bytes(b"RIFF" + b"\x00" * 48)
    (root / "assets" / "pixel.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 48)
    try:
        os.symlink("../outside-do-not-follow", root / "unsafe-link")
    except OSError:
        pass


def test_complete_read_only_tree_and_secret_safe_identity(tmp_path: Path) -> None:
    make_tree(tmp_path)
    compiler = UniversalHydrationCompiler()
    before = {p.relative_to(tmp_path).as_posix(): (p.lstat().st_mode, p.lstat().st_mtime_ns) for p in tmp_path.rglob("*")}
    snapshot = compiler.snapshot_tree(tmp_path)
    after = {p.relative_to(tmp_path).as_posix(): (p.lstat().st_mode, p.lstat().st_mtime_ns) for p in tmp_path.rglob("*")}

    assert snapshot["schema"] == "HHS_PASS182_READ_ONLY_TREE_SNAPSHOT_V1"
    assert snapshot["complete_identity_enumeration"] is True
    assert snapshot["source_mutation_authority"] is False
    assert snapshot["source_metadata_unchanged"] is True
    assert snapshot["secret_text_storage_count"] == 0
    assert len(snapshot["tree_root_hash216"]) == 216
    assert before == after

    by_path = {row["relative_path"]: row for row in snapshot["records"]}
    assert ".env" in by_path
    assert by_path[".env"]["secret_suspected"] is True
    assert by_path[".env"]["text_preview"] is None
    assert by_path["src/app.py"]["authority_class"] == "AUTHORITATIVE_SOURCE"
    assert by_path["assets/tone.wav"]["modality"] == "audio"
    assert by_path["assets/pixel.png"]["modality"] == "images"
    assert any(set(item["paths"]) == {"copy.txt", "duplicate.txt"} for item in snapshot["duplicate_content"])
    if "unsafe-link" in by_path:
        assert by_path["unsafe-link"]["kind"] == "symlink"
        assert by_path["unsafe-link"]["unsafe_symlink"] is True


def test_ir_logic_graph_and_reference_adapters(tmp_path: Path) -> None:
    make_tree(tmp_path)
    compiler = UniversalHydrationCompiler()
    snapshot = compiler.snapshot_tree(tmp_path)
    ir = compiler.build_ir(snapshot)
    graph = compiler.build_logic_graph(tmp_path, snapshot)
    adapters = compiler.modality_reference_adapters(snapshot)

    assert ir["schema"] == "HHS_PASS182_UNIVERSAL_HYDRATION_IR_V1"
    assert len(ir["ir_hash216"]) == 216
    assert "SOURCE_TREE_READ_ONLY" in ir["constraints"]
    assert graph["schema"] == "HHS_PASS182_REPOSITORY_LOGIC_GRAPH_V1"
    assert len(graph["graph_hash216"]) == 216
    assert any(edge["relation"] == "DEFINES_SYMBOL" and edge["to"].endswith(":build") for edge in graph["edges"])
    assert any(edge["relation"] == "IMPORTS_SYMBOL" for edge in graph["edges"])
    for required in ("text", "audio", "images", "video", "repository_tree"):
        assert required in adapters["reference_adapters"]
    assert adapters["external_decoder_authority"] is False


def test_sandbox_dynamic_trace_does_not_mutate_source(tmp_path: Path) -> None:
    make_tree(tmp_path)
    compiler = UniversalHydrationCompiler()
    before = compiler.snapshot_tree(tmp_path)
    trace = compiler.sandbox_dynamic_trace(
        tmp_path,
        command=("python", "-c", "from pathlib import Path; Path('sandbox-only.txt').write_text('ok')"),
        timeout_seconds=30,
    )
    after = compiler.snapshot_tree(tmp_path)
    assert trace["classification"] == "HHS_STATIC_AND_SANDBOX_DYNAMIC_TRACE_VERIFIED"
    assert trace["returncode"] == 0
    assert trace["source_tree_unchanged"] is True
    assert trace["executed_from_sandbox_copy"] is True
    assert before["tree_root_hash216"] == after["tree_root_hash216"]
    assert not (tmp_path / "sandbox-only.txt").exists()


def test_incremental_dependency_scope_reuses_unchanged_content(tmp_path: Path) -> None:
    make_tree(tmp_path)
    compiler = UniversalHydrationCompiler()
    first = compiler.snapshot_tree(tmp_path)
    (tmp_path / "src" / "app.py").write_text(
        "import json\ndef build(value):\n    return json.dumps(value, sort_keys=True)\n",
        encoding="utf-8",
    )
    second = compiler.snapshot_tree(tmp_path)
    scope = compiler.incremental_scope(first, second)
    assert scope["classification"] == "HHS_DEPENDENCY_SCOPED_REHYDRATION_VERIFIED"
    assert scope["changed"] == ["src/app.py"]
    assert "docs/README.md" in scope["unchanged_reused"]
    assert len(scope["scope_hash216"]) == 216


def test_constraint_promotion_requires_vm81_and_all_gates(tmp_path: Path) -> None:
    compiler = UniversalHydrationCompiler()
    gates = {
        "executable_behavior_confirmed": True,
        "positive_tested": True,
        "negative_tested": True,
        "adversarial_tested": True,
        "replay_verified": True,
        "contradiction_scan_passed": True,
    }
    calls = []

    def vm81_admit(proposal):
        calls.append(proposal)
        return {"classification": "TEST_INHERITED_VM81_ADMISSION", "admitted": True}

    result = compiler.promote_constraint({"name": "demo", "value": 1}, gates, vm81_admit=vm81_admit)
    assert calls
    assert result["singleton_vm81_authority_preserved"] is True
    assert result["hash72_mutation_authority"] is False
    assert result["hash216_mutation_authority"] is False
    assert len(result["receipt_hash72"]) == 72
    assert len(result["archive_hash216"]) == 216

    bad = dict(gates)
    bad["adversarial_tested"] = False
    with pytest.raises(HydrationError, match="GATE_INCOMPLETE"):
        compiler.promote_constraint({"name": "bad"}, bad, vm81_admit=vm81_admit)


def test_portable_package_and_cold_start_replay(tmp_path: Path) -> None:
    source = tmp_path / "source"
    package = tmp_path / "package"
    source.mkdir()
    make_tree(source)
    compiler = UniversalHydrationCompiler()
    snapshot = compiler.snapshot_tree(source)
    built = compiler.build_portable_package(package, profile="multimodal", source_snapshot=snapshot)
    assert built["manifest"]["profile"] == "multimodal"
    assert len(built["manifest"]["manifest_hash216"]) == 216
    assert len(built["receipt"]["receipt_hash72"]) == 72
    assert len(built["receipt"]["archive_hash216"]) == 216
    cold = compiler.verify_cold_start(package)
    assert cold["classification"] == "HHS_SERVER_COLD_RESTART_REPLAY_VERIFIED"
    assert cold["singleton_vm81_authority_preserved"] is True
    replay = compiler.replay_snapshot(source, snapshot)
    assert replay["exact"] is True


def test_required_cli_surface_is_registered() -> None:
    required = {
        "doctor", "detect", "plan", "build", "install", "ingest", "reconstruct", "compare",
        "optimize", "promote", "freeze", "replay", "verify", "package", "deploy", "status",
    }
    required_tree = {"snapshot", "enumerate", "ingest", "trace", "graph", "residuals", "verify", "replay", "freeze", "report"}
    assert required.issubset(set(COMMANDS))
    assert required_tree.issubset(set(TREE_COMMANDS))
    parser = build_parser()
    assert parser.parse_args(["doctor"]).command == "doctor"
    parsed = parser.parse_args(["tree", "graph"])
    assert parsed.command == "tree"
    assert parsed.tree_command == "graph"


def test_local_acceptance_is_nonterminal(tmp_path: Path) -> None:
    make_tree(tmp_path)
    result = UniversalHydrationCompiler().acceptance_summary(tmp_path)
    assert result["classification"] == "HHS_PASS182_I144_LOCAL_IMPLEMENTATION_ACCEPTANCE"
    assert all(result["checks"].values())
    assert result["terminal_completion_claimed"] is False
