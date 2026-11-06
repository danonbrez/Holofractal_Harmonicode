ClearAll[row,col,spinor,blockRow,blockCol];
row[n_,i_,j_]:=n i+j;
col[n_,i_,j_]:=n j+i;
spinor[r_,a_,c_,b_]:=row[72,18 r+a,18 c+b];
blockRow[t_,c_,b_]:=648 t+8 c+b;
blockCol[t_,b_,c_]:=648 t+81 b+c;
<|"DimensionClosure"->(16*18^2==72^2==81*64),
 "TransposeAll"->And@@Flatten[Table[col[72,i,j]==row[72,j,i],{i,0,71},{j,0,71}]],
 "SpinorRange"->{spinor[0,0,0,0],spinor[3,17,3,17]},
 "BlockAddressCoverage"->(Sort@Flatten@Table[blockRow[t,c,b],{t,0,7},{c,0,80},{b,0,7}]==Range[0,5183]),
 "TransposeCoverage"->(Sort@Flatten@Table[blockCol[t,b,c],{t,0,7},{b,0,7},{c,0,80}]==Range[0,5183])|>
