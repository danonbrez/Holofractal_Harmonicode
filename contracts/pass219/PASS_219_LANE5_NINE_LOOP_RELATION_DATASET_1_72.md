# Pass 219 Lane 5 Nine-Loop Relation Dataset 1.72

Pass 219 1.72 expands the single source-bound 1.71 training specimen into a deterministic 12-record relation dataset for Lane 5 recognition and mapping work.

The dataset is:

`data/pass219/lane5_nine_loop_relation_dataset_1_72.json`

Canonical SHA-256:

`dd623f4fc778364274e7ba05c914fb441b724ca3ce41a4eb4df4cdc64935d587`

Ordered record-chain SHA-256:

`4a951f76afcd3f759e74263bc9cd0019b50f034bc07e93341b73200e0c85bd6a`

## Record partition

The 12 records are fixed in order and partitioned as:

~~~text
+1 additive/validated = 6
 0 matched/typed      = 4
-1 rejected/incomplete = 2
~~~

The negative records are first-class training data:

1. literal cross-prime NPZ inventory identity is rejected;
2. complete foreign rational reconstruction remains false because 3,821 / 1,018,297 coordinates remain two-prime-only.

The positive records include source attestation, matrix geometry, shared container roles, common E0 support, full comparison closure, and exact modular residue closure.

Neutral/typed records preserve prime-dependent roles, the Genesis constructor boundary, foreign Delta quarantine, and the candidate-only authority membrane.

## Ordered chain

Each record is canonical-JSON SHA-256 hashed. Its ordered chain state is:

~~~text
chain_i = SHA256(chain_(i-1) || record_sha256_i)
chain_-1 = 64 ASCII zeroes
~~~

Reordering any record changes the final chain root and fails admission.

## Native admission

`NineLoopRelationDatasetCellWall` revalidates the complete 1.71 native parent before accepting the dataset. It requires the frozen dataset identity, ordered record-chain root, exact 6/4/2 class partition, source-bound-feature witness, preserved negative examples, and dataset-only scope.

Model-weight-update and learning-commit requests fail closed. The output remains only a candidate Hash216 dataset identity.
