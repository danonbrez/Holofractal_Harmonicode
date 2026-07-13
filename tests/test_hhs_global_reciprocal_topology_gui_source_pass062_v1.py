from pathlib import Path
def test_pass062_gui_surfaces_exist():
 root=Path(__file__).resolve().parents[1]/"hhs_gui/runtime_os/authority"
 names=["GlobalReciprocalTopologyPanel","LocalReciprocalContractInspector","XYZWPhaseGearViewer","TopologyExpansionPanel","TopologyContractionViewer","ReciprocalEntanglementMatrix","PositiveNegativeContractBalancePanel","GlobalReciprocityValidationInspector"]
 for n in names:
  p=root/f"{n}.tsx"; assert p.exists(); assert 'data-hhs-pass="062"' in p.read_text()
