from pathlib import Path
def test_gui_surfaces_exist():
    root=Path("hhs_gui/runtime_os/authority")
    names=["CanonicalAuthorityGraphPanel","RoleContractInspector","CompetencyAuthorityMatrix","TaskAssignmentViewer","CrossRoleHandoffViewer","DerivationEquivalenceInspector","IndependentRevalidationPanel","ResponsePriorityAuthorityPanel","AttentionAuthoritySeparationViewer","CanonicalContinuationInspector"]
    for name in names: assert (root/f"{name}.tsx").exists()
