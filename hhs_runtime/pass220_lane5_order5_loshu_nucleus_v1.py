"""Candidate 5x5 magic-square placement in the inherited 9x9 Lo Shu nucleus.

The 25 cells occupy rows/columns 2..6 in the 81-cell VM81 topology.
This is a proposed placement map, not a change to Genesis ROM addresses.
"""
SIDE=5
MAGIC=65
VM81_SIDE=9
OFFSET=2
SUPPORTED_ORDERS=(2,3,4,6,8,9)

def build_order5():
    cells=[[0]*SIDE for _ in range(SIDE)]
    row,col=0,SIDE//2
    for value in range(1,SIDE*SIDE+1):
        cells[row][col]=value
        nr,nc=(row-1)%SIDE,(col+1)%SIDE
        if cells[nr][nc]:
            row=(row+1)%SIDE
        else:
            row,col=nr,nc
    return tuple(tuple(line) for line in cells)

def hydrate_order5_in_loshu(square=None):
    if square is None:
        square=build_order5()
    if len(square)!=5 or any(len(line)!=5 for line in square) or any(
        type(v) is not int for line in square for v in line):
        raise ValueError("ORDER5_EXACT_MATRIX_REQUIRED")
    if sorted(v for line in square for v in line)!=list(range(1,26)):
        raise ValueError("ORDER5_EXACT_PERMUTATION_REQUIRED")
    rows=tuple(sum(line) for line in square)
    columns=tuple(sum(square[r][c] for r in range(5)) for c in range(5))
    diagonals=(sum(square[i][i] for i in range(5)),
               sum(square[i][4-i] for i in range(5)))
    if rows!=(MAGIC,)*5 or columns!=(MAGIC,)*5 or diagonals!=(MAGIC,MAGIC):
        raise ValueError("ORDER5_MAGIC_CLOSURE_REQUIRED")
    addresses=tuple((OFFSET+r)*VM81_SIDE+(OFFSET+c) for r in range(5) for c in range(5))
    assert len(set(addresses))==25 and min(addresses)>=0 and max(addresses)<81
    return {"schema":"HHS_PASS220_ORDER5_LOSHU_NUCLEUS_CANDIDATE_V1",
            "matrix":square,"magic_horizon":MAGIC,"rows":rows,
            "columns":columns,"diagonals":diagonals,
            "vm81_cell_addresses":addresses,
            "existing_order_circuits":SUPPORTED_ORDERS,
            "candidate_only":True,"genesis_rom_mutated":False,
            "hash72_minted":False,"hash216_minted":False}
