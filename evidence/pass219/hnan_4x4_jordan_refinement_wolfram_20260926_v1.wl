ClearAll[r,s,lam,t];
m={{0,0,0,1},{1,0,1,1},{1,1,1,0},{0,1,0,0}};
j=ConstantArray[1,{4,4}];
mxy=r j+(s-r)m;

cp=Factor[CharacteristicPolynomial[m,lam]];
cpLift=Factor[CharacteristicPolynomial[mxy,lam]];
rank1=MatrixRank[m];
null1=Length[NullSpace[m]];
null2=Length[NullSpace[MatrixPower[m,2]]];

rec4=Simplify[
  MatrixPower[m,4]-MatrixPower[m,3]-2 MatrixPower[m,2]
]===ConstantArray[0,{4,4}];

basisIndependence=MatrixRank[
  Transpose[
    Flatten /@ {
      IdentityMatrix[4],
      m,
      MatrixPower[m,2],
      MatrixPower[m,3]
    }
  ]
]===4;

liftRec=FullSimplify[
  MatrixPower[mxy,4]-
  (3 r+s) MatrixPower[mxy,3]+
  2(r^2-s^2) MatrixPower[mxy,2]
]===ConstantArray[0,{4,4}];

genericNull1=Assuming[
  r!=s && r+s!=0,
  FullSimplify[4-MatrixRank[mxy]]
];

genericNull2=Assuming[
  r!=s && r+s!=0,
  FullSimplify[4-MatrixRank[MatrixPower[mxy,2]]]
];

genericKrylovRank=Assuming[
  r!=s && r+s!=0,
  FullSimplify[
    MatrixRank[
      Transpose[
        Flatten /@ {
          IdentityMatrix[4],
          mxy,
          MatrixPower[mxy,2],
          MatrixPower[mxy,3]
        }
      ]
    ]
  ]
];

sumChecks=Table[
  FullSimplify[
    Total[Flatten[MatrixPower[mxy,n]]]-
    2^(n+2)(r+s)^n
  ]===0,
  {n,1,4}
];

sameState=FullSimplify[mxy/.s->r];
oppositeState=FullSimplify[mxy/.s->-r];

result=<|
"schema"->"HHS_PASS219_HNAN_JORDAN_REFINEMENT_WOLFRAM_V1",
"characteristic_polynomial"->ToString[cp,InputForm],
"rank_m01"->rank1,
"nullity_m01"->null1,
"nullity_m01_squared"->null2,
"degree4_recurrence_exact"->rec4,
"lower_degree_recurrence_excluded_by_independence"->basisIndependence,
"jordan_zero_chain_depth_2"->(
  null1===1 && null2===2
),
"minimal_polynomial_equals_characteristic_polynomial"->(
  rec4 && basisIndependence
),
"lifted_characteristic_polynomial"->ToString[cpLift,InputForm],
"lifted_recurrence_exact"->liftRec,
"generic_lift_conditions"->{"r!=s","r+s!=0"},
"generic_nullity_mxy"->genericNull1,
"generic_nullity_mxy_squared"->genericNull2,
"generic_krylov_rank_I_M_M2_M3"->genericKrylovRank,
"r_equals_s_charpoly"->ToString[
  Factor[CharacteristicPolynomial[sameState,t]],
  InputForm
],
"r_equals_s_rank"->Assuming[r!=0,MatrixRank[sameState]],
"r_equals_s_nullity"->Assuming[r!=0,4-MatrixRank[sameState]],
"r_equals_minus_s_charpoly"->ToString[
  Factor[CharacteristicPolynomial[oppositeState,t]],
  InputForm
],
"r_equals_minus_s_rank"->Assuming[r!=0,MatrixRank[oppositeState]],
"r_equals_minus_s_nullity"->Assuming[
  r!=0,
  4-MatrixRank[oppositeState]
],
"sum_invariant_n1_to_n4"->sumChecks,
"status"->If[
  And[
    cp===lam^2*(-2+lam)*(1+lam),
    rank1===3,
    null1===1,
    null2===2,
    rec4,
    basisIndependence,
    cpLift===lam^2*(lam-2r-2s)*(lam-r+s),
    liftRec,
    genericNull1===1,
    genericNull2===2,
    genericKrylovRank===4,
    And@@sumChecks
  ],
  "PASS",
  "FAIL"
]
|>;

Print[ExportString[result,"RawJSON"]];
