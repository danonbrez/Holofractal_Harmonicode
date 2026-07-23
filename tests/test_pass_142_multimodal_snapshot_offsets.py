import base64, copy
import pytest
from hhs_runtime.harmonicode_multimodal_redundant_snapshot_offsets_v1 import MultimodalSnapshotOffsets, SnapshotError

def request():
    return {"request_id":"p142","global_state":{"phase":17,"unit":"xy","active":True,"nested":{"phase":17}},
      "modalities":[
        {"id":"text","mime_type":"text/plain","text":"HARMONICODE phase phase phase"},
        {"id":"json","mime_type":"application/json","json":{"x":1,"y":2,"phase":17}},
        {"id":"image","mime_type":"image/png","data_base64":base64.b64encode(b"\x89PNG\r\nsynthetic").decode()}],
      "forked_operations":[
        {"id":"ingress","operation":{"kind":"INGRESS"}},
        {"id":"parse","depends_on":["ingress"],"operation":{"kind":"PARSE"}},
        {"id":"reason-a","depends_on":["parse"],"operation":{"kind":"FORK"}},
        {"id":"reason-b","depends_on":["parse"],"operation":{"kind":"FORK"}},
        {"id":"merge","depends_on":["reason-a","reason-b"],"operation":{"kind":"MERGE"}},
        {"id":"release","depends_on":["merge"],"operation":{"kind":"RELEASE"}}]}

def test_round_trip_multimodal():
    rt=MultimodalSnapshotOffsets(); rec=rt.encode(request()); out=rt.reconstruct(rec)
    assert out["status"]=="SNAPSHOT_REPLAYED"
    assert out["global_state_snapshot"]["state"]["phase"]==17
    assert len(out["global_state_snapshot"]["modalities"])==3

def test_one_corrupt_offset_recovered():
    rt=MultimodalSnapshotOffsets(); rec=rt.encode(request()); x=copy.deepcopy(rec)
    # Corrupt all redundant instances of slot 2.
    for row in x["fork_receipts"]:
        if row["global_snapshot_offset"]["offset_slot"]==2:
            row["global_snapshot_offset"]["payload_base64"]=base64.b64encode(b"bad").decode()
            row["receipt_root"] = __import__('hashlib').sha256(__import__('json').dumps({k:v for k,v in row.items() if k!='receipt_root'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    x["receipt_root"] = __import__('hashlib').sha256(__import__('json').dumps({k:v for k,v in x.items() if k!='receipt_root'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    out=rt.reconstruct(x); assert out["recovered_offset_slots"]==[2]

def test_two_missing_offsets_fail_closed():
    rt=MultimodalSnapshotOffsets(); rec=rt.encode(request()); x=copy.deepcopy(rec)
    x["fork_receipts"]=[r for r in x["fork_receipts"] if r["global_snapshot_offset"]["offset_slot"] not in {1,2}]
    x["receipt_root"] = __import__('hashlib').sha256(__import__('json').dumps({k:v for k,v in x.items() if k!='receipt_root'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    with pytest.raises(SnapshotError,match="UNRECOVERABLE"): rt.reconstruct(x)

def test_dependency_index_query():
    rt=MultimodalSnapshotOffsets(); rec=rt.encode(request()); q=rt.query_dependency(rec,"merge")
    assert q["parents"]==["reason-a","reason-b"] and q["children"]==["release"]

def test_cycle_rejected():
    q=request(); q["forked_operations"][0]["depends_on"]=["release"]
    with pytest.raises(SnapshotError,match="DEPENDENCY_CYCLE"): MultimodalSnapshotOffsets().encode(q)

def test_invalid_modality_rejected():
    q=request(); q["modalities"][2]["data_base64"]="***"
    with pytest.raises(SnapshotError,match="INVALID_MODALITY_BASE64"): MultimodalSnapshotOffsets().encode(q)

def test_receipt_mutation_detected():
    rt=MultimodalSnapshotOffsets(); rec=rt.encode(request()); rec["snapshot"]["compressed_length"]+=1
    assert rt.validate_receipt(rec)["valid"] is False

def test_deterministic_receipt():
    rt=MultimodalSnapshotOffsets(); assert rt.encode(request())==rt.encode(request())
