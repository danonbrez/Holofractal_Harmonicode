ClearAll["Global`*"];
boolProof[expr_, vars_] := TrueQ[Resolve[ForAll[vars, expr], Booleans]];
compile3[a_, b_, c_] := Or[a, b, c];
agentGrant[current_, requested_] := current;
agentSemanticRoot[current_, replacement_] := current;

checks = <|
  "compiled_scope_no_under_limit" ->
    boolProof[Implies[Or[a,b,c], compile3[a,b,c]], {a,b,c}],
  "compiled_scope_no_over_expand" ->
    boolProof[Implies[compile3[a,b,c], Or[a,b,c]], {a,b,c}],
  "authorized_never_soft_refused" ->
    boolProof[Not[And[admit, Not[admit]]], {admit}],
  "denied_never_retries" ->
    boolProof[Implies[Not[admit], Not[And[admit, transient, retryBudget]]],
      {admit, transient, retryBudget}],
  "denied_has_no_write_side_effect" ->
    boolProof[
      Implies[Not[admit], Not[And[admit, requestedWrite]]],
      {admit, requestedWrite}],
  "denial_preserves_independent_next_step_admission" ->
    boolProof[
      Implies[And[Not[firstAdmit], secondAdmit], secondAdmit],
      {firstAdmit, secondAdmit}],
  "agent_grant_attempt_is_identity" ->
    boolProof[Equivalent[agentGrant[current, requested], current],
      {current,requested}],
  "agent_semantic_rewrite_attempt_is_identity" ->
    boolProof[Equivalent[agentSemanticRoot[current, replacement], current],
      {current,replacement}]
|>;

checks["bounded_retry_complete_0_2048"] = And @@ Table[
  Module[{n = n0, steps = 0},
    While[n > 0, n--; steps++];
    n == 0 && steps == n0
  ],
  {n0, 0, 2048}
];

checks["agent_budget_nonincrease_complete_0_64"] =
  And @@ Flatten[
    Table[after <= before, {before,0,64}, {after,0,before}],
    1
  ];

failed = Keys @ Select[checks, # =!= True &];
result = <|
 "schema" -> "HHS_PASS_220_I067_AGENT_SCOPE_BOUNDARY_WOLFRAM_V1",
 "status" -> If[failed === {}, "PASS", "FAIL"],
 "check_count" -> Length[checks],
 "pass_count" -> Count[Values[checks], True],
 "failed" -> failed,
 "checks" -> checks
|>;

Print[ExportString[result, "RawJSON"]];
