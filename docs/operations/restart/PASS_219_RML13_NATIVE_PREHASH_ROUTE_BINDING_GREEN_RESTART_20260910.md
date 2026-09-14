# Pass 219 RML13 Native Pre-Hash Route Binding — Green Restart Seal

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Working branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML12 green restart seal: `356b60ef25321e86c6c54f173e3e0a554e7be747`
- RML13 implementation head: `51fcdbd1053fb730964fdcf9a6dec099e4440e16`
- CI dependency repair: `d2b8d7e236bcc5c5172b5146c765bf133b91eab9`
- CI repair checkpoint: `373ca2baf57fe3d91c78e11a603095ab8d2c0543`
- RML13 validated contract seal: `99e1f3b03244629ad49f172985a9f73d1a1db1d1`

## Validation frozen green

Targeted workflow: `Pass 219 RML13 Native Prehash Route Binding`

- first run `34438142834`, job `102747417114`: failed only because the workflow omitted `fastapi`; native build, Pass188, and I168 export had already passed;
- repair commit `d2b8d7e236bcc5c5172b5146c765bf133b91eab9` aligned dependencies with the inherited I168 workflow (`pytest fastapi httpx`);
- green run `34464110690`, job `102828527303`;
- result: `16 passed, 0 failed, 2 warnings in 26.39s`;
- warnings are non-failing inherited/configuration warnings: unknown `asyncio_mode` and FastAPI/Starlette `httpx` deprecation.

Native evidence inside the green gate:

```text
RML13 extension build/export: GREEN
frozen I168 symbol export: GREEN
Pass188 states=1259712
Pass188 active=629856
Pass188 collapse=629856
Pass188 coordinate_drift_states=0
Pass188 checksum=11e3bbf0214751c3
```

## Validated RML13 semantics

RML13 is a versioned native pre-hash witness successor. It serializes the selected RML12 route, selection, bundle, source/target roots, and exact Hopf/Clifford partitions, then binds that witness into the 648-byte VM81 candidate before inherited UQCEL computes `change_hash72`.

Validated causal chain:

```text
RML12 selected route witness
 -> RML13 witness SHA-256
 -> route environment root
 -> VM81 candidate frame
 -> inherited UQCEL change_hash72
 -> previous || change || frozen receipt
 -> transition Hash216 identity
```

Different valid route witnesses change the candidate frame, `change_hash72`, Hash216 triplet, and transition identity. Frozen UQCEL v1 `receipt_hash72` remains unchanged because its historical receipt material does not include the candidate frame; that boundary is explicitly preserved rather than hidden.

## Authority boundary

RML13 adds no second VM81 commit primitive, no optimizer transition authority, no Hash216 persistence authority, no Python Hash72/Hash216 mint authority, no floating-point canonical authority, and no scalar-projection substitution authority. Frozen I162, I168, UQCEL v1, Pass188, and the root runtime Makefile remain unchanged.

## Required next bounded successor

RML14 should close the remaining receipt-side witness gap with a separately versioned receipt successor, not by modifying frozen UQCEL v1. The successor should bind the already-validated RML13 witness root and route-bound change into a new receipt material before constructing a successor Hash216 identity, while preserving the historical UQCEL receipt/hash identities byte-for-byte and retaining the single existing VM81 commit authority.
