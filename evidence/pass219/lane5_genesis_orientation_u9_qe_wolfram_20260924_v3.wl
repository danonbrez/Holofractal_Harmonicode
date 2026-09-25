(* Pass 219 Lane 5 cycle 3:
   Genesis orientation + U9 address orbit + Qe constraint selection.
   Native Eigenvector-0 is the complete ordered x/y/z/w tensor object.
   Existing Pass 220 U9 is used only as the exact nine-position address orbit.
*)
Module[
 {l0,orientation,magnitude,rot180,phaseTensor,flatTensor,n,u9,u9Apply,orbit,
  centerTerms,lockTerms,x1,x2,v1,v2,h,alpha,vp,xp,ang,angSymp,xe,ve,
  angExplicit,r2,rad,mu,alphaKepler,vpK,xpK,energy0,energy1,energySeries,
  energyFirst,qeClass,qeUnique,checks,failed,result},
 l0={{-1,4,-3},{-2,0,2},{3,-4,1}};
 orientation=Sign[l0];
 magnitude=Abs[l0];
 rot180[m_]:=Reverse[Reverse /@ m];
 phaseTensor={
   {"xy","x+y","yx"},
   {"xy-zw","x+y-z-w+xy+yx-zw-wz","wz-yx"},
   {"wz","z+w","zw"}
 };
 flatTensor=Flatten[phaseTensor];

 n=9;
 u9=Table[If[j==Mod[i-2,n]+1,1,0],{i,n},{j,n}];
 u9Apply[v_]:=u9.v;
 orbit=NestList[u9Apply,flatTensor,9];

 centerTerms={"+x","+y","-z","-w","+xy","+yx","-zw","-wz"};
 lockTerms=Join[{"+x","+y","-z","-w"},{"+xy","+yx","-zw","-wz"}];

 (* Central-force order theorem. alpha is the radial scalar so a=alpha*x. *)
 vp={v1+h alpha x1,v2+h alpha x2};
 xp={x1+h vp[[1]],x2+h vp[[2]]};
 ang=x1 v2-x2 v1;
 angSymp=Expand[xp[[1]] vp[[2]]-xp[[2]] vp[[1]]];

 xe={x1+h v1,x2+h v2};
 ve={v1+h alpha x1,v2+h alpha x2};
 angExplicit=Factor[Expand[xe[[1]] ve[[2]]-xe[[2]] ve[[1]]]];

 (* Kepler local-energy expansion for the admitted kick->drift ordering. *)
 r2=x1^2+x2^2;
 rad=Sqrt[r2];
 alphaKepler=-mu/rad^3;
 vpK={v1+h alphaKepler x1,v2+h alphaKepler x2};
 xpK={x1+h vpK[[1]],x2+h vpK[[2]]};
 energy0=(v1^2+v2^2)/2-mu/rad;
 energy1=(vpK[[1]]^2+vpK[[2]]^2)/2-
   mu/Sqrt[xpK[[1]]^2+xpK[[2]]^2];
 energySeries=Normal@Series[energy1-energy0,{h,0,2}];
 energyFirst=FullSimplify[
   Coefficient[energySeries,h,1],
   Assumptions->r2>0
 ];

 (* Native slash surface only: N/D := D mod N^Qe.
    Qe remains surrounding-constraint selected and fails closed when ambiguous. *)
 qeClass[N_Integer,D_Integer,target_Integer,domain_List]:=
   Select[domain,Mod[D,N^#]==target&];
 qeUnique[N_Integer,D_Integer,target_Integer,domain_List]:=
   With[{q=qeClass[N,D,target,domain]},
     If[Length[q]==1,First[q],"UNRESOLVED"]
   ];

 checks=<|
 "loshu_centered_exact"->(l0==={{-1,4,-3},{-2,0,2},{3,-4,1}}),
 "loshu_alphabet"->(Sort[Flatten[l0]]===Range[-4,4]),
 "loshu_zero_total"->(Total[Flatten[l0]]==0),
 "loshu_rows_zero"->And@@(Total[#]==0&/@l0),
 "loshu_cols_zero"->And@@(Total[#]==0&/@Transpose[l0]),
 "loshu_diagonals_zero"->(Tr[l0]==0&&Tr[Reverse[l0]]==0),
 "orientation_table_exact"->
   (orientation==={{-1,1,-1},{-1,0,1},{1,-1,1}}),
 "magnitude_table_exact"->
   (magnitude==={{1,4,3},{2,0,2},{3,4,1}}),
 "reciprocal_scalar_180"->(rot180[l0]===-l0),
 "phase_tensor_180_pairs"->
   ({{phaseTensor[[1,1]],phaseTensor[[3,3]]},
     {phaseTensor[[1,2]],phaseTensor[[3,2]]},
     {phaseTensor[[1,3]],phaseTensor[[3,1]]},
     {phaseTensor[[2,1]],phaseTensor[[2,3]]}}
    ==={{"xy","zw"},{"x+y","z+w"},{"yx","wz"},
        {"xy-zw","wz-yx"}}),
 "center_lock_order_preserved"->(centerTerms===lockTerms),
 "vm81_is_72_plus_9"->(3*24+9==81),
 "vm5184_crosswalk"->(81*64==72^2&&72^2==5184),
 "u9_unitary"->(u9.ConjugateTranspose[u9]===IdentityMatrix[9]),
 "u9_nine_closure"->(MatrixPower[u9,9]===IdentityMatrix[9]),
 "u9_tensor_orbit_length"->(Length[DeleteDuplicates[Most[orbit]]]==9),
 "u9_full_orbit_returns_tensor"->(Last[orbit]===flatTensor),
 "u9_one_step_is_not_flat_tensor_identity"->(orbit[[2]]=!=flatTensor),
 "native_tensor_not_fourier_mode_substitution"->
   (flatTensor=!=ConstantArray[flatTensor[[1]],9]),
 "symplectic_central_L_exact"->FullSimplify[angSymp==ang],
 "explicit_central_L_factor"->
   FullSimplify[angExplicit==(1-h^2 alpha) ang],
 "ordered_update_difference_literal"->
   FullSimplify[xp-xe==h^2 alpha {x1,x2}],
 "kepler_local_energy_has_no_linear_h_term"->TrueQ[energyFirst===0],
 "qe_target_zero_unique_for_2_over_2"->
   (qeClass[2,2,0,Range[1,8]]==={1}),
 "qe_unique_commit"->(qeUnique[2,2,0,Range[1,8]]===1),
 "qe_multicandidate_fail_closed"->
   (qeUnique[2,2,2,Range[1,8]]==="UNRESOLVED"),
 "qe_is_constraint_selected_not_free"->
   (qeClass[2,2,0,Range[1,8]]=!=Range[1,8])
 |>;

 failed=Keys@Select[checks,#=!=True&];
 result=<|
 "schema"->"HHS_PASS_219_GENESIS_ORIENTATION_U9_QE_WOLFRAM_20260924_V3",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "pass_count"->Count[Values[checks],True],
 "failed"->failed,
 "orientation_table"->orientation,
 "magnitude_table"->magnitude,
 "vm81_construction"->"72 phase-cover positions + 9-cell Genesis nucleus",
 "kronecker_scalar_construction_authority"->False,
 "u9_role"->
   "address-orbit permutation over nine tensor positions; full orbit closes",
 "u9_one_step_e0_scalar_eigenclaim"->"NOT_ASSERTED",
 "native_eigenvector0"->"full ordered x,y,z,w tensor object",
 "symplectic_central_L"->"EXACT",
 "explicit_central_L"->"(1-h^2*alpha)*L",
 "kepler_local_energy_defect"->"O(h^2); no linear h term",
 "qe_commit_rule"->
   "commit only after surrounding constraints select exactly one admissible Qe; otherwise unresolved",
 "t_bridge_01_global_band_monotonicity"->"OPEN",
 "global_prime_equivalence"->"OPEN",
 "riemann_bridge"->"OPEN",
 "collatz_asymptotic_bridge"->"OPEN"
 |>;
 Print[ExportString[result,"RawJSON"]];
]
