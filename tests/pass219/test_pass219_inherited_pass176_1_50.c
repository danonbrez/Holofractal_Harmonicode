#include <assert.h>
#include <string.h>
#include "hhs_runtime_exact_abi.h"

static void fill_sha(char out[HHS_EXACT_PASS176_I150_SHA256_STRLEN], const char *value) {
    memcpy(out, value, HHS_EXACT_PASS176_I150_SHA256_LEN);
    out[HHS_EXACT_PASS176_I150_SHA256_LEN] = '\0';
}

static HHSExactPass176TerminalWitnessV1 witness(void) {
    HHSExactPass176TerminalWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass176_version();
    w.terminal_pass176_completion = 1U;
    w.all_verifier_checks_green = 1U;
    w.runtime_os_public_root_preserved = 1U;
    w.pass176_additive_route_preserved = 1U;
    w.browser_evidence_green = 1U;
    w.frontend_non_authority_verified = 1U;
    w.singleton_vm81_admission_preserved = 1U;
    w.hash72_commit_streams = 1U;
    w.pass177_successor_preserved = 1U;
    fill_sha(w.terminal_receipt_sha256, "f43d26f4932074d8de5e001a4de4dee2435ce216c4112c4612547f63ef771173");
    fill_sha(w.artifact_sha256, "b20edde645e16c13eb7629778e3bce3a5f4293684abb605c722a8254cdc86282");
    return w;
}

int main(void) {
    HHSExactPass176TerminalWitnessV1 w = witness();
    HHSExactPass219InheritedPass176BindingV1 b;
    assert(hhs_exact_pass219_bind_pass176_terminal_ide(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 176U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.terminal_completion_claimed == 1U);
    assert(b.browser_evidence_bound == 1U);
    assert(b.runtime_os_public_root_preserved == 1U);
    assert(b.additive_pass176_route_preserved == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.singleton_vm81_admission_preserved == 1U);
    assert(b.hash72_commit_streams == 1U);
    assert(b.independent_vm81_authority == 0U);
    assert(b.independent_hash72_commit_authority == 0U);
    assert(b.hash216_mutation_authority == 0U);

    w = witness(); w.terminal_pass176_completion = 0U;
    assert(hhs_exact_pass219_bind_pass176_terminal_ide(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness(); w.hash72_commit_streams = 2U;
    assert(hhs_exact_pass219_bind_pass176_terminal_ide(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness(); w.independent_vm81_authority = 1U;
    assert(hhs_exact_pass219_bind_pass176_terminal_ide(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
