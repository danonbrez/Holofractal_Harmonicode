import React, { useEffect, useMemo, useRef, useState } from "react"
import { createStoredZip } from "../artifacts/createStoredZip"
import { WorkspaceCommandClient } from "./WorkspaceCommandClient"

type Json = Record<string, any>

const STORAGE_KEY = "hhs.pass185.production-lifecycle.v1"

const CALCULATOR_HTML = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HHS Pass 185 Calculator</title>
<style>
body{font-family:system-ui,sans-serif;margin:0;min-height:100vh;display:grid;place-items:center;background:#071017;color:#e8fbff}
main{width:min(360px,92vw);padding:20px;border:1px solid #155e75;border-radius:18px;background:#06141d}
#display{min-height:54px;padding:12px;border-radius:10px;background:#d8f3f7;color:#10272c;font-size:28px;text-align:right;overflow-wrap:anywhere}
.keys{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px}
button{min-height:52px;border:0;border-radius:10px;background:#164e63;color:white;font-size:20px}
button[data-key="="]{background:#0e7490}
</style>
</head>
<body>
<main data-hhs-calculator="true">
<h1>Calculator</h1>
<div id="display" aria-live="polite">0</div>
<div class="keys">
<button data-key="7">7</button><button data-key="8">8</button><button data-key="+">+</button><button data-key="=">=</button>
<button data-key="1">1</button><button data-key="2">2</button><button data-key="3">3</button><button data-key="C">C</button>
</div>
</main>
<script>
(() => {
  let expression = "";
  const display = document.querySelector("#display");
  const render = () => { display.textContent = expression || "0"; };
  document.querySelectorAll("[data-key]").forEach((button) => button.addEventListener("click", () => {
    const key = button.dataset.key;
    if (key === "C") { expression = ""; render(); return; }
    if (key === "=") {
      const match = expression.match(/^(-?\\d+)\\+(-?\\d+)$/);
      expression = match ? String(Number(match[1]) + Number(match[2])) : "ERROR";
      render();
      return;
    }
    expression += key;
    render();
  }));
})();
</script>
</body>
</html>`

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback

interface PersistedLifecycle {
  schema: "HHS_PASS185_RUNTIME_OS_LIFECYCLE_STATE_V1"
  projectId: string | null
  sourceObjectId: string | null
  projectName: string
  sourceName: string
  sourceText: string
  savedAt: string | null
}

function restore(): PersistedLifecycle {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const value = record(JSON.parse(raw))
      if (value.schema === "HHS_PASS185_RUNTIME_OS_LIFECYCLE_STATE_V1") {
        return {
          schema: "HHS_PASS185_RUNTIME_OS_LIFECYCLE_STATE_V1",
          projectId: text(value.projectId) || null,
          sourceObjectId: text(value.sourceObjectId) || null,
          projectName: text(value.projectName, "Pass 185 Calculator"),
          sourceName: text(value.sourceName, "index.html"),
          sourceText: text(value.sourceText),
          savedAt: text(value.savedAt) || null,
        }
      }
    }
  } catch {}
  return {
    schema: "HHS_PASS185_RUNTIME_OS_LIFECYCLE_STATE_V1",
    projectId: null,
    sourceObjectId: null,
    projectName: "Pass 185 Calculator",
    sourceName: "index.html",
    sourceText: "",
    savedAt: null,
  }
}

export const Pass185ApplicationLifecyclePanel: React.FC = () => {
  const commandClient = useMemo(() => new WorkspaceCommandClient(), [])
  const initial = useMemo(restore, [])
  const [projectId, setProjectId] = useState<string | null>(initial.projectId)
  const [sourceObjectId, setSourceObjectId] = useState<string | null>(initial.sourceObjectId)
  const [projectName, setProjectName] = useState(initial.projectName)
  const [sourceName, setSourceName] = useState(initial.sourceName)
  const [sourceText, setSourceText] = useState(initial.sourceText)
  const [savedText, setSavedText] = useState(initial.sourceText)
  const [savedAt, setSavedAt] = useState<string | null>(initial.savedAt)
  const [previewHtml, setPreviewHtml] = useState(initial.sourceText)
  const [previewRevision, setPreviewRevision] = useState(0)
  const [previewReady, setPreviewReady] = useState(false)
  const [status, setStatus] = useState(initial.sourceText ? "REOPENED_SAVED_SOURCE" : "EMPTY")
  const [testStatus, setTestStatus] = useState("NOT_RUN")
  const [lastReceipt, setLastReceipt] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const iframeRef = useRef<HTMLIFrameElement | null>(null)

  const store = (patch: Partial<PersistedLifecycle> = {}): void => {
    const value: PersistedLifecycle = {
      schema: "HHS_PASS185_RUNTIME_OS_LIFECYCLE_STATE_V1",
      projectId,
      sourceObjectId,
      projectName,
      sourceName,
      sourceText,
      savedAt,
      ...patch,
    }
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
  }

  useEffect(() => {
    if (!initial.projectId) return
    fetch(`/api/runtime/workspace/session?project_id=${encodeURIComponent(initial.projectId)}`, {
      headers: { accept: "application/json" },
    })
      .then(async (response) => ({ response, body: record(await response.json()) }))
      .then(({ response, body }) => {
        if (response.ok && text(record(body.project).project_id) === initial.projectId) {
          setStatus("REOPENED_BACKEND_PROJECT")
        }
      })
      .catch(() => undefined)
  }, [initial.projectId])

  const createCalculator = (): void => {
    setProjectName("Pass 185 Calculator")
    setSourceName("index.html")
    setSourceText(CALCULATOR_HTML)
    setPreviewHtml("")
    setPreviewReady(false)
    setTestStatus("NOT_RUN")
    setStatus("CALCULATOR_SOURCE_CREATED")
    setError(null)
    store({
      projectName: "Pass 185 Calculator",
      sourceName: "index.html",
      sourceText: CALCULATOR_HTML,
    })
  }

  const ensureProject = async (): Promise<string> => {
    if (projectId) return projectId
    const feedback = record(await commandClient.submit("project.create", { name: projectName }))
    const id = text(record(record(feedback.result).project).project_id)
    if (!id || feedback.ok === false) throw new Error(text(feedback.status, "PROJECT_CREATE_FAILED"))
    setProjectId(id)
    store({ projectId: id })
    return id
  }

  const saveSource = async (): Promise<void> => {
    if (!sourceText.trim()) throw new Error("SOURCE_REQUIRED")
    setBusy(true)
    setError(null)
    try {
      const activeProjectId = await ensureProject()
      const feedback = record(await commandClient.submit("ingress.register", {
        project_id: activeProjectId,
        source_name: sourceName,
        source_payload: sourceText,
        declared_modality: "TEXT",
      }))
      if (feedback.ok === false) throw new Error(text(feedback.status, "SOURCE_SAVE_REJECTED"))
      const result = record(feedback.result)
      const object = record(result.workspace_object)
      const objectId = text(object.object_id) || null
      const receipt = text(feedback.receipt_hash72)
        || text(result.receipt_hash72)
        || text(object.root_hash72)
        || text(object.current_root_hash72)
        || null
      const at = new Date().toISOString()
      setSourceObjectId(objectId)
      setLastReceipt(receipt)
      setSavedText(sourceText)
      setSavedAt(at)
      setStatus("SOURCE_WITNESSED")
      store({ projectId: activeProjectId, sourceObjectId: objectId, sourceText, savedAt: at })
    } finally {
      setBusy(false)
    }
  }

  const openPreview = (): void => {
    if (!sourceText.trim()) {
      setError("SOURCE_REQUIRED")
      return
    }
    setPreviewReady(false)
    setPreviewHtml(sourceText)
    setPreviewRevision((value) => value + 1)
    setStatus("PREVIEW_REQUESTED")
    setError(null)
  }

  const runPreviewTest = (): void => {
    try {
      const doc = iframeRef.current?.contentDocument
      if (!doc) throw new Error("PREVIEW_DOCUMENT_UNAVAILABLE")
      const click = (key: string): void => {
        const button = doc.querySelector(`button[data-key="${key}"]`) as HTMLButtonElement | null
        if (!button) throw new Error(`PREVIEW_KEY_MISSING:${key}`)
        button.click()
      }
      const clear = doc.querySelector('button[data-key="C"]') as HTMLButtonElement | null
      clear?.click()
      for (const key of ["7", "+", "8", "="]) click(key)
      const result = doc.querySelector("#display")?.textContent?.trim()
      if (result !== "15") throw new Error(`CALCULATOR_ASSERTION_FAILED:${result ?? "<missing>"}`)
      setTestStatus("CALCULATOR_7_PLUS_8_EQUALS_15")
      setStatus("PREVIEW_TEST_VERIFIED")
      setError(null)
    } catch (reason) {
      setTestStatus("FAILED")
      setError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  const exportZip = (): void => {
    try {
      if (!sourceText.trim()) throw new Error("SOURCE_REQUIRED")
      const manifest = {
        schema: "HHS_PASS185_RUNTIME_OS_BROWSER_APPLICATION_V1",
        project_id: projectId,
        source_object_id: sourceObjectId,
        project_name: projectName,
        entrypoint: "index.html",
        source_name: sourceName,
        source_saved: sourceText === savedText && Boolean(savedAt),
        calculator_acceptance: testStatus,
        frontend_runtime_authority: false,
        canonical_source_authority: "WORKSPACE_COMMAND_INGRESS_REGISTER",
      }
      const bytes = createStoredZip([
        { path: "index.html", data: sourceText },
        { path: "application.manifest.json", data: JSON.stringify(manifest, null, 2) + "\n" },
        { path: "README.txt", data: "HHS Pass 185 production-root application export. Open index.html in a modern browser.\n" },
      ])
      const zipBuffer = new ArrayBuffer(bytes.byteLength)
      new Uint8Array(zipBuffer).set(bytes)
      const url = URL.createObjectURL(new Blob([zipBuffer], { type: "application/zip" }))
      const link = Object.assign(document.createElement("a"), {
        href: url,
        download: "pass185-calculator.zip",
      })
      document.body.append(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
      setStatus(`ZIP_EXPORTED:${bytes.length}`)
      setError(null)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  const dirty = sourceText !== savedText

  return (
    <section data-testid="pass185-application-lifecycle" className="rounded-2xl border border-cyan-950 bg-neutral-900/50 p-3 md:p-4">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-cyan-200">Production application lifecycle</h2>
          <p className="mt-1 text-[10px] leading-5 text-neutral-500">Visible create → edit → witness/save → preview → test → ZIP export. Save uses inherited workspace authority; preview and ZIP packaging remain non-authoritative browser projections.</p>
        </div>
        <span data-testid="pass185-lifecycle-status" className="rounded-full border border-neutral-700 bg-black px-3 py-1 font-mono text-[9px] text-cyan-300">{status}</span>
      </header>

      {error ? <div data-testid="pass185-lifecycle-error" className="mt-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">{error}</div> : null}

      <div className="mt-4 grid gap-3 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.85fr)]">
        <div className="space-y-3">
          <div className="grid gap-2 sm:grid-cols-[1fr_180px_auto]">
            <input data-testid="pass185-project-name" value={projectName} onChange={(event) => setProjectName(event.target.value)} className="rounded-lg border border-neutral-700 bg-black p-2 text-sm" aria-label="Pass 185 project name" />
            <input data-testid="pass185-source-name" value={sourceName} onChange={(event) => setSourceName(event.target.value)} className="rounded-lg border border-neutral-700 bg-black p-2 text-sm" aria-label="Pass 185 source name" />
            <button data-testid="pass185-create-calculator" type="button" onClick={createCalculator} className="runtime-button min-h-10 px-3 text-sm">Create Calculator</button>
          </div>

          <textarea data-testid="pass185-html-editor" value={sourceText} onChange={(event) => setSourceText(event.target.value)} className="min-h-[420px] w-full resize-y rounded-xl border border-neutral-700 bg-black p-3 font-mono text-xs leading-5 text-cyan-50" aria-label="Pass 185 HTML editor" spellCheck={false} />

          <div className="grid gap-2 sm:grid-cols-4">
            <button data-testid="pass185-save-source" type="button" onClick={() => void saveSource().catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))} disabled={busy || !sourceText.trim()} className="runtime-button min-h-10 text-sm">{busy ? "Saving…" : "Save / Witness"}</button>
            <button data-testid="pass185-preview-source" type="button" onClick={openPreview} disabled={!sourceText.trim()} className="runtime-button min-h-10 text-sm">Preview</button>
            <button data-testid="pass185-run-test" type="button" onClick={runPreviewTest} disabled={!previewReady} className="runtime-button min-h-10 text-sm">Run Test</button>
            <button data-testid="pass185-export-zip" type="button" onClick={exportZip} disabled={!sourceText.trim()} className="runtime-button min-h-10 text-sm">Export ZIP</button>
          </div>

          <div className="grid gap-2 text-[10px] sm:grid-cols-4">
            <Status label="project" value={projectId ?? "not created"} ok={Boolean(projectId)} />
            <Status label="source" value={dirty ? "unsaved changes" : savedAt ? "saved" : "not saved"} ok={!dirty && Boolean(savedAt)} />
            <Status label="preview" value={previewReady ? "ready" : "not ready"} ok={previewReady} />
            <Status label="test" value={testStatus} ok={testStatus === "CALCULATOR_7_PLUS_8_EQUALS_15"} />
          </div>
          {lastReceipt ? <div className="truncate rounded-lg border border-neutral-800 bg-black p-2 font-mono text-[9px] text-cyan-700" title={lastReceipt}>receipt {lastReceipt}</div> : null}
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between gap-2">
            <h3 className="text-xs font-semibold text-cyan-200">Sandboxed browser preview</h3>
            <span className="text-[9px] text-neutral-500">same source · non-authoritative</span>
          </div>
          {previewHtml ? (
            <iframe
              key={`${previewRevision}:${previewHtml.length}`}
              ref={iframeRef}
              data-testid="pass185-preview-frame"
              title="Pass 185 application preview"
              sandbox="allow-scripts allow-same-origin"
              srcDoc={previewHtml}
              onLoad={() => { setPreviewReady(true); setStatus("PREVIEW_READY") }}
              className="h-[620px] w-full rounded-xl border border-neutral-700 bg-white"
            />
          ) : (
            <div className="grid h-[620px] place-items-center rounded-xl border border-dashed border-neutral-700 bg-black/50 p-6 text-center text-xs text-neutral-500">Create or edit HTML, then choose Preview.</div>
          )}
        </div>
      </div>
    </section>
  )
}

const Status: React.FC<{ label: string; value: string; ok: boolean }> = ({ label, value, ok }) => (
  <div className="rounded-lg border border-neutral-800 bg-black/50 p-2">
    <div className="text-neutral-600">{label}</div>
    <div className={`mt-1 truncate font-mono ${ok ? "text-emerald-300" : "text-neutral-500"}`} title={value}>{value}</div>
  </div>
)
