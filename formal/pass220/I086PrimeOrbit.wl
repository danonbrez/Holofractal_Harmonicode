(* Pass 220 I086: exact reference projection, not a replacement HNAN/VM81 implementation. *)
ClearAll[lifeStep, orbitTrace, orbitClosure, primeFingerprint];
primeFingerprint[] := Prime[Range[81]];
lifeStep[g_?MatrixQ] /; Dimensions[g] == {9, 9} && 
  AllTrue[Flatten[g], MemberQ[{0, 1}, #] &] := Module[{count},
  count = Table[
    Total[Flatten[Table[
      If[dr == 0 && dc == 0, 0,
        g[[Mod[r - 1 + dr, 9] + 1, Mod[c - 1 + dc, 9] + 1]]],
      {dr, -1, 1}, {dc, -1, 1}]]],
    {r, 9}, {c, 9}];
  MapThread[Boole[#2 == 3 || (#1 == 1 && #2 == 2)] &, {g, count}, 2]
];
orbitTrace[transition_, seed_, steps_Integer?NonNegative] :=
  NestList[transition, seed, steps];
orbitClosure[transition_, seed_, max_Integer?Positive] := Module[
  {seen = <||>, state = seed, key, t = 0},
  While[t <= max,
    key = Compress[state];
    If[KeyExistsQ[seen, key],
      Return[<|"preperiod" -> seen[key], "period" -> t - seen[key],
        "steps" -> t, "exactState" -> state|>]];
    AssociateTo[seen, key -> t];
    state = transition[state]; t++];
  Missing["NotProvenWithinBound", max]
];
(* Reference assertions: 81 distinct consecutive primes and 9x9 toroidal Life. *)
VerificationTest[Length[primeFingerprint[]], 81, TestID -> "prime-count"];
VerificationTest[Length[DeleteDuplicates[primeFingerprint[]]], 81,
  TestID -> "prime-unique"];
VerificationTest[lifeStep[ConstantArray[0, {9, 9}]],
  ConstantArray[0, {9, 9}], TestID -> "dead-still-life"];
VerificationTest[orbitClosure[lifeStep, ConstantArray[0, {9, 9}], 2]["period"],
  1, TestID -> "fixed-point"];
(* Native proof obligations: prime assignment provenance, ordered HNAN gates,
   authenticated Hash216 roots, VM81 admission, and reversible ingress receipts. *)
