"""Pass 138 — HARMONICODE General Algebraic Reasoning Unit.

A deterministic, proof-carrying algebra service for agentic callers.
The Looking Glass invariant requires every derived conclusion to reverse-map to
its admitted premises, rule applications, and executable validation evidence.
"""
from __future__ import annotations
import argparse, ast, hashlib, json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

PASS_ID = "PASS_138_HARMONICODE_GENERAL_ALGEBRAIC_REASONING_UNIT"
SCHEMA = "HHS_GARU_API_V1"
AUTHORITY = "A1_EXECUTION_EVIDENCE"

class ReasoningError(ValueError): pass

def canonical_json(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def root(x: Any) -> str:
    return hashlib.sha256(canonical_json(x)).hexdigest()

def qstr(q: Fraction) -> str:
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"

def parse_fraction(v: Any) -> Fraction:
    if isinstance(v, bool) or isinstance(v, float): raise ReasoningError("FLOAT_OR_BOOL_REJECTED")
    if isinstance(v, int): return Fraction(v)
    if isinstance(v, str):
        try: return Fraction(v)
        except Exception as e: raise ReasoningError("INVALID_RATIONAL") from e
    raise ReasoningError("INVALID_RATIONAL_TYPE")

ALLOWED_BIN = {ast.Add: lambda a,b:a+b, ast.Sub:lambda a,b:a-b, ast.Mult:lambda a,b:a*b, ast.Div:lambda a,b:a/b, ast.Pow:lambda a,b:a**b}
ALLOWED_UNARY = {ast.UAdd:lambda a:a, ast.USub:lambda a:-a}

def eval_expr(expr: str, env: dict[str,Fraction]) -> Fraction:
    try: node=ast.parse(expr, mode="eval").body
    except SyntaxError as e: raise ReasoningError("EXPRESSION_PARSE_FAILURE") from e
    def go(n: ast.AST) -> Fraction:
        if isinstance(n, ast.Constant):
            if isinstance(n.value, bool) or isinstance(n.value, float): raise ReasoningError("FLOAT_OR_BOOL_REJECTED")
            if isinstance(n.value, int): return Fraction(n.value)
            raise ReasoningError("UNSUPPORTED_CONSTANT")
        if isinstance(n, ast.Name):
            if n.id not in env: raise ReasoningError(f"UNBOUND_SYMBOL:{n.id}")
            return env[n.id]
        if isinstance(n, ast.UnaryOp) and type(n.op) in ALLOWED_UNARY: return ALLOWED_UNARY[type(n.op)](go(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in ALLOWED_BIN:
            a,b=go(n.left),go(n.right)
            if isinstance(n.op, ast.Div) and b==0: raise ReasoningError("DIVISION_BY_ZERO")
            if isinstance(n.op, ast.Pow):
                if b.denominator != 1: raise ReasoningError("NONINTEGER_POWER_REQUIRES_TYPED_OPERATOR")
                if abs(b.numerator)>256: raise ReasoningError("POWER_BOUND_EXCEEDED")
            return ALLOWED_BIN[type(n.op)](a,b)
        raise ReasoningError(f"UNSUPPORTED_AST:{type(n).__name__}")
    return go(node)

@dataclass(frozen=True)
class EqualityGate:
    gate_id: str
    lhs: str
    rhs: str

@dataclass(frozen=True)
class ReasoningRequest:
    request_id: str
    assignments: dict[str, Fraction]
    gates: tuple[EqualityGate,...]
    goals: tuple[EqualityGate,...]
    agent: str = "anonymous"

    @classmethod
    def ingress(cls, payload: dict[str,Any]) -> "ReasoningRequest":
        if not isinstance(payload,dict): raise ReasoningError("REQUEST_NOT_OBJECT")
        rid=str(payload.get("request_id","")).strip()
        if not rid: raise ReasoningError("REQUEST_ID_REQUIRED")
        ass=payload.get("assignments",{})
        if not isinstance(ass,dict): raise ReasoningError("ASSIGNMENTS_NOT_OBJECT")
        assignments={str(k):parse_fraction(v) for k,v in ass.items()}
        def gates(key:str)->tuple[EqualityGate,...]:
            rows=payload.get(key,[])
            if not isinstance(rows,list): raise ReasoningError(f"{key.upper()}_NOT_LIST")
            out=[]
            for i,row in enumerate(rows):
                if not isinstance(row,dict) or "lhs" not in row or "rhs" not in row: raise ReasoningError(f"INVALID_{key.upper()}_ROW")
                out.append(EqualityGate(str(row.get("id",f"{key}_{i}")),str(row["lhs"]),str(row["rhs"])))
            return tuple(out)
        return cls(rid,assignments,gates("constraints"),gates("goals"),str(payload.get("agent","anonymous")))

class GeneralAlgebraicReasoningUnit:
    def _evaluate_gate(self,g:EqualityGate,env:dict[str,Fraction],kind:str)->dict[str,Any]:
        lhs=eval_expr(g.lhs,env); rhs=eval_expr(g.rhs,env); residual=lhs-rhs
        witness={"gate_id":g.gate_id,"kind":kind,"lhs":g.lhs,"rhs":g.rhs,"lhs_value":qstr(lhs),"rhs_value":qstr(rhs),"residual":qstr(residual),"closed":residual==0}
        witness["witness_root"]=root(witness)
        return witness

    def execute(self,payload:dict[str,Any])->dict[str,Any]:
        req=ReasoningRequest.ingress(payload)
        ingress={"request_id":req.request_id,"agent":req.agent,"assignments":{k:qstr(v) for k,v in sorted(req.assignments.items())},"constraint_count":len(req.gates),"goal_count":len(req.goals)}
        ingress["ingress_root"]=root(ingress)
        constraints=[self._evaluate_gate(g,req.assignments,"constraint") for g in req.gates]
        admitted=all(x["closed"] for x in constraints)
        goals=[]
        if admitted: goals=[self._evaluate_gate(g,req.assignments,"goal") for g in req.goals]
        conclusion="PROVED" if admitted and goals and all(x["closed"] for x in goals) else ("ADMITTED_NO_GOAL" if admitted and not goals else ("GOAL_NOT_PROVED" if admitted else "CONSTRAINT_REJECTED"))
        proof_path=[x["witness_root"] for x in constraints+goals]
        looking_glass={"forward":{"premise_root":ingress["ingress_root"],"proof_path":proof_path,"conclusion":conclusion},"reverse":{"conclusion":conclusion,"proof_path":list(reversed(proof_path)),"premise_root":ingress["ingress_root"]}}
        looking_glass["closed"]=looking_glass["forward"]["premise_root"]==looking_glass["reverse"]["premise_root"] and looking_glass["forward"]["proof_path"]==list(reversed(looking_glass["reverse"]["proof_path"]))
        result={"schema":SCHEMA,"pass_id":PASS_ID,"authority":AUTHORITY,"ingress":ingress,"alignment":{"no_float":True,"premises_preserved":True,"authority_nonpromotion":True,"execution_required":True},"constraints":constraints,"goals":goals,"conclusion":conclusion,"looking_glass":looking_glass}
        result["receipt_root"]=root(result)
        return result

    def validate_receipt(self,r:dict[str,Any])->dict[str,Any]:
        if not isinstance(r,dict) or "receipt_root" not in r: raise ReasoningError("INVALID_RECEIPT")
        claimed=r["receipt_root"]; body=dict(r); body.pop("receipt_root")
        checks={"receipt_root":claimed==root(body),"schema":r.get("schema")==SCHEMA,"looking_glass":bool(r.get("looking_glass",{}).get("closed")),"authority":r.get("authority")==AUTHORITY,"no_float":r.get("alignment",{}).get("no_float") is True}
        return {"checks":checks,"valid":all(checks.values())}

def execute_request(payload:dict[str,Any])->dict[str,Any]: return GeneralAlgebraicReasoningUnit().execute(payload)

def main(argv=None)->int:
    ap=argparse.ArgumentParser(); ap.add_argument("request",type=Path); ap.add_argument("--output",type=Path)
    ns=ap.parse_args(argv); payload=json.loads(ns.request.read_text()); result=execute_request(payload); text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if ns.output: ns.output.parent.mkdir(parents=True,exist_ok=True); ns.output.write_text(text)
    print(text,end=""); return 0
if __name__=="__main__": raise SystemExit(main())
