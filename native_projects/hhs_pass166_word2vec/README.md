# Pass 166 Word2Vec native ABI

This strict C11 companion implements authority-neutral primitives used by the Pass 166 acquisition and import service:

- bounded manifest geometry validation;
- exact signed rational to Q16.16 half-even quantization;
- checked integer dot products for exact similarity ranking;
- fixed 5,184-bit / 648-byte projection frame operations.

It does not download, install, activate, remove, or mutate a model. Canonical activation remains routed through the inherited singleton VM81 runtime.

```bash
make -C native_projects/hhs_pass166_word2vec clean test
```
