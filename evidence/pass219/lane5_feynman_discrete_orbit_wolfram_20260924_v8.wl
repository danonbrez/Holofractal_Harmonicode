ClearAll["Global`*"];

n9 = 9;
U9 = Table[
  If[j == Mod[i - 2, n9] + 1, 1, 0],
  {i, n9},
  {j, n9}
];

powers = Table[MatrixPower[U9, n], {n, 0, 18}];
nonzeroCounts = Count[Flatten[#], _?(# != 0 &)] & /@ powers;
rowColPermutation = And @@ Table[
  And[
    Total[MatrixPower[U9, n], {2}] == ConstantArray[1, n9],
    Total[MatrixPower[U9, n], {1}] == ConstantArray[1, n9]
  ],
  {n, 0, 18}
];

partitionTrace = Table[Tr[MatrixPower[U9, n]], {n, 1, 9}];

F2 = q P + h (P^2/(2 m) + V[q]);
pF = D[F2, q];
QF = D[F2, P];
Psol = p - h V'[q];
Qcarried = FullSimplify[QF /. P -> Psol];

Sstep = P (Q - q) - h (P^2/(2 m) + V[q]);
stationaryP = D[Sstep, P];
pBoundary = -D[Sstep, q];
PBoundary = D[Sstep, Q];

pOld = P + h V'[q];
Qexplicit = q + h pOld/m;
crossMismatch = FullSimplify[D[Qexplicit, q] - D[pOld, P]];

EkNative = u72*(2 Pi k/9)/(tau theta);
EkScalar = FullSimplify[EkNative /. u72 -> 2/ubar^2];

checks = <|
  "r1_all_powers_have_9_nonzero_entries" ->
    TrueQ[nonzeroCounts == ConstantArray[9, 19]],
  "r1_all_powers_permutation" ->
    TrueQ[rowColPermutation],
  "r3_trace_n1_zero" ->
    TrueQ[partitionTrace[[1]] == 0],
  "r3_trace_n9_nine" ->
    TrueQ[partitionTrace[[9]] == 9],
  "r3_trace_exact_cycle" ->
    TrueQ[partitionTrace == {0,0,0,0,0,0,0,0,9}],
  "r2_F2_kick_relation" ->
    TrueQ[FullSimplify[pF == P + h V'[q]]],
  "r2_F2_drift_relation" ->
    TrueQ[FullSimplify[QF == q + h P/m]],
  "r2_carried_map_after_elimination" ->
    TrueQ[FullSimplify[
      Qcarried == q + h (p - h V'[q])/m
    ]],
  "r2_discrete_action_stationarity" ->
    TrueQ[
      FullSimplify[stationaryP == Q - q - h P/m]
      && FullSimplify[pBoundary == P + h V'[q]]
      && PBoundary == P
    ],
  "r4_explicit_cross_mismatch" ->
    TrueQ[FullSimplify[
      crossMismatch == h^2 V''[q]/m
    ]],
  "spectrum_scalar_face" ->
    TrueQ[FullSimplify[
      EkScalar == 4 Pi k/(9 ubar^2 tau theta)
    ]]
|>;

result = <|
  "schema" ->
    "HHS_PASS_219_LANE5_FEYNMAN_DISCRETE_ORBIT_WOLFRAM_20260924_V8",
  "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> Keys @ Select[checks, Not @* TrueQ],
  "checks" -> checks,
  "nonzero_counts_n0_to_18" -> nonzeroCounts,
  "partition_trace_n1_to_9" -> partitionTrace,
  "F2" -> "q*P+h*(P^2/(2m)+V(q))",
  "glued_step_action" ->
    "P*(Q-q)-h*(P^2/(2m)+V(q)) = P*Q-F2",
  "explicit_euler_cross_mismatch" ->
    "h^2*V''(q)/m; h^2*V''(q) when m=1",
  "weight_policy" ->
    "NO_EXACT_CANONICAL_F2 => NO_ADMITTED_HHS_FEYNMAN_WEIGHT",
  "continuum_path_integral_claimed" -> False,
  "partition_symbol" ->
    "partition_trace; script-Z reserved, twistor Z unchanged",
  "u9_history_semantics" ->
    "one admissible history for each source to its unique reachable endpoint; zero for all other endpoint pairs",
  "partition_trace_class" ->
    "REAL_TIME_SPECTRAL_TRACE_NOT_THERMAL_PARTITION_FUNCTION"
|>;

ExportString[result, "RawJSON"]
