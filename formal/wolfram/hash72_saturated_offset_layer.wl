(* Exact candidate 81x64 and 64x81 address/phase saturation checks. *)
ClearAll[f,g,phase,n,genesis,layer1,layer2];
n=5184;
f[s_]:=81 Mod[s,64]+Quotient[s,64];
g[t_]:=64 Mod[t,81]+Quotient[t,81];
phase[k_]:=Mod[k,72];
genesis=Table[phase[Quotient[s,64]+Mod[s,64]],{s,0,n-1}];
layer1=phase/@(genesis+1);
layer2=phase/@(genesis+2);
<|
 "AddressCoverage"->(Sort[Table[f[s],{s,0,n-1}]]===Range[0,n-1]),
 "ForwardRoundtrip"->And@@Table[g[f[s]]==s,{s,0,n-1}],
 "InverseRoundtrip"->And@@Table[f[g[t]]==t,{t,0,n-1}],
 "PhaseInverse"->And@@Table[phase[k+phase[-k]]==0,{k,0,71}],
 "PhaseSaturation"->And@@Thread[layer1!=genesis],
 "DistinctPhaseLayers"->(layer1=!=layer2&&layer1=!=genesis&&layer2=!=genesis),
 "CompositeOffset"->And@@Table[phase[(layer1[[s]]-genesis[[s]])+(layer2[[s]]-layer1[[s]])]==phase[layer2[[s]]-genesis[[s]]],{s,1,n}]
|>
