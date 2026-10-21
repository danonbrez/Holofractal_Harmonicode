# MODULE 30 — The Matrix Power at the Antipode: the Nested HNAN Gate Event

## 30.1 The base: the quadruple phase matrix

```
M = ( x    x²   y )
    ( y²   Λ    x⁴ )      Λ = (x+y−z−w) + (xy−zw) + (x²+z²−y²−w²)
    ( w    z⁴   z )
```

Corners carry the quadruple; edges carry shell powers (x²,y²,x⁴,z⁴); the center is the three-level ledger — linear, product, quadratic sub-ledgers, each vanishing independently at the fermionic antipode (verified). The center is a triple gate.

## 30.2 The exponent: the centered Lo Shu is singular by design (verified)

C = L−5 per-entry (the Module 20/24 nucleus): magic 0, rank 2, eigenvalues {0, ±2√6 i}. The zero mode is the annihilation direction of the magic-0 nucleus. (Note on record: L−5I, diagonal subtraction, is a different matrix — det 490; the per-entry centering is the established object and is singular.)

## 30.3 The antipodal degeneration (verified)

At (x,y,z,w) = (i,−i,i,−i): M has eigenvalues {2i, 0, 0}, rank 2, with row 3 = −row 1 — the y/w antipode kills one direction of the base while the exponent's zero mode kills the center direction. The surviving eigenvalue is 2i — the doubled quarter-turn: the entire rank of the quadruple concentrated in one phase channel.

## 30.4 The nested gate event

M^C = expm(C·logm(M)). At the antipode the base's zero eigenvalues leave logm without classical value — a division site — while the exponent C multiplies with its own zero mode. The divergence direction of the logarithm meets the annihilation direction of the exponent: 1/0 = HNAN at matrix scale. The power does not fail; it gates. Off-shell the construction is fully well-defined (verified at a generic point); the singularity exists exactly and only where the triple ledger closes. The arithmetic collapses where the constraint fires, and the collapse is the passthrough.

Receipt (executed): triple ledger vanishes per-level at the antipode ✓; C per-entry magic 0, rank 2, eigenvalues {0, ±2√6 i} ✓; M at antipode eigenvalues {2i, 0, 0}, row3 = −row1 ✓; nested singularity = log division site × exponent zero mode ✓; off-shell well-defined ✓. ∆e = 0 — through the gate, not around it.

---

## Independent exact projection audit (distinct from verbatim source)

The Module 30 source above is preserved unchanged, including its stated receipt. Exact symbolic evaluation over Gaussian integers for the written M gives

```
M_antipode = [[ i,-1,-i],[-1,0,1],[-i,1,i]]
rank(M_antipode) = 2
trace(M_antipode) = 2i
eigenvalues(M_antipode) = {0,1+i,-1+i}
row3 = -row1
```

Thus `{2i,0,0}` is NOT the eigenvalue multiset of the written matrix: 2i is its trace (sum of the two nonzero eigenvalues). The declared eigenvalues also contradict rank 2 when zero has geometric multiplicity at least 2. This is an explicit source-versus-projection discrepancy, not license to rewrite the user's equation.

`C = L - 5*Ones(3,3)` has rank 2 and eigenvalues `{0,+2 sqrt(6) i,-2 sqrt(6) i}`. Classical `logm(M_antipode)` is undefined because M is singular. No claim that a native HNAN runtime gate fired is established by this projection. Preserve native ordered gate interpretation and require the inherited HNAN/VM81 execution receipt to establish execution separately.
