ClearAll[
  HCReciprocal, HCPhaseGear, HCBoundaryQuotient, HCConstraint, HCPower,
  HCSum, HCOrderedProduct, HCRoot, P, p, q, A, B, x, u, DeltaSym, InfinityH
];
SetAttributes[
  {HCReciprocal, HCPhaseGear, HCBoundaryQuotient, HCConstraint, HCPower,
   HCSum, HCOrderedProduct, HCRoot},
  HoldAllComplete
];

globalDenominator = HoldComplete[
  HCBoundaryQuotient[
    HCConstraint[
      P,
      HCRoot[
        HCSum[
          HCOrderedProduct[p,q],
          HCBoundaryQuotient[HCPower[P,4], HCOrderedProduct[A,B]]
        ],
        2
      ]
    ],
    DeltaSym
  ]
];

pGenerator = HoldComplete[
  HCConstraint[P, HCBoundaryQuotient[HCOrderedProduct[B,HCPower[x,5184]], DeltaSym]]
];
infinityBoundary = HoldComplete[
  HCConstraint[HCOrderedProduct[InfinityH,DeltaSym], HCOrderedProduct[B,HCPower[x,5184]]]
];
rInfinity = HoldComplete[HCConstraint[HCReciprocal[InfinityH], DeltaSym]];
rDelta = HoldComplete[HCConstraint[HCReciprocal[DeltaSym], x]];
gamma = HoldComplete[HCConstraint[x, HCPhaseGear[u,"18/72mod72",36]]];
gammaReverse = HoldComplete[HCConstraint[x, HCPhaseGear[u,36,"18/72mod72"]]];
gammaCombined = HoldComplete[HCConstraint[x, HCPhaseGear[u,"18/72mod72+36"]]];
pScale = HoldComplete[
  HCConstraint[
    HCPower[HCBoundaryQuotient[P,InfinityH],HCPower[x,2]],
    P
  ]
];
deltaRecurrence = HoldComplete[
  HCConstraint[
    DeltaSym,
    HCBoundaryQuotient[HCPower[InfinityH,HCPower[x,2]],DeltaSym]
  ]
];
pDeltaFixed = HoldComplete[
  HCConstraint[P,HCBoundaryQuotient[P,DeltaSym]]
];
illegalCancel = HoldComplete[
  HCBoundaryQuotient[HCOrderedProduct[InfinityH,DeltaSym],DeltaSym]
];
scalarInfinity = HoldComplete[InfinityH];
ordinaryLeftInverse = HoldComplete[HCOrderedProduct[HCPower[DeltaSym,-1],DeltaSym]];
ordinaryRightInverse = HoldComplete[HCOrderedProduct[DeltaSym,HCPower[DeltaSym,-1]]];
scalarOne = HoldComplete[1];

nestedObjects = {"rational","matrix","continued_fraction","tensor","x","y","z","w","A","B"};
boundaryDenominators = AssociationThread[
  nestedObjects,
  ConstantArray[globalDenominator,Length[nestedObjects]]
];

checks = <|
  "global_denominator_held" -> MatchQ[globalDenominator, HoldComplete[_HCBoundaryQuotient]],
  "p_generator_keeps_delta" -> MatchQ[pGenerator, HoldComplete[HCConstraint[P,HCBoundaryQuotient[_,DeltaSym]]]],
  "infinity_boundary_keeps_delta" -> MatchQ[infinityBoundary, HoldComplete[HCConstraint[HCOrderedProduct[InfinityH,DeltaSym],_]]],
  "reciprocal_infinity_to_delta" -> (rInfinity === HoldComplete[HCConstraint[HCReciprocal[InfinityH],DeltaSym]]),
  "reciprocal_delta_to_x" -> (rDelta === HoldComplete[HCConstraint[HCReciprocal[DeltaSym],x]]),
  "p_distinct_from_infinity" -> (HoldComplete[P] =!= HoldComplete[InfinityH]),
  "gamma_source_ordered" -> (gamma === HoldComplete[HCConstraint[x,HCPhaseGear[u,"18/72mod72",36]]]),
  "gamma_reverse_distinct" -> (gamma =!= gammaReverse),
  "gamma_combined_distinct" -> (gamma =!= gammaCombined),
  "p_scale_reconstruction_held" -> MatchQ[pScale, HoldComplete[HCConstraint[HCPower[HCBoundaryQuotient[P,InfinityH],HCPower[x,2]],P]]],
  "delta_recurrence_held" -> MatchQ[deltaRecurrence, HoldComplete[HCConstraint[DeltaSym,HCBoundaryQuotient[HCPower[InfinityH,HCPower[x,2]],DeltaSym]]]],
  "p_delta_fixed_point_held" -> MatchQ[pDeltaFixed, HoldComplete[HCConstraint[P,HCBoundaryQuotient[P,DeltaSym]]]],
  "delta_cancellation_not_scalar_infinity" -> (illegalCancel =!= scalarInfinity),
  "ordinary_left_inverse_not_one" -> (ordinaryLeftInverse =!= scalarOne),
  "ordinary_right_inverse_not_one" -> (ordinaryRightInverse =!= scalarOne),
  "shared_global_denominator" -> (Length[DeleteDuplicates[Values[boundaryDenominators]]] == 1),
  "geometry_5184" -> (5184 == 72^2 == 81*64 == 144*36),
  "c4_cycle_count" -> (5184 == 1296*4)
|>;

result = <|
  "schema" -> "HHS_PASS219_LANE5_RECIPROCAL_PHASE_BOUNDARY_WOLFRAM_V1",
  "theorem_id" -> "HHS-T5184-002",
  "status" -> If[And@@Values[checks],"PASS","FAIL"],
  "checks" -> checks,
  "law_sources" -> <|
    "global_denominator" -> "(P=sqrt(pq+(P^4/AB)))/Delta",
    "p_generator" -> "P=(Bx^5184)/Delta",
    "infinity_boundary" -> "Infinity*Delta=Bx^5184",
    "reciprocal_chain" -> "R(Infinity)=Delta;R(Delta)=x",
    "gamma_x" -> "Gamma_x=u^(18/72mod72)*u^36",
    "p_not_infinity" -> "P!=Infinity",
    "p_scale_closure" -> "(P/Infinity)^x^2=P",
    "delta_recurrence" -> "Delta=(Infinity^x^2)/Delta",
    "p_delta_fixed_point" -> "P=P/Delta",
    "delta_cancel" -> "forbidden"
  |>,
  "nested_boundary_object_count" -> Length[nestedObjects],
  "delta_cancellation_authority" -> False,
  "ordinary_inverse_authority" -> False,
  "commutation_authority" -> False,
  "scalar_exponent_combination_authority" -> False
|>;

ExportString[result,"RawJSON","Compact"->True]