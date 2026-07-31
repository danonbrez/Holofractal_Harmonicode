#!/usr/bin/env python3
"""Build the deterministic Pass 175 x86_64 invariant-kernel artifact set."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from hhs_runtime.core.hash72_digest_v1 import hash72_digest


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def run(command: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return completed.stdout


def digest(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"name": path.name, "bytes": len(data), "sha256": sha256(data).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out", default="build/terminal")
    parser.add_argument("--cc", default=os.environ.get("CC", "cc"))
    args = parser.parse_args()

    project = Path(args.project_root).resolve()
    out = (project / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    include = project / "include"
    source = project / "src" / "vm81_invariant_kernel.c"
    test_source = project / "tests" / "test_vm81_invariant_kernel.c"

    object_path = out / "vm81_invariant_kernel_x86_64.o"
    shared_path = out / "libvm81_invariant_kernel.so"
    binary_path = out / "vm81_invariant_kernel.bin"
    map_path = out / "vm81_invariant_kernel.map"
    sha_path = out / "vm81_invariant_kernel.sha256"
    hash216_path = out / "vm81_invariant_kernel.hash216"
    manifest_path = out / "vm81_invariant_kernel_manifest.json"
    receipt_path = out / "vm81_invariant_kernel_test_receipt.json"
    test_path = out / "test_vm81_invariant_kernel"

    common = [
        "-std=c11",
        "-O3",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        "-fno-fast-math",
        "-ffp-contract=off",
        "-fno-ident",
        "-fno-asynchronous-unwind-tables",
        "-fno-stack-protector",
        "-fPIC",
        f"-ffile-prefix-map={project}=.",
        f"-I{include}",
    ]
    compile_output = run([args.cc, *common, "-c", str(source), "-o", str(object_path)], cwd=project)
    link_output = run([args.cc, "-shared", "-Wl,--build-id=none", str(object_path), "-o", str(shared_path)], cwd=project)
    test_compile_output = run(
        [args.cc, *common, str(test_source), str(object_path), "-o", str(test_path)],
        cwd=project,
    )
    test_output = run([str(test_path)], cwd=project)
    if "HHS_PASS_175_INVARIANT_KERNEL_TEST_PASS" not in test_output:
        raise SystemExit("native kernel test receipt missing")

    objcopy = shutil.which("objcopy") or shutil.which("llvm-objcopy")
    if objcopy is None:
        raise SystemExit("objcopy or llvm-objcopy is required")
    run(
        [
            objcopy,
            "-O",
            "binary",
            "--only-section=.text",
            "--only-section=.rodata",
            str(object_path),
            str(binary_path),
        ],
        cwd=project,
    )
    nm = shutil.which("nm")
    if nm is None:
        raise SystemExit("nm is required")
    map_output = run([nm, "-n", "-S", str(shared_path)], cwd=project)
    map_path.write_text(map_output, encoding="utf-8")

    primary = [digest(path) for path in (object_path, shared_path, binary_path, map_path)]
    sha_path.write_text(
        "".join(f"{item['sha256']}  {item['name']}\n" for item in primary),
        encoding="ascii",
    )

    compiler_version = run([args.cc, "--version"], cwd=project).splitlines()[0]
    manifest_body = {
        "schema": "HHS_PASS_175_INVARIANT_KERNEL_MANIFEST_V1",
        "contract": "HHS-P175-H216-VM5184-G243-VIP-PCW-SVA-H72-X64IE",
        "abi_version": "0x00017501",
        "target": "x86_64",
        "compiler": compiler_version,
        "compile_flags": common,
        "link_flags": ["-shared", "-Wl,--build-id=none"],
        "host": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "exact_scalar_circuits": {
            "lo": [0, 1, 0, 1, 10, 11, 1, 0],
            "hi": [1, 0, 11, 10, 1, 0, 0, 111],
        },
        "geometry": {
            "vm81_cells": 81,
            "operations_per_cell": 64,
            "permanent_instructions": 5184,
            "controls_per_instruction": 243,
            "projected_addresses": 1259712,
        },
        "authority": {
            "parallel_candidates": True,
            "parallel_state_authority": False,
            "singleton_vm81_admission_callback_required": True,
            "hash72_commit_streams": 1,
        },
        "artifacts": primary + [digest(sha_path)],
        "source_sha256": sha256(source.read_bytes()).hexdigest(),
        "header_sha256": sha256((include / "vm81_invariant_kernel.h").read_bytes()).hexdigest(),
        "test_source_sha256": sha256(test_source.read_bytes()).hexdigest(),
    }
    binary = binary_path.read_bytes()
    lanes = [
        hash72_digest({**manifest_body, "lane": lane}, binary)
        for lane in ("PREDECESSOR", "CURRENT", "SUCCESSOR")
    ]
    combined = "".join(lanes)
    if len(combined) != 216:
        raise SystemExit("Hash216 length mismatch")
    hash216_path.write_text(combined + "\n", encoding="ascii")
    manifest_body["hash216"] = {
        "predecessor": lanes[0],
        "current": lanes[1],
        "successor": lanes[2],
        "combined": combined,
        "characters": len(combined),
    }
    manifest_body["manifest_identity_sha256"] = sha256(
        b"HHS-P175-INVARIANT-KERNEL-MANIFEST\0" + canonical(manifest_body)
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest_body, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    receipt_body = {
        "schema": "HHS_PASS_175_INVARIANT_KERNEL_TEST_RECEIPT_V1",
        "classification": "HHS_PASS_175_INVARIANT_KERNEL_NATIVE_TEST_PASS",
        "test_output": test_output.strip(),
        "compile_output": compile_output.strip(),
        "link_output": link_output.strip(),
        "test_compile_output": test_compile_output.strip(),
        "manifest_identity_sha256": manifest_body["manifest_identity_sha256"],
        "binary_sha256": sha256(binary).hexdigest(),
        "hash216": combined,
        "exact_address_roundtrips": 5184,
        "exact_control_roundtrips": 243,
        "exact_projected_roundtrips": 1259712,
        "parallel_state_authority": False,
        "singleton_vm81_admission_callback_required": True,
    }
    receipt_body["receipt_sha256"] = sha256(
        b"HHS-P175-INVARIANT-KERNEL-TEST\0" + canonical(receipt_body)
    ).hexdigest()
    receipt_path.write_text(json.dumps(receipt_body, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    required = [
        object_path,
        shared_path,
        binary_path,
        map_path,
        sha_path,
        hash216_path,
        manifest_path,
        receipt_path,
    ]
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"missing artifact: {path}")
    print(json.dumps({
        "classification": "HHS_PASS_175_NATIVE_ARTIFACT_SET_COMPLETE",
        "out": str(out),
        "artifacts": [digest(path) for path in required],
        "manifest_identity_sha256": manifest_body["manifest_identity_sha256"],
        "test_receipt_sha256": receipt_body["receipt_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
