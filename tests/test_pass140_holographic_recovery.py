import copy, base64
import pytest
from hhs_runtime.holographic_entanglement_recovery_v1 import HolographicRecovery, RecoveryError, root

REQ={"request_id":"r140","artifacts":[
 {"artifact_id":"source","path":"src/a.txt","content":"alpha"},
 {"artifact_id":"proof","path":"proof/a.json","content":"{\"proved\":true}","dependencies":["source"]},
 {"artifact_id":"release","path":"release.txt","content":"released","dependencies":["proof"]}]}

def enc(): return HolographicRecovery().encode(copy.deepcopy(REQ))

def reroot(e): e["receipt_root"]=root({k:v for k,v in e.items() if k!="receipt_root"})

def test_intact_roundtrip_and_dependency_order():
 e=enc();r=HolographicRecovery().recover(e)
 assert r["conclusion"]=="RECOVERY_CLOSED"
 assert r["recovery_order"]==["source","proof","release"]
 assert [base64.b64decode(x["content_b64"]).decode() for x in r["recovered"]]==["alpha",'{"proved":true}',"released"]

def test_one_corrupt_data_shard_is_recovered_byte_exact():
 e=enc();s=e["artifacts"][1]["shards"][2];s["payload_b64"]=base64.b64encode(b"x"*len(base64.b64decode(s["payload_b64"]))).decode();reroot(e)
 r=HolographicRecovery().recover(e); row=[x for x in r["recovered"] if x["artifact_id"]=="proof"][0]
 assert row["status"]=="BYTE_EXACT_RECOVERED" and row["recovered_shard"]==2

def test_missing_parity_is_reconstructed_without_data_loss():
 e=enc();e["artifacts"][0]["shards"].pop();reroot(e)
 r=HolographicRecovery().recover(e);assert r["conclusion"]=="RECOVERY_CLOSED"

def test_two_missing_shards_fail_closed_and_block_dependents():
 e=enc();e["artifacts"][0]["shards"]=e["artifacts"][0]["shards"][2:];reroot(e)
 r=HolographicRecovery().recover(e);assert r["conclusion"]=="RECOVERY_PARTIAL_OR_FAILED"
 assert any(x["status"]=="UNRECOVERABLE_REDUNDANCY_EXCEEDED" for x in r["failures"])
 assert any(x["artifact_id"]=="proof" and not x["dependency_ok"] for x in r["failures"])

def test_metadata_corruption_rejected():
 e=enc();e["artifacts"][0]["metadata"]["size"]+=1;reroot(e)
 r=HolographicRecovery().recover(e);assert r["failures"][0]["status"]=="METADATA_CORRUPT"

def test_impact_analysis_tracks_transitive_dependents():
 a=HolographicRecovery().analyze_impact(enc(),["source"])
 assert a["impacted"]==["proof","release","source"] and a["recovery_order"]==["source","proof","release"]

def test_cycle_and_unknown_dependency_rejected():
 bad=copy.deepcopy(REQ);bad["artifacts"][0]["dependencies"]=["release"]
 with pytest.raises(RecoveryError):HolographicRecovery().encode(bad)
 bad=copy.deepcopy(REQ);bad["artifacts"][0]["dependencies"]=["ghost"]
 with pytest.raises(RecoveryError):HolographicRecovery().encode(bad)

def test_deterministic_replay(): assert enc()==enc()
