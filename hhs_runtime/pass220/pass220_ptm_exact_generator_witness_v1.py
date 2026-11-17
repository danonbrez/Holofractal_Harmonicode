"""Exact HARMONICODE P,t,m generator source and rational reference receipt.

Only exact source registration, reconstruction and sweep scheduling are provided.
Native Ncalc operation values are not computed by this module.
"""
from fractions import Fraction
from hashlib import sha256

GENERATOR_SOURCE = "NcalcMatrixPower(((MatrixTimes(8000008,(MatrixTimes(t,NcalcEuclideanMod(MatrixTimes(24,List(((x*y)^List(1,0,1))^List((-2),1,2),(-1)+NcalcMatrixPower(NcalcMatrixPower(List(List(x,x^2,x*y),List(y^2,x+y-z-w+x^4+y^2-z^4-w^2,w^2),List(z*w,z^2,z)),List(1,0,1)),List((-2),1,2)),1+((z*w)^List(1,0,2))^List((-2),1,2))),m,30))/10^7))+(0.01-0.001+0.2)/0.209)/List((-1),1,(-1))),1)-1"
CONSTRAINED_SOURCE = "NcalcMatrixPower(((MatrixTimes(8000008,(MatrixTimes((t==25),NcalcEuclideanMod(MatrixTimes(24,List(((x*y==Sqrt(3))^List(1,0,1))^List((-2),1,2),(-1)+NcalcMatrixPower(NcalcMatrixPower(List(List(x,x^2,x*y),List(y^2,x+y-z-w+x^4+y^2-z^4-w^2,w^2),List(z*w,z^2,z)),List(1,0,1)),List((-2),1,2)),1+((z*w==Sqrt(3))^List(1,0,2))^List((-2),1,2))),(m==248),30))/10^7))+(0.01-0.001+0.2)/0.209)/List((-1),1,(-1))),1)-1"
REFERENCE = (
  (Fraction(-1012501,6250),Fraction(-3012503,6250),Fraction(-9012509,6250)),
  (Fraction(29000029,6250),Fraction(0),Fraction(3000003,3125)),
  (Fraction(-2006252,3125),Fraction(-3006253,3125),Fraction(-3001253,625)),
)
FACTOR = ((-1,-3,-9),(29,0,6),(-4,-6,-30))
CORRECTION = ((1,1,1),(0,0,0),(1,1,1))
SCALE = Fraction(8000008,10**7)*200
def witness():
    recovered = tuple(tuple(SCALE*FACTOR[i][j]-2*CORRECTION[i][j] for j in range(3)) for i in range(3))
    assert recovered == REFERENCE
    assert SCALE == Fraction(1000001,6250)
    assert (Fraction(1,100)-Fraction(1,1000)+Fraction(1,5))/Fraction(209,1000) == 1
    assert GENERATOR_SOURCE.count("NcalcMatrixPower") == 3
    assert CONSTRAINED_SOURCE.count("NcalcMatrixPower") == 3
    return {
      "schema":"HHS_PASS220_PTM_GENERATOR_EXACT_SOURCE_V1",
      "generator_sha256":sha256(GENERATOR_SOURCE.encode()).hexdigest(),
      "constrained_sha256":sha256(CONSTRAINED_SOURCE.encode()).hexdigest(),
      "reference":{"P":"Sqrt(3)","t":25,"m":248},
      "exact_reference_reconstruction":True,
      "factor_matrix":FACTOR,
      "correction_matrix":CORRECTION,
      "scale":str(SCALE),
      "sweep":tuple((t,m) for t in (24,25,26) for m in (247,248,249)),
      "native_evaluation":"NOT_EXECUTED",
      "required_next_binding":"SOURCE_BOUND_NCALC_MATRIX_POWER_AND_EUCLIDEAN_MOD",
    }
if __name__ == "__main__":
    import json
    print(json.dumps(witness(),sort_keys=True,indent=2))
