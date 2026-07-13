from pathlib import Path

def test_pass058_gui_surfaces_present():
    root=Path("hhs_gui/runtime_os/authority")
    names=["FederatedStateSnapshotViewer","FederatedConflictSetInspector","ConflictPreservingMergePanel","CommonAncestorViewer","FederatedMergeCandidateViewer","FederatedMergeDecisionPanel","MergeProvenanceInspector","CanonicalStateReconciliationPanel"]
    for name in names:
        text=(root/f"{name}.tsx").read_text()
        assert 'data-hhs-pass="058"' in text
