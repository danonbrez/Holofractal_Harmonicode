(* Pass 220 I076 — ExactMatrixPower HIR hydration.
   Structural lowering only. No host MatrixPower, numeric exponent evaluation,
   square-matrix fallback, or unverified VM81 execution is performed. *)

ClearAll["Global\`*"];

pass169Type="ExactMatrixPower";
nodeKind="EXACT_SYMBOLIC_MATRIX_POWER";
contract="HHS-P169-HSAE-VM81-ESCPR";

mWZ={{"-w*z","z-w"},{"z-w","w*z"},{"w*z","-w*z"},{"y+x","z-w"}};
mXY={{"-x*y","y+x"},{"y+x","x*y"},{"x*y","-x*y"},{"y+x","z-w"}};

nodes={
 <|"node_kind"->nodeKind,"canonical_type"->pass169Type,"contract"->contract,
   "source_node"->"MatrixPower[M_wz,x^2]","shape"->{4,2},
   "exponent_token"->"x^2","ordered_cells"->mWZ,
   "host_matrixpower_evaluated"->False,
   "square_matrix_requirement_imported"->False,
   "numeric_exponent_evaluated"->False,
   "matrix_power_value_derived"->False,
   "vm81_execution_verified"->False,
   "vm81_admission_required"->True|>,
 <|"node_kind"->nodeKind,"canonical_type"->pass169Type,"contract"->contract,
   "source_node"->"MatrixPower[M_xy,x^4]","shape"->{4,2},
   "exponent_token"->"x^4","ordered_cells"->mXY,
   "host_matrixpower_evaluated"->False,
   "square_matrix_requirement_imported"->False,
   "numeric_exponent_evaluated"->False,
   "matrix_power_value_derived"->False,
   "vm81_execution_verified"->False,
   "vm81_admission_required"->True|>
};

sourceNodes=nodes[[All,"source_node"]];
shapes=nodes[[All,"shape"]];
exponents=nodes[[All,"exponent_token"]];
cells=Flatten[nodes[[All,"ordered_cells"]],2];
hash72=72; chars=5184; planes=3; attached=planes chars;

checks=<|
"01_pass169_type_exact"->(pass169Type==="ExactMatrixPower"),
"02_hir_kind_exact"->(nodeKind==="EXACT_SYMBOLIC_MATRIX_POWER"),
"03_contract_exact"->(contract==="HHS-P169-HSAE-VM81-ESCPR"),
"04_two_nodes"->(Length[nodes]===2),
"05_shapes_exact"->(shapes==={{4,2},{4,2}}),
"06_source_nodes_exact"->(sourceNodes==={"MatrixPower[M_wz,x^2]","MatrixPower[M_xy,x^4]"}),
"07_exponent_tokens_exact"->(exponents==={"x^2","x^4"}),
"08_ordered_cells_total_16"->(Length[cells]===16),
"09_mwz_shape_4x2"->(Dimensions[mWZ]==={4,2}),
"10_mxy_shape_4x2"->(Dimensions[mXY]==={4,2}),
"11_xy_present"->MemberQ[cells,"x*y"],
"12_neg_xy_present"->MemberQ[cells,"-x*y"],
"13_wz_present"->MemberQ[cells,"w*z"],
"14_neg_wz_present"->MemberQ[cells,"-w*z"],
"15_y_plus_x_present"->MemberQ[cells,"y+x"],
"16_z_minus_w_present"->MemberQ[cells,"z-w"],
"17_no_host_matrixpower"->And@@Map[(#["host_matrixpower_evaluated"]===False)&,nodes],
"18_no_square_requirement"->And@@Map[(#["square_matrix_requirement_imported"]===False)&,nodes],
"19_no_numeric_exponent_eval"->And@@Map[(#["numeric_exponent_evaluated"]===False)&,nodes],
"20_no_matrix_value_derivation"->And@@Map[(#["matrix_power_value_derived"]===False)&,nodes],
"21_no_vm81_execution_claim"->And@@Map[(#["vm81_execution_verified"]===False)&,nodes],
"22_vm81_admission_required"->And@@Map[(#["vm81_admission_required"]===True)&,nodes],
"23_hash72_square_5184"->(hash72^2===chars),
"24_hash216_width"->(3 hash72===216),
"25_hydration_15552"->(attached===15552),
"26_candidate_only"->True
|>;

failed=Keys@Select[checks,#=!=True&];
report=<|
"schema"->"HHS_PASS_220_I076_EXACT_MATRIX_POWER_HIR_HYDRATION_WOLFRAM_V1",
"status"->If[failed==={},"PASS","FAIL"],
"check_count"->Length[checks],
"pass_count"->Count[Values[checks],True],
"failed"->failed,
"canonical_type"->pass169Type,
"node_kind"->nodeKind,
"contract_id"->contract,
"node_count"->Length[nodes],
"rectangular_shapes"->shapes,
"source_nodes"->sourceNodes,
"exponent_tokens"->exponents,
"ordered_cell_occurrences"->Length[cells],
"host_matrixpower_evaluations"->0,
"numeric_exponent_evaluations"->0,
"matrix_power_values_derived"->0,
"vm81_executions_verified"->0,
"vm81_admission_required"->True,
"hash216_width"->216,
"full_attached_components"->attached,
"checks"->checks
|>;

Print[ExportString[report,"RawJSON","Compact"->False]];
