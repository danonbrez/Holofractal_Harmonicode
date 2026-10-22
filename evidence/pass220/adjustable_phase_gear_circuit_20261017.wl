(* Pass 220: exact candidate-only Wolfram witness; NOT a VM81 admission receipt. *)
ClearAll[angle, m16, chiral, f, cov, rat, expectedRat, expectedCov, checks, result];
m16 = {{16,2,3,13},{5,11,10,8},{9,7,6,12},{4,14,15,1}};
chiral = m16[[All,{1,3,2,4}]];
f = {{1,2,3,5},{2,4,6,10},{3,6,9,15},{4,7,11,18}};
cov = f . chiral;
rat = Map[1/# &, f, {2}] . chiral;
expectedRat = {{223/10,13,379/30,106/5},
               {223/20,13/2,379/60,53/5},
               {223/30,13/3,379/90,106/15},
               {3988/693,3287/924,4831/1386,15355/2772}};
expectedCov = {{73,116,115,70},{146,232,230,140},
               {219,348,345,210},{270,418,414,258}};
(* Angle is an adjustable parameter; -180 is the reference only. *)
gearNumerator[theta_Integer] := theta m16;
checks = <|
  "matrix_magic_rows" -> (Total /@ chiral == ConstantArray[34,4]),
  "matrix_magic_cols" -> (Total /@ Transpose[chiral] == ConstantArray[34,4]),
  "matrix_magic_diagonals" ->
    (Tr[chiral] == 34 && Total[Diagonal[Reverse[chiral]]] == 34),
  "swap_involution" -> (chiral[[All,{1,3,2,4}]] === m16),
  "rank_F_2" -> (MatrixRank[f] == 2),
  "F_null_vector_1" -> (f . {1,1,-1,0} == {0,0,0,0}),
  "F_null_vector_2" -> (f . {0,1,1,-1} == {0,0,0,0}),
  "rational_reference" -> (rat === expectedRat),
  "covariant_reference" -> (cov === expectedCov),
  "covariant_rows" -> ((Total /@ cov) === {374,748,1122,1360}),
  "covariant_total" -> (Total[Flatten[cov]] == 3604),
  "phase_reference" -> (gearNumerator[-180] === -180 m16),
  "angles_distinct" -> (gearNumerator[-180] =!= gearNumerator[180])
|>;
result = <|"schema"->"HHS_PASS220_ADJUSTABLE_PHASE_GEAR_CANDIDATE_V1",
  "status"->If[And@@Values[checks],"PASS","FAIL"],
  "authority"->"candidate-only; no Hash72/Hash216 minting",
  "checks"->checks|>;
Print[ExportString[result,"RawJSON","Compact"->True]];
If[result["status"] =!= "PASS", Exit[1]];
