from __future__ import annotations
import ctypes,json,struct,subprocess
from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_i047_native_library_training_dataset_v1 import Pass220I047DatasetError,REFERENCE_ORIGIN,build_library_training_record,materialize_dataset,typed_value_from_bytes,validate_library_training_record

def _lib(tmp):
    c=tmp/"f.c"; c.write_text("#include <stdint.h>\nint64_t hhs_affine_i64(int64_t x,int64_t y){return x*3+y*2;}\n")
    so=tmp/"libi047.so"; subprocess.run(["cc","-shared","-fPIC","-std=c11","-O2",str(c),"-o",str(so)],check=True); return so

def _i64(v): return typed_value_from_bytes(data_type="i64",encoding="little-endian-twos-complement",payload=struct.pack("<q",v),semantic_value=str(v))
def _meta(n): return {"library_id":"i047-affine","library_format":"ELF_SHARED_OBJECT","architecture":"x86_64","abi":"SYSV_AMD64","provenance":"I047_TEST","codec_boundary":{"ingress_encoder_id":"I64_IN","egress_decoder_id":"I64_OUT","preserve_external_contract":True},"byte_regions":[{"region_id":"IMAGE","start":0,"length":n,"kind":"RAW_LIBRARY_BYTES"}],"entrypoints":[{"entrypoint_id":"affine","symbol":"hhs_affine_i64","inputs":[{"name":"x","data_type":"i64","encoding":"little-endian-twos-complement"},{"name":"y","data_type":"i64","encoding":"little-endian-twos-complement"}],"outputs":[{"name":"return","data_type":"i64","encoding":"little-endian-twos-complement"}],"side_effect_class":"PURE","math_operator_identities":["MUL_I64","ADD_I64"],"phase_relationships":["ORDERED_DEPENDENCY"],"timing_constraints":["SOURCE_ORDER_NOT_SCHEDULER_AUTHORITY"],"vm81_relationships":["LANE5_BIND"],"rna_relationships":["LANE5_TRANSCRIBE"]}],"relationships":[{"relation_id":"R0","relation_type":"BYTE_REGION_CONTAINS_SYMBOL","source":"IMAGE","target":"affine","order":0,"attributes":{}}],"dependencies":[],"hash72_hash216_lineage_hints":["BIND_AT_LANE5_HYDRATION"]}
def _vectors(so):
    f=ctypes.CDLL(str(so)).hhs_affine_i64; f.argtypes=[ctypes.c_int64,ctypes.c_int64]; f.restype=ctypes.c_int64; out=[]
    for i,(x,y) in enumerate(((0,0),(1,2),(-7,9),(1234567,-765432))):
        z=int(f(x,y)); out.append({"vector_id":f"v{i}","entrypoint_id":"affine","reference_origin":REFERENCE_ORIGIN,"inputs":[_i64(x),_i64(y)],"outputs":[_i64(z)],"observation":{"source_library_invoked":True,"observed_output":True,"captured_by":"ctypes-source-library"}})
    return out

def test_record_contract(tmp_path):
    so=_lib(tmp_path); raw=so.read_bytes(); r=build_library_training_record(source_bytes=raw,metadata=_meta(len(raw)),reference_vectors=_vectors(so)); assert validate_library_training_record(r)["ok"]
    assert r["source"]["raw_bytes_preserved"] and r["lane5_handoff"]["algebraic_lifting_requested"] and not r["lane5_handoff"]["algebraic_lifting_performed_here"]
    assert r["lane5_handoff"]["latency_phase_scheduling_requested"] and not r["lane5_handoff"]["latency_phase_scheduling_performed_here"] and r["lane5_handoff"]["ingress_egress_codec_preserved"]
    assert r["authority"]["candidate_only"] and not r["authority"]["canonical_hash216_committed"] and all(v["outputs"][0]["data_type"]=="i64" for v in r["reference_vectors"])

def test_materialization_exact_and_deterministic(tmp_path):
    so=_lib(tmp_path); raw=so.read_bytes(); m=_meta(len(raw)); v=_vectors(so); a=materialize_dataset(((raw,m,v),),tmp_path/"a"); b=materialize_dataset(((raw,m,v),),tmp_path/"b")
    assert a["dataset_root_sha256"]==b["dataset_root_sha256"]; h=a["source_sha256s"][0]; assert (tmp_path/"a"/"raw"/(h+".bin")).read_bytes()==raw; assert validate_library_training_record(json.loads((tmp_path/"a"/"records.jsonl").read_text().strip()))["ok"]

def test_byte_change_changes_identity(tmp_path):
    so=_lib(tmp_path); raw=so.read_bytes(); m=_meta(len(raw)); v=_vectors(so); a=build_library_training_record(source_bytes=raw,metadata=m,reference_vectors=v); x=bytearray(raw); x[-1]^=1; b=build_library_training_record(source_bytes=bytes(x),metadata=m,reference_vectors=v); assert a["record_sha256"]!=b["record_sha256"]

def test_output_type_drift_rejected(tmp_path):
    so=_lib(tmp_path); raw=so.read_bytes(); v=_vectors(so); v[0]["outputs"][0]["data_type"]="u64"
    with pytest.raises(Pass220I047DatasetError,match="type/encoding drift"): build_library_training_record(source_bytes=raw,metadata=_meta(len(raw)),reference_vectors=v)
def test_unobserved_output_rejected(tmp_path):
    so=_lib(tmp_path); raw=so.read_bytes(); v=_vectors(so); v[0]["observation"]["source_library_invoked"]=False
    with pytest.raises(Pass220I047DatasetError,match="observed source-library invocation"): build_library_training_record(source_bytes=raw,metadata=_meta(len(raw)),reference_vectors=v)
def test_codec_metadata_required(tmp_path):
    so=_lib(tmp_path); raw=so.read_bytes(); m=_meta(len(raw)); del m["codec_boundary"]["egress_decoder_id"]
    with pytest.raises(Pass220I047DatasetError,match="codec_boundary missing keys"): build_library_training_record(source_bytes=raw,metadata=m,reference_vectors=_vectors(so))
def test_byte_region_bounded(tmp_path):
    so=_lib(tmp_path); raw=so.read_bytes(); m=_meta(len(raw)); m["byte_regions"][0]["length"]+=1
    with pytest.raises(Pass220I047DatasetError,match="exceeds source byte length"): build_library_training_record(source_bytes=raw,metadata=m,reference_vectors=_vectors(so))
