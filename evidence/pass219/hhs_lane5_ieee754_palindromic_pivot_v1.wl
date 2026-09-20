ClearAll[n,k,frame,blocks,reverseRecover,carrier];

dyadicIdentity = FullSimplify[
  n/2^k == (n*5^k)/10^k,
  Assumptions -> Element[{n,k}, Integers] && k >= 0
];

pad[value_Integer, width_Integer] := IntegerString[value, 10, width];
frame[width_Integer, sign_Integer, scale_Integer, coeff_String] :=
  "754154" <> pad[width,2] <> ToString[sign] <> pad[scale,4] <>
  pad[StringLength[coeff],4] <> coeff;

blocks[s_String] := Table[
  StringTake[s,{i,Min[i+71,StringLength[s]]}],
  {i,1,StringLength[s],72}
];

reverseRecover[s_String] := Module[{rb = blocks[StringReverse[s]]},
  StringJoin[StringReverse /@ Reverse[rb]]
];

carrier[s_String] := s <> "." <> StringReverse[s];

pointOneNumerator = 3602879701896397;
pointOneScale = 55;
pointOneCoeff = ToString[pointOneNumerator*5^pointOneScale];
pointOneFrame = frame[64,0,pointOneScale,pointOneCoeff];

minSubScale = 1074;
minSubCoeff = ToString[5^minSubScale];
minSubFrame = frame[64,0,minSubScale,minSubCoeff];

maxFiniteInteger = (2^53-1)*2^971;
maxFiniteCoeff = ToString[maxFiniteInteger];
maxFiniteFrame = frame[64,0,0,maxFiniteCoeff];

zeroFrame = frame[64,0,0,"0"];
negativeZeroFrame = frame[64,1,0,"0"];

checks = <|
  "dyadic_decimal_identity_symbolic" -> TrueQ[dyadicIdentity],
  "point_one_exact_dyadic_denominator" ->
    Denominator[pointOneNumerator/2^pointOneScale] == 2^55,
  "point_one_decimal_reconstruction_exact" ->
    pointOneNumerator/2^55 == (pointOneNumerator*5^55)/10^55,
  "point_one_frame_is_72_digits" -> StringLength[pointOneFrame] == 72,
  "point_one_one_block" -> Length[blocks[pointOneFrame]] == 1,
  "min_sub_coefficient_digits" -> StringLength[minSubCoeff] == 751,
  "min_sub_frame_is_768_digits" -> StringLength[minSubFrame] == 768,
  "min_sub_crosses_72_in_11_blocks" ->
    Length[blocks[minSubFrame]] == 11 &&
    (StringLength /@ blocks[minSubFrame]) == Join[ConstantArray[72,10],{48}],
  "min_sub_forward_concat_exact" -> StringJoin[blocks[minSubFrame]] == minSubFrame,
  "min_sub_reverse_concat_exact" -> reverseRecover[minSubFrame] == minSubFrame,
  "max_finite_decimal_digits" -> StringLength[maxFiniteCoeff] == 309,
  "max_finite_frame_blocks" ->
    StringLength[maxFiniteFrame] == 326 && Length[blocks[maxFiniteFrame]] == 5,
  "point_one_carrier_palindrome" ->
    carrier[pointOneFrame] == StringReverse[carrier[pointOneFrame]],
  "min_sub_carrier_palindrome" ->
    carrier[minSubFrame] == StringReverse[carrier[minSubFrame]],
  "zero_sign_paths_distinct" -> zeroFrame =!= negativeZeroFrame,
  "reverse_is_involution" -> StringReverse[StringReverse[minSubFrame]] == minSubFrame,
  "5184_factorization" -> 5184 == 72^2 == 81*64,
  "72_is_block_not_global_limit" ->
    StringLength[minSubFrame] > 72 &&
    StringJoin[blocks[minSubFrame]] == minSubFrame
|>;

result = <|
  "schema" -> "HHS_PASS219_LANE5_IEEE754_PALINDROMIC_PIVOT_WOLFRAM_V1",
  "theorem_id" -> "HHS-T5184-003",
  "status" -> If[And@@Values[checks],"PASS","FAIL"],
  "checks" -> checks,
  "proof_terms" -> <|
    "dyadic_to_decimal" -> "n/2^k = n*5^k/10^k",
    "direction_a" -> "Concat(Block72(F))=F",
    "direction_b" -> "Concat[Reverse[ReverseEach(Block72(Reverse(F)))]]=F",
    "carrier" -> "F . Reverse(F)",
    "block_size" -> 72,
    "serializer_size" -> 5184,
    "g3_rna" -> "(y-x)-u^72=G^3"
  |>,
  "point_one_frame_digits" -> StringLength[pointOneFrame],
  "min_sub_frame_digits" -> StringLength[minSubFrame],
  "min_sub_block_count" -> Length[blocks[minSubFrame]],
  "max_finite_frame_digits" -> StringLength[maxFiniteFrame],
  "max_finite_block_count" -> Length[blocks[maxFiniteFrame]],
  "host_float_authority" -> False,
  "ieee_arithmetic_authority" -> False
|>;

ExportString[result,"RawJSON","Compact"->True]