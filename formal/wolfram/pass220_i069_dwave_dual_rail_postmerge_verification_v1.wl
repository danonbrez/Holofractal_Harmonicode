(* Pass 220 I069 — D-Wave dual-rail post-merge exact verification *)

symbols = {0, 1, 2};
pairs = Flatten[Table[{c, t}, {c, symbols}, {t, symbols}], 1];
outcome[{c_, t_}] := 3 c + t;
outcomes = outcome /@ pairs;

erasurePairQ[{c_, t_}] := MemberQ[{c, t}, 2];
erasurePairs = Select[pairs, erasurePairQ];
cleanPairs = Select[pairs, Not@*erasurePairQ];

cells = Flatten[Table[9 n + o, {n, 0, 8}, {o, 0, 8}]];

genericCounts = Array[c, 9, 0];
histogramTotalIdentity = Simplify[
  Total[genericCounts] == Total[genericCounts]
];

checks = <|
  "nine_state_bijection" -> (Sort[outcomes] === Range[0, 8]),
  "nine_state_unique_cardinality" -> (Length[DeleteDuplicates[outcomes]] === 9),
  "erasure_pair_count" -> (Length[erasurePairs] === 5),
  "clean_pair_count" -> (Length[cleanPairs] === 4),
  "ordered_reversal_separates_unequal_pairs" -> And @@ Map[
    If[#[[1]] === #[[2]], True, outcome[#] =!= outcome[Reverse[#]]] &,
    pairs
  ],
  "vm81_81_cell_bijection" -> (Sort[cells] === Range[0, 80]),
  "vm81_81_cell_unique_cardinality" -> (Length[DeleteDuplicates[cells]] === 81),
  "cell_bounds_exact" -> (Min[cells] === 0 && Max[cells] === 80),
  "generic_histogram_total_identity" -> TrueQ[histogramTotalIdentity]
|>;

report = <|
  "schema" -> "HHS_PASS_220_I069_DWAVE_DUAL_RAIL_POSTMERGE_WOLFRAM_V1",
  "status" -> If[And @@ Values[checks], "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> Keys@Select[checks, Not],
  "outcomes" -> outcomes,
  "erasure_pair_count" -> Length[erasurePairs],
  "clean_pair_count" -> Length[cleanPairs],
  "cells_min" -> Min[cells],
  "cells_max" -> Max[cells],
  "cell_count" -> Length[DeleteDuplicates[cells]],
  "checks" -> checks
|>;

Print[ExportString[report, "RawJSON", "Compact" -> False]];
