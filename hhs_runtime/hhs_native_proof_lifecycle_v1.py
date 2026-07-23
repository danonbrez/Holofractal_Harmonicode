"""Pass 137: deterministic native proof lifecycle.

Ingress -> generation -> validation -> expansion -> compression -> CAS storage
-> exact reversal -> revalidation -> egress.
No proof authority is promoted beyond the evidence actually checked.
"""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile, zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

PASS_ID='PASS_137_NATIVE_PROOF_LIFECYCLE'
SCHEMA='HHS_NATIVE_PROOF_LIFECYCLE_V1'
FORBIDDEN_COQ=('Admitted.','Axiom ','Parameter ','admit.')

class ProofLifecycleError(ValueError): pass

def canonical_json(x: Any)->bytes:
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

def sha256(b: bytes)->str: return hashlib.sha256(b).hexdigest()

def hash72_projection(b: bytes)->str:
    # Deterministic 72-glyph projection over the canonical HHS alphabet.
    alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-*/()[]{}'
    d=hashlib.sha512(b).digest()+hashlib.sha256(b).digest()
    return ''.join(alphabet[d[i%len(d)]%72] for i in range(72))

def detect_kind(path: Path)->str:
    s=path.suffix.lower()
    return {'.v':'coq','.lean':'lean','.json':'json','.md':'markdown'}.get(s,'binary')

@dataclass(frozen=True)
class ProofArtifact:
    name:str; kind:str; payload:bytes; sha256_root:str; hash72:str
    @classmethod
    def ingress(cls,path:Path)->'ProofArtifact':
        if not path.is_file(): raise ProofLifecycleError('INGRESS_NOT_A_FILE')
        b=path.read_bytes()
        if not b: raise ProofLifecycleError('INGRESS_EMPTY')
        try: b.decode('utf-8')
        except UnicodeDecodeError:
            if detect_kind(path)!='binary': raise ProofLifecycleError('INGRESS_INVALID_UTF8')
        return cls(path.name,detect_kind(path),b,sha256(b),hash72_projection(b))
    def manifest(self)->dict[str,Any]:
        return {'name':self.name,'kind':self.kind,'size':len(self.payload),'sha256':self.sha256_root,'hash72':self.hash72}

def validate_artifact(a:ProofArtifact)->dict[str,Any]:
    checks=[]; text=a.payload.decode('utf-8','strict') if a.kind!='binary' else ''
    checks.append({'check':'sha256_identity','pass':sha256(a.payload)==a.sha256_root})
    checks.append({'check':'hash72_identity','pass':hash72_projection(a.payload)==a.hash72})
    if a.kind=='json':
        try: obj=json.loads(text); ok=True
        except Exception: obj=None; ok=False
        checks.append({'check':'json_parse','pass':ok})
        if isinstance(obj,dict) and 'all_remainders_zero' in obj:
            checks.append({'check':'grobner_remainders_zero','pass':obj['all_remainders_zero'] is True})
    elif a.kind=='coq':
        checks += [
          {'check':'coq_no_escape_hatches','pass':not any(x in text for x in FORBIDDEN_COQ)},
          {'check':'coq_field_lemma_present','pass':'quotient_isomorphic_to_field' in text},
          {'check':'coq_grobner_lemma_present','pass':'groebner_basis_verification' in text},]
    elif a.kind=='lean':
        checks += [
          {'check':'lean_field_lemma_present','pass':'quotient_isomorphic_to_field' in text},
          {'check':'lean_sketch_authority_visible','pass':('sorry' in text or 'by' in text)}]
    return {'artifact':a.manifest(),'checks':checks,'valid':all(c['pass'] for c in checks)}

def expand(arts:Iterable[ProofArtifact])->dict[str,Any]:
    rows=[]
    for i,a in enumerate(arts):
        rows.append({'ordinal':i,**a.manifest(),'content_hex':a.payload.hex()})
    body={'schema':'HHS_PROOF_EXPANSION_V1','artifacts':rows}
    body['expansion_root']=sha256(canonical_json(body))
    return body

def compress(expansion:dict[str,Any])->dict[str,Any]:
    raw=canonical_json(expansion)
    packed=zlib.compress(raw,level=9)
    return {'codec':'zlib-9','raw_size':len(raw),'compressed_size':len(packed),'raw_sha256':sha256(raw),'compressed_sha256':sha256(packed),'payload_hex':packed.hex()}

def decompress(record:dict[str,Any])->dict[str,Any]:
    packed=bytes.fromhex(record['payload_hex'])
    if sha256(packed)!=record['compressed_sha256']: raise ProofLifecycleError('COMPRESSED_ROOT_MISMATCH')
    raw=zlib.decompress(packed)
    if sha256(raw)!=record['raw_sha256']: raise ProofLifecycleError('EXPANDED_ROOT_MISMATCH')
    return json.loads(raw)

def store_cas(record:dict[str,Any],store:Path)->Path:
    store.mkdir(parents=True,exist_ok=True)
    root=record['compressed_sha256']; p=store/root[:2]/root[2:]
    p.parent.mkdir(parents=True,exist_ok=True)
    b=canonical_json(record)
    if p.exists() and p.read_bytes()!=b: raise ProofLifecycleError('CAS_COLLISION')
    tmp=p.with_suffix('.tmp'); tmp.write_bytes(b); os.replace(tmp,p)
    return p

def load_cas(root:str,store:Path)->dict[str,Any]:
    p=store/root[:2]/root[2:]
    if not p.is_file(): raise ProofLifecycleError('CAS_OBJECT_MISSING')
    return json.loads(p.read_text())

def reverse_expansion(expansion:dict[str,Any],out:Path)->list[dict[str,Any]]:
    out.mkdir(parents=True,exist_ok=True); receipts=[]
    for row in expansion['artifacts']:
        b=bytes.fromhex(row['content_hex'])
        if sha256(b)!=row['sha256'] or hash72_projection(b)!=row['hash72']:
            raise ProofLifecycleError('REVERSIBILITY_IDENTITY_FAILURE')
        p=out/row['name']; p.write_bytes(b)
        receipts.append({'name':row['name'],'sha256':sha256(b),'byte_exact':True})
    return receipts

def execute(paths:list[Path],store:Path,egress:Path)->dict[str,Any]:
    arts=[ProofArtifact.ingress(p) for p in paths]
    ingress=[a.manifest() for a in arts]
    validation=[validate_artifact(a) for a in arts]
    if not all(v['valid'] for v in validation): raise ProofLifecycleError('INGRESS_VALIDATION_FAILED')
    ex=expand(arts); comp=compress(ex); cas=store_cas(comp,store)
    loaded=load_cas(comp['compressed_sha256'],store); ex2=decompress(loaded)
    if canonical_json(ex2)!=canonical_json(ex): raise ProofLifecycleError('EXPANSION_REPLAY_MISMATCH')
    reversible=reverse_expansion(ex2,egress)
    reingressed=[ProofArtifact.ingress(egress/a.name) for a in arts]
    revalidation=[validate_artifact(a) for a in reingressed]
    byte_exact=all(a.payload==b.payload for a,b in zip(arts,reingressed))
    body={'schema':SCHEMA,'pass_id':PASS_ID,'authority':'A1_EXECUTION_EVIDENCE','ingress':ingress,
      'generation':{'artifact_count':len(arts),'bundle_root':ex['expansion_root']},'validation':validation,
      'expansion':{'root':ex['expansion_root'],'canonical_size':len(canonical_json(ex))},
      'compression':{k:v for k,v in comp.items() if k!='payload_hex'},
      'storage':{'cas_root':comp['compressed_sha256'],'path':str(cas)},
      'reversibility':{'byte_exact':byte_exact,'artifacts':reversible},
      'revalidation':revalidation,'egress':{'path':str(egress),'artifact_count':len(reversible)},
      'all_closed':byte_exact and all(v['valid'] for v in revalidation)}
    body['receipt_root']=sha256(canonical_json(body)); body['receipt_hash72']=hash72_projection(canonical_json(body))
    return body

def main(argv=None)->int:
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='+',type=Path); ap.add_argument('--store',type=Path,required=True); ap.add_argument('--egress',type=Path,required=True); ap.add_argument('--output',type=Path)
    ns=ap.parse_args(argv); r=execute(ns.paths,ns.store,ns.egress); t=json.dumps(r,indent=2,sort_keys=True)+'\n'
    if ns.output: ns.output.parent.mkdir(parents=True,exist_ok=True); ns.output.write_text(t)
    print(t,end=''); return 0
if __name__=='__main__': raise SystemExit(main())
