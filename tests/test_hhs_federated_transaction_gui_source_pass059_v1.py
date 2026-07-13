from pathlib import Path

def test_pass059_gui_surfaces_exist():
    root=Path("hhs_gui/runtime_os/federation")
    names=["FederatedTransactionPanel","TransactionPrepareViewer","CommitDecisionInspector","ParticipantReceiptViewer","CompensationRecordPanel","CompensatingRollbackViewer","TransactionAuthorityMatrix","CanonicalTransactionContinuationPanel"]
    for name in names:
        text=(root/f"{name}.tsx").read_text()
        assert name in text and "pass059" in text
