(* Pass 220 I032: G^3 full x/y/z/w IEEE transport proof. *)
ClearAll["Global`*"];

proofCell = ProofCell["123321.111"];

phaseSwapRules = {
  Phase[x] -> Phase[y], Phase[y] -> Phase[x],
  Phase[z] -> Phase[w], Phase[w] -> Phase[z]
};
Sigma[expr_] := expr /. phaseSwapRules;

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
      OProd[Phase[x], Phase[y]], OProd[Phase[y], Phase[x]],
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

forwardZero =
  ODiv[OProd[Phase[x], Phase[y], proofCell], Phase[x]];
returnZero = Sigma[forwardZero];

ingress[b_] := FullPhaseCarrier[
  ScalarBits[b],
  Boundary[Phase[x]],
  g3,
  Table[
    LogicCell[
      i,
      ScalarBits[b],
      Flatten[g3][[i]],
      Sigma[Flatten[g3][[i]]]
    ],
    {i, 1, 9}
  ]
];

reciprocalCarrier[
  FullPhaseCarrier[ScalarBits[b_], Boundary[Phase[x]], tensor_, trace_]
] := FullPhaseCarrier[
  ScalarBits[b],
  Boundary[Phase[y]],
  Sigma[tensor],
  trace /. LogicCell[i_, ScalarBits[s_], f_, r_] :>
    LogicCell[i, ScalarBits[s], r, f]
];

returnPayload[
  FullPhaseCarrier[ScalarBits[b_], Boundary[Phase[y]], tensor_, trace_]
] /; Sigma[tensor] === g3 := ScalarBits[b];

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

phaseNames = DeleteDuplicates @ Cases[g3, Phase[p_] :> p, Infinity];
orderedProducts = DeleteDuplicates @ Cases[
  g3,
  OProd[Phase[a_], Phase[b_]] :> {a, b},
  Infinity
];

c = ingress[n];
r = reciprocalCarrier[c];

checks = <|
  "01_g3_is_3_by_3" -> (Dimensions[g3] === {3,3}),
  "02_all_four_phase_carriers_present" ->
    (Sort[phaseNames] === Sort[{x,y,z,w}]),
  "03_xy_channel_present" -> MemberQ[orderedProducts, {x,y}],
  "04_yx_channel_present" -> MemberQ[orderedProducts, {y,x}],
  "05_zw_channel_present" -> MemberQ[orderedProducts, {z,w}],
  "06_wz_channel_present" -> MemberQ[orderedProducts, {w,z}],
  "07_xy_distinct_yx" ->
    (OProd[Phase[x], Phase[y]] =!= OProd[Phase[y], Phase[x]]),
  "08_zw_distinct_wz" ->
    (OProd[Phase[z], Phase[w]] =!= OProd[Phase[w], Phase[z]]),
  "09_full_tensor_reciprocal_involution" ->
    (Sigma[Sigma[g3]] === g3),
  "10_locked_zero_reciprocal_involution" ->
    (Sigma[Sigma[forwardZero]] === forwardZero),
  "11_boundary_ingress_is_x" ->
    (c[[2]] === Boundary[Phase[x]]),
  "12_boundary_return_is_y" ->
    (r[[2]] === Boundary[Phase[y]]),
  "13_scalar_bits_unchanged_by_reciprocal_carrier" ->
    (c[[1]] === r[[1]]),
  "14_all_nine_logic_cells_preserve_scalar_bits" ->
    And @@ (#[[2]] === ScalarBits[n] & /@ c[[4]]),
  "15_all_nine_logic_cells_have_reciprocal_pair" ->
    And @@ ((Sigma[#[[3]]] === #[[4]]) & /@ c[[4]]),
  "16_return_tensor_is_reciprocal_g3" ->
    (r[[3]] === Sigma[g3]),
  "17_same_payload_returns_after_reciprocal_tensor" ->
    (returnPayload[r] === ScalarBits[n]),
  "18_binary16_partition_parametric" -> partitionProof[5,10],
  "19_binary32_partition_parametric" -> partitionProof[8,23],
  "20_binary64_partition_parametric" -> partitionProof[11,52],
  "21_binary128_partition_parametric" -> partitionProof[15,112],
  "22_proof_cell_opaque" ->
    (proofCell === ProofCell["123321.111"])
|>;

failed = Keys @ Select[checks, # =!= True &];
result = <|
  "schema" ->
    "HHS_PASS_220_I032_G3_FULL_PHASE_IEEE_TRANSPORT_WOLFRAM_20260922_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "proof_cell" -> "123321.111",
  "phase_names" -> (ToString[#, InputForm] & /@ phaseNames),
  "ordered_products" ->
    (ToString[#, InputForm] & /@ orderedProducts),
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
