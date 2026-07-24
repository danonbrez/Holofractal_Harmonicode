from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence
import hashlib
import json
import os
import platform
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
    return {"path": path, "version": (first.stdout or first.stderr).splitlines()[0]}


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
    artifacts = []
    for path in (static_library, shared_library, cli_binary, test_binary):
        artifacts.append({"path": path.relative_to(repo).as_posix(), "size": path.stat().st_size, "sha256": _sha256(path)})
    manifest = {
        "schema": "HHS_GFCC_NATIVE_BUILD_MANIFEST_V1",
        "compiler": _tool_identity(cc, repo),
        "archiver": _tool_identity(ar, repo),
        "target_triple": target,
        "architecture": platform.machine(),
        "optimization_flags": flags,
        "include_paths": [str(include), str(inherited_include)],
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


def compile_shaders(repo: Path) -> dict[str, Any]:
    compiler = shutil.which("glslangValidator")
    if not compiler:
        raise GFCCError("HHS_GFCC_SHADER_COMPILATION_ERROR", "shader", "compile", "glslangValidator unavailable")
    subsystem = repo / "native_projects" / "hhs_gfcc_pass152"
    generated = subsystem / "generated" / "shaders"
    dist = subsystem / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    shaders = [
        (generated / "hhs_gfcc_fragment.glsl", "frag", dist / "hhs_gfcc_shader.spv"),
        (generated / "hhs_gfcc_collision_field.glsl", "comp", dist / "hhs_gfcc_collision_field.spv"),
    ]
    records = []
    for source, stage, output in shaders:
        if not source.is_file():
            raise GFCCError("HHS_GFCC_SHADER_GENERATION_ERROR", "shader", "compile", "generated shader source missing", {"source": source.as_posix()})
        completed = _run([compiler, "-V", "--target-env", "vulkan1.1", "-S", stage, str(source), "-o", str(output)], cwd=repo)
        if output.stat().st_size < 20:
            raise GFCCError("HHS_GFCC_SHADER_COMPILATION_ERROR", "shader", "compile", "compiled SPIR-V artifact too small", {"output": output.as_posix()})
        records.append({
            "stage": stage,
            "source": source.relative_to(repo).as_posix(),
            "source_sha256": _sha256(source),
            "artifact": output.relative_to(repo).as_posix(),
            "artifact_size": output.stat().st_size,
            "artifact_sha256": _sha256(output),
            "compiler_output": (completed.stdout + completed.stderr).strip(),
        })
    manifest = {
        "schema": "HHS_GFCC_SHADER_BUILD_MANIFEST_V1",
        "compiler": _tool_identity(compiler, repo),
        "target_environment": "vulkan1.1",
        "optimization_flags": [],
        "uniform_layout": {
            "phi_projection": "float32 exact-source-bound",
            "inverse_sqrt2_projection": "float32 exact-source-bound",
            "scale_projection": "float32 exact-source-bound",
            "fibonacci_n": "uint32",
            "nonary_phase": "uint32",
            "vm81_cell": "uint32",
            "hash72_index": "uint32",
            "hash216_index": "uint32",
            "shell_depth": "uint32",
            "orientation": "uint32",
            "constraint_flags": "uint32",
        },
        "descriptor_bindings": [],
        "records": records,
        "shader_authority": "PROJECTED_RENDERING_ONLY",
    }
    manifest["build_identity"] = digest256(manifest)
    write_json(subsystem / "manifest" / "shader_manifest.json", manifest)
    return manifest


__all__ = ["compile_native", "compile_shaders"]
