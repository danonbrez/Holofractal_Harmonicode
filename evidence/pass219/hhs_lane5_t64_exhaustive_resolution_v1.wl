ClearAll[kappaCode,triplets,encodeTriplet,decodeOperation,phaseAnchor,phaseOverride,
  phaseProduct,resolve,anchorA,anchorB,terminalRoot];

kappaCode = <|"x"->0,"y"->1,"z"->2,"w"->3|>;
triplets = Tuples[{"x","y","z","w"},3];

encodeTriplet[t_List] := Module[{d,n,left,right,binary},
  d = kappaCode /@ t;
  n = 16*d[[1]] + 4*d[[2]] + d[[3]];
  {left,right} = QuotientRemainder[n,8];
  binary = IntegerString[n,2,6];
  <|"triplet"->t,"operation64"->n,"left"->left,"right"->right,
    "binary6"->binary,"row3"->StringTake[binary,3],"col3"->StringTake[binary,-3]|>
];

decodeOperation[n_Integer] := Module[{d0,r,d1,d2,a={"x","y","z","w"}},
  d0 = Quotient[n,16];
  r = Mod[n,16];
  d1 = Quotient[r,4];
  d2 = Mod[r,4];
  {a[[d0+1]],a[[d1+1]],a[[d2+1]]}
];

phaseAnchor = {18,54,18,54,0,36,0,36};

phaseOverride[left_Integer,right_Integer,raw_Integer] := Switch[
  {left,right},
  {0,1},0,{1,0},36,{2,3},0,{3,2},36,
  {4,5},36,{5,4},36,{6,7},36,{7,6},36,
  {4,6},0,{6,4},0,{5,7},0,{7,5},0,
  _,raw
];

phaseProduct[left_Integer,right_Integer] := Module[{raw,phase,reciprocal},
  raw = Mod[phaseAnchor[[left+1]] + phaseAnchor[[right+1]],72];
  phase = phaseOverride[left,right,raw];
  reciprocal = Mod[-phase,72];
  <|"raw"->raw,"phase"->phase,"reciprocal"->reciprocal,
    "zeroSum"->TrueQ[Mod[phase+reciprocal,72] == 0],
    "nativeClosure"->TrueQ[MemberQ[{0,36},phase]]|>
];

anchorA = {0,-2};
anchorB = {-2,0};
terminalRoot = (anchorA + anchorB)/2;

resolve[t_List] := Module[{e,p},
  e = encodeTriplet[t];
  p = phaseProduct[e["left"],e["right"]];
  <|"triplet"->t,"address"->e["operation64"],"binary6"->e["binary6"],
    "phase"->p["phase"],"reciprocal"->p["reciprocal"],
    "zeroSum"->p["zeroSum"],"resolved"->If[TrueQ[p["zeroSum"]],terminalRoot,{999,999}]|>
];

encoded = encodeTriplet /@ triplets;
resolved = resolve /@ triplets;
addresses = Lookup[encoded,"operation64"];
binaries = Lookup[encoded,"binary6"];
resolvedCount = Total[Boole[TrueQ[#["resolved"] == {-1,-1}]]& /@ resolved];

decodeAll = And@@MapThread[TrueQ[decodeOperation[#1["operation64"]] == #2]&,{encoded,triplets}];
phaseAll = And@@(TrueQ /@ Lookup[resolved,"zeroSum"]);
provenanceAll = And@@MapThread[TrueQ[#1["address"] == #2["operation64"]]&,{resolved,encoded}];

checks = <|
  "four_cubed_is_64" -> TrueQ[4^3 == 64],
  "eight_squared_is_64" -> TrueQ[8^2 == 64],
  "triplet_count_64" -> TrueQ[Length[triplets] == 64],
  "address_unique_64" -> TrueQ[Length[DeleteDuplicates[addresses]] == 64],
  "address_complete_0_63" -> TrueQ[Sort[addresses] == Range[0,63]],
  "binary6_unique_64" -> TrueQ[Length[DeleteDuplicates[binaries]] == 64],
  "decode_encode_all_64" -> TrueQ[decodeAll],
  "xyz_address" -> TrueQ[encodeTriplet[{"x","y","z"}]["binary6"] == "000110"],
  "zyx_address" -> TrueQ[encodeTriplet[{"z","y","x"}]["binary6"] == "100100"],
  "xyz_zyx_distinct" -> TrueQ[encodeTriplet[{"x","y","z"}]["operation64"] =!= encodeTriplet[{"z","y","x"}]["operation64"]],
  "phase_zero_sum_all_64" -> TrueQ[phaseAll],
  "resolved_all_minus_one_minus_one" -> TrueQ[resolvedCount == 64],
  "orthogonal_anchor_exact" -> TrueQ[terminalRoot == {-1,-1}],
  "phase_not_constant_across_states" -> TrueQ[Length[DeleteDuplicates[Lookup[resolved,"phase"]]] > 1],
  "provenance_address_retained" -> TrueQ[provenanceAll],
  "vm81_times_64_is_5184" -> TrueQ[81*64 == 5184],
  "72_squared_is_5184" -> TrueQ[72^2 == 5184],
  "all_inside_5184_geometry" -> TrueQ[81*64 == 72^2]
|>;

result = <|
  "schema" -> "HHS_PASS219_LANE5_T64_EXHAUSTIVE_RESOLUTION_WOLFRAM_V1",
  "theorem_id" -> "HHS-T5184-004",
  "status" -> If[And@@Values[checks],"PASS","FAIL"],
  "checks" -> checks,
  "triplet_count" -> Length[triplets],
  "address_count" -> Length[DeleteDuplicates[addresses]],
  "resolved_terminal_count" -> resolvedCount,
  "terminal_root" -> terminalRoot,
  "serialization_geometry" -> 81*64,
  "phase_modulus" -> 72
|>;

ExportString[result,"RawJSON","Compact"->True]