# Pass 178 native exact physics ABI nucleus

This C11/GNU11 library supplies a bounded public ABI surface for the I148 Pass 178 exact-physics nucleus.

It intentionally does **not** own VM81 admission, Hash72 ordering, Hash216 mutation, browser state, GPU state, filesystem state, or networking. Native commit requires an explicit inherited-VM81 admission witness. The higher-level Python runtime performs the actual inherited VM81 admission before authoritative state is advanced.

Implemented ABI categories include runtime open/close, byte-preserving source identity, model registration, constraint binding, exact fixed-step parameterization, initial-state candidate creation, step candidate/validate/commit, VM81-admitted snapshot projection, immutable render-packet projection, replay cursor operations, measurement-authority rejection, and receipt fingerprint export.

This is an executable nonterminal nucleus, not the terminal Pass 178 physics runtime.
