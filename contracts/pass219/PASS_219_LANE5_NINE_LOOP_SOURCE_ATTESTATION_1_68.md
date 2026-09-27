# Pass 219 Lane 5 Nine-Loop Source Attestation 1.68

Pass 219 1.68 is the streaming source/provenance successor to 1.67.

It consumes the public Cosmic9 sample artifact as an exact text corpus and verifies every supplied row without floating point. The full public sample contract is 20,400 nonzero weight-18 words plus 230 exact-zero words over the nine-letter alphabet `ah bh ch dh eh fh yu yv yw`. Each nonzero rational must reconstruct to both published 31-bit prime residues.

Source identity is two-stage:

1. SHA-256 the raw sample bytes.
2. Require that digest to equal the sample entry in the simultaneously fetched upstream `MANIFEST.sha256`.

This lets Lane 5 distinguish source-attested data from copied or reformatted equivalents. The raw source digest and the manifest digest are carried separately.

The output is candidate metadata only. It has no VM81 mutation, canonical Hash72, canonical Hash216, persistence, or floating-point authority. A later native composition layer may bind the 1.68 source receipt to the already validated 1.67 Hash216 candidate.

The verifier fails closed on malformed width, alphabet drift, field residue range, uncertified nonzero rationals, rational/residue mismatch, zero-section mismatch, row-count mismatch, duplicate words under the full contract, and manifest checksum mismatch.
