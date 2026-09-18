import React, { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react"

type Json = Record<string, any>

type ChatMessage = {
  role: "user" | "assistant"
  content: string
  metadata?: string
}

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback
const short = (value: unknown): string => {
  const raw = text(value)
  return raw ? `${raw.slice(0, 10)}…${raw.slice(-6)}` : "—"
}

async function requestJson(url: string, init?: RequestInit, timeoutMs = 60000): Promise<Json> {
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

function receiptOf(turn: Json): string | null {
  for (const candidate of [
    record(turn.provider_invocation_receipt).provider_invocation_receipt_hash72,
    record(turn.provider_result_ingress).provider_result_ingress_root_hash72,
    turn.hhs_api_tool_trace_root_hash72,
    turn.turn_root_hash72,
  ]) {
    if (typeof candidate === "string" && candidate) return candidate
  }
  return null
}

export interface ProductionAssistantChatProps {
  projectId: string | null
  vectorContextId?: string | null
  onOpenFiles: () => void
}

export const ProductionAssistantChat: React.FC<ProductionAssistantChatProps> = ({
  projectId,
  vectorContextId,
  onOpenFiles,
}) => {
  const [health, setHealth] = useState<Json>({})
  const [threadId, setThreadId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement | null>(null)

  const online = health.online !== false && Object.keys(health).length > 0
  const modelLabel = text(
    health.model_id
      ?? health.selected_model_id
      ?? health.selected_provider_id
      ?? health.effective_mode
      ?? health.status,
    online ? "assistant ready" : "assistant checking",
  )

  const latestReceipt = useMemo(() => {
    const assistant = [...messages].reverse().find((message) => message.role === "assistant" && message.metadata)
    return assistant?.metadata ?? "No assistant turn yet"
  }, [messages])

  const refreshHealth = async (): Promise<void> => {
    try {
      setHealth(await requestJson("/api/assistant/health", undefined, 10000))
      setError(null)
    } catch (reason) {
      setHealth({ online: false, status: "ASSISTANT_OFFLINE" })
      setError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  useEffect(() => {
    void refreshHealth()
    const interval = window.setInterval(() => void refreshHealth(), 15000)
    return () => window.clearInterval(interval)
  }, [])

  useEffect(() => {
    const node = scrollRef.current
    if (node) node.scrollTop = node.scrollHeight
  }, [messages, busy])

  const resetThread = (): void => {
    setThreadId(null)
    setMessages([])
    setInput("")
    setError(null)
  }

  const send = async (event: FormEvent): Promise<void> => {
    event.preventDefault()
    const content = input.trim()
    if (!content || busy) return

    setBusy(true)
    setError(null)
    setInput("")
    setMessages((current) => [...current, { role: "user", content }])

    try {
      const turn = await requestJson("/api/assistant/chat", {
        method: "POST",
        body: JSON.stringify({
          thread_id: threadId,
          project_id: projectId || "project:production-mobile-control",
          title: "HHS Mobile Assistant",
          metadata: {
            workspace_surface: "production_mobile_control",
            vector_identity_visible_to_user: vectorContextId || null,
            vector_payload_auto_attached_to_prompt: false,
          },
          content,
        }),
      }, 120000)

      const nextThreadId = text(turn.thread_id ?? record(turn.thread).thread_id)
      if (nextThreadId) setThreadId(nextThreadId)

      const answer = text(
        record(turn.assistant_message).content
          ?? turn.response
          ?? turn.error,
        `Assistant turn completed with status ${text(turn.status, "UNKNOWN")}.`,
      )
      const receipt = receiptOf(turn)
      const mode = text(turn.effective_mode ?? turn.execution_backend ?? health.effective_mode)
      const toolCount = Number.isInteger(turn.hhs_api_tool_call_count) ? Number(turn.hhs_api_tool_call_count) : 0
      const metadata = [
        mode,
        `${toolCount} HHS tool${toolCount === 1 ? "" : "s"}`,
        receipt ? `receipt ${short(receipt)}` : "",
      ].filter(Boolean).join(" · ")

      setMessages((current) => [...current, {
        role: "assistant",
        content: answer,
        metadata,
      }])
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : String(reason)
      setError(message)
      setMessages((current) => [...current, {
        role: "assistant",
        content: "The assistant request did not complete. No response or runtime mutation was fabricated.",
        metadata: message,
      }])
    } finally {
      setBusy(false)
    }
  }

  const onComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): void => {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <section data-testid="production-mobile-assistant" className="overflow-hidden rounded-3xl border border-cyan-950 bg-neutral-900/70 shadow-2xl">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800 bg-black/35 px-4 py-3 md:px-5">
        <div className="min-w-0">
          <div className="text-[10px] uppercase tracking-[0.22em] text-cyan-500">Natural-language control</div>
          <h2 className="mt-1 text-base font-semibold text-white md:text-lg">HHS Assistant</h2>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => void refreshHealth()} className="rounded-full border border-neutral-800 bg-black/50 px-3 py-1.5 text-[10px] text-neutral-400">
            <span className={`mr-1.5 inline-block h-2 w-2 rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"}`} />
            {modelLabel}
          </button>
          <button type="button" onClick={resetThread} className="runtime-button min-h-9 px-3 text-xs">New chat</button>
        </div>
      </header>

      {error ? <div className="border-b border-red-900/60 bg-red-950/20 px-4 py-2 text-xs text-red-200">{error}</div> : null}

      <div ref={scrollRef} className="flex min-h-[42vh] max-h-[62vh] flex-col gap-3 overflow-y-auto bg-[radial-gradient(circle_at_top,rgba(8,145,178,.08),transparent_46%)] p-3 md:min-h-[460px] md:p-5">
        {messages.length === 0 ? (
          <div className="m-auto max-w-xl text-center">
            <div className="text-lg font-semibold text-white">How can I help?</div>
            <p className="mt-2 text-xs leading-5 text-neutral-500">Ask about your HHS workspace, runtime, files, applications, receipts, HARMONICODE, or any natural-language task supported by the configured assistant.</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {[
                "Summarize the current runtime state.",
                "Explain the latest Hash216 receipt.",
                "What can I do with the files in this workspace?",
              ].map((prompt) => (
                <button key={prompt} type="button" onClick={() => setInput(prompt)} className="rounded-full border border-neutral-800 bg-black/50 px-3 py-2 text-[11px] text-neutral-300 hover:border-cyan-800">
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : messages.map((message, index) => (
          <article
            key={`${message.role}:${index}`}
            className={`max-w-[92%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${message.role === "user" ? "ml-auto border border-cyan-800/50 bg-cyan-950/40 text-white" : "mr-auto border border-neutral-800 bg-black/45 text-neutral-200"}`}
          >
            {message.content}
            {message.metadata ? <div className="mt-2 font-mono text-[9px] leading-4 text-neutral-500">{message.metadata}</div> : null}
          </article>
        ))}

        {busy ? (
          <div className="mr-auto rounded-2xl border border-neutral-800 bg-black/45 px-4 py-3 text-xs text-neutral-400">
            Generating response…
          </div>
        ) : null}
      </div>

      <form onSubmit={(event) => void send(event)} className="border-t border-neutral-800 bg-black/55 p-3 md:p-4">
        <div className="rounded-2xl border border-neutral-700 bg-neutral-950 p-2 focus-within:border-cyan-700">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={onComposerKeyDown}
            placeholder="Message HHS…"
            rows={2}
            className="max-h-40 min-h-16 w-full resize-none bg-transparent px-2 py-2 text-sm leading-6 text-white outline-none placeholder:text-neutral-600"
            aria-label="Message HHS assistant"
          />
          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-neutral-900 pt-2">
            <div className="flex items-center gap-2">
              <button type="button" onClick={onOpenFiles} className="runtime-button min-h-9 px-3 text-xs">Files</button>
              <span className="hidden text-[9px] text-neutral-600 sm:inline">
                {vectorContextId ? `hydrated vector ${short(vectorContextId)} visible` : "no hydrated vector selected"}
              </span>
            </div>
            <button type="submit" disabled={busy || !input.trim()} className="min-h-10 rounded-xl bg-cyan-700 px-5 text-sm font-semibold text-white transition hover:bg-cyan-600 disabled:cursor-not-allowed disabled:bg-neutral-800 disabled:text-neutral-500">
              {busy ? "Working…" : "Send"}
            </button>
          </div>
        </div>
        <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[9px] leading-4 text-neutral-600">
          <span>Enter sends · Shift+Enter adds a line</span>
          <span>File/vector ingress is user-controlled; uploaded payloads are not automatically attached to assistant prompts.</span>
        </div>
      </form>

      <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-neutral-900 bg-black/35 px-4 py-2 font-mono text-[9px] text-neutral-600">
        <span>thread={threadId ? short(threadId) : "new"}</span>
        <span>{latestReceipt}</span>
      </footer>
    </section>
  )
}

export default ProductionAssistantChat
