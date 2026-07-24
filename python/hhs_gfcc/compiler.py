from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence
import hashlib
import os
import platform
import re
import shutil
import subprocess

from .core import GFCCError, digest256, write_json


def _run(command: Sequence[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(list(command), cwd=cwd, text=True, capture_output=True)
    if completed.returncode != 0:
        raise GFCCError(
            "HHS_GFCC_BUILD_ERROR",
            "compiler",
            "invoke",
            "external tool failed",
            {"command": list(command), "stdout": completed.stdout, "stderr": completed.stderr, "returncode": completed.returncode},
        )
    return completed


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tool_identity(path: str, cwd: Path) -> dict[str, Any]:
    first = _run([path, "--version"], cwd=cwd)
    lines = (first.stdout or first.stderr).splitlines()
    return {"name": Path(path).name, "version": lines[0] if lines else "UNKNOWN"}


def compile_native(repo: Path) -> dict[str, Any]:
    cc = shutil.which(os.environ.get("CC", "cc"))
    ar = shutil.which(os.environ.get("AR", "ar"))
    if not cc or not ar:
        raise GFCCError("HHS_GFCC_BUILD_ERROR", "compiler", "compile_native", "required C compiler or archiver unavailable", {"cc": cc, "ar": ar})
    subsystem = repo / "native_projects" / "hhs_gfcc_pass152"
    build = subsystem / "build"
    dist = subsystem / "dist"
    build.mkdir(parents=True, exist_ok=True)
    dist.mkdir(parents=True, exist_ok=True)
    include = subsystem / "include"
    inherited_include = repo / "hhs_runtime" / "include"
    core_source = subsystem / "src" / "hhs_gfcc.c"
    hash_source = repo / "hhs_runtime" / "src" / "hhs_hash216.c"
    cli_source = subsystem / "src" / "hhs_gfcc_cli.c"
    test_source = subsystem / "tests" / "test_hhs_gfcc.c"
    required = [core_source, hash_source, cli_source, test_source, include / "hhs_gfcc.h"]
    missing = [path.as_posix() for path in required if not path.is_file()]
    if missing:
        raise GFCCError("HHS_GFCC_BUILD_ERROR", "compiler", "compile_native", "required source missing", {"missing": missing})
    flags = ["-std=c11", "-O2", "-fPIC", "-Wall", "-Wextra", "-Werror", f"-I{include}", f"-I{inherited_include}"]
    core_object = build / "hhs_gfcc.o"
    hash_object = build / "hhs_hash216.o"
    _run([cc, *flags, "-c", str(core_source), "-o", str(core_object)], cwd=repo)
    _run([cc, *flags, "-c", str(hash_source), "-o", str(hash_object)], cwd=repo)
    static_library = dist / "libhhs_gfcc.a"
    shared_library = dist / "libhhs_gfcc.so"
    cli_binary = dist / "hhs-gfcc"
    test_binary = dist / "test_hhs_gfcc"
    _run([ar, "rcs", str(static_library), str(core_object), str(hash_object)], cwd=repo)
    _run([cc, "-shared", str(core_object), str(hash_object), "-o", str(shared_library)], cwd=repo)
    link_flags = ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", f"-I{include}", f"-I{inherited_include}"]
    _run([cc, *link_flags, str(cli_source), str(core_object), str(hash_object), "-o", str(cli_binary)], cwd=repo)
    _run([cc, *link_flags, str(test_source), str(core_object), str(hash_object), "-o", str(test_binary)], cwd=repo)
    test_run = _run([str(test_binary)], cwd=repo)
    cli_run = _run([str(cli_binary)], cwd=repo)
    target = _run([cc, "-dumpmachine"], cwd=repo).stdout.strip()
    artifacts = [
        {"path": path.relative_to(repo).as_posix(), "size": path.stat().st_size, "sha256": _sha256(path)}
        for path in (static_library, shared_library, cli_binary, test_binary)
    ]
    manifest = {
        "schema": "HHS_GFCC_NATIVE_BUILD_MANIFEST_V1",
        "compiler": _tool_identity(cc, repo),
        "archiver": _tool_identity(ar, repo),
        "target_triple": target,
        "architecture": platform.machine(),
        "optimization_flags": ["-std=c11", "-O2", "-fPIC", "-Wall", "-Wextra", "-Werror"],
        "include_paths": [include.relative_to(repo).as_posix(), inherited_include.relative_to(repo).as_posix()],
        "macro_definitions": [],
        "source_files": [path.relative_to(repo).as_posix() for path in (core_source, hash_source, cli_source, test_source)],
        "linked_libraries": [],
        "artifacts": artifacts,
        "native_test_stdout": test_run.stdout.strip(),
        "native_cli_stdout": cli_run.stdout.strip(),
        "native_test_reached": "GOLDEN_FRACTAL_CORRESPONDENCE_NATIVE_CORE_PASSED" in test_run.stdout,
    }
    manifest["build_identity"] = digest256(manifest)
    write_json(subsystem / "manifest" / "build_manifest.json", manifest)
    return manifest


_EXPECTED_MEMBERS = [
    "phi_projection", "inverse_sqrt2_projection", "scale_projection", "time_projection",
    "fibonacci_n", "nonary_phase", "vm81_cell", "hash72_index", "hash216_index",
    "shell_depth", "orientation", "constraint_flags",
]
_EXPECTED_OFFSETS = [index * 4 for index in range(len(_EXPECTED_MEMBERS))]


def _reflect_spirv(disassembler: str, artifact: Path, output: Path, repo: Path) -> dict[str, Any]:
    _run([disassembler, str(artifact), "-o", str(output)], cwd=repo)
    text = output.read_text(encoding="utf-8")
    member_names: dict[int, str] = {}
    offsets: dict[int, int] = {}
    for line in text.splitlines():
        name_match = re.search(r'OpMemberName\s+%HHS_GFCC_Uniforms\s+(\d+)\s+"([^"]+)"', line)
        if name_match:
            member_names[int(name_match.group(1))] = name_match.group(2)
        offset_match = re.search(r'OpMemberDecorate\s+%HHS_GFCC_Uniforms\s+(\d+)\s+Offset\s+(\d+)', line)
        if offset_match:
            offsets[int(offset_match.group(1))] = int(offset_match.group(2))
    ordered_names = [member_names.get(index) for index in range(len(_EXPECTED_MEMBERS))]
    ordered_offsets = [offsets.get(index) for index in range(len(_EXPECTED_OFFSETS))]
    valid = (
        ordered_names == _EXPECTED_MEMBERS
        and ordered_offsets == _EXPECTED_OFFSETS
        and "OpDecorate %HHS_GFCC_Uniforms Block" in text
        and "DescriptorSet 0" in text
        and "Binding 0" in text
    )
    if not valid:
        raise GFCCError(
            "HHS_GFCC_SHADER_COMPILATION_ERROR",
            "shader",
            "reflect",
            "compiled shader reflection layout mismatch",
            {"members": ordered_names, "offsets": ordered_offsets},
        )
    return {
        "block": "HHS_GFCC_Uniforms",
        "layout": "std140",
        "descriptor_set": 0,
        "binding": 0,
        "size_bytes": 48,
        "members": [
            {"index": index, "name": name, "offset": offset}
            for index, (name, offset) in enumerate(zip(ordered_names, ordered_offsets))
        ],
        "disassembly_sha256": _sha256(output),
    }


def compile_shaders(repo: Path) -> dict[str, Any]:
    compiler = shutil.which("glslangValidator")
    disassembler = shutil.which("spirv-dis")
    validator = shutil.which("spirv-val")
    if not compiler or not disassembler or not validator:
        raise GFCCError(
            "HHS_GFCC_SHADER_COMPILATION_ERROR",
            "shader",
            "compile",
            "required GLSL/SPIR-V tool unavailable",
            {"glslangValidator": compiler, "spirv-dis": disassembler, "spirv-val": validator},
        )
    subsystem = repo / "native_projects" / "hhs_gfcc_pass152"
    generated = subsystem / "generated" / "shaders"
    dist = subsystem / "dist"
    build = subsystem / "build" / "shader"
    dist.mkdir(parents=True, exist_ok=True)
    build.mkdir(parents=True, exist_ok=True)
    shaders = [
        (generated / "hhs_gfcc_fragment.glsl", "frag", dist / "hhs_gfcc_shader.spv"),
        (generated / "hhs_gfcc_collision_field.glsl", "comp", dist / "hhs_gfcc_collision_field.spv"),
    ]
    records = []
    for source, stage, output in shaders:
        if not source.is_file():
            raise GFCCError("HHS_GFCC_SHADER_GENERATION_ERROR", "shader", "compile", "generated shader source missing", {"source": source.as_posix()})
        completed = _run([compiler, "-V", "--target-env", "vulkan1.1", "-S", stage, str(source), "-o", str(output)], cwd=repo)
        _run([validator, str(output)], cwd=repo)
        if output.stat().st_size < 20 or output.read_bytes()[:4] != bytes.fromhex("03022307"):
            raise GFCCError("HHS_GFCC_SHADER_COMPILATION_ERROR", "shader", "compile", "invalid SPIR-V artifact", {"output": output.as_posix()})
        disassembly = build / f"{output.name}.spvasm"
        reflection = _reflect_spirv(disassembler, output, disassembly, repo)
        records.append(
            {
                "stage": stage,
                "source": source.relative_to(repo).as_posix(),
                "source_sha256": _sha256(source),
                "artifact": output.relative_to(repo).as_posix(),
                "artifact_size": output.stat().st_size,
                "artifact_sha256": _sha256(output),
                "compiler_output": (completed.stdout + completed.stderr).strip(),
                "reflection": reflection,
            }
        )
    manifest = {
        "schema": "HHS_GFCC_SHADER_BUILD_MANIFEST_V1",
        "compiler": _tool_identity(compiler, repo),
        "validator": _tool_identity(validator, repo),
        "disassembler": _tool_identity(disassembler, repo),
        "target_environment": "vulkan1.1",
        "optimization_flags": [],
        "uniform_layout": records[0]["reflection"],
        "descriptor_bindings": [{"set": 0, "binding": 0, "block": "HHS_GFCC_Uniforms"}],
        "records": records,
        "shader_authority": "PROJECTED_RENDERING_ONLY",
        "reflection_validated": all(record["reflection"]["size_bytes"] == 48 for record in records),
    }
    manifest["build_identity"] = digest256(manifest)
    write_json(subsystem / "manifest" / "shader_manifest.json", manifest)
    return manifest


__all__ = ["compile_native", "compile_shaders"]
