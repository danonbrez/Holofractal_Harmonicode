from __future__ import annotations
from fractions import Fraction
class TemporalContextMathEngine:
    def evaluate(self,u_num:int,u_den:int,novelty:Fraction=Fraction(1),efficiency:Fraction=Fraction(1),bottleneck:Fraction=Fraction(1),proof:Fraction=Fraction(1))->dict:
        u=Fraction(u_num,u_den)
        if not 0<=u<1: raise ValueError("U_OUT_OF_RANGE")
        G=1/(1-u); theta=u/(1-u)
        return {"u":str(u),"G":str(G),"sigma_symbolic":f"-ln(1-{u})","theta":str(theta),"epsilon_symbolic":f"{G}-1-ln({G})","context_temperature":str(theta*novelty*efficiency*bottleneck*proof)}
class NoveltyEfficiencyScheduler:
    def weight(self,coverage:Fraction,baseline:int,best_proved:int,analysis:int,proof_cost:int,handoff:int,bottleneck:Fraction,resonance:Fraction,proof_admitted:bool,safety_admitted:bool)->Fraction:
        if not proof_admitted or not safety_admitted: return Fraction(0)
        novelty=1-coverage; gain=max(0,baseline-best_proved); denominator=analysis+proof_cost+handoff
        efficiency=Fraction(gain,denominator) if denominator else Fraction(0)
        return novelty*efficiency*bottleneck*resonance
    def protect_stable_primitive(self,direct_cost:int,analysis_cost:int,classification:str)->dict:
        locked={"DIRECT_MINIMAL","CRYPTO_PROVIDER_LOCKED","CONSTANT_TIME_LOCKED","MEMORY_ORDER_LOCKED","CANONICAL_ENCODING_LOCKED","RECEIPT_ORDER_LOCKED","RUNTIME_DISPATCH_LOCKED","REALTIME_DEADLINE_LOCKED"}
        bypass=classification in locked or analysis_cost>=direct_cost
        return {"execute_direct":bypass,"classification":classification,"analysis_interposed":not bypass}
