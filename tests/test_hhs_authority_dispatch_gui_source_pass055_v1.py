from pathlib import Path
def test_pass055_gui_surfaces_present():
 root=Path("hhs_gui/runtime_os/authority"); names=["CapabilityLeasePanel","AuthorityDispatchViewer","LeaseLifecycleInspector","ExecutionCheckpointViewer","LeaseRevocationPanel","ExecutionReceiptInspector","CapabilityLeaseMatrix","AuthorityActivationInspector"]; assert all((root/(n+".tsx")).exists() for n in names)
