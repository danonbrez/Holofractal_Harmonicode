(* Pass 219 Lane 5 cycle 5.
   Harmonic-modulus scalar face, named Delta projection states, and
   T_BRIDGE-01B exact sign-class stability core.

   IMPORTANT:
   U72 is the projection label for the closure assignment 2/ubar^2.
   It is not ordinary exponentiation ubar^72.

   G72 remains the native immutable ordered generator; 2^(1/72) is registered
   only as the licensed scalar projection face.
*)
Module[
 {uu,u72,g72,uh,x2,pp,pv,qv,carrier,c2v,mv,dv,face1,face2,face3,
  deltaR,hh,ord,cv,ccv,rh1,rh2,ep1,ep2,bd1,bd2,checks,failed,result},

 u72=2/uu^2;
 g72=2^(1/72);
 uh=u72^(1/72);
 x2=1/uu;

 pv=pp-1;
 qv=pp+1;
 carrier=(qv-pv)pp/(pv+qv);

 face1=c2v carrier;
 face2=c2v;
 face3=(pp^2-pv qv) mv c2v/dv;
 deltaR=pp*(Sqrt[pv qv+u72])^x2;

 ep1=ccv hh^ord (1+rh1);
 ep2=ccv (hh/2)^ord (1+rh2);
 bd1=cv hh^ord;
 bd2=cv (hh/2)^ord;

 checks=<|
  "closure_assignment_not_ordinary_power_on_committed_root_domain"->
    (Reduce[uu>2 && u72==uu^72,uu,Reals]===False),

  "uh_g72_metric_bridge"->
    FullSimplify[
      uh==g72/uu^(1/36),
      Assumptions->uu>0
    ],

  "g72_scalar_face_closes_dyadic_root"->
    FullSimplify[g72^72==2],

  "carrier_unit_exact"->
    FullSimplify[carrier==1,Assumptions->pp!=0],

  "macro_delta_unit_exact"->
    FullSimplify[pp^2-pv qv==1],

  "triple_face1_equals_face2"->
    FullSimplify[face1==face2,Assumptions->pp!=0],

  "triple_face3_at_delta_m"->
    FullSimplify[
      (face3/.dv->mv)==c2v,
      Assumptions->pp!=0&&mv!=0
    ],

  "delta_m_unique_scalar_gate_solution"->
    FullSimplify[
      Equivalent[c2v==face3,dv==mv],
      Assumptions->c2v!=0&&pp!=0&&dv!=0&&mv!=0
    ],

  "delta_root_projection_named_symbolic_face"->
    FullSimplify[
      deltaR==pp*(Sqrt[(pp-1)(pp+1)+2/uu^2])^(1/uu),
      Assumptions->uu>0
    ],

  "band_envelope_halves_by_power"->
    FullSimplify[
      bd2==bd1/2^ord,
      Assumptions->hh>0&&cv>0&&Element[ord,Integers]&&ord>=1
    ],

  "band_envelope_contracts_under_halving"->
    FullSimplify[
      bd2<bd1,
      Assumptions->hh>0&&cv>0&&Element[ord,Integers]&&ord>=1
    ],

  "sign_stable_at_h_under_relative_remainder_bound"->
    FullSimplify[
      Sign[ep1]==Sign[ccv],
      Assumptions->hh>0&&ccv!=0&&Element[ord,Integers]&&ord>=1&&-1<rh1<1
    ],

  "sign_stable_at_half_h_under_relative_remainder_bound"->
    FullSimplify[
      Sign[ep2]==Sign[ccv],
      Assumptions->hh>0&&ccv!=0&&Element[ord,Integers]&&ord>=1&&-1<rh2<1
    ],

  "sign_class_stable_across_halving"->
    FullSimplify[
      Sign[ep1]==Sign[ep2],
      Assumptions->hh>0&&ccv!=0&&Element[ord,Integers]&&ord>=1&&
        -1<rh1<1&&-1<rh2<1
    ],

  "sign_flip_requires_relative_remainder_crossing_zero_membrane"->
    FullSimplify[
      Implies[ep1 ep2<0,(1+rh1)(1+rh2)<0],
      Assumptions->hh>0&&ccv!=0&&Element[ord,Integers]&&ord>=1
    ]
 |>;

 failed=Keys@Select[checks,#=!=True&];

 result=<|
  "schema"->"HHS_PASS_219_SCALAR_FACE_DELTA_TBRIDGE_WOLFRAM_20260924_V5",
  "status"->If[failed==={},"PASS","FAIL"],
  "check_count"->Length[checks],
  "pass_count"->Count[Values[checks],True],
  "failed"->failed,

  "harmonic_modulus_symbol"->
    "U72 := 2/ubar^2; not ordinary ubar^72",

  "g72_native_status"->
    "immutable ordered generator; scalar preemption forbidden",

  "g72_scalar_projection_face"->
    "2^(1/72)",

  "uh_bridge"->
    "(2/ubar^2)^(1/72)=2^(1/72)/ubar^(1/36)",

  "delta_projection_sigma_m"->
    "Delta -> m on boxed-triple scalar closure membrane",

  "delta_projection_sigma_R"->
    "Delta -> P*(Sqrt[(P-1)(P+1)+2/ubar^2])^(1/ubar)",

  "delta_constructor_identity_global"->False,
  "delta_projection_cross_substitution_authorized"->False,

  "t_bridge_01b_core"->
    "epsilon_h=c*h^p*(1+r_h), c!=0, p>=1, |r_h|<1 => sign stable; C*h^p envelope contracts by 2^-p under halving",

  "t_bridge_01b_workload_interval_certificate"->
    "OPEN",

  "actual_epsilon_monotonicity_claimed"->
    False,

  "monotone_envelope_claimed"->
    True,

  "sextic_root_exact_polynomial_binding"->
    "NOT_PRESENT_IN_REPOSITORY_SEARCH",

  "canonical_runtime_mutation_authority"->
    False
 |>;

 Print[ExportString[result,"RawJSON"]];
]
