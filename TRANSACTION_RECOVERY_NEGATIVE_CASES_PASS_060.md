# Transaction Recovery Negative Cases Pass 060

Authoritative source: corresponding JSON artifact.

```json
{
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
}
```
