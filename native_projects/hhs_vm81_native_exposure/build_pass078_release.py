from pathlib import Path
import json
from .hhs_pass078_vm81_native_exposure_v1 import build_release

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"native_projects/hhs_vm81_native_exposure/artifacts"
OUT.mkdir(parents=True,exist_ok=True)
r=build_release(ROOT)
items={
"PASS_078_KERNEL_FREEZE_MANIFEST.json":r["freeze"],
"PASS_078_NATIVE_CAPABILITY_MANIFEST.json":r["capabilities"],
"PASS_078_NATIVE_EXPOSURE_REGISTRY.json":r["exposure"],
"PASS_078_VM81_LANE_BINDING_MANIFEST.json":r["lanes"],
"PASS_078_VM81_OVERLAP_RELATION_MAP.json":r["overlaps"],
"PASS_078_PLASTIC_E6_GEOMETRY_CONTRACT.json":r["geometry"],
"PASS_078_WAVE_MECHANICS_CONTRACT.json":r["wave"],
"HHS_PASS_078_RELEASE_BUNDLE.json":r,
}
for name,obj in items.items(): (OUT/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps({"status":"PASS_078_RELEASE_BUILT","release_root":r["pass078_release_root_hash72"],"artifacts":len(items)},sort_keys=True))
