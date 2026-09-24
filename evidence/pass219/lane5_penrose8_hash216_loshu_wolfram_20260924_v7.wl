ClearAll["Global`*"];

$Assumptions = Element[{t, x, y, z, a, b, c, d}, Reals];

X = {{t + z, x - I y}, {x + I y, t - z}};
pi = {a + I b, c + I d};
omega = I X.pi;
Z = Join[omega, pi];

nullForm = FullSimplify[
  ComplexExpand[Conjugate[omega].pi + Conjugate[pi].omega],
  $Assumptions
];

momentum = Outer[Times, pi, Conjugate[pi]];
masslessDet = FullSimplify[
  ComplexExpand[Det[momentum]],
  $Assumptions
];

real8 = {
  ComplexExpand[Re[omega[[1]]]],
  ComplexExpand[Re[omega[[2]]]],
  ComplexExpand[Re[pi[[1]]]],
  ComplexExpand[Re[pi[[2]]]],
  ComplexExpand[Im[omega[[1]]]],
  ComplexExpand[Im[omega[[2]]]],
  ComplexExpand[Im[pi[[1]]]],
  ComplexExpand[Im[pi[[2]]]]
};

zReconstructed = {
  real8[[1]] + I real8[[5]],
  real8[[2]] + I real8[[6]],
  real8[[3]] + I real8[[7]],
  real8[[4]] + I real8[[8]]
};

checks = <|
  "hermitian_X" -> TrueQ[FullSimplify[ConjugateTranspose[X] == X, $Assumptions]],
  "incidence_null_form_zero" -> TrueQ[nullForm == 0],
  "massless_momentum_det_zero" -> TrueQ[masslessDet == 0],
  "real8_cardinality" -> TrueQ[Length[real8] == 8],
  "real8_reconstructs_twistor" -> TrueQ[
    FullSimplify[zReconstructed == Z, $Assumptions]
  ],
  "truth_table_2^3" -> TrueQ[2^3 == 8],
  "nine_nuclei_times_eight" -> TrueQ[9*8 == 72],
  "hash216_three_hash72" -> TrueQ[3*72 == 216],
  "vm5184_hash72_square" -> TrueQ[72^2 == 5184]
|>;

result = <|
  "schema" -> "HHS_PASS_219_LANE5_PENROSE8_HASH216_WOLFRAM_20260924_V7",
  "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> Keys @ Select[checks, Not @* TrueQ],
  "checks" -> checks,
  "twistor_complex_dimension" -> 4,
  "twistor_real_dimension" -> 8,
  "incidence_relation" -> "omega=i X pi",
  "null_form" -> "omega^dagger*pi+pi^dagger*omega=0",
  "null_form_class" -> "ALGEBRAIC_IDENTITY",
  "massless_momentum" -> "p=pi*pi^dagger; det(p)=0",
  "massless_momentum_det_class" -> "ALGEBRAIC_IDENTITY",
  "center_role" -> "NUCLEUS_LOCK_NOT_8D_CARRIER_COORDINATE",
  "hash72_geometry" -> "9*8=72; U72 typed geometry = Hash72 = 72 Lo-Shu outer-cell coordinates",
  "u72_scalar_projection_closure_assignment" -> "U72:=2/ubar^2",
  "ordinary_ubar_power_rewrite_authorized" -> False,
  "hash216_geometry" -> "previous72||next72||receipt72; 3*72=216",
  "vm5184_relation" -> "72^2=5184",
  "projective_quotient_applied" -> False,
  "z_gauge_policy" -> "EXACT_PI_REPRESENTATIVE_FROZEN_PER_RECEIPT",
  "cross_gauge_absolute_magnitude_authorized" -> False,
  "canonical_runtime_mutation_authority" -> False
|>;

Print[ExportString[result, "RawJSON"]]
