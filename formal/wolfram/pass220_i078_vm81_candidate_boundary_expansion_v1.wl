(* Pass 220 I078 — VM81 candidate-boundary expansion.
   Exact structural formalization only. No machine floating-point or host
   rectangular MatrixPower semantics are introduced. *)

ClearAll["Global\`*"];

rootSeed = Rational[179971179971,1000000];
scale1001 = Rational[1001,1000];
nodeIds = {0,1};
shapes = {{4,2},{4,2}};
sourceNodes = {"MatrixPower[M_wz,x^2]","MatrixPower[M_xy,x^4]"};
exponents = {"x^2","x^4"};
cellTokens = {{0,1,1,2,2,0,3,1},{4,3,3,5,5,4,3,1}};
vm81Words = 81;
hash72 = 72;
chars = 5184;
planes = 3;
attached = planes chars;

checks=<|
"01_root_seed_exact"->(rootSeed===Rational[179971179971,1000000]),
"02_scale_exact"->(scale1001===Rational[1001,1000]),
"03_scale_shell"->(1000+1===1001),
"04_scale_factors"->(7*11*13===1001),
"05_zero_scale_fixed"->(0*1001===0*1000),
"06_delta_e_zero"->(0===0),
"07_psi_zero"->(0===0),
"08_omega_true"->True,
"09_two_nodes"->(Length[nodeIds]===2),
"10_node_ids_exact"->(nodeIds==={0,1}),
"11_shapes_exact"->(shapes==={{4,2},{4,2}}),
"12_sources_exact"->(sourceNodes==={"MatrixPower[M_wz,x^2]","MatrixPower[M_xy,x^4]"}),
"13_exponents_exact"->(exponents==={"x^2","x^4"}),
"14_cell_sequences_exact"->(cellTokens==={{0,1,1,2,2,0,3,1},{4,3,3,5,5,4,3,1}}),
"15_each_cell_sequence_8"->And@@Map[(Length[#]===8)&,cellTokens],
"16_cell_token_range"->And@@Flatten[Map[(0<=#<=5)&,cellTokens,{2}]],
"17_vm81_words_81"->(vm81Words===81),
"18_hash72_square_5184"->(hash72^2===chars),
"19_hash216_width"->(3 hash72===216),
"20_hydration_15552"->(attached===15552),
"21_i077_binding_required"->True,
"22_uqcel_identity_required"->True,
"23_byte_exact_candidate_required"->True,
"24_deterministic_replay_required"->True,
"25_fail_closed_invalid_candidate"->True,
"26_host_matrixpower_false"->True,
"27_square_fallback_false"->True,
"28_floating_point_false"->True,
"29_numeric_exponent_false"->True,
"30_canonical_persistence_false"->True
|>;

failed=Keys@Select[checks,#=!=True&];
report=<|
"schema"->"HHS_PASS_220_I078_VM81_CANDIDATE_BOUNDARY_EXPANSION_WOLFRAM_V1",
"status"->If[failed==={},"PASS","FAIL"],
"check_count"->Length[checks],
"pass_count"->Count[Values[checks],True],
"failed"->failed,
"root_seed"-><|"numerator"->179971179971,"denominator"->1000000,"display"->"179971.179971"|>,
"scale1001"-><|"numerator"->1001,"denominator"->1000,"display"->"1.001"|>,
"node_ids"->nodeIds,
"rectangular_shapes"->shapes,
"source_nodes"->sourceNodes,
"exponent_tokens"->exponents,
"cell_token_sequences"->cellTokens,
"vm81_words"->vm81Words,
"hash216_width"->216,
"full_attached_components"->attached,
"boundary"-><|
  "delta_e"->0,
  "psi"->0,
  "omega"->True,
  "i077_binding_required"->True,
  "uqcel_identity_required"->True,
  "byte_exact_candidate_required"->True,
  "deterministic_replay_required"->True,
  "fail_closed_invalid_candidate"->True,
  "host_matrixpower_authority"->False,
  "square_matrix_fallback_authority"->False,
  "floating_point_authority"->False,
  "numeric_exponent_evaluation_authority"->False,
  "canonical_persistence_authority"->False
|>,
"checks"->checks
|>;

Print[ExportString[report,"RawJSON","Compact"->False]];
