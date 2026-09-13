#!/usr/bin/env python3
"""Pass 219 generation-integrity verifier.

Generated or edited repository state is treated as untrusted until it passes:
structure -> artifact identity -> build/ABI -> semantic authority checks.

This verifier does not create a second VM81 mutation authority. It verifies the
existing exact ABI and environmental-PQC authority boundary and fails closed on
drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA = "HHS_PASS219_GENERATION_INTEGRITY_EVIDENCE_V1"


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _fail(message: str) -> None:
    raise RuntimeError(message)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        _fail(f"manifest must be a JSON object: {path}")
    return payload


def _read_text(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        _fail(f"missing protected text artifact: {relative}")
    return path.read_text(encoding="utf-8")


def _parse_u32_define(text: str, name: str) -> int:
    match = re.search(
        rf"^\s*#define\s+{re.escape(name)}\s+(?:UINT32_C\()?([0-9]+)(?:\))?U?\s*$",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        _fail(f"missing or non-integer structural define: {name}")
    return int(match.group(1), 10)


def _verify_structural_constants(root: Path, manifest: dict[str, Any]) -> dict[str, int]:
    spec = manifest["structural_constants"]
    source = _read_text(root, spec["path"])
    observed: dict[str, int] = {}
    for name, expected in spec["values"].items():
        value = _parse_u32_define(source, name)
        if value != int(expected):
            _fail(f"structural constant drift: {name} expected={expected} observed={value}")
        observed[name] = value
    if observed["HHS_EXACT_VM81_CELLS"] * observed["HHS_EXACT_VM81_WORD_BITS"] != observed["HHS_EXACT_VM81_FRAME_BITS"]:
        _fail("VM81 cell/word/frame bit geometry no longer composes")
    if observed["HHS_EXACT_VM81_FRAME_BYTES"] * 8 != observed["HHS_EXACT_VM81_FRAME_BITS"]:
        _fail("VM81 byte/bit geometry no longer composes")
    if observed["HHS_EXACT_HASH72_COORDS"] != observed["HHS_EXACT_VM81_FRAME_BITS"]:
        _fail("Hash72 coordinate plane no longer equals VM5184 frame geometry")
    return observed


def _verify_tokens(root: Path, manifest: dict[str, Any]) -> None:
    for relative, required in manifest.get("required_tokens", {}).items():
        text = _read_text(root, relative)
        for token in required:
            if token not in text:
                _fail(f"required integrity token missing: {relative}: {token}")
    for relative, patterns in manifest.get("forbidden_regex", {}).items():
        text = _read_text(root, relative)
        for pattern in patterns:
            if re.search(pattern, text, flags=re.MULTILINE):
                _fail(f"forbidden integrity pattern present: {relative}: {pattern}")


def _verify_provider_scratch(root: Path, manifest: dict[str, Any]) -> None:
    spec = manifest["provider_scratch"]
    text = _read_text(root, spec["path"])
    for token in spec["required_tokens"]:
        if token not in text:
            _fail(f"provider scratch ownership drift: missing {token}")
    for pattern in spec.get("forbidden_regex", []):
        if re.search(pattern, text, flags=re.MULTILINE):
            _fail(f"provider scratch ownership drift: forbidden {pattern}")
    alloc_count = text.count("OPENSSL_malloc(")
    free_count = text.count("OPENSSL_free(")
    if alloc_count != int(spec["openssl_malloc_count"]):
        _fail(f"unexpected OpenSSL allocation surface: expected={spec['openssl_malloc_count']} observed={alloc_count}")
    if free_count != int(spec["openssl_free_count"]):
        _fail(f"unexpected OpenSSL free surface: expected={spec['openssl_free_count']} observed={free_count}")


def _verify_local_authority_map(root: Path, manifest: dict[str, Any]) -> None:
    spec = manifest["authority_map"]
    text = _read_text(root, spec["path"])
    if "local:" not in text:
        _fail("authority export map lost local-only section")
    for symbol in spec["required_local_symbols"]:
        if re.search(rf"^\s*{re.escape(symbol)};\s*$", text, flags=re.MULTILINE) is None:
            _fail(f"authority symbol is no longer explicitly local: {symbol}")


def _verify_artifacts(
    root: Path,
    manifest: dict[str, Any],
    require_sealed: bool,
) -> list[dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    for record in manifest["protected_artifacts"]:
        relative = record["path"]
        path = root / relative
        if not path.is_file():
            _fail(f"missing protected artifact: {relative}")
        data = path.read_bytes()
        row = {
            "path": relative,
            "byte_length": len(data),
            "git_blob_sha1": _git_blob_sha1(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        expected_blob = record.get("git_blob_sha1", "")
        expected_sha256 = record.get("sha256", "")
        expected_length = record.get("byte_length")
        if expected_blob and row["git_blob_sha1"] != expected_blob:
            _fail(
                f"protected artifact git identity drift: {relative} "
                f"expected={expected_blob} observed={row['git_blob_sha1']}"
            )
        if expected_sha256 and row["sha256"] != expected_sha256:
            _fail(
                f"protected artifact sha256 drift: {relative} "
                f"expected={expected_sha256} observed={row['sha256']}"
            )
        if expected_length is not None and row["byte_length"] != int(expected_length):
            _fail(
                f"protected artifact length drift: {relative} "
                f"expected={expected_length} observed={row['byte_length']}"
            )
        if require_sealed and (not expected_blob or not expected_sha256 or expected_length is None):
            _fail(f"protected artifact is not fully sealed: {relative}")
        observed.append(row)
    return observed


def _dynamic_symbols(library: Path) -> set[str]:
    if not library.is_file():
        _fail(f"ABI library missing: {library}")
    proc = subprocess.run(
        ["nm", "-D", "--defined-only", str(library)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        _fail(f"nm failed for {library}: {proc.stderr.strip()}")
    symbols: set[str] = set()
    for line in proc.stdout.splitlines():
        fields = line.split()
        if fields:
            symbols.add(fields[-1].split("@@", 1)[0])
    return symbols


def _verify_abi(library: Path, manifest: dict[str, Any]) -> dict[str, list[str]]:
    symbols = _dynamic_symbols(library)
    required = list(manifest["abi"]["required_public_symbols"])
    forbidden = list(manifest["abi"]["forbidden_dynamic_exports"])
    missing = sorted(symbol for symbol in required if symbol not in symbols)
    leaked = sorted(symbol for symbol in forbidden if symbol in symbols)
    if missing:
        _fail("required public ABI symbols missing: " + ", ".join(missing))
    if leaked:
        _fail("internal canonical mutation symbols leaked dynamically: " + ", ".join(leaked))
    return {"required_public_symbols": sorted(required), "forbidden_dynamic_exports": sorted(forbidden)}


def _aggregate_digest(rows: list[dict[str, Any]]) -> str:
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="contracts/pass219/PASS_219_GENERATION_INTEGRITY_MANIFEST_V1.json",
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--library")
    parser.add_argument("--evidence")
    parser.add_argument("--print-seal", action="store_true")
    parser.add_argument("--require-sealed", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    manifest_path = (root / args.manifest).resolve()
    manifest = _load_json(manifest_path)
    if manifest.get("schema") != "HHS_PASS219_GENERATION_INTEGRITY_MANIFEST_V1":
        _fail("unexpected generation-integrity manifest schema")

    constants = _verify_structural_constants(root, manifest)
    _verify_tokens(root, manifest)
    _verify_provider_scratch(root, manifest)
    _verify_local_authority_map(root, manifest)
    artifacts = _verify_artifacts(root, manifest, args.require_sealed)

    abi: dict[str, list[str]] | None = None
    if args.library:
        abi = _verify_abi((root / args.library).resolve(), manifest)

    seal = {row["path"]: {k: row[k] for k in ("byte_length", "git_blob_sha1", "sha256")} for row in artifacts}
    if args.print_seal:
        print(json.dumps(seal, sort_keys=True, indent=2))

    manifest_bytes = manifest_path.read_bytes()
    evidence = {
        "schema": SCHEMA,
        "result": "PASS",
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "protected_artifact_root_sha256": _aggregate_digest(artifacts),
        "protected_artifacts": artifacts,
        "structural_constants": constants,
        "abi_verified": abi is not None,
        "abi": abi,
        "canonical_mutation_authority_created": False,
        "halt_on_divergence": True,
        "host_escalation_permitted": False,
        "provider_scratch_is_canonical_state": False,
    }
    if args.evidence:
        evidence_path = (root / args.evidence).resolve()
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if not args.print_seal:
        print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"PASS219_GENERATION_INTEGRITY_HALT: {exc}", file=sys.stderr)
        raise SystemExit(1)
