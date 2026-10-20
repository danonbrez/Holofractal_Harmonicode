"""Exact course-module gate provenance; no scalarization or fabricated proof status."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import re
from hhs_runtime.hhs_pass220_whitepaper_proof_dependency_binding_v1 import build_dependency_graph
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

SOURCE="whitepapers/Harmonicode Algebra - Course"
CONTINUATION="docs/pass220/HARMONICODE_ALGEBRA_COURSE_MODULES_13_26.md"
LEGACY_COUNT=15
TOTAL_COUNT=27
HEADER=re.compile(r"^MODULE (\d+) — (.+)$",re.MULTILINE)
SCHEMA="HHS_PASS220_COURSE_MODULE_GATE_PROVENANCE_V1"
HNAN_PASSTHROUGH_THEOREM="COURSE_HNAN_GAIN_ONE_PASSTHROUGH_PROOF"
HNAN_RUNTIME_PHASE_GATE="RUNTIME_HNAN_PHASE_INFORMATION_PRESERVATION_GATE"
# Independent proof obligations: neither discharges the other.

def course_module_gate_inventory(root:Path=Path("."))->dict:
    # Preserve the existing frozen-corpus integrity gate.
    # Source migration requires independent authorization.
    graph=build_dependency_graph(root)
    node=next((n for n in graph["nodes"] if n["source"]==SOURCE),None)
    if node is None: raise ProofCorpusError("COURSE_NOT_IN_FROZEN_CORPUS")
    raw=(root/SOURCE).read_bytes()
    if sha256(raw).hexdigest()!=node["source_sha256"]:
        raise ProofCorpusError("COURSE_SOURCE_IDENTITY_MISMATCH")
    text=raw.decode("utf-8")
    matches=list(HEADER.finditer(text))
    if [int(m.group(1)) for m in matches]!=list(range(LEGACY_COUNT)):
        raise ProofCorpusError("COURSE_MODULE_BOUNDARY_DRIFT")
    preamble=text[:matches[0].start()]
    required=("`==` is a gate","`n/d` is the rank-1 tensor circuit",
              "bypasses at gain exactly 1")
    if not all(x in preamble for x in required):
        raise ProofCorpusError("COURSE_TYPED_GATE_PREAMBLE_DRIFT")
    modules=[]
    for idx,m in enumerate(matches):
        start=m.start()
        end=matches[idx+1].start() if idx+1<len(matches) else len(text)
        section=text[start:end]
        modules.append({"index":idx,"title":m.group(2).strip(),
                        "byte_sha256":sha256(section.encode("utf-8")).hexdigest(),
                        "source_section":section,
                        "gate_syntax_present":"==" in section,
                        "native_verification":"NOT_EXECUTED",
                        "hnan_passthrough_proof":"NOT_VERIFIED",
                        "runtime_hnan_phase_gate":"NOT_VERIFIED",
                        "canonical_admission":False})
    continuation_raw=(root/CONTINUATION).read_bytes()
    continuation_text=continuation_raw.decode("utf-8")
    continuation_matches=list(HEADER.finditer(continuation_text))
    if [int(m.group(1)) for m in continuation_matches]!=list(range(LEGACY_COUNT,TOTAL_COUNT)):
        raise ProofCorpusError("COURSE_CONTINUATION_MODULE_BOUNDARY_DRIFT")
    continuation_sha=sha256(continuation_raw).hexdigest()
    for i,m in enumerate(continuation_matches):
        start=m.start()
        end=continuation_matches[i+1].start() if i+1<len(continuation_matches) else len(continuation_text)
        section=continuation_text[start:end]
        modules.append({"index":int(m.group(1)),"title":m.group(2).strip(),
                        "byte_sha256":sha256(section.encode("utf-8")).hexdigest(),
                        "source_section":section,"source_path":CONTINUATION,
                        "source_sha256":continuation_sha,
                        "gate_syntax_present":"==" in section,
                        "native_verification":"NOT_EXECUTED",
                        "hnan_passthrough_proof":"NOT_VERIFIED",
                        "runtime_hnan_phase_gate":"NOT_VERIFIED",
                        "canonical_admission":False})
    for module in modules[:LEGACY_COUNT]:
        module["source_path"]=SOURCE
        module["source_sha256"]=node["source_sha256"]
    return {"schema":SCHEMA,"source":SOURCE,"source_sha256":node["source_sha256"],
            "continuation_source":CONTINUATION,
            "continuation_source_sha256":continuation_sha,
            "legacy_source_module_count":LEGACY_COUNT,
            "module_count":len(modules),"ordered_modules":modules,
            "verified_native_modules":0,"whole_course_proved":False,
            "hash216_minted":False,
            "independent_hnan_proof_obligations":(HNAN_PASSTHROUGH_THEOREM,HNAN_RUNTIME_PHASE_GATE)}

def require_executed_module_proof(inventory:dict,index:int,receipt:dict)->None:
    if not isinstance(index,int) or index<0 or index>=len(inventory["ordered_modules"]):
        raise ProofCorpusError("UNKNOWN_COURSE_MODULE")
    module=inventory["ordered_modules"][index]
    if (receipt.get("source_sha256")!=module["source_sha256"]
        or receipt.get("module_sha256")!=module["byte_sha256"]
        or receipt.get("native_verified") is not True):
        raise ProofCorpusError("EXECUTED_COURSE_MODULE_PROOF_REQUIRED")
    # A declaration from an arbitrary caller is not verification of a native checker.
    raise ProofCorpusError("TRUSTED_NATIVE_RECEIPT_VERIFIER_NOT_REGISTERED")
