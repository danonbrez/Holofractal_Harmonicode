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


def verify_lean_service_provenance_chain(*, proof_binding: dict,
                                         registry_descriptor: dict,
                                         lane5_binding: dict,
                                         native_receipt: dict) -> dict:
    """Reject detached/mismatched identities; signed proof remains unasserted.

    Native receipt data must be supplied by the inherited runtime, not created
    or synthesized here. Receipt equality is evidence correlation, not signature
    verification.
    """
    service=proof_binding.get("service_name")
    if not isinstance(service,str) or not service:
        raise ServiceLeanProofFailure("LEAN_SERVICE_IDENTITY_REQUIRED")
    if registry_descriptor.get("name") != service or lane5_binding.get("service_name") != service:
        raise ServiceLeanProofFailure("SERVICE_PROVENANCE_IDENTITY_MISMATCH")
    if lane5_binding.get("proof_binding_sha256") != proof_binding.get("binding_sha256"):
        raise ServiceLeanProofFailure("LEAN_PROOF_LINEAGE_MISMATCH")
    if native_receipt.get("service_name") != service:
        raise ServiceLeanProofFailure("NATIVE_RECEIPT_SERVICE_MISMATCH")
    root=lane5_binding.get("knowledge_hash216")
    if not isinstance(root,str) or len(root)!=216 or native_receipt.get("knowledge_hash216") != root:
        raise ServiceLeanProofFailure("NATIVE_LANE5_ROOT_MISMATCH")
    if native_receipt.get("lean_binding_sha256") != proof_binding.get("binding_sha256"):
        raise ServiceLeanProofFailure("NATIVE_LEAN_ROOT_MISMATCH")
    if native_receipt.get("cpp_rna_cell_wall_routed") is not True:
        raise ServiceLeanProofFailure("CPP_CELL_WALL_ROUTE_NOT_PROVEN")
    body={"schema":"HHS_GUARDED_LEAN_SERVICE_PROVENANCE_CHAIN_V1",
          "service_name":service,"lean_binding_sha256":proof_binding["binding_sha256"],
          "knowledge_hash216":root,
          "native_receipt_identity":native_receipt.get("receipt_identity"),
          "evidence_identity_consistent":True,
          "native_signature_cryptographically_verified":False,
          "canonical_vm81_commit_verified":False,
          "production_e2e_verified":False,
          "candidate_only":True}
    body["correlation_sha256"]=sha256(json.dumps(
        body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return body


def lookup_live_lane5_database(*, database_path: str | Path,
                               service_name: str, module: str,
                               function: str, proof_binding: dict) -> dict:
    """Query inherited hydrated knowledge_nodes SQLite in READ-ONLY mode.

    Database is never created/hydrated/mutated by this diagnostic. The results
    are still discovery candidates, NOT canonical C++ proof receipts.
    """
    import sqlite3
    path = Path(database_path).resolve(strict=True)
    if not path.is_file():
        raise ServiceLeanProofFailure("LANE5_DATABASE_NOT_FILE")
    try:
        db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2)
    except sqlite3.Error as exc:
        raise ServiceLeanProofFailure("LANE5_DATABASE_UNAVAILABLE") from exc
    try:
        db.row_factory = sqlite3.Row
        class ReadOnlyKnowledge:
            def search(self, name, *, kinds, limit):
                if not kinds or limit <= 0 or limit > 512:
                    raise ServiceLeanProofFailure("LANE5_QUERY_OUT_OF_BOUNDS")
                placeholders = ",".join("?" for _ in kinds)
                rows = db.execute(
                    "SELECT node_id,node_hash216,node_kind,name,source_path,payload_json "
                    "FROM knowledge_nodes WHERE node_kind IN ("+placeholders+") "
                    "AND (name LIKE ? OR node_id LIKE ? OR COALESCE(source_path,'') LIKE ?) "
                    "ORDER BY node_kind,name,node_id LIMIT ?",
                    (*kinds,"%"+name+"%","%"+name+"%","%"+name+"%",limit),
                ).fetchall()
                return [{"node_id":r["node_id"],"hash216":r["node_hash216"],
                         "node_kind":r["node_kind"],"name":r["name"],
                         "source_path":r["source_path"],
                         "payload":json.loads(r["payload_json"])} for r in rows]
        return lookup_lane5_service_proof_binding(
            service_name=service_name,module=module,function=function,
            proof_binding=proof_binding,knowledge_database=ReadOnlyKnowledge())
    except (OSError, ValueError, sqlite3.Error) as exc:
        if isinstance(exc,ServiceLeanProofFailure):
            raise
        raise ServiceLeanProofFailure("LANE5_DATABASE_SCHEMA_OR_QUERY_FAILURE") from exc
    finally:
        db.close()


def verify_lane5_hydration_metadata(*, database_path: str | Path,
                                    expected_projection_root_hash216: str,
                                    expected_dependency_root_hash216: str) -> dict:
    """Verify existing Pass219 1.69 DB roots before service discovery.

    Root consistency is hydration provenance evidence, not signature or VM81
    admission. Never initialize, rebuild, or mutate the database.
    """
    import sqlite3
    for value in (expected_projection_root_hash216, expected_dependency_root_hash216):
        if not isinstance(value,str) or len(value)!=216:
            raise ServiceLeanProofFailure("LANE5_EXPECTED_ROOT_INVALID")
    try:
        path=Path(database_path).resolve(strict=True)
        with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True,timeout=2) as db:
            rows=db.execute("SELECT key,value FROM hydration_metadata").fetchall()
            metadata=dict(rows)
            if len(rows)!=len(metadata):
                raise ServiceLeanProofFailure("LANE5_DUPLICATE_METADATA_KEY")
            if metadata.get("projection_root_hash216")!=expected_projection_root_hash216:
                raise ServiceLeanProofFailure("LANE5_PROJECTION_ROOT_MISMATCH")
            if metadata.get("source_dependency_graph_root_hash216")!=expected_dependency_root_hash216:
                raise ServiceLeanProofFailure("LANE5_DEPENDENCY_ROOT_MISMATCH")
            if (metadata.get("candidate_only")!="true"
                or metadata.get("execution_authority")!="false"
                or metadata.get("canonical_mutation_authority")!="false"):
                raise ServiceLeanProofFailure("LANE5_AUTHORITY_METADATA_INVALID")
    except (OSError, sqlite3.Error) as exc:
        raise ServiceLeanProofFailure("LANE5_HYDRATION_METADATA_UNAVAILABLE") from exc
    result={"schema":"HHS_GUARDED_SERVICE_LANE5_HYDRATION_ROOT_MATCH_V1",
            "projection_root_hash216":expected_projection_root_hash216,
            "dependency_root_hash216":expected_dependency_root_hash216,
            "metadata_matches_expected_roots":True,
            "hash216_signature_verified":False,
            "canonical_admission_verified":False,
            "candidate_only":True}
    result["verification_sha256"]=sha256(json.dumps(
        result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return result
