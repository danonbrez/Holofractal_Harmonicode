#!/usr/bin/env python3
"""Build restartable Pass219 thread dependency graph from GitHub inventory.

Edges are explicit PR-number references only; file overlap is a conflict
signal, never an invented dependency. All open branches receive graph nodes.
"""
import json
import re
import sys
from pathlib import Path

PR_REF = re.compile(r"(?<![A-Za-z0-9])#([1-9][0-9]*)\b")
CONTRACT = "PASS219_CPP_LEAN_PROOF_ENFORCEMENT"
def graph_from_inventory(inventory):
    prs = inventory["open_prs"]
    nodes = {CONTRACT: {"kind": "contract", "status": "required", "next": "validate native C++/Lean/Hash216 admission"}}
    edges = []
    for pr in prs:
        ident = "pr:" + str(pr["number"])
        blockers = pr.get("blocking_checks", [])
        nodes[ident] = {"kind": "pull_request", "ref": pr["head"], "head_sha": pr["head_sha"],
                        "status": "candidate" if pr["integration_candidate"] else "unfinished",
                        "blockers": blockers, "next": "verify changed files, proofs and merge prerequisites",
                        "url": pr["url"]}
        # Every branch entry participates; this is a gate, not a claim of dependency between PRs.
        edges.append({"from": ident, "to": CONTRACT, "kind": "must_pass_contract"})
    for b in inventory["orphan_branches_without_open_pr"]:
        ident = "branch:" + b
        nodes[ident] = {"kind":"unpaired_branch", "ref":b, "status":"unreviewed",
                        "next":"compare exact head with main, recover unfinished thread objectives"}
        edges.append({"from":ident,"to":CONTRACT,"kind":"must_pass_contract"})
    known = {pr["number"] for pr in prs}
    for pr in prs:
        # PR body text MUST be included by inventory collector. Mentions are hints
        # until maintainer verifies the causal ordering.
        mentions = {int(n) for n in PR_REF.findall(pr.get("body") or "")}
        for number in sorted(mentions & known - {pr["number"]}):
            edges.append({"from":"pr:"+str(pr["number"]), "to":"pr:"+str(number),
                          "kind":"referenced_pr_unverified"})
    # Mainline repair obligations remain graph members even after source PR merge.
    # Source PR references are provenance links, not automatically verified dependencies.
    for repair in inventory.get("mainline_repair_obligations", []):
        ident = "repair:" + str(repair["source_pr"])
        if ident in nodes:
            raise ValueError("duplicate mainline repair")
        nodes[ident] = {
            "kind": "mainline_repair", "status": "unfinished",
            "source_pr": repair["source_pr"],
            "main_sha": repair["main_sha"],
            "blockers": list(repair["blockers"]),
            "next": repair["next"],
            "proof_closure_verified": False,
            "native_replay_verified": False,
            "exact_main_verified": False}
        edges.append({"from": ident, "to": CONTRACT,
                      "kind": "must_pass_contract"})
        edges.append({"from": ident, "to": "source_pr:" + str(repair["source_pr"]),
                      "kind": "inherited_provenance_non_scheduling"})
    assert len(nodes) == len(prs) + len(inventory["orphan_branches_without_open_pr"]) + 1 + len(inventory.get("mainline_repair_obligations", []))
    # Convert only explicitly verified prerequisites into scheduling edges.
    # Unverified references stay review hints and MUST NOT enter the order.
    verified = [e for e in edges if e["kind"] == "verified_prerequisite"]
    remaining = {k for k in nodes if k != CONTRACT}
    order = []
    while remaining:
        ready = sorted(k for k in remaining if not any(
            e["from"] == k and e["to"] in remaining for e in verified))
        if not ready:
            raise ValueError("verified prerequisite cycle; fail closed")
        order.extend(ready)
        remaining.difference_update(ready)
    return {"schema":"HHS_PASS219_UNFINISHED_THREADS_DEPENDENCY_GRAPH_V1",
            "review_order_not_merge_authority": order,
            "source_schema":inventory["schema"],
            "repository":inventory["repository"],
            "nodes":nodes,"edges":edges,
            "admission":{
                "proof":"Pass219 canonical Lean theorem and dependency identities",
                "execution":"Pass219 C++ ordered tensor compiler semantics",
                "normalization":"Delta=1, exact rational/BigInt, no scalar phase cancellation",
                "security":"inherited signed VM81, Hash72 and Hash216 admission/replay",
                "ready":"green checks + code ancestry + satisfied explicit dependencies + signed native replay",
                "merge":"no merge without fresh guarded verification"},
            "policy":"Referenced PRs are candidate edges; do not auto-merge or infer prerequisites from titles."}

def main():
    inventory=json.loads(Path(sys.argv[1]).read_text(encoding="utf8"))
    manifest_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    if manifest_path:
        manifest=json.loads(manifest_path.read_text(encoding="utf8"))
        inventory["mainline_repair_obligations"]=manifest["records"]
    graph=graph_from_inventory(inventory)
    Path(sys.argv[2]).write_text(json.dumps(graph, indent=2, sort_keys=True)+"\n", encoding="utf8")
    print("NODES",len(graph["nodes"]),"EDGES",len(graph["edges"]))
if __name__=="__main__":
    main()
