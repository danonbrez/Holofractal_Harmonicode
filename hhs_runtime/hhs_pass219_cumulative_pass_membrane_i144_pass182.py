from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from hhs_runtime.pass182 import CONTRACT_ID, UniversalHydrationCompiler
from hhs_runtime.pass182.cli import COMMANDS, TREE_COMMANDS

ROOT = Path(__file__).resolve().parents[1]
FROZEN_I143 = "f4ba13da3d4ac556d7fa511c667187d3c9e7ac52"
I143_RECEIPT = Path("evidence/pass183/i143/PASS_219_I143_PASS183_VALIDATION_RECEIPT.json")
I143_RECEIPT_BLOB = "4619ea215173c55fe50e68197dfa87cb6ce58276"
PASS182_CONTRACT = Path("docs/pass182/HHS_PASS_182_UNIVERSAL_MULTIMODAL_HYDRATION_COMPILER_AND_READ_ONLY_TREE_RUNTIME.md")

REQUIRED_COMMANDS = {
    "doctor", "detect", "plan", "build", "install", "ingest", "reconstruct", "compare",
    "optimize", "promote", "freeze", "replay", "verify", "package", "deploy", "status",
}
REQUIRED_TREE_COMMANDS = {"snapshot", "enumerate", "ingest", "trace", "graph", "residuals", "verify", "replay", "freeze", "report"}


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _text(path: str | Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _fixture(root: Path) -> None:
    (root / "src").mkdir()
    (root / "docs").mkdir()
    (root / "assets").mkdir()
    (root / "src" / "logic.py").write_text(
        "import json\ndef normalize(value):\n    return json.dumps(value, sort_keys=True)\n",
        encoding="utf-8",
    )
    (root / "docs" / "README.md").write_text("# Pass 182 fixture\n", encoding="utf-8")
    (root / ".env").write_text("ACCESS_TOKEN=redacted-test-secret-123456\n", encoding="utf-8")
    (root / "assets" / "tone.wav").write_bytes(b"RIFF" + b"\0" * 32)
    (root / "assets" / "frame.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 32)


def validate_pass182_predecessor_and_contract() -> dict[str, Any]:
    _git("merge-base", "--is-ancestor", FROZEN_I143, "HEAD")
    actual_blob = _git("rev-parse", f"HEAD:{I143_RECEIPT}")
    if actual_blob != I143_RECEIPT_BLOB:
        raise RuntimeError(f"PASS182_I143_RECEIPT_BLOB_DRIFT:{actual_blob}")
    receipt = json.loads(_text(I143_RECEIPT))
    contract = _text(PASS182_CONTRACT)
    required_contract_tokens = (
        CONTRACT_ID,
        "READ_ONLY_IDENTITY_SNAPSHOT",
        "HHS_UNIVERSAL_HYDRATION_IR",
        "HHS_COMPLETE_FILE_TREE_ENUMERATION_VERIFIED",
        "HHS_SERVER_COLD_RESTART_REPLAY_VERIFIED",
        "THE FILE TREE AND MODALITY CORPUS ARE IMMUTABLE EVIDENCE.",
    )
    missing = [token for token in required_contract_tokens if token not in contract]
    if missing:
        raise RuntimeError(f"PASS182_CONTRACT_DRIFT:{missing}")
    if receipt.get("closure", {}).get("i143_dependency_scoped_validation_green") is not True:
        raise RuntimeError("PASS182_I143_PREDECESSOR_NOT_GREEN")
    return {
        "ok": True,
        "frozen_i143": FROZEN_I143,
        "i143_validation_receipt_blob": actual_blob,
        "contract_id": CONTRACT_ID,
        "historical_pass182_classification": "CONTRACT_ONLY_BEFORE_I144",
    }


def validate_pass182_runtime_surface() -> dict[str, Any]:
    runtime = _text("hhs_runtime/pass182/runtime.py")
    cli = _text("hhs_runtime/pass182/cli.py")
    shell = _text("bin/hhs-hydrate")
    for token in (
        "class UniversalHydrationCompiler",
        "def snapshot_tree",
        "def build_ir",
        "def build_logic_graph",
        "def incremental_scope",
        "def sandbox_dynamic_trace",
        "def promote_constraint",
        "def build_portable_package",
        "def verify_cold_start",
        "def replay_snapshot",
    ):
        if token not in runtime:
            raise RuntimeError(f"PASS182_RUNTIME_SURFACE_MISSING:{token}")
    if not REQUIRED_COMMANDS.issubset(set(COMMANDS)) or not REQUIRED_TREE_COMMANDS.issubset(set(TREE_COMMANDS)):
        raise RuntimeError("PASS182_COMMAND_SURFACE_INCOMPLETE")
    if "hhs_runtime.pass182.cli" not in shell:
        raise RuntimeError("PASS182_CLI_ENTRYPOINT_DRIFT")
    return {"ok": True, "command_count": len(COMMANDS), "tree_command_count": len(TREE_COMMANDS), "cli_module_bound": True}


def validate_pass182_exact_hydration_cycle() -> dict[str, Any]:
    compiler = UniversalHydrationCompiler()
    with tempfile.TemporaryDirectory(prefix="pass182-i144-") as tmp:
        source = Path(tmp) / "source"
        package = Path(tmp) / "package"
        source.mkdir()
        _fixture(source)
        snapshot = compiler.snapshot_tree(source)
        ir = compiler.build_ir(snapshot)
        graph = compiler.build_logic_graph(source, snapshot)
        trace = compiler.sandbox_dynamic_trace(
            source,
            command=("python", "-c", "from pathlib import Path; Path('sandbox-write').write_text('ok')"),
            timeout_seconds=30,
        )
        adapters = compiler.modality_reference_adapters(snapshot)
        built = compiler.build_portable_package(package, profile="multimodal", source_snapshot=snapshot)
        cold = compiler.verify_cold_start(package)
        replay = compiler.replay_snapshot(source, snapshot)

        assert snapshot["source_mutation_authority"] is False
        assert snapshot["secret_text_storage_count"] == 0
        assert snapshot["complete_identity_enumeration"] is True
        assert len(snapshot["tree_root_hash216"]) == 216
        assert len(ir["ir_hash216"]) == 216
        assert len(graph["graph_hash216"]) == 216
        assert trace["source_tree_unchanged"] is True
        assert trace["executed_from_sandbox_copy"] is True
        assert trace["returncode"] == 0
        assert replay["exact"] is True
        assert cold["classification"] == "HHS_SERVER_COLD_RESTART_REPLAY_VERIFIED"
        for name in ("text", "audio", "images", "video", "repository_tree"):
            assert name in adapters["reference_adapters"]
        assert len(built["receipt"]["receipt_hash72"]) == 72
        assert len(built["receipt"]["archive_hash216"]) == 216

        (source / "src" / "logic.py").write_text(
            "import json\ndef normalize(value):\n    return json.dumps(value, separators=(',', ':'))\n",
            encoding="utf-8",
        )
        changed = compiler.snapshot_tree(source)
        scope = compiler.incremental_scope(snapshot, changed)
        assert scope["changed"] == ["src/logic.py"]
        assert "docs/README.md" in scope["unchanged_reused"]

    return {
        "ok": True,
        "read_only_tree": True,
        "secret_safe": True,
        "ir": True,
        "logic_graph": True,
        "sandbox_dynamic_trace": True,
        "incremental_dependency_scope": True,
        "portable_package": True,
        "cold_start_replay": True,
        "reference_adapters": ["text", "audio", "images", "video", "repository_tree"],
    }


def validate_pass182_vm81_promotion_boundary() -> dict[str, Any]:
    compiler = UniversalHydrationCompiler()
    calls: list[dict[str, Any]] = []

    def inherited_vm81(proposal: dict[str, Any]) -> dict[str, Any]:
        calls.append(proposal)
        return {"classification": "I144_INHERITED_VM81_ADMISSION_WITNESS", "admitted": True}

    result = compiler.promote_constraint(
        {"constraint": "SOURCE_TREE_READ_ONLY", "scope": "fixture"},
        {
            "executable_behavior_confirmed": True,
            "positive_tested": True,
            "negative_tested": True,
            "adversarial_tested": True,
            "replay_verified": True,
            "contradiction_scan_passed": True,
        },
        vm81_admit=inherited_vm81,
    )
    assert len(calls) == 1
    assert result["singleton_vm81_authority_preserved"] is True
    assert result["hash72_mutation_authority"] is False
    assert result["hash216_mutation_authority"] is False
    assert len(result["receipt_hash72"]) == 72
    assert len(result["archive_hash216"]) == 216
    return {
        "ok": True,
        "singleton_vm81_promotion_only": True,
        "hash72_execution_evidence_only": True,
        "hash216_archival_only": True,
        "independent_vm81_authority": False,
        "independent_hash72_clock": False,
        "hash216_mutation_authority": False,
    }


def validate_pass182_global_default_reachability() -> dict[str, Any]:
    contract = json.loads(_text("contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json"))
    census = contract["current_cumulative_binding_census"]
    if census["wired_floor_pass"] != 182 or census["binding_count"] != 39:
        raise RuntimeError(f"PASS182_GLOBAL_CENSUS_DRIFT:{census}")
    if census["ordered_bindings"][-4:] != ["185", "184", "183", "182"]:
        raise RuntimeError("PASS182_GLOBAL_CENSUS_TAIL_DRIFT")
    exact_h = _text("hhs_runtime/include/hhs_runtime_exact_abi.h")
    exact_c = _text("hhs_runtime/c/hhs_runtime_exact_abi.c")
    if exact_h.index("hhs_pass219_inherited_pass183_1_43.h") > exact_h.index("hhs_pass219_inherited_pass182_1_44.h"):
        raise RuntimeError("PASS182_HEADER_ORDER_DRIFT")
    if exact_c.index("hhs_pass219_inherited_pass183_1_43.inc") > exact_c.index("hhs_pass219_inherited_pass182_1_44.inc"):
        raise RuntimeError("PASS182_SOURCE_ORDER_DRIFT")
    return {
        "ok": True,
        "wired_floor": 182,
        "binding_count": 39,
        "global_defaults_mandatory": True,
        "multimodal_generalization_inherited": True,
    }


def validate_pass182_no_new_authority() -> dict[str, Any]:
    h = _text("hhs_runtime/include/hhs_pass219_inherited_pass182_1_44.h")
    hpp = _text("hhs_runtime/include/hhs_pass219_inherited_pass182_1_44.hpp")
    runtime = _text("hhs_runtime/pass182/runtime.py")
    required_false = (
        "independent_vm81_authority",
        "independent_hash72_authority",
        "hash216_mutation_authority",
        "floating_point_canonical_authority",
    )
    for token in required_false:
        if token not in h:
            raise RuntimeError(f"PASS182_NATIVE_AUTHORITY_FIELD_MISSING:{token}")
    if "hash72_clock_authority() noexcept { return false; }" not in hpp:
        raise RuntimeError("PASS182_CPP_HASH72_AUTHORITY_DRIFT")
    if '"direct_pass182_mutation_authority": False' not in runtime:
        raise RuntimeError("PASS182_RUNTIME_PROMOTION_AUTHORITY_DRIFT")
    return {
        "ok": True,
        "singleton_vm81_authority_remains_inherited": True,
        "independent_vm81_authority": False,
        "independent_hash72_clock": False,
        "hash216_mutation_authority": False,
        "floating_point_canonical_authority": False,
    }


def pass182_membrane_manifest() -> dict[str, Any]:
    return {
        "pass_number": 182,
        "iteration": 144,
        "contract_id": CONTRACT_ID,
        "classification": "WIRED_PENDING_EXECUTED_VALIDATION",
        "frozen_predecessor": FROZEN_I143,
        "aggregate_order_tail": [186, 185, 184, 183, 182],
        "terminal_completion_claimed": False,
        "merge_status": "UNMERGED",
        "authoritative_main_verification": False,
        "deployment_status": "NOT_PERFORMED",
    }


def execute_pass182_membrane_preflight() -> dict[str, Any]:
    checks = {
        "predecessor_and_contract": validate_pass182_predecessor_and_contract(),
        "runtime_surface": validate_pass182_runtime_surface(),
        "exact_hydration_cycle": validate_pass182_exact_hydration_cycle(),
        "vm81_promotion_boundary": validate_pass182_vm81_promotion_boundary(),
        "global_default_reachability": validate_pass182_global_default_reachability(),
        "no_new_authority": validate_pass182_no_new_authority(),
    }
    return {
        "ok": all(v.get("ok") is True for v in checks.values()),
        "classification": "HHS_PASS182_I144_DEPENDENCY_SCOPED_PREFLIGHT_VERIFIED",
        "manifest": pass182_membrane_manifest(),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(execute_pass182_membrane_preflight(), sort_keys=True, indent=2))
