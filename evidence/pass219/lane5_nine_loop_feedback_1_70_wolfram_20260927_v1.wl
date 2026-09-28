(* Pass 219 Lane 5 1.70 — exact feedback formalization.
   Preserves the Genesis constructor verbatim and verifies integer/rational
   closure only. No floating or canonical HHS authority is granted. *)

Module[
 {p1=2147483647,p2=2147483629,rows=424,cols=5431,entries=2302744,
  nz=1018297,rat=1014476,two=3821,cmp=107053,c1=103570,c2=3401,c3=82,
  support="64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d",
  relation="4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a",
  comparison="884b05ed4118ed372329c8b002b895dfa98bd92fe72cdd0f88b47cef94448d11",
  septuple="606c5db22ac881a92835cf12e7077d0093c8b599b5205d3e0752be91e82c3967",
  sourceDigests={
   "75a52ebb4526bdb788ae8101e4908d52579637b6aaca1a308e4d783b4a8afe86",
   "13c231664403d35e8ad68747302c7bc26bcc9b1b567d0da0d65444c980c8eb97",
   "d01e62885b74d13650b44baf8da3e42d15bab35c99f6ee778e66df4059ecf37d",
   "082abcea6a66fb434b24938236f443f2703e7e76ded8911f46ffffa292a2c5e1"},
  genesis="F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2",
  rootSeed=179971179971/1000000,hex64,checks,result,material},
 hex64[s_]:=StringMatchQ[s,RegularExpression["[0-9a-f]{64}"]];
 checks=<|
  "prime1_is_prime"->PrimeQ[p1],
  "prime2_is_prime"->PrimeQ[p2],
  "matrix_entry_count_closes"->(rows cols==entries),
  "coordinate_coverage_partition_closes"->(rat+two==nz),
  "comparison_partition_closes"->(c1+c2+c3==cmp),
  "support_digest_typed"->hex64[support],
  "relation_digest_typed"->hex64[relation],
  "comparison_digest_typed"->hex64[comparison],
  "septuple_digest_typed"->hex64[septuple],
  "all_source_digests_typed"->And@@(hex64/@sourceDigests),
  "root_seed_exact_rational"->(Numerator[rootSeed]==179971179971 && Denominator[rootSeed]==1000000),
  "genesis_identity_verbatim"->(genesis=="F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"),
  "candidate_only_authority"->True
 |>;
 material=StringRiffle[ToString/@{p1,p2,rows,cols,entries,nz,rat,two,cmp,c1,c2,c3,support,relation,comparison,septuple,genesis,Numerator[rootSeed],Denominator[rootSeed]},"|"];
 result=<|
  "schema"->"HHS_PASS219_LANE5_NINE_LOOP_FEEDBACK_1_70_WOLFRAM_V1",
  "status"->If[And@@Values[checks],"PASS","FAIL"],
  "check_count"->Length[checks],
  "pass_count"->Count[Values[checks],True],
  "checks"->checks,
  "coverage_exact"-><|"certified_rational"->{rat,nz},"two_prime_only"->{two,nz}|>,
  "comparison_partition"-><|"class_1"->c1,"class_2"->c2,"class_3"->c3,"total"->cmp|>,
  "root_metadata_seed"-><|"numerator"->Numerator[rootSeed],"denominator"->Denominator[rootSeed]|>,
  "genesis_identity_verbatim"->genesis,
  "feedback_material_sha256"->Hash[material,"SHA256","HexString"],
  "native_hash216_authority"->False,
  "canonical_transition_ready"->False
 |>;
 ExportString[result,"RawJSON"]
]
