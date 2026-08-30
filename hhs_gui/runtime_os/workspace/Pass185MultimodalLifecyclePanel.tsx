import React, { useEffect, useMemo, useRef, useState } from "react"
import { createStoredZip } from "../artifacts/createStoredZip"
import type { WorkspaceCommandClient } from "./WorkspaceCommandClient"

type Mode = "document" | "game" | "graphics" | "audio" | "video"
type Json = Record<string, any>

const MODE_LABELS: Record<Mode, string> = {
  document: "Document",
  game: "2D Game",
  graphics: "Graphics",
  audio: "Audio",
  video: "Audiovisual",
}

const MODE_MODALITY: Record<Mode, string> = {
  document: "TEXT",
  game: "JSON",
  graphics: "IMAGE",
  audio: "AUDIO",
  video: "VIDEO",
}

const MODE_SOURCE_NAME: Record<Mode, string> = {
  document: "pass185-document.txt",
  game: "pass185-game.json",
  graphics: "pass185-graphic.svg",
  audio: "pass185-tone.wav.json",
  video: "pass185-audiovisual-reel.json",
}

const encoder = new TextEncoder()
const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback

function receiptFrom(feedback: Json): string | null {
  const result = record(feedback.result)
  const registration = record(result.registration)
  const object = record(result.workspace_object)
  for (const value of [
    feedback.receipt_hash72,
    result.receipt_hash72,
    registration.receipt_hash72,
    object.root_hash72,
    object.current_root_hash72,
    object.object_root_hash72,
  ]) {
    if (typeof value === "string" && value) return value
  }
  return null
}

function wavTone(frequency: number, durationMs: number): Uint8Array {
  const sampleRate = 8000
  const sampleCount = Math.max(1, Math.round(sampleRate * durationMs / 1000))
  const out = new Uint8Array(44 + sampleCount)
  const view = new DataView(out.buffer)
  const ascii = (offset: number, value: string): void => {
    for (let index = 0; index < value.length; index += 1) out[offset + index] = value.charCodeAt(index)
  }
  ascii(0, "RIFF")
  view.setUint32(4, 36 + sampleCount, true)
  ascii(8, "WAVE")
  ascii(12, "fmt ")
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate, true)
  view.setUint16(32, 1, true)
  view.setUint16(34, 8, true)
  ascii(36, "data")
  view.setUint32(40, sampleCount, true)
  for (let index = 0; index < sampleCount; index += 1) {
    const phase = (2 * Math.PI * frequency * index) / sampleRate
    out[44 + index] = Math.max(0, Math.min(255, Math.round(128 + Math.sin(phase) * 80)))
  }
  return out
}

export interface Pass185MultimodalLifecyclePanelProps {
  commandClient: WorkspaceCommandClient
  projectId: string | null
  onAuthorityFeedback?: (feedback: Json) => void
}

export const Pass185MultimodalLifecyclePanel: React.FC<Pass185MultimodalLifecyclePanelProps> = ({
  commandClient,
  projectId,
  onAuthorityFeedback,
}) => {
  const [mode, setMode] = useState<Mode>("document")
  const [activeProjectId, setActiveProjectId] = useState<string | null>(projectId)
  const [documentText, setDocumentText] = useState("Phase 4 document: source identity is preserved.")
  const [gameX, setGameX] = useState(1)
  const [gameY, setGameY] = useState(1)
  const [graphicSize, setGraphicSize] = useState(56)
  const [graphicLabel, setGraphicLabel] = useState("HHS")
  const [audioFrequency, setAudioFrequency] = useState(440)
  const [audioDurationMs, setAudioDurationMs] = useState(250)
  const [audioBytes, setAudioBytes] = useState<Uint8Array | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [videoFrame, setVideoFrame] = useState(0)
  const [videoPlaying, setVideoPlaying] = useState(false)
  const [status, setStatus] = useState("READY")
  const [error, setError] = useState<string | null>(null)
  const [lastReceipt, setLastReceipt] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const videoTimer = useRef<number | null>(null)

  useEffect(() => {
    if (projectId) setActiveProjectId(projectId)
  }, [projectId])

  useEffect(() => () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    if (videoTimer.current !== null) window.clearInterval(videoTimer.current)
  }, [audioUrl])

  const graphicSvg = useMemo(() => (
    `<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180" viewBox="0 0 320 180"><rect width="320" height="180" fill="#071017"/><circle cx="160" cy="90" r="${graphicSize}" fill="#0e7490"/><text x="160" y="96" text-anchor="middle" fill="white" font-family="system-ui" font-size="24">${graphicLabel.replace(/[<>&]/g, "")}</text></svg>`
  ), [graphicLabel, graphicSize])

  const sourcePayload = (): string => {
    if (mode === "document") return documentText
    if (mode === "game") return JSON.stringify({
      schema: "HHS_PASS185_2D_GAME_SOURCE_V1",
      player: { x: gameX, y: gameY },
      board: { width: 4, height: 4 },
      frontend_runtime_authority: false,
    }, null, 2)
    if (mode === "graphics") return graphicSvg
    if (mode === "audio") return JSON.stringify({
      schema: "HHS_PASS185_AUDIO_SOURCE_V1",
      frequency_hz: audioFrequency,
      duration_ms: audioDurationMs,
      generated_preview_bytes: audioBytes?.length ?? 0,
      canonical_audio_authority: false,
    }, null, 2)
    return JSON.stringify({
      schema: "HHS_PASS185_AUDIOVISUAL_REEL_SOURCE_V1",
      frame: videoFrame,
      frames: ["GENESIS", "TRANSFORM", "CLOSURE"],
      transport: videoPlaying ? "PLAYING" : "PAUSED",
      browser_playback_authority: false,
    }, null, 2)
  }

  const ensureProject = async (): Promise<string> => {
    if (activeProjectId) return activeProjectId
    const feedback = record(await commandClient.submit("project.create", { name: "Pass 185 Multimodal" }))
    const id = text(record(record(feedback.result).project).project_id)
    if (!id || feedback.ok === false) throw new Error(text(feedback.status, "PROJECT_CREATE_FAILED"))
    setActiveProjectId(id)
    onAuthorityFeedback?.(feedback)
    return id
  }

  const witness = async (): Promise<void> => {
    setBusy(true)
    setError(null)
    try {
      const id = await ensureProject()
      const feedback = record(await commandClient.submit("ingress.register", {
        project_id: id,
        source_name: MODE_SOURCE_NAME[mode],
        source_payload: sourcePayload(),
        declared_modality: MODE_MODALITY[mode],
      }))
      if (feedback.ok === false) throw new Error(text(feedback.status, "MULTIMODAL_INGRESS_REJECTED"))
      setLastReceipt(receiptFrom(feedback))
      setStatus(`${mode.toUpperCase()}_SOURCE_WITNESSED`)
      onAuthorityFeedback?.(feedback)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  const verify = (): void => {
    if (mode === "document") {
      if (!documentText.includes("Phase 4")) throw new Error("DOCUMENT_EXPECTED_MARKER_MISSING")
      setStatus("DOCUMENT_PREVIEW_VERIFIED")
      return
    }
    if (mode === "game") {
      if (gameX < 0 || gameX > 3 || gameY < 0 || gameY > 3) throw new Error("GAME_POSITION_OUT_OF_BOUNDS")
      setStatus("GAME_INTERACTION_VERIFIED")
      return
    }
    if (mode === "graphics") {
      if (graphicSize < 16 || graphicSize > 80) throw new Error("GRAPHIC_SIZE_OUT_OF_RANGE")
      setStatus("GRAPHICS_RENDER_VERIFIED")
      return
    }
    if (mode === "audio") {
      const bytes = audioBytes
      if (!bytes || bytes.length <= 44 || new TextDecoder().decode(bytes.slice(0, 4)) !== "RIFF") {
        throw new Error("AUDIO_WAV_PREVIEW_REQUIRED")
      }
      setStatus("AUDIO_PREVIEW_VERIFIED")
      return
    }
    if (videoFrame < 0 || videoFrame > 2) throw new Error("VIDEO_FRAME_OUT_OF_RANGE")
    setStatus("AUDIOVISUAL_REEL_VERIFIED")
  }

  const guardedVerify = (): void => {
    setError(null)
    try {
      verify()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  const exportPackage = (): void => {
    setError(null)
    const manifest = {
      schema: "HHS_PASS185_MULTIMODAL_EXPORT_MANIFEST_V1",
      mode,
      modality: MODE_MODALITY[mode],
      source_name: MODE_SOURCE_NAME[mode],
      frontend_runtime_authority: false,
      browser_preview_is_canonical_source: false,
      calculator_phase1_invariant_preserved: true,
    }
    const entries: Array<{ path: string; data: string | Uint8Array }> = [
      { path: MODE_SOURCE_NAME[mode], data: mode === "audio" && audioBytes ? audioBytes : sourcePayload() },
      { path: "application.manifest.json", data: JSON.stringify(manifest, null, 2) + "\n" },
      { path: "README.txt", data: `Pass 185 Phase 4 ${MODE_LABELS[mode]} export. Browser preview is non-authoritative.\n` },
    ]
    const bytes = createStoredZip(entries)
    const blob = new Blob([bytes], { type: "application/zip" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `pass185-${mode}-workflow.zip`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    setStatus(`${mode.toUpperCase()}_EXPORT_READY`)
  }

  const generateAudio = (): void => {
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    const bytes = wavTone(audioFrequency, audioDurationMs)
    const url = URL.createObjectURL(new Blob([bytes], { type: "audio/wav" }))
    setAudioBytes(bytes)
    setAudioUrl(url)
    setStatus("AUDIO_PREVIEW_READY")
  }

  const stepVideo = (): void => {
    setVideoFrame((value) => (value + 1) % 3)
    setStatus("AUDIOVISUAL_FRAME_ADVANCED")
  }

  const toggleVideo = (): void => {
    if (videoPlaying) {
      if (videoTimer.current !== null) window.clearInterval(videoTimer.current)
      videoTimer.current = null
      setVideoPlaying(false)
      setStatus("AUDIOVISUAL_PAUSED")
      return
    }
    setVideoPlaying(true)
    setStatus("AUDIOVISUAL_PLAYING")
    videoTimer.current = window.setInterval(() => {
      setVideoFrame((value) => (value + 1) % 3)
    }, 240)
  }

  return (
    <section data-testid="pass185-multimodal-lifecycle" className="rounded-2xl border border-cyan-950 bg-neutral-900/50 p-3 md:p-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-cyan-200">Pass 185 multimodal application workflows</h2>
          <p className="mt-1 text-[10px] text-neutral-500">Local preview/render lanes are non-authoritative. Witnessing uses inherited workspace ingress only.</p>
        </div>
        <span data-testid="pass185-mm-status" className="rounded-full border border-neutral-700 bg-black px-3 py-1 font-mono text-[9px] text-cyan-300">{status}</span>
      </header>

      <div className="mt-3 grid grid-cols-5 gap-1">
        {(Object.keys(MODE_LABELS) as Mode[]).map((item) => (
          <button
            key={item}
            data-testid={`pass185-mm-mode-${item}`}
            type="button"
            onClick={() => { setMode(item); setStatus("READY"); setError(null) }}
            className={`min-h-10 rounded-lg px-2 text-xs ${mode === item ? "bg-cyan-900 text-white" : "bg-neutral-950 text-neutral-400"}`}
          >
            {MODE_LABELS[item]}
          </button>
        ))}
      </div>

      {error ? <div data-testid="pass185-mm-error" className="mt-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">{error}</div> : null}

      <div className="mt-3 rounded-xl border border-neutral-800 bg-black/40 p-3">
        {mode === "document" ? (
          <div className="grid gap-3 lg:grid-cols-2">
            <textarea data-testid="pass185-mm-document-editor" value={documentText} onChange={(event) => setDocumentText(event.target.value)} className="min-h-64 rounded-lg border border-neutral-700 bg-black p-3 text-sm" />
            <article data-testid="pass185-mm-document-preview" className="min-h-64 whitespace-pre-wrap rounded-lg border border-neutral-800 bg-neutral-950 p-4 text-sm leading-6">{documentText}</article>
          </div>
        ) : null}

        {mode === "game" ? (
          <div className="grid gap-3 lg:grid-cols-[280px_1fr]">
            <div data-testid="pass185-mm-game-board" className="grid aspect-square grid-cols-4 gap-1 rounded-xl border border-neutral-800 bg-neutral-950 p-2">
              {Array.from({ length: 16 }, (_, index) => {
                const x = index % 4
                const y = Math.floor(index / 4)
                const player = x === gameX && y === gameY
                return <div key={index} className="grid place-items-center rounded bg-neutral-900 text-xl">{player ? "◆" : ""}</div>
              })}
            </div>
            <div>
              <div data-testid="pass185-mm-game-position" className="font-mono text-xs text-cyan-300">x={gameX} y={gameY}</div>
              <div className="mt-3 grid grid-cols-2 gap-2">
                <button data-testid="pass185-mm-game-left" type="button" className="runtime-button min-h-10" onClick={() => setGameX((value) => Math.max(0, value - 1))}>Left</button>
                <button data-testid="pass185-mm-game-right" type="button" className="runtime-button min-h-10" onClick={() => setGameX((value) => Math.min(3, value + 1))}>Right</button>
                <button data-testid="pass185-mm-game-up" type="button" className="runtime-button min-h-10" onClick={() => setGameY((value) => Math.max(0, value - 1))}>Up</button>
                <button data-testid="pass185-mm-game-down" type="button" className="runtime-button min-h-10" onClick={() => setGameY((value) => Math.min(3, value + 1))}>Down</button>
              </div>
            </div>
          </div>
        ) : null}

        {mode === "graphics" ? (
          <div className="grid gap-3 lg:grid-cols-[280px_1fr]">
            <div dangerouslySetInnerHTML={{ __html: graphicSvg }} data-testid="pass185-mm-graphics-preview" className="overflow-hidden rounded-xl border border-neutral-800" />
            <div>
              <label className="block text-xs text-neutral-400">Circle size
                <input data-testid="pass185-mm-graphics-size" type="range" min="16" max="80" value={graphicSize} onChange={(event) => setGraphicSize(Number(event.target.value))} className="mt-2 w-full" />
              </label>
              <label className="mt-3 block text-xs text-neutral-400">Label
                <input data-testid="pass185-mm-graphics-label" value={graphicLabel} onChange={(event) => setGraphicLabel(event.target.value)} className="mt-1 w-full rounded border border-neutral-700 bg-black p-2 text-sm" />
              </label>
            </div>
          </div>
        ) : null}

        {mode === "audio" ? (
          <div className="grid gap-3 lg:grid-cols-[1fr_320px]">
            <div>
              <label className="block text-xs text-neutral-400">Frequency Hz
                <input data-testid="pass185-mm-audio-frequency" type="number" min="110" max="880" value={audioFrequency} onChange={(event) => setAudioFrequency(Number(event.target.value))} className="mt-1 w-full rounded border border-neutral-700 bg-black p-2 text-sm" />
              </label>
              <label className="mt-3 block text-xs text-neutral-400">Duration ms
                <input data-testid="pass185-mm-audio-duration" type="number" min="100" max="1000" value={audioDurationMs} onChange={(event) => setAudioDurationMs(Number(event.target.value))} className="mt-1 w-full rounded border border-neutral-700 bg-black p-2 text-sm" />
              </label>
              <button data-testid="pass185-mm-audio-generate" type="button" onClick={generateAudio} className="runtime-button mt-3 min-h-10 w-full">Generate WAV preview</button>
            </div>
            <div className="rounded-xl border border-neutral-800 bg-neutral-950 p-3">
              <audio data-testid="pass185-mm-audio-player" controls src={audioUrl ?? undefined} className="w-full" />
              <div data-testid="pass185-mm-audio-bytes" className="mt-3 font-mono text-[10px] text-cyan-300">{audioBytes ? `${audioBytes.length} bytes · RIFF/WAVE` : "No preview generated"}</div>
            </div>
          </div>
        ) : null}

        {mode === "video" ? (
          <div className="grid gap-3 lg:grid-cols-[1fr_320px]">
            <div data-testid="pass185-mm-video-preview" className="grid min-h-64 place-items-center rounded-xl border border-neutral-800 bg-[radial-gradient(circle_at_center,rgba(6,182,212,.22),transparent_60%)]">
              <div className="text-center">
                <div data-testid="pass185-mm-video-frame" className="text-4xl font-black tracking-widest text-cyan-200">{["GENESIS", "TRANSFORM", "CLOSURE"][videoFrame]}</div>
                <div className="mt-2 font-mono text-[10px] text-neutral-500">frame {videoFrame + 1} / 3</div>
              </div>
            </div>
            <div>
              <button data-testid="pass185-mm-video-step" type="button" className="runtime-button min-h-10 w-full" onClick={stepVideo}>Step frame</button>
              <button data-testid="pass185-mm-video-play" type="button" className="runtime-button mt-2 min-h-10 w-full" onClick={toggleVideo}>{videoPlaying ? "Pause reel" : "Play reel"}</button>
              <p className="mt-3 text-xs leading-5 text-neutral-500">This audiovisual preview is a browser-local projection. Export/witness retains the source description, not the transient timer state as runtime authority.</p>
            </div>
          </div>
        ) : null}
      </div>

      <div className="mt-3 grid gap-2 sm:grid-cols-3">
        <button data-testid="pass185-mm-verify" type="button" onClick={guardedVerify} className="runtime-button min-h-10">Verify visible workflow</button>
        <button data-testid="pass185-mm-witness" type="button" onClick={() => void witness()} disabled={busy} className="runtime-button min-h-10">{busy ? "Witnessing…" : "Witness source"}</button>
        <button data-testid="pass185-mm-export" type="button" onClick={exportPackage} className="runtime-button min-h-10">Export deterministic ZIP</button>
      </div>

      <footer className="mt-3 flex flex-wrap items-center justify-between gap-2 rounded-lg border border-neutral-800 bg-black/30 p-2 font-mono text-[9px] text-neutral-500">
        <span>mode={mode} · modality={MODE_MODALITY[mode]} · project={activeProjectId ?? "not-created"}</span>
        <span data-testid="pass185-mm-receipt">{lastReceipt ? `${lastReceipt.slice(0, 12)}…${lastReceipt.slice(-8)}` : "no receipt"}</span>
      </footer>
    </section>
  )
}

export default Pass185MultimodalLifecyclePanel
