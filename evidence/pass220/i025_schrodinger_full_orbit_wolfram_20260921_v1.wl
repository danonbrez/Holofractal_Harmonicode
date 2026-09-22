(* ============================================================ *)
(* HHS T_QM-02 — EXACT FIRING-ORDER UNITARITY/SPECTRUM          *)
(* Corrected 1-based permutation indexing and standard          *)
(* U = Exp[-i H Delta_t/u72] phase convention.                  *)
(* ============================================================ *)

ClearAll[x, P, d, k, n, mIndex];

sigma[n_] := Mod[8 + 16 n, 72, 1];
firingOrder = Table[sigma[n], {n, 0, 8}];

n9 = 9;
(* Column j -> row j+1, with 1-based correction i-2. *)
U9 = Table[
  If[j == Mod[i - 2, n9] + 1, 1, 0],
  {i, n9}, {j, n9}
];

step = 16; nT = 72;
(* Column j -> row j+16, with 1-based correction i-step-1. *)
U72 = Table[
  If[j == Mod[i - step - 1, nT] + 1, 1, 0],
  {i, nT}, {j, nT}
];

perm = Table[Mod[i + step - 1, nT] + 1, {i, nT}];
cycles = PermutationCycles[perm];
cycleLists = First[List @@ cycles];

(* Wolfram CharacteristicPolynomial is Det[M-xI], so normalize monic. *)
monicCP[matrix_] := Expand[
  (-1)^Length[matrix] CharacteristicPolynomial[matrix, x]
];

cp9 = Factor[monicCP[U9]];
cp72 = Factor[monicCP[U72]];
cyclo9 = (x - 1) (x^2 + x + 1) (x^6 + x^3 + 1);

z72 = Exp[2 Pi I/72];
z9 = Exp[2 Pi I/9];

(* Positive-energy branch under U=Exp[-i H Delta_t/u72]:
   U psi_k = zeta9^(-k) psi_k. *)
mode[k_] := Table[z9^(k (j - 1)), {j, 1, 9}];
modeChecks = Table[
  FullSimplify[U9 . mode[k] == z9^(-k) mode[k]],
  {k, 0, 8}
];

rootOrthogonality = Table[
  FullSimplify[Sum[z9^(mIndex n), {n, 0, 8}]],
  {mIndex, 1, 8}
];

energyPhaseChecks = Table[
  FullSimplify[
    Exp[-I (2 Pi k/9)] == z9^(-k)
  ],
  {k, 0, 8}
];

(* Exact finite difference is NOT the logarithmic Hermitian generator. *)
fdEqualityChecks = Table[
  FullSimplify[
    I (z9^(-k) - 1) == 2 Pi k/9
  ],
  {k, 1, 8}
];

gold = (1 + Sqrt[5])/2;
goldConj = (1 - Sqrt[5])/2;

flank = With[{q = P + 1, p = P - 1},
  FullSimplify[
    p q + (q - p) P/(p + q) == P^2,
    Assumptions -> P != 0
  ]
];

checks = <|
  "01_firing_order_exact" ->
    (firingOrder === {8, 24, 40, 56, 72, 16, 32, 48, 64}),
  "02_period_9" ->
    (Table[sigma[n + 9], {n, 0, 71}] ===
      Table[sigma[n], {n, 0, 71}]),
  "03_order_from_gcd" -> (72/GCD[72, 16] === 9),
  "04_u9_unitary" ->
    (U9 . ConjugateTranspose[U9] === IdentityMatrix[9]),
  "05_u9_nine_closure" ->
    (MatrixPower[U9, 9] === IdentityMatrix[9]),
  "06_u9_monic_charpoly" -> (cp9 === cyclo9),
  "07_u72_unitary" ->
    (U72 . ConjugateTranspose[U72] === IdentityMatrix[72]),
  "08_u72_nine_closure" ->
    (MatrixPower[U72, 9] === IdentityMatrix[72]),
  "09_full_orbit_eight_cycles" ->
    (Sort[Length /@ cycleLists] === ConstantArray[9, 8]),
  "10_u72_eightfold_charpoly" -> (cp72 === cyclo9^8),
  "11_zeta9_embeds_in_zeta72" -> FullSimplify[z72^8 == z9],
  "12_i_is_zeta72_power" -> FullSimplify[z72^18 == I],
  "13_all_9_fourier_modes" -> And @@ modeChecks,
  "14_root_sum_orthogonality" ->
    (rootOrthogonality === ConstantArray[0, 8]),
  "15_positive_energy_branch_phase" -> And @@ energyPhaseChecks,
  "16_fd_not_exact_log_generator" ->
    (fdEqualityChecks === ConstantArray[False, 8]),
  "17_gold_plus_constructor" ->
    (FullSimplify[gold^2 - gold] === 1),
  "18_gold_minus_constructor" ->
    (FullSimplify[goldConj^2 - goldConj] === 1),
  "19_gold_polynomial_plus" ->
    (FullSimplify[gold^2 - gold - 1] === 0),
  "20_flank_with_domain" -> flank,
  "21_idempotent_d_roots" ->
    (Solve[d^2 == d, d] === {{d -> 0}, {d -> 1}}),
  "22_pq_flank" ->
    (FullSimplify[(P + 1) (P - 1) - (P^2 - 1)] === 0),
  "23_sum_flank" ->
    (FullSimplify[(P + 1) + (P - 1) - 2 P] === 0),
  "24_lock_line" ->
    (FullSimplify[2 P - ((P - 1) + (P + 1))] === 0),
  "25_degeneracy_is_eight" ->
    (Exponent[cp72, x] == 72 &&
      Quotient[Exponent[cp72, x], Exponent[cp9, x]] == 8)
|>;

failed = Keys @ Select[checks, # =!= True &];

correctionsFromInitialFixture = <|
  "U9_1_based_index" -> "j == Mod[i - 2, 9] + 1",
  "U72_1_based_index" -> "j == Mod[i - step - 1, 72] + 1",
  "wolfram_monic_charpoly" ->
    "(-1)^n CharacteristicPolynomial[U,x]",
  "standard_evolution_convention" ->
    "U=ExpSym(-i H Delta_t/u72)",
  "positive_energy_eigenphase" -> "zeta9^(-k)",
  "finite_difference_status" ->
    "coarse-grain only; not exact logarithmic Hermitian generator"
|>;

result = <|
  "schema" ->
    "HHS_PASS_220_I025_SCHRODINGER_FULL_ORBIT_WOLFRAM_20260921_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "firing_order" -> firingOrder,
  "charpoly9" -> ToString[InputForm[cp9]],
  "charpoly72" -> ToString[InputForm[cp72]],
  "cycle_lengths" -> Sort[Length /@ cycleLists],
  "positive_energy_eigenphase" -> "zeta9^(-k)",
  "finite_difference_equalities_k1_to_8" -> fdEqualityChecks,
  "corrections_from_initial_fixture" -> correctionsFromInitialFixture,
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
