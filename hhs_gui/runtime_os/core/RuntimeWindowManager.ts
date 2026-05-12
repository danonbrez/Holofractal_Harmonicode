/**
 * HHS Runtime Window Manager
 * ---------------------------------------------------
 * Graph-native Runtime OS window orchestration layer.
 *
 * Responsibilities:
 *
 * - Runtime window lifecycle
 * - Workspace window topology
 * - Focus management
 * - Z-index ordering
 * - Window persistence
 * - Replay-linked window continuity
 * - Graph-native window orchestration
 * - Runtime viewport synchronization
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

import {
    RuntimeWorkspace,
    RuntimeWindowState
} from "./RuntimeWorkspace"

export interface RuntimeWindowCreateOptions {

    title: string

    applicationId: string

    width?: number

    height?: number

    x?: number

    y?: number
}

export interface RuntimeWindowMetrics {

    totalWindows: number

    focusedWindow?: string

    minimizedWindows: number

    maximizedWindows: number
}

export class RuntimeWindowManager {

    private readonly workspace: RuntimeWorkspace

    constructor(
        workspace: RuntimeWorkspace
    ) {

        this.workspace = workspace
    }

    /**
     * ---------------------------------------------------
     * Window Creation
     * ---------------------------------------------------
     */

    public createWindow(
        options: RuntimeWindowCreateOptions
    ): RuntimeWindowState {

        const window: RuntimeWindowState = {

            id: crypto.randomUUID(),

            title: options.title,

            applicationId: options.applicationId,

            position: {

                x: options.x ?? 120,

                y: options.y ?? 80
            },

            size: {

                width: options.width ?? 960,

                height: options.height ?? 640
            },

            minimized: false,

            maximized: false,

            focused: true,

            zIndex:
                this.getHighestZIndex() + 1
        }

        this.workspace.addWindow(window)

        console.log(
            "[RuntimeWindowManager] create",
            window.id
        )

        return window
    }

    /**
     * ---------------------------------------------------
     * Window Removal
     * ---------------------------------------------------
     */

    public destroyWindow(
        windowId: string
    ): void {

        this.workspace.removeWindow(windowId)

        console.log(
            "[RuntimeWindowManager] destroy",
            windowId
        )
    }

    /**
     * ---------------------------------------------------
     * Focus Management
     * ---------------------------------------------------
     */

    public focusWindow(
        windowId: string
    ): void {

        this.workspace.focusWindow(windowId)

        console.log(
            "[RuntimeWindowManager] focus",
            windowId
        )
    }

    /**
     * ---------------------------------------------------
     * Window Movement
     * ---------------------------------------------------
     */

    public moveWindow(
        windowId: string,
        x: number,
        y: number
    ): void {

        const window =
            this.getWindow(windowId)

        if (!window) {

            return
        }

        window.position.x = x

        window.position.y = y

        console.log(
            "[RuntimeWindowManager] move",
            windowId,
            x,
            y
        )
    }

    /**
     * ---------------------------------------------------
     * Window Resize
     * ---------------------------------------------------
     */

    public resizeWindow(
        windowId: string,
        width: number,
        height: number
    ): void {

        const window =
            this.getWindow(windowId)

        if (!window) {

            return
        }

        window.size.width = width

        window.size.height = height

        console.log(
            "[RuntimeWindowManager] resize",
            windowId,
            width,
            height
        )
    }

    /**
     * ---------------------------------------------------
     * Minimize Window
     * ---------------------------------------------------
     */

    public minimizeWindow(
        windowId: string
    ): void {

        const window =
            this.getWindow(windowId)

        if (!window) {

            return
        }

        window.minimized = true

        window.maximized = false

        console.log(
            "[RuntimeWindowManager] minimize",
            windowId
        )
    }

    /**
     * ---------------------------------------------------
     * Restore Window
     * ---------------------------------------------------
     */

    public restoreWindow(
        windowId: string
    ): void {

        const window =
            this.getWindow(windowId)

        if (!window) {

            return
        }

        window.minimized = false

        window.maximized = false

        this.focusWindow(windowId)

        console.log(
            "[RuntimeWindowManager] restore",
            windowId
        )
    }

    /**
     * ---------------------------------------------------
     * Maximize Window
     * ---------------------------------------------------
     */

    public maximizeWindow(
        windowId: string
    ): void {

        const window =
            this.getWindow(windowId)

        if (!window) {

            return
        }

        window.maximized = true

        window.minimized = false

        this.focusWindow(windowId)

        console.log(
            "[RuntimeWindowManager] maximize",
            windowId
        )
    }

    /**
     * ---------------------------------------------------
     * Window Queries
     * ---------------------------------------------------
     */

    public getWindow(
        windowId: string
    ): RuntimeWindowState | undefined {

        return this.workspace.layout.windows.find(

            (window) =>
                window.id === windowId
        )
    }

    public getFocusedWindow():
        RuntimeWindowState | undefined {

        return this.workspace.layout.windows.find(

            (window) =>
                window.focused
        )
    }

    public getWindows():
        RuntimeWindowState[] {

        return this.workspace.layout.windows
    }

    /**
     * ---------------------------------------------------
     * Window Ordering
     * ---------------------------------------------------
     */

    private getHighestZIndex(): number {

        let highest = 0

        for (
            const window
            of this.workspace.layout.windows
        ) {

            if (window.zIndex > highest) {

                highest = window.zIndex
            }
        }

        return highest
    }

    /**
     * ---------------------------------------------------
     * Window Tiling
     * ---------------------------------------------------
     */

    public tileWindows(): void {

        const windows =
            this.workspace.layout.windows

        if (windows.length === 0) {

            return
        }

        const columns =
            Math.ceil(
                Math.sqrt(windows.length)
            )

        const rows =
            Math.ceil(
                windows.length / columns
            )

        const tileWidth =
            window.innerWidth / columns

        const tileHeight =
            window.innerHeight / rows

        windows.forEach(

            (runtimeWindow, index) => {

                const row =
                    Math.floor(index / columns)

                const column =
                    index % columns

                runtimeWindow.position.x =
                    column * tileWidth

                runtimeWindow.position.y =
                    row * tileHeight

                runtimeWindow.size.width =
                    tileWidth

                runtimeWindow.size.height =
                    tileHeight
            }
        )

        console.log(
            "[RuntimeWindowManager] tile windows"
        )
    }

    /**
     * ---------------------------------------------------
     * Cascade Windows
     * ---------------------------------------------------
     */

    public cascadeWindows(): void {

        let offset = 0

        for (
            const runtimeWindow
            of this.workspace.layout.windows
        ) {

            runtimeWindow.position.x =
                80 + offset

            runtimeWindow.position.y =
                80 + offset

            offset += 32
        }

        console.log(
            "[RuntimeWindowManager] cascade windows"
        )
    }

    /**
     * ---------------------------------------------------
     * Metrics
     * ---------------------------------------------------
     */

    public getMetrics():
        RuntimeWindowMetrics {

        const windows =
            this.workspace.layout.windows

        return {

            totalWindows:
                windows.length,

            focusedWindow:
                this.getFocusedWindow()?.id,

            minimizedWindows:
                windows.filter(

                    (window) =>
                        window.minimized
                ).length,

            maximizedWindows:
                windows.filter(

                    (window) =>
                        window.maximized
                ).length
        }
    }

    /**
     * ---------------------------------------------------
     * Serialization
     * ---------------------------------------------------
     */

    public serialize(): object {

        return {

            windows:
                this.workspace.layout.windows,

            metrics:
                this.getMetrics()
        }
    }
}