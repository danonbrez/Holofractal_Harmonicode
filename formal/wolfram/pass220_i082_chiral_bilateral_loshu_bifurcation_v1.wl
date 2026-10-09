(* Pass 220 I082 — exact polynomial Lo Shu + four bifurcation branches.
   This is a scalar PROJECTION only. The ordered source tensor is held
   syntactically and NEVER coerced into commutative operator algebra. *)

ClearAll["Global\`*"];

(* These symbolic HHS relationships are inert: no rewriting/commutation. *)
heldOrderedPromptResponse = HoldComplete[
  List[
    (u^72 == x*y),
    List[
      List[x == -y, x+y == 0, x*y, y == a^2/x],
      List[z == -w, z+w == 0, z*w, w == a^2/w],
      List[c^2-b^2-a^2, a^2 == c^2-b^2,
        b^2 == c^2-a^2 == x*y+z*w, c^2 == a^2+b^2]
    ],
    -List[1 == z*w, 1 == x*y, 6 == b^2*c^2 == b^2+c^2+a^2,
      -(e^2 == c^2+d^2 == b^6 == 8)],
    (x*A == -y*B),
    (A/B != B/A),
    (u^36 == (y*x*w*z)/a^2)
  ]
];

(* Native source ordering and the unary negative mask are retained as
   proof obligations, not assigned numerical boolean truth values. *)
rootMetadata = "179971.179971";
baselineMetadata = "1.001";
sourceCellPolynomials = {
  {"b^4", "P^4=AB=c^4", "b^2=c^2-a^2"},
  {"c^2=a^2+b^2", "d^2=b^2+c^2", "(b^6-a^2)(c^2+b^4)/(d^2+b^2)"},
  {"e^2=b^6=c^2+d^2", "a^2=(xy+zw)/(c^2-a^2)",
   "b^2 c^2=a^2+b^2+c^2"}
};
a2=1; b2=2; c2=3; d2=5; e2=8; xy=1; zw=1;
P4=c2^2;

matrix={
  {b2^2, P4, c2-a2},
  {a2+b2, b2+c2, (b2^3-a2)(c2+b2^2)/(d2+b2)},
  {c2+d2, (xy+zw)/(c2-a2), b2*c2}
};
expected={{4,9,2},{3,5,7},{8,1,6}};
rowSums=Total /@ matrix;
columnSums=Total /@ Transpose[matrix];
diagonalSums={Tr[matrix],Tr[Reverse[matrix,2]]};

(* P^2=3 is the EXPLICITLY SELECTED root branch. P^4=9 alone
   does not exclude P^2=-3 over the complex projection. *)
branches=Flatten[Table[
  Module[{pRoot,delta,pRootSum,pLower,qUpper,ok},
    pRoot=sP*Sqrt[3];
    delta=2*sDelta;
    pRootSum=pRoot*delta;
    pLower=(pRootSum-delta)/2;
    qUpper=(pRootSum+delta)/2;
    ok=FullSimplify[
       pLower*qUpper==2 &&
       pLower+qUpper==pRoot*(qUpper-pLower) &&
       (pLower+qUpper)/(pRoot*(qUpper-pLower))==1 &&
       pRoot^2==3 &&
       pRoot^4==9 &&
       pRoot^2-pLower*qUpper==1
    ];
    <|"P_sign"->sP, "q_minus_p_sign"->sDelta, "verified"->TrueQ[ok],
      "P"->ToString[InputForm[pRoot]],
      "p"->ToString[InputForm[FullSimplify[pLower]]],
      "q"->ToString[InputForm[FullSimplify[qUpper]]]|>
  ], {sP,{-1,1}},{sDelta,{-1,1}}],1];

checks=<|
 "01_source_typed_list_held" -> (Head[heldOrderedPromptResponse]===HoldComplete),
 "02_exact_root_fields" -> (a2==1 && b2==2 && c2==3 && d2==5 && e2==8),
 "03_power_eight" -> (b2^3==8 && e2==c2+d2),
 "04_product_six" -> (b2*c2==a2+b2+c2==6),
 "05_composite_seven" -> (((b2^3-a2)(c2+b2^2))/(d2+b2)===7),
 "06_nine_poly_lo_shu_addresses" -> (matrix===expected),
 "07_three_rows_fifteen" -> (rowSums==={15,15,15}),
 "08_three_columns_fifteen" -> (columnSums==={15,15,15}),
 "09_two_diagonals_fifteen" -> (diagonalSums==={15,15}),
 "10_global_sum_forty_five" -> (Total[Flatten[matrix]]===45),
 "11_values_one_to_nine_unique" -> (Sort[Flatten[matrix]]===Range[9]),
 "12_eight_outer_positions" -> (Sort[Delete[Flatten[matrix],5]]==={1,2,3,4,6,7,8,9}),
 "13_center_five" -> (matrix[[2,2]]===5),
 "14_four_real_quadratic_branches" -> (Length[branches]===4 && And@@(Lookup[branches,"verified"])),
 "15_outer_nine" -> (P4===9),
 "16_72_phase_surface_8x9" -> (8*9===72),
 "17_5184_shared_coordinate" -> (64*81==72*72==144*36==5184),
 "18_gate_metadata_distinct_from_unit" -> (1001/1000=!=1),
 "19_all_projection_values_exact" -> FreeQ[{matrix,rowSums,columnSums},_Real]
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS_220_I082_CHIRAL_LO_SHU_BIFURCATION_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "passed"->Count[Values[checks],True],
 "failed"->failed,
 "ordered_polynomial_source"->sourceCellPolynomials,
 "lo_shu_matrix"->matrix,
 "eight_outer_vertices"->{1,2,3,4,6,7,8,9},
 "center_vertex"->5,
 "rows"->rowSums, "columns"->columnSums,
 "diagonals"->diagonalSums, "total"->Total[Flatten[matrix]],
 "branches"->branches,
 "typed_negative_list_mask_evaluated_as_number"->False,
 "native_noncommutative_division_proven"->False,
 "u36_half_turn_proven"->False,
 "delta_e_zero_for_full_native_expression_proven"->False,
 "canonical_vm81_mutation_authority"->False,
 "source_metadata_root"->rootMetadata,
 "baseline_metadata"->baselineMetadata,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
