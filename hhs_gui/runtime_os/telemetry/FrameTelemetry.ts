export const FRAME_SAMPLE_LIMIT = 180
export const FRAME_PUBLISH_INTERVAL_MS = 500

export interface FrameTelemetrySnapshot {
  samples: readonly number[]
  currentFrameMs: number
  averageFrameMs: number
  p50FrameMs: number
  p95FrameMs: number
  p99FrameMs: number
  effectiveFps: number
  estimatedRefreshHz: number
  droppedFrames: number
  jankRate: number
  longFrameCount: number
  frameCount: number
  sampleWindowMs: number
  visible: boolean
  updatedAt: number
}

const EMPTY_SNAPSHOT: FrameTelemetrySnapshot = Object.freeze({
  samples: Object.freeze([]) as readonly number[],
  currentFrameMs: 0,
  averageFrameMs: 0,
  p50FrameMs: 0,
  p95FrameMs: 0,
  p99FrameMs: 0,
  effectiveFps: 0,
  estimatedRefreshHz: 0,
  droppedFrames: 0,
  jankRate: 0,
  longFrameCount: 0,
  frameCount: 0,
  sampleWindowMs: 0,
  visible: true,
  updatedAt: 0,
})

function percentile(sorted: readonly number[], p: number): number {
  if (sorted.length === 0) return 0
  const index = Math.min(sorted.length - 1, Math.max(0, Math.ceil(sorted.length * p) - 1))
  return sorted[index]
}

export function summarizeFrameSamples(
  values: readonly number[],
  frameCount = values.length,
  visible = true,
  updatedAt = 0,
): FrameTelemetrySnapshot {
  const samples = values
    .filter((value) => Number.isFinite(value) && value > 0)
    .slice(-FRAME_SAMPLE_LIMIT)

  if (samples.length === 0) return { ...EMPTY_SNAPSHOT, visible, frameCount, updatedAt }

  const sorted = [...samples].sort((a, b) => a - b)
  const total = samples.reduce((sum, value) => sum + value, 0)
  const averageFrameMs = total / samples.length
  const p50FrameMs = percentile(sorted, 0.50)
  const p95FrameMs = percentile(sorted, 0.95)
  const p99FrameMs = percentile(sorted, 0.99)
  const baselineMs = Math.max(1, p50FrameMs)
  const jankThresholdMs = Math.max(baselineMs * 1.5, baselineMs + 4)

  let droppedFrames = 0
  let jankCount = 0
  let longFrameCount = 0
  for (const frameMs of samples) {
    droppedFrames += Math.max(0, Math.round(frameMs / baselineMs) - 1)
    if (frameMs > jankThresholdMs) jankCount += 1
    if (frameMs >= 50) longFrameCount += 1
  }

  return {
    samples: Object.freeze([...samples]),
    currentFrameMs: samples[samples.length - 1],
    averageFrameMs,
    p50FrameMs,
    p95FrameMs,
    p99FrameMs,
    effectiveFps: averageFrameMs > 0 ? 1000 / averageFrameMs : 0,
    estimatedRefreshHz: p50FrameMs > 0 ? 1000 / p50FrameMs : 0,
    droppedFrames,
    jankRate: jankCount / samples.length,
    longFrameCount,
    frameCount,
    sampleWindowMs: total,
    visible,
    updatedAt,
  }
}

export class FrameTelemetryMonitor {
  private readonly listeners = new Set<() => void>()
  private consumers = 0
  private rafId: number | null = null
  private lastFrameAt = 0
  private lastPublishedAt = 0
  private frameCount = 0
  private samples: number[] = []
  private snapshot: FrameTelemetrySnapshot = EMPTY_SNAPSHOT

  public readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  public readonly getSnapshot = (): FrameTelemetrySnapshot => this.snapshot
  public readonly getServerSnapshot = (): FrameTelemetrySnapshot => EMPTY_SNAPSHOT

  public acquire(): () => void {
    this.consumers += 1
    if (this.consumers === 1) this.start()
    return () => {
      this.consumers = Math.max(0, this.consumers - 1)
      if (this.consumers === 0) this.stop()
    }
  }

  private start(): void {
    if (typeof window === "undefined" || typeof window.requestAnimationFrame !== "function") return
    if (this.rafId !== null) return
    this.lastFrameAt = 0
    this.lastPublishedAt = performance.now()
    this.rafId = window.requestAnimationFrame(this.tick)
  }

  private stop(): void {
    if (typeof window !== "undefined" && this.rafId !== null) window.cancelAnimationFrame(this.rafId)
    this.rafId = null
    this.lastFrameAt = 0
  }

  private readonly tick = (timestamp: number): void => {
    const visible = typeof document === "undefined" || document.visibilityState !== "hidden"

    if (!visible) {
      this.lastFrameAt = 0
      if (timestamp - this.lastPublishedAt >= FRAME_PUBLISH_INTERVAL_MS) this.publish(timestamp, false)
    } else {
      if (this.lastFrameAt > 0) {
        const delta = timestamp - this.lastFrameAt
        if (Number.isFinite(delta) && delta > 0 && delta < 1000) {
          this.samples = [...this.samples.slice(-(FRAME_SAMPLE_LIMIT - 1)), delta]
          this.frameCount += 1
        }
      }
      this.lastFrameAt = timestamp
      if (timestamp - this.lastPublishedAt >= FRAME_PUBLISH_INTERVAL_MS) this.publish(timestamp, true)
    }

    this.rafId = window.requestAnimationFrame(this.tick)
  }

  private publish(timestamp: number, visible: boolean): void {
    this.lastPublishedAt = timestamp
    this.snapshot = summarizeFrameSamples(this.samples, this.frameCount, visible, Date.now())
    for (const listener of this.listeners) listener()
  }
}

export const frameTelemetryMonitor = new FrameTelemetryMonitor()
