"""Read-only exact Git-ref discovery layered after canonical Hash216 index.

Local Git refs are not exhaustive remote branches or PRs. Findings remain
candidate evidence and cannot authorize nonexistence or VM81 mutation.
"""
from __future__ import annotations
from pathlib import Path
import subprocess
from hhs_runtime.hhs_pass220_index_first_discovery_v1 import search_index, IndexDiscoveryError
from hhs_runtime.hhs_pass220_corpus_negative_claim_gate_v1 import validate_claim

class FederatedDiscoveryError(ValueError):
    pass

def _git(root, *args):
    try:
        return subprocess.run(["git",*args], cwd=root, check=True,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
    except (OSError,subprocess.CalledProcessError) as exc:
        raise FederatedDiscoveryError("GIT_REF_DISCOVERY_UNAVAILABLE") from exc

def search_federated_refs(root: Path, term: str, *, limit: int = 100, max_refs: int = 1000):
    root=Path(root).resolve()
    if not isinstance(term,str) or not term.strip() or len(term)>512:
        raise FederatedDiscoveryError("FEDERATED_QUERY_REQUIRED")
    if type(limit) is not int or not 1<=limit<=1000:
        raise FederatedDiscoveryError("FEDERATED_LIMIT_INVALID")
    if type(max_refs) is not int or not 1<=max_refs<=10000:
        raise FederatedDiscoveryError("FEDERATED_REF_LIMIT_INVALID")
    indexed=None
    index_error=None
    try:
        indexed=search_index(root,term,limit=limit)
    except IndexDiscoveryError as exc:
        index_error=str(exc)
    raw=_git(root,"for-each-ref","--format=%(refname)%09%(objectname)",
             "refs/heads","refs/remotes","refs/pull")
    refs=[]
    for line in raw.decode("utf-8").splitlines():
        if not line: continue
        ref,sep,sha=line.partition("\t")
        if not sep or not ref.startswith(("refs/heads/","refs/remotes/","refs/pull/")):
            raise FederatedDiscoveryError("FEDERATED_REF_RECORD_INVALID")
        if len(sha) not in (40,64) or any(c not in "0123456789abcdef" for c in sha):
            raise FederatedDiscoveryError("FEDERATED_REF_SHA_INVALID")
        refs.append((ref,sha))
    if len(refs)>max_refs:
        raise FederatedDiscoveryError("FEDERATED_REF_CENSUS_LIMIT_EXCEEDED")
    matches=[]
    for ref,sha in sorted(refs):
        for record in _git(root,"ls-tree","-r","-z",ref).split(b"\0"):
            if not record: continue
            metadata,sep,rawpath=record.partition(b"\t")
            parts=metadata.decode("ascii").split()
            if not sep or len(parts)!=3:
                raise FederatedDiscoveryError("FEDERATED_TREE_RECORD_INVALID")
            if parts[1]!="blob": continue
            path=rawpath.decode("utf-8","surrogateescape")
            if term.casefold() in path.casefold():
                matches.append({"path_or_ref":path,"revision":parts[2],
                                "ref":ref,"ref_commit":sha})
    indexed_matches=[] if indexed is None else indexed["matches"]
    witnesses=[{"path_or_ref":x["path_or_ref"],"revision":x["revision"]}
               for x in indexed_matches]
    witnesses += [{"path_or_ref":x["path_or_ref"],"revision":x["revision"]}
                  for x in matches[:limit]]
    report=validate_claim({"object":term,"status":"FOUND" if witnesses else "NOT_YET_LOCATED",
                           "checked_sources":witnesses})
    return {
        "schema":"HHS_PASS220_REF_FEDERATED_CORPUS_DISCOVERY_V1",
        "query":term,"index_first":True,"index_available":indexed is not None,
        "index_error":index_error,
        "indexed_match_count":0 if indexed is None else indexed["matched_count"],
        "indexed_matches":indexed_matches,
        "indexed_truncated":False if indexed is None else indexed["truncated"],
        "local_ref_count":len(refs),
        "enumerated_refs":[{"ref":r,"commit":sha} for r,sha in sorted(refs)],
        "ref_match_count":len(matches),"ref_matches":matches[:limit],
        "ref_matches_truncated":len(matches)>limit,"report":report,
        "all_remote_refs_fetched":False,"all_open_prs_verified":False,
        "distributed_discovery_complete":False,
        "negative_existence_claim_authorized":False,
        "vm81_mutation_authority":False,"canonical_hash216_minted":False,
    }
