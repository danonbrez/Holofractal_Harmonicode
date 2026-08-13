# Pass 215 Iteration 18 Restart Record

- Parent closure: `3d46b0eb233c6f450fa7d939e8b864a6651d3465`
- Parent tree: `687db9f718d2b54c3962ecc8bbb62f49090407c9`
- Branch: `agent/pass215-transformer-ingestion-benchmark`
- Merge target: `main`
- PR: #172
- Contract: `HHS-P215-I18-BOUNDED-CERTIFIED-GENERATION-CONTROL`

## Implemented surfaces

Iteration 18 implements bounded generation policy, deterministic stop/max/context termination, durable symbolic+interval execution checkpoints, JSON durability, concrete `TerminalHeadSymbolicDAG` restoration, zero-forward-replay resume, chained per-token proof receipts, validation, CLI, CI, contract and evidence records.

## Repair-forward lineage

1. `aac1cf3fc2d46f3ceb46cd949e1c72bece31d6aa`, run `31284451616`, job `93170795653`: cumulative validation and model authentication passed; real Process A reached checkpoint restore and failed because restore instantiated the older `SymbolicDAG`, which lacks inherited `powq` support. Repaired by restoring the exact `TerminalHeadSymbolicDAG` class.
2. `845a3d2367941080efac5c3a6bf55290a5cb7b93`, run `31284717765`, job `93171436584`: static tests failed because Python `import *` excludes underscore-prefixed helpers. Repaired by addressing inherited private helpers through the v1 module explicitly. Runtime restore code was unchanged.
3. `f99a1b1e3f66e65a812c335d1e878d4bb67e899a`, tree `d364d2c1fff020ade99ad8f6500ede85df2be09b`, run `31284766350`, job `93171553267`: successful source authority.

## Successful source authority

- 179 cumulative controls passed.
- authenticated model SHA-256: `6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04`
- selected IDs: `[450,6575,471,528,2827,322,278]`
- tokens: `["▁The","▁sun","▁was","▁sh","ining","▁and","▁the"]`
- termination: `MAX_NEW_TOKENS`
- checkpoint after completed step: `4`
- checkpoint canonical bytes: `475300933`
- checkpoint Hash216: `bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f`
- prefix forward replays during restore: `0`
- generated forward replays during restore: `0`
- generation-control Hash216: `309a4e102b6f78338a63c086f536f4d3d62429c77709fa4f9fa9b25d3a6ac509`
- suite Hash216: `bccf558e206bc996d4647533cf310838e1f13cec1322f98c5f22ab5c1ad190d1`
- evidence Hash216: `b89fd35e60428680ac785fa5637f64a2027e4e5c0a1f17f32b88521c7cfb75f9`
- Hash72 receipt: `!ZRAyYb(82+PgZuXyX3!zi4J514L3O+!EUr+aX4ID3tIWThWjg!qa+t)(EPnSk1taEz5!mH5`
- artifact: `9029578676`, 150,749,123 bytes, ZIP SHA-256 `7cf428973e708b6a734ef972f4c8884000b720e2bd427e621873e322e95279e8`
- independent replay: true
- semantic exactness: true

## Frozen per-token proof chain

Hash216 token proofs:

1. `58005dd4a6308a290a2aecf80d6eb2df34b25eb98fc29bdd0e84d52fc9f2978c`
2. `3e5df3e1cfdd1eefc5f1c7baf12282e259640eb6d98020e29d3b6bdecc737603`
3. `7dadc585ff4b9ad00de1d65bfd8490366e192c2025bb2b4e5ca189a703c305e1`
4. `facaec23d59b2e0dbdd4e0d46f1fabbab6f8a7b014c0eaab08502d48ea409d93`
5. `8d1815f573d6d9cb422d0920b001c07a55cac70269ce4197f7ab8965ac83e7cb`
6. `e49ca11ba07579f1ce0eba155b8f1f29ea155d637b78e4898243bfcef5ff6089`
7. `aeb16bff69406410fc8549853aff7359c7eebdab36003c98758c8c6ab019e608`

Terminal per-token Hash72 receipt: `cGF-Ca!gMbH75Px9aQG3Qm1)dC)wsS!!2jTWNu!(2BkEeX+Qn3p3/KYB5hGKvgMB(G>t1lfj`.

## Remaining closure action

Create this restart-state freeze commit, then exact-head replay it through `Pass 215 Iteration 18 Bounded Generation Control`. If the exact-head workflow reproduces the frozen semantic identities, do not create another commit. Retain the terminal artifact as external closure evidence.

The next iteration barrier is checkpoint compaction/content addressing. Do not alter the validated 475,300,933-byte Iteration 18 checkpoint representation during this closure.
