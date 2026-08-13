#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from hhs_backend.runtime import hhs_pass215_iteration17_scalable_rope_certified_greedy_v1 as i17

def write(path,payload): Path(path).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--container'); p.add_argument('--prompt',default=i17.CONTRACTED_PROMPT); p.add_argument('--source-kind',default='public_open_transformer'); p.add_argument('--repo-id',default='ggml-org/tiny-llamas'); p.add_argument('--revision',default='main'); p.add_argument('--expected-sha256'); p.add_argument('--certification-bits',type=int,default=i17.CERTIFICATION_BITS); p.add_argument('--greedy-steps',type=int,default=i17.CERTIFIED_GREEDY_STEP_COUNT); p.add_argument('--validate'); p.add_argument('--compare-replay',nargs=2); p.add_argument('--output',required=True); a=p.parse_args()
 if a.validate:
  e=json.loads(Path(a.validate).read_text()); i17.validate_scalable_rope_certified_greedy_evidence(e); c=e['scalable_rope_certified_greedy']; write(a.output,{'schema':i17.VALIDATION_SCHEMA,'contract':i17.CONTRACT,'valid':True,'selected_token_ids':c['selected_token_ids'],'chain_root_hash216':c['chain_root_hash216'],'suite_root_hash216':e['scalable_rope_certified_greedy_suite_root_hash216'],'evidence_root_hash216':e['evidence_root_hash216'],'receipt_hash72':e['receipt_hash72']}); return 0
 if a.compare_replay:
  l=json.loads(Path(a.compare_replay[0]).read_text()); r=json.loads(Path(a.compare_replay[1]).read_text()); write(a.output,i17.compare_scalable_rope_certified_greedy_replays(l,r)); return 0
 if not a.container: p.error('--container required')
 e=i17.build_scalable_rope_certified_greedy_evidence_from_path(a.container,source={'kind':a.source_kind,'repo_id':a.repo_id,'revision':a.revision},prompt=a.prompt,expected_sha256=a.expected_sha256,certification_bits=a.certification_bits,greedy_steps=a.greedy_steps); write(a.output,e); return 0
if __name__=='__main__': raise SystemExit(main())
