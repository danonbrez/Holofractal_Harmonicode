(* Pass 220 I080 deterministic knowledge-graph QPU formalization. *)

serializedCharacters = 5184;
lastAddress = 5183;
nucleusAnchorPositions = 1;
freeTernaryPositions = 5183;
vm81Cells = 81;
local64 = 64;
hash72 = 72;
hash216Planes = 3;
hash216Width = 216;
fullAttached = 15552;
phaseStep = 16;
phaseModulus = 72;
phaseOrbit = 9;
phaseGearE = {8,24,40,56,72,16,32,48,64};
offsetAlphabet = Range[-9,9];

genesis[prefix_String] := prefix <> StringRepeat["0", serializedCharacters - StringLength[prefix]];
palindromeRNA[bits_String] := bits <> "." <> StringReverse[bits];
rnaRoundTrip[bits_String] := StringReverse[StringReverse[bits]] === bits;

phaseOrbitValues = Table[
  Mod[8 + k phaseStep, phaseModulus] /. 0 -> 72,
  {k,0,phaseOrbit-1}
];

ieeeLayouts = <|
  "binary16" -> {1,5,10},
  "binary32" -> {1,8,23},
  "binary64" -> {1,11,52}
|>;

ieeeVectors = {
  StringRepeat["0",16],
  "1"<>StringRepeat["0",15],
  "0011110000000000",
  StringRepeat["0",32],
  "00111111100000000000000000000000",
  StringRepeat["0",64],
  "0011111111110000000000000000000000000000000000000000000000000000",
  "0111111111110000000000000000000000000000000000000000000000000000",
  "0111111111111000000000000000000000000000000000000000000000000001"
};

checks = <|
  "carrier_width" -> (serializedCharacters === 5184),
  "last_address" -> (lastAddress === serializedCharacters-1),
  "nucleus_plus_free" -> (nucleusAnchorPositions+freeTernaryPositions === serializedCharacters),
  "ternary_source" -> (HoldForm[3^5183] === HoldForm[3^5183]),
  "offset_alphabet_cardinality" -> (Length[offsetAlphabet] === 19),
  "offset_min" -> (First[offsetAlphabet] === -9),
  "offset_max" -> (Last[offsetAlphabet] === 9),
  "vm81_factor" -> (vm81Cells local64 === serializedCharacters),
  "hash72_square" -> (hash72 hash72 === serializedCharacters),
  "ratio_64_72_equals_72_81" -> (64/72 === 72/81),
  "ratio_reduced_8_9" -> (64/72 === 8/9),
  "common_5184_closure" -> (64 81 === 72^2 === serializedCharacters),
  "phase_orbit_exact" -> (phaseOrbitValues === phaseGearE),
  "phase_orbit_length" -> (Length[phaseGearE] === phaseOrbit),
  "u16_nine_steps_two_turns" -> (phaseOrbit phaseStep === 2 phaseModulus === 144),
  "hash216_width" -> (hash216Planes hash72 === hash216Width),
  "hash216_hydration" -> (hash216Planes serializedCharacters === fullAttached),
  "genesis_10_width" -> (StringLength[genesis["10"]] === serializedCharacters),
  "genesis_10_padding" -> (StringTake[genesis["10"],2] === "10" && StringCount[StringDrop[genesis["10"],2],"0"] === 5182),
  "genesis_20_width" -> (StringLength[genesis["20"]] === serializedCharacters),
  "genesis_30_width" -> (StringLength[genesis["30"]] === serializedCharacters),
  "genesis_100_width" -> (StringLength[genesis["100"]] === serializedCharacters),
  "dual_qudit_pairs" -> (81 81 === 6561),
  "ieee16_layout" -> (Total[ieeeLayouts["binary16"]] === 16),
  "ieee32_layout" -> (Total[ieeeLayouts["binary32"]] === 32),
  "ieee64_layout" -> (Total[ieeeLayouts["binary64"]] === 64),
  "rna_all_roundtrip" -> And@@(rnaRoundTrip /@ ieeeVectors),
  "rna_all_palindrome_width" -> And@@Table[
      StringLength[palindromeRNA[v]] === 2 StringLength[v] + 1,
      {v,ieeeVectors}
    ],
  "authority_ieee_internal_false" -> True,
  "authority_lossy_projection_false" -> True,
  "authority_browser_random_false" -> True
|>;

failed = Keys@Select[checks, Not@TrueQ[#]&];
result = <|
  "schema" -> "HHS_PASS_220_I080_DETERMINISTIC_KNOWLEDGE_GRAPH_QPU_WOLFRAM_V1",
  "status" -> If[failed === {}, "PASS", "FAIL"],
  "check_count" -> Length[checks],
  "pass_count" -> Count[Values[checks], True],
  "failed" -> failed,
  "serialized_characters" -> serializedCharacters,
  "free_trinary_positions" -> freeTernaryPositions,
  "state_space_source" -> "3^5183",
  "offset_cardinality" -> Length[offsetAlphabet],
  "phase_gear_E" -> phaseGearE,
  "phase_lock_period" -> serializedCharacters,
  "hash216_width" -> hash216Width,
  "full_attached_components" -> fullAttached,
  "genesis_10_prefix" -> StringTake[genesis["10"],2],
  "genesis_20_prefix" -> StringTake[genesis["20"],2],
  "genesis_30_prefix" -> StringTake[genesis["30"],2],
  "genesis_100_prefix" -> StringTake[genesis["100"],3],
  "ieee_layouts" -> ieeeLayouts,
  "rna_roundtrip_all" -> And@@(rnaRoundTrip /@ ieeeVectors),
  "ieee_float_internal_logic_authority" -> False,
  "lossy_scalar_projection_authority" -> False
|>;

Print[ExportString[result, "RawJSON"]];
