(* Q81 exact static-guard extension, Module 128/130 -> 131.
   External Wolfram scalar projection checks are not native gate certification.
   Literal finite-decimal calibrations are treated as exact rational INPUT
   STRINGS, not proof of exact physical or irrational identities. *)
Module[{P,p,q,delta,a2,b2,c2,c4,ab,ba,alpha,z,cm,cp,k,
 proofs,static,abp,gates,returns,all,step,initial,first,second,
 carrier,hnanReturn,returnInvariant},
 p=P-1;q=P+1;delta=P^2-p q;ab=P^4;ba=-P^4;
 c4=P^4 delta;a2=c2-b2;
 alpha=141421358623/100000000000;
 z=alpha-72 I Sqrt[5717];
 cm=70710645403/100000000000-52087334 I/100000000000000;
 cp=70710672465/100000000000+52087353 I/100000000000000;
 k=31359519013336;
 proofs=<|
 "P_DEF"->TrueQ[FullSimplify[p==P-1&&q==P+1]],
 "PQ_DEF"->TrueQ[FullSimplify[p q==P^2-1]],
 "DELTA_ONE"->TrueQ[FullSimplify[delta==1]],
 "AB_PHASE"->TrueQ[FullSimplify[ab==P^4&&ba==-P^4]],
 "GAIN_CLOSURE"->TrueQ[FullSimplify[ab+ba==0&&ab-ba==2P^4]],
 "K_SUM"->TrueQ[FullSimplify[a2+b2==c2]],
 "GLOBAL_C4"->TrueQ[FullSimplify[c4/delta==P^4,delta!=0]],
 "RADICAL"->TrueQ[FullSimplify[Sqrt[-5717*5184]==72 I Sqrt[5717]]],
 "Z_GUARD"->TrueQ[FullSimplify[z!=0]],
 "C_GUARD"->TrueQ[Re[cm]!=1&&Re[cp]!=1],
 "RAIL_GUARD"->TrueQ[FreeQ[{3,-2},0]&&k!=0&&
    127475453492+31232043559844==k],
 "PI_GUARD"->TrueQ[Pi!=0]
 |>;
 static={"K_SUM","RADICAL","Z_GUARD","C_GUARD",
 "RAIL_GUARD","PI_GUARD","S0_DEFINITION","S1_DEFINITION"};
 abp={"P_DEF","PQ_DEF","DELTA_ONE","A_DEF","B_DEF",
 "AB_PHASE","BA_PHASE","GAIN_CLOSURE"};
 gates={"CUBIC_GUARD","INNER_0","INNER_1","OUTER_0","OUTER_1"};
 returns={"RETURN_0","RETURN_1"};
 all=Join[static,abp,gates,returns];
 initial=AssociationThread[all,ConstantArray["OPEN",Length[all]]];
 step[s_Association]:=AssociationMap[
 Function[key,Which[KeyExistsQ[proofs,key]&&TrueQ[proofs[key]],
 "TRUE_CLOSED",MemberQ[gates,key],"HNAN0",True,"OPEN"]],Keys[s]];
 first=step[initial];second=step[first];
 carrier=<|"value"->"payload","phase"->17,"curvature"->"kappa",
  "address"->"000","swap"->"xy/yx","branch"->"b",
  "residue"->"r","return"->"rho"|>;
 hnanReturn[c_Association]:=c;
 returnInvariant=(hnanReturn[carrier]===carrier&&
    hnanReturn[hnanReturn[carrier]]===carrier);
 Print[InputForm[<|"projectionChecks"->proofs,
  "checksPass"->And@@Values[proofs],
  "cellCounts"->Counts[Values[first]],
  "openCells"->Keys@Select[first,#==="OPEN"&],
  "routeFixedPoint"->(first===second),
  "HNANIdentityReturnFixture"->returnInvariant,
  "typedNativeProof"->False,"VM81Admission"->False|>]];
];
