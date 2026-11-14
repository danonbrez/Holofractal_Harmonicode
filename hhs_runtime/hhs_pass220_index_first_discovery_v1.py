"""Pass 220: index-first discovery over the existing Hash216 file census.

GitHub code search is not an exhaustive file enumerator. Read the existing
repository source index before fallback search. This is a bounded candidate
finder, not a negative-existence or native-admission authority.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from hhs_runtime.hhs_pass220_corpus_negative_claim_gate_v1 import validate_claim

SCHEMA = "HHS_PASS220_INDEX_FIRST_DISCOVERY_V1"
GRAPH = "artifacts/repository_index/REPOSITORY_HASH216_DEPENDENCY_GRAPH.json"
LANE5 = "artifacts/repository_index/LANE5_HASH216_HYDRATION_KNOWLEDGE_GRAPH.json"
RECEIPT = "artifacts/repository_index/LANE5_HASH216_HYDRATION_DATABASE_RECEIPT.json"


class IndexDiscoveryError(ValueError):
    pass


def search_index(root: Path, term: str, *, limit: int = 100) -> dict[str, Any]:
    """Return path matches only from an exact-checkout indexed file census.

    The graph and Lane 5 files are existing discovery surfaces, not proof
    that every branch/PR has been indexed. Never return ABSENT.
    """
    root = Path(root).resolve()
    if not isinstance(term, str) or not term.strip() or len(term) > 512:
        raise IndexDiscoveryError("INDEX_QUERY_REQUIRED")
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise IndexDiscoveryError("INDEX_LIMIT_INVALID")
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"],cwd=root,
                             check=True,capture_output=True,text=True).stdout.strip()
        graph = json.loads((root / GRAPH).read_text("utf-8"))
        lane = json.loads((root / LANE5).read_text("utf-8"))
        receipt = json.loads((root / RECEIPT).read_text("utf-8"))
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise IndexDiscoveryError("INDEX_ARTIFACTS_UNAVAILABLE") from exc
    if any(x.get("source_commit") != rev for x in (graph,lane,receipt)):
        raise IndexDiscoveryError("INDEX_CHECKOUT_REVISION_MISMATCH")
    files=graph.get("files")
    if not isinstance(files,list) or not files:
        raise IndexDiscoveryError("INDEX_FILE_CENSUS_INVALID")
    if len({x.get("path") for x in files if isinstance(x,dict)}) != len(files):
        raise IndexDiscoveryError("INDEX_FILE_CENSUS_DUPLICATE")
    wanted=term.casefold()
    matched=[]
    for item in files:
        if not isinstance(item,dict) or not isinstance(item.get("path"),str):
            raise IndexDiscoveryError("INDEX_FILE_RECORD_INVALID")
        path=item["path"]
        if wanted in path.casefold():
            if not isinstance(item.get("git_blob"),str) or not isinstance(item.get("hash216"),str) or len(item["hash216"])!=216:
                raise IndexDiscoveryError("INDEX_MATCH_IDENTITY_INVALID")
            matched.append({"path_or_ref":path,"revision":item["git_blob"],
                            "hash216":item["hash216"]})
    matched.sort(key=lambda row:row["path_or_ref"])
    report=validate_claim({"object":term,"status":"FOUND" if matched else "NOT_YET_LOCATED",
        "checked_sources":[{"path_or_ref":x["path_or_ref"],"revision":x["revision"]} for x in matched[:limit]]})
    return {"schema":SCHEMA,"query":term,"source_commit":rev,
        "source_index":GRAPH,"lane5_index":LANE5,"database_receipt":RECEIPT,
        "file_census_count":len(files),"matched_count":len(matched),
        "truncated":len(matched)>limit,"matches":matched[:limit],
        "report":report,"github_code_search_used":False,
        "open_branches_and_prs_exhaustively_covered":False,
        "negative_existence_claim_authorized":False,
        "vm81_mutation_authority":False,"hash72_hash216_minted":False}
