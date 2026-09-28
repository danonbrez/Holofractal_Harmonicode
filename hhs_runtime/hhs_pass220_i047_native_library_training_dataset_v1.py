"""Pass 220 I047: candidate-only native-library training dataset adapter."""
from __future__ import annotations
import base64, binascii, json
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA="HHS_PASS_220_I047_NATIVE_LIBRARY_TRAINING_RECORD_V1"
DATASET_SCHEMA="HHS_PASS_220_I047_NATIVE_LIBRARY_TRAINING_DATASET_V1"
INPUT_SCHEMA="HHS_PASS_220_I047_NATIVE_LIBRARY_DATASET_INPUT_V1"
REFERENCE_ORIGIN="SOURCE_LIBRARY_OBSERVED_OUTPUT"
LANE5_ROLE="RELATIONSHIP_METADATA_AND_REFERENCE_OUTPUT_TRAINING_INPUT"
REQUIRED=("library_id","library_format","architecture","abi","provenance","codec_boundary","byte_regions","entrypoints","relationships")
EFFECTS={"PURE","READ_ONLY","STATEFUL_BOUNDED","IO_BOUNDED","OPAQUE_FOREIGN"}

class Pass220I047DatasetError(ValueError): pass

def _stable(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(v): return sha256(_stable(v).encode()).hexdigest()
def _text(v,n):
    if not isinstance(v,str) or not v.strip(): raise Pass220I047DatasetError(f"{n} must be non-empty text")
    return v
def _map(v,n):
    if not isinstance(v,Mapping): raise Pass220I047DatasetError(f"{n} must be a mapping")
    return v
def _seq(v,n,empty=False):
    if isinstance(v,(str,bytes,bytearray,memoryview)) or not isinstance(v,Sequence): raise Pass220I047DatasetError(f"{n} must be a sequence")
    if not empty and not v: raise Pass220I047DatasetError(f"{n} may not be empty")
    return v

def typed_value_from_bytes(*,data_type,encoding,payload,semantic_value=None):
    raw=bytes(payload); out={"data_type":_text(data_type,"data_type"),"encoding":_text(encoding,"encoding"),"byte_length":len(raw),"payload_base64":base64.b64encode(raw).decode(),"payload_sha256":sha256(raw).hexdigest()}
    if semantic_value is not None: out["semantic_value"]=semantic_value
    return out

def _typed(v,n):
    x=_map(v,n)
    try: raw=base64.b64decode(_text(x.get("payload_base64"),n+".payload_base64").encode("ascii"),validate=True)
    except (UnicodeEncodeError,binascii.Error) as e: raise Pass220I047DatasetError(n+" invalid base64") from e
    if x.get("byte_length")!=len(raw) or x.get("payload_sha256")!=sha256(raw).hexdigest(): raise Pass220I047DatasetError(n+" byte identity mismatch")
    return typed_value_from_bytes(data_type=_text(x.get("data_type"),n+".data_type"),encoding=_text(x.get("encoding"),n+".encoding"),payload=raw,semantic_value=x.get("semantic_value") if "semantic_value" in x else None)

def _port(v,n):
    x=_map(v,n); return {"name":_text(x.get("name"),n+".name"),"data_type":_text(x.get("data_type"),n+".data_type"),"encoding":_text(x.get("encoding"),n+".encoding")}

def normalize_metadata(metadata,*,source_byte_length):
    m=_map(metadata,"metadata"); missing=[k for k in REQUIRED if k not in m]
    if missing: raise Pass220I047DatasetError("metadata missing required keys: "+", ".join(missing))
    c=_map(m["codec_boundary"],"codec_boundary"); missing=[k for k in ("ingress_encoder_id","egress_decoder_id") if k not in c]
    if missing: raise Pass220I047DatasetError("codec_boundary missing keys: "+", ".join(missing))
    if c.get("preserve_external_contract") is not True: raise Pass220I047DatasetError("external codec contract must be preserved")
    regions=[]
    for i,r0 in enumerate(_seq(m["byte_regions"],"byte_regions")):
        r=_map(r0,f"byte_regions[{i}]"); start,length=r.get("start"),r.get("length")
        if not isinstance(start,int) or start<0 or not isinstance(length,int) or length<0: raise Pass220I047DatasetError("byte region bounds invalid")
        if start+length>source_byte_length: raise Pass220I047DatasetError("byte region exceeds source byte length")
        regions.append({"region_id":_text(r.get("region_id"),"region_id"),"start":start,"length":length,"kind":_text(r.get("kind"),"kind"),"permissions":str(r.get("permissions","UNKNOWN"))})
    entries=[]
    for i,e0 in enumerate(_seq(m["entrypoints"],"entrypoints")):
        e=_map(e0,f"entrypoints[{i}]"); effect=_text(e.get("side_effect_class"),"side_effect_class").upper()
        if effect not in EFFECTS: raise Pass220I047DatasetError("unsupported side_effect_class")
        entries.append({"entrypoint_id":_text(e.get("entrypoint_id"),"entrypoint_id"),"symbol":_text(e.get("symbol"),"symbol"),"inputs":tuple(_port(p,"input") for p in _seq(e.get("inputs",()),"inputs",True)),"outputs":tuple(_port(p,"output") for p in _seq(e.get("outputs"),"outputs")),"side_effect_class":effect,"state_boundary":e.get("state_boundary","NONE"),"math_operator_identities":tuple(e.get("math_operator_identities",())),"constructor_dependencies":tuple(e.get("constructor_dependencies",())),"phase_relationships":tuple(e.get("phase_relationships",())),"timing_constraints":tuple(e.get("timing_constraints",())),"vm81_relationships":tuple(e.get("vm81_relationships",())),"rna_relationships":tuple(e.get("rna_relationships",()))})
    if len({e["entrypoint_id"] for e in entries})!=len(entries): raise Pass220I047DatasetError("duplicate entrypoint_id")
    relations=[]
    for i,r0 in enumerate(_seq(m["relationships"],"relationships",True)):
        r=_map(r0,f"relationships[{i}]"); order=r.get("order",i)
        if not isinstance(order,int) or order<0: raise Pass220I047DatasetError("relationship order invalid")
        relations.append({"relation_id":_text(r.get("relation_id"),"relation_id"),"relation_type":_text(r.get("relation_type"),"relation_type"),"source":_text(r.get("source"),"source"),"target":_text(r.get("target"),"target"),"order":order,"attributes":dict(_map(r.get("attributes",{}),"attributes"))})
    return {"library_id":_text(m["library_id"],"library_id"),"library_format":_text(m["library_format"],"library_format"),"architecture":_text(m["architecture"],"architecture"),"abi":_text(m["abi"],"abi"),"provenance":_text(m["provenance"],"provenance"),"codec_boundary":{"ingress_encoder_id":_text(c["ingress_encoder_id"],"ingress_encoder_id"),"egress_decoder_id":_text(c["egress_decoder_id"],"egress_decoder_id"),"preserve_external_contract":True},"byte_regions":tuple(regions),"entrypoints":tuple(entries),"relationships":tuple(relations),"dependencies":tuple(m.get("dependencies",())),"hash72_hash216_lineage_hints":tuple(m.get("hash72_hash216_lineage_hints",()))}

def normalize_reference_vector(v,metadata,index=0):
    x=_map(v,f"reference_vectors[{index}]")
    if x.get("reference_origin")!=REFERENCE_ORIGIN: raise Pass220I047DatasetError("reference origin must be source-library observed output")
    obs=_map(x.get("observation"),"observation")
    if obs.get("source_library_invoked") is not True or obs.get("observed_output") is not True: raise Pass220I047DatasetError("reference output requires observed source-library invocation")
    eid=_text(x.get("entrypoint_id"),"entrypoint_id"); entry=next((e for e in metadata["entrypoints"] if e["entrypoint_id"]==eid),None)
    if entry is None: raise Pass220I047DatasetError("reference entrypoint not declared")
    ins=tuple(_typed(p,"reference input") for p in _seq(x.get("inputs",()),"inputs",True)); outs=tuple(_typed(p,"reference output") for p in _seq(x.get("outputs"),"outputs"))
    if len(ins)!=len(entry["inputs"]) or len(outs)!=len(entry["outputs"]): raise Pass220I047DatasetError("reference port count mismatch")
    for got,want in list(zip(ins,entry["inputs"]))+list(zip(outs,entry["outputs"])):
        if (got["data_type"],got["encoding"])!=(want["data_type"],want["encoding"]): raise Pass220I047DatasetError("reference type/encoding drift")
    return {"vector_id":_text(x.get("vector_id"),"vector_id"),"entrypoint_id":eid,"inputs":ins,"outputs":outs,"reference_origin":REFERENCE_ORIGIN,"observation":{"source_library_invoked":True,"observed_output":True,"captured_by":_text(obs.get("captured_by"),"captured_by")}}

def build_library_training_record(*,source_bytes,metadata,reference_vectors):
    raw=bytes(source_bytes)
    if not raw: raise Pass220I047DatasetError("source library bytes may not be empty")
    meta=normalize_metadata(metadata,source_byte_length=len(raw)); vectors=tuple(normalize_reference_vector(v,meta,i) for i,v in enumerate(_seq(reference_vectors,"reference_vectors")))
    if len({v["vector_id"] for v in vectors})!=len(vectors): raise Pass220I047DatasetError("duplicate reference vector_id")
    h=sha256(raw).hexdigest(); body={"schema":SCHEMA,"version":"1.0.0","library_id":meta["library_id"],"source":{"byte_length":len(raw),"sha256":h,"content_address":"sha256:"+h,"raw_bytes_preserved":True,"dataset_relative_path":"raw/"+h+".bin"},"metadata":meta,"relationship_root_sha256":_hash({"byte_regions":meta["byte_regions"],"entrypoints":meta["entrypoints"],"relationships":meta["relationships"],"dependencies":meta["dependencies"],"lineage_hints":meta["hash72_hash216_lineage_hints"]}),"reference_vectors":vectors,"reference_vector_root_sha256":_hash(vectors),"reference_result_contract":{"same_external_inputs_required":True,"same_expected_output_types_required":True,"observable_result_equivalence_required":True,"reference_origin":REFERENCE_ORIGIN},"lane5_handoff":{"role":LANE5_ROLE,"algebraic_lifting_requested":True,"algebraic_lifting_performed_here":False,"latency_phase_scheduling_requested":True,"latency_phase_scheduling_performed_here":False,"reuse_validated_constructor_relations_requested":True,"repetitive_linear_recomputation_requested":False,"ingress_encoder_id":meta["codec_boundary"]["ingress_encoder_id"],"egress_decoder_id":meta["codec_boundary"]["egress_decoder_id"],"ingress_egress_codec_preserved":True},"authority":{"candidate_only":True,"vm81_mutation_invoked":False,"canonical_hash72_minted":False,"canonical_hash216_committed":False,"canonical_persistence_invoked":False,"model_weight_mutation_invoked":False,"alternate_scheduler_created":False,"alternate_optimizer_created":False}}
    return {**body,"record_sha256":_hash(body)}

def validate_library_training_record(record):
    x=_map(record,"record"); body=dict(x); claimed=body.pop("record_sha256",None)
    if x.get("schema")!=SCHEMA or claimed!=_hash(body): raise Pass220I047DatasetError("record identity mismatch")
    a=_map(x.get("authority"),"authority")
    if a.get("candidate_only") is not True: raise Pass220I047DatasetError("record must remain candidate-only")
    for k in ("vm81_mutation_invoked","canonical_hash72_minted","canonical_hash216_committed","canonical_persistence_invoked","model_weight_mutation_invoked","alternate_scheduler_created","alternate_optimizer_created"):
        if a.get(k) is not False: raise Pass220I047DatasetError("forbidden authority escalation: "+k)
    h=_map(x.get("lane5_handoff"),"lane5_handoff")
    if h.get("algebraic_lifting_performed_here") is not False or h.get("latency_phase_scheduling_performed_here") is not False: raise Pass220I047DatasetError("I047 may not duplicate Lane 5")
    if h.get("ingress_egress_codec_preserved") is not True: raise Pass220I047DatasetError("codec membrane lost")
    return {"ok":True,"library_id":x["library_id"],"source_sha256":x["source"]["sha256"],"record_sha256":claimed}

def materialize_dataset(examples,output_root):
    if not examples: raise Pass220I047DatasetError("dataset requires at least one library")
    root=Path(output_root); rawdir=root/"raw"; rawdir.mkdir(parents=True,exist_ok=True); records=[]
    for raw,meta,vectors in examples:
        r=build_library_training_record(source_bytes=raw,metadata=meta,reference_vectors=vectors); validate_library_training_record(r); b=bytes(raw); p=rawdir/(r["source"]["sha256"]+".bin")
        if p.exists() and p.read_bytes()!=b: raise Pass220I047DatasetError("content-address collision")
        p.write_bytes(b); records.append(r)
    if len({r["library_id"] for r in records})!=len(records) or len({r["source"]["sha256"] for r in records})!=len(records): raise Pass220I047DatasetError("duplicate library identity")
    text="".join(_stable(r)+"\n" for r in records); (root/"records.jsonl").write_text(text,encoding="utf-8")
    body={"schema":DATASET_SCHEMA,"version":"1.0.0","library_count":len(records),"records_sha256":sha256(text.encode()).hexdigest(),"record_sha256s":tuple(r["record_sha256"] for r in records),"source_sha256s":tuple(r["source"]["sha256"] for r in records),"lane5_role":LANE5_ROLE,"raw_bytes_preserved":True,"reference_outputs_observed_from_source_libraries":True,"same_input_output_contract_required":True,"ingress_egress_codecs_preserved":True,"candidate_only":True,"canonical_mutation_authority":False}; out={**body,"dataset_root_sha256":_hash(body)}
    (root/"manifest.json").write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8"); return out

def load_input_spec(spec_path):
    p=Path(spec_path); s=json.loads(p.read_text(encoding="utf-8"))
    if s.get("schema")!=INPUT_SCHEMA: raise Pass220I047DatasetError("input spec schema mismatch")
    out=[]
    for item0 in _seq(s.get("libraries"),"libraries"):
        item=_map(item0,"library"); base=p.parent; lib=base/_text(item.get("library_path"),"library_path"); meta=base/_text(item.get("metadata_path"),"metadata_path"); vec=base/_text(item.get("reference_vectors_path"),"reference_vectors_path"); vectors=json.loads(vec.read_text())
        if not isinstance(vectors,list): raise Pass220I047DatasetError("reference vectors file must be a JSON list")
        out.append((lib.read_bytes(),json.loads(meta.read_text()),vectors))
    return tuple(out)
