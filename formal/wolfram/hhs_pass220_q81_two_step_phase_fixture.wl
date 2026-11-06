(* Pass220 Q81: exact Wolfram fixture for Module131 23-cell two-step closure.
   This verifies scheduling and phase-code inversion only. Source-bound fixture
   certificates are NOT canonical VM81 or independent mathematical proof. *)
Module[{names,static,abp,gates,returns,cells,certs,routes,step,
 first,second,b,o,pairs,dec,bit,dir,round},
 static={"K_SUM","RADICAL","Z_GUARD","C_GUARD","RAIL_GUARD",
 "PI_GUARD","S0_DEFINITION","S1_DEFINITION"};
 abp={"P_DEF","PQ_DEF","DELTA_ONE","A_DEF","B_DEF","AB_PHASE",
 "BA_PHASE","GAIN_CLOSURE"};
 gates={"CUBIC_GUARD","INNER_0","INNER_1","OUTER_0","OUTER_1"};
 returns={"RETURN_0","RETURN_1"};
 names=Join[static,abp,gates,returns];
 cells=AssociationThread[names,ConstantArray["OPEN",23]];
 certs=AssociationThread[Join[static,abp,returns],
   ConstantArray["SOURCE_BOUND_FIXTURE",18]];
 routes=AssociationThread[gates,ConstantArray["HNAN0",5]];
 step[s_]:=AssociationMap[
   If[KeyExistsQ[certs,#],"TRUE_CLOSED",
     If[KeyExistsQ[routes,#],"HNAN0","OPEN"]]&,Keys[s]];
 first=step[cells];second=step[first];
 pairs={{{0,1},{1,0}},{{-1,1},{1,-1}}};
 dec[x_,y_]:=pairs[[x+1,y+1]];
 bit[p_]:=If[p==={0,1}||p==={1,0},0,1];
 dir[p_]:=If[p==={0,1}||p==={-1,1},0,1];
 b=Partition[Table[Mod[i,2],{i,0,80}],9];
 o=Partition[Table[Mod[Quotient[i,3],2],{i,0,80}],9];
 round=MapThread[dec,{Map[bit,MapThread[dec,{b,o},2],{2}],
   Map[dir,MapThread[dec,{b,o},2],{2}]},2]===
   MapThread[dec,{b,o},2];
 Print[InputForm[<|"cells"->Length[names],
   "counts"->Counts[Values[first]],
   "fixedPoint"->(first===second),
   "phaseRoundtrip"->round,
   "fixtureIsNotNativeCertification"->True|>]];
];
