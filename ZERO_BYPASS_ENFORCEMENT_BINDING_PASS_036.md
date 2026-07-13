# Zero-Bypass Enforcement Binding — Pass 036

Pass 036 binds Pass 035 runtime constraint enforcement to a concrete interposition token.  Enforcement decides admissibility; the interposer turns that admissibility into a surface-scoped token; guarded propagation requires that token before any downstream surface may execute, mutate, serialize, persist, or emit runtime state.
