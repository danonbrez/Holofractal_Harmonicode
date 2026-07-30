import React, { useEffect, useMemo, useState } from "react"
import { RuntimeAssistantPanel } from "../assistant/RuntimeAssistantPanel"
import { LiveRuntimeProjectionPanel } from "../core/LiveRuntimeProjectionPanel"
import type { RuntimeOS } from "../core/RuntimeOS"
import { WorkspaceCommandClient } from "./WorkspaceCommandClient"

type Json = Record<string, any>
type WorkspaceTab = "workbench" | "assistant" | "runtime" | "receipts"
type BusyAction = "boot" | "project" | "source" | "interpret" | "compile" | "emulator" | "runtime" | null

type Activity = {
  id: string
  operation: string
  ok: boolean
  status: string
  summary: string
  receiptHash72: string | null
  createdAt: number
  raw?: Json
}

export interface HHSWorkspaceShellProps {
  runtimeOS: RuntimeOS
  transportState: string
  transportError?: string | null
}

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback
const shortHash = (value: unknown): string => {
  const valueText = text(value)
  return valueText ? `${valueText.slice(0, 10)}…${valueText.slice(-6)}` : "—"
}

async function requestJson(url: string, init?: RequestInit, timeoutMs = 20000): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
      headers: {
        accept: "application/json",
        ...(init?.body ? { "content-type": "application/json" } : {}),
        ...(init?.headers ?? {}),
      },
    })
    const body = record(await response.json())
    if (!response.ok) throw new Error(text(body.detail ?? body.error ?? body.status, response.statusText))
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

function objectsFromProject(project: Json | null): Json[] {
  if (!project) return []
  const registry = record(project.object_registry)
  const order = Array.isArray(project.object_order) ? project.object_order.map(String) : Object.keys(registry)
  return order.map((id) => record(registry[id])).filter((item) => Boolean(item.object_id))
}

function extractProject(feedback: Json): Json | null {
  const result = record(feedback.result)
  const registration = record(result.registration)
  for (const candidate of [feedback.project, result.project, registration.project]) {
    const project = record(candidate)
    if (project.project_id) return project
  }
  return null
}

function extractReceipt(feedback: Json): string | null {
  const result = record(feedback.result)
  const artifact = record(result.artifact)
  const registration = record(result.registration)
  const receipt = record(result.receipt)
  const executionReceipt = record(result.execution_receipt)
  const candidate = feedback.receipt_hash72
    ?? result.receipt_hash72
    ?? result.result_root_hash72
    ?? artifact.receipt_hash72
    ?? registration.receipt_hash72
    ?? receipt.receipt_hash72
    ?? executionReceipt.receipt_hash72
  return typeof candidate === "string" ? candidate : null
}

function summarize(operation: string, feedback: Json): string {
  const result = record(feedback.result)
  if (operation === "project.create") {
    return `Opened ${text(record(result.project).name, "workspace")} with canonical project identity.`
  }
  if (operation === "ingress.register") {
    const object = record(result.workspace_object)
    return `Witnessed ${text(object.name, "source")} as ${text(object.modality, "source")} and registered it in the active project.`
  }
  if (operation === "interpret.execute") {
    return result.ok
      ? `Exact result: ${text(result.display_value, "completed")}.`
      : `Interpretation rejected: ${(result.reasons ?? []).join(", ") || text(result.status, "unknown rejection")}.`
  }
  if (operation === "compile.execute") {
    const artifact = record(result.artifact)
    const operations = Array.isArray(record(artifact.ir).operations) ? record(artifact.ir).operations.length : 0
    return result.ok
      ? `Created ${text(artifact.target, "HHS_IR")} artifact ${text(artifact.artifact_id)} with ${operations} witnessed IR operation(s).`
      : `Compilation rejected: ${text(result.status, "unknown rejection")}.`
  }
  if (operation.startsWith("emulator.")) {
    const session = record(result.session)
    return result.ok
      ? `${text(result.status, operation)} · tick ${String(session.tick ?? 0)} · ${text(session.mode, "PAUSED")}.`
      : `Emulator request rejected: ${text(result.status, "unknown rejection")}.`
  }
  return text(feedback.status ?? result.status, operation)
}

export const HHSWorkspaceShell: React.FC<HHSWorkspaceShellProps> = ({
  runtimeOS,
  transportState,
  transportError,
}) => {
  const commandClient = useMemo(() => new WorkspaceCommandClient(), [])
  const [tab, setTab] = useState<WorkspaceTab>("workbench")
  const [busyAction, setBusyAction] = useState<BusyAction>("boot")
  const [error, setError] = useState<string | null>(null)
  const [project, setProject] = useState<Json | null>(null)
  const [objects, setObjects] = useState<Json[]>([])
  const [selectedObjectId, setSelectedObjectId] = useState<string | null>(null)
  const [projectName, setProjectName] = useState("HHS Workspace")
  const [sourceName, setSourceName] = useState("main.hhs")
  const [sourceText, setSourceText] = useState("")
  const [witnessedSourceText, setWitnessedSourceText] = useState("")
  const [expression, setExpression] = useState("1+2*3/4")
  const [target, setTarget] = useState("HHS_IR")
  const [artifact, setArtifact] = useState<Json | null>(null)
  const [emulatorSession, setEmulatorSession] = useState<Json | null>(null)
  const [lastResult, setLastResult] = useState<Json | null>(null)
  const [activity, setActivity] = useState<Activity[]>([])

  const selectedObject = objects.find((item) => item.object_id === selectedObjectId) ?? null
  const projectId = text(project?.project_id)
  const artifactId = text(artifact?.artifact_id)
  const sessionId = text(emulatorSession?.session_id)
  const sourceDirty = sourceText !== witnessedSourceText

  const mergeSession = (session: Json): void => {
    const nextProject = record(session.project)
    if (nextProject.project_id) {
      const nextObjects = Array.isArray(session.objects)
        ? session.objects.map(record).filter((item: Json) => Boolean(item.object_id))
        : objectsFromProject(nextProject)
      const lastObject = nextObjects.length > 0 ? nextObjects[nextObjects.length - 1] : null
      setProject(nextProject)
      setObjects(nextObjects)
      setSelectedObjectId((current) => current ?? (text(lastObject?.object_id) || null))
    }

    const history = Array.isArray(session.history) ? session.history.map(record) : []
    if (history.length > 0) {
      setActivity(history.map((item: Json, index: number) => ({
        id: text(item.command_id, `remote-${index}`),
        operation: text(item.operation, "workspace.command"),
        ok: Boolean(item.ok),
        status: text(item.status, "UNKNOWN"),
        summary: text(item.status, "Workspace command"),
        receiptHash72: typeof item.receipt_hash72 === "string" ? item.receipt_hash72 : null,
        createdAt: Date.now() - (history.length - index) * 1000,
      })))
    }
  }

  const refreshSession = async (requestedProjectId?: string): Promise<void> => {
    const query = requestedProjectId ? `?project_id=${encodeURIComponent(requestedProjectId)}` : ""
    mergeSession(await requestJson(`/api/runtime/workspace/session${query}`))
  }

  useEffect(() => {
    let active = true
    requestJson("/api/runtime/workspace/session")
      .then((session) => { if (active) mergeSession(session) })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : String(reason)) })
      .finally(() => { if (active) setBusyAction(null) })
    return () => { active = false }
  }, [])

  const applyFeedback = (operation: string, feedback: Json): void => {
    const result = record(feedback.result)
    const nextProject = extractProject(feedback)
    if (nextProject) {
      setProject(nextProject)
      setObjects(objectsFromProject(nextProject))
    }

    const workspaceObject = record(result.workspace_object)
    if (workspaceObject.object_id) {
      setSelectedObjectId(text(workspaceObject.object_id))
      setWitnessedSourceText(sourceText)
    }

    const compiledArtifact = record(result.artifact)
    if (compiledArtifact.artifact_id) setArtifact(compiledArtifact)
    const nextSession = record(result.session)
    if (nextSession.session_id) setEmulatorSession(nextSession)

    const receiptHash72 = extractReceipt(feedback)
    const summary = summarize(operation, feedback)
    setLastResult({ operation, feedback, receipt_hash72: receiptHash72, summary })
    setActivity((current) => [{
      id: `${operation}:${Date.now()}`,
      operation,
      ok: Boolean(feedback.ok),
      status: text(feedback.status ?? result.status, feedback.ok ? "COMPLETED" : "REJECTED"),
      summary,
      receiptHash72,
      createdAt: Date.now(),
      raw: feedback,
    }, ...current].slice(0, 48))
  }

  const submit = async (operation: string, payload: Json): Promise<Json> => {
    const feedback = record(await commandClient.submit(operation, payload))
    applyFeedback(operation, feedback)
    if (feedback.ok === false) throw new Error(summarize(operation, feedback))
    return feedback
  }

  const ensureProject = async (): Promise<Json> => {
    if (project?.project_id) return project
    const feedback = await submit("project.create", { name: projectName })
    const created = extractProject(feedback)
    if (!created) throw new Error("Project authority returned no project identity")
    return created
  }

  const ensureSource = async (activeProject: Json): Promise<Json> => {
    if (selectedObject?.object_id && !sourceDirty) return selectedObject
    if (!sourceText.trim()) throw new Error("Enter source content before witnessing or compiling it")
    const feedback = await submit("ingress.register", {
      project_id: activeProject.project_id,
      source_name: sourceName,
      source_payload: sourceText,
      declared_modality: sourceName.endsWith(".hhs") ? "HARMONICODE_SOURCE" : "TEXT",
    })
    const workspaceObject = record(record(feedback.result).workspace_object)
    if (!workspaceObject.object_id) throw new Error("Ingress completed without a workspace object")
    await refreshSession(text(activeProject.project_id))
    return workspaceObject
  }

  const run = async (action: BusyAction, task: () => Promise<void>): Promise<void> => {
    if (busyAction) return
    setBusyAction(action)
    setError(null)
    try {
      await task()
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusyAction(null)
    }
  }

  const createProject = () => run("project", async () => {
    await submit("project.create", { name: projectName })
  })

  const witnessSource = () => run("source", async () => {
    await ensureSource(await ensureProject())
  })

  const interpret = () => run("interpret", async () => {
    const activeProject = await ensureProject()
    await submit("interpret.execute", {
      project_id: activeProject.project_id,
      source_object_id: selectedObjectId ?? "object:expression",
      expression,
    })
  })

  const compile = () => run("compile", async () => {
    const activeProject = await ensureProject()
    const object = await ensureSource(activeProject)
    await submit("compile.execute", {
      project_id: activeProject.project_id,
      source_object_id: object.object_id,
      source_text: sourceText,
      target,
    })
  })

  const ensureArtifact = async (): Promise<Json> => {
    if (artifact?.artifact_id && !sourceDirty) return artifact
    const activeProject = await ensureProject()
    const object = await ensureSource(activeProject)
    const feedback = await submit("compile.execute", {
      project_id: activeProject.project_id,
      source_object_id: object.object_id,
      source_text: sourceText,
      target,
    })
    const nextArtifact = record(record(feedback.result).artifact)
    if (!nextArtifact.artifact_id) throw new Error("Compiler returned no artifact identity")
    return nextArtifact
  }

  const createEmulator = () => run("emulator", async () => {
    const activeProject = await ensureProject()
    const nextArtifact = await ensureArtifact()
    await submit("emulator.create", {
      project_id: activeProject.project_id,
      program_artifact_id: nextArtifact.artifact_id,
    })
  })

  const emulatorCommand = (operation: "emulator.step" | "emulator.run" | "emulator.snapshot") => run("emulator", async () => {
    if (!sessionId) throw new Error("Create an emulator session first")
    await submit(operation, {
      project_id: projectId,
      session_id: sessionId,
      ...(operation === "emulator.run" ? { steps: 4 } : {}),
    })
  })

  const runtimeTick = () => run("runtime", async () => {
    const result = await requestJson("/api/runtime/live/tick", { method: "POST" })
    const receiptHash72 = typeof result.receipt_hash72 === "string" ? result.receipt_hash72 : null
    const summary = "Advanced the canonical live runtime workflow by one bounded tick."
    setLastResult({ operation: "runtime.live.tick", feedback: { result }, receipt_hash72: receiptHash72, summary })
    setActivity((current) => [{
      id: `runtime.live.tick:${Date.now()}`,
      operation: "runtime.live.tick",
      ok: Boolean(result.ok ?? true),
      status: text(result.status, "RUNTIME_TICK_COMPLETED"),
      summary,
      receiptHash72,
      createdAt: Date.now(),
      raw: result,
    }, ...current].slice(0, 48))
  })

  const recordAssistantReceipt = (receiptHash72: string, raw: Json): void => {
    setActivity((current) => [{
      id: `assistant:${Date.now()}`,
      operation: "assistant.chat",
      ok: true,
      status: "ASSISTANT_TURN_COMPLETED",
      summary: "Completed a governed assistant turn in the active project context.",
      receiptHash72,
      createdAt: Date.now(),
      raw,
    }, ...current].slice(0, 48))
  }

  const activeReceipt = activity.find((item) => item.receiptHash72)?.receiptHash72 ?? null

  return (
    <section data-testid="hhs-visual-runtime-os-workspace" className="min-h-screen bg-neutral-950 text-neutral-100">
      <header className="sticky top-0 z-40 border-b border-neutral-800 bg-black/95 px-3 py-3 backdrop-blur-xl md:px-5">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold tracking-wide text-cyan-200">HHS Visual Runtime OS</div>
            <div className="truncate text-[10px] text-neutral-500">
              {project ? `${text(project.name, "Workspace")} · ${shortHash(project.project_id)}` : "Create a project to begin"}
            </div>
          </div>
          <div className="flex items-center gap-2 text-[10px]">
            <span className={transportState === "CONNECTED" ? "text-emerald-300" : "text-amber-300"}>{transportState}</span>
            {busyAction ? <span className="rounded-full bg-cyan-950 px-2 py-1 text-cyan-200">{busyAction}</span> : null}
          </div>
        </div>
      </header>

      <nav className="sticky top-[57px] z-30 border-b border-neutral-800 bg-neutral-950/95 px-2 py-2 backdrop-blur-xl">
        <div className="mx-auto grid max-w-3xl grid-cols-4 gap-1">
          {([
            ["workbench", "Build"],
            ["assistant", "Assistant"],
            ["runtime", "Runtime"],
            ["receipts", "Receipts"],
          ] as [WorkspaceTab, string][]).map(([id, label]) => (
            <button key={id} type="button" onClick={() => setTab(id)} className={`min-h-10 rounded-lg px-2 text-xs ${tab === id ? "bg-cyan-900 text-white" : "bg-neutral-900 text-neutral-400"}`}>
              {label}
            </button>
          ))}
        </div>
      </nav>

      <main className="mx-auto max-w-[1600px] p-2 pb-10 md:p-4">
        {error ? (
          <div className="mb-3 flex items-start justify-between gap-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-sm text-red-200">
            <span>{error}</span>
            <button type="button" onClick={() => setError(null)} className="text-xs text-red-300">dismiss</button>
          </div>
        ) : null}

        {tab === "workbench" ? (
          <div className="grid min-w-0 gap-3 lg:grid-cols-[240px_minmax(0,1fr)_340px]">
            <aside className="min-w-0 rounded-2xl border border-neutral-800 bg-neutral-900/60 p-3">
              <div className="flex items-center justify-between gap-2">
                <h2 className="text-xs font-semibold text-cyan-200">Project objects</h2>
                <button type="button" onClick={() => void refreshSession(projectId || undefined)} className="runtime-button px-2 py-1 text-[10px]">refresh</button>
              </div>

              {!project ? (
                <div className="mt-4 space-y-2">
                  <input value={projectName} onChange={(event) => setProjectName(event.target.value)} className="w-full rounded-lg border border-neutral-700 bg-black p-2 text-sm" aria-label="Project name" />
                  <button type="button" onClick={createProject} disabled={Boolean(busyAction)} className="runtime-button min-h-10 w-full px-3 text-sm">Create project</button>
                </div>
              ) : objects.length === 0 ? (
                <p className="mt-4 text-xs leading-5 text-neutral-500">No registered objects. Witness the current source to create the first canonical workspace object.</p>
              ) : (
                <div className="mt-3 space-y-2">
                  {objects.map((object) => (
                    <button key={text(object.object_id)} type="button" onClick={() => setSelectedObjectId(text(object.object_id))} className={`w-full rounded-xl border p-3 text-left ${selectedObjectId === object.object_id ? "border-cyan-700 bg-cyan-950/40" : "border-neutral-800 bg-black/40"}`}>
                      <div className="truncate text-xs font-medium text-neutral-100">{text(object.name, "workspace object")}</div>
                      <div className="mt-1 truncate text-[9px] text-neutral-500">{text(object.object_type)} · {text(object.lifecycle_state)}</div>
                      <div className="mt-1 truncate font-mono text-[9px] text-cyan-800">{shortHash(object.root_hash72 ?? object.current_root_hash72)}</div>
                    </button>
                  ))}
                </div>
              )}
            </aside>

            <section className="min-w-0 rounded-2xl border border-neutral-800 bg-neutral-900/40">
              <div className="border-b border-neutral-800 p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <h2 className="text-sm font-semibold text-white">Source → artifact → emulator</h2>
                    <p className="text-[10px] text-neutral-500">Every action advances the same selected project and receipt chain.</p>
                  </div>
                  <span className={sourceDirty ? "text-[10px] text-amber-300" : "text-[10px] text-emerald-300"}>{sourceDirty ? "local changes not witnessed" : "source witnessed"}</span>
                </div>
              </div>

              <div className="space-y-3 p-3">
                <div className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_160px]">
                  <input value={sourceName} onChange={(event) => setSourceName(event.target.value)} className="rounded-lg border border-neutral-700 bg-black p-2 text-sm" aria-label="Source file name" />
                  <select value={target} onChange={(event) => setTarget(event.target.value)} className="rounded-lg border border-neutral-700 bg-black p-2 text-sm" aria-label="Compiler target">
                    {["HHS_IR", "C_KERNEL_PLAN", "C_SOURCE", "PYTHON_ADAPTER", "JSON_EXECUTION_GRAPH", "DOT_GRAPH", "BYTECODE_OR_VM_PLAN", "RECEIPT_ONLY_PLAN"].map((item) => <option key={item}>{item}</option>)}
                  </select>
                </div>

                <textarea value={sourceText} onChange={(event) => setSourceText(event.target.value)} className="min-h-[38vh] w-full resize-y rounded-xl border border-neutral-700 bg-black p-3 font-mono text-sm leading-6 text-cyan-50 outline-none focus:border-cyan-600" placeholder="Enter HARMONICODE or source content…" spellCheck={false} aria-label="HHS source editor" />

                <div className="grid gap-2 sm:grid-cols-3">
                  <button type="button" onClick={witnessSource} disabled={Boolean(busyAction) || !sourceText.trim()} className="runtime-button min-h-11 px-3 text-sm">Witness source</button>
                  <button type="button" onClick={compile} disabled={Boolean(busyAction) || !sourceText.trim()} className="runtime-button min-h-11 px-3 text-sm">Compile artifact</button>
                  <button type="button" onClick={createEmulator} disabled={Boolean(busyAction) || !sourceText.trim()} className="runtime-button min-h-11 px-3 text-sm">Create emulator</button>
                </div>

                <div className="rounded-xl border border-neutral-800 bg-black/50 p-3">
                  <label className="text-[10px] uppercase tracking-wide text-neutral-500" htmlFor="exact-expression">Exact arithmetic interpreter</label>
                  <div className="mt-2 flex flex-col gap-2 sm:flex-row">
                    <input id="exact-expression" value={expression} onChange={(event) => setExpression(event.target.value)} className="min-h-10 min-w-0 flex-1 rounded-lg border border-neutral-700 bg-black px-3 font-mono text-sm" />
                    <button type="button" onClick={interpret} disabled={Boolean(busyAction) || !expression.trim()} className="runtime-button min-h-10 px-4 text-sm">Interpret</button>
                  </div>
                </div>
              </div>
            </section>

            <aside className="min-w-0 space-y-3">
              <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-3">
                <h2 className="text-xs font-semibold text-cyan-200">Current execution state</h2>
                <div className="mt-3 grid grid-cols-2 gap-2 text-[10px]">
                  <StateField label="project" value={project ? "ready" : "not created"} ready={Boolean(project)} />
                  <StateField label="source" value={selectedObject ? "witnessed" : "local"} ready={Boolean(selectedObject)} />
                  <StateField label="artifact" value={artifactId || "none"} ready={Boolean(artifactId)} />
                  <StateField label="emulator" value={sessionId || "none"} ready={Boolean(sessionId)} />
                </div>

                {emulatorSession ? (
                  <div className="mt-3 rounded-xl border border-neutral-800 bg-black/50 p-3">
                    <div className="flex items-center justify-between text-xs"><span>{text(emulatorSession.mode, "PAUSED")}</span><span>tick {String(emulatorSession.tick ?? 0)}</span></div>
                    <div className="mt-2 grid grid-cols-3 gap-1">
                      <button type="button" onClick={() => emulatorCommand("emulator.step")} disabled={Boolean(busyAction)} className="runtime-button min-h-9 text-xs">Step</button>
                      <button type="button" onClick={() => emulatorCommand("emulator.run")} disabled={Boolean(busyAction)} className="runtime-button min-h-9 text-xs">Run 4</button>
                      <button type="button" onClick={() => emulatorCommand("emulator.snapshot")} disabled={Boolean(busyAction)} className="runtime-button min-h-9 text-xs">Snapshot</button>
                    </div>
                  </div>
                ) : null}
              </section>

              <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-3">
                <div className="flex items-center justify-between gap-2">
                  <h2 className="text-xs font-semibold text-cyan-200">Last result</h2>
                  <span className="font-mono text-[9px] text-neutral-600">{shortHash(record(lastResult).receipt_hash72)}</span>
                </div>
                {lastResult ? (
                  <>
                    <p className="mt-3 text-sm leading-6 text-neutral-200">{text(lastResult.summary, "Operation completed.")}</p>
                    <details className="mt-3 rounded-lg border border-neutral-800 bg-black/50 p-2">
                      <summary className="cursor-pointer text-[10px] text-neutral-500">Technical evidence</summary>
                      <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap break-all text-[9px] text-neutral-400">{JSON.stringify(lastResult, null, 2)}</pre>
                    </details>
                  </>
                ) : <p className="mt-3 text-xs leading-5 text-neutral-500">Execute an operation to see its human-readable result and receipt evidence.</p>}
              </section>
            </aside>
          </div>
        ) : null}

        {tab === "assistant" ? (
          <RuntimeAssistantPanel projectId={projectId || null} sourceObjectId={selectedObjectId} sourceName={sourceName} artifactId={artifactId || null} onReceipt={recordAssistantReceipt} />
        ) : null}

        {tab === "runtime" ? (
          <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_300px]">
            <LiveRuntimeProjectionPanel runtimeOS={runtimeOS} />
            <aside className="space-y-3">
              <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-4">
                <h2 className="text-sm font-semibold text-cyan-200">Runtime control</h2>
                <p className="mt-2 text-xs leading-5 text-neutral-500">The projection is loaded only while this tab is active. One manual tick advances the canonical live workflow through the backend.</p>
                <button type="button" onClick={runtimeTick} disabled={Boolean(busyAction)} className="runtime-button mt-3 min-h-10 w-full px-3 text-sm">Advance one runtime tick</button>
              </section>
              <section className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-4 text-xs">
                <div className="flex justify-between gap-2"><span className="text-neutral-500">transport</span><span>{transportState}</span></div>
                <div className="mt-2 flex justify-between gap-2"><span className="text-neutral-500">project</span><span>{projectId ? shortHash(projectId) : "none"}</span></div>
                <div className="mt-2 flex justify-between gap-2"><span className="text-neutral-500">receipt</span><span>{shortHash(activeReceipt)}</span></div>
                {transportError ? <p className="mt-3 break-words text-red-300">{transportError}</p> : null}
              </section>
            </aside>
          </div>
        ) : null}

        {tab === "receipts" ? (
          <section className="rounded-2xl border border-neutral-800 bg-neutral-900/50">
            <header className="flex items-center justify-between gap-3 border-b border-neutral-800 p-4">
              <div>
                <h2 className="text-sm font-semibold text-cyan-200">Workspace receipts and activity</h2>
                <p className="text-[10px] text-neutral-500">Only operations that actually returned from the backend appear here.</p>
              </div>
              <button type="button" onClick={() => void refreshSession(projectId || undefined)} className="runtime-button min-h-9 px-3 text-xs">Refresh</button>
            </header>
            <div className="divide-y divide-neutral-800">
              {activity.length === 0 ? (
                <p className="p-6 text-sm text-neutral-500">No backend operations have completed in this workspace.</p>
              ) : activity.map((item) => (
                <article key={item.id} className="grid gap-2 p-4 md:grid-cols-[170px_minmax(0,1fr)_180px]">
                  <div>
                    <div className="font-mono text-xs text-cyan-200">{item.operation}</div>
                    <div className={item.ok ? "mt-1 text-[10px] text-emerald-300" : "mt-1 text-[10px] text-red-300"}>{item.status}</div>
                  </div>
                  <p className="text-sm leading-6 text-neutral-300">{item.summary}</p>
                  <div className="font-mono text-[9px] text-neutral-500 md:text-right">{shortHash(item.receiptHash72)}<br />{new Date(item.createdAt).toLocaleTimeString()}</div>
                </article>
              ))}
            </div>
          </section>
        ) : null}
      </main>
    </section>
  )
}

const StateField: React.FC<{ label: string; value: string; ready: boolean }> = ({ label, value, ready }) => (
  <div className="rounded-lg border border-neutral-800 bg-black/50 p-2">
    <div className="text-neutral-600">{label}</div>
    <div className={`mt-1 truncate font-mono ${ready ? "text-emerald-300" : "text-neutral-500"}`} title={value}>{value}</div>
  </div>
)
