#include "hhs_pass219_inherited_pass189_1_37.h"

#include <assert.h>
#include <string.h>

static HHSExactPass189CumulativeAuthorityWitnessV1 witness(void) {
    HHSExactPass189CumulativeAuthorityWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass189_version();
    w.template_registry_contract_preserved = 1U;
    w.hqlh_contract_preserved = 1U;
    w.runtime_implementation_preserved = 1U;
    w.iteration2_calibration_preserved = 1U;
    w.iteration3_adapter_preserved = 1U;
    w.iteration4_provenance_preserved = 1U;
    w.token_lifecycle_preserved = 1U;
    w.contextual_address_count = 51648192U;
    w.lo_shu_xnor_ternary_bound = 1U;
    w.hash72_receipt_chain = 1U;
    w.hash216_topology_identity = 1U;
    w.deterministic_replay = 1U;
    w.calibration_in_progress = 1U;
    w.measured_evidence_required_for_physical_candidate = 1U;
    w.real_hardware_execution_authorized = 0U;
    w.software_test_adapters_only = 1U;
    w.bounded_operator_leases = 1U;
    w.anti_replay_commands = 1U;
    w.payload_bound_quarantine = 1U;
    w.dual_approval_promotion = 1U;
    w.promotion_token_lifecycle = 1U;
    w.deterministic_rollback = 1U;
    w.sqlite_persistence = 1U;
    w.checkpoint_recovery = 1U;
    w.dns_port_separation_bound = 1U;
    w.pass190_successor_preserved = 1U;

    strcpy(w.template_contract_commit, "9dfd373d5ccd66b9172313b750c8439435d90f49");
    strcpy(w.hqlh_contract_merge, "54ffe9d89d1aa928a6be75a3663ad51f709b7b9d");
    strcpy(w.runtime_implementation_commit, "a1a55a4f621ff3678f5af81119439e9558cf9db4");
    strcpy(w.iteration2_commit, "c3cc477cd1b573eb5a318c7f38a1197e428d7014");
    strcpy(w.iteration3_commit, "f3ceba745ce5b478ca850c14a543a18189cc7d6c");
    strcpy(w.iteration4_commit, "7a99674997974262b171a0aee05665cbeab42ab9");
    strcpy(w.token_lifecycle_commit, "0ee579aa574fa8f8b4c827518ae4249bbad4e8be");
    strcpy(w.dns_integration_commit, "8ac51f5de0be323513577863fcbde71578ef4e14");
    strcpy(w.frozen_i136_commit, "3a76667eb463f8027e2bfaea4a2f76cff470c564");

    strcpy(w.template_contract_blob, "daae3c4cb368d42fd9f83c22abd9a81380ba0f2a");
    strcpy(w.hqlh_contract_blob, "0bc9f1a3ee9d2252002310e5c5cab88ad98553a5");
    strcpy(w.runtime_doc_blob, "3d9a4f7869b23d2655c1027fac353c841a8b7a2e");
    strcpy(w.iteration2_doc_blob, "492c28b6368d7f36649e377cb052097a6fa60703");
    strcpy(w.iteration3_doc_blob, "492e5434c4319b28a9f8838606cfd8dc00b0ae65");
    strcpy(w.iteration4_doc_blob, "5c7e8391a28c14ae0bbdae15592d3889c85f53c0");
    strcpy(w.makefile_blob, "35f9ed59c26994247a2fa209afe0280329cef106");
    strcpy(w.native_header_blob, "b558c7f090913a70bf3691f6fb413fd5a7bdebff");
    strcpy(w.native_source_blob, "651a2a2f4be6d802c88182c016657be1698f83b2");
    strcpy(w.python_runtime_blob, "5d98e213ce80f793b0d3761efbe88dff33bb7f14");
    strcpy(w.iteration2_python_blob, "88f50add4b71c9c57877f96f61854aade405c0b3");
    strcpy(w.iteration3_python_blob, "eea7c2f825583d4013395c472d62cf9dd81e5923");
    strcpy(w.iteration4_python_blob, "aeec45db0b773364fdc155be62499cbb5ec4e221");
    strcpy(w.token_lifecycle_blob, "b427718ba16e143797c0856587ec83556314df19");
    strcpy(w.template_registry_blob, "8583c4e2e3621072d414448968cbdbfe81e311ad");
    strcpy(w.focused_workflow_blob, "f184f462b5eb1a93fd3c41d2b622ee4ac0bcc35c");
    strcpy(w.base_receipt_blob, "23d61fa5cc157fcb44967e33956bbc97d50dba36");
    strcpy(w.iteration2_receipt_blob, "2e99a7a11e1adca6168ba10ad51cb6bf9d96b487");
    strcpy(w.iteration3_receipt_blob, "c0ef0202fda59f93581da4cad3f6ec163b7feb0a");
    strcpy(w.iteration4_receipt_blob, "c383e5232d1d16ba2b9f66cbe9a7bda09e432d9d");
    strcpy(w.dns_registry_blob, "16a264268f91301ba499c8beb253b18677873390");
    return w;
}

int main(void) {
    HHSExactPass189CumulativeAuthorityWitnessV1 w = witness();
    HHSExactPass219InheritedPass189BindingV1 b;

    assert(hhs_exact_pass219_bind_pass189_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 189U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.template_registry_bound == 1U);
    assert(b.hqlh_runtime_bound == 1U);
    assert(b.calibration_boundary_bound == 1U);
    assert(b.adapter_authority_bound == 1U);
    assert(b.provenance_authority_bound == 1U);
    assert(b.token_lifecycle_bound == 1U);
    assert(b.exact_topology_bound == 1U);
    assert(b.inherited_vm81_receipt_bound == 1U);
    assert(b.hardware_nonexecution_bound == 1U);
    assert(b.deployment_boundary_bound == 1U);
    assert(b.pass190_successor_bound == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.calibration_in_progress == 1U);
    assert(b.float_is_canonical_authority == 0U);

    w = witness();
    w.calibration_in_progress = 0U;
    assert(hhs_exact_pass219_bind_pass189_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.real_hardware_execution_authorized = 1U;
    assert(hhs_exact_pass219_bind_pass189_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    w.vercel_authority = 1U;
    assert(hhs_exact_pass219_bind_pass189_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    w = witness();
    strcpy(w.iteration4_receipt_blob, "0000000000000000000000000000000000000000");
    assert(hhs_exact_pass219_bind_pass189_cumulative_authority(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
