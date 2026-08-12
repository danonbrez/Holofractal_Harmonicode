/**
 * Canonical Runtime OS window orchestration layer.
 * Window state is UI projection state only.
 */

import { runtimeApplicationRegistry } from "./RuntimeApplicationRegistry"

export interface RuntimeWindow {
    id: string
    title: string
    applicationId: string
    width: number
    height: number
    x: number
    y: number
    minimized?: boolean
    maximized?: boolean
    focused?: boolean
    mobileFullscreen?: boolean
    created_at_ns?: number
}

export interface RuntimeWindowCreateRequest {
    id?: string
    title: string
    applicationId: string
    width?: number
    height?: number
    x?: number
    y?: number
}

export interface RuntimeWindowManagerMetrics {
    windows: number
    focusedWindow?: string
    zIndexCounter: number
}

export class RuntimeWindowManager {
    private readonly windows = new Map<string, RuntimeWindow>()
    private zIndexCounter = 1
    private focusedWindowId?: string
    private readonly mobileBreakpoint = 768

    public openWindow(window: RuntimeWindow): void {
        const application = runtimeApplicationRegistry.get(window.applicationId)
        if (application?.singleton) {
            const existing = [...this.windows.values()].find(
                candidate => candidate.applicationId === window.applicationId,
            )
            if (existing) {
                this.restoreWindow(existing.id)
                this.focusWindow(existing.id)
                console.log("[RuntimeWindowManager] reuse singleton", existing.id)
                return
            }
        }
        const normalized = this.normalizeWindow(window)
        this.windows.set(normalized.id, normalized)
        this.focusWindow(normalized.id)
        console.log("[RuntimeWindowManager] open", normalized.id)
    }

    public createWindow(request: RuntimeWindowCreateRequest): RuntimeWindow {
        const definition = runtimeApplicationRegistry.get(request.applicationId)
        const preset = definition?.windowPreset
        const runtimeWindow: RuntimeWindow = {
            id: request.id ?? `${request.applicationId}_${Date.now()}_${this.windows.size}`,
            title: request.title,
            applicationId: request.applicationId,
            width: request.width ?? preset?.width ?? 720,
            height: request.height ?? preset?.height ?? 520,
            x: request.x ?? 96 + (this.windows.size % 8) * 28,
            y: request.y ?? 72 + (this.windows.size % 8) * 28,
        }
        this.openWindow(runtimeWindow)
        return this.getWindow(runtimeWindow.id) ?? runtimeWindow
    }

    public closeWindow(id: string): void {
        this.windows.delete(id)
        if (this.focusedWindowId === id) this.focusedWindowId = undefined
        console.log("[RuntimeWindowManager] close", id)
    }

    public focusWindow(id: string): void {
        if (!this.windows.has(id)) return
        this.focusedWindowId = id
        this.zIndexCounter += 1
        for (const [windowId, window] of this.windows) window.focused = windowId === id
        console.log("[RuntimeWindowManager] focus", id)
    }

    public moveWindow(id: string, x: number, y: number): void {
        const window = this.windows.get(id)
        if (!window) return
        window.x = x
        window.y = y
    }

    public resizeWindow(id: string, width: number, height: number): void {
        const window = this.windows.get(id)
        if (!window) return
        window.width = Math.max(320, width)
        window.height = Math.max(200, height)
    }

    public minimizeWindow(id: string): void {
        const window = this.windows.get(id)
        if (window) window.minimized = true
    }

    public restoreWindow(id: string): void {
        const window = this.windows.get(id)
        if (!window) return
        window.minimized = false
        window.maximized = false
    }

    public maximizeWindow(id: string): void {
        const window = this.windows.get(id)
        if (window) window.maximized = true
    }

    public tileWindows(
        viewportWidth = typeof globalThis !== "undefined" ? globalThis.innerWidth : 1280,
        viewportHeight = typeof globalThis !== "undefined" ? globalThis.innerHeight : 800,
    ): void {
        const visible = [...this.windows.values()].filter(window => !window.minimized)
        if (visible.length === 0) return

        const columns = Math.max(1, Math.ceil(Math.sqrt(visible.length)))
        const rows = Math.max(1, Math.ceil(visible.length / columns))
        const usableWidth = Math.max(640, viewportWidth)
        const usableHeight = Math.max(420, viewportHeight - 48)
        const tileWidth = Math.max(320, Math.floor(usableWidth / columns))
        const tileHeight = Math.max(220, Math.floor(usableHeight / rows))

        visible.forEach((window, index) => {
            const column = index % columns
            const row = Math.floor(index / columns)
            window.x = column * tileWidth
            window.y = 48 + row * tileHeight
            window.width = tileWidth
            window.height = tileHeight
            window.maximized = false
        })
    }

    public cascadeWindows(originX = 72, originY = 64, offset = 32): void {
        const visible = [...this.windows.values()].filter(window => !window.minimized)
        visible.forEach((window, index) => {
            window.x = originX + index * offset
            window.y = originY + index * offset
            window.maximized = false
        })
        if (visible.length > 0) this.focusWindow(visible[visible.length - 1].id)
    }

    private normalizeWindow(runtimeWindow: RuntimeWindow): RuntimeWindow {
        const mobile = typeof globalThis !== "undefined" && globalThis.innerWidth <= this.mobileBreakpoint
        if (mobile) {
            return {
                ...runtimeWindow,
                x: 0,
                y: 0,
                width: globalThis.innerWidth,
                height: globalThis.innerHeight,
                mobileFullscreen: true,
                created_at_ns: Date.now() * 1_000_000,
            }
        }
        return {
            ...runtimeWindow,
            minimized: runtimeWindow.minimized ?? false,
            maximized: runtimeWindow.maximized ?? false,
            focused: runtimeWindow.focused ?? false,
            mobileFullscreen: false,
            created_at_ns: Date.now() * 1_000_000,
        }
    }

    public getWindows(): RuntimeWindow[] {
        return [...this.windows.values()]
    }

    public getWindow(id: string): RuntimeWindow | undefined {
        return this.windows.get(id)
    }

    public getFocusedWindow(): RuntimeWindow | undefined {
        return this.focusedWindowId ? this.windows.get(this.focusedWindowId) : undefined
    }

    public reset(): void {
        this.windows.clear()
        this.focusedWindowId = undefined
        this.zIndexCounter = 1
    }

    public getMetrics(): RuntimeWindowManagerMetrics {
        return {
            windows: this.windows.size,
            focusedWindow: this.focusedWindowId,
            zIndexCounter: this.zIndexCounter,
        }
    }
}