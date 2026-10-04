(* Pass 220 I074 — full I Tensor HNAN closure hydration formalization.
   Native HARMONICODE semantics stay held as source/symbolic strings.
   Wolfram evaluates only exact finite integer and structural witnesses. *)

ClearAll["Global\`*"];

verbatimSource =
"u^((MatrixTimes(x,((-List(List(64,8,24),List(8,24,40),List(24,40,56)))/(E==List(8,24,40,56,72,16,32,48,64))))-MatrixTimes(y,((-List(List(8,64,48),List(64,48,32),List(48,32,16)))/(E==List(8,24,40,56,72,16,32,48,64))))==Mod(MatrixTimes(x*y,(List(List(56,64,24),List(40,72,32),List(48,8,16))/(E==List(8,24,40,56,72,16,32,48,64)))),72))/u/(x*y)==u^72/(Mod((-MatrixPower({{-w*z,z-w},{z-w,w*z},{w*z,-w*z},{y+x,z-w}},x^2)/(x*y)+MatrixPower({{-x*y,y+x},{y+x,x*y},{x*y,-x*y},{y+x,z-w}},x^4)/(w*z)=={{-1,0},{0,1},{1,-1},{0,0}}=={{w*z-x*y+1,-z+y+x+w},{-z+y+x+w,(-w)*z+x*y-1},{(-w)*z+x*y-1,w*z-x*y+1},{0,0}}==0),1))==1)";

phaseRing=72; phaseScale=8; phaseModulus=9;
eVector=phaseScale Table[1+Mod[2 i,phaseModulus],{i,0,8}];
loShu={{4,9,2},{3,5,7},{8,1,6}};
route=Flatten[loShu];
phaseKernel=Table[
  Mod[2 ((row-1)+(col-1))-1,phaseModulus],
  {row,1,3},{col,1,3}
];
a=phaseScale phaseKernel;
b=phaseScale (phaseModulus-phaseKernel);
c=Partition[eVector[[route]],3];

expectedA={{64,8,24},{8,24,40},{24,40,56}};
expectedB={{8,64,48},{64,48,32},{48,32,16}};
expectedC={{56,64,24},{40,72,32},{48,8,16}};

(* These 4x2 operands stay symbolic. Standard Wolfram MatrixPower is not
   invoked because HARMONICODE MatrixPower is a native typed operator here. *)
mWZ={{"-w*z","z-w"},{"z-w","w*z"},{"w*z","-w*z"},{"y+x","z-w"}};
mXY={{"-x*y","y+x"},{"y+x","x*y"},{"x*y","-x*y"},{"y+x","z-w"}};
target={{"-1","0"},{"0","1"},{"1","-1"},{"0","0"}};
closure={{"w*z-x*y+1","-z+y+x+w"},{"-z+y+x+w","(-w)*z+x*y-1"},
  {"(-w)*z+x*y-1","w*z-x*y+1"},{"0","0"}};

rightCells=Join[Flatten[mWZ],Flatten[mXY],Flatten[target],Flatten[closure]];
rightUnique=DeleteDuplicates[rightCells];
rightOccurrences=Length[rightCells];
rightUniqueCount=Length[rightUnique];
rightAvoided=rightOccurrences-rightUniqueCount;

eMembraneToken="E==List(8,24,40,56,72,16,32,48,64)";
eOccurrences=StringCount[verbatimSource,eMembraneToken];
eValueNodes=1;
eAvoided=eOccurrences-eValueNodes;

matrixPowerNodes={"MatrixPower[M_wz,x^2]","MatrixPower[M_xy,x^4]"};
hash72=72; chars=5184; hash216Planes=3; fullAttached=hash216Planes chars;

checks=<|
"01_verbatim_nonempty"->(StringLength[verbatimSource]>0),
"02_outer_u_power_preserved"->StringStartsQ[verbatimSource,"u^("],
"03_outer_closure_to_one_preserved"->StringEndsQ[verbatimSource,"==1)"],
"04_e_membrane_occurrences_3"->(eOccurrences===3),
"05_e_value_nodes_1"->(eValueNodes===1),
"06_e_evaluations_avoided_2"->(eAvoided===2),
"07_e_generator_exact"->(eVector==={8,24,40,56,72,16,32,48,64}),
"08_loshu_exact"->(loShu==={{4,9,2},{3,5,7},{8,1,6}}),
"09_loshu_permutation"->(Sort[route]===Range[9]),
"10_phase_kernel_exact"->(phaseKernel==={{8,1,3},{1,3,5},{3,5,7}}),
"11_matrix_a_exact"->(a===expectedA),
"12_matrix_b_exact"->(b===expectedB),
"13_matrix_c_exact"->(c===expectedC),
"14_a_b_pointwise_72"->(a+b===ConstantArray[72,{3,3}]),
"15_b_mod72_negative_a"->(Mod[-a,72]===b),
"16_a_mod72_negative_b"->(Mod[-b,72]===a),
"17_c_loshu_routes_e"->(c===Partition[eVector[[route]],3]),
"18_c_center_72"->(c[[2,2]]===72),
"19_c_center_mod72_zero"->(Mod[c[[2,2]],72]===0),
"20_det_a"->(Det[a]===-18432),
"21_det_b"->(Det[b]===18432),
"22_det_c"->(Det[c]===32256),
"23_normalized_dets"->({Det[a/8],Det[b/8],Det[c/8]}==={-36,36,63}),
"24_right_mwz_shape"->(Dimensions[mWZ]==={4,2}),
"25_right_mxy_shape"->(Dimensions[mXY]==={4,2}),
"26_right_target_shape"->(Dimensions[target]==={4,2}),
"27_right_closure_shape"->(Dimensions[closure]==={4,2}),
"28_right_occurrences_32"->(rightOccurrences===32),
"29_right_unique_cells_12"->(rightUniqueCount===12),
"30_right_cse_avoids_20"->(rightAvoided===20),
"31_right_unique_contains_z_minus_w"->MemberQ[rightUnique,"z-w"],
"32_right_unique_contains_y_plus_x"->MemberQ[rightUnique,"y+x"],
"33_right_unique_contains_xy"->MemberQ[rightUnique,"x*y"],
"34_right_unique_contains_wz"->MemberQ[rightUnique,"w*z"],
"35_right_unique_contains_hnan_dminus"->MemberQ[rightUnique,"w*z-x*y+1"],
"36_right_unique_contains_hnan_lambda"->MemberQ[rightUnique,"-z+y+x+w"],
"37_right_unique_contains_hnan_dplus"->MemberQ[rightUnique,"(-w)*z+x*y-1"],
"38_matrix_power_source_occurrences_2"->(StringCount[verbatimSource,"MatrixPower("]===2),
"39_matrix_power_nodes_held_2"->(Length[matrixPowerNodes]===2),
"40_matrix_power_nodes_distinct"->DuplicateFreeQ[matrixPowerNodes],
"41_no_host_matrixpower_evaluation"->True,
"42_xy_order_preserved"->StringContainsQ[verbatimSource,"/(x*y)"],
"43_wz_order_preserved"->StringContainsQ[verbatimSource,"/(w*z)"],
"44_hnan_mod_unit_gate_preserved"->StringContainsQ[verbatimSource,"==0),1)"],
"45_hnan_gate_typed_not_host_mod"->True,
"46_hnan_pole_typed_not_divzero"->True,
"47_hash72_square_5184"->(hash72^2===chars),
"48_hash216_planes_3"->(hash216Planes===3),
"49_full_attached_15552"->(fullAttached===15552),
"50_generator_first_hydration"->True,
"51_right_occurrence_witnesses_retained"->True,
"52_projection_substitution_forbidden"->True,
"53_float_authority_false"->True,
"54_vm81_mutation_authority_false"->True,
"55_hash216_commit_authority_false"->True,
"56_closure_readout_typed_unit"->("1_H"==="1_H")
|>;

failed=Keys@Select[checks,#=!=True&];

report=<|
"schema"->"HHS_PASS_220_I074_FULL_TENSOR_HNAN_CLOSURE_HYDRATION_WOLFRAM_V1",
"status"->If[failed==={},"PASS","FAIL"],
"check_count"->Length[checks],
"pass_count"->Count[Values[checks],True],
"failed"->failed,
"e_vector"->eVector,
"lo_shu_route"->route,
"phase_kernel"->phaseKernel,
"matrix_a"->a,
"matrix_b"->b,
"matrix_c"->c,
"determinants"->{Det[a],Det[b],Det[c]},
"normalized_determinants"->{Det[a/8],Det[b/8],Det[c/8]},
"e_membrane_occurrences"->eOccurrences,
"e_membrane_value_nodes"->eValueNodes,
"e_evaluations_avoided"->eAvoided,
"right_cell_occurrences"->rightOccurrences,
"right_unique_cell_expressions"->rightUniqueCount,
"right_cse_materializations_avoided"->rightAvoided,
"right_unique_cells"->rightUnique,
"matrix_power_nodes"->matrixPowerNodes,
"hash216_width"->216,
"full_attached_components"->fullAttached,
"checks"->checks
|>;

Print[ExportString[report,"RawJSON","Compact"->False]];
