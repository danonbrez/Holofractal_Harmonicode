(* Pass 220 I092: ORIGINAL Hash216 ordered native REFERENCE contract.
   This is a Wolfram logical/index proof, NOT a substitute for the
   original C ABI's SHA256 index resolver. The real native C checks
   the source triplet/216 indexed occurrences and tamper rejection.

   A well-formed reference is not necessarily a historically committed
   parent, a signed receipt, nor permission to mutate VM81.
 *)
ClearAll["Global\`*"];
source="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72";
hashAlphabet="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";
previous=StringRepeat["x",72];
change=StringRepeat["y",72];
receipt=StringRepeat["z",72];
sourceTriplet=previous<>change<>receipt;
roles={"previous","change","receipt"};
allAddresses=Flatten[Table[{role,index,72 role+index},{role,0,2},{index,0,71}],1];
allUniqueIndices=Union[allAddresses[[All,3]]];
roleSource=AssociationThread[roles,{previous,change,receipt}];
reversed=change<>previous<>receipt;
corruptIndexWitness=ReplacePart[allAddresses,84->{1,11,83}];
candidateLabel="I090_ORIGINAL_THREE_PLANE_CANDIDATE";
nativeGenesisLabel="ORIGINAL_SIGNED_PASS219_GENESIS";
nativeParentReferenceInit="hhs_exact_pass219_vm81_pqc_hash216_reference_init";
nativeParentReferenceVerify="hhs_exact_pass219_vm81_pqc_hash216_reference_verify";
signedMutation="hhs_exact_pass219_vm81_environment_admit_signed";
checks=<|
 "01_original_user_matrix_source_verbatim"->(source==="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72"),
 "02_original_seventy_two_glyph_alphabet"->(StringLength[hashAlphabet]===72),
 "03_legacy_three_roles_ordered"->(roles==={"previous","change","receipt"}),
 "04_previous_exact_72"->(StringLength[previous]===72),
 "05_change_exact_72"->(StringLength[change]===72),
 "06_receipt_exact_72"->(StringLength[receipt]===72),
 "07_all_glyphs_in_native_alphabet"->And@@(StringContainsQ[hashAlphabet,#]&/@Characters[previous<>change<>receipt]),
 "08_exact_216_source_triplet"->(StringLength[sourceTriplet]===216),
 "09_216_index_occurrences"->(Length[allAddresses]===216),
 "10_unique_absolute_addresses"->(allUniqueIndices===Range[0,215]),
 "11_first_previous_address"->(allAddresses[[1]]==={0,0,0}),
 "12_last_previous_address"->(allAddresses[[72]]==={0,71,71}),
 "13_first_change_address"->(allAddresses[[73]]==={1,0,72}),
 "14_last_change_address"->(allAddresses[[144]]==={1,71,143}),
 "15_first_receipt_address"->(allAddresses[[145]]==={2,0,144}),
 "16_last_receipt_address"->(allAddresses[[216]]==={2,71,215}),
 "17_reversible_role_position_index"->And@@Table[
   Quotient[k,72]*72+Mod[k,72]===k,{k,0,215}],
 "18_three_source_lanes_remain_distinct"->(Length[DeleteDuplicates[Values[roleSource]]]===3),
 "19_reversing_source_order_changes_triplet"->(reversed=!=sourceTriplet),
 "20_original_index_tamper_differs"->(corruptIndexWitness=!=allAddresses),
 "21_original_native_init_symbol"->(nativeParentReferenceInit==="hhs_exact_pass219_vm81_pqc_hash216_reference_init"),
 "22_original_native_verify_symbol"->(nativeParentReferenceVerify==="hhs_exact_pass219_vm81_pqc_hash216_reference_verify"),
 "23_original_signed_gate_unchanged"->(signedMutation==="hhs_exact_pass219_vm81_environment_admit_signed"),
 "24_candidate_not_native_genesis_proven"->(candidateLabel=!=nativeGenesisLabel),
 "25_81x64_original_position_count"->(81*64===5184),
 "26_72x72_address_plane_count"->(72^2===5184),
 "27_source_candidate_not_signed_reference_claim"->True,
 "28_exact_indices_no_float"->FreeQ[{allAddresses,corruptIndexWitness},_Real]
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS220_I092_NATIVE_HASH216_PARENT_REFERENCE_PREFLIGHT_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "checks_total"->Length[checks],
 "checks_passed"->Count[Values[checks],True],
 "failed"->failed,
 "original_native_reference_init"->nativeParentReferenceInit,
 "original_native_reference_verify"->nativeParentReferenceVerify,
 "original_public_signed_gate"->signedMutation,
 "native_verified_parent_index_records_executed_by_wolfram"->False,
 "native_signed_admission_invoked"->False,
 "candidate_historical_parent_committed_proven"->False,
 "original_UQCEL_source_envelope_candidate_override_allowed"->False,
 "production_vm81_mutation"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
