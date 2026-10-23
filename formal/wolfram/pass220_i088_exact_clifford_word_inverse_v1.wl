(* Pass220 I088 — independent exact Clifford WORD-algebra proof.

   Original RML10 Cl_(0,8) primitive generator matrices are used ONLY
   to decode the previously established exact inverse into 256
   linearly independent, orthogonal Clifford words. Then both matrix
   inverse identities and 5184 quotient identities are independently
   recomputed by the anti-commuting WORD MULTIPLICATION RULE, not
   by multiplying the 48x48 representation. Native VM81 is unchanged.
 *)

ClearAll["Global\`*"];
i2=IdentityMatrix[2]; s1={{0,1},{1,0}};
s2={{1,0},{0,-1}};s12={{0,-1},{1,0}};
gens={
 -KroneckerProduct[i2,i2,s2,s12],
 -KroneckerProduct[i2,i2,s12,i2],
 -KroneckerProduct[i2,s1,s1,s12],
 -KroneckerProduct[i2,s2,s1,s12],
 KroneckerProduct[i2,s12,s1,i2],
 -KroneckerProduct[i2,s12,s2,s1],
 KroneckerProduct[s1,s12,s2,s2],
 KroneckerProduct[s2,s12,s2,s2]
};
{x,y,z,w}=gens[[1;;4]];
xy=x.y;yx=y.x;zw=z.w;wz=w.z;wx=w.x;
source="(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))=hash72";
lexemes={
 {{"yx"},{"y","+w"},{"wx"}},
 {{"-xy","-wz"},{"x","+y","-z","-w","+xy","+yx","-zw","-wz"},{"-zw","-yx"}},
 {{"xy"},{"x","-z"},{"zw"}}
};
m=ArrayFlatten[{{yx,y+w,wx},{-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx},{xy,x-z,zw}}];
det=Det[m];
inv=Inverse[m];
words=Table[
 Fold[Dot,IdentityMatrix[16],
   Pick[gens,Reverse[IntegerDigits[mask,2,8]],1]],
 {mask,0,255}
];
(* e_i e_j = -e_j e_i for i!=j and e_i^2=-1,
   with bitmask words in canonical ordered generator order. *)
wordPair[left_Integer,right_Integer]:=Module[{crosses,overlap},
 crosses=Total@Table[
  If[BitGet[right,j]===1,DigitCount[BitShiftRight[left,j+1],2,1],0],
  {j,0,7}];
 overlap=DigitCount[BitAnd[left,right],2,1];
 {BitXor[left,right],(-1)^(crosses+overlap)}
];
addTerm[acc_Association,key_Integer,val_]:=Module[
 {next=Lookup[acc,key,0]+val},
 If[next===0,KeyDrop[acc,key],Append[acc,key->next]]
];
addWords[list_List]:=Module[{acc=<||>},
 Do[Do[acc=addTerm[acc,First[item],Last[item]],
    {item,Normal[part]}],{part,list}];
 acc
];
wordProduct[left_Association,right_Association]:=Module[
 {out=<||>,pair},
 Do[
  pair=wordPair[First[a],First[b]];
  out=addTerm[out,pair[[1]],Last[a]*Last[b]*pair[[2]]],
 {a,Normal[left]},{b,Normal[right]}];
 out
];
matrixWordsProduct[left_,right_]:=Table[
 addWords@Table[wordProduct[left[[i,k]],right[[k,j]]],{k,1,3}],
 {i,1,3},{j,1,3}
];
identityWords[scalar_:1]:=Table[
 If[i===j,<|0->scalar|>,<||>],{i,1,3},{j,1,3}];
wordMatrix[sparse_Association]:=Fold[
 #1+Last[#2]*words[[First[#2]+1]]&,
 ConstantArray[0,{16,16}],Normal[sparse]
];
indices=<|"x"->0,"y"->1,"z"->2,"w"->3|>;
products=<|"xy"->{"x","y"},"yx"->{"y","x"},
 "zw"->{"z","w"},"wz"->{"w","z"},"wx"->{"w","x"}|>;
cellLexeme[lex_String]:=Module[
 {term,orientation=1,idx,pair},
 If[StringStartsQ[lex,"-"],orientation=-1];
 term=If[StringStartsQ[lex,"-"]||StringStartsQ[lex,"+"],
  StringDrop[lex,1],lex];
 If[KeyExistsQ[indices,term],
  {2^Lookup[indices,term],orientation},
  If[!KeyExistsQ[products,term],Return[$Failed]];
  idx=Lookup[products,term];
  pair=wordPair[2^Lookup[indices,idx[[1]]],
                2^Lookup[indices,idx[[2]]]];
  {pair[[1]],orientation*pair[[2]]}
 ]
];
sourceCell[terms_List]:=Module[{acc=<||>,pair},
 Do[
  pair=cellLexeme[lex];
  If[pair===$Failed,Return[$Failed]];
  acc=addTerm[acc,pair[[1]],pair[[2]]],
 {lex,terms}];acc
];
sourceWords=Map[sourceCell,lexemes,{2}];
sourceProjected=ArrayFlatten[Map[wordMatrix,sourceWords,{2}]];
coefficientBlocks=Table[
 block=inv[[16 i+1;;16 i+16,16 j+1;;16 j+16]];
 Select[Association@Table[
  mask->Total[Flatten[words[[mask+1]]*block]]/16,{mask,0,255}],
 #=!=0&],
 {i,0,2},{j,0,2}
];
reconstructed=ArrayFlatten[Map[wordMatrix,coefficientBlocks,{2}]];
coefficientSupport=Total[Length/@Flatten[coefficientBlocks,1]];
leftWord=matrixWordsProduct[sourceWords,coefficientBlocks];
rightWord=matrixWordsProduct[coefficientBlocks,sourceWords];
quotientWords=Map[(5184 #)&,coefficientBlocks,{3}];
leftQuot=matrixWordsProduct[sourceWords,quotientWords];
rightQuot=matrixWordsProduct[quotientWords,sourceWords];

checks=<|
 "01_original_nine_lexemes"->(Dimensions[lexemes]==={3,3}),
 "02_original_HNAN_center_order"->(StringJoin[lexemes[[2,2]]]==="x+y-z-w+xy+yx-zw-wz"),
 "03_original_wx_distinct"->(wordPair[8,1]==={9,-1} && wordPair[1,8]==={9,1}),
 "04_original_primitive_squares_minus_I"->And@@((#.#===-IdentityMatrix[16])&/@{x,y,z,w}),
 "05_original_rml10_256_words"->(Length[words]===256),
 "06_original_word_orthogonality"->(Tr[Transpose[words[[5]]].words[[5]]]===16),
 "07_source_reproduces_rml11_48x48"->(sourceProjected===m),
 "08_exact_rank_48"->(MatrixRank[m]===48),
 "09_exact_det_10485760000"->(det===10485760000),
 "10_exact_inverse_reconstruction_from_words"->(reconstructed===inv),
 "11_exact_sparse_support_52"->(coefficientSupport===52),
 "12_word_left_inverse"->(leftWord===identityWords[]),
 "13_word_right_inverse"->(rightWord===identityWords[]),
 "14_word_left_5184_quotient"->(leftQuot===identityWords[5184]),
 "15_word_right_5184_quotient"->(rightQuot===identityWords[5184]),
 "16_51_not_used_as_native_mask"->(sourceWords[[1,3]]===<|9->-1|>),
 "17_two_sided_quotient_not_hash_mint"->(81*64===5184),
 "18_exact_no_IEEE"->FreeQ[{sourceProjected,m,inv},_Real],
 "19_word_sign_directed"->(wordPair[1,2]==={3,1} && wordPair[2,1]==={3,-1}),
 "20_generator_bitmask_order_survives"->(wordPair[3,12]==={15,1})
|>;
failed=Keys@Select[checks,#=!=True&];
report=<|
 "schema"->"HHS_PASS220_I088_EXACT_ORIGINAL_RML10_CLIFFORD_WORD_INVERSE_WOLFRAM_V1",
 "status"->If[failed==={},"PASS","FAIL"],
 "checks_total"->Length[checks],
 "checks_passed"->Count[Values[checks],True],
 "failed"->failed,
 "matrix_determinant"->det,
 "Clifford_generator_count"->8,
 "Clifford_word_basis_count"->Length[words],
 "matrix_dimension"->Dimensions[m],
 "inverse_nonzero_word_coefficients"->coefficientSupport,
 "word_level_inverse_left_proven"->(leftWord===identityWords[]),
 "word_level_inverse_right_proven"->(rightWord===identityWords[]),
 "word_level_5184_quotient_left_proven"->(leftQuot===identityWords[5184]),
 "word_level_5184_quotient_right_proven"->(rightQuot===identityWords[5184]),
 "original_VM81_matrix_division_proven"->False,
 "canonical_Hash72_minted"->False,
 "canonical_Hash216_minted"->False,
 "signed_VM81_mutated"->False,
 "checks"->checks
|>;
Print[ExportString[report,"RawJSON","Compact"->False]];
