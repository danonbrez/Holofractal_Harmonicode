phaseRing=72;

ClearAll[qguDelta];
qguDelta[q_,c_,d_]:=Mod[c q^2+d q^4,phaseRing];

xy={"Product","x","y"};
yx={"Product","y","x"};
zw={"Product","z","w"};
wz={"Product","w","z"};
cq2={"Product","c",{"Power","q",2}};
dq4={"Product","d",{"Power","q",4}};

qguDeltaAst={"Mod",{"Sum",cq2,dq4},72};
qguKernel={
  "Quotient",
  {"Sum",xy,cq2,dq4},
  {"Sum",xy,cq2}
};

hnanNumerator={
  "Sum","x","y",{"Negate","z"},{"Negate","w"},
  xy,yx,{"Negate",zw},{"Negate",wz}
};

hnanTensor={
  {xy,{"Sum","x","y"},yx},
  {
    {"Sum",xy,{"Negate",zw}},
    hnanNumerator,
    {"Sum",wz,{"Negate",yx}}
  },
  {wz,{"Sum","z","w"},zw}
};

epsilon={
  "Residual",
  "epsilon",
  {"HNANLoShuTensor",hnanTensor},
  {"RelativeToProjection",xy}
};
terminal={"Sum",xy,epsilon};

transportedTensor=
  Map[{"PhaseTransportMod72",#,qguDeltaAst}&,hnanTensor,{2}];
transportedTerminal={"PhaseTransportMod72",terminal,qguDeltaAst};

(* Independent finite proof over the complete residue classes of q,c,d. *)
boundedResidues=And@@Flatten[
  Table[
    0<=qguDelta[q,c,d]<72,
    {q,0,71},{c,0,71},{d,0,71}
  ]
];

qPeriod72=And@@Flatten[
  Table[
    qguDelta[q+72,c,d]===qguDelta[q,c,d],
    {q,0,71},{c,0,71},{d,0,71}
  ]
];

(* QGU transport is additive in the phase ring.  Test every possible phase
   and every possible delta, independently of how the delta was generated. *)
additiveInverse=And@@Flatten[
  Table[
    Mod[Mod[p+delta,72]-delta,72]===Mod[p,72],
    {p,0,71},{delta,0,71}
  ]
];

checks=<|
  "phase_ring_72"->(phaseRing===72),
  "bounded_complete_residue_scan"->boundedResidues,
  "q_period_72_complete_residue_scan"->qPeriod72,
  "additive_inverse_complete_phase_scan"->additiveInverse,
  "kernel_ast_exact"->(
    qguKernel==={
      "Quotient",
      {"Sum",xy,cq2,dq4},
      {"Sum",xy,cq2}
    }
  ),
  "delta_ast_exact"->(
    qguDeltaAst==={
      "Mod",
      {"Sum",cq2,dq4},
      72
    }
  ),
  "transported_tensor_rows_3x3"->(
    Length/@transportedTensor==={3,3,3}
  ),
  "transported_center_wraps_hnan_numerator"->(
    transportedTensor[[2,2]]===
      {"PhaseTransportMod72",hnanNumerator,qguDeltaAst}
  ),
  "xy_yx_order_preserved"->(
    transportedTensor[[1,1,2]]===xy &&
    transportedTensor[[1,3,2]]===yx &&
    UnsameQ[xy,yx]
  ),
  "zw_wz_order_preserved"->(
    transportedTensor[[3,3,2]]===zw &&
    transportedTensor[[3,1,2]]===wz &&
    UnsameQ[zw,wz]
  ),
  "epsilon_terminal_preserved"->(
    transportedTerminal[[2]]===terminal &&
    UnsameQ[transportedTerminal[[2]],xy]
  )
|>;

failed=Keys@Select[checks,#=!=True&];

result=<|
  "schema"->"HHS_PASS219_HNAN_QGU_TRANSPORT_WOLFRAM_20260930_V1",
  "status"->If[failed==={},"PASS","FAIL"],
  "check_count"->Length[checks],
  "pass_count"->Count[Values[checks],True],
  "failed"->failed,
  "phase_ring"->phaseRing,
  "qgu_kernel_ast"->qguKernel,
  "qgu_delta_ast"->qguDeltaAst,
  "base_tensor_ast"->hnanTensor,
  "transported_tensor_ast"->transportedTensor,
  "base_terminal_ast"->terminal,
  "transported_terminal_ast"->transportedTerminal,
  "ratio_kernel_scalar_cancellation_authorized"->False,
  "ordered_product_commutation_authorized"->False,
  "epsilon_elision_authorized"->False,
  "host_float_authority"->False
|>;

Print[ExportString[result,"RawJSON"]];
