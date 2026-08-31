from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"contracts/pass219/PASS_219_GLOBAL_CANONICAL_DEFAULTS_1_0.json"
EXACT_H=ROOT/"hhs_runtime/include/hhs_runtime_exact_abi.h"
EXACT_C=ROOT/"hhs_runtime/c/hhs_runtime_exact_abi.c"
HEADER_RE=re.compile(r'#include "hhs_pass219_inherited_pass(\d+)([abc]?)_[^"]+\.h"')
SOURCE_RE=re.compile(r'#include "hhs_pass219_inherited_pass(\d+)([abc]?)_[^"]+\.inc"')
REGISTRY_RE=re.compile(r'\{\s*(\d+)U,\s*([0-3])U,\s*0U\s*\}')
VARIANT_TO_NAME={"0":"","1":"a","2":"b","3":"c"}
def read(p): return p.read_text(encoding="utf-8")
def norm(m): return [n+v for n,v in m]
def main():
 c=json.loads(read(CONTRACT)); eh=read(EXACT_H); ec=read(EXACT_C); pi=read(ROOT/"hhs_runtime/c/hhs_pass219_global_canonical_defaults_1_0.inc")
 expected=c["current_cumulative_binding_census"]["ordered_bindings"]; hb=norm(HEADER_RE.findall(eh)); sb=norm(SOURCE_RE.findall(ec))
 if hb!=expected: raise SystemExit(f"HEADER_BINDING_CENSUS_DRIFT:{hb}")
 if sb!=expected: raise SystemExit(f"SOURCE_BINDING_CENSUS_DRIFT:{sb}")
 reg=[n+VARIANT_TO_NAME[v] for n,v in REGISTRY_RE.findall(pi)]
 if reg!=expected: raise SystemExit(f"GLOBAL_POLICY_REGISTRY_DRIFT:{reg}")
 if c["current_cumulative_binding_census"]["binding_count"]!=len(expected) or len(expected)!=38: raise SystemExit("CONTRACT_BINDING_COUNT_DRIFT")
 nums=[int(re.match(r"\d+",x).group(0)) for x in expected]; ceiling=c["current_cumulative_binding_census"]["ceiling_pass"]; floor=c["current_cumulative_binding_census"]["wired_floor_pass"]
 if ceiling!=218 or floor!=183: raise SystemExit("CURRENT_WIRED_BOUNDARY_DRIFT")
 for p in range(floor,ceiling+1):
  if nums.count(p)!=(3 if p==200 else 1): raise SystemExit(f"NUMERIC_COVERAGE_DRIFT:{p}")
 if eh.index('hhs_pass219_inherited_pass183_1_43.h')>eh.index('hhs_pass219_global_canonical_defaults_1_0.h'): raise SystemExit("POLICY_HEADER_NOT_AFTER_CURRENT_INHERITED_TAIL")
 if ec.index('hhs_pass219_inherited_pass183_1_43.inc')>ec.index('hhs_pass219_global_canonical_defaults_1_0.inc'): raise SystemExit("POLICY_SOURCE_NOT_AFTER_CURRENT_INHERITED_TAIL")
 idir=ROOT/"hhs_runtime/include"
 for b in expected:
  m=re.search(rf'#include "(hhs_pass219_inherited_pass{re.escape(b)}_[^"]+)\.h"',eh)
  if m is None: raise SystemExit(f"MISSING_C_HEADER_INCLUDE:{b}")
  if not (idir/f"{m.group(1)}.hpp").is_file(): raise SystemExit(f"MISSING_CPP_MEMBRANE:{b}")
 s=c["pass_semantics"]; d=c["cross_cutting_defaults"]; r=c["repair_forward"]
 if not all([s["numbered_pass_is_additive_system_version"],s["successful_implementation_must_remain_cumulatively_reachable"],d["applies_to_all_applicable_existing_surfaces"],d["applies_to_all_applicable_future_surfaces"],d["retroactive_repair_forward_required"],d["permanent_until_explicit_upgrade_or_deprecation"],r["no_grandfather_bypass"]]): raise SystemExit("MANDATORY_GLOBAL_DEFAULT_FLAG_DISABLED")
 if s["standalone_application_classification_allowed"] or s["isolated_native_project_substitutes_for_canonical_wiring"] or d["optional"]: raise SystemExit("OPTIONAL_OR_STANDALONE_BYPASS_ENABLED")
 mm=c.get("multimodal_optimization_generalization",{})
 if mm.get("contract_id")!="HHS-P219-MULTIMODAL-OPTIMIZATION-GENERALIZATION" or not mm.get("mandatory"): raise SystemExit("MULTIMODAL_GENERALIZATION_CONTRACT_MISSING")
 if not mm.get("all_optimizations_multimodal_by_default") or not mm.get("automatic_compatible_target_discovery") or not mm.get("locality_requires_evidenced_bounded_exception"): raise SystemExit("MULTIMODAL_GENERALIZATION_INVARIANT_DISABLED")
 if mm.get("compatible_untested_targets")!="VALIDATION_REQUIRED" or mm.get("compatible_safe_beneficial_targets")!="GENERALIZE_REQUIRED": raise SystemExit("MULTIMODAL_GENERALIZATION_CLASSIFICATION_DRIFT")
 p157=(ROOT/"native_projects/hhs_pass157_ppf_mptc").is_dir(); wired157=any(x.startswith("157") for x in hb); debt=next((x for x in c["known_repair_forward_debt"] if x["pass"]==157),None)
 if p157 and not wired157 and (debt is None or debt["classification"]!="MISSING_CUMULATIVE_EXPOSURE" or not debt["mandatory_repair_forward"] or not debt["native_project_is_not_canonical_substitute"]): raise SystemExit("PASS157_REPAIR_FORWARD_DEBT_NOT_ENFORCED")
 for p in [ROOT/"docs/architecture/HHS_CUMULATIVE_PASS_GLOBAL_DEFAULTS.md",ROOT/"hhs_runtime/include/hhs_pass219_global_canonical_defaults_1_0.h",ROOT/"hhs_runtime/include/hhs_pass219_global_canonical_defaults_1_0.hpp",ROOT/"tests/pass219/test_pass219_global_canonical_defaults_1_0.c",ROOT/"tests/pass219/test_pass219_global_canonical_defaults_1_0.cpp",ROOT/".github/workflows/pass219-global-canonical-defaults.yml",ROOT/"contracts/pass219/PASS_219_MULTIMODAL_OPTIMIZATION_GENERALIZATION_1_0.json",ROOT/"docs/architecture/HHS_MULTIMODAL_OPTIMIZATION_GENERALIZATION.md"]:
  if not p.is_file(): raise SystemExit(f"REQUIRED_POLICY_SURFACE_MISSING:{p}")
 print(json.dumps({"classification":"HHS_PASS219_GLOBAL_CANONICAL_DEFAULTS_ENFORCED","binding_count":len(expected),"wired_ceiling":ceiling,"wired_floor":floor,"pass157":"MISSING_CUMULATIVE_EXPOSURE_REPAIR_FORWARD_REQUIRED" if not wired157 else "WIRED"},sort_keys=True))
 return 0
if __name__=="__main__": raise SystemExit(main())
