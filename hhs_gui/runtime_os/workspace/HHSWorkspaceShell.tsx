import React, { useMemo, useState } from "react"
import { WorkspaceCommandClient } from "./WorkspaceCommandClient"
import { WorkspaceProjectionStore } from "./WorkspaceProjectionStore"
import { RuntimeProjectTree } from "./RuntimeProjectTree"
import { MultimodalIngressPanel } from "./MultimodalIngressPanel"
import { WorkspaceObjectInspector } from "../inspector/WorkspaceObjectInspector"
import { HHSSymbolicEditor } from "../editor/HHSSymbolicEditor"
import { InterpreterConsole } from "../console/InterpreterConsole"
import { CompilerWorkbench } from "../compiler/CompilerWorkbench"
import { EmulatorControlPanel } from "../emulator/EmulatorControlPanel"
import { RuntimeGraphCanvas } from "../graph/RuntimeGraphCanvas"
import { SemanticMemoryPanel } from "../memory/SemanticMemoryPanel"
import { ReceiptLedgerInspector } from "../ledger/ReceiptLedgerInspector"
import { MutationHistoryPanel } from "../history/MutationHistoryPanel"
import { UniversalModalityPanel } from "../modality/UniversalModalityPanel"
import { ModalityAdapterInspector } from "../modality/ModalityAdapterInspector"
import { ProjectionLineageViewer } from "../modality/ProjectionLineageViewer"
import { CrossModalTransformPanel } from "../modality/CrossModalTransformPanel"
import { ArtifactPipelinePanel } from "../artifacts/ArtifactPipelinePanel"
import { ArtifactLineageViewer } from "../artifacts/ArtifactLineageViewer"
import { WorkspaceAuthorityStatus } from "../status/WorkspaceAuthorityStatus"
import { RuntimeCanonicalObserverPanel } from "../capability/RuntimeCanonicalObserverPanel"
import { CapabilityRegistryPanel } from "../capability/CapabilityRegistryPanel"
import { ProviderInspector } from "../capability/ProviderInspector"
import { CapabilityResolutionViewer } from "../capability/CapabilityResolutionViewer"
import { ExecutionProposalPanel } from "../capability/ExecutionProposalPanel"
import { ProviderInvocationTimeline } from "../capability/ProviderInvocationTimeline"
import { FallbackPlanViewer } from "../capability/FallbackPlanViewer"
import { ProviderResultLineageViewer } from "../capability/ProviderResultLineageViewer"
import { CapabilityAuthorityStatus } from "../capability/CapabilityAuthorityStatus"
import { DocumentPerceptionPanel } from "../document/DocumentPerceptionPanel"
import { DocumentSourceInspector } from "../document/DocumentSourceInspector"
import { PageLayoutViewer } from "../document/PageLayoutViewer"
import { OCRProjectionViewer } from "../document/OCRProjectionViewer"
import { DocumentFusionViewer } from "../document/DocumentFusionViewer"
import { TableProjectionViewer } from "../document/TableProjectionViewer"
import { DocumentGraphViewer } from "../document/DocumentGraphViewer"
import { DocumentAmbiguityInspector } from "../document/DocumentAmbiguityInspector"
import { DocumentReconstructionViewer } from "../document/DocumentReconstructionViewer"

export const HHSWorkspaceShell: React.FC = () => {
  const commandClient = useMemo(() => new WorkspaceCommandClient(), [])
  const projectionStore = useMemo(() => new WorkspaceProjectionStore(), [])
  const [projection, setProjection] = useState(projectionStore.snapshot())

  const applyFeedback = (feedback: any) => {
    setProjection(projectionStore.applyAuthorityFeedback(feedback))
  }

  return (
    <section data-testid="hhs-visual-runtime-os-workspace" className="rounded-2xl border border-cyan-900/60 bg-neutral-950/95 p-3 text-xs text-cyan-50 shadow-2xl">
      <header className="mb-3 flex items-center justify-between gap-3 border-b border-cyan-900/50 pb-2">
        <div>
          <h2 className="text-sm font-semibold tracking-wide">HHS Visual Runtime OS Workspace</h2>
          <p className="text-[11px] text-cyan-300">Workspace is request/projection only. FastAPI/kernel remains authority.</p>
        </div>
        <WorkspaceAuthorityStatus status={projection.authorityStatus} receiptHash72={projection.lastReceiptHash72} />
      </header>
      <div className="grid grid-cols-[220px_1fr_260px] gap-3">
        <RuntimeProjectTree projection={projection} commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
        <main className="grid gap-3">
          <MultimodalIngressPanel commandClient={commandClient} onAuthorityFeedback={applyFeedback} projectId={projection.projectId ?? "project:default"} />
          <div className="grid grid-cols-3 gap-3">
            <UniversalModalityPanel />
            <ModalityAdapterInspector />
            <CrossModalTransformPanel />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <ProjectionLineageViewer />
            <ArtifactPipelinePanel />
            <ArtifactLineageViewer />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <RuntimeCanonicalObserverPanel />
            <CapabilityRegistryPanel />
            <ProviderInspector />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <CapabilityResolutionViewer />
            <ExecutionProposalPanel />
            <ProviderInvocationTimeline />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <FallbackPlanViewer />
            <ProviderResultLineageViewer />
            <CapabilityAuthorityStatus />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <DocumentPerceptionPanel />
            <DocumentSourceInspector />
            <PageLayoutViewer />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <OCRProjectionViewer />
            <DocumentFusionViewer />
            <TableProjectionViewer />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <DocumentGraphViewer />
            <DocumentAmbiguityInspector />
            <DocumentReconstructionViewer />
          </div>
          <HHSSymbolicEditor commandClient={commandClient} onAuthorityFeedback={applyFeedback} projectId={projection.projectId ?? "project:default"} />
          <div className="grid grid-cols-3 gap-3">
            <InterpreterConsole commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
            <CompilerWorkbench commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
            <EmulatorControlPanel commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
          </div>
          <RuntimeGraphCanvas />
        </main>
        <aside className="grid gap-3">
          <WorkspaceObjectInspector projection={projection} />
          <SemanticMemoryPanel commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
          <ReceiptLedgerInspector projection={projection} />
          <MutationHistoryPanel history={projection.commandHistory} />
        </aside>
      </div>
    </section>
  )
}
