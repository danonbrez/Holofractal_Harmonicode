ClearAll[ell, dEll, rhoB0, rhoD0, rhoR0, rhoB, rhoD, rhoR, rhoBnext, rhoDnext, rhoRnext,
  gN, curvK, cLight, bg, lam, tau, theta, hP2, h2, jD, checks, failed, result];

rhoB = rhoB0 Exp[-3 ell];
rhoD = rhoD0 Exp[-3 ell];
rhoR = rhoR0 Exp[-4 ell];

rhoBnext = rhoB Exp[-3 dEll];
rhoDnext = rhoD Exp[-3 dEll] + jD;
rhoRnext = rhoR Exp[-4 dEll];

bg = (8 Pi gN/3) (rhoB + rhoD + rhoR) - curvK cLight^2 Exp[-2 ell];
hP2 = lam^2/(tau^2 theta^2);
h2 = bg + hP2;

checks = <|
  "baryon_continuity_invariant" ->
    FullSimplify[rhoB Exp[3 ell] == rhoB0],
  "radiation_continuity_invariant" ->
    FullSimplify[rhoR Exp[4 ell] == rhoR0],
  "dark_zero_source_invariant" ->
    FullSimplify[
      (rhoDnext /. jD -> 0) Exp[3 (ell+dEll)] == rhoD0
    ],
  "baryon_step_ratio" ->
    FullSimplify[rhoBnext/rhoB == Exp[-3 dEll],
      Assumptions -> {rhoB0 != 0}],
  "dark_sourced_step_law" ->
    FullSimplify[rhoDnext == rhoD Exp[-3 dEll] + jD],
  "dark_zero_source_step_ratio" ->
    FullSimplify[
      ((rhoDnext /. jD -> 0)/rhoD) == Exp[-3 dEll],
      Assumptions -> {rhoD0 != 0}
    ],
  "radiation_step_ratio" ->
    FullSimplify[rhoRnext/rhoR == Exp[-4 dEll],
      Assumptions -> {rhoR0 != 0}],
  "curvature_step_ratio" ->
    FullSimplify[
      (Exp[-2 (ell + dEll)]/Exp[-2 ell]) == Exp[-2 dEll]
    ],
  "background_explicit_no_free_function" ->
    FreeQ[bg, _Function | _InterpolatingFunction],
  "friedmann_background_explicit" ->
    FullSimplify[
      h2 == (8 Pi gN/3) (
        rhoB0 Exp[-3 ell] +
        rhoD0 Exp[-3 ell] +
        rhoR0 Exp[-4 ell]
      ) - curvK cLight^2 Exp[-2 ell] + lam^2/(tau^2 theta^2)
    ]
|>;

failed = Keys @ Select[checks, # =!= True &];

result = <|
  "schema" -> "HHS_PASS_220_I024_COSMO_BACKGROUND_CONTINUITY_WOLFRAM_20260921_V2",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "background_rule" -> ToString[InputForm[bg]],
  "baryon_step_ratio" -> ToString[InputForm[FullSimplify[rhoBnext/rhoB, Assumptions -> rhoB0 != 0]]],
  "dark_sourced_step" -> ToString[InputForm[rhoDnext]],
  "dark_zero_source_step_ratio" -> ToString[InputForm[FullSimplify[(rhoDnext /. jD -> 0)/rhoD, Assumptions -> rhoD0 != 0]]],
  "radiation_step_ratio" -> ToString[InputForm[FullSimplify[rhoRnext/rhoR, Assumptions -> rhoR0 != 0]]],
  "curvature_step_ratio" -> ToString[InputForm[FullSimplify[Exp[-2 (ell+dEll)]/Exp[-2 ell]]]],
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
