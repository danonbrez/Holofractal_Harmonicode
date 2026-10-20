"""Fail-closed Lean 4 proof checker for guarded service contracts.

This is a proof-checking admission prerequisite, never VM81 commit authority.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json
import re
import subprocess

PIN = "4.34.0"


class ServiceLeanProofFailure(ValueError):
    pass


def check_service_lean_proofs(proofs, *, repo_root: str | Path) -> tuple[dict, ...]:
    if not isinstance(proofs, (tuple, list)) or not proofs:
        raise ServiceLeanProofFailure("LEAN_PROOF_MANIFEST_REQUIRED")
    root = Path(repo_root).resolve()
    checked = []
    for entry in proofs:
        if not isinstance(entry, dict):
            raise ServiceLeanProofFailure("LEAN_PROOF_ENTRY_INVALID")
        name, digest = entry.get("path"), entry.get("source_sha256")
        if not isinstance(name, str) or not re.fullmatch(r"formal/lean/[A-Za-z0-9_./-]+\.lean", name) or ".." in Path(name).parts:
            raise ServiceLeanProofFailure("LEAN_PROOF_SOURCE_PATH_INVALID")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ServiceLeanProofFailure("LEAN_PROOF_DIGEST_INVALID")
        path = (root / name).resolve()
        if not path.is_relative_to(root / "formal" / "lean") or not path.is_file():
            raise ServiceLeanProofFailure("LEAN_PROOF_SOURCE_MISSING")
        actual = sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            raise ServiceLeanProofFailure("LEAN_PROOF_SOURCE_DRIFT")
        toolchain = root / "lean-toolchain"
        if not toolchain.is_file() or toolchain.read_text().strip() != "leanprover/lean4:v" + PIN:
            raise ServiceLeanProofFailure("LEAN_TOOLCHAIN_PIN_MISMATCH")
        try:
            version = subprocess.run(["lean", "--version"],cwd=root,
                                     capture_output=True,text=True,timeout=20,check=False)
            if version.returncode != 0 or not re.search(r"Lean \(version 4\.34\.0[,)]",version.stdout):
                raise ServiceLeanProofFailure("LEAN_CHECKER_VERSION_MISMATCH")
            proof = subprocess.run(["lean",name],cwd=root,capture_output=True,
                                   text=True,timeout=120,check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ServiceLeanProofFailure("LEAN_PROOF_CHECKER_UNAVAILABLE") from exc
        if proof.returncode != 0:
            raise ServiceLeanProofFailure("LEAN_PROOF_CHECK_FAILED")
        checked.append({"path":name,"source_sha256":actual,
                        "toolchain":"leanprover/lean4:v"+PIN,"checker_exit":0,
                        "canonical_mutation_authority":False})
    return tuple(checked)


def service_lean_proof_binding(*, service_name: str, manifest,
                               checked_receipts: tuple[dict, ...]) -> dict:
    """Bind executed checker receipts to service identity, not VM81 authority."""
    if not isinstance(service_name,str) or not service_name.strip():
        raise ServiceLeanProofFailure("LEAN_SERVICE_IDENTITY_REQUIRED")
    if not isinstance(manifest,(tuple,list)) or not manifest:
        raise ServiceLeanProofFailure("LEAN_PROOF_MANIFEST_REQUIRED")
    if len(manifest)!=len(checked_receipts):
        raise ServiceLeanProofFailure("LEAN_CHECKER_COVERAGE_MISMATCH")
    for expected, observed in zip(manifest, checked_receipts):
        if (not isinstance(expected,dict) or not isinstance(observed,dict)
                or observed.get("path")!=expected.get("path")
                or observed.get("source_sha256")!=expected.get("source_sha256")
                or observed.get("toolchain")!="leanprover/lean4:v"+PIN
                or observed.get("checker_exit")!=0
                or observed.get("canonical_mutation_authority") is not False):
            raise ServiceLeanProofFailure("LEAN_CHECKER_RECEIPT_MISMATCH")
    body={"schema":"HHS_GUARDED_SERVICE_LEAN_PROOF_BINDING_V1",
          "service_name":service_name,
          "checked_proofs":[dict(x) for x in checked_receipts],
          "candidate_only":True,"signed_hash216_admission_verified":False,
          "native_cpp_cell_wall_verified":False,"canonical_mint_authority":False}
    body["binding_sha256"]=sha256(json.dumps(
        body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return body
