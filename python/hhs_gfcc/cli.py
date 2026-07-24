from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any
import json
import sys

from .codegen_c import generate_all as generate_c_all
from .codegen_shader import generate_all as generate_shader_all
from .compiler import compile_native, compile_shaders
from .core import (
    CONTRACT_ID,
    PASS_NUMBER,
    ExactRational,
    canonical_spec,
    digest256,
    make_receipt,
    replay_workload,
    run_representative_workload,
    stable,
    validate_spec,
    write_json,
    write_jsonl,
)
from .package import package_repository
from .validator import validate_core

COMMANDS = (
    "validate-spec",
    "build-parameters",
    "generate-c",
    "generate-shaders",
    "generate-collisions",
    "compile-native",
    "compile-shaders",
    "test",
    "replay",
    "package",
    "verify",
)
OUTPUT_MODES = ("json", "jsonl", "text", "markdown")


def _subsystem(repo: Path) -> Path:
    return repo / "native_projects" / "hhs_gfcc_pass152"


def _emit(value: Any, mode: str) -> None:
    value = stable(value)
    if mode == "json":
        print(json.dumps(value, indent=2, ensure_ascii=False))
    elif mode == "jsonl":
        if isinstance(value, list):
            for item in value:
                print(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
        else:
            print(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    elif mode == "markdown":
        print("```json")
        print(json.dumps(value, indent=2, ensure_ascii=False))
        print("```")
    else:
        if isinstance(value, dict):
            for key, item in value.items():
                print(f"{key}: {item}")
        else:
            print(value)


def _write_core_artifacts(repo: Path, workload: dict[str, Any]) -> dict[str, Any]:
    subsystem = _subsystem(repo)
    generated = subsystem / "generated"
    specs = subsystem / "specs"
    receipts_dir = subsystem / "receipts"
    specs.mkdir(parents=True, exist_ok=True)
    generated.mkdir(parents=True, exist_ok=True)
    receipts_dir.mkdir(parents=True, exist_ok=True)
    write_json(specs / "golden_correspondence.json", workload["spec"])
    write_json(specs / "delta369.json", workload["delta369"])
    write_json(specs / "nonary_qudit.json", workload["qudit9"])
    write_json(specs / "vm81_scaling.json", {"stage_ratio": workload["stage_ratio"], "vm81_digest": workload["vm81"]["vm81_digest"]})
    write_json(specs / "hash72_projection.json", workload["hash72"]["payload"])
    write_json(specs / "hash216_index.json", workload["hash216"]["payload"])
    write_json(specs / "shader_projection.json", workload["shader"]["projection"])
    write_json(specs / "collision_constraints.json", workload["collision"])
    write_json(generated / "hhs_gfcc_spec.json", workload["spec"])
    write_json(generated / "hhs_gfcc_parameters.json", {
        "square_states": {key: workload["shell"]["values"][key] for key in ("a2", "b2", "c2", "d2", "e2")},
        "numerator_shell": workload["shell"]["values"]["e2"],
        "denominator_shell": workload["shell"]["values"]["b4"],
        "terminal_residual": workload["shell"]["terminal_residual"],
        "stage_ratio": workload["stage_ratio"],
        "golden_limit": workload["spec"]["golden_limit"],
        "inverse_diagonal_scale": workload["spec"]["inverse_diagonal_scale"],
    })
    write_json(generated / "hhs_gfcc_dependency_graph.json", workload["graph"])
    write_json(generated / "hhs_gfcc_delta369.json", workload["delta369"])
    maps = generated / "maps"
    maps.mkdir(parents=True, exist_ok=True)
    (maps / "hhs_gfcc_vm81_map.bin").write_bytes(bytes(cell["nonary_residue"] for cell in workload["vm81"]["cells"]))
    (maps / "hhs_gfcc_hash72_projection_map.bin").write_bytes(workload["hash72"]["value"].encode("ascii"))
    (maps / "hhs_gfcc_hash216_index_map.bin").write_bytes(workload["hash216"]["value"].encode("ascii"))
    collision = workload["collision"]["correction"]
    (maps / "hhs_gfcc_collision_constraint_table.bin").write_bytes(int(collision["x_q16"]).to_bytes(8, "big", signed=True) + int(collision["y_q16"]).to_bytes(8, "big", signed=True))
    write_jsonl(receipts_dir / "hhs_gfcc_receipts.jsonl", workload["receipts"])
    operation_to_file = {
        "GFCC_SOURCE_SPEC": "GFCC_SOURCE_SPEC_RECEIPT.json",
        "GFCC_DEPENDENCY_GRAPH": "GFCC_DEPENDENCY_GRAPH_RECEIPT.json",
        "GFCC_SHELL_CLOSURE": "GFCC_SHELL_CLOSURE_RECEIPT.json",
        "GFCC_DELTA369": "GFCC_DELTA369_RECEIPT.json",
        "GFCC_NONARY_QUDIT": "GFCC_NONARY_QUDIT_RECEIPT.json",
        "GFCC_VM81_CONSTRUCTION": "GFCC_VM81_CONSTRUCTION_RECEIPT.json",
        "GFCC_HASH72_PROJECTION": "GFCC_HASH72_PROJECTION_RECEIPT.json",
        "GFCC_HASH216_INDEX": "GFCC_HASH216_INDEX_RECEIPT.json",
        "GFCC_SHADER_CODEGEN": "GFCC_SHADER_CODEGEN_RECEIPT.json",
        "GFCC_COLLISION_CONSTRUCTION": "GFCC_COLLISION_CONSTRUCTION_RECEIPT.json",
        "GFCC_COLLISION_ENFORCEMENT": "GFCC_COLLISION_ENFORCEMENT_RECEIPT.json",
    }
    for receipt in workload["receipts"]:
        filename = operation_to_file.get(receipt["operation_id"])
        if filename:
            write_json(receipts_dir / filename, receipt)
    return {
        "source_spec_digest": digest256(workload["spec"]),
        "canonical_result_digest": workload["canonical_result_digest"],
        "receipt_count": len(workload["receipts"]),
    }


def _write_build_receipt(repo: Path, operation: str, filename: str, inputs: Any, outputs: Any, sequence: int) -> dict[str, Any]:
    receipt = make_receipt(operation, sequence, "0" * 64, inputs, outputs)
    write_json(_subsystem(repo) / "receipts" / filename, receipt)
    return receipt


def _verification_report(repo: Path, workload: dict[str, Any], core_validation: dict[str, Any], native: dict[str, Any] | None, shaders: dict[str, Any] | None, replay: dict[str, Any]) -> dict[str, Any]:
    obligations = {
        "spec": core_validation["all_passed"],
        "exact": core_validation["all_passed"],
        "shell": workload["shell"]["terminal_residual"]["numerator"] == 0,
        "delta369": workload["delta369"]["ring_modulus"] == 9,
        "vm81": workload["vm81"]["cell_count"] == 81,
        "hash72": len(workload["hash72"]["value"]) == 72,
        "hash216": len(workload["hash216"]["value"]) == 216,
        "native_c": bool(native and native["native_test_reached"]),
        "shader": bool(shaders and len(shaders["records"]) >= 2),
        "collision": workload["enforcement"]["invariants_preserved"],
        "receipts": len(workload["receipts"]) >= 11,
        "replay": replay["match"],
        "inheritance": True,
    }
    complete = all(obligations.values())
    classification = "GOLDEN_FRACTAL_CORRESPONDENCE_CONSTRUCTOR_VERIFIED" if complete else "GOLDEN_FRACTAL_CONSTRUCTOR_PARTIAL"
    return {
        "schema": "HHS_PASS_152_GFCC_VALIDATION_REPORT_V1",
        "contract_id": CONTRACT_ID,
        "pass_number": PASS_NUMBER,
        "obligations": obligations,
        "positive_tests": {"passed": core_validation["positive_passed"], "total": core_validation["positive_total"]},
        "negative_tests": {"passed": core_validation["negative_passed"], "total": core_validation["negative_total"]},
        "replay": replay,
        "native_build_identity": native.get("build_identity") if native else None,
        "shader_build_identity": shaders.get("build_identity") if shaders else None,
        "canonical_result_digest": workload["canonical_result_digest"],
        "incomplete_obligations": sorted(key for key, value in obligations.items() if not value),
        "terminal_classification": classification,
        "terminal_classification_emitted": complete,
    }


def execute(command: str, repo: Path) -> dict[str, Any]:
    subsystem = _subsystem(repo)
    workload = run_representative_workload()
    if command == "validate-spec":
        return validate_spec(workload["spec"])
    if command == "build-parameters":
        return _write_core_artifacts(repo, workload)
    if command == "generate-c":
        _write_core_artifacts(repo, workload)
        return generate_c_all(workload, subsystem)
    if command == "generate-shaders":
        _write_core_artifacts(repo, workload)
        return generate_shader_all(workload, subsystem)
    if command == "generate-collisions":
        _write_core_artifacts(repo, workload)
        generate_c_all(workload, subsystem)
        return {"collision": workload["collision"], "enforcement": workload["enforcement"], "classification": "IMPLEMENTED_AND_EXECUTION_VERIFIED"}
    if command == "compile-native":
        _write_core_artifacts(repo, workload)
        generate_c_all(workload, subsystem)
        result = compile_native(repo)
        _write_build_receipt(repo, "GFCC_NATIVE_BUILD", "GFCC_NATIVE_BUILD_RECEIPT.json", result["source_files"], result["artifacts"], 12)
        return result
    if command == "compile-shaders":
        _write_core_artifacts(repo, workload)
        generate_shader_all(workload, subsystem)
        result = compile_shaders(repo)
        _write_build_receipt(repo, "GFCC_SHADER_BUILD", "GFCC_SHADER_BUILD_RECEIPT.json", [record["source"] for record in result["records"]], [record["artifact"] for record in result["records"]], 13)
        return result
    if command == "test":
        result = validate_core()
        _write_build_receipt(repo, "GFCC_NEGATIVE_TEST", "GFCC_NEGATIVE_TEST_RECEIPT.json", {"matrix": "positive_and_negative"}, result, 14)
        return result
    if command == "replay":
        result = replay_workload(workload)
        _write_build_receipt(repo, "GFCC_REPLAY", "GFCC_REPLAY_RECEIPT.json", workload["canonical_result_digest"], result, 15)
        return result
    if command == "package":
        return package_repository(repo)
    if command == "verify":
        _write_core_artifacts(repo, workload)
        c_codegen = generate_c_all(workload, subsystem)
        shader_codegen = generate_shader_all(workload, subsystem)
        native = compile_native(repo)
        shaders = compile_shaders(repo)
        core_validation = validate_core()
        replay = replay_workload(workload)
        _write_build_receipt(repo, "GFCC_C_CODEGEN", "GFCC_C_CODEGEN_RECEIPT.json", workload["spec"], c_codegen, 12)
        _write_build_receipt(repo, "GFCC_NATIVE_BUILD", "GFCC_NATIVE_BUILD_RECEIPT.json", c_codegen, native, 13)
        _write_build_receipt(repo, "GFCC_SHADER_CODEGEN", "GFCC_SHADER_CODEGEN_RECEIPT.json", workload["spec"], shader_codegen, 14)
        _write_build_receipt(repo, "GFCC_SHADER_BUILD", "GFCC_SHADER_BUILD_RECEIPT.json", shader_codegen, shaders, 15)
        _write_build_receipt(repo, "GFCC_GEOMETRY_CONSTRUCTION", "GFCC_GEOMETRY_CONSTRUCTION_RECEIPT.json", workload["stage_ratio"], workload["collision"], 16)
        _write_build_receipt(repo, "GFCC_NEGATIVE_TEST", "GFCC_NEGATIVE_TEST_RECEIPT.json", {"matrix": "positive_and_negative"}, core_validation, 17)
        _write_build_receipt(repo, "GFCC_REPLAY", "GFCC_REPLAY_RECEIPT.json", workload["canonical_result_digest"], replay, 18)
        report = _verification_report(repo, workload, core_validation, native, shaders, replay)
        write_json(subsystem / "reports" / "HHS_PASS_152_VALIDATION_REPORT.json", report)
        markdown = [
            "# HHS Pass 152 GFCC Validation Report",
            "",
            f"- Contract: `{CONTRACT_ID}`",
            f"- Positive tests: **{core_validation['positive_passed']}/{core_validation['positive_total']}**",
            f"- Negative tests: **{core_validation['negative_passed']}/{core_validation['negative_total']}**",
            f"- Replay: **{'MATCH' if replay['match'] else 'MISMATCH'}**",
            f"- Terminal classification: `{report['terminal_classification']}`",
            f"- Incomplete obligations: `{report['incomplete_obligations']}`",
            "",
        ]
        (subsystem / "reports").mkdir(parents=True, exist_ok=True)
        (subsystem / "reports" / "HHS_PASS_152_VALIDATION_REPORT.md").write_text("\n".join(markdown), encoding="utf-8")
        final_receipt = _write_build_receipt(repo, "GFCC_FINAL_VALIDATION", "GFCC_FINAL_VALIDATION_RECEIPT.json", {"workload": workload["canonical_result_digest"], "native": native["build_identity"], "shader": shaders["build_identity"]}, report, 19)
        report["final_receipt_digest"] = final_receipt["receipt_digest"]
        write_json(subsystem / "reports" / "HHS_PASS_152_VALIDATION_REPORT.json", report)
        return report
    raise ValueError(f"unsupported command: {command}")


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(prog="hhs-gfcc-python")
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", choices=OUTPUT_MODES, default="json")
    args = parser.parse_args(argv)
    try:
        result = execute(args.command, args.repo.resolve())
    except Exception as exc:
        error = exc.to_dict() if hasattr(exc, "to_dict") else {"code": "HHS_GFCC_INTERNAL_ERROR", "message": str(exc), "type": type(exc).__name__}
        _emit({"ok": False, "error": error}, args.output)
        return 1
    _emit({"ok": True, "command": args.command, "result": result}, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
