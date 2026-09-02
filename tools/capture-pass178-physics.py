#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
from hhs_runtime.pass163.vmrc import VMRCRuntime
from hhs_runtime.pass178.runtime import PhysicsAuthority
from hhs_runtime.pass178.templates import relativistic_lab_template

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("destination",type=Path);ap.add_argument("--steps",type=int,default=4);a=ap.parse_args()
    t=relativistic_lab_template();rt=PhysicsAuthority(vm81=VMRCRuntime());sid="capture:source";mid="capture:model"
    rt.ingest_source(sid,t["source"].encode());rt.register_model(model_id=mid,model_kind=t["model_kind"],source_id=sid,parameters={});rt.admit_initial_state(mid,t["initial_state"])
    packets=[rt.project_render_packet(mid)]
    for _ in range(a.steps):
        c=rt.step_candidate(mid);rt.commit_step(mid,c);packets.append(rt.project_render_packet(mid))
    payload={"schema":"HHS_PASS_178_CAPTURE_NUCLEUS_V1","packets":packets,"replay":rt.replay(mid),"mp4_generated":False,"terminal_capture":False}
    a.destination.parent.mkdir(parents=True,exist_ok=True);a.destination.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n");print(payload["replay"]);return 0
if __name__=="__main__":raise SystemExit(main())
