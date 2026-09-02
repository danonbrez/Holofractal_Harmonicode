import pytest

from hhs_runtime.pass163.vmrc import VMRCRuntime
from hhs_runtime.pass177.runtime import Pass177AuthorityError, Pass177WorkflowAuthority


def _project():
    return {
        "schema": "hhs.pass177.generated-project/v1",
        "manifest": {
            "schema": "hhs.pass177.project/v1",
            "id": "field-notes",
            "name": "Field Notes",
            "slug": "field-notes",
            "family": "progressive-web-application",
            "target": "pwa",
            "template": {"id": "offline-pwa", "version": "1.0.0"},
            "workflow": {"id": "pwa.application.source-zip", "version": "1.0.0"},
            "files": [{"path": "index.html", "mediaType": "text/html", "bytes": 18}],
            "identity": {
                "algorithm": "HHS-P150-HASH216-CONSTRAINT-GENOME-V1",
                "root": "a" * 64,
                "payloadSha256": "b" * 64,
                "previousRoot": "0" * 64,
                "sequence": 0,
                "vm81EchoRequired": True,
                "browserProjectionOnly": True,
                "canonicalAdmissionRequired": True,
                "canonicalMutationAuthority": False,
            },
        },
        "identity": {
            "root": "a" * 64,
            "browserProjectionOnly": True,
            "canonicalAdmissionRequired": True,
            "canonicalMutationAuthority": False,
        },
        "files": [
            {
                "path": "index.html",
                "mediaType": "text/html",
                "content": "<!doctype html>\n",
                "dirty": False,
                "checkpoint": "Generated",
            }
        ],
    }


def _run(checkpoint=7):
    return {
        "schema": "hhs.pass177.workflow-run/v1",
        "runId": "workflow-demo",
        "workflowId": "pwa.application.source-zip",
        "workflowVersion": "1.0.0",
        "status": "succeeded",
        "context": {"projectId": "field-notes"},
        "stageStates": {
            "validate": {"status": "succeeded", "attempts": 1, "output": {"ok": True}},
            "package-source-zip": {
                "status": "succeeded",
                "attempts": 1,
                "output": {"format": "zip", "independentOfCompilation": True},
            },
        },
        "checkpoint": checkpoint,
        "checkpointAuthority": "MEMORY_CANDIDATE_ONLY",
        "canonicalAdmissionRequired": True,
        "canonicalMutationAuthority": False,
    }


def test_project_admission_requires_inherited_vm81():
    authority = Pass177WorkflowAuthority(vm81=None)
    with pytest.raises(Pass177AuthorityError, match="VM81_ADMISSION_AUTHORITY_REQUIRED"):
        authority.admit_project(_project())


def test_browser_identity_becomes_evidence_only_after_vm81_admission():
    vm81 = VMRCRuntime()
    authority = Pass177WorkflowAuthority(vm81=vm81)
    before = vm81.epoch
    admitted = authority.admit_project(_project())
    assert vm81.epoch == before + 1
    assert admitted["browser_identity_authoritative"] is False
    assert admitted["vm81_admission"]["classification"] == "HHS_PASS177_VM81_WORKFLOW_ADMISSION_VERIFIED"
    assert admitted["vm81_admission"]["singleton_authority"] is True
    assert admitted["vm81_admission"]["independent_vm81_authority"] is False
    assert admitted["vm81_admission"]["validation_mutation_authority"] is False
    assert len(admitted["post_vm81_hash72_evidence"]) == 72
    assert len(admitted["project_hash216"]) == 216
    assert admitted["hash72_commit_authority"] is False
    assert admitted["hash216_mutation_authority"] is False


def test_workflow_checkpoint_requires_admitted_project_and_vm81():
    vm81 = VMRCRuntime()
    authority = Pass177WorkflowAuthority(vm81=vm81)
    authority.admit_project(_project())
    before = vm81.epoch
    record = authority.admit_workflow_checkpoint(project_id="field-notes", run=_run())
    assert vm81.epoch == before + 1
    assert record["memory_checkpoint_authoritative"] is False
    assert record["canonical_mutation_authority"] == "INHERITED_VM81_ONLY"
    assert len(record["post_vm81_hash72_evidence"]) == 72
    assert len(record["checkpoint_hash216"]) == 216


def test_stale_checkpoint_and_float_canonical_ingress_fail_closed():
    authority = Pass177WorkflowAuthority(vm81=VMRCRuntime())
    authority.admit_project(_project())
    authority.admit_workflow_checkpoint(project_id="field-notes", run=_run(8))
    with pytest.raises(Pass177AuthorityError, match="STALE_WORKFLOW_CHECKPOINT"):
        authority.admit_workflow_checkpoint(project_id="field-notes", run=_run(7))

    bad = _project()
    bad["manifest"]["displayScale"] = 1.25
    with pytest.raises(Pass177AuthorityError, match="FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"):
        Pass177WorkflowAuthority(vm81=VMRCRuntime()).admit_project(bad)


def test_status_keeps_pass177_nonterminal_and_no_peer_authority():
    status = Pass177WorkflowAuthority(vm81=VMRCRuntime()).status()
    assert status["terminal_pass177_completion"] is False
    assert status["repair_forward_required"] is True
    assert status["independent_vm81_authority"] is False
    assert status["independent_hash72_commit_authority"] is False
    assert status["hash216_mutation_authority"] is False
    assert status["browser_hash216_is_candidate_identity_only"] is True
    assert len(status["remaining_terminal_categories"]) >= 10
