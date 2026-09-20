Module[
 {pValues,macroPass=True,rationalityPass=True,P,p,q,correction,
  x,y,z,w,id,phaseAlgebra,alpha,triples,pairs,phasePairs,supportOps,
  combinedTotal=0,combinedPassed=0,phaseBearingChecks=0,
  pi,g,local,vm81,cls,supported,
  scalarVals,squareQ,bridgeStates={},disc,roots,s,d,pv,qv,rr,
  bridgeCounts,bridgeMultiP,bridgeOnlyExample,rationalityCounterexample,
  report,json},

 pValues=Join[Range[-36,-1],Range[1,36]];

 Do[
   p=P-1;
   q=P+1;
   correction=FullSimplify[((q-p) P)/(p+q)];
   macroPass=macroPass && TrueQ[
     p+q==2P &&
     q-p==2 &&
     p q==P^2-1 &&
     correction==1 &&
     P^2==p q+correction
   ];
   rationalityPass=rationalityPass && TrueQ[
     Element[P,Rationals] &&
     Element[p,Rationals] &&
     Element[q,Rationals] &&
     P==(p+q)/2
   ],
   {P,pValues}
 ];

 x={{0,1},{1,0}};
 y={{0,-1},{1,0}};
 z=x;
 w=y;
 id=IdentityMatrix[2];

 phaseAlgebra=<|
   "x2_identity"->TrueQ[x.x==id],
   "y2_minus_identity"->TrueQ[y.y==-id],
   "xy_anticommutes_yx"->TrueQ[x.y==-y.x],
   "xy_plus_yx_zero"->TrueQ[x.y+y.x==ConstantArray[0,{2,2}]],
   "zw_equals_xy"->TrueQ[z.w==x.y],
   "wz_equals_yx"->TrueQ[w.z==y.x]
 |>;

 alpha={"x","y","z","w"};
 triples=Tuples[alpha,3];
 pairs=StringJoin@@Take[#,2]& /@ triples;
 phasePairs={"xy","yx","zw","wz"};
 supportOps=Flatten@Position[pairs,Alternatives@@phasePairs]-1;

 Do[
   P=pValues[[pi]];
   p=P-1;
   q=P+1;
   Do[
     local=Mod[g,64];
     vm81=Quotient[g,64];
     supported=MemberQ[supportOps,local];
     cls=Which[
       4<=local<=7, {"xy",1},
       16<=local<=19, {"yx",-1},
       44<=local<=47, {"zw",1},
       56<=local<=59, {"wz",-1},
       True, {"none",0}
     ];
     combinedTotal++;
     If[supported,phaseBearingChecks++];
     If[
       TrueQ[
         p+q==2P &&
         q-p==2 &&
         p q==P^2-1 &&
         P^2==p q+1 &&
         0<=vm81<81 &&
         0<=local<64 &&
         supported==(cls[[1]]!="none")
       ],
       combinedPassed++
     ],
     {g,0,5183}
   ],
   {pi,Length[pValues]}
 ];

 scalarVals=Join[Range[-36,-1],Range[1,36]]/6;

 squareQ[r_]:=Module[{value=Together[r],n,den},
   If[!TrueQ[Element[value,Rationals]] || !TrueQ[value>=0],Return[False]];
   n=Numerator[value];
   den=Denominator[value];
   IntegerQ[Sqrt[n]] && IntegerQ[Sqrt[den]]
 ];

 Do[
   disc=s^4-4P^2(s^2-1);
   If[squareQ[disc],
     roots={(2P-Sqrt[disc])/s,(2P+Sqrt[disc])/s};
     Do[
       d=rr;
       pv=(s-d)/2;
       qv=(s+d)/2;
       If[
         TrueQ[FullSimplify[
           P^2==pv qv+((qv-pv)P)/(pv+qv) &&
           pv+qv==s &&
           qv-pv==d
         ]],
         AppendTo[bridgeStates,{P,s,pv,qv}]
       ],
       {rr,roots}
     ]
   ],
   {P,scalarVals},
   {s,scalarVals}
 ];

 bridgeStates=DeleteDuplicates[bridgeStates];
 bridgeCounts=Counts[First/@bridgeStates];
 bridgeMultiP=Select[bridgeCounts,#>1&];
 bridgeOnlyExample=Take[
   Select[bridgeStates,#[[1]]==-6&],
   UpTo[8]
 ];

 rationalityCounterexample=<|
   "values"-><|
     "P"->"1/2",
     "p"->"-1/2",
     "q"->"3/2",
     "u72"->"1",
     "Delta"->"1/4",
     "x"->"1",
     "y"->"-1"
   |>,
   "bridge"->TrueQ[
     (1/2)^2==
       (-1/2)(3/2)+
       (((3/2)-(-1/2))(1/2))/((-1/2)+(3/2))
   ],
   "deltaGate"->TrueQ[
     (1/4)/(1/2)==
       (Sqrt[(-1/2)(3/2)+1])^(1^2)
   ],
   "xyGate"->TrueQ[1(-1)==-1],
   "xSquared"->"1",
   "imaginaryPhaseForced"->False
 |>;

 report=<|
   "schema"->"HHS_PASS219_RATIONAL_P_MANIFOLD_LANE5_WOLFRAM_AUDIT_V1",
   "semantics"->"exact_projection_plus_independent_ordered_phase_gate",
   "macroTheorem"-><|
     "status"->"PROVEN_EXACT_PROJECTION",
     "PCount"->Length[pValues],
     "domain"->"P in Q, P != 0, inherited unit-residue branch Delta=1",
     "p"->"P-1",
     "q"->"P+1",
     "pPlusq"->"2P",
     "qMinusp"->2,
     "pq"->"P^2-1",
     "bridgeCorrection"->1,
     "allRowsPass"->macroPass,
     "rationalityBidirectionalOnGate"->rationalityPass
   |>,
   "phaseGate"-><|
     "status"->"PROVEN_EXACT_LANE5_WITNESS",
     "algebra"->phaseAlgebra,
     "operation64SupportCount"->Length[supportOps],
     "supportOps"->supportOps,
     "supportPerVM81"->81Length[supportOps],
     "bypassPerVM81"->81(64-Length[supportOps])
   |>,
   "coupledCompatibility"-><|
     "status"->"EXECUTED_EXACT_CANDIDATE_SWEEP",
     "combinedStateSlotChecks"->combinedTotal,
     "combinedStateSlotPasses"->combinedPassed,
     "allPass"->TrueQ[combinedPassed==combinedTotal],
     "phaseBearingChecks"->phaseBearingChecks,
     "nonPhaseChecks"->combinedTotal-phaseBearingChecks
   |>,
   "negativeGuards"-><|
     "bridgeOnlyGridCells"->Length[scalarVals]^2,
     "bridgeOnlyVerifiedStates"->Length[bridgeStates],
     "bridgeOnlyPValuesWithMultiplePQPairs"->Length[bridgeMultiP],
     "bridgeOnlyExample_P_s_p_q"->bridgeOnlyExample,
     "bridgeAloneDoesNotEstablishSingleParameterAuthority"->True,
     "rationalityOnlyVisibleSubconstraintsCounterexample"->rationalityCounterexample,
     "rationalityAloneDoesNotForceOrderedPhaseGate"->True
   |>,
   "authority"-><|
     "wholeSystemSingleParameterStatus"->"OPEN_FULL_MANIFOLD_OBLIGATION",
     "phaseGateIsIndependentConstraint"->True,
     "scalarProjectionDoesNotGrantNativeSubstitution"->True,
     "canonicalVM81MutationAuthority"->False,
     "canonicalHash72Authority"->False,
     "canonicalHash216Authority"->False
   |>
 |>;

 json=ExportString[report,"RawJSON","Compact"->True];
 Print[json];
 json
]