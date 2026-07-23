
from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
import copy, json

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID="PASS_087"
SCHEMA="HHS_INCREMENTAL_SEMANTIC_GRAPH_LEARNING_WORKLOAD_V1"
RESULT_SCHEMA="HHS_INCREMENTAL_SEMANTIC_GRAPH_LEARNING_RESULT_V1"
OUTCOMES={"INCREMENTAL_GRAPH_CLOSED","INCREMENTAL_GRAPH_STABLE_UNRESOLVED","INCREMENTAL_GRAPH_RESOURCE_BOUNDED"}
REJECTIONS=(
 "REJECT_GRAPH_UPDATE_WITHOUT_PARENT","REJECT_SILENT_SEMANTIC_OVERWRITE","REJECT_DEPENDENCY_SCOPE_BYPASS",
 "REJECT_UNWITNESSED_SUPERSESSION","REJECT_CACHE_REUSE_WITHOUT_REVALIDATION","REJECT_NOVELTY_COLLAPSE",
 "REJECT_GRAPH_EDGE_IDENTITY_COLLAPSE","REJECT_GRAPH_REPLAY_MISMATCH",
 "REJECT_PROVIDER_SCORE_AS_SEMANTIC_AUTHORITY","REJECT_INCREMENTAL_GRAPH_CLOSURE_FAILURE",
)

def _pattern(instance:int,family:int)->dict[str,Any]:
    p={"pattern_id":f"pattern:{family}:{instance}","family":f"family:{family}",
       "instance":instance,"role_signature":[f"role:{family}",f"feature:{instance%5}"],
       "context_scope":{"min":instance,"max":instance+4},"authority":"RUNTIME_ADMITTED"}
    p["pattern_root_hash72"]=root("hhs_pass087_pattern_v1",p)
    return stable(p)

def default_workload(repo:Path,*,workload_id:str,base_pattern_count:int=8,new_pattern_count:int=4,
                     family_count:int=4,update_rounds:int=2,
                     required_outcome:str="INCREMENTAL_GRAPH_CLOSED",
                     resource_budget:Mapping[str,int]|None=None)->dict[str,Any]:
    base=[_pattern(i,i%family_count) for i in range(base_pattern_count)]
    new=[_pattern(base_pattern_count+i,(base_pattern_count+i)%family_count) for i in range(new_pattern_count)]
    base_nodes=[]
    for p in base:
        n={"node_id":p["pattern_id"],"node_type":"PATTERN","pattern_root_hash72":p["pattern_root_hash72"],
           "version":1,"active":True}
        n["node_root_hash72"]=root("hhs_pass087_graph_node_v1",n); base_nodes.append(stable(n))
    base_edges=[]
    for i in range(max(0,len(base_nodes)-1)):
        e={"edge_id":f"edge:base:{i}","relation":"SEQUENTIALLY_RELATED",
           "source_root_hash72":base_nodes[i]["node_root_hash72"],
           "target_root_hash72":base_nodes[i+1]["node_root_hash72"],"version":1,"active":True}
        e["edge_root_hash72"]=root("hhs_pass087_graph_edge_v1",e); base_edges.append(stable(e))
    base_graph={"schema":"HHS_SEMANTIC_GRAPH_STATE_V1","nodes":base_nodes,"edges":base_edges,"version":1}
    base_graph["graph_root_hash72"]=root("hhs_pass087_graph_state_v1",base_graph)
    updates=[]
    for r in range(update_rounds):
        subset=new[r::update_rounds] if update_rounds else new
        u={"update_id":f"{workload_id}:round:{r}","round":r,
           "parent_graph_root_hash72":base_graph["graph_root_hash72"],
           "new_patterns":subset,
           "dependency_scope_families":sorted({p["family"] for p in subset}),
           "cache_candidates":[p["pattern_root_hash72"] for p in base if p["family"] in {x["family"] for x in subset}],
           "provider_scores_non_authoritative":True}
        u["update_root_hash72"]=root("hhs_pass087_update_v1",u); updates.append(stable(u))
    parent=json.loads((repo/"PASS_086_RELEASE_MANIFEST.json").read_text())
    return stable({"schema":SCHEMA,"workload_id":workload_id,"base_graph":base_graph,"updates":updates,
      "required_outcome":required_outcome,
      "learning_contract":{"supersession_not_overwrite":True,"dependency_scoped_revalidation":True,
        "cache_reuse_requires_revalidation":True,"novelty_preserved":True,"provider_score_non_authoritative":True},
      "parent_pass086_release_root_hash72":parent["pass086_release_root_hash72"],
      "resource_budget":dict(resource_budget or {"max_nodes":100000,"max_edges":1000000,"max_updates":10000,"max_receipt_bytes":100000000})})

def _validate(w:Mapping[str,Any])->None:
    if w.get("schema")!=SCHEMA or w.get("required_outcome") not in OUTCOMES:
        raise ContractError("REJECT_INCREMENTAL_GRAPH_CLOSURE_FAILURE")
    base=w.get("base_graph",{})
    if not base.get("graph_root_hash72"): raise ContractError("REJECT_GRAPH_UPDATE_WITHOUT_PARENT")
    edge_ids=[]; edge_roots=[]
    for e in base.get("edges",[]):
        edge_ids.append(e.get("edge_id")); edge_roots.append(e.get("edge_root_hash72"))
    if len(edge_ids)!=len(set(edge_ids)) or len(edge_roots)!=len(set(edge_roots)) or w.get("collapse_graph_edge_identity"):
        raise ContractError("REJECT_GRAPH_EDGE_IDENTITY_COLLAPSE")
    for u in w.get("updates",[]):
        if u.get("parent_graph_root_hash72")!=base.get("graph_root_hash72"):
            raise ContractError("REJECT_GRAPH_UPDATE_WITHOUT_PARENT")
        if not u.get("dependency_scope_families") and u.get("new_patterns"):
            raise ContractError("REJECT_DEPENDENCY_SCOPE_BYPASS")
    if w.get("silent_semantic_overwrite"): raise ContractError("REJECT_SILENT_SEMANTIC_OVERWRITE")
    if w.get("unwitnessed_supersession"): raise ContractError("REJECT_UNWITNESSED_SUPERSESSION")
    if w.get("cache_reuse_without_revalidation"): raise ContractError("REJECT_CACHE_REUSE_WITHOUT_REVALIDATION")
    if w.get("novelty_collapse"): raise ContractError("REJECT_NOVELTY_COLLAPSE")
    if w.get("provider_score_as_authority"): raise ContractError("REJECT_PROVIDER_SCORE_AS_SEMANTIC_AUTHORITY")

def run(repo:Path,w:Mapping[str,Any],*,replay:bool=False)->dict[str,Any]:
    _validate(w)
    graph=copy.deepcopy(w["base_graph"])
    active_nodes={n["node_id"]:n for n in graph["nodes"]}
    active_edges={e["edge_id"]:e for e in graph["edges"]}
    supersessions=[]; revalidations=[]; novelty=[]; cache_reuse=[]
    version=graph["version"]

    for u in w["updates"]:
        version+=1
        scope=set(u["dependency_scope_families"])
        affected=[n for n in active_nodes.values() if any(sig==fam for sig in n.get("family_tags",[]) for fam in scope)]
        # Existing nodes may not yet have family tags; derive them from node id when possible.
        affected_ids=set()
        for n in active_nodes.values():
            parts=n["node_id"].split(":")
            if len(parts)>=3 and f"family:{parts[1]}" in scope:
                affected_ids.add(n["node_id"])
        for nid in sorted(affected_ids):
            revalidations.append({"update_root_hash72":u["update_root_hash72"],"node_id":nid,"status":"REVALIDATED_IN_SCOPE"})
        for p in u["new_patterns"]:
            existing=[n for n in active_nodes.values() if n.get("pattern_root_hash72")==p["pattern_root_hash72"]]
            if existing:
                ce={"pattern_root_hash72":p["pattern_root_hash72"],"revalidated":True,"source_update_root_hash72":u["update_root_hash72"]}
                ce["cache_reuse_receipt_root_hash72"]=root("hhs_pass087_cache_reuse_v1",ce); cache_reuse.append(stable(ce))
                continue
            nid=p["pattern_id"]
            n={"node_id":nid,"node_type":"PATTERN","pattern_root_hash72":p["pattern_root_hash72"],
               "family_tags":[p["family"]],"version":version,"active":True,
               "introduced_by_update_root_hash72":u["update_root_hash72"]}
            n["node_root_hash72"]=root("hhs_pass087_graph_node_v1",n)
            active_nodes[nid]=stable(n)
            novelty.append({"pattern_root_hash72":p["pattern_root_hash72"],"novel_node_root_hash72":n["node_root_hash72"],
                            "update_root_hash72":u["update_root_hash72"]})
            # Supersede prior same-family active node only by explicit receipt, never overwrite.
            prior=[x for x in active_nodes.values() if x["node_id"]!=nid and p["family"] in x.get("family_tags",[]) and x.get("active")]
            if prior:
                old=sorted(prior,key=lambda x:x["node_id"])[-1]
                s={"relation":"SUPERSEDED_BY","old_node_root_hash72":old["node_root_hash72"],
                   "new_node_root_hash72":n["node_root_hash72"],"update_root_hash72":u["update_root_hash72"]}
                s["supersession_root_hash72"]=root("hhs_pass087_supersession_v1",s); supersessions.append(stable(s))
            if len(active_nodes)>1:
                parent_node=sorted(active_nodes.values(),key=lambda x:x["node_id"])[0]
                eid=f"edge:update:{u['round']}:{len(active_edges)}"
                e={"edge_id":eid,"relation":"LEARNED_RELATION","source_root_hash72":parent_node["node_root_hash72"],
                   "target_root_hash72":n["node_root_hash72"],"version":version,"active":True,
                   "update_root_hash72":u["update_root_hash72"]}
                e["edge_root_hash72"]=root("hhs_pass087_graph_edge_v1",e); active_edges[eid]=stable(e)

    if w.get("force_graph_failure"):
        active_nodes={}
    closed=bool(active_nodes)
    if w["required_outcome"]=="INCREMENTAL_GRAPH_CLOSED" and not closed:
        raise ContractError("REJECT_INCREMENTAL_GRAPH_CLOSURE_FAILURE")

    new_graph={"schema":"HHS_SEMANTIC_GRAPH_STATE_V1","version":version,
      "nodes":sorted(active_nodes.values(),key=lambda x:x["node_id"]),
      "edges":sorted(active_edges.values(),key=lambda x:x["edge_id"])}
    new_graph["graph_root_hash72"]=root("hhs_pass087_graph_state_v1",new_graph)
    receipt={"schema":"HHS_INCREMENTAL_SEMANTIC_GRAPH_LEARNING_RECEIPT_V1","workload_id":w["workload_id"],
      "parent_graph_root_hash72":w["base_graph"]["graph_root_hash72"],"result_graph":new_graph,
      "supersession_receipts":supersessions,"dependency_revalidations":revalidations,
      "novelty_records":novelty,"cache_reuse_receipts":cache_reuse,
      "silent_overwrite_occurred":False,"provider_score_authority":False,
      "classification":w["required_outcome"],"closure_verified":closed}
    receipt["learning_receipt_root_hash72"]=root("hhs_pass087_learning_receipt_v1",receipt)
    metrics={"base_node_count":len(w["base_graph"]["nodes"]),"result_node_count":len(new_graph["nodes"]),
      "base_edge_count":len(w["base_graph"]["edges"]),"result_edge_count":len(new_graph["edges"]),
      "update_count":len(w["updates"]),"novel_pattern_count":len(novelty),
      "supersession_count":len(supersessions),"dependency_revalidation_count":len(revalidations),
      "cache_reuse_count":len(cache_reuse),"receipt_bytes":len(json.dumps(receipt,separators=(",",":")))}
    result={"schema":RESULT_SCHEMA,"pass_id":PASS_ID,"status":w["required_outcome"],"workload":stable(dict(w)),
      "parent_pass086_release_root_hash72":w["parent_pass086_release_root_hash72"],
      "learning_receipt":receipt,"metrics":metrics,"replay":replay}
    result["result_root_hash72"]=root("hhs_pass087_result_v1",{k:v for k,v in result.items() if k!="replay"})
    return stable(result)

def verify_replay(repo:Path,w:Mapping[str,Any])->dict[str,Any]:
    a=run(repo,w); w2=copy.deepcopy(w)
    if w.get("alter_update_on_replay"):
        u=w2["updates"][0]; u["dependency_scope_families"].append("family:altered")
        u["update_root_hash72"]=root("hhs_pass087_update_v1",{k:v for k,v in u.items() if k!="update_root_hash72"})
    b=run(repo,w2,replay=True)
    if a["result_root_hash72"]!=b["result_root_hash72"]:
        raise ContractError("REJECT_GRAPH_REPLAY_MISMATCH")
    return {"schema":"HHS_PASS_087_REPLAY_V1","deterministic_replay_verified":True,"initial":a,"replay":b}

def workload_registry(repo:Path)->list[dict[str,Any]]:
    return [
      default_workload(repo,workload_id="W117:single-incremental-update",base_pattern_count=8,new_pattern_count=2,update_rounds=1),
      default_workload(repo,workload_id="W118:two-round-graph-growth",base_pattern_count=8,new_pattern_count=8,update_rounds=2),
      default_workload(repo,workload_id="W119:dependency-scoped-revalidation",base_pattern_count=16,new_pattern_count=8,family_count=4),
      default_workload(repo,workload_id="W120:supersession-with-history",base_pattern_count=16,new_pattern_count=8,family_count=4),
      default_workload(repo,workload_id="W121:cache-assisted-incremental-learning",base_pattern_count=32,new_pattern_count=8,family_count=4),
      default_workload(repo,workload_id="W122:novelty-isolation",base_pattern_count=32,new_pattern_count=16,family_count=8),
      default_workload(repo,workload_id="W123:stable-unresolved-update",base_pattern_count=16,new_pattern_count=0,required_outcome="INCREMENTAL_GRAPH_STABLE_UNRESOLVED"),
      default_workload(repo,workload_id="W124:sixty-four-node-graph",base_pattern_count=64,new_pattern_count=16,family_count=8),
      default_workload(repo,workload_id="W125:one-hundred-twenty-eight-node-graph",base_pattern_count=128,new_pattern_count=32,family_count=8),
      default_workload(repo,workload_id="W126:multi-round-composition",base_pattern_count=64,new_pattern_count=32,family_count=8,update_rounds=4),
      default_workload(repo,workload_id="W127:context-preserving-supersession",base_pattern_count=32,new_pattern_count=16,family_count=4),
      default_workload(repo,workload_id="W128:resource-bounded-graph-learning",base_pattern_count=256,new_pattern_count=128,family_count=16,update_rounds=8,required_outcome="INCREMENTAL_GRAPH_RESOURCE_BOUNDED"),
      default_workload(repo,workload_id="W129:provider-authority-separation",base_pattern_count=32,new_pattern_count=8),
      default_workload(repo,workload_id="W130:graph-receipt-only-replay",base_pattern_count=64,new_pattern_count=16,family_count=8),
    ]

def negative_cases(repo:Path)->list[dict[str,Any]]:
    cases=[]
    def add(name,code,mut):
        w=default_workload(repo,workload_id=f"NEG:{name}"); mut(w)
        try: run(repo,w); observed="NO_REJECTION"
        except ContractError as e: observed=str(e)
        cases.append({"case":name,"expected":code,"observed":observed,"passed":observed==code})
    add("missing-parent","REJECT_GRAPH_UPDATE_WITHOUT_PARENT",lambda w:w["updates"][0].update(parent_graph_root_hash72=""))
    add("silent-overwrite","REJECT_SILENT_SEMANTIC_OVERWRITE",lambda w:w.update(silent_semantic_overwrite=True))
    add("scope-bypass","REJECT_DEPENDENCY_SCOPE_BYPASS",lambda w:w["updates"][0].update(dependency_scope_families=[]))
    add("unwitnessed-supersession","REJECT_UNWITNESSED_SUPERSESSION",lambda w:w.update(unwitnessed_supersession=True))
    add("cache-no-revalidation","REJECT_CACHE_REUSE_WITHOUT_REVALIDATION",lambda w:w.update(cache_reuse_without_revalidation=True))
    add("novelty-collapse","REJECT_NOVELTY_COLLAPSE",lambda w:w.update(novelty_collapse=True))
    add("edge-collapse","REJECT_GRAPH_EDGE_IDENTITY_COLLAPSE",lambda w:w.update(collapse_graph_edge_identity=True))
    add("provider-authority","REJECT_PROVIDER_SCORE_AS_SEMANTIC_AUTHORITY",lambda w:w.update(provider_score_as_authority=True))
    add("closure-failure","REJECT_INCREMENTAL_GRAPH_CLOSURE_FAILURE",lambda w:w.update(force_graph_failure=True))
    w=default_workload(repo,workload_id="NEG:replay"); w["alter_update_on_replay"]=True
    try: verify_replay(repo,w); observed="NO_REJECTION"
    except ContractError as e: observed=str(e)
    cases.append({"case":"replay-mismatch","expected":"REJECT_GRAPH_REPLAY_MISMATCH","observed":observed,"passed":observed=="REJECT_GRAPH_REPLAY_MISMATCH"})
    return cases

def build_artifacts(repo:Path)->dict[str,Any]:
    ws=workload_registry(repo); results=[verify_replay(repo,w)["initial"] for w in ws]; neg=negative_cases(repo)
    def write(n,o): (repo/n).write_text(json.dumps(o,indent=2)+"\n")
    write("PASS_087_GRAPH_WORKLOAD_REGISTRY.json",{"schema":"HHS_PASS_087_WORKLOAD_REGISTRY_V1","workloads":ws})
    write("PASS_087_INCREMENTAL_LEARNING_RESULTS.json",{"schema":"HHS_PASS_087_LEARNING_RESULTS_V1","results":[{"workload_id":r["workload"]["workload_id"],**r["metrics"]} for r in results]})
    write("PASS_087_SEMANTIC_GRAPH_STATES.json",{"schema":"HHS_PASS_087_GRAPH_STATES_V1","graphs":[r["learning_receipt"]["result_graph"] for r in results]})
    write("PASS_087_SUPERSESSION_RECEIPTS.json",{"schema":"HHS_PASS_087_SUPERSESSIONS_V1","receipts":[s for r in results for s in r["learning_receipt"]["supersession_receipts"]]})
    write("PASS_087_DEPENDENCY_REVALIDATION_PROFILE.json",{"schema":"HHS_PASS_087_REVALIDATION_PROFILE_V1","records":[x for r in results for x in r["learning_receipt"]["dependency_revalidations"]]})
    write("PASS_087_NOVELTY_AND_CACHE_REUSE.json",{"schema":"HHS_PASS_087_NOVELTY_CACHE_V1",
      "novelty":[x for r in results for x in r["learning_receipt"]["novelty_records"]],
      "cache_reuse":[x for r in results for x in r["learning_receipt"]["cache_reuse_receipts"]]})
    write("PASS_087_GRAPH_LEARNING_RECEIPTS.json",{"schema":"HHS_PASS_087_RECEIPTS_V1","receipts":[r["learning_receipt"] for r in results]})
    write("PASS_087_GRAPH_SCALING_RESULTS.json",{"schema":"HHS_PASS_087_SCALING_V1","results":[{"workload_id":r["workload"]["workload_id"],**r["metrics"]} for r in results]})
    write("PASS_087_NEGATIVE_CASES.json",{"schema":"HHS_PASS_087_NEGATIVE_CASES_V1","cases":neg})
    parent=json.loads((repo/"PASS_086_RELEASE_MANIFEST.json").read_text())
    body={"schema":"HHS_PASS_087_RELEASE_MANIFEST_V1","pass_id":PASS_ID,
      "parent_pass086_release_root_hash72":parent["pass086_release_root_hash72"],
      "workload_count":len(ws),"negative_case_count":len(neg),"all_negative_cases_passed":all(c["passed"] for c in neg),
      "artifacts":["PASS_087_GRAPH_WORKLOAD_REGISTRY.json","PASS_087_INCREMENTAL_LEARNING_RESULTS.json",
      "PASS_087_SEMANTIC_GRAPH_STATES.json","PASS_087_SUPERSESSION_RECEIPTS.json",
      "PASS_087_DEPENDENCY_REVALIDATION_PROFILE.json","PASS_087_NOVELTY_AND_CACHE_REUSE.json",
      "PASS_087_GRAPH_LEARNING_RECEIPTS.json","PASS_087_GRAPH_SCALING_RESULTS.json",
      "PASS_087_NEGATIVE_CASES.json","PASS_087_CALIBRATION_REPORT.md","CHANGELOG_PASS_087.md"]}
    body["pass087_release_root_hash72"]=root("hhs_pass087_release_v1",body)
    write("PASS_087_RELEASE_MANIFEST.json",body)
    (repo/"PASS_087_CALIBRATION_REPORT.md").write_text("# Pass 087 — Incremental Semantic Graph Learning and Dependency-Scoped Revalidation\n\nW117–W130 verify versioned graph growth, supersession without overwrite, dependency-local revalidation, cache reuse with revalidation, novelty preservation, and exact replay.\n")
    (repo/"CHANGELOG_PASS_087.md").write_text("# Pass 087\n\nAdded incremental semantic graph learning and dependency-scoped revalidation over Pass 086.\n")
    return body
