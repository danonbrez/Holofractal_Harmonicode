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


def build_lean_cellwall_hydration_handoff(*, proof_binding: dict,
                                          native_candidate: dict,
                                          hydration_node: dict) -> dict:
    """Require existing native proof/graph identities before candidate handoff.

    This correlates independently supplied evidence; it never executes or
    signs the C++ wall and cannot substitute for native admission.
    """
    if not isinstance(proof_binding,dict) or proof_binding.get("schema") != "HHS_GUARDED_SERVICE_LEAN_PROOF_BINDING_V1":
        raise ServiceLeanProofFailure("LEAN_SERVICE_BINDING_REQUIRED")
    service=proof_binding.get("service_name")
    if not isinstance(native_candidate,dict) or native_candidate.get("service_name") != service:
        raise ServiceLeanProofFailure("NATIVE_SERVICE_IDENTITY_MISMATCH")
    if native_candidate.get("cpp_rna_cell_wall_routed") is not True or native_candidate.get("canonical_admission_invoked") is not False:
        raise ServiceLeanProofFailure("NATIVE_CANDIDATE_BOUNDARY_INVALID")
    if not isinstance(hydration_node,dict) or hydration_node.get("node_kind") not in ("CAPABILITY","CONSTRUCTOR"):
        raise ServiceLeanProofFailure("LANE5_KNOWLEDGE_NODE_REQUIRED")
    native_root=native_candidate.get("inherited_hash216")
    node_root=hydration_node.get("hash216")
    if not all(isinstance(v,str) and len(v)==216 for v in (native_root,node_root)):
        raise ServiceLeanProofFailure("HASH216_CANDIDATE_IDENTITIES_REQUIRED")
    payload={
        "schema":"HHS_GUARDED_LEAN_CPP_LANE5_HANDOFF_V1",
        "service_name":service,
        "lean_binding_sha256":proof_binding.get("binding_sha256"),
        "cpp_candidate_hash216":native_root,
        "lane5_knowledge_hash216":node_root,
        "cpp_rna_cell_wall_routed":True,
        "signed_environmental_admission_verified":False,
        "lean_proof_carried_in_signed_receipt":False,
        "candidate_only":True,
    }
    payload["handoff_sha256"]=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return payload


def lookup_lane5_service_proof_binding(*, service_name: str, module: str,
                                       function: str, proof_binding: dict,
                                       knowledge_database) -> dict:
    """Read actual inherited Pass219 1.69 search rows, never create graph state."""
    if proof_binding.get("service_name") != service_name:
        raise ServiceLeanProofFailure("LEAN_SERVICE_IDENTITY_MISMATCH")
    if not all(isinstance(v,str) and v for v in (service_name,module,function)):
        raise ServiceLeanProofFailure("SERVICE_BINDING_INCOMPLETE")
    source_path=module.replace(".","/")+".py"
    records=knowledge_database.search(function,kinds=("CAPABILITY","CONSTRUCTOR"),limit=64)
    matching=[row for row in records if row.get("source_path")==source_path
              and row.get("node_kind") in ("CAPABILITY","CONSTRUCTOR")
              and row.get("name")==function
              and isinstance(row.get("payload"),dict)
              and row["payload"].get("candidate_only") is True]
    if len(matching)!=1:
        raise ServiceLeanProofFailure("LANE5_SERVICE_GRAPH_MISSING_OR_AMBIGUOUS")
    node=matching[0]
    if not isinstance(node.get("hash216"),str) or len(node["hash216"])!=216:
        raise ServiceLeanProofFailure("LANE5_HASH216_IDENTITY_INVALID")
    result={"schema":"HHS_GUARDED_LEAN_LANE5_LIVE_SEARCH_BINDING_V1",
            "service_name":service_name,"source_path":source_path,
            "proof_binding_sha256":proof_binding.get("binding_sha256"),
            "knowledge_node_id":node.get("node_id"),
            "knowledge_hash216":node["hash216"],
            "native_cpp_cell_wall_admitted":False,
            "canonical_hash216_signed":False,
            "candidate_only":True}
    result["binding_sha256"]=sha256(json.dumps(
        result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return result
