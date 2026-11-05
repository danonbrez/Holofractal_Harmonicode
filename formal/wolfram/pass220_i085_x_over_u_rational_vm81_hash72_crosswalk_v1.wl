(* Pass 220 I085 exact symbolic x/u rational-exponent ADDRESS crosswalk.
   Preserve native Pass 186 81x64, 36x144 and Hash72 72x72 address geometry.
   Equal numeric cardinalities do NOT establish raw hash equivalence or
   surjectivity over arbitrary HHS tensor CELL VALUES. *)

ClearAll["Global\`*"];
nativeRequestedSource = "(81*x86_64)=hash72=5184/72²=u⁷²";
originalPhaseRelation = "u^72=1";
heldConstructor = HoldComplete[Power[Divide[x,u],s/72]];
positions = Range[0,5183];
hashRows = Quotient[positions,72];
hashCols = Mod[positions,72];
vmCells = Quotient[positions,64];
vmOps = Mod[positions,64];
basis8 = Mod[vmOps,8];
classes8 = Quotient[vmOps,8];
rootLane36 = Quotient[positions,144];
q144 = Mod[positions,144];
rootRow12 = Quotient[q144,12];
rootCol12 = Mod[q144,12];
u72Pair = Quotient[q144,72];
u72Index = Mod[q144,72];
rationalExponents = positions/72;

(* The source uses rational exponents as SYMBOLIC address labels.
   The native (x/u) power requires a coherent root/inverse/phase witness.
   It is not assigned a Wolfram principal complex root. *)

reconstructedHash = 72 hashRows+hashCols;
reconstructedVM = 64 vmCells+vmOps;
reconstructedQ144 = 144 rootLane36+12 rootRow12+rootCol12;
reconstructedPowerIndex = 72 rationalExponents;

checks = <|
 "01_81x64_equals_5184" -> (81*64===5184),
 "02_72squared_equals_5184" -> (72^2===5184),
 "03_36x144_equals_5184" -> (36*144===5184),
 "04_5184_over_72squared_one" -> (5184/72^2===1),
 "05_original_u72_period_literal" -> (originalPhaseRelation==="u^72=1"),
 "06_held_x_over_u_power" -> (Head[heldConstructor]===HoldComplete),
 "07_full_5184_indices" -> (Length[positions]===5184 && First[positions]===0 && Last[positions]===5183),
 "08_81_unique_vm_cells" -> (Length[Union[vmCells]]===81),
 "09_64_unique_vm_operations" -> (Length[Union[vmOps]]===64),
 "10_72_hash_rows" -> (Length[Union[hashRows]]===72),
 "11_72_hash_columns" -> (Length[Union[hashCols]]===72),
 "12_hash_inverse_all_positions" -> (reconstructedHash===positions),
 "13_vm81_inverse_all_positions" -> (reconstructedVM===positions),
 "14_pass186_q144_inverse_all_positions" -> (reconstructedQ144===positions),
 "15_5184_unique_exact_rational_exponents" -> (Length[DeleteDuplicates[rationalExponents]]===5184),
 "16_fractional_exponent_inverse_all_positions" -> (reconstructedPowerIndex===positions),
 "17_q144_u72_pair_range" -> (Union[u72Pair]==={0,1}),
 "18_q144_u72_index_72" -> (Length[Union[u72Index]]===72),
 "19_pass186_8_ordered_basis_count" -> (Union[basis8]===Range[0,7] && Union[classes8]===Range[0,7]),
 "20_no_floats_in_exact_address_projection" -> FreeQ[
    {positions,hashRows,hashCols,vmCells,vmOps,q144,rationalExponents},_Real],
 "21_first_and_last_coordinates" -> ({
   First[vmCells],First[vmOps],First[hashRows],First[hashCols],
   Last[vmCells],Last[vmOps],Last[hashRows],Last[hashCols]
 }==={0,0,0,0,80,63,71,71}),
 "22_integer_72_cycle_separate_from_5184_rational_lift" -> (72*72===5184 && Length[Union[Mod[positions,72]]]===72)
|>;

failed = Keys@Select[checks,#=!=True&];
report = <|
 "schema"->"HHS_PASS_220_I085_X_U_RATIONAL_EXPONENT_ADDRESS_CROSSWALK_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "passed"->Count[Values[checks],True],
 "failed"->failed,
 "source_relation"->nativeRequestedSource,
 "original_u72_torus_period"->originalPhaseRelation,
 "vm81_positions"->5184,
 "hash72_address_geometry"->{72,72},
 "vm81_word_geometry"->{81,64},
 "pass186_q144_geometry"->{36,144},
 "source_constructor_symbol"->"(x/u)^(s5184/72)",
 "canonical_rational_exponent_first_last"->{
   ToString[InputForm[First[rationalExponents]]],
   ToString[InputForm[Last[rationalExponents]]]},
 "formal_exponent_addresses_complete"->(Length[DeleteDuplicates[rationalExponents]]===5184),
 "native_tensor_value_universality_proven"->False,
 "native_fractional_root_branch_consistency_proven"->False,
 "native_x_over_u_inverse_proven"->False,
 "Hash72_cryptographic_witness_equals_72_squared"->False,
 "Hash216_minted"->False,
 "VM81_mutated"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
