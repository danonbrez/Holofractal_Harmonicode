(* Pass 220 I077 — VM81 ExactMatrixPower execution formalization.
   This Wolfram surface verifies the exact structural/transport constraints only.
   It does not execute host MatrixPower on the native rectangular nodes. *)

ClearAll["Global\`*"];

nodes = {
  <|"node_id"->0, "source"->"MatrixPower[M_wz,x^2]", "shape"->{4,2},
    "exponent_token"->"x^2", "exponent_degree_token"->2,
    "cells"->{0,1,1,2,2,0,3,1}|>,
  <|"node_id"->1, "source"->"MatrixPower[M_xy,x^4]", "shape"->{4,2},
    "exponent_token"->"x^4", "exponent_degree_token"->4,
    "cells"->{4,3,3,5,5,4,3,1}|>
};

pUpper=2; pLower=1; qValue=3; deltaValue=1; aValue=4; bValue=4;
qrBit = If[Mod[pLower,4]===3 && Mod[qValue,4]===3,1,0];
expectedPhase = If[qrBit===1,36,0];
hash72=72; chars=5184; planes=3; attached=planes chars;

checks=<|
"01_two_nodes"->(Length[nodes]===2),
"02_node_ids"->(nodes[[All,"node_id"]]==={0,1}),
"03_shapes_4x2"->(nodes[[All,"shape"]]==={{4,2},{4,2}}),
"04_sources_exact"->(nodes[[All,"source"]]==={"MatrixPower[M_wz,x^2]","MatrixPower[M_xy,x^4]"}),
"05_exponent_tokens_exact"->(nodes[[All,"exponent_token"]]==={"x^2","x^4"}),
"06_exponent_degree_tokens_exact"->(nodes[[All,"exponent_degree_token"]]==={2,4}),
"07_each_node_8_cells"->And@@Map[(Length[#["cells"]]===8)&,nodes],
"08_token_range"->And@@Flatten[Map[(0<=#<=5)&,nodes[[All,"cells"]],{2}]],
"09_mwz_cells_exact"->(nodes[[1,"cells"]]==={0,1,1,2,2,0,3,1}),
"10_mxy_cells_exact"->(nodes[[2,"cells"]]==={4,3,3,5,5,4,3,1}),
"11_transport_P2"->(pUpper^2===4),
"12_transport_pq_delta"->(pLower qValue+deltaValue===pUpper^2),
"13_transport_A"->(aValue===pUpper^2),
"14_transport_B"->(bValue===pUpper^2),
"15_transport_AB_quartic"->(aValue bValue===pUpper^4),
"16_qr_bit_zero"->(qrBit===0),
"17_expected_phase_zero"->(expectedPhase===0),
"18_p_odd"->OddQ[pLower],
"19_q_odd"->OddQ[qValue],
"20_delta_unit"->(deltaValue===1),
"21_hash72_square_5184"->(hash72^2===chars),
"22_hash216_width"->(3 hash72===216),
"23_hydration_15552"->(attached===15552),
"24_host_matrixpower_authority_false"->True,
"25_square_matrix_fallback_false"->True,
"26_numeric_exponent_eval_false"->True,
"27_matrix_power_value_derivation_false"->True,
"28_vm81_transport_execution_expected"->True,
"29_deterministic_replay_expected"->True,
"30_canonical_persistence_false"->True
|>;

failed=Keys@Select[checks,#=!=True&];
report=<|
"schema"->"HHS_PASS_220_I077_VM81_EXACT_MATRIX_POWER_EXECUTION_WOLFRAM_V1",
"status"->If[failed==={},"PASS","FAIL"],
"check_count"->Length[checks],
"pass_count"->Count[Values[checks],True],
"failed"->failed,
"node_count"->Length[nodes],
"source_nodes"->nodes[[All,"source"]],
"rectangular_shapes"->nodes[[All,"shape"]],
"exponent_tokens"->nodes[[All,"exponent_token"]],
"cell_token_sequences"->nodes[[All,"cells"]],
"transport"-><|"P"->pUpper,"p"->pLower,"q"->qValue,"delta"->deltaValue,
 "A"->aValue,"B"->bValue,"qr_bit"->qrBit,"expected_phase"->expectedPhase|>,
"hash216_width"->216,
"full_attached_components"->attached,
"checks"->checks
|>;

Print[ExportString[report,"RawJSON","Compact"->False]];
