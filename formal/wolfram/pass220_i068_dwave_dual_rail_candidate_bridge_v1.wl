(* Pass 220 I068 — D-Wave dual-rail candidate bridge exact proof *)

symbols = {0, 1, 2};
outcome[c_, t_] := 3 c + t;
outcomes = Flatten[Table[outcome[c, t], {c, symbols}, {t, symbols}]];

counts = <|"00" -> 3, "0*" -> 1, "*1" -> 1|>;
containsErasure[s_String] := StringContainsQ[s, "*"];
shots = Total[Values[counts]];
erased = Total[Values@KeySelect[counts, containsErasure]];
clean = shots - erased;
yield = Cancel[clean/shots];

checks = <|
  "nine_state_bijection" -> (Sort[outcomes] === Range[0, 8]),
  "unique_cardinality" -> (Length[DeleteDuplicates[outcomes]] === 9),
  "ordered_reversal_separates_unequal_pairs" -> And @@ Flatten@Table[
    If[c === t, True, outcome[c, t] =!= outcome[t, c]],
    {c, symbols}, {t, symbols}
  ],
  "shots_preserved" -> (shots === 5),
  "erasure_shots_preserved" -> (erased === 2),
  "clean_shots_preserved" -> (clean === 3),
  "exact_yield" -> (yield === 3/5)
|>;

report = <|
  "schema" -> "HHS_PASS_220_I068_DWAVE_DUAL_RAIL_WOLFRAM_V1",
  "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> Keys@Select[checks, Not],
  "outcomes" -> outcomes,
  "shots" -> shots,
  "erased" -> erased,
  "clean" -> clean,
  "exact_yield" -> {Numerator[yield], Denominator[yield]},
  "checks" -> checks
|>;

Print[ExportString[report, "RawJSON", "Compact" -> False]];
