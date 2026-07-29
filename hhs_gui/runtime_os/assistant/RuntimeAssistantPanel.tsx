import React, { FormEvent, useEffect, useRef, useState } from "react"

type Message = {
  role: "user" | "assistant"
  content: string
  metadata?: string
}

type JsonObject = Record<string, unknown>

export interface RuntimeAssistantPanelProps {
  projectId?: string | null
  sourceObjectId?: string | null
  sourceName?: string
  artifactId?: string | null
  onReceipt?: (receiptHash72: string, result: JsonObject) => void
}

function asObject(value: unknown): JsonObject {
  return value && typeof value === "object" ? value as JsonObject : {}
}

function shortHash(value: unknown): string {
  const text = typeof value === "string" ? value : ""
  return text ? `${text.slice(0, 12)}…${text.slice(-6)}` : "none"
}

async function requestJson(url: string, init?: RequestInit): Promise<JsonObject> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 45000)
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
    const body = asObject(await response.json())
    if (!response.ok) {
      throw new Error(JSON.stringify(body.detail ?? body.error ?? body.status ?? response.statusText))
    }
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

export const RuntimeAssistantPanel: React.FC<RuntimeAssistantPanelProps> = ({
  projectId,
  sourceObjectId,
  sourceName = "main.hhs",
  artifactId,
  onReceipt,
}) => {
  const [health, setHealth] = useState<JsonObject | null>(null)
  const [threadId, setThreadId] = useState<string | null>(null)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [busy, setBusy] = useState(false)
  const transcriptRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let active = true
    requestJson("/api/assistant/health")
      .then((result) => { if (active) setHealth(result) })
      .catch((error: unknown) => {
        if (active) setHealth({ online: false, error: error instanceof Error ? error.message : String(error) })
      })
    return () => { active = false }
  }, [])

  useEffect(() => {
    transcriptRef.current?.scrollTo({ top: transcriptRef.current.scrollHeight, behavior: "smooth" })
  }, [messages, busy])

  async function submit(event: FormEvent): Promise<void> {
    event.preventDefault()
    const content = input.trim()
    if (!content || busy) return

    setInput("")
    setBusy(true)
    setMessages((current) => [...current, { role: "user", content }])

    try {
      const result = await requestJson("/api/assistant/chat", {
        method: "POST",
        body: JSON.stringify({
          thread_id: threadId,
          project_id: projectId ?? "project:default",
          title: `HHS Workspace · ${sourceName}`,
          metadata: {
            workspace_surface: "HHS_INTEGRATED_WORKSPACE_V1",
            source_object_id: sourceObjectId,
            source_name: sourceName,
            artifact_id: artifactId,
          },
          content,
        }),
      })
      const thread = asObject(result.thread)
      const returnedThreadId = result.thread_id ?? thread.thread_id
      if (typeof returnedThreadId === "string") setThreadId(returnedThreadId)

      const assistantMessage = asObject(result.assistant_message)
      const responseText = String(
        assistantMessage.content
        ?? result.error
        ?? `Assistant turn closed with status ${String(result.status ?? "UNKNOWN")}.`,
      )
      const receipt = asObject(result.provider_invocation_receipt)
      const ingress = asObject(result.provider_result_ingress)
      const receiptHash = receipt.provider_invocation_receipt_hash72
        ?? ingress.provider_result_ingress_root_hash72
        ?? result.turn_root_hash72
      const provider = String(result.selected_provider_id ?? result.execution_backend ?? "unresolved provider")
      const toolCalls = Number(result.hhs_api_tool_call_count ?? 0)

      if (typeof receiptHash === "string") onReceipt?.(receiptHash, result)
      setMessages((current) => [...current, {
        role: "assistant",
        content: responseText,
        metadata: `${provider} · ${toolCalls} governed tool call(s) · ${shortHash(receiptHash)}`,
      }])
    } catch (error: unknown) {
      setMessages((current) => [...current, {
        role: "assistant",
        content: `Assistant request failed: ${error instanceof Error ? error.message : String(error)}`,
        metadata: "No response or runtime mutation was fabricated.",
      }])
    } finally {
      setBusy(false)
    }
  }

  const online = Boolean(health?.online && health?.ok)
  const provider = String(health?.selected_provider_id ?? health?.effective_mode ?? "checking")

  return (
    <section data-testid="runtime-assistant-panel" className="flex min-h-[60vh] flex-col rounded-2xl border border-cyan-900/60 bg-neutral-950">
      <header className="flex items-center justify-between gap-3 border-b border-neutral-800 px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-cyan-100">Workspace assistant</h2>
          <p className="text-[10px] text-neutral-500">Project {projectId ?? "not created"} · source {sourceName}</p>
        </div>
        <span className={online ? "text-[10px] text-emerald-300" : "text-[10px] text-amber-300"}>
          {online ? provider : "provider unavailable"}
        </span>
      </header>

      <div ref={transcriptRef} className="min-h-0 flex-1 space-y-3 overflow-auto p-3">
        {messages.length === 0 ? (
          <div className="mx-auto mt-12 max-w-lg rounded-xl border border-neutral-800 bg-neutral-900/70 p-4 text-sm leading-6 text-neutral-400">
            Ask about the active project, source, compilation, runtime state, installed language memory, receipts, or the next executable operation. The assistant thread is bound to this workspace context.
          </div>
        ) : messages.slice(-40).map((message, index) => (
          <article key={`${message.role}-${index}`} className={message.role === "user" ? "ml-auto max-w-[88%] rounded-2xl rounded-br-sm bg-cyan-950/70 p-3" : "mr-auto max-w-[92%] rounded-2xl rounded-bl-sm bg-neutral-900 p-3"}>
            <div className="whitespace-pre-wrap text-sm leading-6 text-neutral-100">{message.content}</div>
            {message.metadata ? <small className="mt-2 block text-[9px] text-neutral-500">{message.metadata}</small> : null}
          </article>
        ))}
        {busy ? <div className="text-xs text-cyan-300">Executing governed assistant turn…</div> : null}
      </div>

      <form className="border-t border-neutral-800 p-3" onSubmit={submit}>
        <textarea
          className="min-h-24 w-full resize-y rounded-xl border border-neutral-700 bg-black p-3 text-sm text-white outline-none focus:border-cyan-500"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder={online ? "Ask HHS about this workspace…" : "Assistant provider is not ready"}
          required
        />
        <div className="mt-2 flex items-center justify-between gap-2">
          <button className="runtime-button min-h-10 px-4 py-2 text-sm" type="submit" disabled={busy || !online}>
            {busy ? "Processing…" : "Send"}
          </button>
          <button className="runtime-button min-h-10 px-3 py-2 text-xs" type="button" onClick={() => { setThreadId(null); setMessages([]) }}>
            New thread
          </button>
        </div>
      </form>
    </section>
  )
}
