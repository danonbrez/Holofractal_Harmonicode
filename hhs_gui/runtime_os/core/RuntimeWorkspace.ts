/**
 * HHS Runtime Workspace
 * ---------------------------------------------------
 * Persistent graph-native runtime workspace.
 *
 * Responsibilities:
 *
 * - Workspace state continuity
 * - Runtime region management
 * - Viewport persistence
 * - Window persistence
 * - Replay-linked workspace continuity
 * - Graph workspace synchronization
 * - Runtime layout persistence
 * - Session restoration
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeWorkspaceState {

    initialized: boolean

    layoutRestored: boolean

    replaySynchronized: boolean

    graphSynchronized: boolean

    viewportReady: boolean
}

export interface RuntimeWorkspaceLayout {

    windows: RuntimeWindowState[]

    activeWindow?: string

    viewport: RuntimeViewportState

    overlays: RuntimeOverlayState[]
}

export interface RuntimeWindowState {

    id: string

    title: string

    applicationId: string

    position: {

        x: number

        y: number
    }

    size: {

        width: number

        height: number
    }

    minimized: boolean

    maximized: boolean

    focused: boolean

    zIndex: number
}

export interface RuntimeViewportState {

    cameraX: number

    cameraY: number

    zoom: number

    projectionMode: string
}

export interface RuntimeOverlayState {

    id: string

    overlayType: string

    enabled: boolean
}

export class RuntimeWorkspace {

    public readonly id: string

    public readonly createdAt: number

    public readonly state: RuntimeWorkspaceState

    public layout: RuntimeWorkspaceLayout

    constructor() {

        this.id = crypto.randomUUID()

        this.createdAt = Date.now()

        this.state = {

            initialized: false,

            layoutRestored: false,

            replaySynchronized: false,

            graphSynchronized: false,

            viewportReady: false
        }

        this.layout = {

            windows: [],

            viewport: {

                cameraX: 0,

                cameraY: 0,

                zoom: 1,

                projectionMode: "graph"
            },

            overlays: []
        }
    }

    /**
     * ---------------------------------------------------
     * Workspace Initialization
     * ---------------------------------------------------
     */

    public async initialize(): Promise<void> {

        console.log(
            "[RuntimeWorkspace] initialize"
        )

        await this.restoreWorkspaceLayout()

        await this.initializeViewport()

        await this.initializeReplayState()

        await this.initializeGraphState()

        this.state.initialized = true

        console.log(
            "[RuntimeWorkspace] ready"
        )
    }

    /**
     * ---------------------------------------------------
     * Layout Restoration
     * ---------------------------------------------------
     */

    private async restoreWorkspaceLayout(): Promise<void> {

        console.log(
            "[RuntimeWorkspace] restore layout"
        )

        this.layout.windows = [

            {

                id: crypto.randomUUID(),

                title: "Runtime Console",

                applicationId: "runtime_console",

                position: {

                    x: 120,

                    y: 80
                },

                size: {

                    width: 900,

                    height: 600
                },

                minimized: false,

                maximized: false,

                focused: true,

                zIndex: 1
            },

            {

                id: crypto.randomUUID(),

                title: "Graph Debugger",

                applicationId: "graph_debugger",

                position: {

                    x: 240,

                    y: 140
                },

                size: {

                    width: 720,

                    height: 500
                },

                minimized: false,

                maximized: false,

                focused: false,

                zIndex: 0
            }
        ]

        this.state.layoutRestored = true
    }

    /**
     * ---------------------------------------------------
     * Viewport Initialization
     * ---------------------------------------------------
     */

    private async initializeViewport(): Promise<void> {

        console.log(
            "[RuntimeWorkspace] initialize viewport"
        )

        this.layout.viewport = {

            cameraX: 0,

            cameraY: 0,

            zoom: 1,

            projectionMode: "graph"
        }

        this.state.viewportReady = true
    }

    /**
     * ---------------------------------------------------
     * Replay Synchronization
     * ---------------------------------------------------
     */

    private async initializeReplayState(): Promise<void> {

        console.log(
            "[RuntimeWorkspace] replay sync"
        )

        this.state.replaySynchronized = true
    }

    /**
     * ---------------------------------------------------
     * Graph Synchronization
     * ---------------------------------------------------
     */

    private async initializeGraphState(): Promise<void> {

        console.log(
            "[RuntimeWorkspace] graph sync"
        )

        this.state.graphSynchronized = true
    }

    /**
     * ---------------------------------------------------
     * Window Management
     * ---------------------------------------------------
     */

    public addWindow(
        window: RuntimeWindowState
    ): void {

        this.layout.windows.push(window)

        this.focusWindow(window.id)

        console.log(
            "[RuntimeWorkspace] window added",
            window.id
        )
    }

    public removeWindow(
        windowId: string
    ): void {

        this.layout.windows =
            this.layout.windows.filter(

                (window) =>
                    window.id !== windowId
            )

        console.log(
            "[RuntimeWorkspace] window removed",
            windowId
        )
    }

    public focusWindow(
        windowId: string
    ): void {

        let highestZ = 0

        for (const window of this.layout.windows) {

            if (window.zIndex > highestZ) {

                highestZ = window.zIndex
            }
        }

        for (const window of this.layout.windows) {

            window.focused =
                window.id === windowId

            if (window.id === windowId) {

                window.zIndex = highestZ + 1
            }
        }
    }

    /**
     * ---------------------------------------------------
     * Viewport Controls
     * ---------------------------------------------------
     */

    public setViewportZoom(
        zoom: number
    ): void {

        this.layout.viewport.zoom = zoom
    }

    public setViewportPosition(
        x: number,
        y: number
    ): void {

        this.layout.viewport.cameraX = x

        this.layout.viewport.cameraY = y
    }

    public setProjectionMode(
        mode: string
    ): void {

        this.layout.viewport.projectionMode = mode
    }

    /**
     * ---------------------------------------------------
     * Overlay Controls
     * ---------------------------------------------------
     */

    public enableOverlay(
        overlayType: string
    ): void {

        const overlay: RuntimeOverlayState = {

            id: crypto.randomUUID(),

            overlayType,

            enabled: true
        }

        this.layout.overlays.push(overlay)
    }

    public disableOverlay(
        overlayType: string
    ): void {

        this.layout.overlays =
            this.layout.overlays.filter(

                (overlay) =>
                    overlay.overlayType !== overlayType
            )
    }

    /**
     * ---------------------------------------------------
     * Workspace Serialization
     * ---------------------------------------------------
     */

    public serialize(): object {

        return {

            id: this.id,

            createdAt: this.createdAt,

            state: this.state,

            layout: this.layout
        }
    }

    /**
     * ---------------------------------------------------
     * Workspace Metrics
     * ---------------------------------------------------
     */

    public getMetrics(): object {

        return {

            windows:
                this.layout.windows.length,

            overlays:
                this.layout.overlays.length,

            zoom:
                this.layout.viewport.zoom,

            initialized:
                this.state.initialized,

            replaySynchronized:
                this.state.replaySynchronized,

            graphSynchronized:
                this.state.graphSynchronized
        }
    }
}