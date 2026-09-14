# Pass 219 RML13 CI Dependency Repair Checkpoint — 2026-09-10

## Lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Working branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML12 green restart seal: `356b60ef25321e86c6c54f173e3e0a554e7be747`
- RML13 implementation head before CI repair: `51fcdbd1053fb730964fdcf9a6dec099e4440e16`
- First RML13 run: `34438142834`, job `102747417114`
- CI dependency repair commit: `d2b8d7e236bcc5c5172b5146c765bf133b91eab9`
- Repair validation run: `34464110690`, job `102828527303`

## First-run failure classification

The first RML13 targeted workflow built successfully and preserved all native parent evidence:

- RML13 versioned native extension build: PASS
- inherited Pass188 native Bott runtime: PASS
- frozen `hhs_exact_pass219_i168_bind_canonical` export: PASS

The only failure occurred during pytest collection because the RML13 workflow installed only `pytest` while the inherited I168 regression imports `FastAPI`.

Observed error:

```text
ModuleNotFoundError: No module named 'fastapi'
```

This is a workflow dependency defect, not an RML13 runtime or algebra defect.

## Repair applied

Only `.github/workflows/pass219-rml13-native-prehash-route-binding.yml` changed.

Dependency installation now matches the inherited I168 workflow:

```text
python -m pip install --disable-pip-version-check pytest fastapi httpx
```

No RML13 C source, ABI header, Python bridge, tests, contract, I162, I168, UQCEL v1, Pass188 source, or root runtime Makefile changed in this repair.

## Repair-run state at checkpoint creation

Run `34464110690`, job `102828527303` is executing against exact repair head `d2b8d7e236bcc5c5172b5146c765bf133b91eab9`.

Already green inside this run:

- dependency installation;
- frozen runtime + RML13 native-extension build;
- inherited Pass188 native validation;
- frozen I168 export check.

Remaining at checkpoint creation:

- combined RML12/RML13/I168 pytest dependency scope.

## Required next action

Inspect run `34464110690` only.

- If green: freeze exact pytest count/timing and native evidence into the RML13 contract and restart record, create a green RML13 seal, update PR #414, then advance to the next bounded successor.
- If red: repair only the newly exposed impacted RML13/validation surface and rerun the same dependency scope.

Do not rerun validated RML1-RML12 surfaces except where already dependency-scoped into this targeted gate. Do not merge PR #414 from this checkpoint alone.
