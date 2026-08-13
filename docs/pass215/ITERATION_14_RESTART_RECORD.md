# Pass 215 Iteration 14 Restart Record

## Frozen parent

- Pass 215 Iteration 13 closure head: `1253bdfaff0eea3688f28ac749df31e4f1613d06`
- Iteration 13 closure tree: `cdf253c6c08d0bf0184b501f0395667c5e2a04c8`
- Iteration 13 full-model-forward root: `c34e78a37f93597adc703c37ecdd59fefb769447946932e0d5eee496b4373dac`
- Iteration 13 evidence root: `ac57c26fe9119f56c11641297e6f6be8f71aae2fd59bc655445d5b07ad34c2a5`
- Iteration 13 receipt: `6a0VdJ2YaxDx6m2RFaI8UxEyyxSi!gW1<xA4bB0OIKrAg*phhTeHRkYh0tWfWvcO1g/*(A<Z`

## Branch state

- Branch: `agent/pass215-transformer-ingestion-benchmark`
- Merge target: `main`
- Draft PR: `#172`
- This restart record is the terminal repository-visible Iteration 14 source state. Its commit must be treated as the closure-head candidate and validated exactly rather than followed by an additional mutation.

## Authenticated source execution

- Source head: `0734e54d0dac5731cfaacde9e4af625805af7608`
- Source tree: `727be9e83ce95e486e99bb5ae0d79b12cc79e01b`
- Workflow: `Pass 215 Iteration 14 Autoregressive Continuation`
- Run: `31272854840`
- Job: `93141646709`
- Result: success
- Cumulative controls: `134 passed`
- Artifact: `9026173852`
- Artifact bytes: `31,739`
- Artifact SHA-256: `2cf3c140b6d076ccdad54b6223397e34f57aba248e87b7e6aa4bf80d8e7bf21b`
- Cross-process replay: exact

## Contracted continuation

Authenticated prefix:

```text
Hello world!
[1, 15043, 3186, 29991]
```

Exact deterministic selection policy:

```text
LEXICOGRAPHIC_MINIMUM_HASH216_LOGIT_ROOT_THEN_TOKEN_ID
```

This orders symbolic logit identities exactly. It is not numerical logit argmax, likelihood ordering, or stochastic sampling.

Selected continuation:

```text
[29009, 7250]
["icación", "▁morning"]
```

Both selected tokens were appended and processed. Cache sequence length advanced from 4 to 6.

## State-reuse evidence

```text
prefix_hidden_rows_recomputed: 0
prior_kv_token_rows_reused: 54
new_kv_token_rows_materialized: 12
```

Two appended positions across all six blocks executed:

```text
linear row transitions: 35,712
linear products: 11,943,936
linear additions: 11,908,224

terminal projection row transitions: 64,000
terminal projection products: 18,432,000
terminal projection additions: 18,368,000
Q8 block-scale applications: 576,000
```

## Frozen semantic identities

```text
selection 0:
1ffdd8c7eaf4adc7f529f435350aa9f4f8b1333ce45e1b009f307fe247a1cffb

selection 1:
30647ae62a968659b525a99a824ae811185ac1c068e49a5df60a813e3d6ebfac

append 0:
0dc88bfad85007f7ff6447680c3c12919fd93aee0f5813e3dbc7bfcb41c04d1b

append 1:
2823ef988909e3c2b5a816a6e54e514d0e025e96fcb88d26df65151907238181

continuation:
21c9ccbe769f818862a4959ee284aafe65af6d0638ce9c05c2ed52c89387b5eb

final symbolic DAG:
27c8c282b7afede7873374b6377df1a763ecf50cfbcc5ff422075cc5d2f91891

suite:
04935537843adbd98d76583be748725a63f1a04852aefee753373778b4616da3

evidence:
5ff6c491e72327e602fad54ea8cdab3e989a033fb8c4be3e40348ab8206a5710

Hash72 receipt:
Afzln*6<JHol646Lz+3mVuowQB)cS673kS(Hx0z*!nSTBoygeMtJpvfN>8AoznG816seDy3H
```

## Authority boundary after exact-head closure

Eligible for promotion only if the terminal workflow reproduces the above identities directly against this restart-state commit:

- exact deterministic symbolic token selection for the contracted witness;
- autoregressive append and continuation;
- per-block append-only K/V reuse;
- two-step generated continuation.

Remain false:

- numerical logit argmax;
- probabilistic sampling;
- general generation;
- arbitrary/general sequence length;
- numerical or approximate transcendental evaluation;
- canonical float interpretation;
- dense-forward replacement;
- runtime mutation authority;
- canonical mutation;
- migration.

## Exact next action

Run the Iteration 14 workflow against exactly this restart-record commit. Accept closure only if the exact-head checkout, all 134 cumulative controls, authenticated source execution A/B, replay comparison, generated token IDs, selection roots, append roots, continuation root, final DAG root, suite root, evidence root, and Hash72 receipt all reproduce unchanged. Do not create another commit after that successful exact-head validation.
