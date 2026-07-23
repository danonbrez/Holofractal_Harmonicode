# Pass 144 — Natural-Language Documentation and Proof-Lemma Corpus

Pass 144 is an append-only documentation release for API and command-line users. It does not alter, replace, weaken, or reinterpret any file inherited from Pass 143.

## Audience

- command-line users;
- API integrators;
- proof engineers;
- auditors;
- researchers working with HARMONICODE algebra, receipts, and constraint-governed execution.

## Release boundary

Pass 144 may add only documentation, white papers, lemma records, documentation indexes, verification reports, and the immutable-parent verifier used to prove that the Pass 143 tree was preserved byte-for-byte.

The parent tree is identified by `reports/pass_144/PASS_143_PARENT_IMMUTABILITY_BASELINE.json`. Every inherited path must preserve its SHA-256 digest and byte size.

## Reading order

1. [User Guide](USER_GUIDE.md)
2. [CLI Manual](CLI_MANUAL.md)
3. [API Manual](API_MANUAL.md)
4. [Invariant Algebra Guide](INVARIANT_ALGEBRA_GUIDE.md)
5. [Receipts and Authority](RECEIPTS_AND_AUTHORITY.md)
6. [Proof Lemma Corpus Guide](PROOF_LEMMA_CORPUS_GUIDE.md)
7. [Terminology and Glossary](GLOSSARY.md)
8. White papers in `whitepapers/pass_144/`
9. Machine-readable lemma corpus in `formal/lemmas/pass_144/`

## Normative status

These documents explain and index inherited behavior. They do not silently create runtime capability. When documentation and executable behavior differ, the discrepancy is an open repair obligation under the inherited governance rules; documentation cannot erase or downgrade the executable or contractual claim.
