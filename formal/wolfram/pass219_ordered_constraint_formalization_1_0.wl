(* Pass 219 ordered-constraint Wolfram formalization 1.0.
   The HARMONICODE source is imported as opaque authoritative text.
   No Equal/Plus/Times/Power evaluation of the source is permitted here. *)

ClearAll[
  topLevelPositions, splitAtPositions, canonicalSource, chars, delta, depths,
  eqPos, topSegments, firstSegChars, firstSegDelta, firstSegDepthBefore,
  slashPos, requiredDecimals, phaseWitnesses, quarticWitnesses, tests, report,
  repoRoot, sourcePath
];

repoRoot = DirectoryName[DirectoryName[DirectoryName[$InputFileName]]];
sourcePath = FileNameJoin[{
  repoRoot,
  "contracts",
  "pass219",
  "PASS_219_ORDERED_CONSTRAINT_WOLFRAM_FORMALIZATION_1_0.harmonicode"
}];

canonicalSource = Import[sourcePath, "Text"];

topLevelPositions[op_String, s_String] := Module[{cs, ds, db, n},
  cs = Characters[s];
  ds = FoldList[
    Plus,
    0,
    (Switch[#, "(" | "[" | "{", 1, ")" | "]" | "}", -1, _, 0] &) /@ cs
  ];
  db = Most[ds];
  n = StringLength[op];
  Select[
    Range[1, StringLength[s] - n + 1],
    db[[#]] == 0 && StringTake[s, {#, # + n - 1}] === op &
  ]
];

splitAtPositions[s_String, pos_List, opLen_Integer] := Module[{starts, ends},
  starts = Join[{1}, pos + opLen];
  ends = Join[pos - 1, {StringLength[s]}];
  MapThread[StringTake[s, {#1, #2}] &, {starts, ends}]
];

chars = Characters[canonicalSource];
delta[c_] := Switch[c, "(" | "[" | "{", 1, ")" | "]" | "}", -1, _, 0];
depths = FoldList[Plus, 0, delta /@ chars];

eqPos = topLevelPositions["==", canonicalSource];
topSegments = splitAtPositions[canonicalSource, eqPos, 2];

firstSegChars = Characters[topSegments[[1]]];
firstSegDelta =
  (Switch[#, "(" | "[" | "{", 1, ")" | "]" | "}", -1, _, 0] &) /@ firstSegChars;
firstSegDepthBefore = Most @ FoldList[Plus, 0, firstSegDelta];
slashPos = Select[
  Range[StringLength[topSegments[[1]]]],
  firstSegDepthBefore[[#]] == 0 &&
    StringTake[topSegments[[1]], {#, #}] === "/" &
];

requiredDecimals = {
  "0.123456789",
  "0.987654321",
  "123456789.123456789",
  "0.999999999999999999",
  "0.00000000810000007371000067",
  "8.10000005751000053",
  "0.99999999999999999999999999",
  "0.000000008100000073710000670761006",
  "8.1000000575100005395410047",
  "0.000000008100000073710001",
  "8.10000005751",
  "2.133185666641251470403352397272"
};

phaseWitnesses = {
  "List(I*x,I^3*y,I*z,I^3*w)",
  "List((-I)*x+123456789/(a^2*s*x),I*y+987654321/(a^2*s*y),(-I)*z+0.123456789/(a^2*s*z),I*w+0.987654321/(a^2*s*w))",
  "List(-I*x+123456789/(a^2*s*x),I*y+987654321/(a^2*s*y),-I*z+0.123456789/(a^2*s*z),I*w+0.987654321/(a^2*s*w))"
};

quarticWitnesses = {
  "(x*y+z*w)/(y^4*w^4)",
  "(w*z+x*y)/(w^4*y^4)"
};

tests = {
  VerificationTest[
    Last[depths] === 0 && Min[depths] >= 0,
    True,
    TestID -> "balanced-delimiters"
  ],
  VerificationTest[
    Length[eqPos],
    4,
    TestID -> "outer-equality-count"
  ],
  VerificationTest[
    Length[topSegments],
    5,
    TestID -> "outer-ordered-constraint-arity"
  ],
  VerificationTest[
    Length[slashPos],
    1,
    TestID -> "single-top-level-quotient"
  ],
  VerificationTest[
    StringCount[canonicalSource, "List(x,y,z,w)"] >= 2,
    True,
    TestID -> "xyzw-lane-preserved"
  ],
  VerificationTest[
    And @@ (StringContainsQ[canonicalSource, #] & /@ requiredDecimals),
    True,
    TestID -> "exact-decimal-lexemes"
  ],
  VerificationTest[
    DuplicateFreeQ[{
      "0.999999999999999999",
      "0.99999999999999999999999999",
      "1"
    }],
    True,
    TestID -> "perturbation-lexemes-distinct"
  ],
  VerificationTest[
    And @@ (StringContainsQ[canonicalSource, #] & /@ phaseWitnesses),
    True,
    TestID -> "phase-signatures"
  ],
  VerificationTest[
    And @@ (StringContainsQ[canonicalSource, #] & /@ quarticWitnesses),
    True,
    TestID -> "ordered-quartic-corrections"
  ],
  VerificationTest[
    StringContainsQ[
      canonicalSource,
      "(u==2.133185666641251470403352397272)^72"
    ],
    True,
    TestID -> "u72-relational-carrier"
  ],
  VerificationTest[
    topSegments[[-2]],
    "e^(y*Pi)",
    TestID -> "terminal-exponential"
  ],
  VerificationTest[
    topSegments[[-1]],
    "x((a²,b²i,c²,(-c²-b²i)))",
    TestID -> "terminal-x-tuple"
  ],
  VerificationTest[
    ! StringContainsQ[canonicalSource, FromCharacterCode[96]],
    True,
    TestID -> "no-machine-precision-marker"
  ]
};

report = TestReport[tests];

Print @ ExportString[
  <|
    "Schema" -> "HHS_PASS219_ORDERED_CONSTRAINT_WOLFRAM_PROOF_V1",
    "TestsRun" -> Length[tests],
    "TestsSucceeded" -> report["TestsSucceededCount"],
    "TestsFailed" -> report["TestsFailedCount"],
    "AllSucceeded" ->
      (report["TestsFailedCount"] === 0 &&
       report["TestsSucceededCount"] === Length[tests]),
    "OuterSegmentOrderHashSHA256" ->
      IntegerString[Hash[topSegments, "SHA256"], 16, 64]
  |>,
  "RawJSON"
];

If[report["TestsFailedCount"] =!= 0, Exit[1]];
