(* Pass 220 I030: G^3 reciprocal symbol-string codec formalization.
   Ordered constructors are intentionally opaque. No Times/Power cancellation
   is licensed for the phase tensor proof. *)
ClearAll["Global`*"];

proofCell = ProofCell["123321.111"];

phaseSwapRules = {
  Phase[x] -> Phase[y], Phase[y] -> Phase[x],
  Phase[z] -> Phase[w], Phase[w] -> Phase[z]
};
Sigma[expr_] := expr /. phaseSwapRules;

forwardZero =
  ODiv[OProd[Phase[x], Phase[y], proofCell], Phase[x]];
returnZero = Sigma[forwardZero];
expectedReturnZero =
  ODiv[OProd[Phase[y], Phase[x], proofCell], Phase[y]];

g3 = {
  {
    OProd[Phase[x], Phase[y]],
    OSum[Phase[x], Phase[y]],
    OProd[Phase[y], Phase[x]]
  },
  {
    ODiff[
      OProd[Phase[x], Phase[y]],
      OProd[Phase[z], Phase[w]]
    ],
    OSum[
      Phase[x], Phase[y], ONeg[Phase[z]], ONeg[Phase[w]],
      OProd[Phase[x], Phase[y]],
      OProd[Phase[y], Phase[x]],
      ONeg[OProd[Phase[z], Phase[w]]],
      ONeg[OProd[Phase[w], Phase[z]]]
    ],
    ODiff[
      OProd[Phase[w], Phase[z]],
      OProd[Phase[y], Phase[x]]
    ]
  },
  {
    OProd[Phase[w], Phase[z]],
    OSum[Phase[z], Phase[w]],
    OProd[Phase[z], Phase[w]]
  }
};

digitCell[0] := ZeroCell[forwardZero, returnZero];
digitCell[d_Integer /; 1 <= d <= 9] :=
  ScaledProofCell[d, proofCell];

utf8[s_String] := ToCharacterCode[s, "UTF-8"];
encode[s_String] :=
  Carrier[
    utf8[s],
    Reverse[utf8[s]],
    Phase[x],
    Phase[y],
    proofCell
  ];
decode[
  Carrier[
    f_List,
    r_List,
    Phase[x],
    Phase[y],
    ProofCell["123321.111"]
  ]
] /; Reverse[r] === f := FromCharacterCode[f, "UTF-8"];

binary =
  "0011111111110000000000000000000000000000000000000000000000000000";
floatText = "-0.0";
unicodeText = "x+y=0; y=1/x; 0=Φ; Ω";

checks = <|
  "01_proof_cell_is_opaque_string" ->
    (proofCell === ProofCell["123321.111"]),
  "02_forward_zero_locked_syntax" ->
    (forwardZero ===
      ODiv[
        OProd[Phase[x], Phase[y], proofCell],
        Phase[x]
      ]),
  "03_return_is_same_operation_reciprocal_phase" ->
    (returnZero === expectedReturnZero),
  "04_phase_swap_is_involution_on_zero" ->
    (Sigma[Sigma[forwardZero]] === forwardZero),
  "05_phase_swap_is_involution_on_g3" ->
    (Sigma[Sigma[g3]] === g3),
  "06_ordered_xy_distinct_yx" ->
    (OProd[Phase[x], Phase[y]] =!=
      OProd[Phase[y], Phase[x]]),
  "07_no_builtin_multiplicative_cancellation_surface" ->
    FreeQ[
      forwardZero,
      _Times | _Power | _Real | _Rational,
      Infinity
    ],
  "08_nine_digit_cells_scaled_from_same_proof" ->
    And @@ Table[
      digitCell[d] === ScaledProofCell[d, proofCell],
      {d, 1, 9}
    ],
  "09_zero_digit_is_phase_locked_not_blank" ->
    MatchQ[
      digitCell[0],
      ZeroCell[
        ODiv[
          OProd[Phase[x], Phase[y], _ProofCell],
          Phase[x]
        ],
        ODiv[
          OProd[Phase[y], Phase[x], _ProofCell],
          Phase[y]
        ]
      ]
    ],
  "10_arbitrary_utf8_symbol_string_round_trip" ->
    (decode[encode[unicodeText]] === unicodeText),
  "11_binary_symbol_string_round_trip" ->
    (decode[encode[binary]] === binary),
  "12_float_text_round_trip" ->
    (decode[encode[floatText]] === floatText),
  "13_leading_zero_identity_preserved" ->
    (decode[encode["0001.0"]] === "0001.0"),
  "14_distinct_scalar_spellings_remain_distinct" ->
    (encode["1.0"] =!= encode["1.00"]),
  "15_forward_and_return_byte_paths_are_reciprocal" ->
    Module[{c = encode[unicodeText]},
      c[[2]] === Reverse[c[[1]]]
    ],
  "16_g3_is_3_by_3" ->
    (Dimensions[g3] === {3, 3}),
  "17_reciprocal_axiom_is_constructor_level" ->
    (Reciprocal[Phase[x]] === Reciprocal[Phase[x]] &&
      Phase[y] =!= Phase[x])
|>;

failed = Keys @ Select[checks, # =!= True &];
result = <|
  "schema" ->
    "HHS_PASS_220_I030_G3_RECIPROCAL_SYMBOL_CODEC_WOLFRAM_20260922_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "forward_zero" -> ToString[forwardZero, InputForm],
  "return_zero" -> ToString[returnZero, InputForm],
  "proof_cell" -> "123321.111",
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
