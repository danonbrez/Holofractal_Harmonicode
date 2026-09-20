Module[
 {a2=1,b2=2,c2=3,b=Sqrt[2],c=Sqrt[3],x2,y2,xy,x,O,K,
  o1,o2,rxyG,ryxG,baseG,phaseG,rxyE,ryxE,baseE,phaseE,
  genericTraversalAST,witnessTermAST,terminalAST,fullChainAST,
  stateID,boundChainAST,roleRules,envRules,evalRules,eval,
  chainTerms,chainValues,edgePasses,J,id,tests,passed,report},

 ClearAll[HMod,GeoPow,GeoMul,GeoDiv,GeoNeg,GeoScale,GeoAdd,
          AssertEq,AssertChain,BoundState,WitnessValue,
          X2,Y2,XY,X,O,K];

 x2=X2; y2=Y2; xy=XY; x=X; O=Global`O; K=Global`K;
 o1=(a2+c2)^2/b2^2;
 o2=(c2 (b2+c2)+a2)/(b2+c2-a2);

 rxyG=HMod[b-x2,b+x2]/HMod[c+y2,c-y2];
 ryxG=HMod[b-y2,b+y2]/HMod[c+x2,c-x2];
 baseG=GeoAdd[xy,GeoScale[b c b2,GeoPow[rxyG,o1]]];
 phaseG=GeoAdd[xy,GeoScale[b2 c2,GeoPow[ryxG,o2]]];

 rxyE=HMod[Sqrt[2]-x2,Sqrt[2]+x2]/HMod[Sqrt[3]+y2,Sqrt[3]-y2];
 ryxE=HMod[Sqrt[2]-y2,Sqrt[2]+y2]/HMod[Sqrt[3]+x2,Sqrt[3]-x2];
 baseE=GeoAdd[xy,GeoScale[2 Sqrt[6],GeoPow[rxyE,4]]];
 phaseE=GeoAdd[xy,GeoScale[6,GeoPow[ryxE,4]]];

 genericTraversalAST=GeoDiv[GeoPow[baseG,GeoMul[x,phaseG]],xy];
 witnessTermAST=GeoDiv[
   AssertEq[GeoPow[baseE,GeoMul[x,phaseE]],GeoNeg[xy]],
   a2
 ];
 terminalAST=GeoPow[K,GeoMul[x,O]];
 fullChainAST=AssertChain[x2,genericTraversalAST,witnessTermAST,terminalAST];

 stateID="HHS-P219-GEO-I-PI-E-CANDIDATE-V2";
 boundChainAST=Apply[
   AssertChain,
   (BoundState[stateID,#]& /@ (List@@fullChainAST))
 ];

 J={{0,-1},{1,0}}; id=IdentityMatrix[2];

 roleRules={baseG->K,phaseG->O,baseE->K,phaseE->O};
 envRules={X2->J.J,XY->id,X->J,K->E,O->Pi};
 evalRules={
   GeoMul[m_?MatrixQ,s_?NumericQ]:>s m,
   GeoMul[s_?NumericQ,m_?MatrixQ]:>s m,
   GeoPow[s_?NumericQ,m_?MatrixQ]:>FullSimplify[MatrixExp[Log[s] m]],
   GeoDiv[m_?MatrixQ,n_?MatrixQ]:>FullSimplify[m . Inverse[n]],
   GeoNeg[m_?MatrixQ]:>-m,
   AssertEq[l_?MatrixQ,r_?MatrixQ]:>
     If[TrueQ[FullSimplify[l==r]],WitnessValue[l],$Failed],
   GeoDiv[WitnessValue[m_?MatrixQ],s_?NumericQ]:>FullSimplify[m/s]
 };

 eval[expr_]:=Module[{v=expr/.roleRules/.envRules},
   FixedPoint[(#/.evalRules)&,v,20]
 ];

 chainTerms=List@@fullChainAST;
 chainValues=eval/@chainTerms;
 edgePasses=Map[
   TrueQ[FullSimplify[#[[1]]==#[[2]]]]&,
   Partition[chainValues,2,1]
 ];

 tests=<|
  "order_xy_exact_4"->TrueQ[o1===4],
  "order_yx_exact_4"->TrueQ[o2===4],
  "generic_base_role_binds_K"->TrueQ[(baseG/.roleRules)===K],
  "generic_phase_role_binds_O"->TrueQ[(phaseG/.roleRules)===O],
  "explicit_base_role_binds_K"->TrueQ[(baseE/.roleRules)===K],
  "explicit_phase_role_binds_O"->TrueQ[(phaseE/.roleRules)===O],
  "full_chain_term_count_4"->TrueQ[Length[chainTerms]===4],
  "full_chain_has_outer_power"->TrueQ[!FreeQ[fullChainAST,GeoPow]],
  "full_chain_has_outer_division"->TrueQ[!FreeQ[fullChainAST,GeoDiv]],
  "full_chain_has_nested_assert"->TrueQ[!FreeQ[fullChainAST,AssertEq]],
  "full_chain_has_terminal_KxO"->TrueQ[!FreeQ[fullChainAST,terminalAST]],
  "same_candidate_state_binding"->TrueQ[
    Length[List@@boundChainAST]===4 &&
    And@@((#[[1]]===stateID)&/@ (List@@boundChainAST))
  ],
  "HMod_channel_swap_covariance"->TrueQ[
    (rxyE/.{X2->Y2,Y2->X2})===ryxE
  ],
  "builtin_Mod_not_invoked"->TrueQ[
    FreeQ[fullChainAST,Mod]&&!FreeQ[fullChainAST,HMod]
  ],
  "no_machine_real_in_chain"->TrueQ[FreeQ[fullChainAST,_Real]],
  "all_chain_terms_resolved"->TrueQ[
    FreeQ[chainValues,$Failed|GeoPow|GeoMul|GeoDiv|GeoNeg|AssertEq|HMod|WitnessValue]
  ],
  "nested_assertion_witness_resolved"->TrueQ[chainValues[[3]]===-id],
  "chain_edge_1_x2_equals_generic_division"->edgePasses[[1]],
  "chain_edge_2_generic_equals_assertion_normalization"->edgePasses[[2]],
  "chain_edge_3_normalization_equals_KxO"->edgePasses[[3]],
  "complete_coupled_chain_passes"->TrueQ[And@@edgePasses],
  "I_geometric_square"->TrueQ[chainValues[[1]]===-id],
  "geometric_Euler_closure"->TrueQ[chainValues[[4]]===-id]
 |>;

 passed=Count[Values[tests],True];

 report=<|
   "schema"->"HHS_PASS219_GEOMETRIC_I_PI_E_WOLFRAM_AUDIT_V2",
   "semantics"->"typed_geometric_non_scalar_coupled_chain",
   "allPassed"->TrueQ[passed==Length[tests]],
   "checkCount"->Length[tests],
   "passedCount"->passed,
   "tests"->tests,
   "details"-><|
     "candidate_state_id"->stateID,
     "phase_orders"->{o1,o2},
     "role_bindings"-><|
       "generic_base"->"K",
       "generic_phase"->"O",
       "explicit_base"->"K",
       "explicit_phase"->"O"
     |>,
     "candidate_state_projection"-><|
       "I_H"->J,
       "X2"->J.J,
       "XY"->id,
       "a2"->a2,
       "O"->"Pi on fundamental half-turn branch",
       "K"->"E on fundamental positive-base branch"
     |>,
     "chain_edge_count"->Length[edgePasses],
     "chain_values"->chainValues,
     "mod_semantics"->"HMod held as typed geometric membrane; Wolfram built-in Mod not invoked",
     "assert_semantics"->"HARMONICODE == is assertion/witness equality; the common matrix value is released only after AssertEq passes"
   |>
 |>;

 ExportString[report,"RawJSON"]
]
