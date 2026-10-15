"""Run the inherited HTML HNAN passthrough as a *reference witness only*.

The browser physics surface cannot grant native HNAN or Hash216 authority.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from hhs_runtime.hhs_pass220_course_hnan_passthrough_evidence_v1 import course_hnan_proof_obligations
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

SOURCE="examples/ParticleSimulation.html"
EXTRACT=re.compile(r"function hnanGate\(a,b\)\s*\{\s*if\(b!==0\) return a/b;\s*hnanFires\+\+;\s*return a\*1;[^\n]*\n\s*\}", re.M)

def execute_browser_passthrough_reference(root:Path=Path("."))->dict:
    obligations=course_hnan_proof_obligations()
    raw=(root/SOURCE).read_bytes()
    text=raw.decode("utf-8")
    matched=EXTRACT.search(text)
    if not matched: raise ProofCorpusError("INHERITED_BROWSER_HNAN_REFERENCE_DRIFT")
    script="""
"use strict";
let hnanFires=0;
""" + matched.group(0) + """
const state={carrier: Object.freeze([13,-21,34]),phase: Object.freeze([2,3,5]),writes:0};
const before=JSON.stringify(state);
const bypass=hnanGate(13,0);
if(bypass!==13||hnanFires!==1||JSON.stringify(state)!==before||state.writes!==0)
  throw Error("PASSTHROUGH_REFERENCE_REJECTED");
const ordinary=hnanGate(18,3);
if(ordinary!==6||hnanFires!==1||JSON.stringify(state)!==before)
  throw Error("NONZERO_REFERENCE_REJECTED");
console.log(JSON.stringify({bypass,ordinary,hnanFires,phase_unchanged:true,reference_only:true}));
"""
    result=subprocess.run(["node","-e",script],capture_output=True,text=True,timeout=15,check=True)
    witness=json.loads(result.stdout)
    if not (witness.get("phase_unchanged") is True and witness.get("reference_only") is True):
        raise ProofCorpusError("BROWSER_REFERENCE_REJECTED")
    return {"course_module_sha256":obligations["course_module_sha256"],
            "browser_source_sha256":sha256(raw).hexdigest(),
            "browser_reference_witness":witness,
            "course_passthrough_theorem_proved":False,
            "native_hnan_gate_proof_inherited":True,
            "native_theorem_admission":False,
            "hash216_minted":False}
