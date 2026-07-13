from pathlib import Path

def test_pass057_gui_surfaces_exist():
    root=Path('hhs_gui/runtime_os/authority')
    names=['PartitionEvidencePanel','RevocationConsensusViewer','StaleLeaseQuarantineInspector','ReconciliationReceiptViewer','FederatedRecoveryPanel','PartitionAuthorityMatrix','RevocationEpochInspector','StaleRemoteResultViewer']
    for name in names:
        text=(root/f'{name}.tsx').read_text()
        assert 'data-hhs-pass="057"' in text
        assert name in text
