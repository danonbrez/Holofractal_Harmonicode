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
