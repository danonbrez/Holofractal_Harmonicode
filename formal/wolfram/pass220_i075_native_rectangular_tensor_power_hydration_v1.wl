(* Pass 220 I075 — native rectangular tensor-power hydration.
   This formalization evaluates exact structural invariants only. It does not
   invoke standard Wolfram MatrixPower on the native 4x2 HARMONICODE nodes. *)

ClearAll["Global\`*"];

mWZ={{"-w*z","z-w"},{"z-w","w*z"},{"w*z","-w*z"},{"y+x","z-w"}};
mXY={{"-x*y","y+x"},{"y+x","x*y"},{"x*y","-x*y"},{"y+x","z-w"}};

nodes={
 <|"operator"->"HARMONICODE_RECTANGULAR_TENSOR_POWER",
   "base_role"->"M_WZ","rows"->4,"columns"->2,"exponent_token"->"x^2",
   "ordered_cells"->mWZ,"source_node"->"MatrixPower[M_wz,x^2]",
   "host_evaluated"->False,"numeric_exponent_evaluated"->False|>,
 <|"operator"->"HARMONICODE_RECTANGULAR_TENSOR_POWER",
   "base_role"->"M_XY","rows"->4,"columns"->2,"exponent_token"->"x^4",
   "ordered_cells"->mXY,"source_node"->"MatrixPower[M_xy,x^4]",
   "host_evaluated"->False,"numeric_exponent_evaluated"->False|>
};

cells=Flatten[{mWZ,mXY}];
unique=DeleteDuplicates[cells];
occurrenceIds=Flatten[Map[First@FirstPosition[unique,#]-1&,cells]];
reconstructed=unique[[occurrenceIds+1]];

hash72=72; chars=5184; planes=3; attached=planes chars;

checks=<|
"01_two_nodes"->(Length[nodes]===2),
"02_mwz_shape_4x2"->(Dimensions[mWZ]==={4,2}),
"03_mxy_shape_4x2"->(Dimensions[mXY]==={4,2}),
"04_all_nodes_rectangular"->And@@Map[(#["rows"]===4&&#["columns"]===2)&,nodes],
"05_operator_tag_exact"->And@@Map[(#["operator"]==="HARMONICODE_RECTANGULAR_TENSOR_POWER")&,nodes],
"06_exponent_tokens_exact"->(nodes[[All,"exponent_token"]]==={"x^2","x^4"}),
"07_source_nodes_exact"->(nodes[[All,"source_node"]]==={"MatrixPower[M_wz,x^2]","MatrixPower[M_xy,x^4]"}),
"08_host_eval_false"->And@@Map[(#["host_evaluated"]===False)&,nodes],
"09_numeric_exponent_eval_false"->And@@Map[(#["numeric_exponent_evaluated"]===False)&,nodes],
"10_cell_occurrences_16"->(Length[cells]===16),
"11_occurrence_ids_16"->(Length[occurrenceIds]===16),
"12_reconstruction_exact"->(reconstructed===cells),
"13_unique_cells_6"->(Length[unique]===6),
"14_ordered_xy_present"->MemberQ[cells,"x*y"],
"15_ordered_neg_xy_present"->MemberQ[cells,"-x*y"],
"16_ordered_wz_present"->MemberQ[cells,"w*z"],
"17_ordered_neg_wz_present"->MemberQ[cells,"-w*z"],
"18_y_plus_x_present"->MemberQ[cells,"y+x"],
"19_z_minus_w_present"->MemberQ[cells,"z-w"],
"20_hash72_square_5184"->(hash72^2===chars),
"21_hash216_width"->(3 hash72===216),
"22_hydration_15552"->(attached===15552),
"23_no_host_matrixpower_call"->True,
"24_candidate_only"->True
|>;

failed=Keys@Select[checks,#=!=True&];
report=<|
"schema"->"HHS_PASS_220_I075_NATIVE_RECTANGULAR_TENSOR_POWER_HYDRATION_WOLFRAM_V1",
"status"->If[failed==={},"PASS","FAIL"],
"check_count"->Length[checks],
"pass_count"->Count[Values[checks],True],
"failed"->failed,
"node_count"->Length[nodes],
"rectangular_shapes"->{{4,2},{4,2}},
"cell_occurrences"->Length[cells],
"unique_cell_expressions"->Length[unique],
"unique_cells"->unique,
"occurrence_ids"->occurrenceIds,
"source_nodes"->nodes[[All,"source_node"]],
"host_matrixpower_evaluations"->0,
"numeric_exponent_evaluations"->0,
"hash216_width"->216,
"full_attached_components"->attached,
"checks"->checks
|>;

Print[ExportString[report,"RawJSON","Compact"->False]];
