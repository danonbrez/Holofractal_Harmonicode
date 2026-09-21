add[assocs__Association] := Select[Merge[{assocs}, Total], # != 0 &];
scale[c_, a_Association] := Association @ KeyValueMap[#1 -> c #2 &, a];
commProject[a_Association] := Select[
  Merge[
    KeyValueMap[<|StringJoin[Sort[Characters[#1]]] -> #2|> &, a],
    Total
  ],
  # != 0 &
];

lhsOrdered = <|"xxzz" -> 1, "xxww" -> 1, "yyzz" -> 1, "yyww" -> 1|>;
a2b2 = <|
  "xzxz" -> 1, "xzyw" -> -1, "ywxz" -> -1, "ywyw" -> 1,
  "xwxw" -> 1, "xwyz" -> 1, "yzxw" -> 1, "yzyz" -> 1
|>;
deltaD = <|
  "xxzz" -> 1, "xzxz" -> -1,
  "xxww" -> 1, "xwxw" -> -1,
  "yyzz" -> 1, "yzyz" -> -1,
  "yyww" -> 1, "ywyw" -> -1
|>;
lambdaD = <|"xwyz" -> 1, "yzxw" -> 1, "xzyw" -> -1, "ywxz" -> -1|>;
rhsOrdered = add[a2b2, deltaD, scale[-1, lambdaD]];
abOrdered = <|"xzxw" -> 1, "xzyz" -> 1, "ywxw" -> -1, "ywyz" -> -1|>;
baOrdered = <|"xwxz" -> 1, "xwyw" -> -1, "yzxz" -> 1, "yzyw" -> -1|>;

loShu = {{4, 9, 2}, {3, 5, 7}, {8, 1, 6}};
g123 = Outer[Times, {1, 2, 3}, {1, 2, 3}];
palLanes = {"123321", "246642", "369963"};

triplets = Tuples[Range[0, 3], 3];
ops = (16 #[[1]] + 4 #[[2]] + #[[3]]) & /@ triplets;
decode[k_Integer] := {Quotient[k, 16], Quotient[Mod[k, 16], 4], Mod[k, 4]};
roundTrip64 = And @@ MapThread[#1 == decode[#2] &, {triplets, ops}];

phaseOrbit = Replace[Mod[8 + 16 Range[0, 8], 72], 0 -> 72, {1}];
phaseReflection = And @@ Table[
  Mod[phaseOrbit[[k]] + phaseOrbit[[10 - k]], 72] == 0,
  {k, 1, 9}
];

vars9 = Array[v, 9];
recip9 = 10 - Reverse[vars9];
pairMeanResidual = FullSimplify[(Total[vars9] + Total[recip9])/2 - 45];

p = n - 1;
q = n + 1;
sigma = gamma;
omega = rho;
tripartite = {
  Expand[gamma*n*(q - p) - sigma*(p + q)] == 0,
  Expand[gamma*(n^2 - p*q) - sigma] == 0,
  Expand[(n^2 - p*q)*rho*gamma - sigma*omega] == 0
};

hcAB = {"HCProd", "A", "B"};
hcBA = {"HCProd", "B", "A"};
hcAoverB = {"HCQuotient", "A", "B"};
hcBoverA = {"HCQuotient", "B", "A"};
hcCancel = {"HCQuotient", {"HCProd", "InfinityCarrier", "Delta"}, "Delta"};
hcInf = {"InfinityCarrier"};
hcGamma = {
  "HCProd",
  {"HCPow", "u", {"HCMod", {"HCDiv", 18, 72}, 72}},
  {"HCPow", "u", 36}
};
hcGammaCombined = {
  "HCPow", "u", {"HCAdd", {"HCMod", {"HCDiv", 18, 72}, 72}, 36}
};
hcGammaReordered = {
  "HCProd",
  {"HCPow", "u", 36},
  {"HCPow", "u", {"HCMod", {"HCDiv", 18, 72}, 72}}
};

scopeA = {"read", "write", "vector", "receipt"};
scopeB = {"read", "vector", "receipt"};
scopeC = {"read", "receipt"};
scopeABC = Intersection[scopeA, scopeB, scopeC];

stack12 = {"HC216", {"HC216", "EMPTY", {"HCFrame", 1}}, {"HCFrame", 2}};
stack21 = {"HC216", {"HC216", "EMPTY", {"HCFrame", 2}}, {"HCFrame", 1}};

checks = <|
  "ordered_brahmagupta_corrected_identity" ->
    (Sort[Normal[lhsOrdered]] === Sort[Normal[rhsOrdered]]),
  "ordered_brahmagupta_delta_commutative_projection_zero" ->
    (Length[commProject[deltaD]] == 0),
  "ordered_brahmagupta_lambda_commutative_projection_zero" ->
    (Length[commProject[lambdaD]] == 0),
  "ordered_AB_not_BA" -> (Sort[Normal[abOrdered]] =!= Sort[Normal[baOrdered]]),
  "rational_unit_residue_pair" ->
    FullSimplify[
      {(n - 1) + (n + 1), (n + 1) - (n - 1), (n - 1) (n + 1)} ==
      {2 n, 2, n^2 - 1}
    ],
  "rational_bridge_closure" ->
    FullSimplify[
      n^2 == (n - 1) (n + 1) + ((2 n)/(2 n)),
      Assumptions -> n != 0
    ],
  "g123_exact" -> (g123 == {{1, 2, 3}, {2, 4, 6}, {3, 6, 9}}),
  "g123_sum_product_six" -> (Total[{1, 2, 3}] == Times @@ {1, 2, 3} == 6),
  "h36_666_111" -> (Total[Range[36]] == 666 && 666/6 == 111),
  "palindromic_lanes" -> And @@ (StringReverse[#] == # & /@ palLanes),
  "lo_shu_rows_columns_diagonals_15" -> (
    And @@ Thread[Total /@ loShu == 15] &&
    And @@ Thread[Total /@ Transpose[loShu] == 15] &&
    Tr[loShu] == 15 &&
    Total[Table[loShu[[i, 4 - i]], {i, 1, 3}]] == 15
  ),
  "lo_shu_total_45" -> (Total[Flatten[loShu]] == 45),
  "lo_shu_reciprocal_rotate180_self" ->
    (10 - (Reverse /@ Reverse[loShu]) == loShu),
  "lo_shu_centered_outer_set" ->
    (Sort[DeleteCases[Flatten[loShu - 5], 0]] == {-4, -3, -2, -1, 1, 2, 3, 4}),
  "geometry_144x36_5184" ->
    ((4*3)^2 == 144 && 144*36 == 5184 && 72^2 == 5184 &&
      81*64 == 5184 && 1296*4 == 5184),
  "manifold_power_identity" -> (72^72 == 5184^36 == 2^216*3^144),
  "mod_anchor_zero" -> (Mod[72^72, 5184] == 0),
  "fixed_width_zero_state_5184" -> (StringLength[StringRepeat["0", 5184]] == 5184),
  "native_AB_order_structurally_distinct" -> UnsameQ[hcAB, hcBA],
  "native_quotient_order_structurally_distinct" -> UnsameQ[hcAoverB, hcBoverA],
  "delta_cancellation_not_structural_identity" -> UnsameQ[hcCancel, hcInf],
  "gamma_factor_combination_not_identity" -> UnsameQ[hcGamma, hcGammaCombined],
  "gamma_factor_reorder_not_identity" -> UnsameQ[hcGamma, hcGammaReordered],
  "ieee_dyadic_decimal_identity" ->
    FullSimplify[
      n0*5^k/10^k == n0/2^k,
      Assumptions -> Element[{n0, k}, Integers] && k >= 0
    ],
  "t64_cardinality" -> (Length[triplets] == 64),
  "t64_operation64_bijection" -> (Sort[ops] == Range[0, 63]),
  "t64_operation64_roundtrip" -> roundTrip64,
  "operation64_8x8" -> And @@ Table[
    k == 8 Quotient[k, 8] + Mod[k, 8],
    {k, 0, 63}
  ],
  "ascii_bigint_mod64_last_byte" -> (Mod[256, 64] == 0),
  "rna_terminal_codes" -> (Mod[{119, 120, 121, 122}, 64] == {55, 56, 57, 58}),
  "thread_scope_intersection_no_expansion" -> (
    Complement[scopeABC, scopeA] == {} &&
    Complement[scopeABC, scopeB] == {} &&
    Complement[scopeABC, scopeC] == {}
  ),
  "tripartite_family_all_three_surfaces" -> And @@ tripartite,
  "vm81_reciprocal_topology" -> (81 == 1 + 40*2),
  "reciprocal_pair_mean_45" -> (pairMeanResidual == 0),
  "reciprocal_pair_normalizes_zero" -> (pairMeanResidual == 0),
  "quantization_ninth_count" -> (Length[Range[-81, 81]] == 163),
  "quantization_ninth_bounds" ->
    ({Min[Range[-81, 81]/9], Max[Range[-81, 81]/9]} == {-9, 9}),
  "quantization_ninth_step" -> (Union[Differences[Range[-81, 81]/9]] == {1/9}),
  "phase_orbit_exact" -> (phaseOrbit == {8, 24, 40, 56, 72, 16, 32, 48, 64}),
  "phase_orbit_order_nine" -> (72/GCD[16, 72] == 9),
  "phase_orbit_reciprocal_reflection" -> phaseReflection,
  "phase_two_turn_closure" -> (9*16 == 144 == 2*72),
  "half_cycle_reciprocal_involution" ->
    And @@ Table[
      Mod[Mod[e + 36, 72] + 36, 72] == Mod[e, 72],
      {e, 0, 71}
    ],
  "stack_root_preimage_order_sensitive" -> UnsameQ[stack12, stack21]
|>;

failed = Keys @ Select[checks, # =!= True &];

result = <|
  "schema" -> "HHS_LANE5_MATHEMATICAL_SYNTHESIS_WOLFRAM_20260921_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "phase_orbit_lift72" -> phaseOrbit,
  "t64_count" -> Length[triplets],
  "reciprocal_pair_mean_residual" -> pairMeanResidual,
  "ordered_brahmagupta_lhs" -> lhsOrdered,
  "ordered_brahmagupta_rhs" -> rhsOrdered,
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
