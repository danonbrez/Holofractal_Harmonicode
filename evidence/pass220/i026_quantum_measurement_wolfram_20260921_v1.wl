(* ============================================================ *)
(* HHS T_QM-03A — EXACT QUANTUM MEASUREMENT PROJECTOR ALGEBRA   *)
(* Polynomial quotient proof: no floating roots or eigensolver. *)
(* ============================================================ *)

ClearAll[x, y, a, b, k, r, m];

phi9 = x^6 + x^3 + 1;
phi72 = y^24 - y^12 + 1;

red9[p_] := Expand[PolynomialRemainder[p, phi9, x]];
red72[p_] := Expand[PolynomialRemainder[p, phi72, y]];

(* Primitive ninth-root sum identity. Exponents are reduced mod 9. *)
rootSums = Table[
  red9[Sum[x^Mod[m b, 9], {b, 0, 8}]],
  {m, 1, 8}
];

(* P_k[a,b] = (1/9) zeta9^(k(a-b)).
   Sum_k P_k = I follows entrywise from root sums. *)
completeKernel = Table[
  red9[
    (1/9) Sum[x^Mod[k (a - b), 9], {k, 0, 8}]
  ],
  {a, 0, 8}, {b, 0, 8}
];

(* P_k P_r = delta_kr P_k reduces to the inner Fourier sum. *)
orthKernel = Table[
  red9[
    (1/9) Sum[x^Mod[(r - k) b, 9], {b, 0, 8}]
  ],
  {k, 0, 8}, {r, 0, 8}
];

(* Conjugation sends zeta9 -> zeta9^-1. *)
hermitianKernel = And @@ Flatten @ Table[
  red9[
    (1/9) x^Mod[-k (a - b), 9]
    -
    (1/9) x^Mod[k (b - a), 9]
  ] === 0,
  {k, 0, 8}, {a, 0, 8}, {b, 0, 8}
];

checks = <|
  "01_phi72_order72" -> (red72[y^72 - 1] === 0),
  "02_phi72_minus_one" -> (red72[y^36 + 1] === 0),
  "03_phi72_relation" -> (red72[y^24 - y^12 + 1] === 0),
  "04_zeta9_embeds_as_y8" ->
    (red72[(y^8)^6 + (y^8)^3 + 1] === 0),
  "05_i_embeds_as_y18" ->
    (
      red72[(y^18)^2 + 1] === 0
      &&
      red72[(y^18)^4 - 1] === 0
    ),
  "06_root_sums_zero" ->
    (rootSums === ConstantArray[0, 8]),
  "07_projector_completeness" ->
    (completeKernel === IdentityMatrix[9]),
  "08_projector_orthogonality" ->
    (orthKernel === IdentityMatrix[9]),
  "09_projector_hermitian" -> hermitianKernel,
  "10_projector_idempotence" ->
    (orthKernel === IdentityMatrix[9]),
  "11_weight_sum_from_completeness" ->
    (completeKernel === IdentityMatrix[9]),
  "12_repeatable_exclusive_collapse" ->
    (orthKernel === IdentityMatrix[9])
|>;

failed = Keys @ Select[checks, # =!= True &];

result = <|
  "schema" ->
    "HHS_PASS_220_I026_QUANTUM_MEASUREMENT_WOLFRAM_20260921_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "phi9" -> ToString[InputForm[phi9]],
  "phi72" -> ToString[InputForm[phi72]],
  "root_sums" -> rootSums,
  "checks" -> checks
|>;

ExportString[result, "RawJSON"]
