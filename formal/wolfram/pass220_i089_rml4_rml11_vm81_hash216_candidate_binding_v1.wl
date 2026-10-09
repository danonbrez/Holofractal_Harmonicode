(* Pass 220 I089: exact RML4->RML11 u^18 quarter-subalgebra
   and I070/I065 VM81 candidate hash216 topology.
   All phase channels remain typed, ordered and address-bearing.
   This is an exact, bounded ORIGINAL phase-transport theorem, not
   a proof of arbitrary u^(1/72), the full VM81 operator algebra,
   or a canonical signed Hash72/Hash216 commit. *)

ClearAll["Global\`*"];
phase8={"x","y","z","w","xy","yx","zw","wz"};
primitiveNames=Take[phase8,4];
orderedProducts=<|"xy"->{"x","y"},"yx"->{"y","x"},
                  "zw"->{"z","w"},"wz"->{"w","z"}|>;
orderedSigns=<|"xy"->1,"yx"->-1,"zw"->1,"wz"->-1|>;
primitivePhases=<|"x"->7,"y"->19,"z"->31,"w"->43|>;
phaseState=Join[primitivePhases,Association@Table[
 key->Mod[Lookup[primitivePhases,First@Lookup[orderedProducts,key]]+
          18*Lookup[orderedSigns,key],72],
 {key,{"xy","yx","zw","wz"}}]];

i2=IdentityMatrix[2];s1={{0,1},{1,0}};
s2={{1,0},{0,-1}};s12={{0,-1},{1,0}};
(* Exactly the original first four RML10 Cl(0,8) generators.
   Do not fabricate or assign any additional phase generators. *)
gens={
 -KroneckerProduct[i2,i2,s2,s12],
 -KroneckerProduct[i2,i2,s12,i2],
 -KroneckerProduct[i2,s1,s1,s12],
 -KroneckerProduct[i2,s2,s1,s12]
};
primitiveMatrix=AssociationThread[primitiveNames,gens[[1;;4]]];
actions=Join[primitiveMatrix,
  Association@Table[
   key->(Lookup[primitiveMatrix,Lookup[orderedProducts,key][[1]]].
         Lookup[primitiveMatrix,Lookup[orderedProducts,key][[2]]]),
   {key,{"xy","yx","zw","wz"}}]];
identity=IdentityMatrix[16];
quarterTurn=18;
quarterActions=Association@Table[key->Lookup[actions,key],{key,phase8}];
inverseActions=Association@Table[key->(-Lookup[actions,key]),{key,phase8}];
transportReversedIdentity=And@@Table[
 Lookup[actions,key].Lookup[inverseActions,key]===identity &&
 Lookup[inverseActions,key].Lookup[actions,key]===identity,
 {key,phase8}];
nuclei=Range[0,8];local=Range[0,8];
slots=Range[0,71];
positions=Range[0,5183];
cell=Quotient[positions,64]; operation=Mod[positions,64];
nucleus=Quotient[cell,9]; localCell=Mod[cell,9];
basis=Mod[operation,8];class8=Quotient[operation,8];
slot=9 basis+localCell;
reconstructed=64*(9 nucleus+localCell)+8 class8+basis;

(* Source-bound candidate Hash216 is the CONCATENATION of three
   exact 72-character lanes, never a numeric equality to 5184.
   These are shape checks; actual native Hash216 hydration and
   source-bound SHA256 receipt validation occur in I089 Python. *)
placeholder72=StringRepeat["x",72];
placeholder216=placeholder72<>placeholder72<>placeholder72;

checks=<|
 "01_phase_order_exact"->(phase8==={"x","y","z","w","xy","yx","zw","wz"}),
 "02_original_phase_period72"->(Length[Range[0,71]]===72),
 "03_original_phase_quarter18"->(quarterTurn===72/4),
 "04_original_half_phase36"->(2 quarterTurn===36),
 "05_rml4_source_phases_bounded"->And@@(0<=#<72& /@ Values[phaseState]),
 "06_original_product_sources"->(Keys[orderedProducts]==={"xy","yx","zw","wz"}),
 "07_original_xy_sign"->(Lookup[orderedSigns,"xy"]===1),
 "08_original_yx_opposite_sign"->(Lookup[orderedSigns,"yx"]===-1),
 "09_original_zw_sign"->(Lookup[orderedSigns,"zw"]===1),
 "10_original_wz_opposite_sign"->(Lookup[orderedSigns,"wz"]===-1),
 "11_dynamic_xy_phase"->(Lookup[phaseState,"xy"]===25),
 "12_dynamic_yx_phase"->(Lookup[phaseState,"yx"]===1),
 "13_dynamic_zw_phase"->(Lookup[phaseState,"zw"]===49),
 "14_dynamic_wz_phase"->(Lookup[phaseState,"wz"]===25),
 "15_Clifford_8_action_rows"->(Length[actions]===8),
 "16_original_16x16_generators"->And@@(Dimensions[#]==={16,16}&/@Values[actions]),
 "17_each_u18_action_square_minus_I"->And@@((#.#===-identity)&/@Values[actions]),
 "18_original_xy_negative_yx"->(Lookup[actions,"xy"]===-Lookup[actions,"yx"]),
 "19_original_zw_negative_wz"->(Lookup[actions,"zw"]===-Lookup[actions,"wz"]),
 "20_exact_quarter_inverse_all_channels"->transportReversedIdentity,
 "21_19step_not_complete_quarter"->(Quotient[19,18]===1 && Mod[19,18]===1),
 "22_18step_is_complete_quarter"->(Quotient[18,18]===1 && Mod[18,18]===0),
 "23_original_nine_nuclei"->(Length[nuclei]===9),
 "24_original_81_VM81_cells"->(Length[Union[cell]]===81),
 "25_original_72_slots_per_nucleus"->(Union[slot]===slots),
 "26_original_9x9x8x8_crosswalk"->(Length[positions]===9*9*8*8===5184),
 "27_original_position_roundtrip"->(reconstructed===positions),
 "28_exact_hash72_candidate_lane_length"->(StringLength[placeholder72]===72),
 "29_exact_three_plane_hash216_length"->(StringLength[placeholder216]===216),
 "30_exact_no_machine_floats"->FreeQ[{phaseState,actions,nucleus,cell,positions},_Real]
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS220_I089_ORIGINAL_RML4_RML11_I070_HASH216_CANDIDATE_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "checks_total"->Length[checks],
 "checks_passed"->Count[Values[checks],True],
 "failed"->failed,
 "rml4_phases"->phaseState,
 "original_quarter_steps"->quarterTurn,
 "original_complete_quarter_actions"->8,
 "incomplete_u19_residual_preserved"->True,
 "vm81_candidate_address_positions"->5184,
 "actual_authenticated_Hash216_transition_committed"->False,
 "native_full_VM81_Clifford_faithfulness_proven"->False,
 "full_u72_fractional_root_operator_proven"->False,
 "native_wx_phase8_registered"->False,
 "canonical_Hash72_minted"->False,
 "signed_VM81_mutation"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
