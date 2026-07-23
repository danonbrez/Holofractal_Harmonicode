from __future__ import annotations
import sqlite3, time
from pathlib import Path
from typing import Iterable
from .common import canonical_json, sha256_text

STATES={"UNRESOLVED","BLOCKED","IMPLEMENTING","IMPLEMENTED_UNREACHABLE","REACHABLE_UNTESTED","PARTIALLY_TESTED","VERIFIED","FAILED","NOT_APPLICABLE_PROVED","SUPERSEDED_EXPLICITLY"}
CLOSED={"VERIFIED","NOT_APPLICABLE_PROVED","SUPERSEDED_EXPLICITLY"}

class ObligationLedger:
    def __init__(self, path: str | Path):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db=sqlite3.connect(self.path); self.db.row_factory=sqlite3.Row
        self.db.executescript('''
        PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
        CREATE TABLE IF NOT EXISTS obligations(id TEXT PRIMARY KEY, payload TEXT NOT NULL, state TEXT NOT NULL, updated_ns INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS transitions(seq INTEGER PRIMARY KEY AUTOINCREMENT, obligation_id TEXT NOT NULL, from_state TEXT, to_state TEXT NOT NULL, evidence TEXT NOT NULL, previous_digest TEXT NOT NULL, digest TEXT NOT NULL, created_ns INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        '''); self.db.commit()

    def import_obligations(self, obligations: Iterable[dict]) -> int:
        count=0; now=time.time_ns()
        with self.db:
            for o in obligations:
                self.db.execute("INSERT OR IGNORE INTO obligations(id,payload,state,updated_ns) VALUES(?,?,?,?)",(o["obligation_id"],canonical_json(o),"UNRESOLVED",now)); count+=self.db.total_changes>0
        return count

    def list(self, state: str|None=None) -> list[dict]:
        rows=self.db.execute("SELECT id,payload,state,updated_ns FROM obligations"+(" WHERE state=?" if state else "")+" ORDER BY id",((state,) if state else ())).fetchall()
        import json
        return [dict(json.loads(r["payload"]), state=r["state"], updated_ns=r["updated_ns"]) for r in rows]

    def read(self, oid: str) -> dict:
        rows=[x for x in self.list() if x["obligation_id"]==oid]
        if not rows: raise KeyError(oid)
        return rows[0]

    def transition(self, oid: str, state: str, evidence: dict) -> dict:
        if state not in STATES: raise ValueError("INVALID_LEDGER_STATE")
        row=self.db.execute("SELECT state FROM obligations WHERE id=?",(oid,)).fetchone()
        if not row: raise KeyError(oid)
        previous=self.db.execute("SELECT digest FROM transitions ORDER BY seq DESC LIMIT 1").fetchone(); prev=previous[0] if previous else "0"*64
        created=time.time_ns(); payload={"obligation_id":oid,"from_state":row[0],"to_state":state,"evidence":evidence,"created_ns":created,"previous_digest":prev}
        digest=sha256_text(canonical_json(payload)); payload["digest"]=digest
        with self.db:
            self.db.execute("UPDATE obligations SET state=?,updated_ns=? WHERE id=?",(state,created,oid))
            self.db.execute("INSERT INTO transitions(obligation_id,from_state,to_state,evidence,previous_digest,digest,created_ns) VALUES(?,?,?,?,?,?,?)",(oid,row[0],state,canonical_json(evidence),prev,digest,created))
        return payload

    def active(self) -> list[dict]: return [o for o in self.list() if o["state"] not in CLOSED]
    def verify_chain(self) -> bool:
        import json
        prev="0"*64
        for r in self.db.execute("SELECT * FROM transitions ORDER BY seq"):
            payload={"obligation_id":r["obligation_id"],"from_state":r["from_state"],"to_state":r["to_state"],"evidence":json.loads(r["evidence"]),"created_ns":r["created_ns"],"previous_digest":r["previous_digest"]}
            if r["previous_digest"]!=prev or sha256_text(canonical_json(payload))!=r["digest"]: return False
            prev=r["digest"]
        return True
    def close(self): self.db.close()
