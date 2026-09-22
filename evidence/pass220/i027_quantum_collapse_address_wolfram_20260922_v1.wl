(* Pass 220 I027 exact outcome -> Lo Shu -> VM81 address proof. *)
ClearAll[k,n,row,col,cell,lo,zero,sign];

lo={{4,9,2},{3,5,7},{8,1,6}};
zero={{-1,4,-3},{-2,0,2},{3,-4,1}};

addr = Table[
 row=Quotient[k,3]+1;
 col=Mod[k,3]+1;
 <|
  "k"->k,
  "row"->row-1,
  "col"->col-1,
  "lo"->lo[[row,col]],
  "zero"->zero[[row,col]],
  "sign"->Sign[zero[[row,col]]]
 |>,
 {k,0,8}
];

cells=Flatten@Table[9 n+k,{n,0,8},{k,0,8}];

checks=<|
 "01_outcomes_nine" -> (Length[addr]===9),
 "02_row_major_cover" ->
   (Sort[({#row,#col}& /@ addr)]===
    Sort[Flatten[Table[{r,c},{r,0,2},{c,0,2}],1]]),
 "03_lo_shu_flat_exact" ->
   ((#lo& /@ addr)==={4,9,2,3,5,7,8,1,6}),
 "04_zero_centered_flat_exact" ->
   ((#zero& /@ addr)==={-1,4,-3,-2,0,2,3,-4,1}),
 "05_trinary_sign_range" ->
   (Union[#sign& /@ addr]==={-1,0,1}),
 "06_center_outcome_zero_sign" ->
   (addr[[5,"k"]]===4 && addr[[5,"lo"]]===5 &&
    addr[[5,"sign"]]===0),
 "07_vm81_bijection" ->
   (Sort[cells]===Range[0,80] && DuplicateFreeQ[cells]),
 "08_vm81_formula_bounds" ->
   And@@Flatten@Table[0<=9n+k<=80,{n,0,8},{k,0,8}]
|>;

failed=Keys@Select[checks,#=!=True&];
result=<|
 "schema"->
  "HHS_PASS_220_I027_QUANTUM_COLLAPSE_ADDRESS_WOLFRAM_20260922_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "pass_count"->Count[Values[checks],True],
 "failed"->failed,
 "lo_shu_flat"->{4,9,2,3,5,7,8,1,6},
 "zero_centered_flat"->{-1,4,-3,-2,0,2,3,-4,1},
 "vm81_min"->Min[cells],
 "vm81_max"->Max[cells],
 "checks"->checks
|>;

ExportString[result,"RawJSON"]
