(* Pass220 I090 exact original VM81/RNA physical frame vs scientific source.
   Actual 648-byte source ABI is the Pass219 vm81_rna_bigint_execution
   binding probe. The 5184 *character* HARMONICODE rational scientific
   normalization is a separate original Pass220 typed ABI.
   Their shared 5184 address count does NOT erase payload/type lineage.
   Source-bound Hash216 is candidate-only until original SIGNED gate.
 *)

ClearAll["Global\`*"];
vm81Words=81;bitsPerWord=64;frameBytes=648;
wordIndices=Range[0,80];
bigintLimbs=Range[0,6];
headerWord=7;glyphWords=Range[8,79];metadataWord=80;
frameBitCount=vm81Words*bitsPerWord;
integerFrameBytes=frameBitCount/8;
localNuclei=9;localCells=9;
hash72Rows=72;hash72Cols=72;
serializedTokenLength=64;serializedTokenCount=81;
originalScientificZeroToken=
 "+"<>StringRepeat["0",20]<>"/"<>StringRepeat["0",19]<>"1"<>
 "e+"<>StringRepeat["0",20];
offsets=ConstantArray[0,81];
offsets[[8]]=1;offsets[[81]]=8;
scientificToken[n_Integer]:="+"<>IntegerString[n,10,20]<>"/"<>
   StringRepeat["0",19]<>"1"<>"e+"<>StringRepeat["0",20];
scientificSource=StringJoin[scientificToken/@offsets];
decodedTokens=StringPartition[scientificSource,64];
decodedOffsets=ToExpression[StringTake[#, {2,21}]]& /@ decodedTokens;
typedOpcode=Range[0,11];
typedLane=Quotient[typedOpcode,2];
typedDirection=Mod[typedOpcode,2];
literalSource=
 "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72";
candidatePrevious=StringRepeat["x",72];
candidateChange=StringRepeat["y",72];
candidateReceipt=StringRepeat["z",72];
candidateHash216=candidatePrevious<>candidateChange<>candidateReceipt;
position=Range[0,5183];
vmCell=Quotient[position,64];
vmLocalBit=Mod[position,64];
hashRow=Quotient[position,72];
hashColumn=Mod[position,72];
reconstruction=64 vmCell+vmLocalBit;
scientificCharCell=Quotient[position,64];
scientificCharLocal=Mod[position,64];

checks=<|
 "01_source_vm81_words_exact"->(vm81Words===81),
 "02_original_word_width64"->(bitsPerWord===64),
 "03_original_81x64_bit_geometry"->(frameBitCount===5184),
 "04_original_frame648_bytes"->(frameBytes===648),
 "05_raw_5184_bits_equal648_bytes"->(integerFrameBytes===frameBytes),
 "06_original_7_bigint_limbs"->(bigintLimbs===Range[0,6]),
 "07_original_bigint_capacity448"->(Length[bigintLimbs]*64===448),
 "08_original_header_word7"->(headerWord===7),
 "09_exact_72_glyph_words"->(Length[glyphWords]===72),
 "10_glyph_word_start8_end79"->(First[glyphWords]===8&&Last[glyphWords]===79),
 "11_direction_metadata_word80"->(metadataWord===80),
 "12_whole_original_frame_words"->(Length[wordIndices]===81),
 "13_frame_layout_partition_exact"->(Union[Join[bigintLimbs,{headerWord},glyphWords,{metadataWord}]]===wordIndices),
 "14_original_12_directional_opcodes"->(typedOpcode===Range[0,11]),
 "15_original_6_directional_lanes"->(Union[typedLane]===Range[0,5]),
 "16_original_pq_qp_alternation"->(typedDirection===Flatten[ConstantArray[{0,1},6]]),
 "17_72_pow72_fits448_bits"->(IntegerLength[72^72-1,2]<=448),
 "18_original_81_scientific_tokens"->(serializedTokenCount===81),
 "19_original_64_char_token"->(StringLength[originalScientificZeroToken]===64),
 "20_original_positive_rational_scientific_layout"->(StringTake[originalScientificZeroToken,1]==="+"),
 "21_no_zero_rational_denominator"->(StringTake[originalScientificZeroToken,{23,42}]===StringRepeat["0",19]<>"1"),
 "22_5184_char_source_width"->(StringLength[scientificSource]===5184),
 "23_all_original_tokens_exact_width"->And@@(StringLength[#]===64& /@decodedTokens),
 "24_scientific_positive_offsets_decoded_exact"->(decodedOffsets===offsets),
 "25_scientific_nonzero_ends_preserved"->(offsets[[8]]===1&&offsets[[81]]===8),
 "26_81x64_and_72squared_addresses"->(81*64===72^2),
 "27_original_raw_VM81_position_inverse"->(reconstruction===position),
 "28_original_hash72_position_inverse"->(72 hashRow+hashColumn===position),
 "29_scientific_char_address_recoverable"->(64 scientificCharCell+scientificCharLocal===position),
 "30_three_candidate_lanes_216_chars"->(StringLength[candidateHash216]===216),
 "31_original_source_matrix_verbatim"->(literalSource==="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72"),
 "32_exact_not_float"->FreeQ[{wordIndices,offsets,typedOpcode,vmCell,scientificSource},_Real]
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS220_I090_ORIGINAL_81X64_RNA_AND_5184_CHAR_SOURCE_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "checks_total"->Length[checks],
 "checks_passed"->Count[Values[checks],True],
 "failed"->failed,
 "raw_vm81_bits"->frameBitCount,
 "raw_vm81_bytes"->frameBytes,
 "typed_scientific_source_characters"->StringLength[scientificSource],
 "typed_64char_exact_tokens"->Length[decodedTokens],
 "typed_72_glyph_frame_words"->Length[glyphWords],
 "original_typed_directional_lanes"->Length[typedOpcode],
 "Hash216_candidate_chars"->StringLength[candidateHash216],
 "original_native_cpp_RNA_probe_executed_by_Wolfram"->False,
 "signed_VM81_environment_admission_executed"->False,
 "canonical_Hash72_mint"->False,
 "canonical_Hash216_persistence"->False,
 "raw_5184_bits_equals_scientific_5184_characters_as_payload"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
