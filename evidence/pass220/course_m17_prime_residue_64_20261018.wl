(* Pass220 M17 exact arithmetic projection; NOT canonical Hash216 mint. *)
primes={2,3,5,7,11,13,17,19};
ring={8,1,6,7,2,9,4,3}; hub=5;
spins={-4,-3,-2,-1,1,2,3,4};
classes=<|"+1"->{17},"+3"->{3,11,19},"-3"->{5,13},"-1"->{7},"even"->{2}|>;
checks=<|
 "primeCensus"->(Select[Range[19],PrimeQ]===primes),
 "residueOrder"->(Mod[primes,8]==={2,3,5,7,3,5,1,3}),
 "classCensus"->(And@@(And@@(MemberQ[primes,#]& /@ #2)& @@@ Normal[classes]) && Sort[Flatten[Values[classes]]]===primes),
 "ringEight"->(Length[ring]==8 && FreeQ[ring,hub] && Sort[Append[ring,hub]]===Range[9]),
 "hubPrime"->PrimeQ[hub],
 "spinsNoZero"->(Length[spins]==8 && FreeQ[spins,0]),
 "64Cells"->(8*4*2==64 && 8*8==64),
 "uniqueIndices"->(Length[DeleteDuplicates[Flatten[Table[8*i+j,{i,0,7},{j,0,7}]]]]==64)
|>;
receipt=<|"schema"->"HHS_PASS220_M17_PRIME_RESIDUE_CANDIDATE_V1","checks"->checks,
 "status"->If[And@@Values[checks],"PASS","FAIL"],"hash216Mint"->False,
 "nativeGateAdmission"->False|>;
Print[ExportString[receipt,"RawJSON","Compact"->True]];
If[receipt["status"]=!="PASS",Exit[1]];
