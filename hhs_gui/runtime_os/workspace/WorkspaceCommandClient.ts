export type WorkspaceAuthorityTier =
  | "PRESENTATION_ONLY"
  | "READ_ONLY"
  | "PROPOSE_ONLY"
  | "RECEIPT_ONLY"
  | "AUTHORIZED_NONMUTATING"
  | "AUTHORIZED_MUTATING"
  | "ADMINISTRATIVE_PROJECT_OPERATION"

export interface WorkspaceCommandEnvelope {
  schema: "HHS_WORKSPACE_COMMAND_ENVELOPE_V1"
  operation: string
  project_id?: string
  object_id?: string
  authority_tier: WorkspaceAuthorityTier
  payload: Record<string, unknown>
  requires_fastapi_authority: boolean
  frontend_may_commit_runtime_truth: false
}

const PRESENTATION_ONLY = new Set([
  "panel.resize",
  "panel.move",
  "canvas.zoom",
  "canvas.pan",
  "selection.change",
  "editor.cursor.move",
])

const READ_ONLY = new Set([
  "project.inspect",
  "object.inspect",
  "receipt.verify",
  "graph.query",
  "memory.search",
  "interpret.execute",
  "compile.execute",
])

export class WorkspaceCommandClient {
  constructor(
    private readonly baseUrl = "",
    private readonly timeoutMs = 30000,
  ) {}

  buildCommand(operation: string, payload: Record<string, unknown> = {}): WorkspaceCommandEnvelope {
    const presentation = PRESENTATION_ONLY.has(operation)
    const authorityTier: WorkspaceAuthorityTier = presentation
      ? "PRESENTATION_ONLY"
      : READ_ONLY.has(operation)
        ? "AUTHORIZED_NONMUTATING"
        : operation.startsWith("project.")
          ? "ADMINISTRATIVE_PROJECT_OPERATION"
          : "AUTHORIZED_MUTATING"

    return {
      schema: "HHS_WORKSPACE_COMMAND_ENVELOPE_V1",
      operation,
      project_id: String(payload.project_id ?? "project:default"),
      object_id: payload.object_id ? String(payload.object_id) : undefined,
      authority_tier: authorityTier,
      payload,
      requires_fastapi_authority: !presentation,
      frontend_may_commit_runtime_truth: false,
    }
  }

  async submit(operation: string, payload: Record<string, unknown> = {}): Promise<any> {
    const envelope = this.buildCommand(operation, payload)
    if (!envelope.requires_fastapi_authority) {
      return {
        schema: "HHS_WORKSPACE_PRESENTATION_ONLY_RESULT_V1",
        ok: true,
        status: "PRESENTATION_ONLY_LOCAL_STATE",
        canonical_runtime_mutated: false,
        envelope,
      }
    }

    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), this.timeoutMs)
    try {
      const response = await fetch(`${this.baseUrl}/api/runtime/workspace/command`, {
        method: "POST",
        headers: { accept: "application/json", "content-type": "application/json" },
        body: JSON.stringify(envelope),
        signal: controller.signal,
      })
      const body = await response.json()
      if (!response.ok) {
        throw new Error(String(body?.detail ?? body?.error ?? body?.status ?? response.statusText))
      }
      return body
    } finally {
      window.clearTimeout(timeout)
    }
  }
}
