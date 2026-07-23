from pathlib import Path
import json, pytest
from hhs_runtime.hhs_native_proof_lifecycle_v1 import execute, ProofLifecycleError, compress, decompress, expand, ProofArtifact
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[ROOT/'formal/coq/HHS_GFE_Field_Quotient.v',ROOT/'formal/lean/HHS_GFE_Field_Quotient.lean',ROOT/'formal/certificates/gfe_state_5_4_grobner.json']

def test_full_lifecycle(tmp_path):
 r=execute(SOURCES,tmp_path/'cas',tmp_path/'egress')
 assert r['all_closed'] is True
 assert r['reversibility']['byte_exact'] is True
 assert len(r['ingress'])==3
 assert all((tmp_path/'egress'/p.name).read_bytes()==p.read_bytes() for p in SOURCES)

def test_deterministic_receipt(tmp_path):
 r1=execute(SOURCES,tmp_path/'cas',tmp_path/'e1'); r2=execute(SOURCES,tmp_path/'cas',tmp_path/'e2')
 # Paths differ, but all canonical proof-state roots remain identical.
 assert r1['generation']==r2['generation']; assert r1['compression']==r2['compression']; assert r1['storage']['cas_root']==r2['storage']['cas_root']

def test_corrupt_compressed_payload_rejected():
 ex=expand([ProofArtifact.ingress(SOURCES[0])]); c=compress(ex); c['payload_hex']='00'+c['payload_hex'][2:]
 with pytest.raises(ProofLifecycleError,match='COMPRESSED_ROOT_MISMATCH'): decompress(c)

def test_invalid_coq_rejected(tmp_path):
 p=tmp_path/'bad.v'; p.write_text('Theorem x : True. Admitted.\n')
 with pytest.raises(ProofLifecycleError,match='INGRESS_VALIDATION_FAILED'): execute([p],tmp_path/'cas',tmp_path/'out')

def test_float_free_receipt(tmp_path):
 r=execute(SOURCES,tmp_path/'cas',tmp_path/'out'); s=json.dumps(r)
 assert 'NaN' not in s and 'Infinity' not in s
