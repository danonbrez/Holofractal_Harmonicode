#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from hhs_backend.runtime import hhs_pass215_iteration18_bounded_generation_control_v2 as i18

def write(path,payload): Path(path).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--container'); p.add_argument('--prompt',default=i18.CONTRACTED_PROMPT); p.add_argument('--source-kind',default='public_open_transformer'); p.add_argument('--repo-id',default='ggml-org/tiny-llamas'); p.add_argument('--revision',default='main'); p.add_argument('--expected-sha256'); p.add_argument('--certification-bits',type=int,default=i18.CERTIFICATION_BITS); p.add_argument('--max-new-tokens',type=int,default=i18.MAX_NEW_TOKENS); p.add_argument('--resume-after-steps',type=int,default=i18.RESUME_AFTER_STEPS); p.add_argument('--checkpoint-output'); p.add_argument('--validate'); p.add_argument('--compare-replay',nargs=2); p.add_argument('--output',required=True); a=p.parse_args()
 if a.validate:
  e=json.loads(Path(a.validate).read_text()); i18.validate_bounded_generation_control_evidence(e); c=e['bounded_generation_control']; write(a.output,{'schema':i18.VALIDATION_SCHEMA,'contract':i18.CONTRACT,'valid':True,'selected_token_ids':c['selected_token_ids'],'termination_reason':c['termination_reason'],'checkpoint_root_hash216':e['resume_checkpoint']['checkpoint_root_hash216'],'suite_root_hash216':e['bounded_generation_control_suite_root_hash216'],'evidence_root_hash216':e['evidence_root_hash216'],'receipt_hash72':e['receipt_hash72']}); return 0
 if a.compare_replay:
  l=json.loads(Path(a.compare_replay[0]).read_text()); r=json.loads(Path(a.compare_replay[1]).read_text()); write(a.output,i18.compare_bounded_generation_control_replays(l,r)); return 0
 if not a.container: p.error('--container required')
 e,c=i18.execute_bounded_generation_with_resume_from_path(a.container,source={'kind':a.source_kind,'repo_id':a.repo_id,'revision':a.revision},prompt=a.prompt,expected_sha256=a.expected_sha256,certification_bits=a.certification_bits,max_new_tokens=a.max_new_tokens,resume_after_steps=a.resume_after_steps)
 write(a.output,e)
 if a.checkpoint_output: write(a.checkpoint_output,c)
 return 0
if __name__=='__main__': raise SystemExit(main())
