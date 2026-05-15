/**
 * =========================================================
 * RuntimeWindowManager
 * =========================================================
 *
 * Canonical Runtime OS window orchestration layer.
 *
 * IMPORTANT
 * ---------------------------------------------------------
 * Window state is UI projection state ONLY.
 *
 * Window state is NOT:
 *
 *   - runtime authority
 *   - replay authority
 *   - graph authority
 *   - transport authority
 *
 * This layer only manages:
 *
 *   - layout
 *   - focus
 *   - z-order
 *   - window geometry
 *   - mobile fallback
 *   - fullscreen projection
 */

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

// =========================================================
// Metrics
// =========================================================

export interface RuntimeWindowManagerMetrics {

    windows: number

    focusedWindow?: string

    zIndexCounter: number
}

// =========================================================
// RuntimeWindowManager
// =========================================================

export class RuntimeWindowManager {

    // =====================================================
    // Windows
    // =====================================================

    private readonly windows =
        new Map<
            string,
            RuntimeWindow
        >()

    // =====================================================
    // Z-Index
    // =====================================================

    private zIndexCounter =
        1

    // =====================================================
    // Focus
    // =====================================================

    private focusedWindowId?:
        string

    // =====================================================
    // Mobile Breakpoint
    // =====================================================

    private readonly mobileBreakpoint =
        768

    // =====================================================
    // Open Window
    // =====================================================

    public openWindow(
        window: RuntimeWindow
    ): void {

        const normalized =

            this.normalizeWindow(
                window
            )

        this.windows.set(

            normalized.id,

            normalized
        )

        this.focusWindow(
            normalized.id
        )

        console.log(

            "[RuntimeWindowManager] open",

            normalized.id
        )
    }

    // =====================================================
    // Close Window
    // =====================================================

    public closeWindow(
        id: string
    ): void {

        this.windows.delete(id)

        if (
            this.focusedWindowId
            === id
        ) {

            this.focusedWindowId =
                undefined
        }

        console.log(

            "[RuntimeWindowManager] close",

            id
        )
    }

    // =====================================================
    // Focus
    // =====================================================

    public focusWindow(
        id: string
    ): void {

        if (
            !this.windows.has(id)
        ) {

            return
        }

        this.focusedWindowId =
            id

        this.zIndexCounter += 1

        for (
            const [
                windowId,
                window
            ]
            of this.windows
        ) {

            window.focused =
                (
                    windowId === id
                )
        }

        console.log(

            "[RuntimeWindowManager] focus",

            id
        )
    }

    // =====================================================
    // Move
    // =====================================================

    public moveWindow(

        id: string,

        x: number,

        y: number

    ): void {

        const window =
            this.windows.get(id)

        if (!window) {

            return
        }

        window.x = x

        window.y = y
    }

    // =====================================================
    // Resize
    // =====================================================

    public resizeWindow(

        id: string,

        width: number,

        height: number

    ): void {

        const window =
            this.windows.get(id)

        if (!window) {

            return
        }

        window.width = Math.max(
            320,
            width
        )

        window.height = Math.max(
            200,
            height
        )
    }

    // =====================================================
    // Minimize
    // =====================================================

    public minimizeWindow(
        id: string
    ): void {

        const window =
            this.windows.get(id)

        if (!window) {

            return
        }

        window.minimized = true
    }

    // =====================================================
    // Restore
    // =====================================================

    public restoreWindow(
        id: string
    ): void {

        const window =
            this.windows.get(id)

        if (!window) {

            return
        }

        window.minimized = false

        window.maximized = false
    }

    // =====================================================
    // Maximize
    // =====================================================

    public maximizeWindow(
        id: string
    ): void {

        const window =
            this.windows.get(id)

        if (!window) {

            return
        }

        window.maximized = true
    }

    // =====================================================
    // Normalize
    // =====================================================

    private normalizeWindow(
        window: RuntimeWindow
    ): RuntimeWindow {

        const mobile =

            typeof window !== "undefined"
            &&
            typeof globalThis !== "undefined"
            &&
            globalThis.innerWidth
            <= this.mobileBreakpoint

        if (mobile) {

            return {

                ...window,

                x: 0,

                y: 0,

                width:
                    globalThis.innerWidth,

                height:
                    globalThis.innerHeight,

                mobileFullscreen: true,

                created_at_ns:
                    Date.now() * 1_000_000
            }
        }

        return {

            ...window,

            minimized:
                window.minimized
                ?? false,

            maximized:
                window.maximized
                ?? false,

            focused:
                window.focused
                ?? false,

            mobileFullscreen:
                false,

            created_at_ns:
                Date.now() * 1_000_000
        }
    }

    // =====================================================
    // Windows
    // =====================================================

    public getWindows():
        RuntimeWindow[] {

        return [

            ...this.windows.values()
        ]
    }

    // =====================================================
    // Get Window
    // =====================================================

    public getWindow(
        id: string
    ):
        RuntimeWindow
        | undefined {

        return this.windows.get(
            id
        )
    }

    // =====================================================
    // Focused Window
    // =====================================================

    public getFocusedWindow():
        RuntimeWindow
        | undefined {

        if (
            !this.focusedWindowId
        ) {

            return undefined
        }

        return this.windows.get(
            this.focusedWindowId
        )
    }

    // =====================================================
    // Reset
    // =====================================================

    public reset():
        void {

        this.windows.clear()

        this.focusedWindowId =
            undefined

        this.zIndexCounter = 1
    }

    // =====================================================
    // Metrics
    // =====================================================

    public getMetrics():
        RuntimeWindowManagerMetrics {

        return {

            windows:
                this.windows.size,

            focusedWindow:
                this.focusedWindowId,

            zIndexCounter:
                this.zIndexCounter
        }
    }
}