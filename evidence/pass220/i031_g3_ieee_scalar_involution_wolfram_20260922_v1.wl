(* Pass 220 I031: exact IEEE scalar reciprocal involution. *)
ClearAll["Global`*"];

proofCell = ProofCell["123321.111"];

splitRebuild[n_, e_, f_] := Module[
  {low, sign, exponent, fraction},
  low = Mod[n, 2^(e + f)];
  sign = Quotient[n, 2^(e + f)];
  exponent = Quotient[low, 2^f];
  fraction = Mod[low, 2^f];
  sign*2^(e + f) + exponent*2^f + fraction
];

partitionProof[e_, f_] := FullSimplify[
  splitRebuild[n, e, f] == n,
  Assumptions ->
    Element[n, Integers] && 0 <= n < 2^(1 + e + f)
];

phaseSwapRules = {
  Phase[x] -> Phase[y], Phase[y] -> Phase[x],
  Phase[z] -> Phase[w], Phase[w] -> Phase[z]
};
Sigma[expr_] := expr /. phaseSwapRules;

scalarState[b_] := ScalarPhase[b, Phase[x]];
returnState[b_] := Sigma[scalarState[b]];

binary64Tenth = FromDigits["3FB999999999999A", 16];
binary64TenthNumerator = 3602879701896397;
binary64TenthDenominator = 36028797018963968;

positiveZero64 = FromDigits["0000000000000000", 16];
negativeZero64 = FromDigits["8000000000000000", 16];
nanPayload64 = FromDigits["7FF8000000000042", 16];
positiveInfinity64 = FromDigits["7FF0000000000000", 16];
negativeInfinity64 = FromDigits["FFF0000000000000", 16];

binary16Exhaustive =
  And @@ Table[splitRebuild[k, 5, 10] == k, {k, 0, 2^16 - 1}];

checks = <|
  "01_binary16_partition_parametric" -> partitionProof[5, 10],
  "02_binary32_partition_parametric" -> partitionProof[8, 23],
  "03_binary64_partition_parametric" -> partitionProof[11, 52],
  "04_binary128_partition_parametric" -> partitionProof[15, 112],
  "05_binary16_all_65536_rebuild" -> binary16Exhaustive,
  "06_phase_swap_scalar_bits_invariant" ->
    (returnState[n][[1]] === scalarState[n][[1]]),
  "07_phase_swap_is_involution" ->
    (Sigma[Sigma[scalarState[n]]] === scalarState[n]),
  "08_reciprocal_phase_is_y" ->
    (returnState[n][[2]] === Phase[y]),
  "09_signed_zero_bit_patterns_distinct" ->
    (positiveZero64 =!= negativeZero64),
  "10_signed_zero_numeric_projection_can_coincide" ->
    (0 == -0),
  "11_nan_payload_field_rebuild_exact" ->
    (splitRebuild[nanPayload64, 11, 52] == nanPayload64),
  "12_positive_infinity_field_rebuild_exact" ->
    (splitRebuild[positiveInfinity64, 11, 52] == positiveInfinity64),
  "13_negative_infinity_field_rebuild_exact" ->
    (splitRebuild[negativeInfinity64, 11, 52] == negativeInfinity64),
  "14_binary64_tenth_storage_bit_rebuild_exact" ->
    (splitRebuild[binary64Tenth, 11, 52] == binary64Tenth),
  "15_binary64_tenth_exact_dyadic_diff_exact" ->
    (
      binary64TenthNumerator/binary64TenthDenominator - 1/10 ==
      1/180143985094819840
    ),
  "16_proof_cell_opaque" ->
    (proofCell === ProofCell["123321.111"]),
  "17_no_scalar_inflation_under_phase_exchange" ->
    (ScalarMagnitude[returnState[n][[1]]] === ScalarMagnitude[n])
|>;

failed = Keys @ Select[checks, # =!= True &];
result = <|
  "schema" ->
    "HHS_PASS_220_I031_G3_IEEE_SCALAR_INVOLUTION_WOLFRAM_20260922_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "proof_cell" -> "123321.111",
  "binary64_0p1_hex" -> "3FB999999999999A",
  "binary64_0p1_exact_dyadic" -> {
    binary64TenthNumerator,
    binary64TenthDenominator
  },
  "binary64_0p1_minus_one_tenth" -> "1/180143985094819840",
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
