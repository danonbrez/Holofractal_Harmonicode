(* Pass220 M19 source-faithful conventional symbolic projection audit.
   Does not evaluate native ordered / or == gates and cannot mint Hash216. *)
ClearAll[x,y,lam,s,l,n,m,adj,expected,checks,result,fermionicN,spectralPoly,spectralRoots,spectralChecks,cardanoP,cardanoQ,cardanoOmega,cardanoRoots,generalK,generalP,generalQ,generalCubic,generalDisc,generalU,generalV,generalOmega,generalRoots,literalK,literalShellA,literalShellB,literalC,literalU,literalV,literalRoots,literalFermionicRoots,literalUnitRoots];
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
(* Parametric three-branch Cardano proof with correlated cube roots.
   The second cubic radical is fixed by v=-p/(3u): independent principal
   roots need not satisfy the Cardano product gate. Exclude only u=0 in
   this expression; degeneracies require inherited HNAN semantics. *)
generalDisc=generalQ^2/4+generalP^3/27;
generalU=(-generalQ/2+Sqrt[generalDisc])^(1/3);
generalV=-generalP/(3*generalU);
generalOmega=Exp[2 Pi I/3];
generalRoots=Table[5/(x*y)+generalOmega^j*generalU+
 generalOmega^(-j)*generalV,{j,0,2}];
(* Verbatim polynomial shells from the user's three radical expressions.
   Only shell/coefficient identity is claimed, not literal cube-root
   branch identity or native ordered quantization. *)
literalK=x*y*generalK;
literalShellA=-3*x^3*y^3*literalK+225*x^4*y^4;
literalShellB=-135*x^5*y^5*literalK+16470*x^6*y^6;
(* Literal user Cardano shell is sqrt(B^2-4A^3)+B, not sqrt(...)-B.
   Correlate the second cube-root via the reciprocal coefficient, rather
   than allowing independently selected principal cube-root branches. *)
literalC=(Sqrt[literalShellB^2-4*literalShellA^3]+literalShellB)^(1/3);
literalU=literalC/(3*2^(1/3)*(x*y)^3);
literalV=literalShellA*2^(1/3)/(3*(x*y)^3*literalC);
(* Literal-shell Cardano spectral reconstruction with ordered orientation:
   principal C is paired with its constrained reciprocal, not an
   independently selected cube root. This checks the full parametric
   cubic but does not conflate native gates with scalar equality. *)
literalRoots=Table[5/(x*y)+generalOmega^j*literalU+
 generalOmega^(-j)*literalV,{j,0,2}];
(* Two exact boundary probes of the literal-shell branch orbit.
   RootReduce checks equality of algebraic roots, not floating closeness. *)
literalFermionicRoots=RootReduce/@(literalRoots/.{x->I,y->-I});
literalUnitRoots=RootReduce/@(literalRoots/.{x->1,y->1});
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
 "literal_cardano_shell_A"->TrueQ[FullSimplify[literalShellA==-3*(x*y)^6*generalP]],
 "literal_cardano_shell_B"->TrueQ[FullSimplify[literalShellB==-27*(x*y)^9*generalQ]],
 "literal_cardano_three_roots"->And@@(TrueQ[FullSimplify[
    generalCubic/.lam->#,Assumptions->x*y!=0&&literalC!=0]==0]&/@literalRoots),
 "literal_cardano_fermionic_orbit"->(Sort[literalFermionicRoots]===
   Sort[RootReduce/@(spectralRoots)]),
 "literal_cardano_unit_orbit"->(Sort[literalUnitRoots]===
   Sort[{15,2 I Sqrt[6],-2 I Sqrt[6]}]),
 "literal_realsurd_2_4_prefactor"->TrueQ[FullSimplify[
   2/Surd[4,3]==Surd[2,3]]],
 "literal_complex_branch_multiplier"->TrueQ[FullSimplify[
   (I*Sqrt[3]-1)/(3*Surd[4,3])==
   (-1/2+I*Sqrt[3]/2)*Surd[2,3]/3]],
 "literal_cardano_prefactor_product"->TrueQ[FullSimplify[
   literalU*literalV==-generalP/3]],
 "literal_cardano_discriminant"->TrueQ[FullSimplify[
   literalShellB^2-4*literalShellA^3==2916*(x*y)^18*generalDisc]],
 "general_cardano_three_roots"->And@@(TrueQ[FullSimplify[
   generalCubic/.lam->#,Assumptions->x*y!=0&&generalU!=0]==0]&/@generalRoots),
 "fermionic_exact_spectral_roots"->(And@@Values[spectralChecks])
|>;
result=<|"schema"->"HHS_PASS220_M19_SPIN_LOSHU_EXACT_PROJECTION_V1",
 "checks"->checks,"spectralChecks"->spectralChecks,"cardanoLiteralVerified"->False,"status"->If[And@@Values[checks],"PASS","FAIL"],
 "nativeGateAdmission"->False,"hash216Mint"->False|>;
Print[ExportString[result,"RawJSON","Compact"->True]];
If[result["status"]!="PASS",Exit[1]];
