"""Read-only content-level course/lemma extraction from exact remote Git blobs.

Preserve raw source and ordered equation text. Candidates are not proofs of
equivalence, execution, or completeness. Fail on identity mismatch; report
every source not examined rather than interpreting skipped files as absent.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Callable, Mapping
from hhs_runtime.hhs_pass220_remote_ref_census_v1 import API, REPO, SHA, http_page

SCHEMA="HHS_PASS220_SOURCE_BOUND_PROOF_EXTRACTION_V1"
MODULE=re.compile(r"^#{1,4}\s+(?:Module|MODULE)\s+(\d+)\s*[—–-]\s*(.*)$",re.M)
LEAN=re.compile(r"^\s*(?:private\s+|protected\s+)?(?:theorem|lemma)\s+([^\s(:]+)",re.M)
PY=re.compile(r"^\s*(?:def|class)\s+((?:test_|prove_|verify_|lemma_)[A-Za-z0-9_]+)\b",re.M)
EQ=re.compile(r"==|(?<![<>=!])=(?!=)|≡|⇒|⇔|→|∆e|Δe")
MAX_BYTES=2_000_000

class ProofExtractionError(ValueError):
    pass

def git_blob_hash(raw: bytes, size: int = 40) -> str:
    payload=b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw
    if size==40:
        return hashlib.sha1(payload).hexdigest()
    if size==64:
        return hashlib.sha256(payload).hexdigest()
    raise ProofExtractionError("SOURCE_BLOB_HASH_WIDTH_INVALID")

def _scan(raw: bytes, path: str) -> list[dict[str,Any]]:
    try:
        source=raw.decode("utf-8")
    except UnicodeDecodeError:
        return []
    rows=[]
    lines=source.splitlines(keepends=True)
    positions=[0]
    for line in lines: positions.append(positions[-1]+len(line))
    if path.lower().endswith(".json"):
        try: packet=json.loads(source)
        except ValueError: packet=None
        if isinstance(packet,dict) and isinstance(packet.get("lemmas"),list):
            for i,lemma in enumerate(packet["lemmas"]):
                if isinstance(lemma,dict) and isinstance(lemma.get("statement"),str):
                    rows.append({"kind":"REGISTERED_LEMMA","identifier":lemma.get("id"),
                        "source_locator":{"json_pointer":f"/lemmas/{i}/statement"},
                        "exact_expression":lemma["statement"],"assumptions":lemma.get("assumptions"),
                        "declared_status":lemma.get("status"),"dependencies":lemma.get("dependencies"),
                        "proof_executed_by_extractor":False})
    heads=list(MODULE.finditer(source))
    for i,m in enumerate(heads):
        start=m.start()
        end=heads[i+1].start() if i+1<len(heads) else len(source)
        # Preserve complete module text; only bounded equation-bearing lines are
        # projected as candidates. Do not silently normalize ordered symbols.
        block=source[start:end]
        first=source.count("\n",0,start)+1
        candidates=[{"line":first+j,"exact_text":v}
                    for j,v in enumerate(block.splitlines())
                    if EQ.search(v) and len(v)<=16000]
        rows.append({"kind":"COURSE_MODULE","identifier":int(m.group(1)),
            "title":m.group(2),"source_locator":{"start_line":first,
            "end_line":source.count("\n",0,end)+1},
            "equation_candidates":candidates,
            "proof_executed_by_extractor":False})
    if path.lower().endswith((".lean",".v",".py")):
        pattern=LEAN if path.lower().endswith(".lean") else PY if path.lower().endswith(".py") else re.compile(r"^\s*(?:Lemma|Theorem)\s+([^\s:]+)",re.M)
        for match in pattern.finditer(source):
            rows.append({"kind":"FORMAL_DECLARATION" if not path.lower().endswith(".py") else "PYTHON_PROOF_CANDIDATE",
                "identifier":match.group(1),
                "source_locator":{"start_line":source.count("\n",0,match.start())+1},
                "exact_expression":source[match.start():source.find("\n",match.start()) if "\n" in source[match.start():] else len(source)],
                "proof_executed_by_extractor":False})
    return rows

def extract_proof_candidates(tree: Mapping[str,Any], *,
                             fetch: Callable[[str],Mapping[str,Any]] | None = None,
                             max_files: int = 250, max_bytes: int = MAX_BYTES) -> dict[str,Any]:
    if tree.get("schema")!="HHS_PASS220_REMOTE_REF_TREE_RECONCILIATION_V1":
        raise ProofExtractionError("SOURCE_TREE_SCHEMA_INVALID")
    if not isinstance(tree.get("candidate_matches"),list):
        raise ProofExtractionError("SOURCE_TREE_MATCHES_INVALID")
    if type(max_files) is not int or max_files<1 or type(max_bytes) is not int or max_bytes<1:
        raise ProofExtractionError("SOURCE_EXTRACT_LIMIT_INVALID")
    if fetch is None:
        token=os.environ.get("GITHUB_TOKEN")
        fetch=lambda url:http_page(url,token=token)[0]
    candidates=tree["candidate_matches"]
    distinct={}
    for item in candidates:
        repository,path,sha=item.get("repository"),item.get("path"),item.get("git_blob")
        if not isinstance(repository,str) or not REPO.fullmatch(repository) or not isinstance(path,str) or not path or not isinstance(sha,str) or not SHA.fullmatch(sha):
            raise ProofExtractionError("SOURCE_CANDIDATE_IDENTITY_INVALID")
        key=(repository,sha)
        distinct.setdefault(key,[]).append(item)
    extracted=[]
    skipped=[]
    for i,((repository,sha),references) in enumerate(sorted(distinct.items())):
        if i>=max_files:
            skipped.append({"repository":repository,"git_blob":sha,"reason":"FILE_LIMIT"})
            continue
        url=f"{API}/repos/{repository}/git/blobs/{sha}"
        try:
            packet=fetch(url)
        except Exception:
            skipped.append({"repository":repository,"git_blob":sha,"reason":"FETCH_UNAVAILABLE"})
            continue
        if not isinstance(packet,Mapping) or packet.get("encoding")!="base64" or not isinstance(packet.get("content"),str):
            skipped.append({"repository":repository,"git_blob":sha,"reason":"ENCODING_UNSUPPORTED"})
            continue
        try:
            raw=base64.b64decode(packet["content"],validate=False)
        except (ValueError,TypeError):
            raise ProofExtractionError("SOURCE_BLOB_BASE64_INVALID")
        if len(raw)>max_bytes:
            skipped.append({"repository":repository,"git_blob":sha,"reason":"BYTE_LIMIT"})
            continue
        if git_blob_hash(raw,len(sha))!=sha or (packet.get("sha") is not None and packet["sha"]!=sha):
            raise ProofExtractionError("SOURCE_BLOB_IDENTITY_MISMATCH")
        for item in references:
            extracted.append({"repository":repository,"ref":item.get("ref"),"commit":item.get("commit"),
                "path":item["path"],"git_blob":sha,"byte_length":len(raw),
                "objects":_scan(raw,item["path"])})
    return {"schema":SCHEMA,"extracted_sources":extracted,"skipped_blobs":skipped,
        "distinct_blob_count":len(distinct),"extracted_source_count":len(extracted),
        "source_tree_report_truncated":bool(tree.get("candidate_results_truncated")),
        "source_tree_errors":tree.get("remote_tree_errors",[]),
        "content_coverage_complete":False,"typed_equivalence_verified":False,
        "native_proof_executed":False,"negative_existence_claim_authorized":False,
        "vm81_mutation_authority":False,"canonical_hash216_minted":False}

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--tree",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--max-files",type=int,default=250)
    args=parser.parse_args()
    tree=json.loads(Path(args.tree).read_text("utf-8"))
    record=extract_proof_candidates(tree,max_files=args.max_files)
    Path(args.output).write_text(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=False)+"\n","utf-8")
    print("Source records:",record["extracted_source_count"])
    print("Uninspected blobs:",len(record["skipped_blobs"]))
