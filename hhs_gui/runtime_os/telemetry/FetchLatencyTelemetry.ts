export type LatencyTier = 0 | 1 | 2 | 3

export interface EndpointLatencySnapshot {
  url: string
  tier: LatencyTier
  sampleCount: number
  p50Ms: number
  p95Ms: number
  meanMs: number
  errorCount: number
  lastStatus: number
  lastFetchedAt: number
}

interface MutableEndpointStats {
  url: string
  tier: LatencyTier
  samples: number[]
  errorCount: number
  lastStatus: number
  lastFetchedAt: number
}

interface FetchInstrumentationState {
  originalFetch: typeof window.fetch
  activeMonitor: FetchLatencyTelemetry
  inflight: Map<string, Promise<Response>>
}

const FETCH_STATE_KEY = "__hhsFrontendFetchLatencyState_v1__"
const SAMPLE_LIMIT = 60

export const TIER_THRESHOLDS = Object.freeze({
  T01_IN: 500,
  T01_OUT: 800,
  T12_IN: 1500,
  T12_OUT: 2500,
  T23_IN: 4000,
  T23_OUT: 6000,
})

function percentile(sorted: readonly number[], p: number): number {
  if (sorted.length === 0) return 0
  const index = Math.min(sorted.length - 1, Math.max(0, Math.ceil(sorted.length * p) - 1))
  return sorted[index]
}

function nextTier(current: LatencyTier, p95: number): LatencyTier {
  switch (current) {
    case 0: return p95 > TIER_THRESHOLDS.T01_OUT ? 1 : 0
    case 1:
      if (p95 < TIER_THRESHOLDS.T01_IN) return 0
      return p95 > TIER_THRESHOLDS.T12_OUT ? 2 : 1
    case 2:
      if (p95 < TIER_THRESHOLDS.T12_IN) return 1
      return p95 > TIER_THRESHOLDS.T23_OUT ? 3 : 2
    case 3: return p95 < TIER_THRESHOLDS.T23_IN ? 2 : 3
  }
}

function currentState(): FetchInstrumentationState | undefined {
  if (typeof window === "undefined") return undefined
  return (window as unknown as Record<string, unknown>)[FETCH_STATE_KEY] as FetchInstrumentationState | undefined
}

function requestUrl(input: RequestInfo | URL): string {
  if (typeof input === "string") return input
  if (typeof URL !== "undefined" && input instanceof URL) return input.href
  return (input as Request).url
}

function requestMethod(input: RequestInfo | URL, init?: RequestInit): string {
  if (init?.method) return init.method.toUpperCase()
  if (typeof Request !== "undefined" && input instanceof Request) return input.method.toUpperCase()
  return "GET"
}

function coalesceIdentity(input: RequestInfo | URL, init: RequestInit | undefined, url: string): string {
  const headers = new Headers(typeof Request !== "undefined" && input instanceof Request ? input.headers : undefined)
  if (init?.headers) new Headers(init.headers).forEach((value, key) => headers.set(key, value))

  const identityHeaders = ["accept", "authorization", "content-type", "range"]
    .map((name) => `${name}:${headers.get(name) ?? ""}`)
    .join("|")
  const credentials = init?.credentials
    ?? (typeof Request !== "undefined" && input instanceof Request ? input.credentials : "same-origin")

  return `${url}|credentials:${credentials}|${identityHeaders}`
}

export class FetchLatencyTelemetry {
  private readonly listeners = new Set<() => void>()
  private readonly stats = new Map<string, MutableEndpointStats>()

  public readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  public instrument(): void {
    if (typeof window === "undefined" || typeof window.fetch !== "function") return

    const existing = currentState()
    if (existing) {
      existing.activeMonitor = this
      return
    }

    const state: FetchInstrumentationState = {
      originalFetch: window.fetch.bind(window),
      activeMonitor: this,
      inflight: new Map<string, Promise<Response>>(),
    }
    ;(window as unknown as Record<string, unknown>)[FETCH_STATE_KEY] = state

    window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
      const activeState = currentState() ?? state
      const url = requestUrl(input)
      const method = requestMethod(input, init)
      const isGet = method === "GET"
      const key = isGet ? coalesceIdentity(input, init, url) : ""

      if (isGet) {
        const pending = activeState.inflight.get(key)
        if (pending) return pending.then((response) => response.clone())
      }

      const startedAt = performance.now()
      const request = activeState.originalFetch(input, init)
        .then((response) => {
          activeState.activeMonitor.record(url, performance.now() - startedAt, response.status)
          return response
        })
        .catch((error: unknown) => {
          activeState.activeMonitor.record(url, performance.now() - startedAt, 0)
          throw error
        })
        .finally(() => {
          if (isGet) activeState.inflight.delete(key)
        })

      if (isGet) {
        activeState.inflight.set(key, request)
        return request.then((response) => response.clone())
      }
      return request
    }
  }

  public getInFlightCount(): number {
    return currentState()?.inflight.size ?? 0
  }

  public getAll(): EndpointLatencySnapshot[] {
    return [...this.stats.values()]
      .map((stats) => this.snapshot(stats))
      .sort((a, b) => b.p95Ms - a.p95Ms)
  }

  public get(url: string): EndpointLatencySnapshot | undefined {
    const stats = this.stats.get(url)
    return stats ? this.snapshot(stats) : undefined
  }

  private record(url: string, elapsedMs: number, status: number): void {
    const stats = this.stats.get(url) ?? {
      url,
      tier: 1 as LatencyTier,
      samples: [],
      errorCount: 0,
      lastStatus: 0,
      lastFetchedAt: 0,
    }

    stats.samples = [...stats.samples.slice(-(SAMPLE_LIMIT - 1)), elapsedMs]
    stats.lastStatus = status
    stats.lastFetchedAt = Date.now()
    if (status === 0 || status >= 500) stats.errorCount += 1

    const sorted = [...stats.samples].sort((a, b) => a - b)
    stats.tier = nextTier(stats.tier, percentile(sorted, 0.95))
    this.stats.set(url, stats)
    for (const listener of this.listeners) listener()
  }

  private snapshot(stats: MutableEndpointStats): EndpointLatencySnapshot {
    const sorted = [...stats.samples].sort((a, b) => a - b)
    const total = stats.samples.reduce((sum, sample) => sum + sample, 0)
    return {
      url: stats.url,
      tier: stats.tier,
      sampleCount: stats.samples.length,
      p50Ms: percentile(sorted, 0.50),
      p95Ms: percentile(sorted, 0.95),
      meanMs: stats.samples.length > 0 ? total / stats.samples.length : 0,
      errorCount: stats.errorCount,
      lastStatus: stats.lastStatus,
      lastFetchedAt: stats.lastFetchedAt,
    }
  }
}

export const fetchLatencyTelemetry = new FetchLatencyTelemetry()
