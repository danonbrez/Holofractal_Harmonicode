# Pass 220 V6 — XYZW ordered tensor + 9-cell Lo Shu polynomial grid

Date 2026-10-09. Additive checkpoint, draft PR #754 → main.

Base `3f9b442edbbd4348650994c7ff3d20b200deaa26` on `agent/pass220-ordered-tensor-quotient-20261009`; preserve V1–V5 source histories and native receipts.

The user supplied three mathematical source components. The fixture `contracts/pass220/PASS_220_V6_XYZW_LOSHU_20261009.harmonicode` stores their exact tensor line, exact Unicode `where` clause, and exact final polynomial grid, each with one LF; the explanatory intervening prose is not an algebraic component. The source contains a literal backslash-asterisk `\\*` in `-yB\\*(`: preserve it rather than silently changing to `*`. Native source spelling `xy,zw,yxwz,b^2c^2` is NOT the same as host-scalar commuting products, and the full source requires a registered parser/evaluator before native proof.

The native-byte and exact conditional coordinate projection tests are in `hhs_runtime/hhs_pass220_v6_loshu_projection_v1.py`, `tests/pass220/test_pass220_v6_loshu_projection_v1.py`, `.github/workflows/pass220-v6-xyzw-loshu.yml`. They consume source-verbatim bytes. Exactly 40 `==` occurrences, outer source offsets 243 and 247, 18 ordered matching inner copy occurrences at relative displacement 244. Noncommuting proof is **not** inferred from mere lexical equality.

Conditional rational roots: `a²=1, b²=2, c²=3, d²=5, e²=8, xy=zw=1`. The polynomial matrix then projects exactly, no floats:

```text
4 9 2
3 5 7
8 1 6
```

All sums across the 3 rows, 3 columns and 2 main diagonals are 15. Each value 1..9 is present once. The eight peripheral vertices remain distinct, center nucleus=5. Coordinate values minus nucleus project to `[-1,4,-3;-2,0,2;3,-4,1]`, row/column/diagonal zero-sum.

The rational polynomial `((b⁶-a²)(c²+b⁴))/(d²+b²)` conditionally evaluates to `(7*7)/7=7`. Separately `(xy+zw)/b²=1`. Neither evaluation proves the signed nested `-List(...)` mask equals 1 or evaluates the entire typed quotient. The scalar comparison `P⁴=9` admits multiple branches; `P=sqrt3` needs its real-positive branch assumption. Even commuting scalars `A=1,B=9` satisfy `AB=9` and `A/B!=B/A`, so native operator chirality/noncommutation requires an additional HHS witness.

The CI mediates full three-line Unicode source through **real Lane5 candidate-only ingress**, and builds the existing shared C ABI. It does not borrow the older Pass159/169 native source proof or assert a source-wide 40-gate truth. No canonical VM81 state mutation or Hash72/Hash216 canonical transition/replay occurs. All gate and mask truths remain UNRESOLVED.

Run `python -m pytest -q tests/pass220/test_pass220_v6_loshu_projection_v1.py` and `python -m hhs_runtime.hhs_pass220_v6_loshu_projection_v1 --source contracts/pass220/PASS_220_V6_XYZW_LOSHU_20261009.harmonicode --output artifacts/pass220/v6-loshu/projection.json`.

Next: inspect only the scoped V6 CI; repair impacted code and checkpoint. Then integrate V6 native registered xy/zw/yxwz carrier semantics, signed mask and exact 9-cell placement into 40 source gate witness production under one global denominator, before VM81 signed admission.
