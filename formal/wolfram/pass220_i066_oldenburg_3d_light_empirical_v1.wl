(* Pass 220 I066 — Oldenburg 3D-light empirical topology.
   This file verifies exact finite geometry used by the repository fixture.
   It does not invent unreported laser parameters or promote the chiral route
   to a demonstrated potassium result. *)

ClearAll[selection, basis, h72, h216, vm5184, hydrated, tests, report];

selection = {-1, 0, 1};
basis = IdentityMatrix[3];
h72 = 72;
h216 = 3 h72;
vm5184 = 72^2;
hydrated = 3 vm5184;

tests = {
  VerificationTest[
    selection,
    {-1, 0, 1},
    TestID -> "dipole-selection-set"
  ],

  VerificationTest[
    Length[selection],
    3,
    TestID -> "selection-cardinality"
  ],

  VerificationTest[
    DuplicateFreeQ[selection],
    True,
    TestID -> "selection-unique"
  ],

  VerificationTest[
    Sort[selection],
    {-1, 0, 1},
    TestID -> "selection-ordered"
  ],

  VerificationTest[
    MatrixRank[basis],
    3,
    TestID -> "xyz-basis-rank-three"
  ],

  VerificationTest[
    Det[basis],
    1,
    TestID -> "xyz-basis-nondegenerate"
  ],

  VerificationTest[
    h216,
    216,
    TestID -> "hash216-3x72"
  ],

  VerificationTest[
    vm5184,
    5184,
    TestID -> "hash72-square-5184"
  ],

  VerificationTest[
    hydrated,
    15552,
    TestID -> "three-hydrated-planes"
  ],

  VerificationTest[
    AssociationThread[{"PREVIOUS", "CHANGE", "RECEIPT"} -> Range[3]][
      ["PREVIOUS"]
    ],
    1,
    TestID -> "ordered-plane-previous"
  ],

  VerificationTest[
    AssociationThread[{"PREVIOUS", "CHANGE", "RECEIPT"} -> Range[3]][
      ["CHANGE"]
    ],
    2,
    TestID -> "ordered-plane-change"
  ],

  VerificationTest[
    AssociationThread[{"PREVIOUS", "CHANGE", "RECEIPT"} -> Range[3]][
      ["RECEIPT"]
    ],
    3,
    TestID -> "ordered-plane-receipt"
  ]
};

report = TestReport[tests];

<|
  "Schema" ->
    "HHS_PASS_220_I066_OLDENBURG_3D_LIGHT_EMPIRICAL_WOLFRAM_V1",
  "TestsSucceeded" -> report["TestsSucceededCount"],
  "TestsFailed" -> report["TestsFailedCount"],
  "AllTestsSucceeded" -> report["AllTestsSucceeded"],
  "ChiralDemonstratedByPotassiumExperiment" -> False,
  "NumericI061CalibrationSatisfiedByFixtureAlone" -> False,
  "CanonicalMutationAuthority" -> False
|>
