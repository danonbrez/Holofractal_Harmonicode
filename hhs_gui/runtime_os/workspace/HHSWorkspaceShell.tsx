import React, { useMemo, useState } from "react"
import { RuntimeAssistantPanel } from "../assistant/RuntimeAssistantPanel"
import { LiveBackendCapabilityPanel } from "../capability/LiveBackendCapabilityPanel"
import { CompilerWorkbench } from "../compiler/CompilerWorkbench"
import { InterpreterConsole } from "../console/InterpreterConsole"
import { HHSSymbolicEditor } from "../editor/HHSSymbolicEditor"
import { EmulatorControlPanel } from "../emulator/EmulatorControlPanel"
import { RuntimeGraphCanvas } from "../graph/RuntimeGraphCanvas"
import { MutationHistoryPanel } from "../history/MutationHistoryPanel"
import { WorkspaceObjectInspector } from "../inspector/WorkspaceObjectInspector"
import { ReceiptLedgerInspector } from "../ledger/ReceiptLedgerInspector"
import { SemanticMemoryPanel } from "../memory/SemanticMemoryPanel"
import { WorkspaceAuthorityStatus } from "../status/WorkspaceAuthorityStatus"
import { MultimodalIngressPanel } from "./MultimodalIngressPanel"
import { RuntimeProjectTree } from "./RuntimeProjectTree"
import { WorkspaceCommandClient } from "./WorkspaceCommandClient"
import { WorkspaceProjectionStore } from "./WorkspaceProjectionStore"

export const HHSWorkspaceShell: React.FC = () => {
  const commandClient = useMemo(() => new WorkspaceCommandClient(), [])
  const projectionStore = useMemo(() => new WorkspaceProjectionStore(), [])
  const [projection, setProjection] = useState(projectionStore.snapshot())

  const applyFeedback = (feedback: unknown) => {
    setProjection(projectionStore.applyAuthorityFeedback(feedback))
  }

  const projectId = projection.projectId ?? "project:default"

  return (
    <section
      data-testid="hhs-visual-runtime-os-workspace"
      className="min-w-0 rounded-2xl border border-cyan-900/60 bg-neutral-950/95 p-3 text-xs text-cyan-50 shadow-2xl"
    >
      <header className="mb-3 flex flex-wrap items-center justify-between gap-3 border-b border-cyan-900/50 pb-2">
        <div>
          <h1 className="text-sm font-semibold tracking-wide">HHS Visual Runtime OS Workspace</h1>
          <p className="text-[11px] text-cyan-300">Project, language, multimodal, provider, runtime, receipt, and assistant operations share one backend authority.</p>
        </div>
        <WorkspaceAuthorityStatus status={projection.authorityStatus} receiptHash72={projection.lastReceiptHash72} />
      </header>

      <div className="grid min-w-0 grid-cols-1 gap-3 xl:grid-cols-[220px_minmax(0,1fr)_300px]">
        <div className="min-w-0">
          <RuntimeProjectTree projection={projection} commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
        </div>

        <main className="grid min-w-0 content-start gap-3">
          <RuntimeAssistantPanel />
          <MultimodalIngressPanel commandClient={commandClient} onAuthorityFeedback={applyFeedback} projectId={projectId} />
          <LiveBackendCapabilityPanel />
          <HHSSymbolicEditor commandClient={commandClient} onAuthorityFeedback={applyFeedback} projectId={projectId} />
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
            <InterpreterConsole commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
            <CompilerWorkbench commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
            <EmulatorControlPanel commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
          </div>
          <RuntimeGraphCanvas />
        </main>

        <aside className="grid min-w-0 content-start gap-3">
          <WorkspaceObjectInspector projection={projection} />
          <SemanticMemoryPanel commandClient={commandClient} onAuthorityFeedback={applyFeedback} />
          <ReceiptLedgerInspector projection={projection} />
          <MutationHistoryPanel history={projection.commandHistory} />
        </aside>
      </div>
    </section>
  )
}
