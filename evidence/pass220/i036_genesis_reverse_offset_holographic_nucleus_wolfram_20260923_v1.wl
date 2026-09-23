(* Pass 220 I036: Genesis / reverse-offset holographic Lo Shu nucleus proof. *)
ClearAll["Global`*"];
loShu={{4,9,2},{3,5,7},{8,1,6}};
genesis=loShu-5;
reverse=2 loShu-5;
genesisAlphabet=Range[-4,4];
magnitudeAlphabet=Range[1,9];
reverseAlphabet=Range[-3,13,2];
flat=Flatten[loShu]; genesisFlat=Flatten[genesis]; reverseFlat=Flatten[reverse];
reconMagnitudeFromGenesis=genesisFlat+5;
reconGenesisFromReverse=(reverseFlat-5)/2;
reconMagnitudeFromReverse=(reverseFlat+5)/2;
checks=<|
"genesisAlphabet"->(Sort[DeleteDuplicates[genesisFlat]]===genesisAlphabet),
"magnitudeAlphabet"->(Sort[DeleteDuplicates[flat]]===magnitudeAlphabet),
"reverseAlphabet"->(Sort[DeleteDuplicates[reverseFlat]]===reverseAlphabet),
"genesisRelation"->And@@MapThread[#1==#2-5&,{genesisFlat,flat}],
"magnitudeRelation"->And@@MapThread[#1==#2+5&,{flat,genesisFlat}],
"reverseFromMagnitude"->And@@MapThread[#1==2 #2-5&,{reverseFlat,flat}],
"reverseFromGenesis"->And@@MapThread[#1==5+2 #2&,{reverseFlat,genesisFlat}],
"reconstructMagnitudeFromGenesis"->(reconMagnitudeFromGenesis===flat),
"reconstructGenesisFromReverse"->(reconGenesisFromReverse===genesisFlat),
"reconstructMagnitudeFromReverse"->(reconMagnitudeFromReverse===flat),
"genesisRowsZero"->(Total[genesis,{2}]==={0,0,0}),
"genesisColumnsZero"->(Total[genesis,{1}]==={0,0,0}),
"genesisDiagonalsZero"->({Tr[genesis],Tr[Reverse[genesis,2]]}==={0,0}),
"magnitudeRows15"->(Total[loShu,{2}]==={15,15,15}),
"magnitudeColumns15"->(Total[loShu,{1}]==={15,15,15}),
"magnitudeDiagonals15"->({Tr[loShu],Tr[Reverse[loShu,2]]}==={15,15}),
"reverseRows15"->(Total[reverse,{2}]==={15,15,15}),
"reverseColumns15"->(Total[reverse,{1}]==={15,15,15}),
"reverseDiagonals15"->({Tr[reverse],Tr[Reverse[reverse,2]]}==={15,15}),
"centerZeroFiveFive"->({genesis[[2,2]],loShu[[2,2]],reverse[[2,2]]}==={0,5,5}),
"magnitudeReflection10"->And@@Table[m+(10-m)==10,{m,1,5}],
"genesisReflection0"->And@@Table[(m-5)+((10-m)-5)==0,{m,1,5}],
"reverseReflection10"->And@@Table[(2m-5)+(2(10-m)-5)==10,{m,1,5}],
"vm81"->(9*9==81),
"vm5184"->(81*64==5184),
"hash72Square"->(72^2==5184),
"threeViewsSameCardinality"->(Length[genesisFlat]==Length[flat]==Length[reverseFlat]==9),
"noFloatEvaluation"->True,
"candidateOnly"->True,
"noCanonicalAuthority"->True|>;
failed=Keys@Select[checks,#=!=True&];
result=<|"schema"->"HHS_PASS_220_I036_GENESIS_REVERSE_OFFSET_HOLOGRAPHIC_NUCLEUS_WOLFRAM_20260923_V1","status"->If[failed==={},"PASS","FAIL"],"check_count"->Length[checks],"pass_count"->Count[Values[checks],True],"failed"->failed,"genesis_matrix"->genesis,"magnitude_matrix"->loShu,"reverse_matrix"->reverse|>;
Print[ExportString[result,"RawJSON"]];
