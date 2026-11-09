(* Read-only formal extension. The Sudoku instance below is a valid
   permutation witness, not a replacement of canonical VM81 data.
   HNAN center, native phase products, receipt admission and 18-peer
   semantics remain inherited and are not evaluated as host scalars. *)
Module[{loshu,sudoku,rows,columns,boxes,pairs,center=41,control,records,immutable,addresses,checks,report},
 loshu={{4,9,2},{3,5,7},{8,1,6}};
 sudoku=Table[Mod[3 Mod[r-1,3]+Quotient[r-1,3]+c-1,9]+1,
   {r,1,9},{c,1,9}];
 rows=sudoku; columns=Transpose[sudoku];
 boxes=Flatten[Table[
   Flatten[sudoku[[3 br+1;;3 br+3,3 bc+1;;3 bc+3]]],
   {br,0,2},{bc,0,2}],1];
 pairs=Table[{k,82-k},{k,1,40}];
 control=Table[Boole[j<=i],{i,1,4},{j,1,4}];
 records=FoldList[Append,{}, {"phase1","phase2","phase3"}];
 immutable=ConstantArray[loshu,Length[records]];
 addresses=Table[{Quotient[k,81],Mod[k,81]},{k,0,81^2-1}];
 checks={
  VerificationTest[And@@(Sort[#]===Range[9]&/@Join[rows,columns,boxes]),True,
    TestID->"sudoku-27-permutations"],
  VerificationTest[And@@(Total[#]===45&/@Join[rows,columns,boxes]),True,
    TestID->"sudoku-27-sums"],
  VerificationTest[And@@(Times@@#===362880&/@Join[rows,columns,boxes]),True,
    TestID->"sudoku-27-products"],
  VerificationTest[Length[Union[Flatten[pairs]]],80,
    TestID->"40-disjoint-antipodal-address-pairs"],
  VerificationTest[Sort[Append[Flatten[pairs],center]],Range[81],
    TestID->"pair-plus-center-complete"],
  VerificationTest[And@@(Total[#]===82&/@pairs),True,
    TestID->"pair-address-complements"],
  VerificationTest[loshu[[2,2]],5,TestID->"loshu-center"],
  VerificationTest[And@@(Total[#]===15&/@Join[loshu,Transpose[loshu]]),
    True,TestID->"loshu-row-column"],
  VerificationTest[81*64,72^2,TestID->"hash72-vm81-coordinate-identity"],
  VerificationTest[And@@Flatten[Table[
    Mod[j+Mod[i-j,72],72]===i,{i,0,71},{j,0,71}]],
    True,TestID->"all-72-cross-phase-inverses"],
  VerificationTest[And@@(Reverse[Reverse[#]]===#&/@rows),True,
    TestID->"row-double-reverse"],
  VerificationTest[And@@(Mod[#[[1]],9]===Mod[#[[2]],9]&/@pairs),False,
    TestID->"no-unsupported-antipodal-symbol-equality"],
  VerificationTest[control[[1,2;;4]],{0,0,0},TestID->"no-descendant-control-of-nucleus"],
  VerificationTest[control[[4,1;;4]],{1,1,1,1},TestID->"descendant-inherits-prior-rules"],
  VerificationTest[AllTrue[immutable,#===immutable[[1]]&],True,TestID->"immutable-generator-while-parameters-accumulate"],
  VerificationTest[Length[records]==4&&Length[Last[records]]==3,True,TestID->"cumulative-parameter-history"],
  VerificationTest[Length[addresses],6561,TestID->"81x81-fractal-address-count"],
  VerificationTest[Length[DeleteDuplicates[addresses]],6561,TestID->"81x81-unique-addresses"],
  VerificationTest[MinMax[Flatten[addresses]],{0,80},TestID->"81x81-coordinate-range"]
 };
 report=TestReport[checks];
 <|"Schema"->"HHS_PASS220_NUCLEUS_81_RECIPROCAL_PHASE_INHERITANCE_WOLFRAM_V1",
   "TestsSucceeded"->report["TestsSucceededCount"],
   "TestsFailed"->report["TestsFailedCount"],
   "AllTestsSucceeded"->report["AllTestsSucceeded"],
   "CanonicalVM81MutationAuthority"->False,
   "CanonicalHash72MintAuthority"->False,
   "FullHNANExpressionProven"->False,
   "EighteenPeerRelationProven"->False|>
]
