(* HHS documentation mathematical expansion audit — 2026-09-21 *)
ClearAll[P,p,q,A,B,Delta,c,mD,a2,b2,n];

loShu = {{4,9,2},{3,5,7},{8,1,6}} - 5;
phase = {-4,-3,-2,-1,1,2,3,4};
seq = Mod[8 + 16 Range[0,8],72];
display = seq /. 0 -> 72;

<|
 "factorization5184" -> And[
   72^2 == 5184,
   81*64 == 5184,
   144*36 == 5184,
   72*24*3 == 5184,
   648*8 == 5184
 ],
 "macroBranch" -> FullSimplify[
   {p+q==2P,q-p==2,p q==P^2-1,P(q-p)/(p+q)==1,P^2-p q==1},
   Assumptions->{P>1,p==P-1,q==P+1}
 ],
 "licensedDeltaProjection" -> FullSimplify[
   Sqrt[(P-1)(P+1) + P^4/(P^2 P^2)] == P,
   Assumptions->P>1
 ],
 "loShu" -> <|
   "matrix"->loShu,
   "rowSums"->Total/@loShu,
   "columnSums"->Total/@Transpose[loShu],
   "nonzeroSpectrum"->Sort[DeleteCases[Flatten[loShu],0]]
 |>,
 "orderedPairCount" -> Length[Tuples[phase,2]],
 "reciprocalInvolution" -> And@@Flatten[
   Table[-(-i)==i && -(-j)==j,{i,phase},{j,phase}]
 ],
 "q9Depth" -> FullSimplify[(1/9)^n==9^-n,
   Assumptions->Element[n,Integers]&&n>=0],
 "radical" -> FullSimplify[Sqrt[5184-64/81]==32 Sqrt[410]/9],
 "kinematicsCoreResidual" -> FullSimplify[
   P(q-p)/(p+q)==P^2-p q,
   Assumptions->{P>1,p==P-1,q==P+1}
 ],
 "kinematicsPayloadClosure" -> FullSimplify[
   c^2(P(q-p)/(p+q))==((P^2-p q)mD c^2)/Delta,
   Assumptions->{P>1,p==P-1,q==P+1,Delta>0,mD==Delta}
 ],
 "kinematicsPythagoreanClosure" -> FullSimplify[
   c^2(P(q-p)/(p+q))==a2+b2,
   Assumptions->{P>1,p==P-1,q==P+1,a2+b2==c^2}
 ],
 "zeroFrictionScalarLeft" -> FullSimplify[
   c^2(P^2-p q)==c^2,
   Assumptions->{P>1,p==P-1,q==P+1}
 ],
 "phaseOrbit" -> <|
   "mod72"->seq,
   "display"->display,
   "gcd"->GCD[16,72],
   "orbitLength"->72/GCD[16,72],
   "distinct"->DuplicateFreeQ[seq],
   "returnsAfter9"->Mod[8+16*9,72]==8,
   "stepDegrees"->360*16/72,
   "complements"->{{8,64},{24,48},{40,32},{56,16}},
   "complementsSum72"->And@@(Total[#]==72&/@{{8,64},{24,48},{40,32},{56,16}})
 |>
|>
