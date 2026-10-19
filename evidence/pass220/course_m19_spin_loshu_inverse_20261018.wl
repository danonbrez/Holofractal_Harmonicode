(* Pass220 M19 source-faithful conventional symbolic projection audit.
   Does not evaluate native ordered / or == gates and cannot mint Hash216. *)
ClearAll[x,y,lam,s,l,n,m,adj,expected,checks,result,fermionicN,spectralPoly,spectralRoots,spectralChecks,cardanoP,cardanoQ,cardanoOmega,cardanoRoots,generalK,generalP,generalQ,generalCubic];
s={{-4,-3,-2},{-1,0,1},{2,3,4}};
l={{4,9,2},{3,5,7},{8,1,6}};
n=Expand[x*s+l+y*(-s)];
m=n/(x*y);
adj={
{-3*x^2+6*x*y-2*x-3*y^2+2*y+23,6*x^2-12*x*y-14*x+6*y^2+14*y-52,-3*x^2+6*x*y-2*x-3*y^2+2*y+53},
{6*x^2-12*x*y+16*x+6*y^2-16*y+38,-12*x^2+24*x*y+4*x-12*y^2-4*y+8,6*x^2-12*x*y+16*x+6*y^2-16*y-22},
{-3*x^2+6*x*y-2*x-3*y^2+2*y-37,6*x^2-12*x*y-14*x+6*y^2+14*y+68,-3*x^2+6*x*y-2*x-3*y^2+2*y-7}};
expected=lam^3*x^3*y^3-15*lam^2*x^2*y^2+
  (-18*x^3*y+36*x^2*y^2-18*x*y^3+24*x*y)*lam-360;
(* Independent exact spectral boundary evaluation: x=I, y=-I.
   Do not mistake this SolveValues/Root witness for verification of
   the separately supplied Cardano radical branch syntax. *)
fermionicN=n/.{x->I,y->-I};
spectralPoly=CharacteristicPolynomial[fermionicN,lam];
spectralRoots=lam/.Solve[spectralPoly==0,lam];
(* Cardano reconstruction of the fermionic cubic using its exact depressed
   coefficients. This verifies branch structure, not the literal external
   arbitrary-x,y RealSurd transcription. *)
cardanoP=21;
cardanoQ=-130;
cardanoOmega=Exp[2 Pi I/3];
cardanoRoots=Table[
 RootReduce[5+cardanoOmega^k*
   Surd[-cardanoQ/2+Sqrt[(cardanoQ/2)^2+(cardanoP/3)^3],3]+
   cardanoOmega^(-k)*
   Surd[-cardanoQ/2-Sqrt[(cardanoQ/2)^2+(cardanoP/3)^3],3]],
 {k,0,2}];
spectralChecks=<|
 "fermi_cubic"->TrueQ[Expand[spectralPoly-(-lam^3+15*lam^2-96*lam+360)]===0],
 "three_exact_roots"->(Length[spectralRoots]==3 &&
    And@@(TrueQ[RootReduce[spectralPoly/.lam->#]===0]&/@spectralRoots)),
 "fermi_vieta_sum"->TrueQ[RootReduce[Total[spectralRoots]-15]===0],
 "fermi_cardano_three_branches"->(Length[cardanoRoots]==3 &&
   And@@(TrueQ[RootReduce[spectralPoly/.lam->#]===0]&/@cardanoRoots)),
 "fermi_cardano_roots_match"->(Sort[cardanoRoots]===Sort[RootReduce/@spectralRoots])
|>;
(* Parametric Cardano depression with exact x,y source order and symbolic
   nonzero-bus projection; not a native quantization or ==-gate evaluator. *)
generalK=24-18*(x-y)^2;
generalCubic=lam^3-15*lam^2/(x*y)+generalK*lam/(x*y)^2-360/(x*y)^3;
generalP=(generalK-75)/(x*y)^2;
generalQ=(5*generalK-610)/(x*y)^3;
checks=<|
 "source_ordered_numerator"->(n===Expand[x*s+l+y*(-s)]),
 "det_n_360"->TrueQ[FullSimplify[Det[n]==360]],
 "all_9_inverse_entries"->TrueQ[And@@Flatten[MapThread[
   (FullSimplify[#1==#2])&, {Inverse[m],x*y*adj/360},2]]],
 "two_sided_cofactor_identity"->TrueQ[
   Expand[n.adj-360*IdentityMatrix[3]]===ConstantArray[0,{3,3}]],
 "characteristic_polynomial"->TrueQ[FullSimplify[
   Expand[Det[lam*x*y*IdentityMatrix[3]-n]-expected]==0]],
 "trace_15"->TrueQ[FullSimplify[Tr[n]==15]],
 "general_cardano_depression"->TrueQ[FullSimplify[
   Expand[generalCubic/.lam->lam+5/(x*y)]-(lam^3+generalP*lam+generalQ)==0]],
 "fermionic_exact_spectral_roots"->(And@@Values[spectralChecks])
|>;
result=<|"schema"->"HHS_PASS220_M19_SPIN_LOSHU_EXACT_PROJECTION_V1",
 "checks"->checks,"spectralChecks"->spectralChecks,"cardanoLiteralVerified"->False,"status"->If[And@@Values[checks],"PASS","FAIL"],
 "nativeGateAdmission"->False,"hash216Mint"->False|>;
Print[ExportString[result,"RawJSON","Compact"->True]];
If[result["status"]!="PASS",Exit[1]];
