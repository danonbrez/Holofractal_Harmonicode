(* Exact phase-address candidate; not a canonical Hash72 mint. *)
ClearAll[omega,lo,phase,m];
omega=Exp[2 Pi I/72];
lo={{4,9,2},{3,5,7},{8,1,6}};
phase[j_,k_]:=Mod[j-k,72];
m=Table[phase[j,k],{j,0,71},{k,0,71}];
<|"Dimensions"->Dimensions[m],"Cells"->Length[Flatten[m]],
"LoShuRowSums"->(Total/@lo),
"Reciprocal"->And@@Flatten[Table[Mod[m[[j+1,k+1]]+m[[k+1,j+1]],72]==0,{j,0,71},{k,0,71}]],
"RootClosure"->FullSimplify[omega^72==1],"Factorization"->(16*18^2==72^2)|>
