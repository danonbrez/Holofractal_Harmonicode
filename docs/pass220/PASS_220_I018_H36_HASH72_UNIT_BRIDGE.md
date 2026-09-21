# Pass 220 I018 — H36 / HASH72 Unit Bridge

Status: **MERGED AT I018 — REVIEW REPAIR-FORWARD IN PROGRESS**

## Restart identity

- Base main: `0d34e94698fed76321dceafe2cf64356cb6dc099`
- Branch: `pass220/i018-h36-hash72-unit-bridge-v1`
- Merge target: `main`
- I017 post-merge exact gate `35451029925`: success.

## Objective

Join the new exact unit-ratio relation

```text
(e/H36=(mc^2)/u^144)
=(a^2/P^4)*(c^2(a^2+b^2))
=(xy+zw)/(q-p)
```

to the already-merged I017 constraint manifold and existing Pass 219 H36/UCE
surfaces.

## Projection closure

Exact Wolfram audit before implementation: **10/10** checks green.

Repository projection target:

```text
H36 = 36
u^144_projection = HASH72_projection = 36
P^4 = 9 != 1
P^2-pq = 1
xy+zw = 2
q-p = 2
all four ratios = 1
```

The typed `mc^2` compound is preserved; I018 deliberately does not solve the
native `m` symbol. The typed `e` symbol is likewise not rebound to any
unrelated basis symbol.

## Files

- `hhs_runtime/hhs_pass220_h36_hash72_unit_bridge_v1.py`
- `tests/pass220/test_hhs_pass220_h36_hash72_unit_bridge_v1.py`
- `hhs_runtime/hhs_service_registry_v1.py`
- `.github/workflows/pass220-i018-h36-hash72-unit-bridge.yml`
- `whitepapers/HHS_PASS220_H36_HASH72_UNIT_BRIDGE_V1.md`
- this restart record

## Commits

- `4e0b74a38112d603b21637b4f18c896ac46b02c5` runtime bridge
- `940507498bcf60a78c123fccdf578d4899d9c4ad` negative/exact tests
- `d29c5d8e505e6b7dd40068445d8e3211bce81514` service registration
- `4b5e137f5ef7a342a7eb59224d7918beae11932a` exact-head workflow

## Remaining

Create the whitepaper/restart commits, open the PR, run the I018 dependency
surface, repair forward if needed, merge, and verify main.


## September 19 review repair-forward

Branch: `pass220/repair-i018-i020-proof-closure-v1`  
Base main: `857e41a868634f8c7c7906ba249b8614e9115981`

The repair closes the five post-merge findings:

1. `u^144` is derived independently from the H36 left branch and the
   `72*(b^2/a^4)=144` exponent path, then compared with the separate I017
   HASH72 projection.
2. `mc^2` is independently evaluated from the H36 right branch, so the
   `mc^2/u^144` ratio no longer reuses one value.
3. the complete ordered witness
   `(sx,sz,xy,yx,zw,wz)=(0,0,1,-1,1,-1)` is enforced through I017.
4. the UCE source SHA-256 is recomputed and compared with the pinned native
   UQCEL digest `7eb0cc...3d42`.
5. I018 workflow triggers now include the inherited I014/I015 runtime/tests and
   native UCE digest dependencies.

Reproducible Wolfram input, output, command, and receipt are committed under
`evidence/pass220/i018_repair_wolfram_audit_v1.*`.
