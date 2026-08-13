# Pass 218 Iteration 7 — Durable Evidence Summary

Repository-native workload: `creative_writing/novels/THE_SMALLEST_PERMISSION.md`

- source SHA-256: `42caa64e6d75aeeedb256f8e9c72b773ab9e5e230bcbc63e76bdff59fae37c03`
- structural beats: `61`
- candidate entry ID: `2cb8dffce47850123f6f6878ce8e4c107670e493c4d681963d1fde0051fa2eae`
- VM5184 projection SHA-256: `7496cdb5047f7609397ba06adbc0e9c303efd4d9240f9b6a6198164df70b2baa`
- admitted entry ID: `3c5dd541843037d2e6e5274ea08a6a45359a56e6f5ec8664876491757762cf1b`
- generation-0 canonical root Hash72: `W6!FGa6bVmuhXwZV<Yz8?KPhf+aPvX7F3hOAOX7N-csz*Z6HkPnA6e(CorD>7<cA>B5UV?s8`
- generation-0 checkpoint SHA-256: `b18104ba7eee6912d412ad85115f2348c1b1c5f18e893c24749a7272a4ee78a0`
- generation-0 checkpoint Hash72: `hqMKgQ!*ScH0*C)W4-j4Q82ovjPyImP)yMAOXIlWebb?SwXofF/shR-mCQ<64KHK27<f-2ea`
- generation-0 validation Hash72: `TFvPi4Pmgdyr*2d9P3Vb8)DM2GT7wyAPotVsSFx-T123Y5joZktiz<9JFA-PUasfBPPZeGtX`
- generation-0 manifest Hash72: `qRkJ+p/(dtf8b1fdU31xUZX7Chs1RNwtV+JaQHwB8Ud!M>Po>(OQxPoQm*GRjv))1X1d5mPg`
- generation-0 checkpoint Hash216: `W6!FGa6bVmuhXwZV<Yz8?KPhf+aPvX7F3hOAOX7N-csz*Z6HkPnA6e(CorD>7<cA>B5UV?s8hqMKgQ!*ScH0*C)W4-j4Q82ovjPyImP)yMAOXIlWebb?SwXofF/shR-mCQ<64KHK27<f-2eaTFvPi4Pmgdyr*2d9P3Vb8)DM2GT7wyAPotVsSFx-T123Y5joZktiz<9JFA-PUasfBPPZeGtX`

Validated behavioral evidence:

- generation-0 restart state: `RESTORED_ACTIVE_GENERATION`
- exact canonical root after restart: `true`
- exact VM81 snapshot after restart: `true`
- exact Iteration-6 commit receipt after restart: `true`
- new canonical mutation during restart: `false`
- new authorization minted during restart: `false`
- unchanged checkpoint replay: `DURABLE_CHECKPOINT_IDEMPOTENT_REPLAY`
- second explicit authorization produces a distinct generation-1 canonical root: `true`
- injected pre-manifest failure: `P218_I7_INJECTED_FAILURE_BEFORE_MANIFEST_SWAP`
- manifest byte-identical after injected failure: `true`
- interrupted restart remains on generation 0: `true`
- generation-1 previous checkpoint binds generation-0 SHA-256: `true`
- corrupted active generation recovery: `RECOVERED_PREVIOUS_VALID_GENERATION`
- corrupted-active fallback reconstructs generation 0 exactly: `true`
- source text present in generation-0 persistence: `false`
- source text present in generation-1 persistence: `false`
- source text present in authority artifacts: `false`
- canonical learning commit invoked: `false`
- truth promotion: `false`
- action authority minted: `false`
- verbatim source retained: `false`
- Pass-165 source-retaining path invoked: `false`

The evidence also records the exact inherited Iteration-6 outer receipt label as `HHS-P218-I6-CANONICAL-COMMIT-PAYLOAD-V1`. Iteration 7 preserves that validated serialized form through an explicit compatibility membrane while independently recomputing the embedded Iteration-6 commit Hash72, receipt Hash72, and Hash216.
