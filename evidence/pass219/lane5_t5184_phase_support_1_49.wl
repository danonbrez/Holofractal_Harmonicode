Module[
 {x,y,z,w,alpha,triples,pairs,phasePairs,supportOps,counts,countsVM81,mask,checks,audit,json},
 x={{0,1},{1,0}};
 y={{0,-1},{1,0}};
 z=x; w=y;
 alpha={"x","y","z","w"};
 triples=Tuples[alpha,3];
 pairs=StringJoin@@Take[#,2]& /@ triples;
 phasePairs={"xy","yx","zw","wz"};
 supportOps=Flatten@Position[pairs,Alternatives@@phasePairs]-1;
 counts=Counts[Select[pairs,MemberQ[phasePairs,#]&]];
 countsVM81=Association@KeyValueMap[#1->81 #2&,counts];
 mask=Total[2^supportOps];
 checks=<|
   "x2"->(x.x==IdentityMatrix[2]),
   "y2"->(y.y==-IdentityMatrix[2]),
   "anticommutator"->(x.y+y.x==ConstantArray[0,{2,2}]),
   "zwEqualsXY"->(z.w==x.y),
   "wzEqualsYX"->(w.z==y.x),
   "yxEqualsMinusXY"->(y.x==-x.y),
   "operation64Count"->(Length[triples]==64),
   "phaseSupportPerCell"->(Length[supportOps]==16),
   "phaseBypassPerCell"->(64-Length[supportOps]==48),
   "phaseSupportAcrossVM81"->(81 Length[supportOps]==1296),
   "phaseBypassAcrossVM81"->(81 (64-Length[supportOps])==3888),
   "supportEquals36Squared"->(81 Length[supportOps]==36^2),
   "supportEquals18Times72"->(81 Length[supportOps]==18*72),
   "pairCountEachPerCell"->(Values[counts]==ConstantArray[4,4]),
   "pairCountEachAcrossVM81"->(Values[countsVM81]==ConstantArray[324,4]),
   "pairCountEachEquals18Squared"->(Values[countsVM81]==ConstantArray[18^2,4]),
   "supportFraction"->(Length[supportOps]/64==1/4),
   "complementFraction"->((64-Length[supportOps])/64==3/4)
 |>;
 audit=<|
  "schema"->"HHS_PASS_219_LANE5_T5184_PHASE_SUPPORT_WOLFRAM_AUDIT_1_49",
  "supportOps"->supportOps,
  "supportMaskInteger"->mask,
  "supportMaskHex"->IntegerString[mask,16,16],
  "countsPerCell"->counts,
  "countsVM81"->countsVM81,
  "orderedProducts"-><|"xy"->x.y,"yx"->y.x,"zw"->z.w,"wz"->w.z|>,
  "checks"->checks,
  "checkCount"->Length[checks],
  "passedCount"->Count[Values[checks],True],
  "allPassed"->And@@Values[checks]
 |>;
 json=ExportString[audit,"RawJSON","Compact"->True];
 Export["evidence/pass219/lane5_t5184_phase_support_1_49.output.json",json,"String"];
 Print[json];
]
