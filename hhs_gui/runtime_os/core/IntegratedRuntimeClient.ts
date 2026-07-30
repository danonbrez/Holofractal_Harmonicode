import { RuntimeSocketManager, type RuntimeSocketEvent } from "./RuntimeSocketManager"
import { RuntimeStateStore } from "./RuntimeStateStore"

export interface IntegratedRuntimeClientConfig {
  runtimeEndpoint: string
  replayEndpoint: string
  graphEndpoint: string
  transportEndpoint: string
}

/**
 * Public-workspace runtime projection client.
 *
 * It deliberately excludes the legacy desktop window registry and application
 * loaders. Transport is connected only while the user is viewing the Runtime
 * surface, so ordinary editing and assistant work do not pay for four live
 * WebSocket channels or dormant visualization modules.
 */
export class IntegratedRuntimeClient {
  public readonly socketManager: RuntimeSocketManager
  public readonly store = new RuntimeStateStore()

  private initialized = false
  private subscriptions: Array<() => void> = []

  constructor(config: IntegratedRuntimeClientConfig) {
    this.socketManager = new RuntimeSocketManager(config)
  }

  public async initialize(): Promise<void> {
    if (this.initialized) return
    await this.socketManager.initialize()
    for (const channel of ["runtime", "replay", "graph", "transport"] as const) {
      this.subscriptions.push(
        this.socketManager.subscribe(channel, (event: RuntimeSocketEvent) => {
          this.store.ingestEvent(event)
        }),
      )
    }
    this.initialized = true
  }

  public shutdown(): void {
    for (const unsubscribe of this.subscriptions) unsubscribe()
    this.subscriptions = []
    this.socketManager.shutdown()
    this.initialized = false
  }

  public getMetrics(): Record<string, unknown> {
    return {
      initialized: this.initialized,
      sockets: this.socketManager.getMetrics(),
      store: this.store.getMetrics(),
    }
  }
}
