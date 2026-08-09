# Pass 215 Iteration 18 — Bounded Certified Generation Control

Iteration 18 converts the frozen Iteration 17 witness into a bounded generation-control surface without widening model, prompt, sampling, or mutation authority.

The contracted session has a 4-token authenticated prefix, at most 7 generated tokens, an 11-token context ceiling, fixed 256-bit certified argmax authority, and stop token ID 2. Every selected token is required to reproduce the frozen Iteration 17 chain.

After four generated transitions the runtime serializes an authoritative checkpoint containing the concrete `TerminalHeadSymbolicDAG`/hash-cons state, symbolic K/V cache, interval K/V cache, current complete 32,000-logit interval vector, current 32,000 symbolic logit roots, scalable-RoPE dyadic context and trig cache, generation policy, and per-token receipt chain. Restore round-trips this state through durable JSON, recompiles immutable tensor bindings from the authenticated model, and performs zero prompt or generated-token forward replay.

The successful authenticated source execution reproduced token IDs `[450,6575,471,528,2827,322,278]` / `The sun was shining and the`, terminated at `MAX_NEW_TOKENS`, and independently replayed exactly across two processes.

Source authority:

- head: `f99a1b1e3f66e65a812c335d1e878d4bb67e899a`
- tree: `d364d2c1fff020ade99ad8f6500ede85df2be09b`
- workflow run: `31284766350`
- job: `93171553267`
- cumulative controls: `179`
- checkpoint split: after generated step 4
- checkpoint canonical bytes: `475300933`
- checkpoint Hash216: `bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f`
- restore prefix forward replays: `0`
- restore generated forward replays: `0`
- generation-control Hash216: `309a4e102b6f78338a63c086f536f4d3d62429c77709fa4f9fa9b25d3a6ac509`
- suite Hash216: `bccf558e206bc996d4647533cf310838e1f13cec1322f98c5f22ab5c1ad190d1`
- evidence Hash216: `b89fd35e60428680ac785fa5637f64a2027e4e5c0a1f17f32b88521c7cfb75f9`
- Hash72 receipt: `!ZRAyYb(82+PgZuXyX3!zi4J514L3O+!EUr+aX4ID3tIWThWjg!qa+t)(EPnSk1taEz5!mH5`
- source artifact: `9029578676`, 150,749,123 bytes, ZIP SHA-256 `7cf428973e708b6a734ef972f4c8884000b720e2bd427e621873e322e95279e8`

The 475,300,933-byte canonical checkpoint is intentionally accepted as the exact self-contained Iteration 18 representation. It exposes, rather than hides, the next optimization barrier: exact content-addressed/deduplicated checkpoint state that preserves zero-forward-replay resume while avoiding serialization of redundant symbolic state.

Every generated token receives a Hash216 proof root and a chained Hash72 receipt. Termination is evaluated after each certified append. For the contracted witness token ID 2 is never selected, so termination occurs exactly at the seven-token `MAX_NEW_TOKENS` boundary.

This remains benchmark authority. It does not authorize probabilistic sampling, arbitrary prompts or models, unbounded generation, arbitrary context length, float canonical authority, dense-forward replacement, runtime mutation, canonical mutation, or migration.
