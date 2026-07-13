from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_capability_gui_surfaces_are_mounted():
    shell = read("hhs_gui/runtime_os/workspace/HHSWorkspaceShell.tsx")
    for token in [
        "RuntimeCanonicalObserverPanel",
        "CapabilityRegistryPanel",
        "ProviderInspector",
        "CapabilityResolutionViewer",
        "ExecutionProposalPanel",
        "ProviderInvocationTimeline",
        "FallbackPlanViewer",
        "ProviderResultLineageViewer",
        "CapabilityAuthorityStatus",
    ]:
        assert token in shell


def test_capability_gui_declares_noncanonical_boundaries():
    source = "\n".join(
        read(path)
        for path in [
            "hhs_gui/runtime_os/capability/RuntimeCanonicalObserverPanel.tsx",
            "hhs_gui/runtime_os/capability/CapabilityRegistryPanel.tsx",
            "hhs_gui/runtime_os/capability/ProviderInspector.tsx",
            "hhs_gui/runtime_os/capability/ExecutionProposalPanel.tsx",
            "hhs_gui/runtime_os/capability/ProviderResultLineageViewer.tsx",
        ]
    )
    for token in [
        "NO_INTERFACE_IS_CANONICAL",
        "NO_PROVIDER_IS_CANONICAL",
        "provider ≠ capability",
        "provider output ≠ canonical truth",
        "successful invocation ≠ admitted mutation",
        "REJECT_RAW_PROVIDER_OUTPUT_AS_CANONICAL_SOURCE",
    ]:
        assert token in source
