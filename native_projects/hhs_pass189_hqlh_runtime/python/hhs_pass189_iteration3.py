#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, sqlite3, threading, time
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

CONTRACT="HHS-P189-HQLH-LS41-XNOR-P1-H72-H216-UPA"
ITERATION="HHS-P189-HQLH-ITERATION-3-DEVICE-ADAPTER-LEASE-WATCHDOG"
CLASSIFICATION="HHS_PASS_189_HQLH_CALIBRATION_IN_PROGRESS"
ZERO_HASH72="0"*72
SUPPORTED_DRIVERS=("LOOPBACK","FILE_SINK")
FORBIDDEN_DRIVERS=("GPIO","SERIAL","USB","NETWORK_DEVICE","ACTUATOR")
HEX72=set("0123456789abcdef")

def canonical_json(v:Any)->str:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def hash72(v:Any)->str:return hashlib.sha512(canonical_json(v).encode()).hexdigest()[:72]
def require_hash72(v:Any,name:str)->str:
    s=str(v).lower()
    if len(s)!=72 or any(c not in HEX72 for c in s):raise ValueError(f"{name} must be 72 lowercase hexadecimal glyphs")
    return s
def exact_fraction(v:Any,name:str="value")->Fraction:
    if isinstance(v,(bool,float)):raise ValueError(f"{name} rejects floating-point or Boolean canonical ingress")
    if isinstance(v,Fraction):return v
    if isinstance(v,int):return Fraction(v,1)
    if isinstance(v,str):
        if "." in v or "e" in v.lower():raise ValueError(f"{name} requires exact integer or rational pair")
        return Fraction(int(v),1)
    if isinstance(v,Mapping) and set(v)=={"numerator","denominator"}:
        if isinstance(v["numerator"],float) or isinstance(v["denominator"],float):raise ValueError(f"{name} rejects floating-point canonical ingress")
        return Fraction(int(v["numerator"]),int(v["denominator"]))
    raise ValueError(f"{name} requires exact integer or rational pair")
def fraction_json(v:Fraction)->dict[str,int]:return {"numerator":v.numerator,"denominator":v.denominator}
def integer(v:Any,name:str,positive:bool=False)->int:
    if isinstance(v,(bool,float)):raise ValueError(f"{name} must be an integer")
    n=int(v)
    if n<0 or (positive and n==0):raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return n
def now_ns()->int:return time.time_ns()

class DeviceAuthority:
    def __init__(self,database:str|os.PathLike[str],*,state_directory:str|os.PathLike[str]|None=None,busy_timeout_ms:int=1500,retry_count:int=4):
        self.database=Path(database);self.database.parent.mkdir(parents=True,exist_ok=True)
        self.state_directory=Path(state_directory or self.database.parent).resolve();self.state_directory.mkdir(parents=True,exist_ok=True)
        self.busy_timeout_ms=integer(busy_timeout_ms,"busy_timeout_ms",True);self.retry_count=integer(retry_count,"retry_count",True)
        self._lock=threading.RLock();self._connection=sqlite3.connect(str(self.database),timeout=self.busy_timeout_ms/1000,check_same_thread=False,isolation_level=None)
        self._connection.row_factory=sqlite3.Row
        for q in ("PRAGMA journal_mode=WAL","PRAGMA synchronous=FULL","PRAGMA foreign_keys=ON",f"PRAGMA busy_timeout={self.busy_timeout_ms}"):self._connection.execute(q)
        self._connection.executescript("""
CREATE TABLE IF NOT EXISTS events(sequence INTEGER PRIMARY KEY,event_type TEXT NOT NULL,predecessor_hash72 TEXT NOT NULL,successor_hash72 TEXT NOT NULL UNIQUE,payload_json TEXT NOT NULL,created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS adapters(adapter_id TEXT PRIMARY KEY,payload_json TEXT NOT NULL,adapter_hash72 TEXT NOT NULL UNIQUE,enabled INTEGER NOT NULL,created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS leases(lease_id TEXT PRIMARY KEY,adapter_id TEXT NOT NULL REFERENCES adapters(adapter_id),payload_json TEXT NOT NULL,lease_hash72 TEXT NOT NULL UNIQUE,expires_ns INTEGER NOT NULL,max_commands INTEGER NOT NULL,commands_used INTEGER NOT NULL DEFAULT 0,status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS commands(command_id TEXT PRIMARY KEY,adapter_id TEXT NOT NULL REFERENCES adapters(adapter_id),lease_id TEXT NOT NULL REFERENCES leases(lease_id),sequence INTEGER NOT NULL,payload_json TEXT NOT NULL,command_hash72 TEXT NOT NULL UNIQUE,deadline_ns INTEGER NOT NULL,status TEXT NOT NULL,UNIQUE(adapter_id,sequence));
CREATE TABLE IF NOT EXISTS traces(trace_id TEXT PRIMARY KEY,command_id TEXT NOT NULL UNIQUE REFERENCES commands(command_id),payload_json TEXT NOT NULL,trace_hash72 TEXT NOT NULL UNIQUE,created_ns INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS checkpoints(checkpoint_id TEXT PRIMARY KEY,captured_sequence INTEGER NOT NULL,captured_root_hash72 TEXT NOT NULL,digest_sha256 TEXT NOT NULL,path TEXT NOT NULL,created_ns INTEGER NOT NULL);
""")
    def close(self):
        with self._lock:self._connection.close()
    @contextmanager
    def _tx(self)->Iterator[sqlite3.Connection]:
        with self._lock:
            for attempt in range(self.retry_count):
                try:self._connection.execute("BEGIN IMMEDIATE");break
                except sqlite3.OperationalError as e:
                    if "locked" not in str(e).lower() or attempt+1>=self.retry_count:raise
                    time.sleep((attempt+1)*.01)
            try:yield self._connection;self._connection.execute("COMMIT")
            except Exception:self._connection.execute("ROLLBACK");raise
    def _root(self,c):
        r=c.execute("SELECT sequence,successor_hash72 FROM events ORDER BY sequence DESC LIMIT 1").fetchone();return (int(r[0]),str(r[1])) if r else (0,ZERO_HASH72)
    def _event(self,c,t,p,ns):
        seq,prev=self._root(c);payload={"schema":"HHS_PASS_189_ITERATION_3_EVENT_V1","contract":CONTRACT,"iteration":ITERATION,"classification":CLASSIFICATION,"sequence":seq+1,"event_type":t,"predecessor_hash72":prev,"payload":dict(p),"created_ns":ns};succ=hash72(payload)
        c.execute("INSERT INTO events VALUES(?,?,?,?,?,?)",(seq+1,t,prev,succ,canonical_json(payload),ns));return {**payload,"successor_hash72":succ}
    def get_adapter(self,adapter_id):
        with self._lock:r=self._connection.execute("SELECT payload_json,enabled FROM adapters WHERE adapter_id=?",(adapter_id,)).fetchone()
        if not r:raise ValueError("unknown adapter_id")
        p=json.loads(r[0]);p["enabled"]=bool(r[1]);return p
    def register_adapter(self,m):
        aid=str(m.get("adapter_id","")).strip();did=str(m.get("device_id","")).strip();kind=str(m.get("driver_kind","")).upper();unit=str(m.get("unit","")).strip()
        if not all((aid,did,unit)):raise ValueError("adapter_id, device_id, and unit are required")
        if kind not in SUPPORTED_DRIVERS:raise ValueError(f"driver_kind must be one of {SUPPORTED_DRIVERS}; physical drivers are not implemented")
        lo,hi=exact_fraction(m.get("minimum",0),"minimum"),exact_fraction(m.get("maximum",0),"maximum")
        if lo>hi:raise ValueError("minimum cannot exceed maximum")
        ops=sorted({str(x).strip().upper() for x in m.get("allowed_operations",[]) if str(x).strip()})
        if not ops:raise ValueError("allowed_operations must be non-empty")
        wd=integer(m.get("watchdog_timeout_ms",1000),"watchdog_timeout_ms",True);mx=integer(m.get("max_commands_per_lease",1),"max_commands_per_lease",True)
        if wd>60000 or mx>10000:raise ValueError("adapter bounds exceeded")
        if not bool(m.get("software_attested",False)):raise ValueError("software_attested must be true")
        ns=integer(m.get("created_ns",now_ns()),"created_ns");sink=""
        if kind=="FILE_SINK":
            dest=(self.state_directory/(str(m.get("sink_directory","sinks")).strip() or "sinks")).resolve()
            try:dest.relative_to(self.state_directory)
            except ValueError as e:raise ValueError("sink_directory must remain inside state_directory") from e
            dest.mkdir(parents=True,exist_ok=True);sink=str(dest.relative_to(self.state_directory))
        p={"schema":"HHS_PASS_189_ITERATION_3_ADAPTER_V1","adapter_id":aid,"device_id":did,"driver_kind":kind,"unit":unit,"minimum":fraction_json(lo),"maximum":fraction_json(hi),"allowed_operations":ops,"watchdog_timeout_ms":wd,"max_commands_per_lease":mx,"software_attested":True,"enabled":bool(m.get("enabled",True)),"sink_directory":sink,"created_ns":ns};p["adapter_hash72"]=hash72(p)
        with self._tx() as c:
            r=c.execute("SELECT payload_json FROM adapters WHERE adapter_id=?",(aid,)).fetchone()
            if r:
                current=json.loads(r[0])
                if canonical_json(current)!=canonical_json(p):raise ValueError("adapter_id already exists with different canonical payload")
                return current
            c.execute("INSERT INTO adapters VALUES(?,?,?,?,?)",(aid,canonical_json(p),p["adapter_hash72"],int(p["enabled"]),ns));e=self._event(c,"ADAPTER_REGISTERED",p,ns)
        return {**p,"event":e}
    def set_adapter_enabled(self,aid,enabled,*,created_ns=None):
        ns=now_ns() if created_ns is None else integer(created_ns,"created_ns")
        with self._tx() as c:
            if not c.execute("SELECT 1 FROM adapters WHERE adapter_id=?",(aid,)).fetchone():raise ValueError("unknown adapter_id")
            c.execute("UPDATE adapters SET enabled=? WHERE adapter_id=?",(int(enabled),aid))
            if not enabled:c.execute("UPDATE leases SET status='REVOKED' WHERE adapter_id=? AND status='ACTIVE'",(aid,));c.execute("UPDATE commands SET status='REVOKED' WHERE adapter_id=? AND status='PREPARED'",(aid,))
            e=self._event(c,"ADAPTER_ENABLED" if enabled else "ADAPTER_DISABLED",{"adapter_id":aid,"enabled":bool(enabled)},ns)
        return {"adapter_id":aid,"enabled":bool(enabled),"event":e}
    def issue_lease(self,m):
        lid=str(m.get("lease_id","")).strip();aid=str(m.get("adapter_id","")).strip();issued=integer(m.get("issued_ns",now_ns()),"issued_ns");expires=integer(m.get("expires_ns",0),"expires_ns")
        if not lid or not aid:raise ValueError("lease_id and adapter_id are required")
        if expires<=issued or expires-issued>86400000000000:raise ValueError("lease expiry is invalid or exceeds 24 hours")
        adapter=self.get_adapter(aid)
        if not adapter["enabled"]:raise ValueError("adapter is disabled")
        ops=sorted({str(x).strip().upper() for x in m.get("allowed_operations",[]) if str(x).strip()})
        if not ops or not set(ops)<=set(adapter["allowed_operations"]):raise ValueError("lease operations must be a non-empty subset")
        mx=integer(m.get("max_commands",1),"max_commands",True)
        if mx>int(adapter["max_commands_per_lease"]):raise ValueError("max_commands exceeds adapter bound")
        p={"schema":"HHS_PASS_189_ITERATION_3_LEASE_V1","lease_id":lid,"adapter_id":aid,"issued_ns":issued,"expires_ns":expires,"max_commands":mx,"commands_used":0,"allowed_operations":ops,"arm_token_hash72":require_hash72(m.get("arm_token_hash72",""),"arm_token_hash72"),"status":"ACTIVE"};p["lease_hash72"]=hash72(p)
        with self._tx() as c:
            r=c.execute("SELECT payload_json,status,commands_used FROM leases WHERE lease_id=?",(lid,)).fetchone()
            if r:
                cur=json.loads(r[0]);cur["status"]=r[1];cur["commands_used"]=r[2]
                if cur.get("lease_hash72")!=p["lease_hash72"]:raise ValueError("lease_id already exists with different canonical payload")
                return cur
            c.execute("INSERT INTO leases VALUES(?,?,?,?,?,?,0,'ACTIVE')",(lid,aid,canonical_json(p),p["lease_hash72"],expires,mx));e=self._event(c,"LEASE_ISSUED",p,issued)
        return {**p,"event":e}
    def revoke_lease(self,lid,*,created_ns=None):
        ns=now_ns() if created_ns is None else integer(created_ns,"created_ns")
        with self._tx() as c:
            if not c.execute("SELECT 1 FROM leases WHERE lease_id=?",(lid,)).fetchone():raise ValueError("unknown lease_id")
            c.execute("UPDATE leases SET status='REVOKED' WHERE lease_id=?",(lid,));c.execute("UPDATE commands SET status='REVOKED' WHERE lease_id=? AND status='PREPARED'",(lid,));e=self._event(c,"LEASE_REVOKED",{"lease_id":lid},ns)
        return {"lease_id":lid,"status":"REVOKED","event":e}
    def _candidate(self,m):
        if not bool(m.get("physical_output_authorized",False)) or str(m.get("dispatch_class",""))!="CANDIDATE_ONLY_NO_DEVICE_DRIVER":raise ValueError("command requires an Iteration 2 admitted physical candidate")
        pid=str(m.get("profile_id","")).strip()
        if not pid:raise ValueError("candidate profile_id is required")
        return {"candidate_hash72":require_hash72(m.get("candidate_hash72",""),"candidate_hash72"),"profile_id":pid,"physical_output_authorized":True,"dispatch_class":"CANDIDATE_ONLY_NO_DEVICE_DRIVER","candidate_receipt_index":integer(m.get("candidate_receipt_index",0),"candidate_receipt_index")}
    def prepare_command(self,m):
        cid=str(m.get("command_id","")).strip();lid=str(m.get("lease_id","")).strip();seq=integer(m.get("sequence",0),"sequence",True);op=str(m.get("operation","")).strip().upper();unit=str(m.get("unit","")).strip();issued=integer(m.get("issued_ns",now_ns()),"issued_ns");val=exact_fraction(m.get("value",0));candidate=self._candidate(m.get("candidate",{}));arm=require_hash72(m.get("arm_token_hash72",""),"arm_token_hash72")
        if not cid or not lid:raise ValueError("command_id and lease_id are required")
        with self._tx() as c:
            l=c.execute("SELECT * FROM leases WHERE lease_id=?",(lid,)).fetchone()
            if not l:raise ValueError("unknown lease_id")
            lp=json.loads(l["payload_json"])
            if l["status"]!="ACTIVE" or issued>=l["expires_ns"] or l["commands_used"]>=l["max_commands"]:raise ValueError("lease is inactive, expired, or exhausted")
            if arm!=lp["arm_token_hash72"] or op not in lp["allowed_operations"]:raise ValueError("operator arm or operation outside lease authority")
            arow=c.execute("SELECT payload_json,enabled FROM adapters WHERE adapter_id=?",(l["adapter_id"],)).fetchone();a=json.loads(arow[0])
            if not arow or not arow[1]:raise ValueError("adapter is disabled")
            if op not in a["allowed_operations"] or unit!=a["unit"] or not exact_fraction(a["minimum"])<=val<=exact_fraction(a["maximum"]):raise ValueError("command operation, unit, or range invalid")
            deadline=issued+int(a["watchdog_timeout_ms"])*1000000;p={"schema":"HHS_PASS_189_ITERATION_3_COMMAND_V1","command_id":cid,"adapter_id":a["adapter_id"],"lease_id":lid,"sequence":seq,"operation":op,"value":fraction_json(val),"unit":unit,"issued_ns":issued,"deadline_ns":deadline,"candidate":candidate,"status":"PREPARED"};p["command_hash72"]=hash72(p)
            try:c.execute("INSERT INTO commands VALUES(?,?,?,?,?,?,?,'PREPARED')",(cid,a["adapter_id"],lid,seq,canonical_json(p),p["command_hash72"],deadline))
            except sqlite3.IntegrityError as e:raise ValueError("command_id or adapter sequence already admitted") from e
            e=self._event(c,"COMMAND_PREPARED",p,issued)
        return {**p,"event":e}
    def execute_command(self,cid,*,execution_ns=None):
        ns=now_ns() if execution_ns is None else integer(execution_ns,"execution_ns");sink=None
        with self._tx() as c:
            cmd=c.execute("SELECT * FROM commands WHERE command_id=?",(cid,)).fetchone()
            if not cmd:raise ValueError("unknown command_id")
            if cmd["status"]!="PREPARED":raise ValueError("command is not PREPARED")
            if ns>cmd["deadline_ns"]:
                c.execute("UPDATE commands SET status='EXPIRED' WHERE command_id=?",(cid,));e=self._event(c,"COMMAND_EXPIRED",{"command_id":cid,"execution_ns":ns},ns);return {"command_id":cid,"status":"EXPIRED","executed":False,"event":e}
            lease=c.execute("SELECT * FROM leases WHERE lease_id=?",(cmd["lease_id"],)).fetchone();adapter_row=c.execute("SELECT payload_json,enabled FROM adapters WHERE adapter_id=?",(cmd["adapter_id"],)).fetchone()
            if not lease or lease["status"]!="ACTIVE" or ns>=lease["expires_ns"] or lease["commands_used"]>=lease["max_commands"]:raise ValueError("lease is inactive, expired, or exhausted")
            if not adapter_row or not adapter_row[1]:raise ValueError("adapter is disabled")
            adapter=json.loads(adapter_row[0]);command=json.loads(cmd["payload_json"]);requested=exact_fraction(command["value"]);trace={"schema":"HHS_PASS_189_ITERATION_3_TRACE_V1","command_id":cid,"adapter_id":adapter["adapter_id"],"driver_kind":adapter["driver_kind"],"execution_class":"SOFTWARE_LOOPBACK_TRACE","requested":fraction_json(requested),"observed":fraction_json(requested),"residual":fraction_json(Fraction(0,1)),"unit":command["unit"],"operation":command["operation"],"execution_ns":ns,"hardware_measurement":False,"physical_claim":False};trace["trace_hash72"]=hash72(trace);trace["trace_id"]=hash72({"command_id":cid,"trace_hash72":trace["trace_hash72"]})
            c.execute("UPDATE commands SET status='EXECUTED' WHERE command_id=?",(cid,));c.execute("UPDATE leases SET commands_used=commands_used+1 WHERE lease_id=?",(cmd["lease_id"],));c.execute("INSERT INTO traces VALUES(?,?,?,?,?)",(trace["trace_id"],cid,canonical_json(trace),trace["trace_hash72"],ns));e=self._event(c,"COMMAND_EXECUTED",trace,ns)
            if adapter["driver_kind"]=="FILE_SINK":sink=((self.state_directory/adapter["sink_directory"]).resolve()/f"{cid}.json",trace)
        if sink:
            target,p=sink;target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_suffix(".tmp");tmp.write_text(canonical_json(p)+"\n");os.replace(tmp,target)
        return {**trace,"event":e,"dispatch_status":"SOFTWARE_TEST_DRIVER_ONLY"}
    def sweep_watchdogs(self,*,sweep_ns=None):
        ns=now_ns() if sweep_ns is None else integer(sweep_ns,"sweep_ns")
        with self._tx() as c:
            ids=[r[0] for r in c.execute("SELECT command_id FROM commands WHERE status='PREPARED' AND deadline_ns<? ORDER BY command_id",(ns,)).fetchall()]
            for cid in ids:c.execute("UPDATE commands SET status='EXPIRED' WHERE command_id=?",(cid,));self._event(c,"COMMAND_EXPIRED",{"command_id":cid,"sweep_ns":ns},ns)
        return {"expired":ids,"count":len(ids),"sweep_ns":ns}
    def get_command(self,cid):
        with self._lock:r=self._connection.execute("SELECT payload_json,status FROM commands WHERE command_id=?",(cid,)).fetchone();t=self._connection.execute("SELECT payload_json FROM traces WHERE command_id=?",(cid,)).fetchone()
        if not r:raise ValueError("unknown command_id")
        p=json.loads(r[0]);p["status"]=r[1];p["trace"]=json.loads(t[0]) if t else None;return p
    def verify_event_chain(self):
        with self._lock:rows=self._connection.execute("SELECT * FROM events ORDER BY sequence").fetchall()
        prev=ZERO_HASH72
        for i,r in enumerate(rows,1):
            p=json.loads(r["payload_json"])
            if r["sequence"]!=i or p["sequence"]!=i:return {"valid":False,"reason":"SEQUENCE_DRIFT","sequence":i}
            if r["predecessor_hash72"]!=prev or p["predecessor_hash72"]!=prev:return {"valid":False,"reason":"PREDECESSOR_DRIFT","sequence":i}
            if hash72(p)!=r["successor_hash72"]:return {"valid":False,"reason":"HASH_DRIFT","sequence":i}
            prev=r["successor_hash72"]
        return {"valid":True,"events":len(rows),"root_hash72":prev}
    def checkpoint(self,path,*,checkpoint_id,created_ns=None):
        ns=now_ns() if created_ns is None else integer(created_ns,"created_ns");target=Path(path).resolve()
        if target.exists():raise ValueError("checkpoint path must not already exist")
        target.parent.mkdir(parents=True,exist_ok=True)
        with self._lock:seq,root=self._root(self._connection);self._connection.execute("PRAGMA wal_checkpoint(FULL)");dst=sqlite3.connect(str(target));self._connection.backup(dst);dst.close()
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        with self._tx() as c:c.execute("INSERT INTO checkpoints VALUES(?,?,?,?,?,?)",(checkpoint_id,seq,root,digest,str(target),ns));e=self._event(c,"CHECKPOINT_CREATED",{"checkpoint_id":checkpoint_id,"captured_sequence":seq,"captured_root_hash72":root,"digest_sha256":digest},ns)
        return {"checkpoint_id":checkpoint_id,"path":str(target),"captured_sequence":seq,"captured_root_hash72":root,"digest_sha256":digest,"event":e}
    @staticmethod
    def verify_checkpoint(path,digest_sha256,captured_sequence,captured_root_hash72):
        p=Path(path)
        if not p.is_file():return {"valid":False,"reason":"MISSING_CHECKPOINT"}
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        if digest!=digest_sha256:return {"valid":False,"reason":"DIGEST_MISMATCH","digest_sha256":digest}
        c=sqlite3.connect(str(p));r=c.execute("SELECT sequence,successor_hash72 FROM events ORDER BY sequence DESC LIMIT 1").fetchone();c.close();seq=int(r[0]) if r else 0;root=str(r[1]) if r else ZERO_HASH72
        return {"valid":seq==int(captured_sequence) and root==captured_root_hash72,"sequence":seq,"root_hash72":root,"digest_sha256":digest}
    @staticmethod
    def recover_checkpoint(source,destination,**v):
        target=Path(destination)
        if target.exists():raise ValueError("recovery destination must not already exist")
        result=DeviceAuthority.verify_checkpoint(source,v["digest_sha256"],v["captured_sequence"],v["captured_root_hash72"])
        if not result["valid"]:raise ValueError("checkpoint verification failed")
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);return {"recovered":True,"destination":str(target),**result}
    def status(self):
        with self._lock:
            q=lambda sql:self._connection.execute(sql).fetchone()[0]
            seq,root=self._root(self._connection)
            counts={"events":q("SELECT COUNT(*) FROM events"),"adapters":q("SELECT COUNT(*) FROM adapters"),"enabled_adapters":q("SELECT COUNT(*) FROM adapters WHERE enabled=1"),"active_leases":q("SELECT COUNT(*) FROM leases WHERE status='ACTIVE'"),"prepared_commands":q("SELECT COUNT(*) FROM commands WHERE status='PREPARED'"),"executed_commands":q("SELECT COUNT(*) FROM commands WHERE status='EXECUTED'"),"expired_commands":q("SELECT COUNT(*) FROM commands WHERE status='EXPIRED'"),"traces":q("SELECT COUNT(*) FROM traces"),"checkpoints":q("SELECT COUNT(*) FROM checkpoints")}
        return {"contract":CONTRACT,"iteration":ITERATION,"classification":CLASSIFICATION,"deployment_authority":"DIGITALOCEAN_SELF_HOSTED","vercel_required":False,"supported_drivers":list(SUPPORTED_DRIVERS),"forbidden_physical_drivers":list(FORBIDDEN_DRIVERS),"actual_physical_dispatch":False,"receipt_index":seq,"root_hash72":root,**counts}

def main(argv:Sequence[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("--database",default=os.environ.get("HHS189_I3_DB","iteration3.sqlite3"));p.add_argument("--state-directory",default=os.environ.get("HHS189_I3_STATE","."));s=p.add_subparsers(dest="command",required=True);s.add_parser("status");r=s.add_parser("register-loopback");r.add_argument("adapter_id");r.add_argument("device_id");c=s.add_parser("checkpoint");c.add_argument("path");c.add_argument("checkpoint_id");a=p.parse_args(argv);d=DeviceAuthority(a.database,state_directory=a.state_directory)
    try:
        if a.command=="status":result=d.status()
        elif a.command=="register-loopback":result=d.register_adapter({"adapter_id":a.adapter_id,"device_id":a.device_id,"driver_kind":"LOOPBACK","unit":"unit","minimum":-100,"maximum":100,"allowed_operations":["SET"],"watchdog_timeout_ms":1000,"max_commands_per_lease":10,"software_attested":True,"created_ns":1})
        else:result=d.checkpoint(a.path,checkpoint_id=a.checkpoint_id)
        print(json.dumps(result,indent=2,sort_keys=True))
    finally:d.close()
    return 0
if __name__=="__main__":raise SystemExit(main())
