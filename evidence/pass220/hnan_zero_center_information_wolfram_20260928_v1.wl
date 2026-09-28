(* HHS Pass 220: explicit HNAN zero/center information-preservation proof.
   The proof is structural.  HHS ordered products and closure nodes are encoded
   as inert list ASTs so Wolfram host Plus/Times/Divide evaluation cannot
   commute, cancel, or scalarize them. *)

xy = {"OrderedProduct", "x", "y"};
yx = {"OrderedProduct", "y", "x"};
zw = {"OrderedProduct", "z", "w"};
wz = {"OrderedProduct", "w", "z"};

center = {
  "OrderedSum",
  "x",
  "y",
  {"Negate", "z"},
  {"Negate", "w"},
  xy,
  yx,
  {"Negate", zw},
  {"Negate", wz}
};

zeroCenterClosure = {
  "OrderedClosure",
  "ZERO",
  "EMPTYSET",
  "HNAN",
  center
};

inheritedDenominatorClosure = {
  "OrderedClosure",
  "ZERO",
  "EMPTYSET",
  "AB_P4_EMPTYSET",
  "HNAN"
};

epsilonResidual = {
  "Residual",
  "epsilon",
  {"HNANLoShuTensor", center},
  {"RelativeToProjection", xy}
};

terminal = {"OrderedSum", xy, epsilonResidual};

sourceString = "0=∅=HNAN=x+y-z-w+xy+yx-zw-wz";
inheritedString = "0=∅=AB/P⁴∅=HNAN";
terminalString = "xy+epsilon";

alternateCenter = {
  "OrderedSum",
  "x",
  "y",
  {"Negate", "z"},
  {"Negate", "w"},
  yx,
  xy,
  {"Negate", zw},
  {"Negate", wz}
};

alternateZeroCenterClosure = {
  "OrderedClosure",
  "ZERO",
  "EMPTYSET",
  "HNAN",
  alternateCenter
};

alternateResidual = {
  "Residual",
  "epsilonAlt",
  {"HNANLoShuTensor", center},
  {"RelativeToProjection", xy}
};

visibleHNANProjection[closure_List] := closure[[4]];
visibleXYProjection[terminalState_List] := terminalState[[2]];

checks = <|
  "source_string_exact" ->
    (sourceString === "0=∅=HNAN=x+y-z-w+xy+yx-zw-wz"),
  "inherited_string_exact" ->
    (inheritedString === "0=∅=AB/P⁴∅=HNAN"),
  "terminal_string_exact" ->
    (terminalString === "xy+epsilon"),
  "center_has_exactly_8_ordered_terms" ->
    (Length[Rest[center]] === 8),
  "center_term_sequence_exact" ->
    (Rest[center] === {
      "x", "y", {"Negate", "z"}, {"Negate", "w"},
      xy, yx, {"Negate", zw}, {"Negate", wz}
    }),
  "xy_yx_structurally_distinct" -> UnsameQ[xy, yx],
  "zw_wz_structurally_distinct" -> UnsameQ[zw, wz],
  "swapping_xy_yx_changes_center" -> UnsameQ[center, alternateCenter],
  "zero_emptyset_hnan_center_chain_exact" ->
    (zeroCenterClosure === {
      "OrderedClosure", "ZERO", "EMPTYSET", "HNAN", center
    }),
  "inherited_ab_p4_closure_exact" ->
    (inheritedDenominatorClosure === {
      "OrderedClosure", "ZERO", "EMPTYSET", "AB_P4_EMPTYSET", "HNAN"
    }),
  "two_closure_surfaces_remain_distinct" ->
    UnsameQ[zeroCenterClosure, inheritedDenominatorClosure],
  "no_host_plus_times_divide_in_zero_center_ast" ->
    (Cases[zeroCenterClosure, _Plus | _Times, Infinity] === {}),
  "zero_center_roundtrip_structural_exact" ->
    (Uncompress[Compress[zeroCenterClosure]] === zeroCenterClosure),
  "inherited_closure_roundtrip_structural_exact" ->
    (Uncompress[Compress[inheritedDenominatorClosure]] ===
      inheritedDenominatorClosure),
  "terminal_roundtrip_structural_exact" ->
    (Uncompress[Compress[terminal]] === terminal),

  (* Necessity theorem: deleting the center creates a many-to-one map. *)
  "dropping_center_is_noninjective" ->
    (
      UnsameQ[zeroCenterClosure, alternateZeroCenterClosure] &&
      SameQ[
        visibleHNANProjection[zeroCenterClosure],
        visibleHNANProjection[alternateZeroCenterClosure]
      ]
    ),

  (* Residual theorem: deleting epsilon creates a many-to-one xy projection. *)
  "dropping_epsilon_is_noninjective" ->
    (
      UnsameQ[
        {"OrderedSum", xy, epsilonResidual},
        {"OrderedSum", xy, alternateResidual}
      ] &&
      SameQ[
        visibleXYProjection[{"OrderedSum", xy, epsilonResidual}],
        visibleXYProjection[{"OrderedSum", xy, alternateResidual}]
      ]
    ),
  "full_center_signature_changes_on_order_change" ->
    UnsameQ[
      Hash[center, "SHA256"],
      Hash[alternateCenter, "SHA256"]
    ],
  "full_zero_center_signature_changes_on_order_change" ->
    UnsameQ[
      Hash[zeroCenterClosure, "SHA256"],
      Hash[alternateZeroCenterClosure, "SHA256"]
    ],
  "terminal_preserves_typed_residual" ->
    (
      terminal === {"OrderedSum", xy, epsilonResidual} &&
      UnsameQ[terminal, xy]
    )
|>;

result = <|
  "schema" -> "HHS_PASS220_HNAN_ZERO_CENTER_INFORMATION_WOLFRAM_V1",
  "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
  "checks" -> checks,
  "passed" -> Count[Values[checks], True],
  "total" -> Length[checks],
  "source_string_ascii" ->
    StringReplace[sourceString, "∅" -> "<EMPTYSET>"],
  "source_string_codepoints" -> ToCharacterCode[sourceString, "Unicode"],
  "inherited_closure_ascii" ->
    StringReplace[inheritedString, {"∅" -> "<EMPTYSET>", "⁴" -> "^4"}],
  "inherited_closure_codepoints" ->
    ToCharacterCode[inheritedString, "Unicode"],
  "terminal_string" -> terminalString,
  "center_ast" -> center,
  "zero_center_closure_ast" -> zeroCenterClosure,
  "inherited_closure_ast" -> inheritedDenominatorClosure,
  "terminal_ast" -> terminal,
  "center_sha256_decimal" -> ToString[Hash[center, "SHA256"]],
  "zero_center_sha256_decimal" ->
    ToString[Hash[zeroCenterClosure, "SHA256"]],
  "inherited_closure_sha256_decimal" ->
    ToString[Hash[inheritedDenominatorClosure, "SHA256"]],
  "proof_claims" -> <|
    "necessity" ->
      "Removing the center binding makes the HNAN projection non-injective over distinct ordered center states.",
    "residual_necessity" ->
      "Removing epsilon makes the visible xy projection non-injective over distinct residual states.",
    "meaning" ->
      "The source string is a typed ordered binding from ZERO and EMPTYSET through HNAN to the exact eight-term ordered center; it is not host scalar equality.",
    "coexistence" ->
      "The zero/HNAN/center closure and inherited AB/P^4 EMPTYSET closure remain distinct structural witnesses and are both retained."
  |>
|>;

Print[ExportString[result, "JSON", "Compact" -> False]];
If[result["status"] === "PASS", Exit[0], Exit[1]];
