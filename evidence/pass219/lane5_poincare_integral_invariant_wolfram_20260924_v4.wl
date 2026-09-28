(* Pass 219 Lane 5 — T_BRIDGE-01A Poincare integral invariant.
   State order: (q1,q2,p1,p2).
   A is the symmetric inverse-mass matrix.
   B is the symmetric potential Hessian.
*)
Module[
 {h,a,b,c,u,v,w,ainv,hess,i2,z2,omega,kick,drift,phi,phiReverse,
  explicit,volOnly,sympDefect,reverseDefect,explicitDefect,volumeDefect,
  phi1,explicit1,checks,failed,result},
 i2=IdentityMatrix[2];
 z2=ConstantArray[0,{2,2}];
 ainv={{a,b},{b,c}};
 hess={{u,v},{v,w}};
 omega=ArrayFlatten[{{z2,i2},{-i2,z2}}];

 kick=ArrayFlatten[{{i2,z2},{-h hess,i2}}];
 drift=ArrayFlatten[{{i2,h ainv},{z2,i2}}];

 (* Carry[A=B]: kick first, then drift using the carried p. *)
 phi=Expand[drift.kick];

 (* Reverse sequential order is different, but still symplectic. *)
 phiReverse=Expand[kick.drift];

 (* Simultaneous old-state explicit Euler. *)
 explicit=ArrayFlatten[{{i2,h ainv},{-h hess,i2}}];

 (* det=1 is weaker than symplecticity. *)
 volOnly=DiagonalMatrix[{2,1,1,1/2}];

 sympDefect=Simplify[Transpose[phi].omega.phi-omega];
 reverseDefect=Simplify[Transpose[phiReverse].omega.phiReverse-omega];
 explicitDefect=Expand[Transpose[explicit].omega.explicit-omega];
 volumeDefect=Transpose[volOnly].omega.volOnly-omega;

 phi1={{1-h^2 a u,h a},{-h u,1}};
 explicit1={{1,h a},{-h u,1}};

 checks=<|
  "kick_is_symplectic"->
    (Simplify[Transpose[kick].omega.kick-omega]===ConstantArray[0,{4,4}]),
  "drift_is_symplectic"->
    (Simplify[Transpose[drift].omega.drift-omega]===ConstantArray[0,{4,4}]),
  "carry_composition_is_symplectic"->
    (sympDefect===ConstantArray[0,{4,4}]),
  "reverse_sequential_is_symplectic"->
    (reverseDefect===ConstantArray[0,{4,4}]),
  "sequential_orders_noncommute_generically"->
    (Expand[phi-phiReverse]=!=ConstantArray[0,{4,4}]),
  "carry_composition_det_one"->(Factor[Det[phi]]===1),
  "reverse_composition_det_one"->(Factor[Det[phiReverse]]===1),
  "one_d_carry_det_one"->(Factor[Det[phi1]]===1),
  "one_d_explicit_det"->(Factor[Det[explicit1]]===1+h^2 a u),
  "explicit_not_symplectic_generically"->
    (explicitDefect=!=ConstantArray[0,{4,4}]),
  "explicit_not_volume_preserving_generically"->
    (Factor[Det[explicit]]=!=1),
  "volume_only_witness_det_one"->(Det[volOnly]===1),
  "volume_only_witness_not_symplectic"->
    (volumeDefect=!=ConstantArray[0,{4,4}]),
  "poincare_form_preserved"->
    (Simplify[Transpose[phi].omega.phi-omega]===ConstantArray[0,{4,4}]),
  "canonical_two_form_rank_preserved"->
    (MatrixRank[Transpose[phi].omega.phi]===MatrixRank[omega]),
  "phase_volume_follows_symplecticity"->(Det[phi]===1)
 |>;

 failed=Keys@Select[checks,#=!=True&];
 result=<|
  "schema"->"HHS_PASS_219_T_BRIDGE_01A_POINCARE_INVARIANT_WOLFRAM_20260924_V4",
  "status"->If[failed==={},"PASS","FAIL"],
  "check_count"->Length[checks],
  "pass_count"->Count[Values[checks],True],
  "failed"->failed,
  "state_order"->"(q1,q2,p1,p2)",
  "omega"->ToString[InputForm[omega]],
  "carry_order"->"kick(p using q) -> drift(q using carried p)",
  "sequential_orders_commute"->False,
  "both_sequential_orders_symplectic"->True,
  "simultaneous_old_state_explicit_symplectic"->False,
  "poincare_integral_invariant"->
    "Phi^*(sum_i dq_i wedge dp_i)=sum_i dq_i wedge dp_i",
  "four_d_projection_reading"->
    "oriented A1+A2 is invariant; individual Ai may exchange",
  "volume_only_is_insufficient"->True,
  "one_d_symplectic_euler_det"->"1",
  "one_d_explicit_euler_det"->"1+h^2*a*u",
  "t_bridge_01b_energy_band_class_stability"->"OPEN",
  "canonical_runtime_mutation_authority"->False
 |>;
 Print[ExportString[result,"RawJSON"]];
]
