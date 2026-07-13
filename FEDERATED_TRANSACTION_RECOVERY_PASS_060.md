# Federated Transaction Recovery Pass 060

Authoritative source: corresponding JSON artifact.

```json
{
  "run": {
    "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
    "canonical_admission": {
      "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
      "canonical_admission_count": 1,
      "canonical_admission_root_hash72": "K/<Drziw+)ARm0kdK1?A5fG!m2G<)hknwzYYeQfKAlHXQIaI43N7O3KZsGGnRzTlpLUJIq5M",
      "canonical_continuation": true,
      "checkpoint_chain_root_hash72": "?Qq23dq8w84yAwR75W9(7R)w?JMy<!+3HQc)sdHCeyO9KfWl>66XQC4bmlO-foA7WhNUDDO9",
      "exactly_once_admitted": true,
      "local_revalidation_performed": true,
      "prior_canonical_admission_count": 0,
      "reasons": [],
      "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
      "recovery_epoch": 10,
      "replay_confers_authority": false,
      "replay_decision_roots_hash72": [
        "jl><EdS6WWSl8LzVhz)jnbpn-euCq9FYydm8KvtJxAQsQHuA/gOZDveFxOMAgQFkiOB<x<XQ",
        "ixW2O211!d/erj>-c6?X)CxmF1i+e<UYsOgvOpVEE)nO*mce!Jd4Ht6jUvq/+T4*RwQ<fRGy"
      ],
      "schema": "HHS_EXACTLY_ONCE_CANONICAL_ADMISSION_RECORD_V1",
      "status": "ADMIT_EXACTLY_ONCE_CANONICAL_RECOVERY",
      "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
    },
    "checkpoint_chain": {
      "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
      "chain_complete": true,
      "checkpoint_chain_root_hash72": "?Qq23dq8w84yAwR75W9(7R)w?JMy<!+3HQc)sdHCeyO9KfWl>66XQC4bmlO-foA7WhNUDDO9",
      "checkpoint_sequences": [
        201,
        202
      ],
      "participant_receipt_roots_hash72": [
        "UbN+5PzwTkW0-Xkz5j)<DAz!!Re8odNf+A!727Sl?UM8eeGUw1!N?yMokoWo(Kz/2Ag>usor",
        "J*Hd>+NJi9uNEyBaTpTdgu<P1AHSv?nEiPgMu+M?qEySsVWP27+k9G32J5WA)ntIF1Q>v+-D"
      ],
      "reasons": [],
      "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
      "schema": "HHS_TRANSACTION_RECOVERY_CHECKPOINT_CHAIN_V1",
      "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
    },
    "idempotency_records": [
      {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "canonical_admission_count": 0,
        "effect_application_count": 1,
        "effect_root_hash72": "w2eUq4-le*dt2ke1ykglkq9nkwssssMbUB<qQ2mxRMAOuXD0MKkPQRSTUVWXYZ-+*/()<>!z",
        "idempotency_key": "idem:runtime:local:pass060",
        "idempotency_record_root_hash72": "e68lCP*CNk6?44pUEis>J>Wq3+iDdSXa(n5AiN6UmYt>NaL-ug!lyOdhDv/!))dNp2FFFQA8",
        "participant_id": "runtime:local",
        "reasons": [],
        "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
        "schema": "HHS_TRANSACTION_IDEMPOTENCY_RECORD_V1",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      },
      {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "canonical_admission_count": 0,
        "effect_application_count": 1,
        "effect_root_hash72": "w2eUq4-le*dt2ke1ykglkq9nkwssssMbUB<qQ2mMsOJNuEPYTHVB(K7TRkWXYZ-+*/()<>!z",
        "idempotency_key": "idem:runtime:remote-a:pass060",
        "idempotency_record_root_hash72": "W-rAdQWCV*plUnVv-44CBWsRYwNRgeIc-AXi9-a6FdNMG/IuPnK<Xv1n9YYWTZW6kpHcnruP",
        "participant_id": "runtime:remote-a",
        "reasons": [],
        "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
        "schema": "HHS_TRANSACTION_IDEMPOTENCY_RECORD_V1",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      }
    ],
    "ok": true,
    "pass059_transaction_root_hash72": "1x(4ZbTIspUa254g>4TmED?l10>dDkmqKh?ZUC/9kzOB3KKT5C!GEf7s<4>V-t-EZYZSxpkT",
    "recovery_contract": {
      "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
      "participants": [
        "runtime:local",
        "runtime:remote-a"
      ],
      "reasons": [],
      "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
      "recovery_epoch": 10,
      "replay_confers_authority": false,
      "replay_policy": "IDEMPOTENT_EFFECT_EXACTLY_ONCE_ADMISSION",
      "schema": "HHS_FEDERATED_TRANSACTION_RECOVERY_CONTRACT_V1",
      "transaction_decision_root_hash72": "5pU3f<WVolDyLjoVcQF3T+b?H-EuqM!yFR02ck5YZv1SI<m0MTd?ZWW01-QjieKFdX2TxQiU",
      "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
    },
    "rejection_codes": [
      "REJECT_RECOVERY_WITHOUT_TRANSACTION_RECEIPT",
      "REJECT_REPLAY_WITHOUT_IDEMPOTENCY_KEY",
      "REJECT_IDEMPOTENCY_KEY_REBOUND_TO_DIFFERENT_EFFECT",
      "REJECT_DUPLICATE_EFFECT_APPLICATION",
      "REJECT_REPLAY_AS_NEW_AUTHORITY",
      "REJECT_RECOVERY_WITHOUT_CHECKPOINT_CHAIN",
      "REJECT_EXACTLY_ONCE_ADMISSION_WITHOUT_CANONICAL_ADMISSION_RECORD",
      "REJECT_DUPLICATE_CANONICAL_ADMISSION",
      "REJECT_RECOVERY_EPOCH_MISMATCH",
      "REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION",
      "REJECT_PARTIAL_RECOVERY_AS_CANONICAL_COMPLETION"
    ],
    "replay_decisions": [
      {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "candidate_effect_root_hash72": "w2eUq4-le*dt2ke1ykglkq9nkwssssMbUB<qQ2mxRMAOuXD0MKkPQRSTUVWXYZ-+*/()<>!z",
        "duplicate_effect_suppressed": true,
        "effect_applied": false,
        "idempotency_record_root_hash72": "e68lCP*CNk6?44pUEis>J>Wq3+iDdSXa(n5AiN6UmYt>NaL-ug!lyOdhDv/!))dNp2FFFQA8",
        "prior_effect_application_count": 1,
        "reasons": [],
        "replay_confers_new_authority": false,
        "replay_decision_root_hash72": "jl><EdS6WWSl8LzVhz)jnbpn-euCq9FYydm8KvtJxAQsQHuA/gOZDveFxOMAgQFkiOB<x<XQ",
        "same_effect": true,
        "schema": "HHS_IDEMPOTENT_REPLAY_DECISION_V1",
        "status": "ADMIT_IDEMPOTENT_REPLAY",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      },
      {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "candidate_effect_root_hash72": "w2eUq4-le*dt2ke1ykglkq9nkwssssMbUB<qQ2mMsOJNuEPYTHVB(K7TRkWXYZ-+*/()<>!z",
        "duplicate_effect_suppressed": true,
        "effect_applied": false,
        "idempotency_record_root_hash72": "W-rAdQWCV*plUnVv-44CBWsRYwNRgeIc-AXi9-a6FdNMG/IuPnK<Xv1n9YYWTZW6kpHcnruP",
        "prior_effect_application_count": 1,
        "reasons": [],
        "replay_confers_new_authority": false,
        "replay_decision_root_hash72": "ixW2O211!d/erj>-c6?X)CxmF1i+e<UYsOgvOpVEE)nO*mce!Jd4Ht6jUvq/+T4*RwQ<fRGy",
        "same_effect": true,
        "schema": "HHS_IDEMPOTENT_REPLAY_DECISION_V1",
        "status": "ADMIT_IDEMPOTENT_REPLAY",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      }
    ],
    "run_root_hash72": "rUp>by2g2gswKA9)-zHqj>ZRIQmC)/QKp+)f(JX7Z5tg/fyui6y(CRhzpkFOuI(pHvMgVQWv",
    "schema": "HHS_FEDERATED_TRANSACTION_RECOVERY_RUN_V1",
    "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
  },
  "self_test": {
    "negative_cases": {
      "duplicate_admission": {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "canonical_admission_count": 1,
        "canonical_admission_root_hash72": "78++c?EVehDNi3v7YxMQf7RlF*lNF/zbT0DZxXAeRhI?aGlNuV/R3nMCOA4x*z3FY4Q+uccV",
        "canonical_continuation": false,
        "checkpoint_chain_root_hash72": "?Qq23dq8w84yAwR75W9(7R)w?JMy<!+3HQc)sdHCeyO9KfWl>66XQC4bmlO-foA7WhNUDDO9",
        "exactly_once_admitted": false,
        "local_revalidation_performed": true,
        "prior_canonical_admission_count": 1,
        "reasons": [
          "REJECT_DUPLICATE_CANONICAL_ADMISSION"
        ],
        "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
        "recovery_epoch": 10,
        "replay_confers_authority": false,
        "replay_decision_roots_hash72": [
          "jl><EdS6WWSl8LzVhz)jnbpn-euCq9FYydm8KvtJxAQsQHuA/gOZDveFxOMAgQFkiOB<x<XQ",
          "ixW2O211!d/erj>-c6?X)CxmF1i+e<UYsOgvOpVEE)nO*mce!Jd4Ht6jUvq/+T4*RwQ<fRGy"
        ],
        "schema": "HHS_EXACTLY_ONCE_CANONICAL_ADMISSION_RECORD_V1",
        "status": "REJECT_CANONICAL_RECOVERY",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      },
      "epoch": {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "canonical_admission_count": 0,
        "canonical_admission_root_hash72": ">C98lOy-OFO8ll*Su5Ub?UQoW)4?xanl7bxHJ4ekEABLzS6K*Y2oxi6+qtL5bkYm!-v7+?V?",
        "canonical_continuation": false,
        "checkpoint_chain_root_hash72": "?Qq23dq8w84yAwR75W9(7R)w?JMy<!+3HQc)sdHCeyO9KfWl>66XQC4bmlO-foA7WhNUDDO9",
        "exactly_once_admitted": false,
        "local_revalidation_performed": true,
        "prior_canonical_admission_count": 0,
        "reasons": [
          "REJECT_RECOVERY_EPOCH_MISMATCH"
        ],
        "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
        "recovery_epoch": 11,
        "replay_confers_authority": false,
        "replay_decision_roots_hash72": [
          "jl><EdS6WWSl8LzVhz)jnbpn-euCq9FYydm8KvtJxAQsQHuA/gOZDveFxOMAgQFkiOB<x<XQ",
          "ixW2O211!d/erj>-c6?X)CxmF1i+e<UYsOgvOpVEE)nO*mce!Jd4Ht6jUvq/+T4*RwQ<fRGy"
        ],
        "schema": "HHS_EXACTLY_ONCE_CANONICAL_ADMISSION_RECORD_V1",
        "status": "REJECT_CANONICAL_RECOVERY",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      },
      "missing_chain": {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "canonical_admission_count": 0,
        "canonical_admission_root_hash72": "Tb43(WNmcyfDI?7/*PW2ci/aWPeqAM2zELHuWTc3?Vpn9S)PmFg8WMaTG03rYPOjfy+iQz4D",
        "canonical_continuation": false,
        "checkpoint_chain_root_hash72": "fp<Sb(DavmPrT/K)e9wf+MG5(G+?TfBr*FHal43RSmClhqUS5F7dqmxolo+*BtNSa(o)<q/H",
        "exactly_once_admitted": false,
        "local_revalidation_performed": true,
        "prior_canonical_admission_count": 0,
        "reasons": [
          "REJECT_RECOVERY_WITHOUT_CHECKPOINT_CHAIN"
        ],
        "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
        "recovery_epoch": 10,
        "replay_confers_authority": false,
        "replay_decision_roots_hash72": [
          "jl><EdS6WWSl8LzVhz)jnbpn-euCq9FYydm8KvtJxAQsQHuA/gOZDveFxOMAgQFkiOB<x<XQ",
          "ixW2O211!d/erj>-c6?X)CxmF1i+e<UYsOgvOpVEE)nO*mce!Jd4Ht6jUvq/+T4*RwQ<fRGy"
        ],
        "schema": "HHS_EXACTLY_ONCE_CANONICAL_ADMISSION_RECORD_V1",
        "status": "REJECT_CANONICAL_RECOVERY",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      },
      "no_revalidation": {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "canonical_admission_count": 0,
        "canonical_admission_root_hash72": "(-qFRi<WM?gGReJ)I?FzuAlbq8+V-L+Y*SC7hE/zMgqWCWs5dGk<p2as8LJK*dtomPdp4IsJ",
        "canonical_continuation": false,
        "checkpoint_chain_root_hash72": "?Qq23dq8w84yAwR75W9(7R)w?JMy<!+3HQc)sdHCeyO9KfWl>66XQC4bmlO-foA7WhNUDDO9",
        "exactly_once_admitted": false,
        "local_revalidation_performed": false,
        "prior_canonical_admission_count": 0,
        "reasons": [
          "REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION"
        ],
        "recovery_contract_root_hash72": ">bkviO)Uzy2Denx4KRahCmXZ2<H<s0!OBkjiYT1v?+xTq?Oq-*T1F0FNK3K5epDQN/O2L2Gf",
        "recovery_epoch": 10,
        "replay_confers_authority": false,
        "replay_decision_roots_hash72": [
          "jl><EdS6WWSl8LzVhz)jnbpn-euCq9FYydm8KvtJxAQsQHuA/gOZDveFxOMAgQFkiOB<x<XQ",
          "ixW2O211!d/erj>-c6?X)CxmF1i+e<UYsOgvOpVEE)nO*mce!Jd4Ht6jUvq/+T4*RwQ<fRGy"
        ],
        "schema": "HHS_EXACTLY_ONCE_CANONICAL_ADMISSION_RECORD_V1",
        "status": "REJECT_CANONICAL_RECOVERY",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      },
      "rebound": {
        "authority": "HHS_I019_FEDERATED_TRANSACTION_RECOVERY_AUTHORITY_V1",
        "candidate_effect_root_hash72": "s7044j(hfZhddddxT8yU4A9MhtkrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!z",
        "duplicate_effect_suppressed": false,
        "effect_applied": false,
        "idempotency_record_root_hash72": "e68lCP*CNk6?44pUEis>J>Wq3+iDdSXa(n5AiN6UmYt>NaL-ug!lyOdhDv/!))dNp2FFFQA8",
        "prior_effect_application_count": 1,
        "reasons": [
          "REJECT_IDEMPOTENCY_KEY_REBOUND_TO_DIFFERENT_EFFECT"
        ],
        "replay_confers_new_authority": false,
        "replay_decision_root_hash72": "WpvUxP(c0kEuM0SJ6G29xnof/5ks9(Zw(<TgwqQxpFGyV9hl+myBfLywzlx3c5Lb9vh+<JwV",
        "same_effect": false,
        "schema": "HHS_IDEMPOTENT_REPLAY_DECISION_V1",
        "status": "REJECT_REPLAY",
        "version": "PASS_060_FEDERATED_TRANSACTION_RECOVERY_IDEMPOTENT_REPLAY_EXACTLY_ONCE_ADMISSION_V1"
      }
    },
    "ok": true,
    "run_root_hash72": "rUp>by2g2gswKA9)-zHqj>ZRIQmC)/QKp+)f(JX7Z5tg/fyui6y(CRhzpkFOuI(pHvMgVQWv",
    "schema": "HHS_FEDERATED_TRANSACTION_RECOVERY_SELF_TEST_V1"
  }
}
```
