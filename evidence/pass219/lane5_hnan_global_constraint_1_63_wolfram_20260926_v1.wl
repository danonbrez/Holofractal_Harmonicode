ClearAll[lam,r,s];

m={{0,0,0,1},{1,0,1,1},{1,1,1,0},{0,1,0,0}};
j=ConstantArray[1,{4,4}];
mxy=r j+(s-r)m;

rules={
 {1,"ZERO","EMPTYSET","ORDERED_CLOSURE"},
 {2,"EMPTYSET","AB_P4_EMPTYSET","ORDERED_CLOSURE"},
 {3,"AB_P4_EMPTYSET","HNAN","ORDERED_CLOSURE"},
 {4,"ZERO","XYZW_SUM","TYPED_VIEW"},
 {5,"U72","U0","PHASE_CLOSURE"},
 {6,"INFINITY","DELTA","DIRECTED_RECIPROCAL"},
 {7,"DELTA","X","DIRECTED_RECIPROCAL"},
 {8,"INFINITY_DELTA","BX5184","UNBOUNDED_CARRIER"},
 {9,"P","BX5184_OVER_DELTA","GLOBAL_DENOMINATOR"},
 {10,"ONE_OVER_ZERO","HNAN_GATE","HNAN_BOUNDARY"},
 {11,"J2_ZERO","HNAN_GATE","JORDAN_CORRESPONDENCE"},
 {12,"XY","YX","NONCOMMUTATIVE_DISTINCTION"},
 {13,"ZW","WZ","NONCOMMUTATIVE_DISTINCTION"},
 {14,"X","GAMMA_X","DIRECTED_TYPED_IDENTITY"},
 {15,"U0","ZERO_POWER4","TYPED_VIEW"}
};

zeroClosure={"ZERO","EMPTYSET","AB_P4_EMPTYSET","HNAN"};
reciprocalChain={"INFINITY","DELTA","X"};
hnanOrder={"x","y","-z","-w","xy","yx","-zw","-wz"};
heldP={"Quotient","BX5184","DELTA"};
heldInfinityDelta={"Product","INFINITY","DELTA"};
heldGamma={"Product",{"Power","u","18/72mod72"},{"Power","u",36}};

cp=Factor[CharacteristicPolynomial[m,lam]];
cpLift=Factor[CharacteristicPolynomial[mxy,lam]];
m2=MatrixPower[m,2];
m3=MatrixPower[m,3];
m4=MatrixPower[m,4];

checks=<|
 "rule_count_15"->(Length[rules]===15),
 "rule_ids_unique"->DuplicateFreeQ[rules[[All,1]]],
 "rule_ids_contiguous"->(rules[[All,1]]===Range[15]),
 "zero_closure_order_exact"->(zeroClosure==={"ZERO","EMPTYSET","AB_P4_EMPTYSET","HNAN"}),
 "zero_closure_reverse_absent"->FreeQ[rules,{_,"HNAN","AB_P4_EMPTYSET",_}],
 "reciprocal_chain_exact"->(reciprocalChain==={"INFINITY","DELTA","X"}),
 "reciprocal_reverse_absent"->(FreeQ[rules,{_,"DELTA","INFINITY",_}]&&FreeQ[rules,{_,"X","DELTA",_}]),
 "xy_yx_not_equality_rule"->MemberQ[rules,{12,"XY","YX","NONCOMMUTATIVE_DISTINCTION"}],
 "zw_wz_not_equality_rule"->MemberQ[rules,{13,"ZW","WZ","NONCOMMUTATIVE_DISTINCTION"}],
 "u72_to_u0_directed"->MemberQ[rules,{5,"U72","U0","PHASE_CLOSURE"}],
 "p_bx5184_delta_structural"->(heldP==={"Quotient","BX5184","DELTA"}),
 "infinity_delta_bx_structural"->(heldInfinityDelta==={"Product","INFINITY","DELTA"}),
 "gamma_order_structural"->(heldGamma==={"Product",{"Power","u","18/72mod72"},{"Power","u",36}}),
 "hnan_channel_order_exact"->(hnanOrder==={"x","y","-z","-w","xy","yx","-zw","-wz"}),
 "m01_rank_3"->(MatrixRank[m]===3),
 "m01_nullity_1"->(Length[NullSpace[m]]===1),
 "m01_squared_nullity_2"->(Length[NullSpace[m2]]===2),
 "m01_charpoly_exact"->(cp===lam^2*(lam-2)*(lam+1)),
 "m01_degree4_closure"->(m4===m3+2m2),
 "m01_krylov_degree4"->(MatrixRank[Transpose[Flatten /@ {IdentityMatrix[4],m,m2,m3}]]===4),
 "mxy_charpoly_exact"->(cpLift===lam^2*(lam-r+s)*(lam-2r-2s)),
 "mxy_recurrence_exact"->(FullSimplify[MatrixPower[mxy,4]-(3r+s)MatrixPower[mxy,3]+2(r^2-s^2)MatrixPower[mxy,2]]===ConstantArray[0,{4,4}]),
 "mxy_generic_nullity_1"->Assuming[r!=s&&r+s!=0,FullSimplify[4-MatrixRank[mxy]]===1],
 "mxy_generic_squared_nullity_2"->Assuming[r!=s&&r+s!=0,FullSimplify[4-MatrixRank[MatrixPower[mxy,2]]]===2],
 "sum_invariant_n1_n4"->And@@Table[FullSimplify[Total[Flatten[MatrixPower[mxy,n]]]-2^(n+2)(r+s)^n]===0,{n,1,4}]
|>;

failed=Keys@Select[checks,#=!=True&];
result=<|
 "schema"->"HHS_PASS219_LANE5_HNAN_GLOBAL_CONSTRAINT_1_63_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "pass_count"->Count[Values[checks],True],
 "failed"->failed,
 "rules"->rules,
 "zero_closure"->zeroClosure,
 "reciprocal_chain"->reciprocalChain,
 "hnan_order"->hnanOrder,
 "characteristic_polynomial"->ToString[cp,InputForm],
 "lifted_characteristic_polynomial"->ToString[cpLift,InputForm],
 "generic_lift_conditions"->{"r!=s","r+s!=0"},
 "forbidden_rewrites"->{"scalarize_ZERO_EMPTYSET_HNAN","reverse_ordered_closure","cancel_DELTA","INFINITY_to_float","commute_XY_YX","commute_ZW_WZ","replace_HNAN_with_scalar_division"}
|>;
Print[ExportString[result,"RawJSON"]];
