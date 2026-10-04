(* Pass 220 I071 — shared-root phase-gear loop closure theorem. *)

ClearAll["Global\`*"];

phaseBasis = {"x","y","z","w","xy","yx","zw","wz"};
loShu = {{4,9,2},{3,5,7},{8,1,6}};
route = Flatten[loShu];
phaseSlots = Range[0,71];

decode[slot_] := {Quotient[slot,9], Mod[slot,9]};
encode[channel_, outcome_] := 9 channel + outcome;
successor[slot_] := Mod[slot+1,72];
vm81[nucleus_, outcome_] := 9 nucleus + outcome;

decoded = decode /@ phaseSlots;
encoded = encode @@@ decoded;
succ = successor /@ phaseSlots;

geometryKey[nucleus_, slot_] := Module[
  {d = decode[slot], channel, outcome, row, col},
  channel = d[[1]];
  outcome = d[[2]];
  row = Quotient[outcome,3] + 1;
  col = Mod[outcome,3] + 1;
  {
    nucleus,
    channel,
    outcome,
    phaseBasis[[channel+1]],
    loShu[[row,col]],
    vm81[nucleus,outcome]
  }
];

path[nucleus_, steps_] := Table[
  geometryKey[nucleus,Mod[t,72]],
  {t,0,steps}
];

firstRepeatPeriod[states_] := Module[
  {seen=<||>, key, i},
  For[i=1,i<=Length[states],i++,
    key=ToString[states[[i]],InputForm];
    If[KeyExistsQ[seen,key], Return[(i-1)-seen[key]]];
    seen[key]=i-1;
  ];
  0
];

rootSeed = 179971179971/1000000;
invariantGate = 1001/1000;
sharedRootPayload = {
  rootSeed,invariantGate,81*64,72*72,144*36
};
sharedRoot = Hash[ToString[sharedRootPayload,InputForm],"SHA256"];

lower[state_] := state["geometry"];
lift[geometry_,depth_,lineage_] := <|
  "geometry"->geometry,
  "depth"->depth,
  "lineage"->lineage,
  "shared_root"->sharedRoot
|>;

basePath = path[0,72];
lineages = Table[
  Hash[ToString[{sharedRoot,t},InputForm],"SHA256"],
  {t,0,72}
];
lifted = Table[
  lift[basePath[[t+1]],3,lineages[[t+1]]],
  {t,0,72}
];
lowered = lower /@ lifted;

checks = <|
 "01_phase_basis_width_8" -> (Length[phaseBasis]===8),
 "02_loshu_exact" -> (loShu==={{4,9,2},{3,5,7},{8,1,6}}),
 "03_loshu_permutation_1_9" -> (Sort[route]===Range[9]),
 "04_phase_slot_count_72" -> (Length[phaseSlots]===72),
 "05_decode_count_72" -> (Length[decoded]===72),
 "06_encode_decode_identity" -> (encoded===phaseSlots),
 "07_phase_pairs_unique" -> (Length[DeleteDuplicates[decoded]]===72),
 "08_successor_count_72" -> (Length[succ]===72),
 "09_successor_is_permutation" -> (Sort[succ]===phaseSlots),
 "10_successor_wrap_71_0" -> (successor[71]===0),
 "11_successor_no_self_loop" -> And@@Table[successor[s]=!=s,{s,0,71}],
 "12_72_steps_return_zero" -> Nest[successor,0,72]===0,
 "13_no_early_return_to_zero" -> And@@Table[Nest[successor,0,t]=!=0,{t,1,71}],
 "14_vm81_count_81" -> Length[Flatten@Table[vm81[n,k],{n,0,8},{k,0,8}]]===81,
 "15_vm81_unique_81" -> Length[DeleteDuplicates[Flatten@Table[vm81[n,k],{n,0,8},{k,0,8}]]]===81,
 "16_vm81_exact_0_80" -> Sort[Flatten@Table[vm81[n,k],{n,0,8},{k,0,8}]]===Range[0,80],
 "17_geometry_path_73" -> Length[basePath]===73,
 "18_first_and_last_geometry_equal" -> First[basePath]===Last[basePath],
 "19_first_72_geometry_unique" -> Length[DeleteDuplicates[Take[basePath,72]]]===72,
 "20_first_repeat_period_72" -> firstRepeatPeriod[basePath]===72,
 "21_no_repeat_before_72" -> firstRepeatPeriod[Take[basePath,72]]===0,
 "22_lift_count_73" -> Length[lifted]===73,
 "23_lower_lift_identity" -> lowered===basePath,
 "24_lifted_first_last_geometry_equal" -> lower[First[lifted]]===lower[Last[lifted]],
 "25_lifted_first_last_lineage_distinct" -> First[lifted]["lineage"]=!=Last[lifted]["lineage"],
 "26_lifted_repeat_period_72" -> firstRepeatPeriod[lowered]===72,
 "27_shared_root_exact_integer_hash" -> IntegerQ[sharedRoot],
 "28_root_seed_exact_rational" -> Head[rootSeed]===Rational,
 "29_invariant_gate_exact_rational" -> Head[invariantGate]===Rational,
 "30_coordinate_closure_5184" -> ({81*64,72*72,144*36}==={5184,5184,5184}),
 "31_phase_gear_determinant_zero" -> (64*81-72*72===0),
 "32_phase_lock_lcm_5184" -> (LCM[64,72,81]===5184),
 "33_all_nuclei_local_period_72" -> And@@Table[firstRepeatPeriod[path[n,72]]===72,{n,0,8}],
 "34_all_nuclei_first72_unique" -> And@@Table[Length[DeleteDuplicates[Take[path[n,72],72]]]===72,{n,0,8}],
 "35_all_geometry_integer_addressed" -> FreeQ[basePath,_Real],
 "36_history_advances_under_geometry_return" -> (First[lifted]["lineage"]=!=Last[lifted]["lineage"])
|>;

failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS_220_I071_SHARED_ROOT_PHASE_GEAR_LOOP_CLOSURE_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "check_count"->Length[checks],
 "pass_count"->Count[Values[checks],True],
 "failed"->failed,
 "phase_slots"->Length[phaseSlots],
 "local_orbit_period"->firstRepeatPeriod[basePath],
 "vm81_addresses"->81,
 "shared_coordinate_closure"->5184,
 "phase_lock_period"->LCM[64,72,81],
 "geometry_returns"->(First[basePath]===Last[basePath]),
 "lineage_advances"->(First[lifted]["lineage"]=!=Last[lifted]["lineage"]),
 "checks"->checks
|>;

Print[ExportString[report,"RawJSON","Compact"->False]];
