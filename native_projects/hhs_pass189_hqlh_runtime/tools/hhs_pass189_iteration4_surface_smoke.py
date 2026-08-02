#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, http.client, json, os, socket, subprocess, sys, tempfile, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PYTHON=ROOT/'python'; SERVER=ROOT/'server'/'hhs_pass189_iteration4_server.py'
sys.path.insert(0,str(PYTHON))
from hhs_pass189_iteration3 import hash72
from hhs_pass189_iteration4 import sign_manifest

def request(port,method,path,body=None,headers=None):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=5); data=None
    if body is not None:data=json.dumps(body).encode();headers={**(headers or {}),'Content-Type':'application/json'}
    c.request(method,path,data,headers or {});r=c.getresponse();payload=r.read();c.close();return r.status,r.getheaders(),payload

def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);port=38192;env=os.environ.copy();env.update({'HHS189_I4_DB':str(root/'i4.sqlite3'),'HHS189_I4_QUARANTINE':str(root/'q'),'HHS189_I4_QUIET':'1','PYTHONPATH':str(PYTHON)})
        p=subprocess.Popen([sys.executable,str(SERVER),'--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for _ in range(60):
                try:
                    if request(port,'GET','/api/pass189/i4/status')[0]==200:break
                except OSError:time.sleep(.05)
            else:raise RuntimeError('server did not start')
            status,_,raw=request(port,'GET','/api/pass189/i4/status');d=json.loads(raw);assert status==200 and d['vercel_required'] is False and d['real_hardware_dispatch_authorized'] is False
            status,_,html=request(port,'GET','/pass189/i4/');assert status==200 and b'Driver provenance' in html
            key=b'surface-key';key64=base64.b64encode(key).decode()
            status,_,raw=request(port,'POST','/api/pass189/i4/trust/register',{'signer_id':'surface','key_base64':key64,'created_ns':1});assert status==200
            payload=b'surface-driver';manifest={'driver_id':'surface-loop','version':'1.0.0','driver_kind':'LOOPBACK','entrypoint':'driver/main.py','signer_id':'surface','payload_sha256':hashlib.sha256(payload).hexdigest(),'operations':['WRITE'],'capabilities':['software-test'],'units':['volt'],'device_ids':['surface-device'],'minimum':0,'maximum':5,'watchdog_timeout_ms':1000,'required_interlocks':['WATCHDOG'],'created_ns':2}
            sig=sign_manifest(manifest,key)
            status,_,raw=request(port,'POST','/api/pass189/i4/package/ingest',{'package_id':'surface-package','manifest':manifest,'payload_base64':base64.b64encode(payload).decode(),'signature_hex':sig,'verification_key_base64':key64});assert status==200
            tests={k:True for k in ('manifest_identity','payload_digest','path_confinement','capability_scope','range_enforcement','watchdog_fail_closed','anti_replay','rollback_ready')}
            status,_,raw=request(port,'POST','/api/pass189/i4/conformance',{'run_id':'surface-run','package_id':'surface-package','evidence_class':'SOFTWARE_FIXTURE','tests':tests,'trace_hash72':hash72({'surface':1}),'physical_measurement':False,'created_ns':3});assert status==200
            status,_,raw=request(port,'POST','/api/pass189/i4/promote',{'promotion_id':'surface-promotion','package_id':'surface-package','approver_a_hash72':'a'*72,'approver_b_hash72':'b'*72,'issued_ns':10,'expires_ns':20});prom=json.loads(raw);assert status==200 and prom['executable'] is True and prom['real_hardware_dispatch_authorized'] is False
            status,_,raw=request(port,'POST','/api/pass189/i4/chain/verify',{});assert status==200 and json.loads(raw)['valid'] is True
            status,_,raw=request(port,'GET','/api/pass189/i4/events');assert status==200 and b'pass189-i4' in raw
            sock=socket.create_connection(('127.0.0.1',port),timeout=5);keyh=base64.b64encode(b'0123456789abcdef').decode();sock.sendall((f'GET /ws/pass189/i4 HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {keyh}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode());resp=sock.recv(4096);sock.close();assert b'101 Switching Protocols' in resp
            print('HHS_PASS_189_ITERATION_4_SURFACE_PASS http=1 visual=1 trust=1 quarantine=1 conformance=1 promotion=1 chain=1 sse=1 websocket=1')
        finally:
            p.terminate();
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill()
if __name__=='__main__':main()
