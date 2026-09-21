# Pass 220 I016 — G41 Boundary Hardening

Status: **IMPLEMENTED — EXACT-HEAD GREEN — MERGE PENDING**

This is a repair-forward hardening cycle for the G41 implementation originally
introduced by PR #500 and now inherited on main.

## Restart identity

- Repository: `danonbrez/Holofractal_Harmonicode`
- Base / inherited main: `15f0931606868f5a69327b106b89eb221b43359a`
- Branch: `pass220/i016-g41-boundary-hardening-v1`
- Merge target: `main`

PR #500 is already merged. These findings are therefore repaired forward on
current main rather than treated as an unmerged-PR gate.

## Findings repaired

### 1. Unsupported Sudoku seeds could mint contradictory G41 receipts

The generic Sudoku validator accepts any valid 9x9 Sudoku, but the exact
41-class theorem, fixed center at position 41, and reciprocal
`p <-> 82-p` witness were proved only for `SUDOKU81`.

Repair:

- canonical G41 receipt/class/full-serialization functions now require the
  exact canonical seed;
- other valid Sudoku seeds remain inspectable through generic local
  `fingerprint` calls but cannot mint canonical G41 evidence;
- fixed reciprocal positions are computed from the actual canonical
  fingerprint set before receipt emission rather than inserted blindly.

### 2. Quadratic norm admitted approximate and boolean values

`quadratic3_norm` previously unpacked its input directly and therefore
accepted Python floats and booleans despite the declared no-floating exact
boundary.

Repair:

- exact quadratic pairs now pass through one two-element exact-integer
  validator;
- `quadratic3_norm` and `quadratic3_mul` both reject floats, booleans, and
  malformed pair widths.

### 3. C0 scalar evaluation erased ordered-composite identity

The scalar expression for C0 could accept altered `XY/YX/ZW/WZ` values that
cancelled to the same scalar zero.

Repair:

- `ordered_zero_cell_witness` records all named ordered composites and the
  ordered term sequence;
- the I014 scalar projection admits only the canonical Genesis ordered
  composite tuple:
  `SX=0, SZ=0, XY=1, YX=-1, ZW=1, WZ=-1`;
- scalar-equivalent but differently ordered/composed inputs fail closed;
- direct `c0` scalar override is rejected.

### 4. CI path filters omitted normalization dependencies

The I014 job executes the normalization test but previously did not trigger
when either normalization source or normalization test changed.

Repair:

- I014 push and pull-request filters now include:
  - `hhs_runtime/hhs_pass220_lo_shu_normalization_v1.py`
  - `tests/pass220/test_hhs_pass220_lo_shu_normalization_v1.py`
- I015 filters were also repaired forward to include its inherited I014 and
  normalization runtime/test dependencies.

## Negative regression tests

The G41 suite now explicitly verifies:

- a valid but noncanonical Sudoku cannot mint G41 reachability, class, or full
  serialization receipts;
- `quadratic3_norm` rejects float and boolean coordinates and malformed
  pairs;
- `quadratic3_mul` rejects approximate/boolean coordinates;
- scalar-cancelling but noncanonical C0 ordered composites are rejected;
- direct C0 scalar injection is rejected;
- I014/I015 workflow path filters contain all exact dependencies.

## Changed files

- `hhs_runtime/hhs_pass220_g41_sudoku_fingerprint_algebra_v1.py`
- `tests/pass220/test_hhs_pass220_g41_sudoku_fingerprint_algebra_v1.py`
- `.github/workflows/pass220-i014-g41-sudoku-fingerprint-algebra.yml`
- `.github/workflows/pass220-i015-palindromic-ordered-phase.yml`
- `.github/workflows/pass220-i016-g41-boundary-hardening.yml`
- this checkpoint

## Commits so far

- `426f8bf6ebfb5e2c0858a4712b607f3eab0a0912` — exact runtime boundary hardening
- `0b7fd2dfe75287c91a4a384b1652a0285c4ff8b2` — I014 normalization trigger repair
- `372453aa91231ee5f9c0eb23abfa9c7e2a7b21b8` — I015 inherited trigger repair
- `804ccf6f2a1655974fcc53e79d514a3aae232e93` — negative regression tests
- `f39dd79294d86c1f6c5956239d3f08f545098350` — restartable checkpoint
- `4f7ddd27004ddfda3117497a10874a14b9cf8fd6` — I016 exact-head workflow

## Dependency-scoped validation

PR #503 exact-head results at `4f7ddd27004ddfda3117497a10874a14b9cf8fd6`:

- I014 G41 exact gate `35446513390`: **success**;
- I015 inherited integration gate `35446513408`: **success**;
- I016 hardening exact-head gate `35446513458`: **success**;
- I016 dependency surface: **47 passed**, one pre-existing pytest
  `asyncio_mode` configuration warning.

The I016 gate includes the G41, palindromic ordered-phase, and Lo Shu
normalization suites. All four reported P2 boundaries now have negative
regression coverage.

## Validation remaining

- rerun I016 exact-head after this checkpoint-only documentation commit;
- merge PR #503 if the new head remains green;
- read back and record the resulting main identity.

## Next action

Consume the exact-head result for this documentation checkpoint, then merge and
verify main.

