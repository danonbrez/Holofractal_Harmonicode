from pathlib import Path
def test_pass060_gui_surfaces_exist():
 text="\n".join(p.read_text() for p in Path("hhs_gui/runtime_os/federation").glob("*.tsx"))
 for name in ["FederatedTransactionRecoveryPanel","IdempotencyRegistryViewer","ReplayDecisionInspector","RecoveryCheckpointViewer","ExactlyOnceAdmissionPanel","DuplicateEffectSuppressionViewer","RecoveryEpochInspector","CanonicalRecoveryContinuationPanel"]: assert name in text and "pass060" in text
