# Pass 036 — Zero-Bypass Runtime Interposer

Pass 036 converts runtime constraint enforcement into mandatory interposition for propagation-capable surfaces.  Pass 035 exposed the enforcement decision; Pass 036 requires an admissible interposition token before downstream propagation can proceed.

## Summary

- Propagation surfaces declared: `10`
- Scenarios exercised: `12`
- Allowed records: `4`
- Rejected records: `8`
- Direct bypass rejections: `6`
- Wrong-surface token rejected: `True`
- Terminal-value interposition rejected: `True`
- Canonical interposition admitted: `True`
- Rule-following brute force reclassified: `True`
- Any uninterposed propagation allowed: `False`
- Ledger verified: `True`

## Runtime invariant

No ingress, service dispatch, plugin invocation, authorized execution, SRCG closure, semantic-memory write, vector-cache write, persistence write, API egress, or websocket broadcast may propagate without a prior admissible zero-bypass interposition token.
