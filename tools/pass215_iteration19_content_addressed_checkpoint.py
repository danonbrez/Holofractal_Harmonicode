#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from hhs_backend.runtime import hhs_pass215_iteration19_content_addressed_checkpoint_v2 as i19

def write(path,payload): Path(path).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--container'); p.add_argument('--prompt',default=i19.CONTRACTED_PROMPT); p.add_argument('--source-kind',default='public_open_transformer'); p.add_argument('--repo-id',default='ggml-org/tiny-llamas'); p.add_argument('--revision',default='main'); p.add_argument('--expected-sha256'); p.add_argument('--certification-bits',type=int,default=i19.CERTIFICATION_BITS); p.add_argument('--checkpoint-output'); p.add_argument('--validate'); p.add_argument('--compare-replay',nargs=2); p.add_argument('--output',required=True); a=p.parse_args()
 if a.validate:
  e=json.loads(Path(a.validate).read_text()); i19.validate_content_addressed_checkpoint_evidence(e); c=e['content_addressed_checkpoint']; write(a.output,{'schema':i19.VALIDATION_SCHEMA,'contract':i19.CONTRACT,'valid':True,'compact_checkpoint_root_hash216':c['compact_checkpoint_root_hash216'],'content_store_root_hash216':c['content_store_root_hash216'],'iteration18_checkpoint_root_hash216':c['iteration18_checkpoint_root_hash216'],'compact_checkpoint_canonical_bytes':c['compact_checkpoint_canonical_bytes'],'suite_root_hash216':e['content_addressed_checkpoint_suite_root_hash216'],'evidence_root_hash216':e['evidence_root_hash216'],'receipt_hash72':e['receipt_hash72']}); return 0
 if a.compare_replay:
  l=json.loads(Path(a.compare_replay[0]).read_text()); r=json.loads(Path(a.compare_replay[1]).read_text()); write(a.output,i19.compare_content_addressed_checkpoint_replays(l,r)); return 0
 if not a.container: p.error('--container required')
 e,c=i19.execute_content_addressed_checkpoint_benchmark_from_path(a.container,source={'kind':a.source_kind,'repo_id':a.repo_id,'revision':a.revision},prompt=a.prompt,expected_sha256=a.expected_sha256,certification_bits=a.certification_bits)
 write(a.output,e)
 if a.checkpoint_output: write(a.checkpoint_output,c)
 return 0
if __name__=='__main__': raise SystemExit(main())
