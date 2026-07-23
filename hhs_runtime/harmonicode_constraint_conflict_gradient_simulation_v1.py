"""Pass 143 — continuous constraint conflict gradients and temperature orthogonality.

Exact-rational parallel simulations evaluate recursively nested balancing equations.
Quantum/audio/visual adapters are deterministic projections of the same symbolic
state; they do not promote simulation output into physical authority.
"""
from __future__ import annotations
import argparse, hashlib, json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

PASS_ID="PASS_143_CONTINUOUS_CONSTRAINT_CONFLICT_GRADIENTS"
SCHEMA="HHS_CONSTRAINT_GRADIENT_SIMULATION_API_V1"
AUTHORITY="A1_EXECUTION_EVIDENCE"
PHASE_MODULUS=72

class ConflictSimulationError(ValueError): pass

def canonical_json(x:Any)->bytes:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha256(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def F(x:Any)->Fraction:
    if isinstance(x,bool) or isinstance(x,float): raise ConflictSimulationError("NO_FLOAT_AUTHORITY")
    if isinstance(x,Fraction): return x
    if isinstance(x,int): return Fraction(x,1)
    if isinstance(x,str):
        try:return Fraction(x)
        except Exception as e: raise ConflictSimulationError("INVALID_RATIONAL") from e
    raise ConflictSimulationError("INVALID_RATIONAL")
def fs(x:Fraction)->str:return str(x.numerator) if x.denominator==1 else f"{x.numerator}/{x.denominator}"
def vadd(a,b):return [x+y for x,y in zip(a,b)]
def vsub(a,b):return [x-y for x,y in zip(a,b)]
def vscale(a,s):return [x*s for x in a]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),Fraction(0))
def norm2(a):return dot(a,a)

def _parse_request(req:dict[str,Any]):
    if not isinstance(req,dict): raise ConflictSimulationError("REQUEST_NOT_OBJECT")
    dims=[str(x) for x in req.get("dimensions",[])]
    if not dims or len(set(dims))!=len(dims): raise ConflictSimulationError("INVALID_DIMENSIONS")
    initial=req.get("initial_state",{})
    state=[F(initial[d]) for d in dims]
    constraints=req.get("constraints",[])
    if not constraints: raise ConflictSimulationError("CONSTRAINTS_REQUIRED")
    rows=[]
    ids=set()
    for c in constraints:
        cid=str(c.get("id","")); coeff=c.get("coefficients",{}); target=F(c.get("target",0)); priority=F(c.get("priority",1)); temp=F(c.get("temperature",1))
        if not cid or cid in ids: raise ConflictSimulationError("INVALID_CONSTRAINT_ID")
        ids.add(cid)
        if priority<0 or temp<=0: raise ConflictSimulationError("INVALID_PRIORITY_OR_TEMPERATURE")
        vec=[F(coeff.get(d,0)) for d in dims]
        if norm2(vec)==0: raise ConflictSimulationError("ZERO_CONSTRAINT_GRADIENT")
        rows.append({"id":cid,"a":vec,"b":target,"priority":priority,"temperature":temp,"children":[str(x) for x in c.get("children",[])]})
    known={r['id'] for r in rows}
    if any(ch not in known for r in rows for ch in r['children']): raise ConflictSimulationError("UNKNOWN_NESTED_CONSTRAINT")
    # cycle check
    graph={r['id']:r['children'] for r in rows}; visiting=set(); done=set()
    def dfs(x):
        if x in visiting: raise ConflictSimulationError("NESTED_CONSTRAINT_CYCLE")
        if x in done:return
        visiting.add(x)
        for y in graph[x]:dfs(y)
        visiting.remove(x);done.add(x)
    for x in sorted(graph):dfs(x)
    return dims,state,rows

def residual(row,state): return dot(row['a'],state)-row['b']
def raw_gradient(row,state): return vscale(row['a'], residual(row,state)*row['priority']/row['temperature'])
def orthogonalize(g,temp_axis):
    d=norm2(temp_axis)
    return g if d==0 else vsub(g,vscale(temp_axis,dot(g,temp_axis)/d))

def nested_factor(row, byid, state, depth=0):
    # recursively nested balance: 1/(1 + sum child squared residuals / temperature)
    if depth>81: raise ConflictSimulationError("NESTED_DEPTH_EXCEEDED")
    burden=Fraction(0)
    for cid in row['children']:
        ch=byid[cid]; r=residual(ch,state)
        burden += r*r/ch['temperature']
        burden += (Fraction(1)-nested_factor(ch,byid,state,depth+1))
    return Fraction(1,1)/(Fraction(1,1)+burden)

def project_one(state,row,step):
    r=residual(row,state); return vsub(state,vscale(row['a'], step*r/norm2(row['a'])))

@dataclass
class ConstraintConflictSimulator:
    def execute(self,req:dict[str,Any])->dict[str,Any]:
        dims,state,rows=_parse_request(req); byid={r['id']:r for r in rows}
        iterations=int(req.get('iterations',8)); branches=int(req.get('parallel_branches',4)); step=F(req.get('step','1/2'))
        if not (1<=iterations<=81 and 1<=branches<=81 and 0<step<=1): raise ConflictSimulationError("INVALID_EXECUTION_BOUNDS")
        temp_axis=[sum((r['a'][i]/r['temperature'] for r in rows),Fraction(0)) for i in range(len(dims))]
        trace=[]
        def energy_of(st):
            return sum((r['priority']*residual(r,st)**2/r['temperature'] for r in rows),Fraction(0))
        for k in range(iterations):
            grads=[]; branch_states=[]; branch_rows=[]
            for b in range(branches):
                r=rows[(k*branches+b)%len(rows)]
                factor=nested_factor(r,byid,state)
                g=orthogonalize(raw_gradient(r,state),temp_axis)
                g=vscale(g,factor)
                # Stable exact branch: bounded projection toward one admitted constraint.
                cand=project_one(state,r,step*factor)
                grads.append(g);branch_states.append(cand);branch_rows.append(r['id'])
            merged=[sum(vals,Fraction(0))/branches for vals in zip(*branch_states)]
            candidates=[state,merged]+branch_states
            # Monotonic deterministic admission: energy, then canonical rational tuple.
            next_state=min(candidates,key=lambda st:(energy_of(st),tuple((x.numerator,x.denominator) for x in st)))
            conflicts={r['id']:residual(r,next_state) for r in rows}
            energy=energy_of(next_state)
            orth=[dot(g,temp_axis) for g in grads]
            item={"iteration":k,"branch_constraints":branch_rows,"state":{d:fs(v) for d,v in zip(dims,next_state)},
                  "conflict_residuals":{x:fs(y) for x,y in conflicts.items()},"conflict_energy":fs(energy),
                  "temperature_orthogonality": [fs(x) for x in orth],"phase_index":k%PHASE_MODULUS,
                  "admission":"MONOTONIC_ENERGY_MINIMUM"}
            item['trace_root']=sha256(canonical_json(item));trace.append(item);state=next_state
        final_res={r['id']:residual(r,state) for r in rows}
        initial_vec=[F(req['initial_state'][d]) for d in dims]
        initial_energy=sum((r['priority']*residual(r,initial_vec)**2/r['temperature'] for r in rows),Fraction(0))
        final_energy=sum((r['priority']*final_res[r['id']]**2/r['temperature'] for r in rows),Fraction(0))
        smoothed=final_energy<=initial_energy
        projections=self._projections(state,final_res,rows)
        out={"pass_id":PASS_ID,"schema":SCHEMA,"authority":AUTHORITY,"request_id":str(req.get('request_id','')),
             "dimensions":dims,"initial_conflict_energy":fs(initial_energy),"final_conflict_energy":fs(final_energy),
             "smoothed_or_equal":smoothed,"final_state":{d:fs(v) for d,v in zip(dims,state)},
             "final_residuals":{x:fs(y) for x,y in final_res.items()},"temperature_axis":[fs(x) for x in temp_axis],
             "orthogonality_closed":all(x=='0' for t in trace for x in t['temperature_orthogonality']),
             "simulation_projections":projections,"trace":trace,
             "classification":"CONFLICT_SMOOTHED" if smoothed else "CONFLICT_NOT_SMOOTHED"}
        out['receipt_root']=sha256(canonical_json(out));return out
    def _projections(self,state,res,rows):
        # deterministic multimodal views; all exact integers/rationals
        phase=[(abs(v.numerator)+v.denominator)%72 for v in state]
        quantum={"basis_residue":phase,"normalization_witness":fs(sum((v*v for v in state),Fraction(0)))}
        audio={"sample_rate":72,"symbolic_amplitudes":[fs(v) for v in state],"phase_offsets":phase}
        visual={"coordinates":[fs(v) for v in state],"constraint_intensity":{r['id']:fs(abs(res[r['id']])) for r in rows}}
        return {"quantum":quantum,"audio":audio,"visual":visual,"authority":"SIMULATION_PROJECTION_ONLY"}
    def validate_receipt(self,r):
        root=r.get('receipt_root'); calc=sha256(canonical_json({k:v for k,v in r.items() if k!='receipt_root'}))
        errors=[]
        if root!=calc:errors.append('RECEIPT_ROOT_MISMATCH')
        if not r.get('orthogonality_closed'):errors.append('TEMPERATURE_ORTHOGONALITY_OPEN')
        if r.get('simulation_projections',{}).get('authority')!='SIMULATION_PROJECTION_ONLY':errors.append('PROJECTION_AUTHORITY_MISMATCH')
        return {"valid":not errors,"errors":errors}

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('request');p.add_argument('--output');a=p.parse_args(argv)
    req=json.loads(Path(a.request).read_text()); out=ConstraintConflictSimulator().execute(req)
    text=json.dumps(out,indent=2,sort_keys=True)
    if a.output:Path(a.output).write_text(text+'\n')
    else:print(text)
if __name__=='__main__':main()
