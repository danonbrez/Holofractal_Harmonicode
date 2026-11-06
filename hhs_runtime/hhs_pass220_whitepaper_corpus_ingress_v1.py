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
EDITION_PIN = Path("contracts/pass220/COURSE_EDITION_IDENTITY_V1.json")
COURSE = "whitepapers/Harmonicode Algebra - Course"
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
    editions = json.loads((root / EDITION_PIN).read_text("utf-8"))
    if (editions.get("schema") != "HHS_PASS220_COURSE_EDITION_IDENTITY_V1"
        or editions.get("source") != COURSE
        or editions.get("automatic_proof_inheritance_between_editions") is not False
        or editions.get("source_edition_identity_is_proof_authority") is not False
        or editions.get("vm81_admission") is not False):
        raise ProofCorpusError("COURSE_EDITION_CONTRACT_INVALID")
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
        edition = "HISTORICAL_FROZEN"
        if git_sha != entry["git_blob_sha"]:
            if (path != COURSE
                or entry["git_blob_sha"] != editions["historical"]["git_blob_sha"]
                or git_sha != editions["expanded"]["git_blob_sha"]):
                raise ProofCorpusError("SOURCE_BLOB_CHANGED:" + path)
            edition = "EXPANDED_PINNED"
        text = data.decode("utf-8")
        headings = [line.strip() for line in text.splitlines() if line.lstrip().startswith("#")]
        references = sorted(set(REFERENCE.findall(text)))
        records.append({
            "path": path,
            "git_blob_sha": git_sha,
            "edition": edition,
            "historical_git_blob_sha": entry["git_blob_sha"],
            "content_sha256": sha256(data).hexdigest(),
            "byte_count": len(data),
            "heading_count": len(headings),
            "headings": headings,
            "proof_term_mentions": len(PROOF_LANGUAGE.findall(text)),
            "referenced_native_or_formal_paths": references,
            "native_proof_binding_status": "UNRESOLVED",
            "native_admission_authority": False,
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
