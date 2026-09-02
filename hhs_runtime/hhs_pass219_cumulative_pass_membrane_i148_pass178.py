from __future__ import annotations
import json
from pathlib import Path
import subprocess
from typing import Any

from hhs_runtime.pass163.vmrc import VMRCRuntime
from hhs_runtime.pass178.runtime import PhysicsAuthority
from hhs_runtime.pass178.templates import relativistic_lab_template

ROOT=Path(__file__).resolve().parents[1]
VALIDATED_NUCLEUS_HEAD="1f63e08370d0e3c54390a7b4b3bec8ef042ddfa3"
NUCLEUS_RECEIPT_BLOB="1b74415c302f81e5fa424b8cf7e1d4daa036c529"
PRE_CUMULATIVE_GREEN_RUN=33626761513
REMAINING_TERMINAL_CATEGORIES=(
 "COMPLETE_HARMONICODE_CONSTRAINT_CORPUS","COMPLETE_TYPED_CST_AST_HIR_PIPELINE",
 "FULL_NATIVE_PUBLIC_ABI_PARITY","THERMODYNAMIC_SYMBOLIC_KERNEL",
 "RELATIVISTIC_CHARGED_PARTICLE_LAB","QUANTUM_DOUBLE_SLIT_LAB",
 "REGISTERED_MEASUREMENT_AUTHORITY","SINGULAR_HASH72_COMMIT_INTEGRATION",
 "THREEJS_EXECUTING_VIEWPORT","DETERMINISTIC_MP4_CAPTURE",
 "BROWSER_MOBILE_E2E_AND_PERFORMANCE","AUTHORITATIVE_MAIN_INTEGRATION",
)

def _git(*args:str)->str:
 return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()

def validate_pass178_frozen_nucleus()->dict[str,Any]:
 _git("merge-base","--is-ancestor",VALIDATED_NUCLEUS_HEAD,"HEAD")
 path=ROOT/"evidence/pass178/i148/PASS_219_I148_PASS178_EXACT_PHYSICS_NUCLEUS_RECEIPT_INDEX.json"
 blob=_git("hash-object",str(path.relative_to(ROOT)))
 if blob!=NUCLEUS_RECEIPT_BLOB: raise RuntimeError(f"PASS178_NUCLEUS_RECEIPT_BLOB_DRIFT:{blob}")
 receipt=json.loads(path.read_text("utf-8"))
 v=receipt["validated_nucleus"]
 if v["workflow_run_id"]!=PRE_CUMULATIVE_GREEN_RUN or v["conclusion"]!="success": raise RuntimeError("PASS178_PRE_CUMULATIVE_RECEIPT_NOT_GREEN")
 if receipt["constraint_corpus"]["classification"]!="CONTRACT_VISIBLE_CORPUS_NUCLEUS_NOT_COMPLETE_HISTORICAL_CORPUS": raise RuntimeError("PASS178_CORPUS_CLASSIFICATION_DRIFT")
 return {"ok":True,"validated_nucleus_head":VALIDATED_NUCLEUS_HEAD,"nucleus_receipt_blob":NUCLEUS_RECEIPT_BLOB,"pre_cumulative_green_run":PRE_CUMULATIVE_GREEN_RUN}

def validate_pass178_runtime_projection()->dict[str,Any]:
 t=relativistic_lab_template();vm=VMRCRuntime();rt=PhysicsAuthority(vm81=vm)
 rt.ingest_source("i148:source",t["source"].encode())
 rt.register_model(model_id="i148:model",model_kind=t["model_kind"],source_id="i148:source",parameters={})
 before=vm.epoch;initial=rt.admit_initial_state("i148:model",t["initial_state"])
 if vm.epoch!=before+1: raise RuntimeError("PASS178_INITIAL_VM81_ADMISSION_DRIFT")
 candidate=rt.step_candidate("i148:model")
 if candidate.get("ok") is not True or candidate.get("authoritative_clock_advanced") is not False: raise RuntimeError("PASS178_CANDIDATE_VALIDATION_DRIFT")
 step=rt.commit_step("i148:model",candidate)
 if vm.epoch!=before+2: raise RuntimeError("PASS178_STEP_VM81_ADMISSION_DRIFT")
 replay=rt.replay("i148:model");packet=rt.project_render_packet("i148:model")
 if not replay["deterministic_replay_chain"]: raise RuntimeError("PASS178_REPLAY_DRIFT")
 if packet["renderer_feedback_authority"] is not False or packet["simulation_mutation_authority"] is not False: raise RuntimeError("PASS178_RENDER_AUTHORITY_DRIFT")
 if len(step["post_vm81_hash72_evidence"])!=72 or len(step["state_hash216"])!=216: raise RuntimeError("PASS178_HASH_EVIDENCE_DRIFT")
 return {"ok":True,"vm81_state_admission":True,"post_vm81_hash72_evidence":True,"archival_hash216_identity":True,"deterministic_replay":True,"immutable_render_projection":True}

def validate_pass178_global_census()->dict[str,Any]:
 c=json.loads((ROOT/"contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json").read_text("utf-8"));x=c["current_cumulative_binding_census"]
 if x["wired_floor_pass"]!=178 or x["binding_count"]!=43: raise RuntimeError(f"PASS178_GLOBAL_CENSUS_DRIFT:{x}")
 if x["ordered_bindings"][-5:]!=["182","181","180","179","178"]: raise RuntimeError("PASS178_GLOBAL_CENSUS_TAIL_DRIFT")
 debt=next((d for d in c["known_repair_forward_debt"] if d["pass"]==178),None)
 if debt is None or debt["classification"]!="WIRED_NONTERMINAL_REPAIR_FORWARD" or debt["terminal_completion_claimed"] is not False or debt["complete_historical_constraint_corpus"] is not False: raise RuntimeError("PASS178_REPAIR_FORWARD_DEBT_DRIFT")
 if tuple(debt["remaining_terminal_categories"])!=REMAINING_TERMINAL_CATEGORIES: raise RuntimeError("PASS178_TERMINAL_CATEGORY_DRIFT")
 return {"ok":True,"wired_floor":178,"binding_count":43,"terminal_completion_claimed":False,"repair_forward_required":True,"remaining_terminal_category_count":12}

def validate_pass178_exact_binding_surface()->dict[str,Any]:
 h=(ROOT/"hhs_runtime/include/hhs_pass219_inherited_pass178_1_48.h").read_text("utf-8")
 hpp=(ROOT/"hhs_runtime/include/hhs_pass219_inherited_pass178_1_48.hpp").read_text("utf-8")
 c=(ROOT/"hhs_runtime/c/hhs_pass219_inherited_pass178_1_48.inc").read_text("utf-8")
 agg_h=(ROOT/"hhs_runtime/include/hhs_runtime_exact_abi.h").read_text("utf-8")
 agg_c=(ROOT/"hhs_runtime/c/hhs_runtime_exact_abi.c").read_text("utf-8")
 for token in ["hhs_exact_pass219_bind_pass178_exact_physics","terminal_pass178_completion","complete_historical_constraint_corpus"]:
  if token not in h+c: raise RuntimeError(f"PASS178_BINDING_TOKEN_MISSING:{token}")
 if "terminal_pass178_completion_claimed() noexcept { return false; }" not in hpp or "repair_forward_required() noexcept { return true; }" not in hpp: raise RuntimeError("PASS178_CPP_NONTERMINAL_DRIFT")
 if "hhs_pass219_inherited_pass178_1_48.h" not in agg_h or "hhs_pass219_inherited_pass178_1_48.inc" not in agg_c: raise RuntimeError("PASS178_AGGREGATE_EXPOSURE_MISSING")
 return {"ok":True,"terminal_completion_claimed":False,"repair_forward_required":True,"complete_historical_constraint_corpus":False}

def pass178_membrane_manifest()->dict[str,Any]:
 return {"schema":"HHS_PASS219_I148_PASS178_CUMULATIVE_MEMBRANE_V1","aggregate_order_tail":[182,181,180,179,178],"repair_forward_required":True,"remaining_terminal_categories":list(REMAINING_TERMINAL_CATEGORIES),"authority":{"singleton_vm81_inherited":True,"independent_hash72_commit_authority":False,"hash216_mutation_authority":False,"renderer_gpu_browser_mutation_authority":False,"floating_point_canonical_authority":False}}

def execute_pass178_membrane_preflight()->dict[str,Any]:
 return {"ok":True,"classification":"HHS_PASS178_I148_CUMULATIVE_NONTERMINAL_PREFLIGHT","frozen":validate_pass178_frozen_nucleus(),"runtime":validate_pass178_runtime_projection(),"census":validate_pass178_global_census(),"exact_binding":validate_pass178_exact_binding_surface(),"manifest":pass178_membrane_manifest()}
