# Known Issues — Pass 033

- Pass 033 registers the full admissibility stack but does not yet promote real external sensors or live audio streams into the runtime.
- The harmonic-time/audio ECC witness uses exact integer/rational timing and a conservative synthetic sample profile. Pass 034 should audit and wire the existing backend audio/time correction functions directly.
- The BigInt carrier validates lossless Hash72/u^72 state reconstruction but does not yet encode every future u^216 extension channel.
- The Lo Shu, Golay-compatible, reciprocal, and Fibonacci checks are represented as deterministic admissibility gates; future passes should deepen them against the existing specialized modules.
