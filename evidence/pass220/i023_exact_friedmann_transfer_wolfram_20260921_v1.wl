ClearAll[tau, theta, lambda, b, hP, h, dt, ell, ellNext, aRatio, c0, dcStep, dh, zeta, checks, failed, result, g72Held, x];

dt = tau theta;
hP = lambda/(tau theta);
h = Sqrt[b + hP^2];
ellNext = ell + h dt;
aRatio = Exp[h dt];
zeta = -h dt;
dh = c0/h;
dcStep = c0 Exp[-ell] (1 - Exp[-h dt])/h;
g72Held = Inactive[Power][2, Rational[1,72]];

phaseOnlyIncrement = FullSimplify[
  (h dt) /. b -> 0,
  Assumptions -> {tau > 0, theta > 0, lambda > 0}
];

phaseOnlyScaleRatio = FullSimplify[
  aRatio /. b -> 0,
  Assumptions -> {tau > 0, theta > 0, lambda > 0}
];

phaseOnlyRedshiftLogStep = FullSimplify[
  zeta /. b -> 0,
  Assumptions -> {tau > 0, theta > 0, lambda > 0}
];

distanceLimit = Quiet @ FullSimplify[
  Limit[c0 Exp[-ell] (1 - Exp[-x dt])/x, x -> 0],
  Assumptions -> {tau > 0, theta > 0}
];

checks = <|
  "phase_hubble_definition" -> (hP === lambda/(tau theta)),
  "egress_time_definition" -> (dt === tau theta),
  "zoh_log_scale_update" -> (ellNext === ell + h dt),
  "phase_only_log_scale_increment_tau_free" -> (phaseOnlyIncrement === lambda),
  "phase_only_scale_ratio_tau_free" -> (phaseOnlyScaleRatio === Exp[lambda]),
  "phase_only_redshift_log_step_tau_free" -> (phaseOnlyRedshiftLogStep === -lambda),
  "exact_comoving_zoh_limit" -> (distanceLimit === c0 Exp[-ell] tau theta),
  "hubble_distance_symbolic" -> (dh === c0/h),
  "g72_remains_inactive_symbolic" -> (Head[g72Held] === Inactive[Power])
|>;

failed = Keys @ Select[checks, # =!= True &];

result = <|
  "schema" -> "HHS_PASS_220_I023_COSMO_FRIEDMANN_TRANSFER_WOLFRAM_20260921_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "phase_only_log_scale_increment" -> ToString[InputForm[phaseOnlyIncrement]],
  "phase_only_scale_ratio" -> ToString[InputForm[phaseOnlyScaleRatio]],
  "phase_only_redshift_log_step" -> ToString[InputForm[phaseOnlyRedshiftLogStep]],
  "exact_comoving_interval" -> ToString[InputForm[dcStep]],
  "zero_hubble_limit" -> ToString[InputForm[distanceLimit]],
  "g72_representation" -> ToString[InputForm[g72Held]],
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
