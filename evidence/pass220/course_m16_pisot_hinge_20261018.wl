(* Pass 220: exact projections of user's Module 16 and 8-S.6-.8.
   This program prints a diagnostic receipt only; Hash216 mint remains VM81-owned. *)
ClearAll[polys, x, d, f18, f19, fb, fourth, checks, result];
d = x^8-x^5-x^4-x^3-x^2-3*x-11;
polys = {
x^2-x-1, x^3-x-1, x^4-x^3-1,
x^5-x^4-x^3-x^2-1, x^3-x^2-1,
x^6-x^5-x^4+x^2-1, x^5-x^3-x^2-x-1,
x^7-x^6-x^5+x^2-1, x^6-2*x^5+x^4-x^2-1,
x^5-x^4-x^2-1, x^8-x^7-x^6+x^2-1};
f18={{1,2,3,5},{2,4,6,10},{3,6,9,15},{4,7,11,18}};
f19=ReplacePart[f18,{4,4}->19];
fb={{1,2,3,9/2},{2,4,6,17/2},{3,6,9,13},{4,7,11,19}};
fourth={4,7,11,19};
checks=<|
  "denominator_expand" -> (Expand[x*(x^7-x^4-x^3-x^2-x-3)-11]===d),
  "11_polynomials" -> (Length[polys]==11),
  "irred_exact" -> And@@(IrreduciblePolynomialQ /@ polys),
  "f18_rank2" -> (MatrixRank[f18]==2),
  "f19_rank2" -> (MatrixRank[f19]==2),
  "f18_kernel" -> (f18.{0,1,1,-1}=={0,0,0,0}),
  "f19_rotated_kernel" -> (f19.{3,1,0,-1}=={0,0,0,0}),
  "balanced_rank3" -> (MatrixRank[fb]==3 && Det[fb]==0),
  "balanced_vertical" -> (9/2+17/2==13),
  "f19_primes" -> (PrimeQ[7]&&PrimeQ[11]&&PrimeQ[19]),
  "hinge_midpoint" -> ((18+20)/2==19),
  "hinge_plus_one" -> (19==3^2*2+1),
  "hinge_offset_ledger" -> (fourth=={2^2,2^3-1,2^2*3-1,3^2*2+1}),
  "f19_column_sums" -> (Total /@ Transpose[f19]=={10,19,29,49}),
  "f19_total" -> (Total[Flatten[f19]]==107),
  "prime_census_under20" -> (Select[Range[19],PrimeQ]=={2,3,5,7,11,13,17,19})
|>;
result=<|"schema"->"PASS220_M16_8S_EXACT_PROJECTION_CANDIDATE",
 "checks"->checks,"status"->If[And@@Values[checks],"PASS","FAIL"],
 "source"->"HARMONICODE ALGEBRA user-supplied 2026-10-18 update",
 "nativeGateAdmission"->False,"hash216Mint"->False|>;
Print[ExportString[result,"RawJSON","Compact"->True]];
If[result["status"]!="PASS",Exit[1]];
