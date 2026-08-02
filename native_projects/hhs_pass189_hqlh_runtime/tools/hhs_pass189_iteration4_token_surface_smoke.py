#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, http.client, json, os, subprocess, sys, tempfile, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PYTHON=ROOT/'python'
SERVER=ROOT/'server'/'hhs_pass189_iteration4_token_server.py'
sys.path.insert(0,str(PYTHON))
from hhs_pass189_iteration3 import hash72
from hhs_pass189_iteration4 import sign_manifest

def request(port,method,path,body=None):
    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
    data=None
    headers={}
    if body is not None:
        data=json.dumps(body).encode()
        headers={'Content-Type':'application/json'}
    connection.request(method,path,data,headers)
    response=connection.getresponse()
    raw=response.read()
    connection.close()
    return response.status,json.loads(raw)

def main():
    with tempfile.TemporaryDirectory() as temporary_directory:
        root=Path(temporary_directory)
        port=39192
        environment=os.environ.copy()
        environment.update({
            'HHS189_I4_DB':str(root/'i4.sqlite3'),
            'HHS189_I4_QUARANTINE':str(root/'q'),
            'HHS189_I4_QUIET':'1',
            'PYTHONPATH':str(PYTHON),
        })
        process=subprocess.Popen(
            [sys.executable,str(SERVER),'--host','127.0.0.1','--port',str(port)],
            cwd=ROOT,env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        )
        try:
            for _ in range(60):
                try:
                    if request(port,'GET','/api/pass189/i4/status')[0]==200:
                        break
                except OSError:
                    time.sleep(.05)
            else:
                raise RuntimeError('server did not start')
            key=b'lifecycle-surface'
            key_base64=base64.b64encode(key).decode()
            assert request(port,'POST','/api/pass189/i4/trust/register',{
                'signer_id':'surface','key_base64':key_base64,'created_ns':1,
            })[0]==200
            payload=b'driver'
            manifest={
                'driver_id':'surface','version':'1.0.0','driver_kind':'LOOPBACK',
                'entrypoint':'driver/main.py','signer_id':'surface',
                'payload_sha256':hashlib.sha256(payload).hexdigest(),
                'operations':['WRITE'],'capabilities':['software-test'],'units':['volt'],
                'device_ids':['surface'],'minimum':0,'maximum':5,'watchdog_timeout_ms':1000,
                'required_interlocks':['WATCHDOG'],'created_ns':2,
            }
            signature=sign_manifest(manifest,key)
            assert request(port,'POST','/api/pass189/i4/package/ingest',{
                'package_id':'package','manifest':manifest,
                'payload_base64':base64.b64encode(payload).decode(),
                'signature_hex':signature,'verification_key_base64':key_base64,
            })[0]==200
            tests={name:True for name in (
                'manifest_identity','payload_digest','path_confinement','capability_scope',
                'range_enforcement','watchdog_fail_closed','anti_replay','rollback_ready',
            )}
            assert request(port,'POST','/api/pass189/i4/conformance',{
                'run_id':'run','package_id':'package','evidence_class':'SOFTWARE_FIXTURE',
                'tests':tests,'trace_hash72':hash72({'run':1}),
                'physical_measurement':False,'created_ns':3,
            })[0]==200
            status,token=request(port,'POST','/api/pass189/i4/promote',{
                'promotion_id':'promotion','package_id':'package',
                'approver_a_hash72':'a'*72,'approver_b_hash72':'b'*72,
                'issue_witness_hash72':'c'*72,'issued_ns':10,'expires_ns':20,
            })
            assert status==200
            status,valid=request(port,'POST','/api/pass189/i4/promotion/validate',{
                'token_hash72':token['token_hash72'],'at_ns':15,
            })
            assert status==200 and valid['valid'] is True
            status,sweep=request(port,'POST','/api/pass189/i4/promotion/sweep',{'at_ns':20})
            assert status==200 and sweep['count']==1
            status,expired=request(port,'POST','/api/pass189/i4/promotion/validate',{
                'token_hash72':token['token_hash72'],'at_ns':20,
            })
            assert status==200 and expired['valid'] is False
            print('HHS_PASS_189_ITERATION_4_TOKEN_LIFECYCLE_PASS issue=1 validate=1 expiry=1 fail_closed=1')
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__=='__main__':
    main()
