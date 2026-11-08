(* Q81 Module 131-133: external exact-projection audit, candidate-only. *)
(* Ordered products are independent typed input witnesses; do not commute AB and BA. *)
ClearAll[seed, a2, b2, c2, p, q, ab, ba, delta, ers, omega, z3, proj, checks];
p = seed - 1; q = seed + 1;
ab = seed^4; ba = -seed^4;
delta = {FullSimplify[ab/seed^4, seed != 0],
  FullSimplify[-seed^4/ba, seed != 0],
  FullSimplify[c2^2/(a2 + b2), c2 == a2 + b2 && c2 != 0],
  Mod[a2, 2]};
ers = {{1, 0, -1}, {0, 0, 0}, {-1, 0, 1}};
omega = Exp[2 Pi I/3];
z3 = DiagonalMatrix[{1, omega, omega^2}];
proj = FullSimplify[(IdentityMatrix[3] + z3 + MatrixPower[z3, 2])/3];
checks = <|
  "P2MinusPQ" -> FullSimplify[seed^2 - p q],
  "ABPlusBA" -> FullSimplify[ab + ba],
  "ABMinusBA" -> FullSimplify[ab - ba],
  "DeltaFactorVector" -> delta,
  "Genesis" -> (delta /. {a2 -> 1, b2 -> 2, c2 -> 3}),
  "CurrentN" -> (delta /. {a2 -> 1004006004001/1000000000000,
    c2 -> 3004006004001/1000000000000}),
  "GenesisCrossCellEquality" -> (3 == Mod[1, 2]),
  "ERSMatrix" -> ers,
  "ERSRowSums" -> (Total /@ ers),
  "ERSTrace" -> Tr[ers],
  "QutritProjection" -> proj,
  "QutritProjectionIdempotent" -> TrueQ[FullSimplify[proj.proj == proj]],
  "QutritProjectionRank" -> MatrixRank[proj]
|>;
Print[InputForm[checks]];
(* These exact scalar projections are not proof of HNAN native routes,
   physical quantum hardware, canonical VM81 admission, or Hash mint. *)
