# Pass 220 Module 29: canonical Siamese traversal and reciprocal matrices

## Source expression (verbatim)

```
List(NcalcMatrixPower((I^List(List(List(List(1,x,2),List(w,z,y),List(4,z,3)),List(List(-x,1,-y),List(4,y,2),List(-w,3,-z))),List(List(List(4,3,3),List(2,z,4),List(1,1,2)),List(List(w,3,-z),List(2,w,4),List(-x,1,y))))/List(List(4,9,2),List(3,5,7),List(8,1,6))),(-1)),I^List(List(List(List(1,x,2),List(w,z,y),List(4,z,3)),List(List(-x,1,-y),List(4,y,2),List(-w,3,-z))),List(List(List(4,3,3),List(2,z,4),List(1,1,2)),List(List(w,3,-z),List(2,w,4),List(-x,1,y))))/List(List(4,9,2),List(3,5,7),List(8,1,6)))
```

The expression is an ordered typed native source statement: gate operations, fraction bindings and matrix power are not silently replaced with scalar division or inverse. Its proposed reciprocal two-matrix mapping into the 72 outer Sudoku cells is a distinct unverified native integration claim.

## Deterministic canonical traversal

Zero-based origin (0,4), 81 steps of cell placement k=1..81; ordinary displacement (-1,+1) modulo 9, occupied-target displacement (+1,0) modulo 9. All 81 cells once, magic sum 369 across 9 rows, 9 columns, 2 main diagonals. Of 80 inter-cell transitions exactly 72 are ordinary and 8 breaks, after k=9,18,27,36,45,54,63,72. There are nine arcs of 9 cells. These are independent exact combinatorial checks and not native VM81 transition/Hash216 receipts. Distinct Sudoku digit weave not assumed equal to mod9 projection.
