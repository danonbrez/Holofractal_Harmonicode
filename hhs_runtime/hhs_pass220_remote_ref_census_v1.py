"""Paginated remote GitHub branch and open-PR census, read-only.

This is a ref observation, not an atomic snapshot or exhaustive mathematical
content audit. No remote ref enumeration authorizes absence or VM81 mutation.
"""
from __future__ import annotations
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Mapping

SCHEMA = "HHS_PASS220_REMOTE_REF_CENSUS_V1"
SHA = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
API = "https://api.github.com"

class RemoteCensusError(ValueError):
    pass

def http_page(url: str, *, token: str | None = None) -> tuple[Any, str | None]:
    headers = {"Accept":"application/vnd.github+json",
               "X-GitHub-Api-Version":"2022-11-28",
               "User-Agent":"hhs-pass220-corpus-discovery"}
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urllib.request.urlopen(urllib.request(url, headers=headers), timeout=30) as response:
            return json.load(response), response.headers.get("Link")
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        raise RemoteCensusError("REMOTE_CENSUS_API_UNAVAILABLE") from exc

def next_link(links: str | None) -> str | None:
    if not links:
        return None
    for part in links.split(","):
        if 'rel="next"' not in part:
            continue
        match = re.match(r"\s*<([^>]+)>", part)
        if not match:
            raise RemoteCensusError("REMOTE_CENSUS_INVALID_LINK")
        target = urllib.parse.urlsplit(match.group(1))
        if target.scheme != "https" or target.netloc != "api.github.com":
            raise RemoteCensusError("REMOTE_CENSUS_UNTRUSTED_NEXT_LINK")
        return match.group(1)
    return None

def pages(url: str, get: Callable[[str], tuple[Any,str|None]], *,
          max_pages: int) -> list[Mapping[str, Any]]:
    result = []
    visited = set()
    while url:
        if url in visited:
            raise RemoteCensusError("REMOTE_CENSUS_PAGINATION_CYCLE")
        if len(visited) >= max_pages:
            raise RemoteCensusError("REMOTE_CENSUS_PAGE_LIMIT_REACHED")
        visited.add(url)
        rows, links = get(url)
        if not isinstance(rows, list) or any(not isinstance(x,Mapping) for x in rows):
            raise RemoteCensusError("REMOTE_CENSUS_INVALID_PAGE")
        result.extend(rows)
        url = next_link(links)
    return result

def inventory_remote_refs(repository: str, *,
                          get: Callable[[str], tuple[Any,str|None]] | None = None,
                          max_pages: int = 100) -> dict[str, Any]:
    if not isinstance(repository,str) or not REPO.fullmatch(repository):
        raise RemoteCensusError("REMOTE_CENSUS_REPOSITORY_INVALID")
    if type(max_pages) is not int or not 1<=max_pages<=1000:
        raise RemoteCensusError("REMOTE_CENSUS_MAX_PAGES_INVALID")
    if get is None:
        token=os.environ.get("GITHUB_TOKEN")
        get=lambda url: http_page(url, token=token)
    prefix=f"{API}/repos/{repository}"
    br=pages(prefix+"/branches?per_page=100", get, max_pages=max_pages)
    pr=pages(prefix+"/pulls?state=open&per_page=100", get, max_pages=max_pages)
    branches={}
    pulls={}
    for row in br:
        name=row.get("name")
        commit=row.get("commit")
        sha=commit.get("sha") if isinstance(commit,Mapping) else None
        if not isinstance(name,str) or not name or not isinstance(sha,str) or not SHA.fullmatch(sha):
            raise RemoteCensusError("REMOTE_CENSUS_INVALID_BRANCH")
        if name in branches:
            raise RemoteCensusError("REMOTE_CENSUS_DUPLICATE_BRANCH")
        branches[name]=sha
    for row in pr:
        num=row.get("number")
        head=row.get("head")
        if type(num) is not int or num<1 or not isinstance(head,Mapping):
            raise RemoteCensusError("REMOTE_CENSUS_INVALID_PR")
        sha=head.get("sha")
        head_ref=head.get("ref")
        head_repo=head.get("repo")
        full=head_repo.get("full_name") if isinstance(head_repo,Mapping) else None
        if not isinstance(sha,str) or not SHA.fullmatch(sha) or not isinstance(head_ref,str) or not head_ref:
            raise RemoteCensusError("REMOTE_CENSUS_INVALID_PR_HEAD")
        if num in pulls:
            raise RemoteCensusError("REMOTE_CENSUS_DUPLICATE_PR")
        pulls[num]={"head_sha":sha,"head_ref":head_ref,
                    "head_repo":full,"head_accessible":full is not None}
    return {"schema":SCHEMA,"repository":repository,
            "branches":[{"name":k,"sha":branches[k]} for k in sorted(branches)],
            "open_pulls":[{"number":k,**pulls[k]} for k in sorted(pulls)],
            "branch_count":len(branches),"open_pr_count":len(pulls),
            "branch_pages_exhausted":True,"open_pr_pages_exhausted":True,
            "atomic_remote_snapshot":False,
            "trees_and_proof_contents_exhaustively_inspected":False,
            "distributed_discovery_complete":False,
            "negative_existence_claim_authorized":False,
            "vm81_mutation_authority":False,"canonical_hash216_minted":False}

def compare_local_refs(census: Mapping[str,Any],
                       local_refs: Mapping[str,str]) -> dict[str,Any]:
    missing=[]
    outdated=[]
    expected=[("refs/remotes/origin/"+row["name"],row["sha"]) for row in census["branches"]]
    expected += [(f'refs/pull/{row["number"]}/head',row["head_sha"]) for row in census["open_pulls"]]
    for ref,sha in expected:
        if ref not in local_refs:
            missing.append({"ref":ref,"remote_sha":sha})
        elif local_refs[ref]!=sha:
            outdated.append({"ref":ref,"remote_sha":sha,"local_sha":local_refs[ref]})
    return {"missing_local_refs":missing,"outdated_local_refs":outdated,
            "local_ref_alignment_verified":not missing and not outdated,
            "remote_trees_verified":False,"negative_existence_claim_authorized":False}

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",required=True)
    options=parser.parse_args()
    print(json.dumps(inventory_remote_refs(options.repo),sort_keys=True))
