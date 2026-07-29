import React, { useEffect, useMemo, useState } from "react"
import { RuntimeAssistantPanel } from "../assistant/RuntimeAssistantPanel"
import { LiveRuntimeProjectionPanel } from "../core/LiveRuntimeProjectionPanel"
import type { RuntimeOS } from "../core/RuntimeOS"
import { WorkspaceCommandClient } from "./WorkspaceCommandClient"

type JsonRecord = Record<string, any>
type WorkspaceTab = "workbench" | "assistant" | "runtime" | "receipts"
type BusyAction = "boot" | "project" | "source" | "interpret" | "compile" | "emulator" | "runtime" | null

type ActivityRecord = {
  id: string
  operation: string
  ok: boolean
  status: string
  summary: string
  receiptHash72: string | null
  createdAt: number
  raw?: JsonRecord
}

export interface HHSWorkspaceShellProps {
  runtimeOS: RuntimeOS
  transportState: string
  transportError?: string | null
}

const asRecord = (value: unknown): JsonRecord => value && typeof value === "object" ? value as JsonRecord : {}
const asString = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback
const shortHash = (value: unknown): string => {
  const text = asString(value)
  return text ? `${text.slice(0, 10)}…${text.slice(-6)}` : "—"
}

async function requestJson(url: string, init?: RequestInit, timeoutMs = 20000): Promise<JsonRecord> {
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
    const body = asRecord(await response.json())
    if (!response.ok) throw new Error(asString(body.detail ?? body.error ?? body.status, response.statusText))
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

function projectObjects(project: JsonRecord | null): JsonRecord[] {
  if (!project) return []
  const registry = asRecord(project.object_registry)
  const order = Array.isArray(project.object_order) ? project.object_order.map(String) : Object.keys(registry)
  return order.map((id) => asRecord(registry[id])).filter((item) => Object.keys(item).length > 0)
}

function extractProject(feedback: JsonRecord): JsonRecord | null {
  const result = asRecord(feedback.result)
  const registration = asRecord(result.registration)
  const candidates = [feedback.project, result.project, registration.project]
  for (const candidate of candidates) {
    const project = asRecord(candidate)
    if (project.project_id) return project
  }
  return null
}

function extractReceipt(feedback: JsonRecord): string | null {
  const result = asRecord(feedback.result)
  const artifact = asRecord(result.artifact)
  const registration = asRecord(result.registration)
  const receipt = asRecord(result.receipt)
  const executionReceipt = asRecord(result.execution_receipt)
  const candidate = feedback.receipt_hash72
    ?? result.receipt_hash72
    ?? result.result_root_hash72
    ?? artifact.receipt_hash72
    ?? registration.receipt_hash72
    ?? receipt.receipt_hash72
    ?? executionReceipt.receipt_hash72
  return typeof candidate === "string" ? candidate : null
}

function describe(operation: string, feedback: JsonRecord): string {
  const result = asRecord(feedback.result)
  if (operation === "project.create") {
    const project = asRecord(result.project)
    return `Opened ${asString(project.name, "workspace")} with canonical project identity.`
  }
  if (operation === "ingress.register") {
    const object = asRecord(result.workspace_object)
    return `Witnessed ${asString(object.name, "source")} as ${asString(object.modality, "source")} and registered it in the active project.`
  }
  if (operation === "interpret.execute") {
    return result.ok
      ? `Exact result: ${asString(result.display_value, "completed")}.`
      : `Interpretation rejected: ${(result.reasons ?? []).join(", ") || asString(result.status, "unknown rejection")}.`
  }
  if (operation === "compile.execute") {
    const artifact = asRecord(result.artifact)
    const ir = asRecord(artifact.ir)
    const operations = Array.isArray(ir.operations) ? ir.operations.length : 0
    return result.ok
      ? `Created ${asString(artifact.target, "HHS_IR")} artifact ${asString(artifact.artifact_id, "")}; ${operations} witnessed IR operation(s).`
      : `Compilation rejected: ${asString(result.status, "unknown rejection")}.`
  }
  if (operation.startsWith("emulator.")) {
    const session = asRecord(result.session)
    return result.ok
      ? `${asString(result.status, operation)} · tick ${String(session.tick ?? 0)} · ${asString(session.mode, "PAUSED")}.`
      : `Emulator request rejected: ${asString(result.status, "unknown rejection")}.`
  }
  return asString(feedback.status ?? result.status, operation)
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
  const [project, setProject] = useState<JsonRecord | null>(null)
  const [objects, setObjects] = useState<JsonRecord[]>([])
  const [selectedObjectId, setSelectedObjectId] = useState<string | null>(null)
  const [projectName, setProjectName] = useState("HHS Workspace")
  const [sourceName, setSourceName] = useState("main.hhs")
  const [sourceText, setSourceText] = useState("")
  const [witnessedSourceText, setWitnessedSourceText] = useState("")
  const [expression, setExpression] = useState("1+2*3/4")
  const [target, setTarget] = useState("HHS_IR")
  const [artifact, setArtifact] = useState<JsonRecord | null>(null)
  const [emulatorSession, setEmulatorSession] = useState<JsonRecord | null>(null)
  const [lastResult, setLastResult] = useState<JsonRecord | null>(null)
  const [activity, setActivity] = useState<ActivityRecord[]>([])

  const selectedObject = objects.find((item) => item.object_id === selectedObjectId) ?? null
  const projectId = asString(project?.project_id)
  const sourceDirty = sourceText !== witnessedSourceText
  const artifactId = asString(artifact?.artifact_id)
  const sessionId = asString(emulatorSession?.session_id)

  const mergeSession = (session: JsonRecord): void => {
    const nextProject = asRecord(session.project)
    if (nextProject.project_id) {
      setProject(nextProject)
      const nextObjects = Array.isArray(session.objects)
        ? session.objects.map(asRecord)
        : projectObjects(nextProject)
      setObjects(nextObjects)
      setSelectedObjectId((current) => current ?? asString(nextObjects.at(-1)?.object_id) || null)
    }
    const remoteHistory = Array.isArray(session.history) ? session.history.map(asRecord) : []
    if (remoteHistory.length) {
      setActivity(remoteHistory.map((item, index) => ({
        id: asString(item.command_id, `remote-${index}`),
        operation: asString(item.operation, "workspace.command"),
        ok: Boolean(item.ok),
        status: asString(item.status, "UNKNOWN"),
        summary: asString(item.status, "Workspace command"),
        receiptHash72: typeof item.receipt_hash72 === "string" ? item.receipt_hash72 : null,
        createdAt: Date.now() - (remoteHistory.length - index) * 1000,
      })))
    }
  }

  const refreshSession = async (requestedProjectId?: string): Promise<void> => {
    const query = requestedProjectId ? `?project_id=${encodeURIComponent(requestedProjectId)}` : ""
    const session = await requestJson(`/api/runtime/workspace/session${query}`)
    mergeSession(session)
  }

  useEffect(() => {
    let active = true
    requestJson("/api/runtime/workspace/session")
      .then((session) => { if (active) mergeSession(session) })
      .catch((reason: unknown) => { if (active) setError(reason instanceof Error ? reason.message : String(reason)) })
      .finally(() => { if (active) setBusyAction(null) })
    return () => { active = false }
  }, [])

  const applyFeedback = (operation: string, feedback: JsonRecord): void => {
    const result = asRecord(feedback.result)
    const nextProject = extractProject(feedback)
    if (nextProject) {
      setProject(nextProject)
      setObjects(projectObjects(nextProject))
    }

    const workspaceObject = asRecord(result.workspace_object)
    if (workspaceObject.object_id) {
      setSelectedObjectId(asString(workspaceObject.object_id))
      setWitnessedSourceText(sourceText)
    }

    const compiledArtifact = asRecord(result.artifact)
    if (compiledArtifact.artifact_id) setArtifact(compiledArtifact)
    const nextSession = asRecord(result.session)
    if (nextSession.session_id) setEmulatorSession(nextSession)

    const receiptHash72 = extractReceipt(feedback)
    setLastResult({ operation, feedback, result, receipt_hash72: receiptHash72 })
    setActivity((current) => [{
      id: `${operation}:${Date.now()}`,
      operation,
      ok: Boolean(feedback.ok),
      status: asString(feedback.status ?? result.status, feedback.ok ? "COMPLETED" : "REJECTED"),
      summary: describe(operation, feedback),
      receiptHash72,
      createdAt: Date.now(),
      raw: feedback,
    }, ...current].slice(0, 48))
  }

  const submit = async (operation: string, payload: JsonRecord): Promise<JsonRecord> => {
    const feedback = asRecord(await commandClient.submit(operation, payload))
    applyFeedback(operation, feedback)
    if (feedback.ok === false) throw new Error(describe(operation, feedback))
    return feedback
  }

  const ensureProject = async (): Promise<JsonRecord> => {
    if (project?.project_id) return project
    const feedback = await submit("project.create", { name: projectName })
    const created = extractProject(feedback)
    if (!created) throw new Error("Project authority returned no project identity")
    return created
  }

  const ensureSource = async (activeProject: JsonRecord): Promise<JsonRecord> => {
    if (selectedObject?.object_id && !sourceDirty) return selectedObject
    if (!sourceText.trim()) throw new Error("Enter source content before witnessing or compiling it")
    const feedback = await submit("ingress.register", {
      project_id: activeProject.project_id,
      source_name: sourceName,
      source_payload: sourceText,
      declared_modality: sourceName.endsWith(".hhs") ? "HARMONICODE_SOURCE" : "TEXT",
    })
    const object = asRecord(asRecord(feedback.result).workspace_object)
    if (!object.object_id) throw new Error("Ingress completed without a workspace object")
    await refreshSession(asString(activeProject.project_id))
    return object
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
    const activeProject = await ensureProject()
    await ensureSource(activeProject)
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

  const ensureArtifact = async (): Promise<JsonRecord> => {
    if (artifact?.artifact_id && !sourceDirty) return artifact
    const activeProject = await ensureProject()
    const object = await ensureSource(activeProject)
    const feedback = await submit("compile.execute", {
      project_id: activeProject.project_id,
      source_object_id: object.object_id,
      source_text: sourceText,
      target,
    })
    const nextArtifact = asRecord(asRecord(feedback.result).artifact)
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
    setLastResult({ operation: "runtime.live.tick", result })
    setActivity((current) => [{
      id: `runtime.live.tick:${Date.now()}`,
      operation: "runtime.live.tick",
      ok: Boolean(result.ok ?? true),
      status: asString(result.status, "RUNTIME_TICK_COMPLETED"),
      summary: `Advanced the canonical live runtime workflow by one bounded tick.`,
      receiptHash72: typeof result.receipt_hash72 === "string" ? result.receipt_hash72 : null,
      createdAt: Date.now(),
      raw: result,
    }, ...current].slice(0, 48))
  })

  const recordAssistantReceipt = (receiptHash72: string, raw: JsonRecord): void => {
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
              {project ? `${asString(project.name, "Workspace")} · ${shortHash(project.project_id)}` : "Create a project to begin"}
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
            <button
              key={id}
              type="button"
              onClick={() => setTab(id)}
              className={`min-h-10 rounded-lg px-2 text-xs ${tab === id ? "bg-cyan-900 text-white" : "bg-neutral-900 text-neutral-400"}`}
            >
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
                    <button
                      key={asString(object.object_id)}
                      type="button"
                      onClick={() => setSelectedObjectId(asString(object.object_id))}
                      className={`w-full rounded-xl border p-3 text-left ${selectedObjectId === object.object_id ? "border-cyan-700 bg-cyan-950/40" : "border-neutral-800 bg-black/40"}`}
                    >
                      <div className="truncate text-xs font-medium text-neutral-100">{asString(object.name, "workspace object")}</div>
                      <div className="mt-1 truncate text-[9px] text-neutral-500">{asString(object.object_type)} · {asString(object.lifecycle_state)}</div>
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
                    <p className="text-[10px] text-neutral-500">Every action below advances the same selected project and receipt chain.</p>
                  </div>
                  <span className={sourceDirty ? "text-[10px] text-amber-300" : "text-[10px] text-emerald-300"}>{sourceDirty ? "local changes not witnessed" : "source witnessed"}</span>
                </div>
              </div>

              <div className="space-y-3 p-3">
                <div className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_160px]">
                  <input value={sourceName} onChange={(event) => setSourceName(event.target.value)} className="rounded-lg border border-neutral-700 bg-black p-2 text-sm" aria-label="Source file name" />
                  <select value={target} onChange={(event) => setTarget(event.target.value)} className="rounded-lg border border-neutral-700 bg-black p-2 text-sm" aria-label="Compiler target">
                    {[
                      "HHS_IR",
                      "C_KERNEL_PLAN",
                      "C_SOURCE",
                      "PYTHON_ADAPTER",
                      "JSON_EXECUTION_GRAPH",
                      "DOT_GRAPH",
                      "BYTECODE_OR_VM_PLAN",
                      "RECEIPT_ONLY_PLAN",
                    ].map((item) => <option key={item}>{item}</option>)}
                  </select>
                </div>

                <textarea
                  value={sourceText}
                  onChange={(event) => setSourceText(event.target.value)}
                  className="min-h-[38vh] w-full resize-y rounded-xl border border-neutral-700 bg-black p-3 font-mono text-sm leading-6 text-cyan-50 outline-none focus:border-cyan-600"
                  placeholder="Enter HARMONICODE or source content…"
                  spellCheck={false}
                  aria-label="HHS source editor"
                />

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
                    <div className="flex items-center justify-between text-xs"><span>{asString(emulatorSession.mode, "PAUSED")}</span><span>tick {String(emulatorSession.tick ?? 0)}</span></div>
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
                  <span className="font-mono text-[9px] text-neutral-600">{shortHash(asRecord(lastResult).receipt_hash72)}</span>
                </div>
                {lastResult ? (
                  <>
                    <p className="mt-3 text-sm leading-6 text-neutral-200">{describe(asString(lastResult.operation), asRecord(lastResult.feedback ?? lastResult.result))}</p>
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
          <RuntimeAssistantPanel
            projectId={projectId || null}
            sourceObjectId={selectedObjectId}
            sourceName={sourceName}
            artifactId={artifactId || null}
            onReceipt={recordAssistantReceipt}
          />
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
