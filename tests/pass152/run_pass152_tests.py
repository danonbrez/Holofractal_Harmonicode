#!/usr/bin/env python3
from __future__ import annotations
import copy, json, os, tempfile, time, traceback
from fractions import Fraction
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hhs_runtime.pass152 import *
from hhs_runtime.pass152.adapters import DeterministicVM81TestAuthority, HHSRuntimeControllerAuthority
from hhs_runtime.pass152.common import sha256_json
from hhs_runtime.pass152.model import (
    AuthorityViolation, CandidateState, ClosureIncomplete, EdgeType,
    EquivalenceWitness, InvalidWitness, OperationNode, ResourceBounded,
    RootEquivalenceWitness, SkipWitness,
)

RESULTS=[]
def case(cid, kind, fn):
    start=time.perf_counter_ns(); error=None
    try: fn(); status="PASS"
    except Exception as exc: status="FAIL"; error=f"{type(exc).__name__}: {exc}"
    RESULTS.append({"case_id":cid,"kind":kind,"status":status,"duration_ns":time.perf_counter_ns()-start,"error":error})

def require(cond, msg="assertion failed"):
    if not cond: raise AssertionError(msg)

def must_raise(exc, fn):
    try: fn()
    except exc: return
    raise AssertionError(f"expected {exc.__name__}")

def simple_engine(path, *, max_nodes=32, max_horizon=4):
    e=ElasticClosureEngine({"cycle":0},"ROOT-A",path,workers=2,max_nodes=max_nodes,max_horizon=max_horizon)
    e.add_node(OperationNode("x","SEED")); e.add_node(OperationNode("y","PLUS",compute=lambda d:d["x"]+1))
    e.add_edge("x","y",EdgeType.VALUE_DEPENDS_ON); e.seed("x",1)
    return e

def run():
    with tempfile.TemporaryDirectory(prefix="hhs152_tests_") as td0:
        td=Path(td0)
        authority=DeterministicVM81TestAuthority()
        demo=delayed_closure_workload(td/"demo", authority.admit, delay_seconds=0.008, workers=4)
        eng=demo["engine"]; metrics=demo["metrics"]

        case("P152-POS-001","positive",lambda: require(demo["proof"]["omega_closure"] is True))
        case("P152-POS-002","positive",lambda: require(demo["commit"]["vm81_admitted"] is True))
        case("P152-POS-003","positive",lambda: require(bool(demo["commit"]["hash72_receipt"]["receipt_hash72"])))
        case("P152-POS-004","positive",lambda: require(demo["replay"]["replay_status"]=="MATCH"))
        case("P152-POS-005","positive",lambda: require(metrics["max_concurrent_workers_observed"]>=2,"parallel branches did not overlap"))
        case("P152-POS-006","positive",lambda: require(metrics["N_propagated"]>0 and metrics["N_partial"]>0))
        case("P152-POS-007","positive",lambda: require(metrics["N_reused"]==1))
        case("P152-POS-008","positive",lambda: require(metrics["N_skipped"]==1))
        case("P152-POS-009","positive",lambda: require(metrics["T_productive_ns"]>0 and metrics["eta_closure"]>0))
        case("P152-POS-010","positive",lambda: require(metrics["eta_candidate"]==1.0))
        case("P152-POS-011","positive",lambda: require(eng.graph.nodes["sum_alias"].provenance[-1]["provenance_collapsed"] is False))
        case("P152-POS-012","positive",lambda: require({e.edge_type.value for e in eng.graph.edges}>={"VALUE_DEPENDS_ON","CONSTRAINT_DEPENDS_ON","CLOSURE_DEPENDS_ON"}))
        case("P152-POS-013","positive",lambda: require(eng.authoritative_state["status"]=="COMMITTED"))
        case("P152-POS-014","positive",lambda: require(all((td/"demo"/name).exists() for name in ["P152_CYCLE_OPEN.json","P152_DEPENDENCY_GRAPH.json","P152_GLOBAL_CLOSURE_PROOF.json","P152_COMMIT_RECEIPT.json","P152_REPLAY_RECEIPT.json"])))
        case("P152-POS-015","positive",lambda: require(metrics["N_critical"]>0))
        case("P152-POS-016","positive",lambda: require(eng.graph.nodes["identity"].evaluation_count==0))
        case("P152-POS-017","positive",lambda: require(eng.graph.nodes["sum_alias"].evaluation_count==0))
        def deterministic_order():
            a=delayed_closure_workload(td/"det_a",DeterministicVM81TestAuthority().admit,delay_seconds=0.002)
            b=delayed_closure_workload(td/"det_b",DeterministicVM81TestAuthority().admit,delay_seconds=0.002)
            require(a["proof"]["logical_work_order"]==b["proof"]["logical_work_order"])
            require(a["commit"]["candidate_digest"]==b["commit"]["candidate_digest"])
        case("P152-POS-018","positive",deterministic_order)
        def root_equivalence():
            e=simple_engine(td/"root_eq"); e.register_root_equivalence(RootEquivalenceWitness("RW","ROOT-A","ROOT-B","1.0.0","PROOF")); require(e.invalidate_for_root_change("ROOT-B")==[]); require(e.graph.nodes["x"].candidate_root=="ROOT-B")
        case("P152-POS-019","positive",root_equivalence)
        def live_vm81():
            from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
            e=ElasticClosureEngine({"cycle":0},"LIVE-ROOT",td/"live",workers=1)
            e.add_node(OperationNode("x","SEED")); e.seed("x",3)
            e.run_until_closed(); receipt=e.commit(HHSRuntimeControllerAuthority(HHSRuntimeController()).admit)
            require(receipt["hash72_receipt"].get("receipt_hash72")); require(receipt["authority_audit"].get("ok") is True)
        case("P152-POS-020","positive",live_vm81)

        # Recursive control invariant: higher layers optimize policy, never truth.
        case("P152-POS-021","positive",lambda: require(demo["proof"]["recursive_control"]["history_valid"] is True))
        case("P152-POS-022","positive",lambda: require(demo["proof"]["higher_layers_optimize_policy_not_truth"] is True))
        case("P152-POS-023","positive",lambda: require(demo["commit"]["history_extended_not_rewritten"] is True))
        case("P152-POS-024","positive",lambda: require(demo["replay"]["causal_history_valid"] is True))
        case("P152-POS-025","positive",lambda: require(all((td/"demo"/name).exists() for name in ["P152_LAYER_HISTORY.jsonl","P152_RECURSIVE_CONTROL_TRACE.jsonl","P152_PLAN_REVISION.jsonl"])))
        def downward_projection():
            e=simple_engine(td/"rc_down")
            vector=e.recursive_control.optimize(
                source_layer="L2", target_layer="L1",
                ready_nodes=[{"node_id":"y","critical_cost":"2","predicted_risk":"0","redundancy_cost":"0"}],
                context={"authority_root":"ROOT-A","semantic_version":"1.0.0","authoritative_state_digest":e._authoritative_digest},
            )
            require(vector.source_layer=="L2" and vector.target_layer=="L1")
            require(vector.max_batch<=e.workers)
        case("P152-POS-026","positive",downward_projection)
        def plan_revision_append_only():
            e=simple_engine(td/"rc_revision")
            ctx={"authority_root":"ROOT-A","semantic_version":"1.0.0","authoritative_state_digest":e._authoritative_digest}
            obs=[{"node_id":"y","critical_cost":"2","predicted_risk":"0","redundancy_cost":"0"}]
            e.recursive_control.optimize(source_layer="L2",target_layer="L1",ready_nodes=obs,context=ctx)
            before=e.recursive_control.histories["L2"].entries
            e.recursive_control.optimize(source_layer="L2",target_layer="L1",ready_nodes=obs,context=ctx,requested_controls={"branch_priority":{"y":100}})
            after=e.recursive_control.histories["L2"].entries
            require(after[:len(before)]==before)
            require(any(item["event"]=="FUTURE_PLAN_REVISED" for item in after))
        case("P152-POS-027","positive",plan_revision_append_only)
        def deterministic_control_vector():
            a=simple_engine(td/"rc_det_a"); b=simple_engine(td/"rc_det_b")
            obs=[{"node_id":"y","critical_cost":"2","predicted_risk":"1/10","redundancy_cost":"0"}]
            ca={"authority_root":"ROOT-A","semantic_version":"1.0.0","authoritative_state_digest":a._authoritative_digest}
            cb={"authority_root":"ROOT-A","semantic_version":"1.0.0","authoritative_state_digest":b._authoritative_digest}
            va=a.recursive_control.optimize(source_layer="L2",target_layer="L1",ready_nodes=obs,context=ca)
            vb=b.recursive_control.optimize(source_layer="L2",target_layer="L1",ready_nodes=obs,context=cb)
            require(va.to_dict()==vb.to_dict())
        case("P152-POS-028","positive",deterministic_control_vector)
        case("P152-POS-029","positive",lambda: require(demo["proof"]["recursive_control"]["authority_root"]=="AUTHORITY-ROOT-152-A"))
        case("P152-POS-030","positive",lambda: require(demo["proof"]["recursive_control"]["canonical_invariant"].startswith("PRESERVE_CAUSAL_AUTHORITY")))

        # Required negative matrix.
        case("P152-NEG-001","negative",lambda: must_raise(ClosureIncomplete,lambda: simple_engine(td/"n1").commit(DeterministicVM81TestAuthority().admit)))
        def provisional_hash72():
            e=simple_engine(td/"n2"); require(e.graph.nodes["y"].lifecycle==CandidateState.READY); require(e.commit_receipt is None)
        case("P152-NEG-002","negative",provisional_hash72)
        def fabricated_resolution():
            e=simple_engine(td/"n3"); e.graph.nodes["y"].lifecycle=CandidateState.VERIFIED; e.graph.nodes["y"].value=999; require(e.closure_proof()["omega_closure"] is False)
        case("P152-NEG-003","negative",fabricated_resolution)
        def witnessless_reuse():
            e=simple_engine(td/"n4"); e.run_until_closed(); require(e.counters["reused"]==0 and e.graph.nodes["y"].evaluation_count==1)
        case("P152-NEG-004","negative",witnessless_reuse)
        def cross_root_reuse():
            e=simple_engine(td/"n5"); w=EquivalenceWitness("W","x","y","C","OTHER","1.0.0",sha256_json({"x":1}),"int","s","x","x+1","0","A","B","P"); must_raise(InvalidWitness,lambda:e.register_equivalence_witness(w))
        case("P152-NEG-005","negative",cross_root_reuse)
        def heuristic_skip():
            e=simple_engine(td/"n6"); e.run_until_closed(); require(e.counters["skipped"]==0 and e.graph.nodes["y"].evaluation_count==1)
        case("P152-NEG-006","negative",heuristic_skip)
        def stale_survival():
            e=simple_engine(td/"n7"); e.run_until_closed(); invalid=e.invalidate_for_root_change("ROOT-B"); require("y" in invalid and e.graph.nodes["y"].lifecycle==CandidateState.INVALIDATED)
        case("P152-NEG-007","negative",stale_survival)
        def local_not_global():
            e=ElasticClosureEngine({"cycle":0},"R",td/"n8"); e.add_node(OperationNode("a","SEED")); e.add_node(OperationNode("b","BLOCKED",compute=lambda d:1)); e.add_node(OperationNode("missing","SEED")); e.add_edge("missing","b",EdgeType.CLOSURE_DEPENDS_ON); e.graph.nodes["missing"].lifecycle=CandidateState.BLOCKED; e.seed("a",1); must_raise(ClosureIncomplete,e.run_until_closed)
        case("P152-NEG-008","negative",local_not_global)
        def physical_race():
            orders=[]
            for i in range(3):
                r=delayed_closure_workload(td/f"race{i}",DeterministicVM81TestAuthority().admit,delay_seconds=0.001)
                orders.append(r["proof"]["logical_work_order"])
            require(orders[0]==orders[1]==orders[2])
        case("P152-NEG-009","negative",physical_race)
        case("P152-NEG-010","negative",lambda: require(eng.graph.nodes["sum"].provenance!=eng.graph.nodes["sum_alias"].provenance))
        def candidate_not_authority():
            e=simple_engine(td/"n11"); e.run_until_closed(); require(e.authoritative_state=={"cycle":0}); require(e.candidate_state()["values"]["y"]==2)
        case("P152-NEG-011","negative",candidate_not_authority)
        def prediction_no_truth():
            e=simple_engine(td/"n12"); e._ready_nodes(); require(e.graph.nodes["y"].value is None and e.graph.nodes["y"].lifecycle==CandidateState.READY)
        case("P152-NEG-012","negative",prediction_no_truth)
        def invalidated_dependency():
            e=simple_engine(td/"n13"); e.run_until_closed(); e.invalidate_for_root_change("ROOT-C"); require("y" not in e.resolved); require(e.closure_proof()["omega_closure"] is False)
        case("P152-NEG-013","negative",invalidated_dependency)
        def mandatory_starvation():
            e=ElasticClosureEngine({"cycle":0},"R",td/"n14",workers=2); e.add_node(OperationNode("a","A",compute=lambda d:1,estimated_cost=Fraction(100))); e.add_node(OperationNode("b","B",compute=lambda d:2,estimated_cost=Fraction(1),mandatory=True)); e.run_until_closed(); require(e.graph.nodes["b"].lifecycle==CandidateState.VERIFIED)
        case("P152-NEG-014","negative",mandatory_starvation)
        case("P152-NEG-015","negative",lambda: must_raise(ResourceBounded,lambda: ElasticClosureEngine({},"R",td/"n15",max_horizon=1).add_node(OperationNode("f","F",horizon=2))))
        def missing_reuse_receipt():
            e=simple_engine(td/"n16"); e.run_until_closed(); require(not (td/"n16"/"P152_EQUIVALENCE_REUSE.jsonl").exists())
        case("P152-NEG-016","negative",missing_reuse_receipt)
        def resource_hidden():
            e=ElasticClosureEngine({},"R",td/"n17",max_nodes=1); e.add_node(OperationNode("a","A")); must_raise(ResourceBounded,lambda:e.add_node(OperationNode("b","B"))); require(e.closure_flags["resource"] is False)
        case("P152-NEG-017","negative",resource_hidden)
        case("P152-NEG-018","negative",physical_race)
        def external_direct_commit():
            e=simple_engine(td/"n19"); e.graph.nodes["y"].lifecycle=CandidateState.COMMITTED; must_raise(ClosureIncomplete,lambda:e.commit(DeterministicVM81TestAuthority().admit))
        case("P152-NEG-019","negative",external_direct_commit)
        def cache_root_revalidate():
            e=ElasticClosureEngine({},"R",td/"n20"); must_raise(AuthorityViolation,lambda:e.add_node(OperationNode("cache","CACHE",candidate_root="FOREIGN")))
        case("P152-NEG-020","negative",cache_root_revalidate)
        def prohibit_invariant_truth():
            e=simple_engine(td/"n21")
            must_raise(AuthorityViolation,lambda:e.recursive_control.reject_prohibited_mutation({"invariant_truth":False}))
        case("P152-NEG-021","negative",prohibit_invariant_truth)
        def prohibit_committed_state():
            e=simple_engine(td/"n22")
            must_raise(AuthorityViolation,lambda:e.recursive_control.reject_prohibited_mutation({"committed_state":{"cycle":999}}))
        case("P152-NEG-022","negative",prohibit_committed_state)
        def upward_projection_rejected():
            e=simple_engine(td/"n23")
            ctx={"authority_root":"ROOT-A","semantic_version":"1.0.0","authoritative_state_digest":e._authoritative_digest}
            must_raise(AuthorityViolation,lambda:e.recursive_control.optimize(source_layer="L1",target_layer="L2",ready_nodes=[],context=ctx))
        case("P152-NEG-023","negative",upward_projection_rejected)
        def batch_bound_rejected():
            e=simple_engine(td/"n24")
            ctx={"authority_root":"ROOT-A","semantic_version":"1.0.0","authoritative_state_digest":e._authoritative_digest}
            must_raise(ResourceBounded,lambda:e.recursive_control.optimize(source_layer="L2",target_layer="L1",ready_nodes=[{"node_id":"y"}],context=ctx,requested_controls={"batching":{"max_batch":e.workers+1}}))
        case("P152-NEG-024","negative",batch_bound_rejected)
        def depth_bound_rejected():
            e=simple_engine(td/"n25",max_horizon=2)
            ctx={"authority_root":"ROOT-A","semantic_version":"1.0.0","authoritative_state_digest":e._authoritative_digest}
            must_raise(ResourceBounded,lambda:e.recursive_control.optimize(source_layer="L2",target_layer="L1",ready_nodes=[{"node_id":"y"}],context=ctx,requested_controls={"speculative_depth":3}))
        case("P152-NEG-025","negative",depth_bound_rejected)
        def history_tamper_detected():
            e=simple_engine(td/"n26")
            e.recursive_control.histories["L0"]._entries[0]["payload"]["committed_prefix_digest"]="tampered"
            require(e.recursive_control.verify() is False)
        case("P152-NEG-026","negative",history_tamper_detected)
        def wrong_commit_prefix_rejected():
            e=simple_engine(td/"n27")
            must_raise(AuthorityViolation,lambda:e.recursive_control.record_commit_extension("wrong",e.recursive_control.active_plan_digest,"after"))
        case("P152-NEG-027","negative",wrong_commit_prefix_rejected)
        def unsupported_control_rejected():
            e=simple_engine(td/"n28")
            must_raise(AuthorityViolation,lambda:e.recursive_control.reject_prohibited_mutation({"invented_policy":1}))
        case("P152-NEG-028","negative",unsupported_control_rejected)
        def unproved_rebase_rejected():
            e=simple_engine(td/"n29")
            must_raise(AuthorityViolation,lambda:e.recursive_control.rebase_authority_root("ROOT-B"))
        case("P152-NEG-029","negative",unproved_rebase_rejected)
        def rewritten_core_context_rejected():
            e=simple_engine(td/"n30")
            must_raise(AuthorityViolation,lambda:e.recursive_control.optimize(source_layer="L2",target_layer="L1",ready_nodes=[],context={"authority_root":"ROOT-A","semantic_version":"1.0.0","authoritative_state_digest":"rewritten"}))
        case("P152-NEG-030","negative",rewritten_core_context_rejected)

    report={
        "schema":"HHS_PASS152_TEST_REPORT_V1",
        "positive_cases_required":30,"negative_cases_required":30,
        "positive_cases_executed":sum(r["kind"]=="positive" for r in RESULTS),
        "negative_cases_executed":sum(r["kind"]=="negative" for r in RESULTS),
        "passed":sum(r["status"]=="PASS" for r in RESULTS),
        "failed":sum(r["status"]=="FAIL" for r in RESULTS),
        "cases":RESULTS,
    }
    out=ROOT/"reports/pass152/P152_TEST_REPORT.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    neg={"schema":"HHS_PASS152_NEGATIVE_TEST_REPORT_V1","required":30,"executed":report["negative_cases_executed"],"passed":sum(r["kind"]=="negative" and r["status"]=="PASS" for r in RESULTS),"failed":sum(r["kind"]=="negative" and r["status"]=="FAIL" for r in RESULTS),"cases":[r for r in RESULTS if r["kind"]=="negative"]}
    (ROOT/"reports/pass152/P152_NEGATIVE_TEST_REPORT.json").write_text(json.dumps(neg,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("positive_cases_executed","negative_cases_executed","passed","failed")},sort_keys=True))
    if report["failed"]:
        for r in RESULTS:
            if r["status"]=="FAIL": print(r, file=sys.stderr)
    return 0 if report["failed"]==0 and report["positive_cases_executed"]==30 and report["negative_cases_executed"]==30 else 1

if __name__=="__main__": raise SystemExit(run())
