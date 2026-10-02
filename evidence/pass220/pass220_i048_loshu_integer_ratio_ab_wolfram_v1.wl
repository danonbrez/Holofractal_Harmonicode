(* Pass 220 I048 — exact Lo Shu integer-ratio A/B formalization.
   Whole-integer ratio geometry only; fractions remain ordered reciprocal tensors.
   Arm A recomputes exact Mod[...,9]; Arm B hydrates the exact same table once.
   Candidate-only: no canonical VM81/Hash72/Hash216 authority. *)
Module[
 {triples,names,loShu,residues,labels,expectedResidues,expectedLabels,residue,label,
  cache,armA,armB,repeats=81,modWorkA,modWorkB,invariantText,reciprocalText,checks,material,result},
 triples=<|"A"->{1,2,3},"B"->{2,3,5},"C"->{3,5,8},"D"->{4,7,11},
  "E"->{5,8,13},"F"->{3,6,9},"G"->{2,4,6},"H"->{7,11,18}|>;
 names=Keys[triples]; loShu={{4,9,2},{3,5,7},{8,1,6}};
 expectedResidues=<|"A"->{1,2,3},"B"->{2,3,5},"C"->{3,5,8},"D"->{4,7,2},
  "E"->{5,8,4},"F"->{3,6,0},"G"->{2,4,6},"H"->{7,2,0}|>;
 expectedLabels=<|"A"->{1,2,3},"B"->{2,3,5},"C"->{3,5,8},"D"->{4,7,2},
  "E"->{5,8,4},"F"->{3,6,9},"G"->{2,4,6},"H"->{7,2,9}|>;
 residue[v_]:=Mod[v,9]; label[r_]:=If[r==0,9,r];
 residues=AssociationMap[residue[triples[#]]&,names];
 labels=AssociationMap[label/@residues[#]&,names];
 cache=<|"residues"->residues,"labels"->labels|>;
 armA=Table[With[{r=AssociationMap[residue[triples[#]]&,names]},
   <|"residues"->r,"labels"->AssociationMap[label/@r[#]&,names]|>],{repeats}];
 armB=Table[cache,{repeats}];
 modWorkA=repeats Total[Length/@Values[triples]]; modWorkB=Total[Length/@Values[triples]];
 invariantText="AB=P^4=c^4=(a^2+b^2)^2=9/Delta";
 reciprocalText="(p/q)=(q/p)^-1";
 checks=<|
  "all_ratio_entries_whole_integers"->And@@(IntegerQ/@Flatten[Values[triples]]),
  "lo_shu_is_1_through_9_permutation"->(Sort[Flatten[loShu]]==Range[9]),
  "lo_shu_rows_sum_15"->(Total/@loShu=={15,15,15}),
  "lo_shu_columns_sum_15"->(Total/@Transpose[loShu]=={15,15,15}),
  "lo_shu_diagonals_sum_15"->({Tr[loShu],Tr[Reverse[loShu]]}=={15,15}),
  "nested_qudit_cell_count_81"->(Length[Flatten[Outer[List,Range[9],Range[9]],1]]==81),
  "C_equals_A_plus_B"->(triples["C"]==triples["A"]+triples["B"]),
  "D_equals_A_plus_C"->(triples["D"]==triples["A"]+triples["C"]),
  "E_equals_B_plus_C"->(triples["E"]==triples["B"]+triples["C"]),
  "G_equals_2A"->(triples["G"]==2 triples["A"]),
  "F_equals_3A"->(triples["F"]==3 triples["A"]),
  "H_equals_B_plus_E"->(triples["H"]==triples["B"]+triples["E"]),
  "base9_residues_expected"->(residues==expectedResidues),
  "zero_residue_maps_to_lo_shu_9"->(label[0]==9),
  "lo_shu_cell_labels_expected"->(labels==expectedLabels),
  "all_labels_are_lo_shu_digits"->And@@(MemberQ[Flatten[loShu],#]&/@Flatten[Values[labels]]),
  "mod9_preserves_C_constructor"->(Mod[triples["A"]+triples["B"],9]==residues["C"]),
  "mod9_preserves_D_constructor"->(Mod[triples["A"]+triples["C"],9]==residues["D"]),
  "mod9_preserves_E_constructor"->(Mod[triples["B"]+triples["C"],9]==residues["E"]),
  "mod9_preserves_G_constructor"->(Mod[2 triples["A"],9]==residues["G"]),
  "mod9_preserves_F_constructor"->(Mod[3 triples["A"],9]==residues["F"]),
  "mod9_preserves_H_constructor"->(Mod[triples["B"]+triples["E"],9]==residues["H"]),
  "global_invariant_preserved_verbatim"->(invariantText=="AB=P^4=c^4=(a^2+b^2)^2=9/Delta"),
  "reciprocal_tensor_preserved_verbatim"->(reciprocalText=="(p/q)=(q/p)^-1"),
  "arm_A_arm_B_exact_payload_equality"->(armA==armB),
  "hydrated_mod_work_strictly_lower"->(modWorkB<modWorkA),
  "no_machine_real_values"->FreeQ[{triples,loShu,residues,labels,armA,armB},_Real],
  "candidate_only_authority"->True|>;
 material=ExportString[<|"triples"->triples,"base9_residues"->residues,"lo_shu_cell_labels"->labels,
  "lo_shu"->loShu,"global_invariant"->invariantText,"reciprocal_tensor"->reciprocalText,
  "repeats"->repeats,"mod_work_A"->modWorkA,"mod_work_B"->modWorkB|>,"RawJSON"];
 result=<|"schema"->"HHS_PASS_220_I048_LOSHU_INTEGER_RATIO_AB_WOLFRAM_V1",
  "status"->If[And@@Values[checks],"PASS","FAIL"],"check_count"->Length[checks],
  "pass_count"->Count[Values[checks],True],"checks"->checks,"triples"->triples,
  "base9_residues"->residues,"lo_shu_cell_labels"->labels,"lo_shu"->loShu,
  "global_invariant_verbatim"->invariantText,"reciprocal_tensor_verbatim"->reciprocalText,
  "ab_repeats"->repeats,"arm_A_mod_operations"->modWorkA,"arm_B_mod_operations"->modWorkB,
  "mod_operation_reduction"->(modWorkA-modWorkB),"ab_exact_payload_equal"->(armA==armB),
  "material_sha256"->Hash[material,"SHA256","HexString"],"native_hash216_authority"->False,
  "canonical_transition_ready"->False|>;
 ExportString[result,"RawJSON"]
]
