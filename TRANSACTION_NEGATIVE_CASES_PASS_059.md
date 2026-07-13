# Transaction Negative Cases Pass 059

```json
{
  "negative_cases": {
    "epoch_mismatch": {
      "authority": "HHS_I019_CANONICAL_FEDERATED_TRANSACTION_AUTHORITY_V1",
      "canonical_completion": false,
      "commit_decision_root_hash72": "vEsN4Y8C3gnRHJnkvd37g)T<8Gi4CJnN9xDyqfSsJWefofj4+)YWlvqrtGI<wjvfI4g+D/ra",
      "commit_epoch": 10,
      "commit_state": "ABORTED",
      "decision_witnessed": true,
      "participant_success_confers_global_commit_authority": false,
      "prepare_record_roots_hash72": [
        "xmpR<UIbE998HlATtt5eMNX*XMkip<Qll8WQe?5!gvvCQw>7)9cLVH6kz(RfJv<)5EN!UROU",
        "KJy9qnrstHPo>QGQ1SC<Z574Zcczk?7H)7U+3?QrMT(4tMAl!0EtZ*qW(Q*j<3LRvMt6g?*?"
      ],
      "reasons": [
        "REJECT_COMMIT_EPOCH_MISMATCH"
      ],
      "schema": "HHS_FEDERATED_TRANSACTION_COMMIT_DECISION_V1",
      "transaction_contract_root_hash72": "RpT9)S1y<xM/3?DS7aB8DPd6V7kzsquSREA>Rtv0Cx8s/WCr>r3aYoztEsn-SnHgsUr<P8da",
      "version": "PASS_059_CANONICAL_FEDERATED_TRANSACTION_COMMIT_COMPENSATING_ROLLBACK_V1"
    },
    "no_revalidation": {
      "authority": "HHS_I019_CANONICAL_FEDERATED_TRANSACTION_AUTHORITY_V1",
      "canonical_continuation": false,
      "commit_decision_root_hash72": "m?!SQhiUuwtKV(btbCL!Zlu0fVq4+e(5bu13TfGQWPam3)zyG4NKk1/B0MOVEoHuaLVCaGOx",
      "local_revalidation_performed": false,
      "participant_receipt_roots_hash72": [
        "UbN+5PzwTkW0-Xkz5j)<DAz!!Re8odNf+A!727Sl?UM8eeGUw1!N?yMokoWo(Kz/2Ag>usor",
        "J*Hd>+NJi9uNEyBaTpTdgu<P1AHSv?nEiPgMu+M?qEySsVWP27+k9G32J5WA)ntIF1Q>v+-D"
      ],
      "reasons": [
        "REJECT_TRANSACTION_RESULT_WITHOUT_LOCAL_REVALIDATION"
      ],
      "schema": "HHS_CANONICAL_FEDERATED_TRANSACTION_DECISION_V1",
      "status": "REJECT_CANONICAL_FEDERATED_TRANSACTION",
      "successful_participant_confers_global_authority": false,
      "transaction_decision_root_hash72": "j8HFdRdV<GfR7m!h0vu80gzwK02gjLho7XztToEiDKieZN!3<5X93iqKS9y+cU2OclHGwdnt",
      "version": "PASS_059_CANONICAL_FEDERATED_TRANSACTION_COMMIT_COMPENSATING_ROLLBACK_V1"
    },
    "partial_commit": {
      "authority": "HHS_I019_CANONICAL_FEDERATED_TRANSACTION_AUTHORITY_V1",
      "canonical_continuation": false,
      "commit_decision_root_hash72": "m?!SQhiUuwtKV(btbCL!Zlu0fVq4+e(5bu13TfGQWPam3)zyG4NKk1/B0MOVEoHuaLVCaGOx",
      "local_revalidation_performed": true,
      "participant_receipt_roots_hash72": [
        "UbN+5PzwTkW0-Xkz5j)<DAz!!Re8odNf+A!727Sl?UM8eeGUw1!N?yMokoWo(Kz/2Ag>usor",
        "skke6TTJ4isaY0k<ZA3NG5gPCDT<jwzuW8T!wIN-rIe9DOKCm8teTrf4N*PvaCupK9*vR+SR"
      ],
      "reasons": [
        "REJECT_PARTIAL_COMMIT_AS_CANONICAL_COMPLETION"
      ],
      "schema": "HHS_CANONICAL_FEDERATED_TRANSACTION_DECISION_V1",
      "status": "REJECT_CANONICAL_FEDERATED_TRANSACTION",
      "successful_participant_confers_global_authority": false,
      "transaction_decision_root_hash72": "NR+oL9d6z+UZILvT33Mh/7glE8K/S!ErtV)tuRib)MLr41ZMMxhC)1iF-PQ?qWl/j)ddp!xI",
      "version": "PASS_059_CANONICAL_FEDERATED_TRANSACTION_COMMIT_COMPENSATING_ROLLBACK_V1"
    },
    "partial_prepare": {
      "authority": "HHS_I019_CANONICAL_FEDERATED_TRANSACTION_AUTHORITY_V1",
      "canonical_completion": false,
      "commit_decision_root_hash72": "4YexKN5yORzCOH>)(gRGvxhcPwleiTE0sX5ow*JfAIPZ9?WYjVrKEPS05gz+Tb!5mI*q2WNw",
      "commit_epoch": 9,
      "commit_state": "ABORTED",
      "decision_witnessed": true,
      "participant_success_confers_global_commit_authority": false,
      "prepare_record_roots_hash72": [
        "xmpR<UIbE998HlATtt5eMNX*XMkip<Qll8WQe?5!gvvCQw>7)9cLVH6kz(RfJv<)5EN!UROU"
      ],
      "reasons": [
        "REJECT_COMMIT_WITHOUT_COMPLETE_PREPARE_SET"
      ],
      "schema": "HHS_FEDERATED_TRANSACTION_COMMIT_DECISION_V1",
      "transaction_contract_root_hash72": "RpT9)S1y<xM/3?DS7aB8DPd6V7kzsquSREA>Rtv0Cx8s/WCr>r3aYoztEsn-SnHgsUr<P8da",
      "version": "PASS_059_CANONICAL_FEDERATED_TRANSACTION_COMMIT_COMPENSATING_ROLLBACK_V1"
    }
  },
  "schema": "HHS_TRANSACTION_NEGATIVE_CASES_PASS_059_V1"
}
```
