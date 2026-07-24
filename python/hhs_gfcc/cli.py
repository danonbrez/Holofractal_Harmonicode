from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Mapping
import json

from .codegen_c import generate_all as generate_c_all
from .codegen_shader import generate_all as generate_shader_all
from .compiler import compile_native, compile_shaders
from .core import (
    CONTRACT_ID,
    PASS_NUMBER,
    ExactRational,
    canonical_bytes,
    digest256,
    inherited_hash72,
    make_receipt,
    replay_workload,
    run_representative_workload,
    stable,
    validate_spec,
    write_json,
    write_jsonl,
)
from .geometry import build_transform
from .manifest import (
    REQUIRED_RECEIPTS,
    audit_receipt_set,
    build_artifact_manifest,
    build_repository_manifest,
    build_source_manifest,
    validate_archive,
    validate_inherited_pass152,
    validate_source_manifest,
)
from .package import ARCHIVE_NAME, package_repository
from .schema import load_canonical_spec
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
VERIFIED = "GOLDEN_FRACTAL_CORRESPONDENCE_CONSTRUCTOR_VERIFIED"
PARTIAL = "GOLDEN_FRACTAL_CONSTRUCTOR_PARTIAL"


def _subsystem(repo: Path) -> Path:
    return repo / "native_projects" / "hhs_gfcc_pass152"


def _emit(value: Any, mode: str) -> None:
    value = stable(value)
    if mode == "json":
        print(json.dumps(value, indent=2, ensure_ascii=False))
    elif mode == "jsonl":
        values = value if isinstance(value, list) else [value]
        for item in values:
            print(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    elif mode == "markdown":
        print("```json")
        print(json.dumps(value, indent=2, ensure_ascii=False))
        print("```")
    elif isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {item}")
    else:
        print(value)


def _load_workload(repo: Path) -> dict[str, Any]:
    loaded = load_canonical_spec(repo)
    workload = run_representative_workload()
    if workload["spec"] != loaded:
        raise ValueError("HHS_GFCC_INVALID_SPEC:file-ingested specification differs from executed specification")
    return workload


def _write_core_artifacts(repo: Path, workload: Mapping[str, Any]) -> dict[str, Any]:
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
    write_json(
        generated / "hhs_gfcc_parameters.json",
        {
            "square_states": {key: workload["shell"]["values"][key] for key in ("a2", "b2", "c2", "d2", "e2")},
            "numerator_shell": workload["shell"]["values"]["e2"],
            "denominator_shell": workload["shell"]["values"]["b4"],
            "terminal_residual": workload["shell"]["terminal_residual"],
            "stage_ratio": workload["stage_ratio"],
            "golden_limit": workload["spec"]["golden_limit"],
            "inverse_diagonal_scale": workload["spec"]["inverse_diagonal_scale"],
        },
    )
    write_json(generated / "hhs_gfcc_dependency_graph.json", workload["graph"])
    write_json(generated / "hhs_gfcc_delta369.json", workload["delta369"])
    maps = generated / "maps"
    maps.mkdir(parents=True, exist_ok=True)
    (maps / "hhs_gfcc_vm81_map.bin").write_bytes(bytes(cell["nonary_residue"] for cell in workload["vm81"]["cells"]))
    (maps / "hhs_gfcc_hash72_projection_map.bin").write_bytes(workload["hash72"]["value"].encode("ascii"))
    (maps / "hhs_gfcc_hash216_index_map.bin").write_bytes(workload["hash216"]["value"].encode("ascii"))
    correction = workload["collision"]["correction"]
    (maps / "hhs_gfcc_collision_constraint_table.bin").write_bytes(
        int(correction["x_q16"]).to_bytes(8, "big", signed=True)
        + int(correction["y_q16"]).to_bytes(8, "big", signed=True)
    )
    return {
        "source_spec_digest": digest256(workload["spec"]),
        "canonical_result_digest": workload["canonical_result_digest"],
    }


def _bound_receipt(
    operation_id: str,
    sequence: int,
    predecessor: str,
    inputs: Any,
    outputs: Any,
    *,
    build_identity: str,
    replay_identity: str,
) -> dict[str, Any]:
    receipt = make_receipt(operation_id, sequence, predecessor, inputs, outputs)
    receipt["build_identity"] = build_identity
    receipt["replay_identity"] = replay_identity
    base = {key: value for key, value in receipt.items() if key not in {"hash72_witness", "receipt_digest"}}
    receipt["hash72_witness"] = inherited_hash72(canonical_bytes(base))
    receipt["receipt_digest"] = digest256({**base, "hash72_witness": receipt["hash72_witness"]})
    return stable(receipt)


def _write_receipt_ledger(
    repo: Path,
    workload: Mapping[str, Any],
    c_codegen: Mapping[str, Any],
    native: Mapping[str, Any],
    shader_codegen: Mapping[str, Any],
    shaders: Mapping[str, Any],
    geometry: Mapping[str, Any],
    core_validation: Mapping[str, Any],
    replay: Mapping[str, Any],
    report: Mapping[str, Any],
) -> dict[str, Any]:
    operations = [
        ("GFCC_SOURCE_SPEC", workload["spec"], validate_spec(workload["spec"])),
        ("GFCC_DEPENDENCY_GRAPH", workload["spec"], workload["graph"]),
        ("GFCC_SHELL_CLOSURE", workload["graph"], workload["shell"]),
        ("GFCC_DELTA369", workload["spec"]["delta369"], workload["delta369"]),
        ("GFCC_NONARY_QUDIT", workload["delta369"], workload["qudit9"]),
        ("GFCC_VM81_CONSTRUCTION", workload["qudit9"], workload["vm81"]),
        ("GFCC_HASH72_PROJECTION", workload["vm81"], workload["hash72"]),
        ("GFCC_HASH216_INDEX", workload["hash72"], workload["hash216"]),
        ("GFCC_C_CODEGEN", workload["spec"], c_codegen),
        ("GFCC_NATIVE_BUILD", c_codegen, native),
        ("GFCC_SHADER_CODEGEN", workload["spec"], shader_codegen),
        ("GFCC_SHADER_BUILD", shader_codegen, shaders),
        ("GFCC_GEOMETRY_CONSTRUCTION", workload["stage_ratio"], geometry),
        ("GFCC_COLLISION_CONSTRUCTION", workload["hash216"], workload["collision"]),
        ("GFCC_COLLISION_ENFORCEMENT", workload["collision"], workload["enforcement"]),
        ("GFCC_NEGATIVE_TEST", {"required_cases": 25}, core_validation),
        ("GFCC_REPLAY", workload["canonical_result_digest"], replay),
        ("GFCC_FINAL_VALIDATION", {"native": native["build_identity"], "shader": shaders["build_identity"]}, report),
    ]
    if len(operations) != len(REQUIRED_RECEIPTS):
        raise AssertionError("receipt operation count differs from required receipt set")
    receipts = []
    predecessor = "0" * 64
    for sequence, (operation, inputs, outputs) in enumerate(operations, start=1):
        receipt = _bound_receipt(
            operation,
            sequence,
            predecessor,
            inputs,
            outputs,
            build_identity=str(native["build_identity"]),
            replay_identity=str(workload["canonical_result_digest"]),
        )
        receipts.append(receipt)
        predecessor = receipt["receipt_digest"]
    receipts_dir = _subsystem(repo) / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(receipts_dir / "hhs_gfcc_receipts.jsonl", receipts)
    for filename, receipt in zip(REQUIRED_RECEIPTS, receipts):
        write_json(receipts_dir / filename, receipt)
    return audit_receipt_set(receipts_dir)


def _base_obligations(
    workload: Mapping[str, Any],
    core_validation: Mapping[str, Any],
    native: Mapping[str, Any],
    shaders: Mapping[str, Any],
    replay: Mapping[str, Any],
    inheritance: Mapping[str, Any],
    source_validation: Mapping[str, Any],
) -> dict[str, bool]:
    return {
        "inheritance": bool(inheritance.get("valid")),
        "spec": validate_spec(workload["spec"])["valid"],
        "exact": core_validation["positive_passed"] == 23,
        "shell": workload["shell"]["terminal_residual"] == {"numerator": 0, "denominator": 1},
        "delta369": workload["delta369"]["ring_modulus"] == 9 and workload["delta369"]["coordinate_dimensions"] == 4,
        "vm81": workload["vm81"]["cell_count"] == 81,
        "hash72": len(workload["hash72"]["value"]) == 72,
        "hash216": len(workload["hash216"]["value"]) == 216,
        "native_c": bool(native.get("native_test_reached")),
        "shader": bool(shaders.get("reflection_validated")) and len(shaders.get("records", [])) == 2,
        "collision": bool(workload["enforcement"]["invariants_preserved"]),
        "negative_tests": core_validation["negative_passed"] == 25,
        "replay": bool(replay.get("match")),
        "source_manifest": bool(source_validation.get("valid")),
    }


def _report(
    workload: Mapping[str, Any],
    core_validation: Mapping[str, Any],
    native: Mapping[str, Any],
    shaders: Mapping[str, Any],
    inheritance: Mapping[str, Any],
    source_validation: Mapping[str, Any],
    obligations: Mapping[str, bool],
    *,
    archive_basis: Mapping[str, Any] | None,
) -> dict[str, Any]:
    complete = all(obligations.values())
    return stable(
        {
            "schema": "HHS_PASS_152_GFCC_VALIDATION_REPORT_V1",
            "contract_id": CONTRACT_ID,
            "pass_number": PASS_NUMBER,
            "repository_classification": "COMPLETE_INHERITED_PASS_HISTORY_NUCLEUS",
            "obligations": dict(obligations),
            "obligation_classifications": {
                key: "IMPLEMENTED_AND_EXECUTION_VERIFIED" if value else "IMPLEMENTED_VALIDATION_FAILED"
                for key, value in obligations.items()
            },
            "positive_tests": {"passed": core_validation["positive_passed"], "total": core_validation["positive_total"]},
            "negative_tests": {"passed": core_validation["negative_passed"], "total": core_validation["negative_total"]},
            "replay": "MATCH" if obligations["replay"] else "MISMATCH",
            "native_build_identity": native.get("build_identity"),
            "shader_build_identity": shaders.get("build_identity"),
            "shader_reflection_validated": shaders.get("reflection_validated"),
            "canonical_result_digest": workload["canonical_result_digest"],
            "inherited_evidence_digest": inheritance.get("evidence_digest"),
            "source_manifest_result": source_validation,
            "archive_validation_basis": archive_basis,
            "incomplete_obligations": sorted(key for key, value in obligations.items() if not value),
            "terminal_classification": VERIFIED if complete else PARTIAL,
            "terminal_classification_emitted": complete,
        }
    )


def _write_report(repo: Path, report: Mapping[str, Any]) -> None:
    reports = _subsystem(repo) / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    write_json(reports / "HHS_PASS_152_VALIDATION_REPORT.json", report)
    lines = [
        "# HHS Pass 152 GFCC Validation Report",
        "",
        f"- Contract: `{CONTRACT_ID}`",
        f"- Positive tests: **{report['positive_tests']['passed']}/{report['positive_tests']['total']}**",
        f"- Negative tests: **{report['negative_tests']['passed']}/{report['negative_tests']['total']}**",
        f"- Replay: **{report['replay']}**",
        f"- Terminal classification: `{report['terminal_classification']}`",
        f"- Incomplete obligations: `{report['incomplete_obligations']}`",
        "",
    ]
    (reports / "HHS_PASS_152_VALIDATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _clear_derived_manifests(repo: Path) -> None:
    manifest_dir = _subsystem(repo) / "manifest"
    for name in (
        "inherited_pass152_evidence.json",
        "source_manifest.json",
        "source_manifest_validation.json",
        "repository_manifest.json",
        "artifact_manifest.json",
        "archive_manifest.json",
    ):
        path = manifest_dir / name
        if path.exists():
            path.unlink()
    root_artifact = _subsystem(repo) / "HHS_PASS_152_ARTIFACT_MANIFEST.json"
    if root_artifact.exists():
        root_artifact.unlink()


def _execute_full(
    repo: Path,
    *,
    archive_valid: bool,
    archive_basis: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    subsystem = _subsystem(repo)
    _clear_derived_manifests(repo)
    workload = _load_workload(repo)
    _write_core_artifacts(repo, workload)
    c_codegen = generate_c_all(workload, subsystem)
    shader_codegen = generate_shader_all(workload, subsystem)
    native = compile_native(repo)
    shaders = compile_shaders(repo)
    core_validation = validate_core()
    replay = replay_workload(workload)
    inheritance = validate_inherited_pass152(repo)
    source_manifest = build_source_manifest(repo)
    source_validation = validate_source_manifest(repo, source_manifest)
    geometry = build_transform(
        x_q16=3 * 65536,
        y_q16=4 * 65536,
        stage_ratio=ExactRational(workload["stage_ratio"]["numerator"], workload["stage_ratio"]["denominator"]),
        phase=9,
        shell_depth=3,
    )
    manifest_dir = subsystem / "manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    write_json(manifest_dir / "generated_manifest.json", {"c": c_codegen, "shader": shader_codegen})
    write_json(manifest_dir / "test_manifest.json", core_validation)

    obligations = _base_obligations(workload, core_validation, native, shaders, replay, inheritance, source_validation)
    obligations.update({"receipts": True, "artifacts": True, "archive": archive_valid})
    provisional = _report(workload, core_validation, native, shaders, inheritance, source_validation, obligations, archive_basis=archive_basis)
    _write_report(repo, provisional)
    receipt_audit = _write_receipt_ledger(repo, workload, c_codegen, native, shader_codegen, shaders, geometry, core_validation, replay, provisional)
    obligations["receipts"] = bool(receipt_audit.get("valid"))
    current = _report(workload, core_validation, native, shaders, inheritance, source_validation, obligations, archive_basis=archive_basis)
    _write_report(repo, current)
    receipt_audit = _write_receipt_ledger(repo, workload, c_codegen, native, shader_codegen, shaders, geometry, core_validation, replay, current)
    obligations["receipts"] = bool(receipt_audit.get("valid"))
    artifact_manifest = build_artifact_manifest(subsystem)
    obligations["artifacts"] = bool(artifact_manifest.get("valid"))
    final_report = _report(workload, core_validation, native, shaders, inheritance, source_validation, obligations, archive_basis=archive_basis)
    _write_report(repo, final_report)
    receipt_audit = _write_receipt_ledger(repo, workload, c_codegen, native, shader_codegen, shaders, geometry, core_validation, replay, final_report)
    obligations["receipts"] = bool(receipt_audit.get("valid"))
    final_report = _report(workload, core_validation, native, shaders, inheritance, source_validation, obligations, archive_basis=archive_basis)
    _write_report(repo, final_report)
    artifact_manifest = build_artifact_manifest(subsystem)
    obligations["artifacts"] = bool(artifact_manifest.get("valid"))
    if obligations != final_report["obligations"]:
        final_report = _report(workload, core_validation, native, shaders, inheritance, source_validation, obligations, archive_basis=archive_basis)
        _write_report(repo, final_report)
        receipt_audit = _write_receipt_ledger(repo, workload, c_codegen, native, shader_codegen, shaders, geometry, core_validation, replay, final_report)
        artifact_manifest = build_artifact_manifest(subsystem)

    repository_manifest = build_repository_manifest(repo)
    write_json(manifest_dir / "inherited_pass152_evidence.json", inheritance)
    write_json(manifest_dir / "source_manifest.json", source_manifest)
    write_json(manifest_dir / "source_manifest_validation.json", source_validation)
    write_json(manifest_dir / "repository_manifest.json", repository_manifest)
    write_json(manifest_dir / "artifact_manifest.json", artifact_manifest)
    write_json(subsystem / "HHS_PASS_152_ARTIFACT_MANIFEST.json", artifact_manifest)
    return {
        "report": final_report,
        "workload": workload,
        "native": native,
        "shaders": shaders,
        "core_validation": core_validation,
        "receipt_audit": receipt_audit,
        "artifact_manifest": artifact_manifest,
        "repository_manifest": repository_manifest,
        "source_manifest_validation": source_validation,
        "inheritance": inheritance,
    }


def _existing_archive_validation(repo: Path) -> dict[str, Any]:
    archive = _subsystem(repo) / "dist" / ARCHIVE_NAME
    return validate_archive(
        archive,
        required_paths=(
            "native_projects/hhs_gfcc_pass152/reports/HHS_PASS_152_VALIDATION_REPORT.json",
            "native_projects/hhs_gfcc_pass152/receipts/GFCC_FINAL_VALIDATION_RECEIPT.json",
            "native_projects/hhs_gfcc_pass152/dist/libhhs_gfcc.a",
            "native_projects/hhs_gfcc_pass152/dist/hhs_gfcc_shader.spv",
        ),
        expected_repository_file_minimum=3275,
    )


def execute(command: str, repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    subsystem = _subsystem(repo)
    workload = _load_workload(repo)
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
        return compile_native(repo)
    if command == "compile-shaders":
        _write_core_artifacts(repo, workload)
        generate_shader_all(workload, subsystem)
        return compile_shaders(repo)
    if command == "test":
        return validate_core()
    if command == "replay":
        return replay_workload(workload)
    if command == "verify":
        archive_validation = _existing_archive_validation(repo)
        result = _execute_full(repo, archive_valid=bool(archive_validation.get("valid")), archive_basis=archive_validation if archive_validation.get("valid") else None)
        result["archive"] = archive_validation
        return result
    if command == "package":
        prepackage = _execute_full(repo, archive_valid=False)
        remaining = prepackage["report"]["incomplete_obligations"]
        if remaining != ["archive"]:
            raise ValueError(f"HHS_GFCC_BUILD_ERROR:package blocked by obligations:{remaining}")
        candidate = package_repository(repo, require_verified_report=False)
        archive_path = subsystem / "dist" / ARCHIVE_NAME
        external_manifest = subsystem / "manifest" / "archive_manifest.json"
        archive_path.unlink(missing_ok=True)
        external_manifest.unlink(missing_ok=True)
        promoted = _execute_full(repo, archive_valid=bool(candidate.get("valid")), archive_basis=candidate.get("archive_validation"))
        if promoted["report"]["terminal_classification"] != VERIFIED:
            raise ValueError(f"HHS_GFCC_BUILD_ERROR:promotion failed:{promoted['report']['incomplete_obligations']}")
        final_archive = package_repository(repo, require_verified_report=True)
        if not final_archive.get("valid"):
            raise ValueError("HHS_GFCC_BUILD_ERROR:final archive validation failed")
        return {**promoted, "archive": final_archive}
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
        error = exc.to_dict() if hasattr(exc, "to_dict") else {"code": "HHS_GFCC_INTERNAL_ERROR", "message": str(exc)}
        _emit({"ok": False, "command": args.command, "error": error}, args.output)
        return 1
    _emit({"ok": True, "command": args.command, "result": result}, args.output)
    if args.command == "verify" and result["report"]["terminal_classification"] != VERIFIED:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
