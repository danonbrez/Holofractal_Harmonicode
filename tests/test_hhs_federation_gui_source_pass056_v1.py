from pathlib import Path

def test_pass056_gui_surfaces_present():
    root=Path('hhs_gui/runtime_os/federation')
    expected=['FederationDomainPanel','RemoteAuthorityIdentityViewer','DelegationChainInspector','DelegatedSubleaseMatrix','RemoteDispatchViewer','RemoteCheckpointChainViewer','FederatedResultIngressPanel','RevocationPropagationInspector']
    for name in expected:
        text=(root/f'{name}.tsx').read_text(); assert 'data-hhs-pass="056"' in text
