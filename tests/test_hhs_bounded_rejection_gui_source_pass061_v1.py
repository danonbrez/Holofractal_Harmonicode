from pathlib import Path

def test_pass061_gui_surfaces_exist():
 root=Path(__file__).resolve().parents[1]/"hhs_gui/runtime_os/authority"
 names=["BoundedRejectionAuthorityPanel","RejectionRoleContractInspector","LocalRejectionDecisionViewer","MinimalCorrectivePropagationPanel","RejectionProvenanceInspector","RejectionExpiryViewer","RejectionRemediationPanel","RejectionNonAmplificationMatrix"]
 for n in names:
  p=root/f"{n}.tsx"; assert p.exists(); assert "data-hhs-pass=\"061\"" in p.read_text()
