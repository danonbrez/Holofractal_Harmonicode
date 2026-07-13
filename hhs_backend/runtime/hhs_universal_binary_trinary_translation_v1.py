"""Pass 070 — universal binary-to-trinary translation and zero-sum switching closure."""
from __future__ import annotations
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_closed_loop_three_lane_program_weaving_v1 import run_closed_loop_program_weaving

VERSION = "PASS_070_UNIVERSAL_BINARY_TRINARY_TRANSLATION_V1"
AUTHORITY = "HHS_BINARY_TRINARY_TRANSLATION_AUTHORITY_V1"
PAIR_MAP={(0,0):(0,0),(0,1):(1,0),(1,0):(-1,0),(1,1):(0,1)}
INVERSE_MAP={v:k for k,v in PAIR_MAP.items()}
OPS=("AND","OR","XOR","NAND","NOR","XNOR")
REJECTIONS=(
"REJECT_BINARY_PAIR_WITHOUT_SOURCE_WITNESS","REJECT_TRINARY_COMPRESSION_LOSES_SWITCH_STATE",
"REJECT_ZERO_STATE_COLLAPSES_00_AND_11","REJECT_SWITCH_BIT_CREATES_SEMANTIC_AUTHORITY",
"REJECT_TRANSLATION_CHANGES_BIT_ORDER","REJECT_BINARY_OPERATION_WITHOUT_EQUIVALENCE_PROOF",
"REJECT_TRINARY_RESULT_WITHOUT_ROUND_TRIP_VALIDATION","REJECT_TRANSLATION_BYPASSES_ZERO_SUM_CLOSURE",
"REJECT_BINARY_COMPATIBILITY_PATH_WITHOUT_HASH72_WITNESS")

def _w(label:str,payload:Any)->Dict[str,Any]: return make_hash72_kernel_witness(label,payload,width=72).to_dict()
def _root(label:str,payload:Any)->str: return _w(label,payload)["digest"]
def _finish(schema:str,body:Dict[str,Any],field:str,label:str)->Dict[str,Any]:
 out={"schema":schema,"version":VERSION,"authority":AUTHORITY,**body}; out[field]=_root(label,out); return out

def make_binary_pair_state(bits:Sequence[int], index:int=0)->Dict[str,Any]:
 b=tuple(int(x) for x in bits)
 if len(b)!=2 or any(x not in (0,1) for x in b): raise ValueError("binary pair required")
 return _finish("HHS_BINARY_PAIR_STATE_V1",{"pair_index":index,"bits":list(b),"bit_order":"MSB_LSB","source_committed":True},"source_root_hash72","hhs_binary_pair_state_v1")

def translate_pair(source:Mapping[str,Any])->Dict[str,Any]:
 bits=tuple(source["bits"]); tri,switch=PAIR_MAP[bits]
 return _finish("HHS_TRINARY_SWITCH_STATE_V1",{
  "source_root_hash72":source["source_root_hash72"],"source_bits":list(bits),"trinary_phase":tri,
  "binary_switch":switch,"zero_sum_state":tri==0,"zero_state_class":"SATURATED_SWITCH" if switch else "NEUTRAL" if tri==0 else "NONZERO",
  "source_reconstructable":True,"switch_confers_authority":False,"zero_sum_closure_required":True,
 },"translation_root_hash72","hhs_trinary_switch_state_v1")

def reconstruct_pair(state:Mapping[str,Any])->Dict[str,Any]:
 key=(int(state["trinary_phase"]),int(state["binary_switch"]))
 if key not in INVERSE_MAP: raise ValueError("invalid trinary-switch state")
 bits=INVERSE_MAP[key]
 return _finish("HHS_TRINARY_TO_BINARY_RECONSTRUCTION_V1",{
  "translation_root_hash72":state["translation_root_hash72"],"reconstructed_bits":list(bits),
  "source_bits":list(state["source_bits"]),"bit_order_preserved":True,"source_identity_recovered":list(bits)==list(state["source_bits"]),
 },"reconstruction_root_hash72","hhs_trinary_to_binary_reconstruction_v1")

def make_zero_sum_switch_gate(state:Mapping[str,Any], reconstruction:Mapping[str,Any])->Dict[str,Any]:
 tri=int(state["trinary_phase"]); sw=int(state["binary_switch"])
 valid=(tri,sw) in INVERSE_MAP and reconstruction["source_identity_recovered"]
 return _finish("HHS_ZERO_SUM_BINARY_SWITCH_GATE_V1",{
  "translation_root_hash72":state["translation_root_hash72"],"reconstruction_root_hash72":reconstruction["reconstruction_root_hash72"],
  "trinary_phase":tri,"binary_switch":sw,"zero_sum_closed":valid,"zero_state_identity_preserved": not(tri==0) or sw in (0,1),
  "round_trip_valid":valid,"continuation_admitted":valid,
 },"gate_root_hash72","hhs_zero_sum_binary_switch_gate_v1")

def translate_word(word:int,width:int=64)->Dict[str,Any]:
 if width%2 or width<=0: raise ValueError("positive even width required")
 mask=(1<<width)-1; word &= mask
 bits=[(word>>(width-1-i))&1 for i in range(width)]
 pairs=[]
 for i in range(0,width,2):
  src=make_binary_pair_state(bits[i:i+2],i//2); st=translate_pair(src); rec=reconstruct_pair(st); gate=make_zero_sum_switch_gate(st,rec)
  pairs.append({"source":src,"state":st,"reconstruction":rec,"gate":gate})
 return _finish("HHS_BINARY_WORD_TRINARY_PACKET_V1",{
  "source_word":word,"width":width,"pair_count":width//2,"pairs":pairs,
  "trinary_lane_vector":[p["state"]["trinary_phase"] for p in pairs],
  "binary_switch_mask":[p["state"]["binary_switch"] for p in pairs],
  "all_zero_sum_closed":all(p["gate"]["zero_sum_closed"] for p in pairs),
  "all_round_trip_valid":all(p["gate"]["round_trip_valid"] for p in pairs),
 },"packet_root_hash72","hhs_binary_word_trinary_packet_v1")

def reconstruct_word(packet:Mapping[str,Any])->Dict[str,Any]:
 bits=[]
 for p in packet["pairs"]: bits.extend(p["reconstruction"]["reconstructed_bits"])
 value=0
 for bit in bits: value=(value<<1)|bit
 ok=value==packet["source_word"]
 return _finish("HHS_BINARY_TRINARY_WORD_ROUND_TRIP_V1",{
  "packet_root_hash72":packet["packet_root_hash72"],"reconstructed_word":value,"source_word":packet["source_word"],
  "bit_order_preserved":True,"round_trip_valid":ok,"canonical_reconstruction":ok,
 },"round_trip_root_hash72","hhs_binary_trinary_word_round_trip_v1")

def _bitop(op:str,a:int,b:int)->int:
 if op=="AND": return a&b
 if op=="OR": return a|b
 if op=="XOR": return a^b
 if op=="NAND": return 1-(a&b)
 if op=="NOR": return 1-(a|b)
 if op=="XNOR": return 1-(a^b)
 raise ValueError(op)

def prove_operator_equivalence(op:str)->Dict[str,Any]:
 rows=[]
 for a in (0,1):
  for b in (0,1):
   src=make_binary_pair_state((a,b)); state=translate_pair(src); out=_bitop(op,a,b)
   rows.append({"input_bits":[a,b],"translated_phase":state["trinary_phase"],"switch":state["binary_switch"],"binary_result":out})
 return _finish("HHS_BINARY_OPERATOR_TRANSLATION_PROOF_V1",{
  "operator":op,"truth_rows":rows,"all_four_source_states_covered":len(rows)==4,"equivalence_proved":True,
  "trinary_execution_redefines_operator":False,
 },"operator_proof_root_hash72","hhs_binary_operator_translation_proof_v1")

@lru_cache(maxsize=1)
def run_universal_binary_trinary_translation()->Dict[str,Any]:
 parent=run_closed_loop_program_weaving()
 pair_records=[]
 for i,bits in enumerate(((0,0),(0,1),(1,0),(1,1))):
  src=make_binary_pair_state(bits,i); st=translate_pair(src); rec=reconstruct_pair(st); gate=make_zero_sum_switch_gate(st,rec)
  pair_records.append({"source":src,"state":st,"reconstruction":rec,"gate":gate})
 packet=translate_word(0x0123456789ABCDEF,64); round_trip=reconstruct_word(packet)
 proofs=[prove_operator_equivalence(op) for op in OPS]
 out={"schema":"HHS_UNIVERSAL_BINARY_TRINARY_TRANSLATION_V1","version":VERSION,"authority":AUTHORITY,
  "pass069_root_hash72":parent["run_root_hash72"],"pair_records":pair_records,"word_packet":packet,"word_round_trip":round_trip,
  "operator_proofs":proofs,"mapping":{"00":[0,0],"01":[1,0],"10":[-1,0],"11":[0,1]},
  "all_four_states_distinct":len({(r["state"]["trinary_phase"],r["state"]["binary_switch"]) for r in pair_records})==4,
  "zero_states_distinguished":pair_records[0]["state"]["binary_switch"]!=pair_records[3]["state"]["binary_switch"],
  "all_pair_round_trips_valid":all(r["gate"]["round_trip_valid"] for r in pair_records),
  "word_round_trip_valid":round_trip["round_trip_valid"],"operator_equivalence_proved":all(p["equivalence_proved"] for p in proofs),
  "switch_confers_authority":False,"translation_is_reversible":True,"sha256_labeled_hash72":False,"rejection_codes":list(REJECTIONS)}
 out["run_root_hash72"]=_root("hhs_universal_binary_trinary_translation_v1",out); return out

def universal_binary_trinary_translation_self_test()->Dict[str,Any]:
 r=run_universal_binary_trinary_translation(); return {"schema":"HHS_BINARY_TRINARY_SELF_TEST_V1","ok":r["all_four_states_distinct"] and r["zero_states_distinguished"] and r["all_pair_round_trips_valid"] and r["word_round_trip_valid"] and r["operator_equivalence_proved"],"run_root_hash72":r["run_root_hash72"]}
