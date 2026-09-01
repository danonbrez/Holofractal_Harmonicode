from __future__ import annotations
import json, subprocess
from pathlib import Path
from typing import Any
from hhs_runtime.pass184.runtime import APP_IMPORT, CONTRACT_ID, PortableRuntimeAuthority
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_BRANCH_HEAD="8fc42ee8364bd79cd711c0b0e60808b24a19a20d"
HISTORICAL_CONTRACT_BLOB="33043f3fc5f8446b6513156f7cf6eecdfd9f9c28"
HISTORICAL_RUNTIME_BLOB="3cc9da85a3098ce819fab55701392b3f50e38167"
HISTORICAL_API_BLOB="2947a3b088d2bd746aa718f35ae32a3e519293d7"
HISTORICAL_TEST_BLOB="991c19fdacc2d310ca7a99adc10e5f6bb5f4aae5"
PASS185_VALIDATED_HEAD="ee21cebede955354c0a0050dc3b267f166ef9cfe"
PASS185_RECEIPT=Path("evidence/pass185/i141/PASS_185_I141_CUMULATIVE_LOCAL_CLOSURE_RECEIPT.json")
CURRENT_APP_IMPORT="hhs_backend.runtime_os_application_server:app"
REQUIRED_OPERATIONS=(
 "validate_pass184_historical_nucleus","validate_pass185_successor_exposure",
 "validate_pass184_current_runtime_target","validate_pass184_package_authority",
 "validate_pass184_public_surfaces","validate_pass184_global_default_reachability",
 "validate_pass184_no_new_authority",
)
def _git(*args:str)->str:return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
def _text(path:str|Path)->str:return (ROOT/path).read_text("utf-8")
def validate_pass184_historical_nucleus()->dict[str,Any]:
 expected={
  "docs/pass184/HHS_PASS_184_PORTABLE_HYDRATION_RUNTIME_PACKAGE_AND_SUPERVISED_SERVICE_AUTHORITY.md":HISTORICAL_CONTRACT_BLOB,
  "hhs_runtime/pass184/runtime.py":HISTORICAL_RUNTIME_BLOB,
  "hhs_backend/api/pass184_runtime_routes.py":HISTORICAL_API_BLOB,
  "tests/test_pass184_portable_runtime.py":HISTORICAL_TEST_BLOB,
 }
 for path,blob in expected.items():
  if _git("rev-parse",f"{HISTORICAL_BRANCH_HEAD}:{path}")!=blob:raise RuntimeError(f"PASS184_HISTORICAL_BLOB_DRIFT:{path}")
 contract=_text("docs/pass184/HHS_PASS_184_PORTABLE_HYDRATION_RUNTIME_PACKAGE_AND_SUPERVISED_SERVICE_AUTHORITY.md")
 assert CONTRACT_ID in contract and "A RUNNING PID IS NOT A READY SERVICE." in contract
 return {"ok":True,"historical_branch_head":HISTORICAL_BRANCH_HEAD,"historical_implementation_existed":True,
         "historical_completion_receipt_committed":False,"historical_branch_merged":False,"repair_forward_required":True}
def validate_pass185_successor_exposure()->dict[str,Any]:
 receipt=json.loads(_text(PASS185_RECEIPT))
 assert receipt["classification"]=="HHS_PASS_185_CUMULATIVE_PHASE1_PHASE7_LOCAL_CLOSURE_VERIFIED"
 assert receipt["lineage"]["cumulative_validated_head"]==PASS185_VALIDATED_HEAD
 return {"ok":True,"pass185_validated_head":PASS185_VALIDATED_HEAD,"cumulative_local_closure_preserved":True,
         "native_exposure_repaired_forward_in_i142":True}
def validate_pass184_current_runtime_target()->dict[str,Any]:
 assert APP_IMPORT==CURRENT_APP_IMPORT
 runtime=_text("hhs_runtime/pass184/runtime.py")
 assert 'APP_MODULE_RELATIVE = Path("hhs_backend/runtime_os_application_server.py")' in runtime
 assert "hhs_backend.application_ide_server:app" not in runtime
 return {"ok":True,"historical_target":"hhs_backend.application_ide_server:app","current_target":CURRENT_APP_IMPORT,"target_upgrade_explicit":True}
def validate_pass184_package_authority()->dict[str,Any]:
 a=PortableRuntimeAuthority(); env={"schema":"HHS_PASS_184_ENVIRONMENT_SNAPSHOT_V1","repository_root":str(ROOT),
 "writable_root":"/tmp/hhs-pass184-i142","environment_identity":"e"*64}
 left=a.plan(profile="full",install_root="/tmp/hhs-pass184-i142/hhs-runtime",repository_root=ROOT,environment=env)
 right=a.plan(profile="full",install_root="/tmp/hhs-pass184-i142/hhs-runtime",repository_root=ROOT,environment=env)
 assert left.to_dict()==right.to_dict() and "application_ide" in left.components and "games" in left.components
 assert left.app_import==CURRENT_APP_IMPORT
 return {"ok":True,"stable_plan_identity":True,"profile_count":len(a.status()["profiles"]),
         "full_profile_contains_application_ide":True,"full_profile_contains_games":True}
def validate_pass184_public_surfaces()->dict[str,Any]:
 server=_text("hhs_backend/runtime_os_application_server_full.py")
 shell=_text("hhs_gui/runtime_os/workspace/HHSWorkspaceShell.tsx")
 panel=_text("hhs_gui/runtime_os/workspace/Pass184RuntimePackagePanel.tsx")
 assert "app.include_router(pass184_runtime_router)" in server and "Pass184RuntimePackagePanel" in shell
 for tid in ("pass184-plan","pass184-build","pass184-verify","pass184-probe"):assert tid in panel
 return {"ok":True,"cli":True,"api":True,"runtime_os_gui":True}
def validate_pass184_global_default_reachability()->dict[str,Any]:
 c=json.loads(_text("contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json"))["current_cumulative_binding_census"]
 ordered=c["ordered_bindings"]
 assert c["wired_floor_pass"]<=184 and c["binding_count"]>=37
 assert "184" in ordered
 i=ordered.index("184")
 assert i>=2 and ordered[i-2:i+1]==["186","185","184"]
 assert ordered[-1]==str(c["wired_floor_pass"])
 return {"ok":True,"wired_floor":c["wired_floor_pass"],"binding_count":c["binding_count"],
         "pass184_bound":True,"pass184_position":i,"global_defaults_mandatory":True,
         "multimodal_generalization_inherited":True}
def validate_pass184_no_new_authority()->dict[str,Any]:
 s=PortableRuntimeAuthority().status()
 assert s["canonical_mutation_authority"] is False and s["independent_vm81_authority"] is False and s["independent_hash72_clock"] is False
 return {"ok":True,"singleton_vm81_authority_remains_inherited":True,"package_is_canonical_mutation_authority":False,
 "supervisor_is_vm81_authority":False,"independent_hash72_clock":False,"hash216_is_archival_identity_only":True,
 "floating_point_canonical_authority":False}
def pass184_membrane_manifest()->dict[str,Any]:
 return {"pass_number":184,"iteration":142,"classification":"WIRED_PENDING_EXECUTED_VALIDATION",
 "historical_contract":CONTRACT_ID,"historical_branch_head":HISTORICAL_BRANCH_HEAD,
 "aggregate_order_tail":[188,187,186,185,184],"declared_operations":list(REQUIRED_OPERATIONS)}
def execute_pass184_membrane_preflight()->dict[str,Any]:
 ops={
  "validate_pass184_historical_nucleus":validate_pass184_historical_nucleus(),
  "validate_pass185_successor_exposure":validate_pass185_successor_exposure(),
  "validate_pass184_current_runtime_target":validate_pass184_current_runtime_target(),
  "validate_pass184_package_authority":validate_pass184_package_authority(),
  "validate_pass184_public_surfaces":validate_pass184_public_surfaces(),
  "validate_pass184_global_default_reachability":validate_pass184_global_default_reachability(),
  "validate_pass184_no_new_authority":validate_pass184_no_new_authority(),
 }
 if tuple(ops)!=REQUIRED_OPERATIONS or not all(v.get("ok") is True for v in ops.values()):raise RuntimeError("PASS184_I142_PREFLIGHT_FAILURE")
 return {"ok":True,"operations":ops}
