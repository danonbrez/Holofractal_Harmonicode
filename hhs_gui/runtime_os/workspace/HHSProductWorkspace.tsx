import React, { useEffect, useMemo, useState } from "react"
import type { RuntimeOS } from "../core/RuntimeOS"
import { HHSWorkspaceShell } from "./HHSWorkspaceShell"
import { RegistryVisualProgrammer } from "./RegistryVisualProgrammer"
import { WorkspaceCommandClient } from "./WorkspaceCommandClient"

type Json = Record<string, any>
type ProductSurface = "program" | "workspace"

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback

async function requestSession(): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 20000)
  try {
    const response = await fetch("/api/runtime/workspace/session", {
      headers: { accept: "application/json" },
      signal: controller.signal,
    })
    const body = record(await response.json())
    if (!response.ok) throw new Error(text(body.detail ?? body.error ?? body.status, response.statusText))
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
 * Product composition for the public Runtime OS.
 *
 * The registry canvas is the primary object-oriented programming surface.
 * The conventional workspace remains fully available and is mounted on demand,
 * so no functionality is removed and inactive modules do not consume resources.
 */
export const HHSProductWorkspace: React.FC<HHSProductWorkspaceProps> = ({
  runtimeOS,
  transportState,
  transportError,
}) => {
  const commandClient = useMemo(() => new WorkspaceCommandClient(), [])
  const [surface, setSurface] = useState<ProductSurface>("program")
  const [session, setSession] = useState<Json>({})
  const [sessionError, setSessionError] = useState<string | null>(null)
  const [externalResultCount, setExternalResultCount] = useState(0)

  const refreshSession = async (): Promise<void> => {
    try {
      setSession(await requestSession())
      setSessionError(null)
    } catch (reason) {
      setSessionError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  useEffect(() => {
    void refreshSession()
  }, [])

  useEffect(() => {
    if (surface === "program") void refreshSession()
  }, [surface])

  const project = record(session.project)
  const objects = Array.isArray(session.objects) ? session.objects.map(record) : []
  const selectedObject = objects.length > 0 ? objects[objects.length - 1] : null
  const projectId = text(project.project_id) || null
  const sourceObjectId = text(selectedObject?.object_id) || null

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

  return (
    <section data-testid="hhs-product-workspace" className="min-h-screen bg-neutral-950 text-white">
      <nav className="sticky top-0 z-50 border-b border-cyan-950 bg-black/95 p-2 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1800px] items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold text-cyan-200">HHS Visual Runtime OS</div>
            <div className="truncate text-[9px] text-neutral-500">
              {projectId ? `${text(project.name, "Workspace")} · ${projectId.slice(0, 12)}…` : "Registry-driven modular programming"}
              {externalResultCount > 0 ? ` · ${externalResultCount} registry dispatches` : ""}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-1 rounded-xl border border-neutral-800 bg-neutral-900 p-1">
            <button
              type="button"
              onClick={() => setSurface("program")}
              className={`min-h-9 rounded-lg px-3 text-xs ${surface === "program" ? "bg-cyan-900 text-white" : "text-neutral-400"}`}
            >
              Visual Program
            </button>
            <button
              type="button"
              onClick={() => setSurface("workspace")}
              className={`min-h-9 rounded-lg px-3 text-xs ${surface === "workspace" ? "bg-cyan-900 text-white" : "text-neutral-400"}`}
            >
              Workspace
            </button>
          </div>
        </div>
      </nav>

      {sessionError ? (
        <div className="m-3 rounded-xl border border-amber-900 bg-amber-950/30 p-3 text-xs text-amber-200">
          Workspace session unavailable: {sessionError}. Registry services and application modules remain independently callable.
        </div>
      ) : null}

      {surface === "program" ? (
        <RegistryVisualProgrammer
          runtimeOS={runtimeOS}
          projectId={projectId}
          sourceObjectId={sourceObjectId}
          artifactId={null}
          executeWorkspaceOperation={executeWorkspaceOperation}
          onExternalResult={recordExternalResult}
        />
      ) : (
        <HHSWorkspaceShell
          runtimeOS={runtimeOS}
          transportState={transportState}
          transportError={transportError}
        />
      )}
    </section>
  )
}
