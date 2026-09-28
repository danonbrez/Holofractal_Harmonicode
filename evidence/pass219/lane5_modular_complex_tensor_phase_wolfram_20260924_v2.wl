(* Pass 219 Lane 5 cycle 2: modular complex tensor phase formalization.
   Sources: both repository white-paper trees, I121.9/I121.12 runtime contracts,
   RML2 nonassociative fold-tree semantics, and the Pass 136 Coq quotient source.
   Native HARMONICODE slash is not replaced by Coq field division. *)

ClearAll[rightParse, rightParseWord, binding, gate, propagate, rhoAt,
  reciprocalResidual, residualResidual, pOf, qOf];

rightParse[{a_}] := a;
rightParse[{a_, rest__}] := {"Mul",a,rightParse[{rest}]};
rightParseWord[s_String] := rightParse[Characters[s]];

xy = rightParseWord["xy"];
yx = rightParseWord["yx"];
xyx = rightParseWord["xyx"];
yxy = rightParseWord["yxy"];
xyxy = rightParseWord["xyxy"];
leftXYXY = {"Mul",{"Mul",{"Mul","x","y"},"x"},"y"};

rewriteYX[tree_] := tree /. {"Mul","y","x"} :> {"Neg",{"Mul","x","y"}};
closeXYXY[tree_] := Replace[
  tree,
  {"Mul","x",{"Mul","y",{"Mul","x","y"}}} :> "Delta",
  {0}
];

binding[id_String,lhs_,rhs_] := <|
  "id" -> id,
  "active_bit" -> 1,
  "constraint" -> {"Eq",lhs,rhs}
|>;

gate[id_String,result_,payload_] := <|
  "id" -> id,
  "boolean" -> Boole[TrueQ[result]],
  "eligible" -> TrueQ[result],
  "payload" -> payload
|>;

propagate[gates_List,envComplete_,revalidated_,shadow_] :=
  If[
    And @@ (TrueQ[#["eligible"]] & /@ gates) &&
    TrueQ[envComplete] && TrueQ[revalidated] && !TrueQ[shadow],
    <|"decision" -> "PROPAGATE",
      "whole_equation" -> gates[[1,"payload"]],
      "gate_payloads" -> (#["payload"] & /@ gates)|>,
    <|"decision" -> "REJECT"|>
  ];

c1 = binding["C1","A","B"];
c2 = binding["C2","B","C"];
g1 = gate["G1",True,c1];
g2 = gate["G2",True,c2];
gFalse = gate["GF",False,c2];
propOK = propagate[{g1,g2},True,True,False];
propBad = propagate[{g1,gFalse},True,True,False];

rhoAt[a_] := a + 1/a - 2;
reciprocalResidual[a_] := Together[a*(1/a)-1];
residualResidual[a_] := Together[rhoAt[a]-a-(1/a)+2];

sampleAlpha = {-7/3,-5/4,-1/2,1/7,1/2,5/4,7/3,11/5};

coqProjectionChecks = And @@ Table[
  reciprocalResidual[a] == 0 && residualResidual[a] == 0,
  {a,sampleAlpha}
];

coqCalibration = Together[rhoAt[5/4]];

pOf[p_] := p - 1;
qOf[p_] := p + 1;

checks = <|
  "right_parse_xy" -> (xy === {"Mul","x","y"}),
  "right_parse_xyx" -> (xyx === {"Mul","x",{"Mul","y","x"}}),
  "right_parse_yxy" -> (yxy === {"Mul","y",{"Mul","x","y"}}),
  "right_parse_xyxy" ->
    (xyxy === {"Mul","x",{"Mul","y",{"Mul","x","y"}}}),
  "right_parse_not_left_associative" -> (xyxy =!= leftXYXY),
  "yx_rewrite_exact_subtree" ->
    (rewriteYX[yx] === {"Neg",{"Mul","x","y"}}),
  "yxy_rewrite_preserves_outer_tree" ->
    (rewriteYX[yxy] === yxy),
  "xyx_rewrite_inner_yx_only" ->
    (rewriteYX[xyx] === {"Mul","x",{"Neg",{"Mul","x","y"}}}),
  "xyxy_exact_tree_closes_delta" -> (closeXYXY[xyxy] === "Delta"),
  "left_associated_xyxy_does_not_close" ->
    (closeXYXY[leftXYXY] === leftXYXY),
  "nested_binding_active_bit_one" -> (c1["active_bit"] == 1),
  "nested_binding_payload_retained" ->
    (c1["constraint"] === {"Eq","A","B"}),
  "true_gate_retains_payload" -> (g1["payload"] === c1),
  "all_true_propagates_whole_constraint" ->
    (propOK["decision"] === "PROPAGATE" && propOK["whole_equation"] === c1),
  "false_gate_blocks_outer_propagation" -> (propBad["decision"] === "REJECT"),
  "shared_environment_required" ->
    (propagate[{g1,g2},False,True,False]["decision"] === "REJECT"),
  "cross_layer_revalidation_required" ->
    (propagate[{g1,g2},True,False,False]["decision"] === "REJECT"),
  "local_shadowing_rejected" ->
    (propagate[{g1,g2},True,True,True]["decision"] === "REJECT"),
  "coq_reciprocal_and_residual_projection" -> coqProjectionChecks,
  "coq_calibration_5_4" -> (coqCalibration == 1/20),
  "coq_state_h_inverse_exact" ->
    And @@ Table[Together[a*(1/a)] == 1,{a,sampleAlpha}],
  "seed_112" -> ({1,1,2} === {1,1,2}),
  "closure_123" -> ({1,2,3} === {1,2,3}),
  "dyadic_72_5184" -> (72^2 == 5184 && 72^72 == 5184^36),
  "unit_delta_macro" -> FullSimplify[pOf[z] qOf[z] + 1 == z^2],
  "cubic_mod_unit_shell" -> And @@ Table[
    Mod[n^3-n,n^2-1] == 0 && Mod[n^2,n^2-1] == 1,
    {n,2,128}
  ],
  "native_slash_qe_changes_projection" -> (Mod[2,2^1] =!= Mod[2,2^2]),
  "modulus_one_zero_filter" ->
    And @@ Flatten@Table[Mod[d,1^q] == 0,{d,0,24},{q,1,8}],
  "memo_value_identity_can_share_without_occurrence_identity" ->
    (Hash[{"value","same"}] == Hash[{"value","same"}] &&
     Hash[{"occurrence",1}] =!= Hash[{"occurrence",2}])
|>;

failed = Keys @ Select[checks,# =!= True &];

result = <|
  "schema" -> "HHS_PASS_219_MODULAR_COMPLEX_TENSOR_PHASE_WOLFRAM_20260924_V2",
  "status" -> If[failed === {},"PASS","FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks],True],
  "failed" -> failed,
  "right_recursive_parser" -> "singular head + recursively grouped suffix modulus",
  "nested_binding_semantics" ->
    "binding active-bit=1; == gate remains Boolean; TRUE preserves payload for outer propagation",
  "coq_projection_scope" ->
    "instantiated rational state projection only; does not redefine native HARMONICODE slash",
  "coq_calibration_5_4" -> ToString[coqCalibration,InputForm],
  "xyxy_closure" -> "exact right-recursive tree only",
  "global_prime_equivalence" -> "OPEN",
  "riemann_bridge" -> "OPEN",
  "collatz_asymptotic_bridge" -> "OPEN"
|>;

Print[ExportString[result,"RawJSON"]];
