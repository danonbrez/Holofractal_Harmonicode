# Pass 215 Iteration 10 — Exact Authenticated Text-to-Token Ingress

Iteration 10 advances the frozen Iteration 9 boundary from authenticated token IDs to a contracted UTF-8 text input. It does not replace the repository's generic Pass 165 multimodal tokenizer. Pass 165 remains the reusable HHS source/provenance and lexical-ingress layer; Iteration 10 adds the model-specific translation required to reproduce token IDs from the authenticated GGUF vocabulary and tokenizer scores.

## Frozen parent

Iteration 10 inherits the exact Iteration 9 closure at:

- commit `8a9ca8907edb94d84ce828639145b94a119c2571`
- tree `cc40fca257d1265882cdc3973205a6962117eb40`
- Iteration 9 suite Hash216 `5f544e489fb05cf6675e6034a9acf552d53e1dd83801c6941384de868d9e4a94`
- Iteration 9 evidence Hash216 `71e36d07d2e5c016cfdae8356eb50abb5d750aefc796a2ad3f413d0391d06261`
- Iteration 9 Hash72 receipt `SF>Bd3yVELc5N4?z>34u6tM05-NirTF!PtssI5l3on*)3IzGzwj/4SC48Gtl>PGZ2EN7lKDH`

The Iteration 9 real source execution is re-run and all frozen tokenizer, special-token, embedding, stage, attention, output, DAG, suite, evidence and receipt identities are checked before the text-derived token sequence is admitted.

## Exact score authority

`tokenizer.ggml.scores` is GGUF binary32 storage. Iteration 10 does not call Python floating-point conversion for these values. Each 32-bit storage word is decoded using integer sign/exponent/fraction fields into an exact reduced rational `(numerator, denominator)`. NaN and infinity fail closed.

Pair priority is compared by integer cross multiplication. Equal scores are resolved by the smaller original left position. This means tokenizer merge ordering is deterministic without giving IEEE floating values canonical numeric authority.

## Contracted tokenizer surface

The benchmark prompt is exactly:

`Hello world!`

The supported normalization surface is intentionally narrow:

1. bind the authenticated tokenizer model, vocabulary, token types, special-token metadata and score array;
2. use authenticated `add_space_prefix`, `add_bos_token` and `add_eos_token` settings when present;
3. for absent legacy LLaMA flags, use the explicitly contracted legacy defaults: prefix-space true, BOS true, EOS false;
4. use U+2581 as the whitespace marker only when that marker is present in the authenticated vocabulary;
5. reject a precompiled normalization character map in Iteration 10 rather than pretending to implement it;
6. split the resulting UTF-8 string into deterministic codepoint symbols;
7. repeatedly merge the available adjacent pair having the greatest exact tokenizer score, with left-position tie-breaking;
8. emit authenticated vocabulary IDs, falling back to authenticated byte tokens or the authenticated UNK token when required;
9. require exactly four resulting token IDs. No truncation or padding is permitted.

The exact real-model token IDs are not predeclared. They are frozen only after the authenticated GGUF passes the exact-head workflow.

## Downstream execution

The four text-derived IDs select four exact Q4_0 rows from `token_embd.weight`:

- 162 source bytes per row;
- 9 Q4_0 blocks per row;
- 36 selected blocks total;
- 1,152 exact rational embedding coordinates;
- 648 source bytes read for the selected rows.

Those four embeddings enter the inherited Iteration 9 four-position causal `blk.0` topology. The existing exact RMSNorm, Q/K/V projections, RoPE expression construction, causal score scaling/softmax expression construction, value aggregation, attention output, residuals and gated SiLU FFN topology remain unchanged.

## Authority boundary

Iteration 10 may close the following claims only after real-model exact-head replay:

- contracted UTF-8 text tokenization executed;
- authenticated tokenizer scores bound;
- exact binary32 score ordering executed;
- score-ordered SentencePiece pair merge executed;
- text-derived token IDs fed exact Q4_0 embeddings;
- contracted text-to-`blk.0` forward executed.

It does **not** claim general arbitrary-text tokenizer conformance, arbitrary sequence length, multi-block execution, full-model execution, output logits, sampling/generation, numeric transcendental evaluation, dense-forward replacement, runtime mutation, canonical mutation or migration.
