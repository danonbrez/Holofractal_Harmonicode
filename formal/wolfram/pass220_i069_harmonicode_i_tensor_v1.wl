(* Pass 220 I069 — HARMONICODE I Tensor exact formalization.
   The verbatim source is preserved as text so native E-membrane and ordered
   MatrixTimes semantics are not rewritten by host Wolfram evaluation. *)

ClearAll["Global\`*"];

verbatimSource =
"u^((MatrixTimes(x,((-List(List(64,8,24),List(8,24,40),List(24,40,56)))/(E==List(8,24,40,56,72,16,32,48,64))))-MatrixTimes(y,((-List(List(8,64,48),List(64,48,32),List(48,32,16)))/(E==List(8,24,40,56,72,16,32,48,64))))==Mod(MatrixTimes(x*y,(List(List(56,64,24),List(40,72,32),List(48,8,16))/(E==List(8,24,40,56,72,16,32,48,64)))),72))/u==u^72)";

eVector = {8,24,40,56,72,16,32,48,64};
loShu = {{4,9,2},{3,5,7},{8,1,6}};
route = Flatten[loShu];

phaseKernel = Table[
  Mod[2 ((row - 1) + (col - 1)) - 1, 9],
  {row, 1, 3}, {col, 1, 3}
];

a = 8 phaseKernel;
b = 8 (9 - phaseKernel);
c = Partition[eVector[[route]], 3];

expectedA = {{64,8,24},{8,24,40},{24,40,56}};
expectedB = {{8,64,48},{64,48,32},{48,32,16}};
expectedC = {{56,64,24},{40,72,32},{48,8,16}};

checks = <|
  "01_verbatim_source_nonempty" -> (StringLength[verbatimSource] > 0),
  "02_verbatim_matrix_times_preserved" -> StringContainsQ[verbatimSource, "MatrixTimes"],
  "03_verbatim_e_membrane_preserved" -> StringContainsQ[verbatimSource, "E==List(8,24,40,56,72,16,32,48,64)"],
  "04_verbatim_ordered_xy_preserved" -> StringContainsQ[verbatimSource, "MatrixTimes(x*y"],
  "05_verbatim_u72_preserved" -> StringContainsQ[verbatimSource, "u^72"],
  "06_e_vector_length" -> (Length[eVector] === 9),
  "07_e_vector_eight_scaled_permutation" -> (Sort[eVector/8] === Range[9]),
  "08_lo_shu_exact" -> (loShu === {{4,9,2},{3,5,7},{8,1,6}}),
  "09_lo_shu_is_permutation" -> (Sort[route] === Range[9]),
  "10_phase_kernel_exact" -> (phaseKernel === {{8,1,3},{1,3,5},{3,5,7}}),
  "11_a_generator_reconstructs" -> (a === expectedA),
  "12_b_generator_reconstructs" -> (b === expectedB),
  "13_a_b_pointwise_72_closure" -> (a + b === ConstantArray[72,{3,3}]),
  "14_b_is_mod72_negative_a" -> (Mod[-a,72] === b),
  "15_a_is_mod72_negative_b" -> (Mod[-b,72] === a),
  "16_c_loshu_routes_e" -> (c === expectedC),
  "17_c_eight_scaled_permutation" -> (Sort[Flatten[c/8]] === Range[9]),
  "18_c_center_is_72" -> (c[[2,2]] === 72),
  "19_c_center_mod72_zero" -> (Mod[c[[2,2]],72] === 0),
  "20_a_det_exact" -> (Det[a] === -18432),
  "21_b_det_exact" -> (Det[b] === 18432),
  "22_c_det_exact" -> (Det[c] === 32256),
  "23_normalized_dets_exact" -> ({Det[a/8],Det[b/8],Det[c/8]} === {-36,36,63}),
  "24_all_dets_72_divisible" -> (Mod[{Det[a],Det[b],Det[c]},72] === {0,0,0}),
  "25_integer_only" -> FreeQ[{eVector,loShu,phaseKernel,a,b,c}, _Real],
  "26_generator_exact_roundtrip" -> (
    {a,b,c} === {
      8 Table[Mod[2 ((row - 1) + (col - 1)) - 1, 9], {row,1,3},{col,1,3}],
      8 (9 - Table[Mod[2 ((row - 1) + (col - 1)) - 1, 9], {row,1,3},{col,1,3}]),
      Partition[eVector[[Flatten[loShu]]],3]
    }
  )
|>;

failed = Keys @ Select[checks, # =!= True &];

report = <|
  "schema" -> "HHS_PASS_220_I069_HARMONICODE_I_TENSOR_WOLFRAM_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "e_vector" -> eVector,
  "lo_shu_route" -> route,
  "phase_kernel" -> phaseKernel,
  "matrix_a" -> a,
  "matrix_b" -> b,
  "matrix_c" -> c,
  "determinants" -> {Det[a],Det[b],Det[c]},
  "normalized_determinants" -> {Det[a/8],Det[b/8],Det[c/8]},
  "checks" -> checks
|>;

Print[ExportString[report, "RawJSON", "Compact" -> False]];
