import React, { FormEvent, useEffect, useState } from "react"

type Message = {
  role: "user" | "assistant"
  content: string
  metadata?: string
}

type JsonObject = Record<string, unknown>

function asObject(value: unknown): JsonObject {
  return value && typeof value === "object" ? value as JsonObject : {}
}

function shortHash(value: unknown): string {
  const text = typeof value === "string" ? value : ""
  return text ? `${text.slice(0, 18)}…` : "none"
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

export const RuntimeAssistantPanel: React.FC = () => {
  const [health, setHealth] = useState<JsonObject | null>(null)
  const [threadId, setThreadId] = useState<string | null>(null)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let active = true
    requestJson("/api/assistant/health")
      .then((result) => { if (active) setHealth(result) })
      .catch((error: unknown) => {
        if (active) setHealth({ online: false, error: error instanceof Error ? error.message : String(error) })
      })
    return () => { active = false }
  }, [])

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
          project_id: "project:visual-runtime-os",
          title: "HHS Runtime OS Assistant",
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

      setMessages((current) => [...current, {
        role: "assistant",
        content: responseText,
        metadata: `${provider} · ${toolCalls} governed tool call(s) · receipt ${shortHash(receiptHash)}`,
      }])
    } catch (error: unknown) {
      setMessages((current) => [...current, {
        role: "assistant",
        content: `Assistant request failed: ${error instanceof Error ? error.message : String(error)}`,
        metadata: "No assistant response or runtime mutation was fabricated.",
      }])
    } finally {
      setBusy(false)
    }
  }

  const online = Boolean(health?.online && health?.ok)
  const provider = String(health?.selected_provider_id ?? health?.effective_mode ?? "checking")

  return (
    <section data-testid="runtime-assistant-panel" className="rounded-xl border border-cyan-900/60 bg-neutral-950 p-2">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h3 className="text-xs font-semibold text-cyan-200">Natural-language HHS Assistant</h3>
          <p className="text-[10px] text-neutral-400">Real provider output, governed tools, Hash72-linked ingress.</p>
        </div>
        <span className={online ? "text-[10px] text-emerald-300" : "text-[10px] text-amber-300"}>
          {online ? provider : "provider unavailable"}
        </span>
      </div>

      <div className="mt-2 max-h-72 space-y-2 overflow-auto rounded-lg border border-neutral-800 bg-black/50 p-2">
        {messages.length === 0 ? (
          <div className="text-[10px] text-neutral-500">Ask about runtime state, HARMONICODE, capabilities, projects, receipts, or installed language memory.</div>
        ) : messages.slice(-20).map((message, index) => (
          <article key={`${message.role}-${index}`} className={message.role === "user" ? "rounded-lg bg-cyan-950/50 p-2" : "rounded-lg bg-neutral-900 p-2"}>
            <div className="whitespace-pre-wrap text-[11px] text-neutral-100">{message.content}</div>
            {message.metadata ? <small className="mt-1 block text-[9px] text-neutral-500">{message.metadata}</small> : null}
          </article>
        ))}
      </div>

      <form className="mt-2 grid gap-2" onSubmit={submit}>
        <textarea
          className="min-h-20 rounded-lg border border-neutral-700 bg-black p-2 text-[11px] text-white outline-none focus:border-cyan-500"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask HHS…"
          required
        />
        <div className="flex items-center justify-between gap-2">
          <button className="runtime-button px-3 py-2 text-[11px]" type="submit" disabled={busy || !online}>
            {busy ? "Processing…" : "Send"}
          </button>
          <button className="runtime-button px-3 py-2 text-[11px]" type="button" onClick={() => { setThreadId(null); setMessages([]) }}>
            New thread
          </button>
        </div>
      </form>
    </section>
  )
}
