/**
 * =========================================================
 * RuntimeOS
 * =========================================================
 * Canonical frontend orchestration layer. Runtime truth remains backend-owned.
 */

import { RuntimeSocketManager, RuntimeSocketEvent } from "./RuntimeSocketManager"
import { RuntimeStateStore } from "../state/RuntimeStateStore"
import { runtimeApplicationRegistry } from "./RuntimeApplicationRegistry"
import { RuntimeWindowManager } from "./RuntimeWindowManager"
import { RuntimeWorkspace } from "./RuntimeWorkspace"
import { RuntimeSession } from "./RuntimeSession"

export interface RuntimeOSConfig {
    runtimeEndpoint: string
    replayEndpoint: string
    graphEndpoint: string
    transportEndpoint: string
    diagnosticsEnabled?: boolean
    mobileMode?: boolean
}

export class RuntimeOS {
    public readonly socketManager: RuntimeSocketManager
    public readonly store: RuntimeStateStore
    public readonly registry = runtimeApplicationRegistry
    public readonly windowManager: RuntimeWindowManager
    public readonly workspace: RuntimeWorkspace
    public readonly session: RuntimeSession

    private initialized = false
    private destroyed = false
    private readonly subscriptions: (() => void)[] = []
    public readonly config: RuntimeOSConfig
    private readonly bootTimeMs = Date.now()

    constructor(config: RuntimeOSConfig) {
        this.config = config
        this.socketManager = new RuntimeSocketManager({
            runtimeEndpoint: config.runtimeEndpoint,
            replayEndpoint: config.replayEndpoint,
            graphEndpoint: config.graphEndpoint,
            transportEndpoint: config.transportEndpoint,
        })
        this.store = new RuntimeStateStore()
        this.windowManager = new RuntimeWindowManager()
        this.workspace = new RuntimeWorkspace()
        this.session = new RuntimeSession()
    }

    public async initialize(): Promise<void> {
        if (this.initialized) return

        console.log("[RuntimeOS] initialize")

        await this.socketManager.initialize()
        await this.session.initialize()
        await this.workspace.initialize()

        this.subscriptions.push(
            this.socketManager.subscribe("runtime", (event: RuntimeSocketEvent) => {
                this.store.ingestEvent(event)
            }),
        )
        this.subscriptions.push(
            this.socketManager.subscribe("replay", (event: RuntimeSocketEvent) => {
                this.store.ingestEvent(event)
            }),
        )
        this.subscriptions.push(
            this.socketManager.subscribe("graph", (event: RuntimeSocketEvent) => {
                this.store.ingestEvent(event)
            }),
        )
        this.subscriptions.push(
            this.socketManager.subscribe("transport", (event: RuntimeSocketEvent) => {
                this.store.ingestEvent(event)
            }),
        )

        this.bootstrapWindows()
        this.initialized = true
        console.log("[RuntimeOS] initialized")
    }

    private bootstrapWindows(): void {
        this.windowManager.openWindow({
            id: "runtime_console",
            title: "Runtime Console",
            applicationId: "runtime_console",
            width: 520,
            height: 420,
            x: 80,
            y: 80,
        })
        this.windowManager.openWindow({
            id: "calculator",
            title: "Calculator",
            applicationId: "calculator",
            width: 900,
            height: 600,
            x: 220,
            y: 120,
        })
        this.windowManager.openWindow({
            id: "breadboard",
            title: "Breadboard",
            applicationId: "breadboard",
            width: 980,
            height: 640,
            x: 160,
            y: 160,
        })
    }

    public openApplication(applicationId: string): void {
        const definition = this.registry.get(applicationId)
        if (!definition) {
            console.error("[RuntimeOS] missing application", applicationId)
            return
        }
        const preset = definition.windowPreset
        this.windowManager.openWindow({
            id: `${applicationId}_${Date.now()}`,
            title: definition.title,
            applicationId,
            width: preset.width,
            height: preset.height,
            x: 140,
            y: 140,
        })
    }

    public getMetrics() {
        const registryMetrics = this.registry.metrics()
        const storeMetrics = this.store.getMetrics()
        const socketMetrics = this.socketManager.getMetrics() as {
            runtimeConnected: boolean
            replayConnected: boolean
            graphConnected: boolean
            transportConnected: boolean
            totalEvents: number
        }
        const windowMetrics = this.windowManager.getMetrics()

        return {
            initialized: this.initialized,
            destroyed: this.destroyed,
            diagnosticsEnabled: Boolean(this.config.diagnosticsEnabled),
            mobileMode: Boolean(this.config.mobileMode),
            uptimeMs: Date.now() - this.bootTimeMs,
            connected: socketMetrics.runtimeConnected,
            replayReady: socketMetrics.replayConnected,
            graphReady: socketMetrics.graphConnected,
            transportReady: socketMetrics.transportConnected,
            totalEvents: socketMetrics.totalEvents,
            workspaceWindows: windowMetrics.windows,
            applicationsMounted: registryMetrics.registeredApplications,
            registry: registryMetrics,
            store: storeMetrics,
            sockets: socketMetrics,
            windows: windowMetrics,
            workspace: this.workspace.getMetrics(),
            session: this.session.getMetrics(),
        }
    }

    public shutdown(): void {
        this.destroy()
    }

    public destroy(): void {
        if (this.destroyed) return
        console.log("[RuntimeOS] destroy")

        for (const unsubscribe of this.subscriptions) {
            try {
                unsubscribe()
            } catch (error) {
                console.error("[RuntimeOS] unsubscribe failure", error)
            }
        }
        this.subscriptions.length = 0

        this.socketManager.shutdown()
        this.session.terminate()
        this.windowManager.reset()
        this.destroyed = true
        console.log("[RuntimeOS] destroyed")
    }
}
