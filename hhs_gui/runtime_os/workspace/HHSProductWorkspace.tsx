import React, { useEffect, useMemo, useState } from "react"
import type { RuntimeOS } from "../core/RuntimeOS"
import { ApprovalStatusPanel } from "./ApprovalStatusPanel"
import { AuthorityOperationsPanel } from "./AuthorityOperationsPanel"
import { HHSWorkspaceShell } from "./HHSWorkspaceShell"
import { ProductionMobileControlCenter } from "./ProductionMobileControlCenter"
import { RegistryVisualProgrammer } from "./RegistryVisualProgrammer"
import { WorkspaceCommandClient } from "./WorkspaceCommandClient"

type Json = Record<string, any>
type ProductSurface = "control" | "program" | "workspace" | "authority"

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback

async function requestJson(url: string, timeoutMs = 20000): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(url, {
      headers: { accept: "application/json" },
      signal: controller.signal,
    })
    const raw = await response.text()
    let body: Json = {}
    try {
      body = raw ? record(JSON.parse(raw)) : {}
    } catch {
      body = { detail: raw || response.statusText }
    }
    if (!response.ok) {
      const detail = record(body.detail)
      throw new Error(text(detail.classification ?? detail.detail ?? body.detail ?? body.error ?? body.status, `${response.status} ${response.statusText}`))
    }
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

export interface HHSProductWorkspaceProps {
  runtimeOS: RuntimeOS
  transportState: string
  transportError?: string | null
}

/**
 * Public production composition for the HHS Runtime OS.
 *
 * Mobile Control is the default click-through application server surface.
 * Heavy programming, workspace, and authority modules remain mounted only
 * when selected, preserving the existing backend-owned authority boundaries.
 */
export const HHSProductWorkspace: React.FC<HHSProductWorkspaceProps> = ({
  runtimeOS,
  transportState,
  transportError,
}) => {
  const commandClient = useMemo(() => new WorkspaceCommandClient(), [])
  const [surface, setSurface] = useState<ProductSurface>("control")
  const [session, setSession] = useState<Json>({})
  const [sessionError, setSessionError] = useState<string | null>(null)
  const [productHealth, setProductHealth] = useState<Json>({})
  const [healthError, setHealthError] = useState<string | null>(null)
  const [externalResultCount, setExternalResultCount] = useState(0)

  const refreshSession = async (): Promise<void> => {
    try {
      setSession(await requestJson("/api/runtime/workspace/session"))
      setSessionError(null)
    } catch (reason) {
      setSessionError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  const refreshHealth = async (): Promise<void> => {
    try {
      setProductHealth(await requestJson("/api/product/health", 8000))
      setHealthError(null)
    } catch (reason) {
      setHealthError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  useEffect(() => {
    void refreshSession()
    void refreshHealth()
    const interval = window.setInterval(() => void refreshHealth(), 15000)
    return () => window.clearInterval(interval)
  }, [])

  useEffect(() => {
    if (surface === "program" || surface === "control") void refreshSession()
  }, [surface])

  const project = record(session.project)
  const objects = Array.isArray(session.objects) ? session.objects.map(record) : []
  const selectedObject = objects.length > 0 ? objects[objects.length - 1] : null
  const projectId = text(project.project_id) || null
  const sourceObjectId = text(selectedObject?.object_id) || null
  const runtimeHealth = record(productHealth.runtime)
  const assistantHealth = record(productHealth.assistant)
  const runtimeOnline = Boolean(runtimeHealth.ok)
  const assistantOnline = Boolean(assistantHealth.online)
  const assistantMode = text(assistantHealth.effective_mode, assistantOnline ? "READY" : "OFFLINE")

  const executeWorkspaceOperation = async (operation: string, payload: Json): Promise<Json> => {
    const feedback = record(await commandClient.submit(operation, payload))
    if (feedback.ok === false) {
      throw new Error(text(record(feedback.result).status ?? feedback.status, `${operation} rejected`))
    }
    await refreshSession()
    return feedback
  }

  const recordExternalResult = (_operation: string, _feedback: Json): void => {
    setExternalResultCount((count) => count + 1)
  }

  const tabClass = (id: ProductSurface): string => `min-h-10 shrink-0 rounded-xl px-3 text-xs ${surface === id ? "bg-cyan-900 text-white shadow-lg" : "bg-neutral-900 text-neutral-400"}`

  return (
    <section data-testid="hhs-product-workspace" className="min-h-screen bg-neutral-950 text-white">
      <nav className="sticky top-0 z-50 border-b border-cyan-950 bg-black/95 px-2 py-2 backdrop-blur-xl md:px-4">
        <div className="mx-auto flex max-w-[1800px] items-center gap-3">
          <div className="min-w-0 flex-1">
            <div className="truncate text-sm font-semibold text-cyan-200">HHS Runtime OS</div>
            <div className="truncate text-[9px] text-neutral-500">
              {projectId ? `${text(project.name, "Workspace")} · ${projectId.slice(0, 12)}…` : "Production application server"}
              {externalResultCount > 0 ? ` · ${externalResultCount} registry dispatches` : ""}
            </div>
          </div>

          <div className="hidden items-center gap-2 lg:flex">
            <button type="button" onClick={() => void refreshHealth()} className="flex items-center gap-1.5 rounded-lg border border-neutral-800 bg-neutral-900 px-2 py-1 text-[9px]">
              <span className={`h-2 w-2 rounded-full ${runtimeOnline ? "bg-emerald-400" : "bg-red-400"}`} />
              runtime {runtimeOnline ? "online" : "offline"}
            </button>
            <button type="button" onClick={() => void refreshHealth()} className="flex items-center gap-1.5 rounded-lg border border-neutral-800 bg-neutral-900 px-2 py-1 text-[9px]" title={text(assistantHealth.selected_provider_id, assistantMode)}>
              <span className={`h-2 w-2 rounded-full ${assistantOnline ? "bg-emerald-400" : "bg-red-400"}`} />
              assistant {assistantOnline ? assistantMode.toLowerCase() : "offline"}
            </button>
          </div>
        </div>

        <div className="mx-auto mt-2 flex max-w-[1800px] gap-1 overflow-x-auto pb-0.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          <button type="button" onClick={() => setSurface("control")} className={tabClass("control")}>Control</button>
          <button type="button" onClick={() => setSurface("program")} className={tabClass("program")}>Visual Program</button>
          <button type="button" onClick={() => setSurface("workspace")} className={tabClass("workspace")}>Workspace</button>
          <button type="button" onClick={() => setSurface("authority")} className={tabClass("authority")}>Authority</button>
        </div>
      </nav>

      {healthError ? (
        <div className="m-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">Execution authority health request failed: {healthError}</div>
      ) : null}

      {sessionError && surface !== "control" ? (
        <div className="m-3 rounded-xl border border-amber-900 bg-amber-950/30 p-3 text-xs text-amber-200">Workspace session unavailable: {sessionError}. Registry services and application modules remain independently callable.</div>
      ) : null}

      {surface === "control" ? (
        <ProductionMobileControlCenter
          projectId={projectId}
          projectName={text(project.name, "HHS Mobile Ingress")}
          onNavigate={(next) => setSurface(next)}
        />
      ) : surface === "program" ? (
        <RegistryVisualProgrammer
          runtimeOS={runtimeOS}
          projectId={projectId}
          sourceObjectId={sourceObjectId}
          artifactId={null}
          executeWorkspaceOperation={executeWorkspaceOperation}
          onExternalResult={recordExternalResult}
        />
      ) : surface === "workspace" ? (
        <HHSWorkspaceShell runtimeOS={runtimeOS} transportState={transportState} transportError={transportError} />
      ) : (
        <>
          <ApprovalStatusPanel />
          <AuthorityOperationsPanel />
        </>
      )}
    </section>
  )
}
