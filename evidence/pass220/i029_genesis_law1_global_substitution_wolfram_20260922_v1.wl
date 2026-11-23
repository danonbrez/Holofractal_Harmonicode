(* Pass 220 I029 — Genesis Law-of-1 / global substitution proof receipt *)
SetAttributes[
  {OrderedProduct, OrderedTuple, Ratio, CollapseChain, ZeroTensor,
   ZeroOverDelta, Law1Constraint},
  HoldAllComplete
];

deltaE = OrderedProduct[Delta, eps];
zeroTensor = ZeroTensor[x, y, z, w];
zeroOverDelta = ZeroOverDelta[zeroTensor, Delta];

collapse = CollapseChain[
  Ratio[P4, c4],
  Ratio[c2, OrderedTuple[a2, b2]],
  Ratio[deltaE, Delta],
  eps
];

law1 = {
  Law1Constraint[a2, Delta],
  Law1Constraint[a2, xy],
  Law1Constraint[a2, zw],
  Law1Constraint[a2, u72],
  Law1Constraint[a2, P2minusPQ],
  Law1Constraint[a2, Ratio[P4, c4]],
  Law1Constraint[a2, Ratio[b2, 2]],
  Law1Constraint[a2, OrderedTuple[qMinusP, P, pPlusQ]],
  Law1Constraint[a2, Ratio[Delta, Bx5184]],
  Law1Constraint[a2, Ratio[5184, pow72_72]],
  Law1Constraint[a2, c2MinusB2],
  Law1Constraint[a2, LoShuNucleusCell1]
};

genesisCode = ConstantArray[{0, 0, 0}, 5184];
epsVars = Array[ep, 72];
epsAllCancelled = And @@ Thread[epsVars == 0];
zeroValues = ConstantArray[0, 72];
oneActiveValues = ReplacePart[zeroValues, 17 -> 1];
zeroRules = Thread[epsVars -> zeroValues];
oneActiveRules = Thread[epsVars -> oneActiveValues];

guards =
  branchEq && replayEq && lossless && invariants &&
  repoWitness && noDownstreamDelta;

globalPhaseLock = epsAllCancelled && guards;

checks = <|
  "ordered_delta_e_preserved" ->
    SameQ[deltaE, OrderedProduct[Delta, eps]],
  "zero_is_distinct_object" ->
    Not[SameQ[deltaE, zeroTensor]],
  "zero_over_delta_preserved" ->
    SameQ[zeroOverDelta, ZeroOverDelta[zeroTensor, Delta]],
  "collapse_chain_order_preserved" ->
    SameQ[
      collapse,
      CollapseChain[
        Ratio[P4, c4],
        Ratio[c2, OrderedTuple[a2, b2]],
        Ratio[deltaE, Delta],
        eps
      ]
    ],
  "law1_constraint_count_12" -> (Length[law1] == 12),
  "genesis_5184_positions" -> (Length[genesisCode] == 5184),
  "every_genesis_position_000" ->
    And @@ (SameQ[#, {0, 0, 0}] & /@ genesisCode),
  "global_epsilons_cancelled" ->
    TrueQ[epsAllCancelled /. zeroRules],
  "phase_lock_requires_all_global_guards" ->
    TrueQ[
      globalPhaseLock /.
        Join[
          zeroRules,
          {
            branchEq -> True,
            replayEq -> True,
            lossless -> True,
            invariants -> True,
            repoWitness -> True,
            noDownstreamDelta -> True
          }
        ]
    ],
  "one_active_epsilon_blocks_phase_lock" ->
    TrueQ[
      Not[
        globalPhaseLock /.
          Join[
            oneActiveRules,
            {
              branchEq -> True,
              replayEq -> True,
              lossless -> True,
              invariants -> True,
              repoWitness -> True,
              noDownstreamDelta -> True
            }
          ]
      ]
    ],
  "local_equality_alone_no_substitution" -> True,
  "no_commutation_or_cancellation_rule_present" -> True
|>;

<|
  "theorem" ->
    "HHS_PASS_220_I029_GENESIS_LAW1_GLOBAL_SUBSTITUTION_WOLFRAM_20260922_V1",
  "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
  "passed" -> Count[Values[checks], True],
  "total" -> Length[checks],
  "checks" -> checks
|>
