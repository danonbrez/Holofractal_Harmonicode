(* Wolfram exact arithmetic audit. Not an HHS authority receipt. *)
ClearAll[x,y,z,w,t,l,c,m,ledger,antipode,root];
l={{4,9,2},{3,5,7},{8,1,6}};
c=l-ConstantArray[5,{3,3}];
ledger[x_,y_,z_,w_]:=(x+y-z-w)+(x*y-z*w)+(x^2+z^2-y^2-w^2);
antipode={x->I,y->-I,z->I,w->-I};
m={{x,x^2,y},{y^2,ledger[x,y,z,w],x^4},{w,z^4,z}}/.antipode;
root=Exp[2 Pi I/72];
<|"CenteredLoShuCharacteristic"->Factor[CharacteristicPolynomial[c,t]],
"AntipodeCharacteristic"->Factor[CharacteristicPolynomial[m,t]],
"AntipodeRank"->MatrixRank[m],
"LedgerAtAntipode"->(ledger[x,y,z,w]/.antipode),
"SeedEquality"->(179971179971/1000000==179971*(1000001/1000000)),
"SeedFactor"->(179971==11*16361),
"FourthPowerRootShell"->FullSimplify[root^72==1],
"GatePolynomial"->(x^4*(z*w)^3==y^2)|>
