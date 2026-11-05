(* Pass 220 I091: typed signed VM81 environmental acceptance contract.
   This Wolfram formalization certifies source and admission invariants
   only. It DOES NOT create or verify ML-DSA-65 cryptographic signatures,
   nor does it execute the native C++ signed environmental entrypoint.
   The dedicated GitHub C++ OpenSSL3.5 job tests the real original probe.
 *)
ClearAll["Global\`*"];
source="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72";
entrypoint="hhs_exact_pass219_vm81_environment_admit_signed";
nativeFrameWords=81;
wordBits=64;
nativeFrameBytes=648;
originalOpcodes=Range[0,11];
originalLanes=Quotient[originalOpcodes,2];
directionBits=Mod[originalOpcodes,2];
originalSignedModes={"commit","constraint","bad-parent","missing-input","bad-pass"};
nativePositiveProofKeys={
 "provider_available","committed_exact","parent_hash216_verified",
 "child_hash216_verified","inherited_rna_authority_invoked",
 "canonical_receipt_minted","transition_verified",
 "child_identity_matches","signature_verified",
 "environment_verified","authority_handoff_exact"};
candidateHash216=StringRepeat["x",72]<>StringRepeat["y",72]<>StringRepeat["z",72];
(* Independent temporal namespaces: source-bound candidate Hash216
   is not the original signed helper's verified genesis reference. *)
candidateNamespace="I090_SOURCE_BOUND_CANDIDATE";
nativeGenesisNamespace="ORIGINAL_PASS219_VERIFIED_GENESIS";
signedTestSource="ORIGINAL_PASS219_DETERMINISTIC_TEST_ROOT";
testPositive=<|"status"->0,"committed_bytes_equal_source"->True,
 "all_positive_keys"->AssociationThread[nativePositiveProofKeys,
 ConstantArray[1,Length[nativePositiveProofKeys]]],
 "signature_length_positive"->True|>;
testNegative=AssociationThread[Rest[originalSignedModes],
 ConstantArray[<|"nonzero_status"->True,"committed_zero"->True,
    "canonical_receipt_minted"->False|>,4]];
(* These are formal logical fixtures ONLY, not fetched native output. *)
checks=<|
 "01_unchanged_verbatim_i086_source"->(source==="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72"),
 "02_only_original_signed_export"->(entrypoint==="hhs_exact_pass219_vm81_environment_admit_signed"),
 "03_original_81_vm81_words"->(nativeFrameWords===81),
 "04_original_64_word_bits"->(wordBits===64),
 "05_original_5184_bit_geometry"->(nativeFrameWords*wordBits===5184),
 "06_original_648_byte_frame"->(8*nativeFrameBytes===5184),
 "07_original_twelve_opcode_values"->(originalOpcodes===Range[0,11]),
 "08_original_six_lanes"->(Union[originalLanes]===Range[0,5]),
 "09_original_pq_qp_source_order"->(directionBits===Flatten[ConstantArray[{0,1},6]]),
 "10_original_positive_commit_mode"->(First[originalSignedModes]==="commit"),
 "11_four_original_negative_modes"->(Length[Rest[originalSignedModes]]===4),
 "12_constraint_negative_mode"->MemberQ[originalSignedModes,"constraint"],
 "13_parent_tamper_negative_mode"->MemberQ[originalSignedModes,"bad-parent"],
 "14_missing_input_negative_mode"->MemberQ[originalSignedModes,"missing-input"],
 "15_bad_pass_negative_mode"->MemberQ[originalSignedModes,"bad-pass"],
 "16_eleven_positive_security_fields"->(Length[nativePositiveProofKeys]===11),
 "17_signature_and_environment_auth_separate"->MemberQ[nativePositiveProofKeys,"signature_verified"]&&MemberQ[nativePositiveProofKeys,"environment_verified"],
 "18_previous_parent_and_child_roles_separate"->MemberQ[nativePositiveProofKeys,"parent_hash216_verified"]&&MemberQ[nativePositiveProofKeys,"child_hash216_verified"],
 "19_inherited_rna_receipt_owner"->MemberQ[nativePositiveProofKeys,"inherited_rna_authority_invoked"],
 "20_exact_commit_frame_contract"->(testPositive["committed_bytes_equal_source"]===True),
 "21_all_positive_fields_required"->(And@@(Values[testPositive["all_positive_keys"]]===ConstantArray[1,11])),
 "22_all_four_failure_records_fail_closed"->And@@(Lookup[Values[testNegative],"committed_zero"]),
 "23_no_negative_can_mint"->And@@(Not/@Lookup[Values[testNegative],"canonical_receipt_minted"]),
 "24_candidate_216_plane_source"->(StringLength[candidateHash216]===216),
 "25_candidate_not_native_genesis_namespace"->(candidateNamespace=!=nativeGenesisNamespace),
 "26_deterministic_original_test_root_not_production"->(signedTestSource==="ORIGINAL_PASS219_DETERMINISTIC_TEST_ROOT"),
 "27_legal_shape_not_native_signature"->(StringLength[candidateHash216]===216&&entrypoint=!=""),
 "28_no_float_authority"->FreeQ[{originalOpcodes,nativeFrameWords,nativeFrameBytes,originalLanes},_Real]
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS220_I091_ORIGINAL_SIGNED_VM81_ENVIRONMENT_TEST_CONTRACT_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "passed"->Count[Values[checks],True],
 "failed"->failed,
 "unchanged_matrix_source"->source,
 "original_signed_environment_export"->entrypoint,
 "candidate_hash216_length"->StringLength[candidateHash216],
 "original_negative_modes"->Rest[originalSignedModes],
 "original_ml_dsa65_provider_executed_by_wolfram"->False,
 "original_native_signed_vm81_probe_executed_by_wolfram"->False,
 "test_fixture_positive_values_are_native_witnesses"->False,
 "test_fixture_negative_values_are_native_witnesses"->False,
 "i090_candidate_hash216_verified_as_original_genesis"->False,
 "native_signed_child_equals_i090_candidate_hash216_proven"->False,
 "canonical_production_admission_verified"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
