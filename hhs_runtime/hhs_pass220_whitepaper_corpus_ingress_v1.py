"""Full, source-frozen two-folder proof-corpus ingress.

A source-complete machine index is not itself a theorem proof. Native admission
requires explicit independently verified theorem-to-runtime bindings.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

FREEZE = Path("contracts/pass220/PASS_220_WHITEPAPER_CORPUS_SOURCE_FREEZE_V1.json")
REVISION_LINEAGE = Path("contracts/pass220/PASS_220_WHITEPAPER_COURSE_REVISION_LINEAGE_V1.json")
DIRECTORIES = ("whitepapers/", "docs/whitepapers/")
SCHEMA = "HHS_PASS220_WHITEPAPER_CORPUS_INDEX_V1"
REFERENCE = re.compile(r"(?:hhs_runtime/[A-Za-z0-9_./-]+|formal/lean/[A-Za-z0-9_./-]+|contracts/[A-Za-z0-9_./-]+)")
PROOF_LANGUAGE = re.compile(r"\b(?:theorem|lemma|proof|axiom|constraint|invariant|corollary)\b", re.I)

class ProofCorpusError(ValueError):
    pass

def _tracked_sources() -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z", "--", *DIRECTORIES],
                            check=True, stdout=subprocess.PIPE).stdout
    return sorted(x.decode("utf-8") for x in result.split(b"\0") if x)

def _verified_course_revision(root: Path, path: str, frozen_sha: str, current_sha: str) -> dict:
    """Admit only a dual-source revision with BOTH complete original blobs.

    The original frozen manifest stays immutable. The original course bytes
    remain available separately; the expanded source is checked byte-for-byte
    against an explicit registered successor identity. This never authorizes
    any mathematical proof or a different, unregistered revision.
    """
    lineage = json.loads((root / REVISION_LINEAGE).read_text("utf-8"))
    if (lineage.get("schema") != "HHS_PASS220_WHITEPAPER_COURSE_REVISION_LINEAGE_V1"
        or lineage.get("revision_count") != 1
        or len(lineage.get("revisions", [])) != 1):
        raise ProofCorpusError("SOURCE_REVISION_LINEAGE_INVALID")
    row = lineage["revisions"][0]
    if (row.get("source_path") != path or row.get("historic_blob_sha") != frozen_sha
        or row.get("current_blob_sha") != current_sha
        or row.get("source_integrity_gate") != "VERIFY_HISTORICAL_AND_CURRENT_BLOBS_INDEPENDENTLY"
        or row.get("proof_admission_inferred") is not False):
        raise ProofCorpusError("SOURCE_BLOB_CHANGED:" + path)
    preserved = row.get("historic_copy_path")
    if (not isinstance(preserved, str) or not preserved.startswith("docs/pass220/frozen_sources/")
        or ".." in Path(preserved).parts):
        raise ProofCorpusError("SOURCE_REVISION_COPY_PATH_INVALID")
    historical_file = root / preserved
    if not historical_file.is_file():
        raise ProofCorpusError("SOURCE_HISTORICAL_BLOB_MISSING:" + path)
    verified_historical = subprocess.run(
        ["git", "hash-object", "--", preserved],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout.strip()
    if verified_historical != frozen_sha:
        raise ProofCorpusError("SOURCE_HISTORICAL_BLOB_CHANGED:" + path)
    return {
        "historical_git_blob_sha": frozen_sha,
        "historical_copy_path": preserved,
        "current_git_blob_sha": current_sha,
        "revision_relation": row["relation"],
        "proof_admission_inferred": False,
    }

def build_corpus_index(root: Path = Path(".")) -> dict:
    root = root.resolve()
    frozen = json.loads((root / FREEZE).read_text("utf-8"))
    entries = frozen["files"]
    expected = [entry["path"] for entry in entries]
    actual = _tracked_sources()
    if len(expected) != frozen["expected_file_count"] or len(set(expected)) != len(expected):
        raise ProofCorpusError("SOURCE_FREEZE_COUNT_OR_DUPLICATE")
    if actual != sorted(expected):
        raise ProofCorpusError("SOURCE_COVERAGE_DRIFT")
    records = []
    for entry in entries:
        path = entry["path"]
        if not any(path.startswith(prefix) for prefix in DIRECTORIES):
            raise ProofCorpusError("OUTSIDE_REQUIRED_CORPUS_DIRECTORIES")
        filepath = root / path
        data = filepath.read_bytes()
        git_sha = subprocess.run(["git", "hash-object", "--", path],
                                 cwd=root, check=True, capture_output=True,
                                 text=True).stdout.strip()
        revision = None
        if git_sha != entry["git_blob_sha"]:
            # Only this explicitly registered course revision can be
            # reconciled; every other changed frozen source still fails.
            if path != "whitepapers/Harmonicode Algebra - Course":
                raise ProofCorpusError("SOURCE_BLOB_CHANGED:" + path)
            revision = _verified_course_revision(
                root, path, entry["git_blob_sha"], git_sha,
            )
        text = data.decode("utf-8")
        headings = [line.strip() for line in text.splitlines() if line.lstrip().startswith("#")]
        references = sorted(set(REFERENCE.findall(text)))
        # The legacy course proof graph must inherit the historical course's
        # references; successor references remain separately source-bound.
        historical_references = references
        if revision is not None:
            historical_text = (root / revision["historical_copy_path"]).read_text("utf-8")
            historical_references = sorted(set(REFERENCE.findall(historical_text)))
        records.append({
            "path": path,
            "git_blob_sha": git_sha,
            "content_sha256": sha256(data).hexdigest(),
            "byte_count": len(data),
            "heading_count": len(headings),
            "headings": headings,
            "proof_term_mentions": len(PROOF_LANGUAGE.findall(text)),
            "referenced_native_or_formal_paths": historical_references,
            "registered_successor_references": references if revision is not None else None,
            "native_proof_binding_status": "UNRESOLVED",
            "native_admission_authority": False,
            "registered_source_revision": revision,
        })
    result = {
        "schema": SCHEMA,
        "source_base_commit": frozen["source_base_commit"],
        "source_complete": True,
        "file_count": len(records),
        "files": records,
        "all_proofs_native_admitted": False,
        "candidate_metadata_index_only": True,
    }
    result["index_sha256"] = sha256(json.dumps(
        result, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()
    return result

def require_native_proof_binding(record: dict, receipts: dict) -> None:
    """Never infer proof admission from occurrence in the corpus index."""
    if record.get("native_proof_binding_status") != "VERIFIED" or not receipts.get("native_verification_receipt"):
        raise ProofCorpusError("NATIVE_PROOF_BINDING_NOT_ADMITTED")
