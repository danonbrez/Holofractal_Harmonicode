Module[
 {a2,b2,c2,b,c,x2,y2,xy,yx,o1,o2,rxyG,ryxG,baseG,phaseG,rxyE,ryxE,baseE,phaseE,specRules,swap,J,id,oo,kk,tests,passed,report},
 ClearAll[HMod,GeoPow,GeoScale,GeoAdd,a2,b2,c2,b,c,x2,y2,xy,yx,oo,kk];
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
 specRules={a2->1,b2->2,c2->3,b->Sqrt[2],c->Sqrt[3]};
 swap[expr_]:=expr/.{x2->y2,y2->x2};
 J={{0,-1},{1,0}}; id=IdentityMatrix[2];
 tests=<|
  "independent_order_xy_is_4"->TrueQ[FullSimplify[o1/.specRules]===4],
  "independent_order_yx_is_4"->TrueQ[FullSimplify[o2/.specRules]===4],
  "generic_base_specializes_exactly"->TrueQ[FullSimplify[(baseG/.specRules)==baseE]],
  "generic_phase_specializes_exactly"->TrueQ[FullSimplify[(phaseG/.specRules)==phaseE]],
  "HMod_channel_swap_covariance"->TrueQ[swap[rxyE]===ryxE],
  "builtin_Mod_not_invoked"->TrueQ[FreeQ[{rxyE,ryxE},Mod]&&!FreeQ[{rxyE,ryxE},HMod]],
  "no_machine_real_in_constructor"->TrueQ[FreeQ[{baseE,phaseE},_Real]],
  "I_geometric_square"->TrueQ[FullSimplify[J.J==-id]],
  "O_fundamental_half_turn_is_Pi"->TrueQ[Reduce[And@@Thread[MatrixExp[oo J]==-id]&&0<oo<2 Pi,oo,Reals]===(oo==Pi)],
  "K_fundamental_positive_base_is_E"->TrueQ[Reduce[And@@Thread[MatrixExp[Pi Log[kk] J]==-id]&&kk>0&&0<Log[kk]<2,kk,Reals]===(kk==E)],
  "geometric_Euler_closure"->TrueQ[FullSimplify[MatrixExp[Pi Log[E] J]==-id]]
 |>;
 passed=Count[Values[tests],True];
 report=<|"schema"->"HHS_PASS219_GEOMETRIC_I_PI_E_WOLFRAM_AUDIT_V1","semantics"->"typed_geometric_non_scalar","allPassed"->TrueQ[passed==Length[tests]],"checkCount"->Length[tests],"passedCount"->passed,"tests"->tests,"details"-><|"phase_orders"->{4,4},"I_operator"->J,"I_square"->J.J,"O_branch"->"O == Pi on 0 < O < 2 Pi","K_branch"->"K == E on K > 0 and 0 < Log[K] < 2","base_metric"->"2*Sqrt[6]","phase_metric"->6,"mod_semantics"->"HMod held as typed geometric membrane; Wolfram built-in Mod not invoked"|>|>;
 Print[ExportString[report,"RawJSON"]];
 If[!TrueQ[report["allPassed"]],Exit[1]];
]
