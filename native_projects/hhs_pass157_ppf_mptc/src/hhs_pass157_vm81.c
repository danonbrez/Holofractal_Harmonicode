#include "hhs_pass157_internal.h"
#include "hhs_runtime_abi.h"

#include <inttypes.h>
#include <stdio.h>
#include <string.h>

static HHS157Status kernel_profile(const HHSRuntimeState *runtime,char out[HHS157_HASH216_STRLEN]){
    char payload[512];
    if(!runtime||!out)return HHS157_INVALID_ARGUMENT;
    int n=snprintf(payload,sizeof(payload),"HHS-P157-KERNEL-PROFILE-V1|magic=%"PRIu64"|abi=%"PRIu32".%"PRIu32".%"PRIu32"|size=%zu|loshu=%u|genomic=%u,%u,%u,%u",runtime->runtime_magic,runtime->abi_major,runtime->abi_minor,runtime->abi_patch,hhs_sizeof_runtime_state(),runtime->lo_shu_slot,runtime->genomic.genomic[0],runtime->genomic.genomic[1],runtime->genomic.genomic[2],runtime->genomic.genomic[3]);
    if (n < 0 || (size_t)n >= sizeof(payload)) {
        return HHS157_SERIALIZATION_BOUNDED;
    }
    hhs157_hash216_bytes(payload, (size_t)n, out);
    return HHS157_OK;
}
static HHS157Status transition_hash(const HHS157Request*q,const HHS157Result*r,char out[HHS157_HASH216_STRLEN]){
    char payload[8192];HHS157Status s=hhs157_canonical_transition(q,r,payload,sizeof(payload));if(s)return s;hhs157_hash216_bytes(payload,strlen(payload),out);return HHS157_OK;
}
static HHS157Status seal_receipt(HHS157AuthorityReceipt *receipt){
    char payload[2048];
    int n=snprintf(payload,sizeof(payload),"HHS-P157-ADMISSION-SEAL-V1|kernel=%s|transition=%s|before=%"PRIu64"|after=%"PRIu64"|wb=%"PRIu64"|wa=%"PRIu64"|parent=%s|state=%s|receipt=%s",receipt->kernel_profile_hash216,receipt->transition_hash216,receipt->step_before,receipt->step_after,receipt->witness_before,receipt->witness_after,receipt->parent_hash72,receipt->state_hash72,receipt->receipt_hash72);
    if (n < 0 || (size_t)n >= sizeof(payload)) {
        return HHS157_SERIALIZATION_BOUNDED;
    }
    hhs157_hash216_bytes(payload, (size_t)n, receipt->admission_seal_hash216);
    return HHS157_OK;
}
HHS157Status hhs157_admit(const HHS157Request*q,HHS157Result*r,void*runtime_state,HHS157AuthorityReceipt*receipt){
    HHSRuntimeState*runtime=(HHSRuntimeState*)runtime_state;HHSTensorState tensor;HHSReceipt vmreceipt;HHS157Status s;
    if(!q||!r||!runtime||!receipt)return HHS157_INVALID_ARGUMENT;
    if(!hhs_validate_abi(runtime)||runtime->halted||runtime->abi_minor!=HHS_ABI_VERSION_MINOR||runtime->abi_patch!=HHS_ABI_VERSION_PATCH)return HHS157_KERNEL_DRIFT;
    if(!r->pythagorean_verified||!r->reciprocal_membrane_verified||!r->delta_verified||!r->centerline_verified||!r->phase_reconstruction_verified||!r->pass155_fold_verified||!r->pass156_membrane_verified||!r->pass156_1_dependency_hardened)return HHS157_VM81_REJECTED;
    memset(receipt,0,sizeof(*receipt));receipt->abi_version=HHS157_ABI_VERSION;receipt->runtime_magic=runtime->runtime_magic;receipt->runtime_abi_major=runtime->abi_major;receipt->runtime_abi_minor=runtime->abi_minor;receipt->runtime_abi_patch=runtime->abi_patch;receipt->runtime_state_size=hhs_sizeof_runtime_state();receipt->step_before=runtime->step;receipt->witness_before=runtime->witness_flags;
    s=kernel_profile(runtime,receipt->kernel_profile_hash216);if(s)return s;s=transition_hash(q,r,receipt->transition_hash216);if(s)return s;
    hhs_tensor_reset(&tensor);tensor.xy=r->xy;tensor.yx=r->yx;tensor.transport=r->A+r->B;tensor.orientation=r->xy-r->yx;tensor.constraint=r->Delta<0?-r->Delta:r->Delta;
    hhs_runtime_step(runtime,&tensor);if(runtime->step!=receipt->step_before+1U)return HHS157_VM81_REJECTED;
    hhs_receipt_reset(&vmreceipt);vmreceipt.opcode=157U;hhs_receipt_commit(runtime,&vmreceipt);
    receipt->step_after=runtime->step;receipt->witness_after=runtime->witness_flags;memcpy(receipt->parent_hash72,vmreceipt.parent_receipt,73);memcpy(receipt->state_hash72,runtime->state_hash72,73);memcpy(receipt->receipt_hash72,vmreceipt.current_receipt,73);
    return seal_receipt(receipt);
}
HHS157Status hhs157_verify_receipt(const HHS157Request*q,const HHS157Result*r,const HHS157AuthorityReceipt*receipt){
    HHS157AuthorityReceipt expected;HHSRuntimeState initial;HHS157Status s;
    if(!q||!r||!receipt||receipt->abi_version!=HHS157_ABI_VERSION)return HHS157_INVALID_ARGUMENT;
    hhs_runtime_init(&initial);s=hhs157_admit(q,(HHS157Result*)r,&initial,&expected);if(s)return s;
    if(strcmp(expected.kernel_profile_hash216,receipt->kernel_profile_hash216)||strcmp(expected.transition_hash216,receipt->transition_hash216)||strcmp(expected.parent_hash72,receipt->parent_hash72)||strcmp(expected.state_hash72,receipt->state_hash72)||strcmp(expected.receipt_hash72,receipt->receipt_hash72)||strcmp(expected.admission_seal_hash216,receipt->admission_seal_hash216)||expected.step_before!=receipt->step_before||expected.step_after!=receipt->step_after||expected.runtime_magic!=receipt->runtime_magic||expected.runtime_state_size!=receipt->runtime_state_size)return HHS157_RECEIPT_MISMATCH;
    return HHS157_OK;
}
HHS157Status hhs157_replay_verify(const HHS157Request*q,const HHS157Result*expected,const HHS157AuthorityReceipt*expected_receipt){
    HHS157Result replay;HHS157AuthorityReceipt receipt;HHSRuntimeState runtime;HHS157Status s;
    if(!q||!expected||!expected_receipt)return HHS157_INVALID_ARGUMENT;
    s=hhs157_construct(q,&replay);if(s)return s;if (strcmp(replay.result_hash216, expected->result_hash216) ||
        strcmp(replay.tensor_hash216, expected->tensor_hash216) ||
        memcmp(replay.tensor, expected->tensor, sizeof(replay.tensor)) != 0 ||
        memcmp(replay.vm81_cells, expected->vm81_cells, sizeof(replay.vm81_cells)) != 0 ||
        memcmp(replay.centerline, expected->centerline, sizeof(replay.centerline)) != 0) {
        return HHS157_REPLAY_MISMATCH;
    }
    hhs_runtime_init(&runtime);s=hhs157_admit(q,&replay,&runtime,&receipt);if(s)return s;if(strcmp(receipt.receipt_hash72,expected_receipt->receipt_hash72)||strcmp(receipt.admission_seal_hash216,expected_receipt->admission_seal_hash216))return HHS157_REPLAY_MISMATCH;return HHS157_OK;
}
