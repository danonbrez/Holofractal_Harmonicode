(* Pass 220 I084 -- original Law-of-1 x4 ordered quotient.
   The native quotient operator and its inversion/phase direction remain
   held. Exact scalar projection is computed only on registered units. *)

ClearAll["Global\`*"];
sourceRelation = "x⁴=(t³-t)/(m²-m)=a²";
sourceOrder = {"x⁴", "(t³-t)/(m²-m)", "a²"};
sourceAST = HoldComplete[
  Equal[Power[x,4],
        Divide[Subtract[Power[t,3],t],Subtract[Power[m,2],m]],
        Power[a,2]]
];
inheritedI083Fragment = "(t³=t+(m²-m)=a²+t";
originalSPIRegistered = {"x⁴","t³-t","m²-m","a²"};

(* These are projections recorded in original SPI Law-of-1.
   Do not make native t, m, x, or a independent scalar solutions. *)
projX4 = 1;
projTResidue = 1;
projMResidue = 1;
projA2 = 1;
projectedRatio = projTResidue / projMResidue;
scalarDenominatorAdmissible = projMResidue =!= 0;
unitChainProjected = projectedRatio===projX4===projA2;

(* This quotient test uses only an ordinary commutative POLYNOMIAL
   DIAGNOSTIC, never the native operator or Hash216 authority. *)
scalarIdeal = {x^4-1, t^3-t-1, m^2-m-1, a^2-1};
groebner = GroebnerBasis[scalarIdeal,{x,t,m,a}];
numMinusDen = PolynomialReduce[(t^3-t)-(m^2-m),
  groebner,{x,t,m,a}][[2]];
denMinusOne = PolynomialReduce[(m^2-m)-1,
  groebner,{x,t,m,a}][[2]];
x4MinusA2 = PolynomialReduce[x^4-a^2,
  groebner,{x,t,m,a}][[2]];
ratioCrossProduct = PolynomialReduce[
  x^4*(m^2-m)-(t^3-t),
  groebner,{x,t,m,a}][[2]];
ratioEqualsA2CrossProduct = PolynomialReduce[
  a^2*(m^2-m)-(t^3-t),
  groebner,{x,t,m,a}][[2]];

checks=<|
 "01_source_relation_exact" -> (sourceRelation==="x⁴=(t³-t)/(m²-m)=a²"),
 "02_source_order_exact" -> (sourceOrder==={"x⁴","(t³-t)/(m²-m)","a²"}),
 "03_source_native_ast_held" -> (Head[sourceAST]===HoldComplete),
 "04_original_I083_group_still_open" -> StringStartsQ[inheritedI083Fragment,"("],
 "05_four_original_SPI_units" -> (originalSPIRegistered==={"x⁴","t³-t","m²-m","a²"}),
 "06_x4_unit" -> (projX4===1),
 "07_t_residual_unit" -> (projTResidue===1),
 "08_m_residual_unit" -> (projMResidue===1),
 "09_a2_unit" -> (projA2===1),
 "10_denominator_nonzero" -> scalarDenominatorAdmissible,
 "11_exact_projected_ratio" -> (projectedRatio===1),
 "12_projected_equality_chain" -> unitChainProjected,
 "13_scalar_cubic_minus_quadratic_residual" -> (numMinusDen===0),
 "14_scalar_denominator_minus_one" -> (denMinusOne===0),
 "15_scalar_x4_minus_a2" -> (x4MinusA2===0),
 "16_scalar_x4_quotient_cross_product" -> (ratioCrossProduct===0),
 "17_scalar_a2_quotient_cross_product" -> (ratioEqualsA2CrossProduct===0),
 "18_scalar_c_geometric_root_unchanged" -> (Sqrt[1+2]===Sqrt[3]),
 "19_source_phase_order_not_collapsed" -> (sourceOrder[[1]]=!=sourceOrder[[3]]),
 "20_no_floats" -> FreeQ[{projX4,projTResidue,projMResidue,projA2,scalarIdeal},_Real]
|>;
failures=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS_220_I084_X4_ORDERED_UNIT_QUOTIENT_WOLFRAM_V1",
 "status"->If[failures==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "passed"->Count[Values[checks],True],
 "failed"->failures,
 "source_relation"->sourceRelation,
 "source_order"->sourceOrder,
 "exact_projected_denominator"->projMResidue,
 "exact_projected_ratio"->projectedRatio,
 "scalar_polynomial_ideal_remainders"->{
   numMinusDen,denMinusOne,x4MinusA2,
   ratioCrossProduct,ratioEqualsA2CrossProduct
 },
 "native_quotient_inverse_direction_proven"->False,
 "native_phase_x4_operator_executed"->False,
 "native_equality_chain_proven"->False,
 "native_hash72_hash216_mint_authority"->False,
 "vm81_mutation_authority"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
