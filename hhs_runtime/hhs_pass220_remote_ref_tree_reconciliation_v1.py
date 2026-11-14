"""Pass 220 remote Git-tree candidate corpus reconciliation, candidate-only.

Observes exact tree blob IDs for SHAs from the paginated remote-ref census.
Never calls GitHub code search, and never treats filename hits or misses as
mathematical proof, completeness, or native admission. GitHub's recursive
tree truncated flag is a hard incomplete-coverage condition.
"""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Mapping

from hhs_runtime.hhs_pass220_remote_ref_census_v1 import (
    API, REPO, SHA, RemoteCensusError, http_page,
)

SCHEMA = "HHS_PASS220_REMOTE_REF_TREE_RECONCILIATION_V1"
SUFFIXES = (".md", ".lean", ".v", ".wl", ".wls", ".json",
            ".py", ".h", ".hpp", ".c", ".cpp", ".harmonicode")
TOKENS = ("course", "lemma", "proof", "theorem", "axiom", "math",
          "formal", "tensor", "constructor", "hnan", "harmonicode")


class RemoteTreeReconciliationError(ValueError):
    pass


def _get_json(url: str, get: Callable[[str], Any]) -> Mapping[str, Any]:
    try:
        packet = get(url)
    except (OSError, ValueError, RemoteCensusError) as exc:
        raise RemoteTreeReconciliationError("REMOTE_TREE_FETCH_FAILED") from exc
    if not isinstance(packet, Mapping):
        raise RemoteTreeReconciliationError("REMOTE_TREE_PACKET_INVALID")
    return packet


def reconcile_remote_trees(census: Mapping[str, Any], *,
                           get: Callable[[str], Any] | None = None,
                           max_trees: int = 2000,
                           max_matches: int = 5000,
                           baseline: Mapping[str, str] | None = None,
                           query: str | None = None) -> dict[str, Any]:
    if census.get("schema") != "HHS_PASS220_REMOTE_REF_CENSUS_V1":
        raise RemoteTreeReconciliationError("REMOTE_TREE_CENSUS_SCHEMA_INVALID")
    repository = census.get("repository")
    if not isinstance(repository, str) or not REPO.fullmatch(repository):
        raise RemoteTreeReconciliationError("REMOTE_TREE_REPOSITORY_INVALID")
    if census.get("branch_pages_exhausted") is not True or census.get("open_pr_pages_exhausted") is not True:
        raise RemoteTreeReconciliationError("REMOTE_TREE_CENSUS_INCOMPLETE")
    if type(max_trees) is not int or not 1 <= max_trees <= 10000:
        raise RemoteTreeReconciliationError("REMOTE_TREE_LIMIT_INVALID")
    if type(max_matches) is not int or not 1 <= max_matches <= 100000:
        raise RemoteTreeReconciliationError("REMOTE_TREE_MATCH_LIMIT_INVALID")
    if query is not None and (not isinstance(query, str) or not query.strip() or len(query) > 512):
        raise RemoteTreeReconciliationError("REMOTE_TREE_QUERY_INVALID")
    if baseline is not None and (
        not isinstance(baseline, Mapping) or
        any(not isinstance(k, str) or not isinstance(v, str) or not SHA.fullmatch(v)
            for k, v in baseline.items())
    ):
        raise RemoteTreeReconciliationError("REMOTE_TREE_BASELINE_INVALID")
    if get is None:
        token = os.environ.get("GITHUB_TOKEN")
        get = lambda url: http_page(url, token=token)[0]
    heads = []
    for entry in census.get("branches", []):
        heads.append(("branch:" + entry["name"], repository, entry["sha"]))
    for entry in census.get("open_pulls", []):
        repo = entry.get("head_repo")
        heads.append((f'pr:{entry["number"]}', repo, entry["head_sha"]))
    if len(heads) > max_trees:
        raise RemoteTreeReconciliationError("REMOTE_TREE_REF_LIMIT_EXCEEDED")
    by_identity: dict[tuple[str, str], dict[str, Any]] = {}
    ref_records = []
    for label, source_repo, sha in heads:
        if not isinstance(sha, str) or not SHA.fullmatch(sha):
            raise RemoteTreeReconciliationError("REMOTE_TREE_REF_SHA_INVALID")
        if not isinstance(source_repo, str) or not REPO.fullmatch(source_repo):
            ref_records.append({"ref": label, "commit": sha,
                                "status": "HEAD_REPOSITORY_UNAVAILABLE"})
            continue
        key = (source_repo, sha)
        if key not in by_identity:
            url = f"{API}/repos/{source_repo}/git/trees/{sha}?recursive=1"
            packet = _get_json(url, get)
            truncated = packet.get("truncated")
            tree = packet.get("tree")
            if type(truncated) is not bool or not isinstance(tree, list):
                raise RemoteTreeReconciliationError("REMOTE_TREE_RESPONSE_INVALID")
            if packet.get("sha") is not None and (
                not isinstance(packet["sha"], str) or not SHA.fullmatch(packet["sha"])
            ):
                raise RemoteTreeReconciliationError("REMOTE_TREE_IDENTITY_INVALID")
            rows = []
            seen = set()
            for item in tree:
                if not isinstance(item, Mapping):
                    raise RemoteTreeReconciliationError("REMOTE_TREE_ENTRY_INVALID")
                if item.get("type") != "blob":
                    continue
                path, blob = item.get("path"), item.get("sha")
                if not isinstance(path, str) or not path or not isinstance(blob, str) or not SHA.fullmatch(blob):
                    raise RemoteTreeReconciliationError("REMOTE_TREE_BLOB_INVALID")
                if path in seen:
                    raise RemoteTreeReconciliationError("REMOTE_TREE_DUPLICATE_PATH")
                seen.add(path)
                if not path.lower().endswith(SUFFIXES):
                    continue
                if query is not None:
                    relevant = query.casefold() in path.casefold()
                else:
                    relevant = any(t in path.casefold() for t in TOKENS)
                if relevant:
                    rows.append({"path": path, "git_blob": blob})
            by_identity[key] = {"truncated": truncated, "matches": sorted(rows, key=lambda r:r["path"])}
        ref_records.append({"ref": label, "commit": sha,
                            "head_repository": source_repo,
                            "status": "TREE_TRUNCATED" if by_identity[key]["truncated"] else "TREE_ENUMERATED",
                            "tree_identity": {"repository":source_repo,"commit":sha},
                            "candidate_count": len(by_identity[key]["matches"])})
    candidate_matches = []
    for row in ref_records:
        identity = row.get("tree_identity")
        if not identity:
            continue
        for entry in by_identity[(identity["repository"], identity["commit"])]["matches"]:
            candidate_matches.append({"ref":row["ref"],"repository":identity["repository"],
                                      "commit":identity["commit"],**entry})
    if len(candidate_matches) > max_matches:
        # Do not present a partial table as a complete discovery result.
        displayed = candidate_matches[:max_matches]
    else:
        displayed = candidate_matches
    baseline = {} if baseline is None else baseline
    overlaps = []
    for item in candidate_matches:
        if item["path"] in baseline:
            overlaps.append({**item, "indexed_blob":baseline[item["path"]],
                             "blob_equal":item["git_blob"]==baseline[item["path"]]})
    errors = [x for x in ref_records if x["status"]!="TREE_ENUMERATED"]
    return {
        "schema": SCHEMA, "repository": repository,
        "census_branch_count":census["branch_count"],
        "census_open_pr_count":census["open_pr_count"],
        "ref_records":ref_records,
        "unique_source_tree_count":len(by_identity),
        "candidate_count":len(candidate_matches),
        "candidate_matches":displayed,
        "candidate_results_truncated":len(candidate_matches)>max_matches,
        "baseline_index_overlap":overlaps,
        "baseline_index_path_count":len(baseline),
        "remote_tree_errors":errors,
        "all_census_trees_enumerated":not errors,
        "source_content_and_proof_equivalence_checked":False,
        "atomic_remote_snapshot":False,
        "distributed_discovery_complete":False,
        "negative_existence_claim_authorized":False,
        "vm81_mutation_authority":False,
        "canonical_hash216_minted":False,
    }


def load_exact_checkout_baseline(root: Path) -> tuple[dict[str, str], str | None]:
    """Use existing Hash216 index only if its three records bind to HEAD.

    A stale index cannot silently become the reference against which remote
    branches are judged. The missing/error status is carried into the output.
    """
    import subprocess
    from hhs_runtime.hhs_pass220_index_first_discovery_v1 import GRAPH, LANE5, RECEIPT
    root=Path(root).resolve()
    try:
        head=subprocess.run(["git","rev-parse","HEAD"],cwd=root,check=True,
                            capture_output=True,text=True).stdout.strip()
        records=[json.loads((root/path).read_text("utf-8"))
                 for path in (GRAPH,LANE5,RECEIPT)]
    except (OSError,ValueError,subprocess.CalledProcessError):
        return {}, "INDEX_ARTIFACTS_UNAVAILABLE"
    if any(record.get("source_commit")!=head for record in records):
        return {}, "INDEX_CHECKOUT_REVISION_MISMATCH"
    rows=records[0].get("files")
    if not isinstance(rows,list):
        return {}, "INDEX_FILE_CENSUS_INVALID"
    result={}
    for row in rows:
        if not isinstance(row,Mapping):
            return {}, "INDEX_FILE_CENSUS_INVALID"
        path,blob,hash216=row.get("path"),row.get("git_blob"),row.get("hash216")
        if not isinstance(path,str) or not isinstance(blob,str) or not SHA.fullmatch(blob) or not isinstance(hash216,str) or len(hash216)!=216 or path in result:
            return {}, "INDEX_FILE_IDENTITY_INVALID"
        result[path]=blob
    return result, None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--query", default=None)\n    parser.add_argument("--index-root", default=None)
    args = parser.parse_args()
    packet = json.loads(Path(args.census).read_text("utf-8"))
    baseline, index_error = ({}, "INDEX_ROOT_NOT_SUPPLIED") if args.index_root is None else load_exact_checkout_baseline(Path(args.index_root))\n    result = reconcile_remote_trees(packet,query=args.query,baseline=baseline)\n    result["checkout_index_error"] = index_error\n    result["checkout_index_bound"] = index_error is None
    Path(args.output).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n","utf-8")
    print("Remote tree candidates:",result["candidate_count"])
    print("Uninspected or truncated trees:",len(result["remote_tree_errors"]))
