# Pass 219 RML8 Bott8 Native Correspondence — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML7 validated head: `71fa0ef9dd64376862585feb33e61f9e3b815457`
- Parent RML7 validation seal: `429f4f4104deb6f26db4f3129f7e0d6466300f68`
- RML8 implementation: `6ed16bcf65ff7f890845dce0e7d0011945bd7035`
- RML8 tests: `9845865df562ad4f7718fb040d71702bd111f653`
- RML8 contract: `c9795757ced93b3494e152ca30a920e789ec719e`
- RML8 checksum-contract repair: `87e7b0171032c77197934d04c0b4c321cc189f8d`
- RML8 workflow / validation target head: `47854f340aa4910c620ccff11e0c02399605db67`

## Parent validation frozen

RML7 is dependency-scoped validated:

- Workflow: `Pass 219 Exact Hopf Projection`
- Run: `34420516153`
- Job: `102694683447`
- Result: `88 passed, 0 failed, 1 inherited pytest-config warning in 12.20s`
- Complete generator partition: `4` same-base identity cases, `286` base-moving cases, `0` inverse failures.

## RML8 purpose

RML8 does not create a new Bott abstraction. It binds the RML4-RML7 dynamic topology stack to the inherited Pass 187/188 native Bott substrate already present in the repository.

Inherited ordered basis:

```text
B8 = (x,y,z,w,xy,yx,zw,wz)
```

Inherited internal three-bit Bott cell:

```text
H8 = Z2(xy) tensor Z2(zw) tensor Z2(I/Z^72)
q  = 4q2 + 2q1 + q0
```

RML8 requires the RML4 channel order to match this native Pass188 `basis8` order exactly.

## Pass188 projection law preserved exactly

RML8 implements an exact Python transcription of the inherited branchless C law:

```text
m    = ((q >> 2) XOR (q >> 1)) AND 1
mask = m - 1
F(q) = ((q XOR 1) AND mask) AND 7
```

with exact table:

```text
[1,0,0,0,0,0,7,6]
```

The resulting inherited classes remain:

```text
period-two active: x,y,zw,wz
asymmetric projection/collapse: z,w,xy,yx -> x
```

This `basis8` projection is explicitly NOT promoted to the full reversible phase-state authority. RML5 continues to own exact reciprocal phase motion and receipt-visible state ancestry.

## RML7 topology binding

For every balanced/product-admissible RML5 state, RML8 binds together:

```text
8 live u^72 phase coordinates
-> RML6 exact rational S7 point
-> RML7 exact rational S4 Hopf base
-> Pass187/188 B8/H8 ordered basis packet
```

Each of the eight basis rows retains:

- ordered tag;
- current live `phase72` / `u^k` coordinate;
- exact H8 three-bit coordinates;
- inherited Pass188 projection output/classification;
- period-8 grade witness;
- explicit non-authority of the Pass188 projection over the full phase state.

## Period-8 repository-internal correspondence

RML8 implements exact grade closure:

```text
grade(n+8) mod 8 = grade(n) mod 8
```

and requires the ordered B8 tag to be unchanged by the +8 grade shift.

This is a repository-internal Bott8 correspondence witness. It does not, by itself, claim the full classical K-theory Bott periodicity theorem.

## Full native hydration parity

RML8 recomputes the inherited Pass188 hydration over all

```text
1,259,712
```

projected addresses using uint64-compatible integer arithmetic.

Expected exact result:

```text
hydrated states:             1,259,712
period-two active:             629,856
asymmetric collapse:           629,856
gear-preserved:              1,259,712
coordinate drift:                    0
checksum:         0x11e3bbf0214751c3
```

The corrected decimal checksum witness is:

```text
1289080558382961091
```

The RML8 CI also executes the inherited native runtime's own:

```text
make -C native_projects/hhs_pass188_bott_runtime validate
```

so C11, x86_64 assembly parity, no-float disassembly checks, hydrate checksum, Python runtime parity, and surface smoke tests remain authoritative.

## RML7 generator bridge

The RML7 290-case partition is carried through the Bott8 packet without modifying it:

```text
4   same Hopf base
286 base-moving Hopf transport
0   inverse restoration failures
```

B8 ordered identity remains structurally defined for every balanced RML5 state and therefore for every admitted generator target.

## Files added

- `hhs_runtime/pass219/bott8_native_correspondence.py`
- `tests/pass219/test_pass219_bott8_native_correspondence.py`
- `contracts/pass219/PASS_219_RML8_BOTT8_NATIVE_CORRESPONDENCE_1_0.json`
- `.github/workflows/pass219-bott8-native-correspondence.yml`
- `docs/operations/restart/PASS_219_RML8_BOTT8_NATIVE_CORRESPONDENCE_RESTART_20260909.md`

## Validation status at checkpoint creation

- Workflow: `Pass 219 Bott8 Native Correspondence`
- Run: `34425763871`
- Job: `102710529097`
- Validation target head: `47854f340aa4910c620ccff11e0c02399605db67`
- Status: `queued`

No RML8 failure has been observed at checkpoint creation. The branch is checkpointed under the responsiveness policy instead of blocking development on runner availability.

## Required next action

1. Inspect run `34425763871`, job `102710529097`.
2. If green, record native Pass188 validation success, exact Python pass count/time, and promote the RML8 contract to dependency-scoped validated.
3. If red, repair only the affected RML8/native bridge surface and rerun the same dependency scope.
4. After RML8 is green, decide whether the next successor can prove a stronger classical Bott correspondence from the already-validated eight-grade/Hopf/native structure without weakening any existing authority boundary.

Do not rewrite frozen RML1-RML8 parent evidence or inherited Pass187/188 native files in place.
