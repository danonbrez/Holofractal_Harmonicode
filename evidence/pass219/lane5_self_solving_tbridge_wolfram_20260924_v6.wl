(* Pass 219 Lane 5 cycle 6.
   Self-solving proof-optimization result:
   1) exact Genesis root isolation;
   2) exact radical-free local symplectic-Euler energy-defect membrane.

   This file is intentionally projection/proof only.  It grants no canonical
   VM81/Hash72/Hash216/persistence authority.
*)
Module[
 {u,f,lo,hi,a,al,be,ga,r2,rr,aa,ff,dd,ar,br,gr,h,ffh,gh,gc,ge,
  gammaDefinition,checks,failed,result},

 f=2 u^3+3 u^2-8 u-16;
 lo=2133185666641251/10^15;
 hi=2133185666641252/10^15;

 r2=(1+al-be)^2+ga;
 rr=Sqrt[r2];
 aa=1-al+be/2;
 ff=Expand[aa^2*r2-1];
 dd=aa-1/rr;

 ffh=Expand[ff/.{al->h ar,be->h^2 br,ga->h^2 gr}];
 gh=Cancel[ffh/h^2];
 gc=Factor[gh/.{ar->0,br->1,gr->1}];
 ge=Factor[gh/.{ar->0,br->1,gr->16/25}];
 gammaDefinition="h^2*v_t^2/r^2=h^2*L^2/r^4 (L=r*v_t)";

 checks=<|
  "genesis_squared_relation_to_cubic"->
    (Expand[(u+4)^2-2 u^2 (u+2)]===-f),
  "root_low_sign"->
    (Together[f/.u->lo]<0),
  "root_high_sign"->
    (Together[f/.u->hi]>0),
  "root_unique_between_2_and_3"->
    (CountRoots[f,{u,2,3}]===1),
  "root_monotone_for_u_ge_2"->
    FullSimplify[D[f,u]>0,Assumptions->u>=2],
  "sextic_carrier_from_u_equals_a2"->
    (Expand[f/.u->a^2]===2 a^6+3 a^4-8 a^2-16),

  "energy_defect_rationalization"->
    FullSimplify[
      dd==ff/(rr*(aa rr+1)),
      Assumptions->r2>0&&aa>0
    ],
  "energy_zero_membrane_exact"->
    FullSimplify[
      Equivalent[dd==0,ff==0],
      Assumptions->r2>0&&aa>0
    ],
  "energy_sign_denominator_positive"->
    FullSimplify[
      rr*(aa rr+1)>0,
      Assumptions->rr>0&&aa>0
    ],

  "F_constant_term_zero"->
    (Coefficient[ffh,h,0]===0),
  "F_linear_term_zero"->
    (Coefficient[ffh,h,1]===0),
  "F_exact_h2_factor"->
    (PolynomialQ[gh,h]&&Expand[h^2 gh]===ffh),

  "circular_G_exact"->
    (gc===h^2 (1+3 h^2+h^4)/4),
  "eccentric_G_exact"->
    (ge===(-36-11 h^2+66 h^4+25 h^6)/100),
  "circular_class_positive_for_0_h_quarter"->
    FullSimplify[gc>0,Assumptions->0<h<=1/4],
  "eccentric_class_negative_for_0_h_quarter"->
    FullSimplify[ge<0,Assumptions->0<h<=1/4]
 |>;

 failed=Keys@Select[checks,#=!=True&];

 result=<|
  "schema"->"HHS_PASS_219_LANE5_SELF_SOLVING_TBRIDGE_WOLFRAM_20260924_V6",
  "status"->If[failed==={},"PASS","FAIL"],
  "check_count"->Length[checks],
  "pass_count"->Count[Values[checks],True],
  "failed"->failed,

  "root_polynomial"->
    "2*u^3+3*u^2-8*u-16",

  "root_isolation"->
    "2133185666641251/10^15 < u < 2133185666641252/10^15",

  "sextic_carrier"->
    "2*a^6+3*a^4-8*a^2-16=0 with u=a^2",

  "root_derivation"->
    "u+4=u*sqrt(2*(u+2)); positive branch; square to (u+4)^2=2*u^2*(u+2)",

  "energy_normalization"->
    "alpha=h*(x.v)/r^2; beta=h^2*mu/r^3; gamma=h^2*v_t^2/r^2",

  "gamma_definition"->gammaDefinition,

  "energy_radius_ratio"->
    "R^2=(1+alpha-beta)^2+gamma",

  "energy_A"->
    "A=1-alpha+beta/2",

  "energy_membrane_polynomial"->
    "F=A^2*R^2-1",

  "energy_defect_identity"->
    "(DeltaH*r/mu)=F/(R*(A*R+1))",

  "energy_sign_rule"->
    "A>0,R>0 => sgn(DeltaH)=sgn(F)",

  "local_order"->
    "F=h^2*G(h); exact, no Taylor remainder required for local sign classification",

  "halving_rule"->
    "opposite endpoint signs of polynomial F at h and h/2 require an F=0 membrane between scales",

  "circular_h_le_quarter_class"->"+1",
  "eccentric_vt_4_over_5_h_le_quarter_class"->"-1",

  "cumulative_multistep_energy_band"->
    "OPEN: requires exact or validated-enclosure trajectory trace",

  "canonical_runtime_mutation_authority"->
    False
 |>;

 Print[ExportString[result,"RawJSON"]];
]
