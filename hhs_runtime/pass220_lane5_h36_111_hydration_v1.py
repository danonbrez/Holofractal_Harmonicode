"""Lane 5 H36 four-Lo-Shu extension: 111 horizon and 6+6 hydration services.

Twelve ordered candidate services inspect six rows then six columns; the two
main diagonals are additional admission checks, not replacements for services.
No canonical Hash72/Hash216 mint or VM81 mutation takes place here.
"""
from hashlib import sha256
import json

MAGIC = 111
SIDE = 6
HYDRATION_SERVICES = tuple(f"H36_ROW_{i}" for i in range(6)) + tuple(f"H36_COL_{i}" for i in range(6))
FINAL = (
    (35,1,6,26,19,24),
    (3,32,7,21,23,25),
    (31,9,2,22,27,20),
    (8,28,33,17,10,15),
    (30,5,34,12,14,16),
    (4,36,29,13,18,11),
)
SWAPS = ((8,35),(4,31),(5,32))

def _swap(grid, left, right):
    positions = {v:(i,j) for i,row in enumerate(grid) for j,v in enumerate(row)}
    if left not in positions or right not in positions:
        raise ValueError("SWAP_OPERAND_NOT_FOUND")
    x,y=positions[left],positions[right]
    grid[x[0]][x[1]],grid[y[0]][y[1]]=grid[y[0]][y[1]],grid[x[0]][x[1]]

def source_quadrants():
    grid=[list(row) for row in FINAL]
    for x,y in reversed(SWAPS):
        _swap(grid,x,y)
    return tuple(tuple(row) for row in grid)

def hydrate_h36(source=None, *, swaps=SWAPS):
    if source is None:
        source=source_quadrants()
    if type(source) not in (list,tuple) or len(source)!=SIDE or any(
        type(row) not in (tuple,list) or len(row)!=SIDE for row in source
    ) or any(type(v) is not int for row in source for v in row):
        raise ValueError("H36_EXACT_6X6_INTEGER_CELLS_REQUIRED")
    source=tuple(tuple(row) for row in source)  # freeze validated caller input
    grid=[list(row) for row in source]
    if sorted(v for row in grid for v in row)!=list(range(1,37)):
        raise ValueError("H36_PERMUTATION_REQUIRED")
    if swaps!=SWAPS:
        raise ValueError("H36_ORDERED_THREE_SWAP_CONTRACT_REQUIRED")
    if tuple(tuple(row) for row in grid)!=source_quadrants():
        raise ValueError("H36_SOURCE_QUADRANT_CONTRACT_REQUIRED")
    visits=[]
    for index,(left,right) in enumerate(swaps):
        _swap(grid,left,right)
        visits.append({"tick":index,"ordered_exchange":(left,right)})
    services=[]
    for index,service in enumerate(HYDRATION_SERVICES):
        values=tuple(grid[index]) if index<6 else tuple(grid[r][index-6] for r in range(6))
        subtotal=sum(values)
        services.append({"name":service,"sum":subtotal,"closed":subtotal==MAGIC})
    diagonals=(sum(grid[i][i] for i in range(6)),sum(grid[i][5-i] for i in range(6)))
    if not all(service["closed"] for service in services) or diagonals!=(MAGIC,MAGIC):
        raise ValueError("H36_GLOBAL_111_CLOSURE_FAILED")
    result={"schema":"HHS_PASS220_H36_111_12_HYDRATION_CANDIDATE_V1",
            "magic_horizon":MAGIC,"hydration_service_count":len(services),
            "services":services,"diagonal_witnesses":diagonals,
            "swaps":visits,"source":source,"completed":tuple(tuple(row) for row in grid),
            "candidate_only":True,"canonical_hash216_minted":False}
    result["candidate_sha256"]=sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return result

def hydrate_service(service_name, source=None):
    if service_name not in HYDRATION_SERVICES:
        raise ValueError("UNKNOWN_H36_SERVICE")
    witness=hydrate_h36(source)
    return witness["services"][HYDRATION_SERVICES.index(service_name)]
