from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import hashlib, json, re

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError, product_root, stable

PASS_ID = "PASS_078"
SCHEMA = "HHS_VM81_NATIVE_EXPOSURE_PASS_078_V1"
GRID_SIZE = 81
LO_SHU = (4,9,2,3,5,7,8,1,6)
KERNEL_PATHS = (
    "hhs_runtime/HARMONICODE_VM_RUNTIME.c",
    "hhs_runtime/include/HARMONICODE_VM_RUNTIME.h",
    "hhs_runtime/c/hhs_runtime_abi.c",
    "hhs_runtime/c/hhs_runtime_abi.h",
)

CATEGORY_RULES = (
    ("VM81_LIFECYCLE", ("init", "reset", "run_vm", "load_demo")),
    ("CELL_STATE", ("cell", "tensor81", "load", "store")),
    ("LO_SHU_OPERATIONS", ("loshu", "lo_shu")),
    ("SUDOKU_CONSTRAINT_ENFORCEMENT", ("constraint", "constrain", "relax", "sweep81", "close81")),
    ("ROTATION_PHASE", ("rot", "phase", "orientation")),
    ("RECIPROCAL_INVERSE", ("reciprocal", "ouroboros", "mulxy", "mulyx")),
    ("TRANSITION_MECHANICS", ("step", "execute", "branch", "dispatch")),
    ("PATH_CLOSURE", ("orbit", "close", "closure")),
    ("WITNESS_HASH_REPLAY", ("hash72", "receipt", "witness", "replay")),
    ("MANIFOLD_EXTENSION", ("manifold", "genomic", "tensor_seed", "frame")),
    ("DIAGNOSTICS", ("print", "summary", "trace")),
)

FUNC_RE = re.compile(
    r"(?m)^(?P<prefix>(?:static\s+)?(?:inline\s+)?[A-Za-z_][\w\s\*]*?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*\((?P<args>[^;{}]*)\)\s*\{"
)
DECL_RE = re.compile(
    r"(?m)^(?P<prefix>(?:extern\s+)?[A-Za-z_][\w\s\*]*?)\s+"
    r"(?P<name>hhs_[A-Za-z_]\w*)\s*\((?P<args>[^;{}]*)\)\s*;"
)


def _bytes(path: Path) -> bytes: return path.read_bytes()
def _sha(path: Path) -> str: return hashlib.sha256(_bytes(path)).hexdigest()
def _root(label: str, body: Mapping[str, Any]) -> dict[str, Any]:
    out = stable(dict(body)); out[f"{label}_root_hash72"] = product_root(label, out); return stable(out)


def kernel_freeze_manifest(repo: Path) -> dict[str, Any]:
    files = []
    for rel in KERNEL_PATHS:
        path = repo / rel
        if not path.is_file(): raise ContractError(f"REJECT_MISSING_FROZEN_KERNEL_FILE:{rel}")
        files.append({"path": rel, "size": path.stat().st_size, "sha256": _sha(path)})
    return _root("pass078_kernel_freeze_manifest", {
        "schema": "HHS_KERNEL_FREEZE_MANIFEST_PASS_078_V1", "pass_id": PASS_ID,
        "policy": "ANALYZE_AND_EXPOSE_WITHOUT_NATIVE_SEMANTIC_MODIFICATION", "files": files,
    })


def verify_kernel_freeze(repo: Path, manifest: Mapping[str, Any]) -> bool:
    for item in manifest["files"]:
        path = repo / item["path"]
        if not path.is_file() or _sha(path) != item["sha256"] or path.stat().st_size != item["size"]: return False
    unsigned = dict(manifest); supplied = unsigned.pop("pass078_kernel_freeze_manifest_root_hash72", "")
    return supplied == product_root("pass078_kernel_freeze_manifest", stable(unsigned))


def _categories(name: str) -> list[str]:
    lower = name.lower(); out = [cat for cat, words in CATEGORY_RULES if any(w in lower for w in words)]
    return out or ["NATIVE_EXECUTION_CONTROL"]


def native_capability_manifest(repo: Path) -> dict[str, Any]:
    source_rels = ("hhs_runtime/HARMONICODE_VM_RUNTIME.c", "hhs_runtime/c/hhs_runtime_abi.c")
    header_rels = ("hhs_runtime/include/HARMONICODE_VM_RUNTIME.h", "hhs_runtime/c/hhs_runtime_abi.h")
    headers = "\n".join((repo/x).read_text(encoding="utf-8") for x in header_rels)
    declared = {m.group("name") for m in DECL_RE.finditer(headers)}
    functions = []
    for source_rel in source_rels:
      source = (repo/source_rel).read_text(encoding="utf-8")
      for m in FUNC_RE.finditer(source):
        name = m.group("name"); prefix = " ".join(m.group("prefix").split()); args = " ".join(m.group("args").split())
        is_static = prefix.startswith("static ")
        functions.append({
            "symbol": name, "source_path": source_rel, "line": source.count("\n", 0, m.start())+1,
            "signature": f"{prefix} {name}({args})", "native_visibility": "INTERNAL_STATIC" if is_static else "EXTERNAL_LINKAGE",
            "declared_public_abi": name in declared, "categories": _categories(name),
            "exposure_status": "PUBLIC_ABI" if name in declared else "CATALOGUED_NOT_DIRECTLY_EXPORTED",
            "semantic_authority": "FROZEN_NATIVE_IMPLEMENTATION",
        })
    functions.sort(key=lambda x: (x["line"], x["symbol"]))
    public_decl_missing_definition = sorted(declared - {x["symbol"] for x in functions})
    return _root("pass078_native_capability_manifest", {
        "schema": "HHS_NATIVE_CAPABILITY_MANIFEST_PASS_078_V1", "pass_id": PASS_ID,
        "source_sha256": {x:_sha(repo/x) for x in source_rels}, "header_sha256": {x:_sha(repo/x) for x in header_rels},
        "native_function_count": len(functions), "public_abi_declaration_count": len(declared),
        "public_declarations_without_same_translation_unit_definition": public_decl_missing_definition,
        "functions": functions,
    })


def native_exposure_registry(manifest: Mapping[str, Any]) -> dict[str, Any]:
    entries=[]
    for f in manifest["functions"]:
        entries.append({
            "operation_id": f"vm81.native.{f['symbol']}", "native_symbol": f["symbol"],
            "binding_mode": "DIRECT_ABI" if f["declared_public_abi"] else "WITNESSED_CAPABILITY_DESCRIPTOR",
            "callable_from_higher_level": bool(f["declared_public_abi"]),
            "native_semantics_reimplemented": False, "requires_vm81_lane_binding": True,
            "result_policy": "PRESERVE_NATIVE_RESULT_IDENTITY", "categories": f["categories"],
        })
    return _root("pass078_native_exposure_registry", {
        "schema":"HHS_NATIVE_EXPOSURE_REGISTRY_PASS_078_V1", "pass_id":PASS_ID,
        "capability_manifest_root_hash72":manifest["pass078_native_capability_manifest_root_hash72"],
        "entry_count":len(entries), "entries":entries,
        "complete_catalogue": len(entries)==manifest["native_function_count"],
        "direct_abi_count":sum(1 for x in entries if x["callable_from_higher_level"]),
        "descriptor_only_count":sum(1 for x in entries if not x["callable_from_higher_level"]),
    })

DEFAULT_LANES = ("language","document","audio","vision","compiler","artifact","agent","search","planning")

def vm81_lane_binding_manifest(lanes: Sequence[str]=DEFAULT_LANES) -> dict[str, Any]:
    if not lanes or len(set(lanes)) != len(lanes): raise ContractError("REJECT_INVALID_OR_DUPLICATE_VM81_LANES")
    bindings=[]
    for ordinal, lane in enumerate(lanes):
        cells=tuple(range(ordinal, GRID_SIZE, len(lanes)))
        bindings.append({"lane_id":lane,"lane_ordinal":ordinal,"cell_indices":list(cells),"phase_slot":LO_SHU[ordinal%9],
                         "authority":"REQUESTER_NOT_NATIVE_SEMANTIC_AUTHORITY","mandatory_vm81_boundary":True})
    covered=sorted({c for b in bindings for c in b["cell_indices"]})
    return _root("pass078_vm81_lane_binding_manifest", {
        "schema":"HHS_VM81_LANE_BINDING_MANIFEST_PASS_078_V1","pass_id":PASS_ID,
        "grid_size":GRID_SIZE,"lane_count":len(bindings),"bindings":bindings,"covered_cells":covered,
        "complete_grid_coverage":covered==list(range(GRID_SIZE)),"unbound_lanes":[],
    })


def vm81_overlap_relation_map() -> dict[str, Any]:
    cells=[]
    for idx in range(GRID_SIZE):
        row,col=divmod(idx,9); box=(row//3)*3+col//3
        cells.append({"cell":idx,"row":row,"column":col,"subgrid":box,"lo_shu_slot":LO_SHU[idx%9],
                      "reciprocal_cell":GRID_SIZE-1-idx,"rot90_cell":col*9+(8-row),"phase":idx%72})
    return _root("pass078_vm81_overlap_relation_map", {
        "schema":"HHS_VM81_OVERLAP_RELATION_MAP_PASS_078_V1","pass_id":PASS_ID,"cell_count":81,"cells":cells,
        "relations":["ROW","COLUMN","SUBGRID","LO_SHU_SLOT","RECIPROCAL","ROTATION_90","PHASE"],
    })


def plastic_recurrence(n: int) -> list[int]:
    if n < 3: raise ContractError("REJECT_PLASTIC_RECURRENCE_REQUIRES_AT_LEAST_THREE_TERMS")
    seq=[0,0,1]
    while len(seq)<n: seq.append(seq[-2]+seq[-3])  # characteristic x^3=x+1
    return seq


def plastic_e6_geometry(vm_state_root_hash72: str) -> dict[str, Any]:
    if not vm_state_root_hash72: raise ContractError("REJECT_GEOMETRY_MISSING_VM81_SOURCE_STATE")
    rec=plastic_recurrence(87)
    nodes=[]
    for i in range(81):
        row,col=divmod(i,9)
        nodes.append({"cell":i,"e6_coordinate":[row,col,LO_SHU[i%9],(row-col),((row+col)%6),((row*col)%6)],
                      "plastic_scale_exact":{"numerator":rec[i+6],"denominator":rec[i+5] or 1}})
    edges=[]
    for i in range(81):
        r,c=divmod(i,9)
        for j in (i+1 if c<8 else -1, i+9 if r<8 else -1, 80-i):
            if j>=0 and i<j: edges.append({"source":i,"target":j,"relation":"GRID_OR_RECIPROCAL"})
    return _root("pass078_plastic_e6_geometry", {
        "schema":"HHS_EXTERNAL_PLASTIC_E6_GEOMETRY_PASS_078_V1","pass_id":PASS_ID,
        "source_vm81_state_root_hash72":vm_state_root_hash72,"kernel_mutation":False,
        "numeric_model":"EXACT_INTEGER_RATIONAL_NO_FLOATS","plastic_characteristic":"p^3=p+1",
        "nodes":nodes,"edges":edges,"removable_without_kernel_semantic_change":True,
    })


def wave_candidate(*, geometry: Mapping[str, Any], source_cell: int, amplitude: int, phase_delta: int) -> dict[str, Any]:
    if not 0<=source_cell<81: raise ContractError("REJECT_WAVE_SOURCE_CELL_OUT_OF_RANGE")
    candidates=[]
    for edge in geometry["edges"]:
        if edge["source"]==source_cell: target=edge["target"]
        elif edge["target"]==source_cell: target=edge["source"]
        else: continue
        candidates.append({"target_cell":target,"amplitude":int(amplitude),"phase":(source_cell+phase_delta+target)%72,
                           "status":"CANDIDATE_REQUIRES_NATIVE_VM81_ADMISSION"})
    return _root("pass078_wave_candidate", {
        "schema":"HHS_WAVE_CANDIDATE_PASS_078_V1","geometry_root_hash72":geometry["pass078_plastic_e6_geometry_root_hash72"],
        "source_cell":source_cell,"candidate_count":len(candidates),"candidates":candidates,
        "canonical_admission":False,"admission_boundary":"FROZEN_NATIVE_VM81_CONSTRAINT_ENFORCEMENT",
    })


def build_release(repo: Path) -> dict[str, Any]:
    freeze=kernel_freeze_manifest(repo); caps=native_capability_manifest(repo); exposure=native_exposure_registry(caps)
    lanes=vm81_lane_binding_manifest(); overlaps=vm81_overlap_relation_map()
    synthetic_vm_root=product_root("pass078_vm81_source_state", {"freeze":freeze["pass078_kernel_freeze_manifest_root_hash72"],"lanes":lanes["pass078_vm81_lane_binding_manifest_root_hash72"]})
    geometry=plastic_e6_geometry(synthetic_vm_root); wave=wave_candidate(geometry=geometry,source_cell=40,amplitude=1,phase_delta=9)
    release={"schema":SCHEMA,"pass_id":PASS_ID,"freeze":freeze,"capabilities":caps,"exposure":exposure,"lanes":lanes,"overlaps":overlaps,"geometry":geometry,"wave":wave}
    release["pass078_release_root_hash72"]=product_root("pass078_release",release)
    return stable(release)
