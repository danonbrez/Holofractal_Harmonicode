ClearAll[sigma, n, tau, theta, thetaPrev, lambda, lambdaPrev, hp, hpPrev, dotHp, wp, variableExpected, g72Held, checks, failed, result];

sigma[k_Integer] := Replace[Mod[8 + 16 k, 72], 0 -> 72];
phaseOrbit = Table[sigma[k], {k, 0, 8}];

hp = lambda/(tau theta);
hpPrev = lambdaPrev/(tau thetaPrev);
dotHp = 2 (hp - hpPrev)/(tau (theta + thetaPrev));
wp = -1 - (2/3) dotHp/hp^2;

variableExpected = -1 + (4 theta (theta - thetaPrev))/(3 lambda thetaPrev (theta + thetaPrev));
g72Held = Inactive[Power][2, Rational[1,72]];

checks = <|
  "phase_orbit_exact" -> (phaseOrbit === {8,24,40,56,72,16,32,48,64}),
  "phase_orbit_period_nine" -> And @@ Table[sigma[k + 9] == sigma[k], {k,0,71}],
  "phase_orbit_nine_distinct" -> (Length[DeleteDuplicates[phaseOrbit]] == 9),
  "constant_cadence_dot_h_zero" -> FullSimplify[
      dotHp /. {lambdaPrev -> lambda, thetaPrev -> theta},
      Assumptions -> {tau != 0, theta != 0}
    ] === 0,
  "constant_cadence_w_minus_one" -> FullSimplify[
      wp /. {lambdaPrev -> lambda, thetaPrev -> theta},
      Assumptions -> {tau != 0, theta != 0, lambda != 0}
    ] === -1,
  "variable_cadence_closed_form" -> FullSimplify[
      (wp /. lambdaPrev -> lambda) == variableExpected,
      Assumptions -> {tau != 0, theta != 0, thetaPrev != 0, lambda != 0}
    ],
  "variable_cadence_tau_invariant" -> FreeQ[
      FullSimplify[
        wp /. lambdaPrev -> lambda,
        Assumptions -> {tau != 0, theta != 0, thetaPrev != 0, lambda != 0}
      ],
      tau
    ],
  "g72_remains_inactive_symbolic" -> (Head[g72Held] === Inactive[Power])
|>;

failed = Keys @ Select[checks, # =!= True &];
result = <|
  "schema" -> "HHS_PASS_220_I022_COSMO_CLOCK_WOLFRAM_20260921_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "phase_orbit_lift72" -> phaseOrbit,
  "constant_cadence_dot_h" -> ToString[InputForm @ FullSimplify[
      dotHp /. {lambdaPrev -> lambda, thetaPrev -> theta},
      Assumptions -> {tau != 0, theta != 0}
  ]],
  "constant_cadence_w" -> ToString[InputForm @ FullSimplify[
      wp /. {lambdaPrev -> lambda, thetaPrev -> theta},
      Assumptions -> {tau != 0, theta != 0, lambda != 0}
  ]],
  "variable_cadence_w_constant_increment" -> ToString[InputForm @ FullSimplify[
      wp /. lambdaPrev -> lambda,
      Assumptions -> {tau != 0, theta != 0, thetaPrev != 0, lambda != 0}
  ]],
  "g72_representation" -> ToString[InputForm[g72Held]],
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
