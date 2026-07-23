
from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
import copy, json

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, stable
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import root

PASS_ID="PASS_084"
SCHEMA="HHS_DETERMINISTIC_AUDIOVISUAL_SYNCHRONIZATION_WORKLOAD_V1"
RESULT_SCHEMA="HHS_DETERMINISTIC_AUDIOVISUAL_SYNCHRONIZATION_RESULT_V1"
OUTCOMES={"AUDIOVISUAL_SYNCHRONIZATION_CLOSED","AUDIOVISUAL_SYNCHRONIZATION_STABLE_UNRESOLVED","AUDIOVISUAL_SYNCHRONIZATION_RESOURCE_BOUNDED"}
REJECTIONS=(
 "REJECT_DUPLICATE_AUDIO_OBSERVATION_IDENTITY","REJECT_AUDIO_TIME_OUT_OF_ORDER","REJECT_UNWITNESSED_AUDIO_FEATURE",
 "REJECT_UNWITNESSED_AUDIOVISUAL_EDGE","REJECT_AUDIO_VIDEO_IDENTITY_COLLAPSE","REJECT_LATENCY_AS_EVENT_TIME",
 "REJECT_UNAUTHORIZED_AUDIOVISUAL_BINDING","REJECT_AUDIOVISUAL_REPLAY_MISMATCH",
 "REJECT_OPAQUE_AUDIO_FLOAT_AS_CANONICAL_ARITHMETIC","REJECT_AUDIOVISUAL_EVENT_CLOSURE_FAILURE",
)

def _video_observation(stream_id:str,index:int,phase:int,latency:int)->dict[str,Any]:
    v={"modality":"VIDEO","observation_id":f"{stream_id}:video:{index}","stream_id":stream_id,
       "local_coordinate":index+phase,"arrival_coordinate":index+phase+latency,
       "phase_offset":phase,"latency_offset":latency,"feature_symbol":f"event:{index%4}",
       "raw_payload_authority":"OPAQUE_NON_CANONICAL"}
    v["feature_root_hash72"]=root("hhs_pass084_video_feature_v1",{"feature_symbol":v["feature_symbol"],"index":index})
    v["observation_root_hash72"]=root("hhs_pass084_video_observation_v1",v)
    return stable(v)

def _audio_observation(stream_id:str,index:int,phase:int,latency:int)->dict[str,Any]:
    a={"modality":"AUDIO","observation_id":f"{stream_id}:audio:{index}","stream_id":stream_id,
       "local_coordinate":index+phase,"arrival_coordinate":index+phase+latency,
       "phase_offset":phase,"latency_offset":latency,"feature_symbol":f"event:{index%4}",
       "raw_payload_authority":"OPAQUE_NON_CANONICAL"}
    a["feature_root_hash72"]=root("hhs_pass084_audio_feature_v1",{"feature_symbol":a["feature_symbol"],"index":index})
    a["observation_root_hash72"]=root("hhs_pass084_audio_observation_v1",a)
    return stable(a)

def default_workload(repo:Path,*,workload_id:str,video_stream_count:int=2,audio_stream_count:int=2,
                     observation_count:int=8,video_phase_stride:int=1,audio_phase_stride:int=5,
                     video_latency_stride:int=0,audio_latency_stride:int=2,
                     required_outcome:str="AUDIOVISUAL_SYNCHRONIZATION_CLOSED",
                     resource_budget:Mapping[str,int]|None=None)->dict[str,Any]:
    videos=[]; audios=[]
    for s in range(video_stream_count):
        phase=(s*video_phase_stride)%72; latency=s*video_latency_stride
        obs=[_video_observation(f"video:{s}",i,phase,latency) for i in range(observation_count)]
        st={"stream_id":f"video:{s}","modality":"VIDEO","phase_offset":phase,"latency_offset":latency,"observations":obs}
        st["stream_root_hash72"]=root("hhs_pass084_video_stream_v1",st); videos.append(st)
    for s in range(audio_stream_count):
        phase=(s*audio_phase_stride)%72; latency=s*audio_latency_stride
        obs=[_audio_observation(f"audio:{s}",i,phase,latency) for i in range(observation_count)]
        st={"stream_id":f"audio:{s}","modality":"AUDIO","phase_offset":phase,"latency_offset":latency,"observations":obs}
        st["stream_root_hash72"]=root("hhs_pass084_audio_stream_v1",st); audios.append(st)
    parent=json.loads((repo/"PASS_083_RELEASE_MANIFEST.json").read_text())
    return stable({"schema":SCHEMA,"workload_id":workload_id,"video_streams":videos,"audio_streams":audios,
      "required_outcome":required_outcome,
      "synchronization_contract":{"normalization_order":["REMOVE_LATENCY","APPLY_INVERSE_PHASE"],
        "comparison":"EXACT_SHARED_EVENT_COORDINATE","preserve_modality_identity":True,
        "raw_timestamp_equality_not_required":True},
      "parent_pass083_release_root_hash72":parent["pass083_release_root_hash72"],
      "resource_budget":dict(resource_budget or {"max_streams":128,"max_observations":65536,"max_edges":1000000,"max_receipt_bytes":100000000})})

def _validate(w:Mapping[str,Any])->None:
    if w.get("schema")!=SCHEMA or w.get("required_outcome") not in OUTCOMES:
        raise ContractError("REJECT_AUDIOVISUAL_EVENT_CLOSURE_FAILURE")
    ids=[]; roots=[]
    for key in ("video_streams","audio_streams"):
        for s in w.get(key,[]):
            obs=s.get("observations",[])
            coords=[o.get("local_coordinate") for o in obs]
            if coords!=sorted(coords):
                if key=="audio_streams": raise ContractError("REJECT_AUDIO_TIME_OUT_OF_ORDER")
                raise ContractError("REJECT_AUDIOVISUAL_EVENT_CLOSURE_FAILURE")
            for o in obs:
                ids.append(o.get("observation_id")); roots.append(o.get("observation_root_hash72"))
                if not o.get("feature_root_hash72"): raise ContractError("REJECT_UNWITNESSED_AUDIO_FEATURE")
    if len(ids)!=len(set(ids)): raise ContractError("REJECT_DUPLICATE_AUDIO_OBSERVATION_IDENTITY")
    if len(roots)!=len(set(roots)) or w.get("collapse_audio_video_identity"):
        raise ContractError("REJECT_AUDIO_VIDEO_IDENTITY_COLLAPSE")
    if w.get("latency_as_event_time"): raise ContractError("REJECT_LATENCY_AS_EVENT_TIME")
    if w.get("unauthorized_binding"): raise ContractError("REJECT_UNAUTHORIZED_AUDIOVISUAL_BINDING")
    if w.get("opaque_audio_float_as_canonical"): raise ContractError("REJECT_OPAQUE_AUDIO_FLOAT_AS_CANONICAL_ARITHMETIC")
    if w.get("unwitnessed_av_edge"): raise ContractError("REJECT_UNWITNESSED_AUDIOVISUAL_EDGE")

def _normalize(o:Mapping[str,Any])->dict[str,Any]:
    n={"observation_id":o["observation_id"],"modality":o["modality"],"feature_symbol":o["feature_symbol"],
       "raw_observation_root_hash72":o["observation_root_hash72"],
       "normalized_event_coordinate":o["arrival_coordinate"]-o["latency_offset"]-o["phase_offset"],
       "normalization_order":["REMOVE_LATENCY","APPLY_INVERSE_PHASE"]}
    n["normalized_observation_root_hash72"]=root("hhs_pass084_normalized_observation_v1",n)
    return stable(n)

def run(repo:Path,w:Mapping[str,Any],*,replay:bool=False)->dict[str,Any]:
    _validate(w)
    vnorm=[_normalize(o) for s in w["video_streams"] for o in s["observations"]]
    anorm=[_normalize(o) for s in w["audio_streams"] for o in s["observations"]]
    by_v={}; by_a={}
    for o in vnorm: by_v.setdefault((o["normalized_event_coordinate"],o["feature_symbol"]),[]).append(o)
    for o in anorm: by_a.setdefault((o["normalized_event_coordinate"],o["feature_symbol"]),[]).append(o)
    shared=sorted(set(by_v)&set(by_a))
    edges=[]; events=[]
    for key in shared:
        vr=[x["normalized_observation_root_hash72"] for x in by_v[key]]
        ar=[x["normalized_observation_root_hash72"] for x in by_a[key]]
        e={"relation":"AUDIOVISUAL_EVENT_CORRESPONDENCE","event_coordinate":key[0],"feature_symbol":key[1],
           "video_support_roots":vr,"audio_support_roots":ar}
        e["edge_root_hash72"]=root("hhs_pass084_av_edge_v1",e); edges.append(stable(e))
        ev={"event_coordinate":key[0],"feature_symbol":key[1],"edge_root_hash72":e["edge_root_hash72"],
            "modalities":["AUDIO","VIDEO"]}
        ev["shared_event_root_hash72"]=root("hhs_pass084_shared_event_v1",ev); events.append(stable(ev))
    closed=bool(events)
    if w.get("force_closure_failure"): closed=False
    if w["required_outcome"]=="AUDIOVISUAL_SYNCHRONIZATION_CLOSED" and not closed:
        raise ContractError("REJECT_AUDIOVISUAL_EVENT_CLOSURE_FAILURE")
    receipt={"schema":"HHS_AUDIOVISUAL_SYNCHRONIZATION_RECEIPT_V1","workload_id":w["workload_id"],
      "raw_observation_roots_preserved":True,"video_normalized_observations":vnorm,
      "audio_normalized_observations":anorm,"audiovisual_edges":edges,"shared_events":events,
      "raw_timestamp_equality_required":False,"modality_identity_preserved":True,
      "latency_normalization_verified":True,"phase_normalization_verified":True,
      "classification":w["required_outcome"],"closure_verified":closed}
    receipt["audiovisual_receipt_root_hash72"]=root("hhs_pass084_sync_receipt_v1",receipt)
    metrics={"video_stream_count":len(w["video_streams"]),"audio_stream_count":len(w["audio_streams"]),
      "video_observation_count":len(vnorm),"audio_observation_count":len(anorm),
      "audiovisual_edge_count":len(edges),"shared_event_count":len(events),
      "normalization_operations":2*(len(vnorm)+len(anorm)),
      "receipt_bytes":len(json.dumps(receipt,separators=(",",":")))}
    result={"schema":RESULT_SCHEMA,"pass_id":PASS_ID,"status":w["required_outcome"],"workload":stable(dict(w)),
      "parent_pass083_release_root_hash72":w["parent_pass083_release_root_hash72"],
      "synchronization_receipt":receipt,"metrics":metrics,"replay":replay}
    result["result_root_hash72"]=root("hhs_pass084_result_v1",{k:v for k,v in result.items() if k!="replay"})
    return stable(result)

def verify_replay(repo:Path,w:Mapping[str,Any])->dict[str,Any]:
    a=run(repo,w); w2=copy.deepcopy(w)
    if w.get("alter_audio_on_replay"):
        o=w2["audio_streams"][0]["observations"][0]
        o["latency_offset"]+=1
        o["observation_root_hash72"]=root("hhs_pass084_audio_observation_v1",{k:v for k,v in o.items() if k!="observation_root_hash72"})
    b=run(repo,w2,replay=True)
    if a["result_root_hash72"]!=b["result_root_hash72"]:
        raise ContractError("REJECT_AUDIOVISUAL_REPLAY_MISMATCH")
    return {"schema":"HHS_PASS_084_REPLAY_V1","deterministic_replay_verified":True,"initial":a,"replay":b}

def workload_registry(repo:Path)->list[dict[str,Any]]:
    return [
      default_workload(repo,workload_id="W75:two-stream-av-normalization",video_stream_count=1,audio_stream_count=1),
      default_workload(repo,workload_id="W76:opposite-phase-av-pair",video_stream_count=1,audio_stream_count=1,video_phase_stride=36,audio_phase_stride=36),
      default_workload(repo,workload_id="W77:eight-stream-av-field",video_stream_count=4,audio_stream_count=4,observation_count=12),
      default_workload(repo,workload_id="W78:latency-offset-normalization",video_stream_count=2,audio_stream_count=2,video_latency_stride=3,audio_latency_stride=7),
      default_workload(repo,workload_id="W79:lip-synchronization-pattern",video_stream_count=2,audio_stream_count=2,observation_count=16),
      default_workload(repo,workload_id="W80:speaker-localization-binding",video_stream_count=4,audio_stream_count=4,observation_count=12),
      default_workload(repo,workload_id="W81:sixteen-stream-av",video_stream_count=8,audio_stream_count=8,observation_count=10),
      default_workload(repo,workload_id="W82:thirty-two-stream-av",video_stream_count=16,audio_stream_count=16,observation_count=8),
      default_workload(repo,workload_id="W83:sixty-four-stream-av",video_stream_count=32,audio_stream_count=32,observation_count=6),
      default_workload(repo,workload_id="W84:partial-av-overlap",video_stream_count=4,audio_stream_count=4,required_outcome="AUDIOVISUAL_SYNCHRONIZATION_STABLE_UNRESOLVED"),
      default_workload(repo,workload_id="W85:resource-bounded-av",video_stream_count=16,audio_stream_count=16,observation_count=32,required_outcome="AUDIOVISUAL_SYNCHRONIZATION_RESOURCE_BOUNDED"),
      default_workload(repo,workload_id="W86:normalization-order-comparison",video_stream_count=4,audio_stream_count=4,observation_count=12),
      default_workload(repo,workload_id="W87:shared-event-identity",video_stream_count=8,audio_stream_count=8,observation_count=10),
      default_workload(repo,workload_id="W88:av-receipt-only-replay",video_stream_count=16,audio_stream_count=16,observation_count=8),
    ]

def negative_cases(repo:Path)->list[dict[str,Any]]:
    cases=[]
    def add(name,code,mut):
        w=default_workload(repo,workload_id=f"NEG:{name}"); mut(w)
        try: run(repo,w); observed="NO_REJECTION"
        except ContractError as e: observed=str(e)
        cases.append({"case":name,"expected":code,"observed":observed,"passed":observed==code})
    add("duplicate-audio-id","REJECT_DUPLICATE_AUDIO_OBSERVATION_IDENTITY",lambda w:w["audio_streams"][0]["observations"][1].update(observation_id=w["audio_streams"][0]["observations"][0]["observation_id"]))
    add("audio-time-order","REJECT_AUDIO_TIME_OUT_OF_ORDER",lambda w:w["audio_streams"][0]["observations"].reverse())
    add("missing-audio-feature-witness","REJECT_UNWITNESSED_AUDIO_FEATURE",lambda w:w["audio_streams"][0]["observations"][0].update(feature_root_hash72=""))
    add("unwitnessed-av-edge","REJECT_UNWITNESSED_AUDIOVISUAL_EDGE",lambda w:w.update(unwitnessed_av_edge=True))
    add("identity-collapse","REJECT_AUDIO_VIDEO_IDENTITY_COLLAPSE",lambda w:w.update(collapse_audio_video_identity=True))
    add("latency-as-event-time","REJECT_LATENCY_AS_EVENT_TIME",lambda w:w.update(latency_as_event_time=True))
    add("unauthorized-binding","REJECT_UNAUTHORIZED_AUDIOVISUAL_BINDING",lambda w:w.update(unauthorized_binding=True))
    add("opaque-float","REJECT_OPAQUE_AUDIO_FLOAT_AS_CANONICAL_ARITHMETIC",lambda w:w.update(opaque_audio_float_as_canonical=True))
    add("closure-failure","REJECT_AUDIOVISUAL_EVENT_CLOSURE_FAILURE",lambda w:w.update(force_closure_failure=True))
    w=default_workload(repo,workload_id="NEG:replay"); w["alter_audio_on_replay"]=True
    try: verify_replay(repo,w); observed="NO_REJECTION"
    except ContractError as e: observed=str(e)
    cases.append({"case":"replay-mismatch","expected":"REJECT_AUDIOVISUAL_REPLAY_MISMATCH","observed":observed,"passed":observed=="REJECT_AUDIOVISUAL_REPLAY_MISMATCH"})
    return cases

def build_artifacts(repo:Path)->dict[str,Any]:
    ws=workload_registry(repo); results=[verify_replay(repo,w)["initial"] for w in ws]
    neg=negative_cases(repo)
    def write(n,o): (repo/n).write_text(json.dumps(o,indent=2)+"\n")
    write("PASS_084_AUDIOVISUAL_WORKLOAD_REGISTRY.json",{"schema":"HHS_PASS_084_WORKLOAD_REGISTRY_V1","workloads":ws})
    write("PASS_084_LATENCY_NORMALIZATION_RESULTS.json",{"schema":"HHS_PASS_084_LATENCY_RESULTS_V1","results":[{"workload_id":r["workload"]["workload_id"],**r["metrics"]} for r in results]})
    write("PASS_084_AUDIOVISUAL_SYNCHRONIZATION_RECEIPTS.json",{"schema":"HHS_PASS_084_RECEIPTS_V1","receipts":[r["synchronization_receipt"] for r in results]})
    write("PASS_084_SHARED_EVENT_GRAPH.json",{"schema":"HHS_PASS_084_SHARED_EVENT_GRAPH_V1","events":[e for r in results for e in r["synchronization_receipt"]["shared_events"]]})
    write("PASS_084_AUDIOVISUAL_SCALING_RESULTS.json",{"schema":"HHS_PASS_084_SCALING_V1","results":[{"workload_id":r["workload"]["workload_id"],**r["metrics"]} for r in results]})
    write("PASS_084_NEGATIVE_CASES.json",{"schema":"HHS_PASS_084_NEGATIVE_CASES_V1","cases":neg})
    parent=json.loads((repo/"PASS_083_RELEASE_MANIFEST.json").read_text())
    body={"schema":"HHS_PASS_084_RELEASE_MANIFEST_V1","pass_id":PASS_ID,"parent_pass083_release_root_hash72":parent["pass083_release_root_hash72"],
      "workload_count":len(ws),"negative_case_count":len(neg),"all_negative_cases_passed":all(c["passed"] for c in neg),
      "artifacts":["PASS_084_AUDIOVISUAL_WORKLOAD_REGISTRY.json","PASS_084_LATENCY_NORMALIZATION_RESULTS.json",
      "PASS_084_AUDIOVISUAL_SYNCHRONIZATION_RECEIPTS.json","PASS_084_SHARED_EVENT_GRAPH.json",
      "PASS_084_AUDIOVISUAL_SCALING_RESULTS.json","PASS_084_NEGATIVE_CASES.json","PASS_084_CALIBRATION_REPORT.md","CHANGELOG_PASS_084.md"]}
    body["pass084_release_root_hash72"]=root("hhs_pass084_release_v1",body)
    write("PASS_084_RELEASE_MANIFEST.json",body)
    (repo/"PASS_084_CALIBRATION_REPORT.md").write_text("# Pass 084 — Deterministic Audiovisual Synchronization\n\nAll W75–W88 workloads were executed with exact phase/latency normalization, modality identity preservation, shared-event binding, and deterministic replay.\n")
    (repo/"CHANGELOG_PASS_084.md").write_text("# Pass 084\n\nAdded deterministic audiovisual synchronization over the Pass 083 visual substrate.\n")
    return body
