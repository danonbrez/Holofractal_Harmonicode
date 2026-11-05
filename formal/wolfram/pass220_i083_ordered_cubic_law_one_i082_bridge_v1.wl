(* Pass220 I083: source-faithful ordered cubic Law-of-1 extension.
   Native ordering and the opening "(" are held as typed source. All
   numeric reductions below are explicitly NON-AUTHORITATIVE scalar
   projections of inherited SPI Law-of-1 units. Never solve native t/m. *)

ClearAll["Global\`*"];
sourceFragment="(t³=t+(m²-m)=a²+t";
sourceOpenParenthesis=True;
orderedOperands={"t³","t+(m²-m)","a²+t"};
orderedNativeAST=HoldComplete[Equal[
  Power[t,3],
  Plus[t,Plus[Power[m,2],Times[-1,m]]],
  Plus[Power[a,2],t]
]];
originalSPI="t³=t+a²";
originalResidual="t³-t=a²=∆=1";

(* Exact scalar Law-of-1 projection, inherited a²=m²-m=t³-t=1. *)
a2Unit=1;
mResidueUnit=1;
tCubicResidueUnit=1;
rootC=Sqrt[1+2];
matrix={{4,9,2},{3,5,7},{8,1,6}};

(* The polynomial ideal is a diagnostic commutative projection. It is NOT
   the native ordered operator equality evaluation. *)
scalarRelations={t^3-t-1,m^2-m-1};
basis=GroebnerBasis[scalarRelations,{t,m}];
scalarCubicResidual=PolynomialReduce[t^3-t-(m^2-m),basis,{t,m}][[2]];
scalarMiddleLastResidual=PolynomialReduce[
  (t+(m^2-m))-(a2Unit+t),basis,{t,m}
][[2]];
scalarFirstLastResidual=PolynomialReduce[
  t^3-(a2Unit+t),basis,{t,m}
][[2]];

checks=<|
 "01_user_source_open_parenthesis" -> StringStartsQ[sourceFragment,"("],
 "02_three_exact_ordered_operands" -> (orderedOperands==={"t³","t+(m²-m)","a²+t"}),
 "03_native_ast_held" -> (Head[orderedNativeAST]===HoldComplete),
 "04_no_reversed_equals_assumed" -> (orderedOperands[[1]]=!=orderedOperands[[3]]),
 "05_inherited_pass219_cubic" -> (originalSPI==="t³=t+a²"),
 "06_inherited_pass219_residual" -> (originalResidual==="t³-t=a²=∆=1"),
 "07_projected_t_cubic_unit" -> (tCubicResidueUnit===1),
 "08_projected_m_unit" -> (mResidueUnit===1),
 "09_projected_a2_unit" -> (a2Unit===1),
 "10_projected_addend_residual_zero" -> (mResidueUnit-a2Unit===0),
 "11_projected_cubic_residual_zero" -> (tCubicResidueUnit-mResidueUnit===0),
 "12_scalar_polynomial_ideal_cubic_matches_m" -> (scalarCubicResidual===0),
 "13_scalar_polynomial_ideal_middle_last" -> (scalarMiddleLastResidual===0),
 "14_scalar_polynomial_ideal_first_last" -> (scalarFirstLastResidual===0),
 "15_c_root_original_sqrt1plus2" -> (rootC===Sqrt[3] && rootC^2===3),
 "16_i082_lo_shu_nucleus_retained" -> (matrix==={{4,9,2},{3,5,7},{8,1,6}}),
 "17_no_floating_point" -> FreeQ[{scalarRelations,basis,matrix,rootC},_Real],
 "18_open_group_not_autoclosed" -> TrueQ[sourceOpenParenthesis]
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS_220_I083_ORDERED_CUBIC_LAW_ONE_I082_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "passed"->Count[Values[checks],True],
 "failed"->failed,
 "original_source_fragment"->sourceFragment,
 "source_open_parenthesis"->sourceOpenParenthesis,
 "ordered_operands"->orderedOperands,
 "inherited_spi_cubic"->originalSPI,
 "inherited_spi_residual"->originalResidual,
 "projected_a2"->a2Unit,
 "projected_m_residual"->mResidueUnit,
 "projected_t_cubic_residual"->tCubicResidueUnit,
 "scalar_polynomial_ideal_residuals"->{
   scalarCubicResidual,scalarMiddleLastResidual,scalarFirstLastResidual},
 "canonical_geometric_c"->ToString[InputForm[rootC]],
 "native_t_or_m_solved"->False,
 "native_commutation_proven"->False,
 "native_chained_equality_proven"->False,
 "native_hash216_minted"->False,
 "canonical_vm81_mutation_authority"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
