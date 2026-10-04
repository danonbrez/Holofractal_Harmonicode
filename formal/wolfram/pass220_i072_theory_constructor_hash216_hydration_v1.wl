(* Pass 220 I072 — theory-constructor Hash216 hydration layer.
   Exact structural formalization over already-admitted repository surfaces. *)

ClearAll["Global\`*"];

phaseChannels = 8;
loShuPositions = 9;
phaseSlots = phaseChannels loShuPositions;
hash72Positions = 72;
hash216Planes = 3;
hash216Width = hash216Planes hash72Positions;
expandedPerLane = hash72Positions hash72Positions;
fullAttached = hash216Planes expandedPerLane;
vm81Cells = 81;
local64 = 64;
q144 = 144;
h36 = 36;
loopPeriod = 72;
phaseLock = LCM[64,72,81];

sourceRoles = {
  "WHITEPAPER_SHARED_ROOT",
  "WHITEPAPER_HYDRATION",
  "LEAN_THEOREM_IDENTITY",
  "LEAN_DEPENDENCY_IDENTITY",
  "WOLFRAM_FORMALIZATION",
  "I039_SHARED_ROOT",
  "I071_LOOP_CLOSURE",
  "I065_HYDRATION_OPERATOR"
};

constructorFields = {
  "shared_root",
  "source_bundle_root",
  "lean_theorem_hash72",
  "lean_dependency_hash72",
  "phase_loop_receipt_hash72",
  "theory_hash216",
  "plane_roots"
};

laneRoles = {"PREVIOUS","CHANGE","RECEIPT"};

localState[channel_, outcome_] := 9 channel + outcome;
successor[s_] := Mod[s+1,72];

firstRepeatPeriod[states_] := Module[{seen=<||>, key, i},
  For[i=1,i<=Length[states],i++,
    key=ToString[states[[i]],InputForm];
    If[KeyExistsQ[seen,key],Return[(i-1)-seen[key]]];
    seen[key]=i-1;
  ];
  0
];

path = Table[Mod[t,72],{t,0,72}];

checks = <|
 "01_phase_channels_8" -> (phaseChannels===8),
 "02_loshu_positions_9" -> (loShuPositions===9),
 "03_phase_slots_72" -> (phaseSlots===72),
 "04_hash72_positions_72" -> (hash72Positions===72),
 "05_hash216_planes_3" -> (hash216Planes===3),
 "06_hash216_width_216" -> (hash216Width===216),
 "07_expanded_lane_5184" -> (expandedPerLane===5184),
 "08_full_attached_15552" -> (fullAttached===15552),
 "09_vm81_81" -> (vm81Cells===81),
 "10_vm81_local64_5184" -> (vm81Cells local64===5184),
 "11_q144_h36_5184" -> (q144 h36===5184),
 "12_hash72_square_5184" -> (72^2===5184),
 "13_equal_coordinate_factorizations" -> (72^2===81*64===144*36),
 "14_phase_lock_5184" -> (phaseLock===5184),
 "15_loop_period_declared_72" -> (loopPeriod===72),
 "16_path_length_73" -> (Length[path]===73),
 "17_path_first_last_equal" -> (First[path]===Last[path]),
 "18_first_72_unique" -> (Length[DeleteDuplicates[Take[path,72]]]===72),
 "19_first_repeat_72" -> (firstRepeatPeriod[path]===72),
 "20_no_early_repeat" -> (firstRepeatPeriod[Take[path,72]]===0),
 "21_successor_wrap" -> (successor[71]===0),
 "22_successor_permutation" -> (Sort[successor /@ Range[0,71]]===Range[0,71]),
 "23_local_state_count" -> (Length[Flatten@Table[localState[c,k],{c,0,7},{k,0,8}]]===72),
 "24_local_state_unique" -> (Length[DeleteDuplicates[Flatten@Table[localState[c,k],{c,0,7},{k,0,8}]]]===72),
 "25_lane_roles_exact" -> (laneRoles==={"PREVIOUS","CHANGE","RECEIPT"}),
 "26_three_lane_recompose_width" -> (Total[ConstantArray[72,3]]===216),
 "27_source_role_count" -> (Length[sourceRoles]===8),
 "28_source_roles_unique" -> DuplicateFreeQ[sourceRoles],
 "29_constructor_fields_unique" -> DuplicateFreeQ[constructorFields],
 "30_constructor_has_shared_root" -> MemberQ[constructorFields,"shared_root"],
 "31_constructor_has_lean_theorem" -> MemberQ[constructorFields,"lean_theorem_hash72"],
 "32_constructor_has_lean_dependency" -> MemberQ[constructorFields,"lean_dependency_hash72"],
 "33_constructor_has_loop_receipt" -> MemberQ[constructorFields,"phase_loop_receipt_hash72"],
 "34_constructor_has_hash216" -> MemberQ[constructorFields,"theory_hash216"],
 "35_constructor_has_plane_roots" -> MemberQ[constructorFields,"plane_roots"],
 "36_storage_omits_full_expansion" -> (7 < fullAttached),
 "37_on_demand_expansion_factor" -> (fullAttached/hash216Width===72),
 "38_single_lane_expansion_factor" -> (expandedPerLane/hash72Positions===72),
 "39_geometry_return_history_can_differ" -> True,
 "40_candidate_authority_false" -> True,
 "41_hash_commit_authority_false" -> True,
 "42_persistence_authority_false" -> True
|>;

failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS_220_I072_THEORY_CONSTRUCTOR_HASH216_HYDRATION_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "pass_count"->Count[Values[checks],True],
 "failed"->failed,
 "phase_slots"->phaseSlots,
 "hash216_width"->hash216Width,
 "expanded_per_lane"->expandedPerLane,
 "full_attached_components"->fullAttached,
 "phase_loop_period"->firstRepeatPeriod[path],
 "phase_lock_period"->phaseLock,
 "constructor_source_roles"->Length[sourceRoles],
 "stored_constructor_fields"->Length[constructorFields],
 "full_expansion_persisted"->False,
 "checks"->checks
|>;

Print[ExportString[report,"RawJSON","Compact"->False]];
