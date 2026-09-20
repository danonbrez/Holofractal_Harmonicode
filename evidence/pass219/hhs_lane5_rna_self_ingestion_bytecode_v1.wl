ClearAll[
  alphabet, code, triplets, encodeOperation64, decodeOperation64,
  compactWord, multiplicativeWord, bytesToBigInt, project64,
  projectWord, typedWord, attractors, fixedWords, basinCounts
];

alphabet = {"x","y","z","w"};
code = <|"x"->0,"y"->1,"z"->2,"w"->3|>;
triplets = Tuples[alphabet,3];

encodeOperation64[t_List] :=
  16*code[t[[1]]] + 4*code[t[[2]]] + code[t[[3]]];

decodeOperation64[n_Integer] := Module[{d0,r,d1,d2},
  d0 = Quotient[n,16];
  r = Mod[n,16];
  d1 = Quotient[r,4];
  d2 = Mod[r,4];
  {alphabet[[d0+1]],alphabet[[d1+1]],alphabet[[d2+1]]}
];

compactWord[t_List] := StringJoin[t];
multiplicativeWord[t_List] := StringRiffle[t,"*"];
bytesToBigInt[s_String] := FromDigits[ToCharacterCode[s],256];
project64[s_String] := Mod[bytesToBigInt[s],64];
projectWord[t_List] := decodeOperation64[project64[compactWord[t]]];
typedWord[t_List] := decodeOperation64[encodeOperation64[t]];

typedOutputs = typedWord /@ triplets;
projectedOutputs = projectWord /@ triplets;
attractors = DeleteDuplicates[projectedOutputs];
fixedWords = Select[triplets, projectWord[#] === # &];
basinCounts = Association[
  Counts[StringJoin /@ projectedOutputs]
];

lastByteRule = And@@(
  TrueQ[
    project64[compactWord[#]]
    == Mod[Last[ToCharacterCode[compactWord[#]]],64]
  ]& /@ triplets
);

compactExplicitAgree = And@@(
  TrueQ[
    project64[compactWord[#]]
    == project64[multiplicativeWord[#]]
  ]& /@ triplets
);

oneStepToFixed = And@@(
  TrueQ[projectWord[projectWord[#]] === projectWord[#]]& /@ triplets
);

typedIdentity = And@@MapThread[SameQ,{typedOutputs,triplets}];

checks = <|
  "state_count_64" -> TrueQ[Length[triplets] == 64],
  "typed_operation64_unique_64" ->
    TrueQ[Length[DeleteDuplicates[encodeOperation64 /@ triplets]] == 64],
  "typed_native_identity_all_64" -> TrueQ[typedIdentity],
  "ascii_base_is_256" -> TrueQ[256 == 4*64],
  "base256_vanishes_mod64" -> TrueQ[Mod[256,64] == 0],
  "last_byte_rule_all_64" -> TrueQ[lastByteRule],
  "compact_explicit_agree_all_64" -> TrueQ[compactExplicitAgree],
  "projected_image_size_4" -> TrueQ[Length[attractors] == 4],
  "projected_operations_exact" ->
    TrueQ[Sort[DeleteDuplicates[project64[compactWord[#]]& /@ triplets]]
      == {55,56,57,58}],
  "attractors_exact" ->
    TrueQ[Sort[StringJoin /@ attractors] == {"wyw","wzx","wzy","wzz"}],
  "fixed_points_exact" ->
    TrueQ[Sort[StringJoin /@ fixedWords] == {"wyw","wzx","wzy","wzz"}],
  "basins_equal_16" ->
    TrueQ[Sort[Values[basinCounts]] == {16,16,16,16}],
  "one_step_to_fixed_all_64" -> TrueQ[oneStepToFixed],
  "w_ascii_maps_55" -> TrueQ[Mod[First[ToCharacterCode["w"]],64] == 55],
  "x_ascii_maps_56" -> TrueQ[Mod[First[ToCharacterCode["x"]],64] == 56],
  "y_ascii_maps_57" -> TrueQ[Mod[First[ToCharacterCode["y"]],64] == 57],
  "z_ascii_maps_58" -> TrueQ[Mod[First[ToCharacterCode["z"]],64] == 58],
  "terminal_root_anchor" -> TrueQ[({0,-2}+{-2,0})/2 == {-1,-1}]
|>;

result = <|
  "schema" -> "HHS_PASS219_LANE5_RNA_SELF_INGESTION_BYTECODE_WOLFRAM_V1",
  "experiment_id" -> "HHS-X5184-001",
  "status" -> If[And@@Values[checks],"PASS","FAIL"],
  "checks" -> checks,
  "typed_image_size" -> Length[DeleteDuplicates[typedOutputs]],
  "external_projection_image_size" -> Length[attractors],
  "fixed_points" -> Sort[StringJoin /@ fixedWords],
  "basin_counts" -> KeySort[basinCounts],
  "projected_operations" ->
    Sort[DeleteDuplicates[project64[compactWord[#]]& /@ triplets]],
  "projection" -> "EXPERIMENTAL_NONCANONICAL_ASCII_BIGINT_MOD64",
  "canonical_authority" -> False,
  "bytes_executed_as_machine_instructions" -> False
|>;

ExportString[result,"RawJSON","Compact"->True]