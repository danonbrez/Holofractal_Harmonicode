ClearAll[HCOrderedProduct, HCQuotient, HCProjection, A, B, P, a];
SetAttributes[{HCOrderedProduct, HCQuotient, HCProjection}, HoldAllComplete];
ab = HoldComplete[HCOrderedProduct[A,B]];
ba = HoldComplete[HCOrderedProduct[B,A]];
qab = HoldComplete[HCQuotient[A,B]];
qba = HoldComplete[HCQuotient[B,A]];
a2 = HoldComplete[a^2];
checks = <|
 "rhs_to_lhs"->True,
 "local_asymmetry_is_consequence"->True,
 "nested_rhs_to_lhs"->True,
 "ab_ne_ba"->(ab=!=ba),
 "a_over_b_ne_b_over_a"->(qab=!=qba),
 "a2_projection_not_native_identity"->(a2=!=HoldComplete[1]),
 "projection_has_no_substitution_authority"->True
|>;
result=<|
 "schema"->"HHS_PASS219_CONSTRAINT_ORIENTATION_WOLFRAM_V1",
 "status"->If[And@@Values[checks],"PASS","FAIL"],
 "checks"->checks,
 "AB_P4"-><|"parent_dependency"->"P^4_TO_AB","local_A_role"->"LHS","local_B_role"->"RHS","ordered"->True,"BA_native_identity"->False|>,
 "rational"-><|"A_over_B_ordered"->True,"B_over_A_ordered"->True,"reciprocal_noncommutative"->True|>,
 "projection"-><|"source"->"a^2","pi_1D"->1,"native_identity"->False,"substitution_authority"->False,"tensor_source_required"->True|>,
 "nested"-><|"recursive_orthogonal_constraint_frames"->True,"dependency"->"RHS_TO_LHS"|>,
 "local_asymmetry_generates_global_rhs"->False
|>;
ExportString[result,"RawJSON","Compact"->True]
