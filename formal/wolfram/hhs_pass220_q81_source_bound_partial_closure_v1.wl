(* Q81 Module 131-133 source-bound exact witness candidate; no VM81/Hash72 mutation.
   Verifies seven exact algebraic projections; no forged 18-of-18 certificate.
   All native ordered operands remain distinct typed witnesses. *)
Module[{P,p,q,delta,a2,b2,c2,c4,ab,ba,proofs,static,abp,gates,returns,
 cells,certificateNames,resolve,first,second,phasePairs,decode,bit,orient,
 binary,orientation,native,roundtrip},
 p=P-1;q=P+1;delta=P^2-p q;
 ab=P^4;ba=-P^4;c4=P^4 delta;a2=c2-b2;
 proofs=<|
 "P_DEF"->TrueQ[FullSimplify[p==P-1&&q==P+1]],
 "PQ_DEF"->TrueQ[FullSimplify[p q==P^2-1]],
 "DELTA_ONE"->TrueQ[FullSimplify[delta==1]],
 "AB_PHASE"->TrueQ[FullSimplify[ab==P^4&&ba==-P^4]],
 "GAIN_CLOSURE"->TrueQ[FullSimplify[ab+ba==0&&ab-ba==2 P^4]],
 "K_SUM"->TrueQ[FullSimplify[a2+b2==c2]],
 "GLOBAL_C4"->TrueQ[FullSimplify[c4/delta==P^4,delta!=0]]
 |>;
 static={"K_SUM","RADICAL","Z_GUARD","C_GUARD","RAIL_GUARD",
 "PI_GUARD","S0_DEFINITION","S1_DEFINITION"};
 abp={"P_DEF","PQ_DEF","DELTA_ONE","A_DEF","B_DEF","AB_PHASE",
 "BA_PHASE","GAIN_CLOSURE"};
 gates={"CUBIC_GUARD","INNER_0","INNER_1","OUTER_0","OUTER_1"};
 returns={"RETURN_0","RETURN_1"};
 certificateNames=Join[static,abp,returns];
 cells=AssociationThread[Join[static,abp,gates,returns],
 ConstantArray["OPEN",23]];
 resolve[s_Association]:=AssociationMap[
  Function[key,Which[
    KeyExistsQ[proofs,key]&&TrueQ[proofs[key]],"TRUE_CLOSED",
    MemberQ[gates,key],"HNAN0",True,"OPEN"]],Keys[s]];
 first=resolve[cells];second=resolve[first];
 phasePairs={{{0,1},{1,0}},{{-1,1},{1,-1}}};
 decode[x_,y_]:=phasePairs[[x+1,y+1]];
 bit[v_]:=Which[v==={0,1}||v==={1,0},0,
                     v==={-1,1}||v==={1,-1},1,True,Missing["Invalid"]];
 orient[v_]:=Which[v==={0,1}||v==={-1,1},0,
                     v==={1,0}||v==={1,-1},1,True,Missing["Invalid"]];
 binary=Partition[Table[Mod[i,2],{i,0,80}],9];
 orientation=Partition[Table[Mod[Quotient[i,3],2],{i,0,80}],9];
 native=MapThread[decode,{binary,orientation},2];
 roundtrip=(Map[bit,native,{2}]===binary&&
    Map[orient,native,{2}]===orientation&&
    MapThread[decode,{Map[bit,native,{2}],Map[orient,native,{2}]},2]===native);
 Print[InputForm[<|"exactChecks"->proofs,"exactChecksPass"->And@@Values[proofs],
 "module131States"->Counts[Values[first]],
 "unprovedNames"->Keys@Select[first,#==="OPEN"&],
 "fixedPoint"->(first===second),
 "phase81Roundtrip"->roundtrip,
 "candidateOnly"->True,
 "nativeGateExecutionClaimed"->False|>]];
];
