# Post-promotion filesystem-ledger repair restart record — 2026-10-03

## Authority and branch

- repository: `danonbrez/Holofractal_Harmonicode`
- authoritative base / merge target: `main`
- base commit: `341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`
- repair branch: `repair/post-promotion-filesystem-ledger-20261003`
- preceding checkpoint: `checkpoint/post-promotion-filesystem-ledger-20261003`
- preceding checkpoint commit: `e9a8ea754adc50a8479e09dd2ad69ab984ffc20e`

## Repair implemented

The post-promotion dirty-check remains fail-closed. The repair changes only candidate validation state placement and its current Pass 202 successor identity.

`deployment/digitalocean/guarded_auto_update/validate-candidate.sh` now:

- creates or accepts an explicitly isolated candidate-state root;
- derives the candidate filesystem ledger outside the repository checkout;
- rejects any candidate ledger path resolving inside the repository checkout;
- launches the production gateway with explicit
  `HHS_FILESYSTEM_LEDGER_PATH=<external candidate ledger>`;
- fingerprints tracked `data/runtime/hhs_filesystem_ledger.json` before and after candidate boot;
- fails candidate validation if that tracked ledger changes;
- removes an internally-created disposable candidate-state directory during cleanup.

Production service authority is unchanged:

`HHS_FILESYSTEM_LEDGER_PATH=/var/lib/hhs/data/runtime/hhs_filesystem_ledger.json`

The Exact-Main post-promotion assertion remains unchanged and still rejects any dirty production checkout.

## Pass 202 identity handling

Historical Pass 202 identities are unchanged.

The validator's new current-successor blob is:

`18febf52f56a794edb25bcd0ee18d0f3a9c1dcf5`

That current-successor value is resealed in:

- `.github/workflows/pass219-cumulative-pass202-membrane-i122.yml`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i122_pass202.py`

The membrane also requires the external ledger binding and tracked-ledger mutation guard tokens.

## Changed files

- `deployment/digitalocean/guarded_auto_update/validate-candidate.sh`
- `tests/test_hhs_guarded_auto_update_contract_v1.py`
- `.github/workflows/pass219-cumulative-pass202-membrane-i122.yml`
- `hhs_runtime/hhs_pass219_cumulative_pass_membrane_i122_pass202.py`
- this restart record

## Repository operations completed

Connected GitHub operations created the repair branch and committed the repair as four source/test/membrane commits before this restart record.

Implementation commits:

- `16f13dc52fc9f183508c2de045d4738ff9fee6ca` — externalize candidate filesystem ledger;
- `08f9aeadfff1b689014258ed9d3fee28549d3fac` — lock candidate ledger isolation regression contract;
- `5f5b5cae6193c5ccf32c9f28f35d0bcb196c8920` — reseal workflow current-successor validator identity;
- `7ba9e3974c52c0d40b389f6814d6ebb2465aae24` — bind kernel membrane current-successor identity and ledger guard tokens.

## Validation completed

- base/main freshness confirmed at `341b31e9f3e7e6332d3cbb3c00c80a0b38e7d784`;
- repair branch is ahead of base only by the intended source/test/membrane commits;
- modified path set is dependency-scoped to candidate validation and Pass 202 successor resealing;
- historical Pass 202 blob table was not modified;
- production service ledger path was not modified;
- Exact-Main post-promotion dirty-check was not weakened or removed.

## Validation remaining

1. open repair PR against `main`;
2. run exact-head required workflows, including Pass 202 exact/synthetic, Exact-Main deployment contract, Runtime OS production root, unified chatbot/Lane 5, Hash216 index, source integrity, and full IDE where path filters apply;
3. confirm candidate validation executes with the isolated ledger and its tracked-ledger fingerprint guard remains green;
4. merge only with expected-head protection after exact-head gates are green;
5. follow the merge-triggered Hash216 projection and require explicit Exact-Main redispatch for any generated current-main commit;
6. require authoritative Exact-Main promotion receipt `PROMOTED`;
7. verify post-promotion production checkout is clean;
8. verify production SHA equals authoritative current `main`;
9. verify `hhs.service`, Lane 5 socket/service, listener topology, nginx zero-bypass, and public HTTPS closure.

## Separate repair-forward item

The Pass 220 LiteRT1 Native Model Runtime C++ compile defect remains separate and is not modified by this repair.
