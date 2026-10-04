(* Pass 220 I070 — I Tensor Lane 5 / VM81 exact candidate bridge. *)

ClearAll["Global\`*"];

eVector = {8,24,40,56,72,16,32,48,64};
eNorm = eVector/8;
loShu = {{4,9,2},{3,5,7},{8,1,6}};
route = Flatten[loShu];
phaseKernel = Table[
  Mod[2 ((row - 1) + (col - 1)) - 1, 9],
  {row, 1, 3}, {col, 1, 3}
];
a = 8 phaseKernel;
b = 8 (9 - phaseKernel);
c = Partition[eVector[[route]],3];
cNorm = c/8;

address[nucleus_, outcome_] := 9 nucleus + outcome;
addresses = Flatten@Table[address[n,o], {n,0,8},{o,0,8}];
perNucleus = Table[Table[address[n,o],{o,0,8}],{n,0,8}];

cells = Table[
  With[
    {
      row = Quotient[k,3] + 1,
      col = Mod[k,3] + 1,
      loshu = route[[k+1]]
    },
    <|
      "outcome" -> k,
      "row" -> row - 1,
      "column" -> col - 1,
      "lo_shu_value" -> loshu,
      "phase_a" -> a[[row,col]],
      "phase_b" -> b[[row,col]],
      "product_c" -> c[[row,col]],
      "product_e_index" -> loshu,
      "product_e_value" -> eVector[[loshu]],
      "normalized_a" -> phaseKernel[[row,col]],
      "normalized_b" -> 9-phaseKernel[[row,col]],
      "normalized_c" -> cNorm[[row,col]]
    |>
  ],
  {k,0,8}
];

checks = <|
  "01_e_width_9" -> (Length[eVector] === 9),
  "02_loshu_exact" -> (loShu === {{4,9,2},{3,5,7},{8,1,6}}),
  "03_route_permutation" -> (Sort[route] === Range[9]),
  "04_phase_kernel_exact" -> (phaseKernel === {{8,1,3},{1,3,5},{3,5,7}}),
  "05_a_reconstructs" -> (a === {{64,8,24},{8,24,40},{24,40,56}}),
  "06_b_reconstructs" -> (b === {{8,64,48},{64,48,32},{48,32,16}}),
  "07_c_reconstructs" -> (c === {{56,64,24},{40,72,32},{48,8,16}}),
  "08_reciprocal72" -> (a+b === ConstantArray[72,{3,3}]),
  "09_c_routes_e" -> (Flatten[c] === eVector[[route]]),
  "10_c_norm_permutation" -> (Sort[Flatten[cNorm]] === Range[9]),
  "11_cell_count_9" -> (Length[cells] === 9),
  "12_outcomes_0_8" -> (Lookup[cells,"outcome"] === Range[0,8]),
  "13_cell_loshu_matches_route" -> (Lookup[cells,"lo_shu_value"] === route),
  "14_cell_c_matches_e_route" -> And@@Table[
      cells[[k+1]]["product_c"] === eVector[[cells[[k+1]]["product_e_index"]]],
      {k,0,8}
    ],
  "15_cell_ab_72" -> And@@Table[
      cells[[k+1]]["phase_a"] + cells[[k+1]]["phase_b"] === 72,
      {k,0,8}
    ],
  "16_cell_normalized_ab_9" -> And@@Table[
      cells[[k+1]]["normalized_a"] + cells[[k+1]]["normalized_b"] === 9,
      {k,0,8}
    ],
  "17_vm81_global_count" -> (Length[addresses] === 81),
  "18_vm81_global_unique" -> (Length[DeleteDuplicates[addresses]] === 81),
  "19_vm81_global_range" -> (Sort[addresses] === Range[0,80]),
  "20_per_nucleus_width" -> And@@(Length[#]===9& /@ perNucleus),
  "21_nucleus0_range" -> (perNucleus[[1]] === Range[0,8]),
  "22_nucleus8_range" -> (perNucleus[[9]] === Range[72,80]),
  "23_address_rule_monotonic_per_nucleus" -> And@@Table[
      Differences[perNucleus[[n+1]]] === ConstantArray[1,8],
      {n,0,8}
    ],
  "24_nucleus_stride_9" -> And@@Table[
      perNucleus[[n+2,1]] - perNucleus[[n+1,1]] === 9,
      {n,0,7}
    ],
  "25_center_outcome_4" -> (cells[[5]]["outcome"] === 4),
  "26_center_loshu_5" -> (cells[[5]]["lo_shu_value"] === 5),
  "27_center_c_72" -> (cells[[5]]["product_c"] === 72),
  "28_center_c_mod72_zero" -> (Mod[cells[[5]]["product_c"],72] === 0),
  "29_no_real_values" -> FreeQ[{eVector,loShu,phaseKernel,a,b,c,cells,addresses},_Real],
  "30_generator_only_reconstructible" -> (
    {
      8 phaseKernel,
      8 (9-phaseKernel),
      Partition[eVector[[Flatten[loShu]]],3]
    } === {a,b,c}
  )
|>;

failed = Keys@Select[checks,#=!=True&];
report = <|
  "schema" -> "HHS_PASS_220_I070_I_TENSOR_LANE5_VM81_BRIDGE_WOLFRAM_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks],True],
  "failed" -> failed,
  "lo_shu_route" -> route,
  "matrix_a" -> a,
  "matrix_b" -> b,
  "matrix_c" -> c,
  "vm81_address_min" -> Min[addresses],
  "vm81_address_max" -> Max[addresses],
  "vm81_address_count" -> Length[addresses],
  "vm81_unique_count" -> Length[DeleteDuplicates[addresses]],
  "cells" -> cells,
  "checks" -> checks
|>;

Print[ExportString[report,"RawJSON","Compact"->False]];
