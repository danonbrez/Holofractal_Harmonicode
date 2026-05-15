import React, {
    useEffect,
    useMemo,
    useRef,
    useState
} from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeWindowManager
} from "./RuntimeWindowManager.tsx"

import {
    RuntimeViewport
} from "./RuntimeViewport"

import {
    RuntimeCommandBar
} from "./RuntimeCommandBar"

import {
    runtimeWorkspacePersistence
} from "../state/RuntimeWorkspacePersistence"

// =========================================================
// Props
// =========================================================

export interface RuntimeDesktopProps {

    runtimeOS: RuntimeOS
}

// =========================================================
// Desktop State
// =========================================================

interface DesktopViewport {

    width: number

    height: number
}

// =========================================================
// RuntimeDesktop
// =========================================================

export const RuntimeDesktop: React.FC<
    RuntimeDesktopProps
> = ({
    runtimeOS
}) => {

    const rootRef =
        useRef<HTMLDivElement>(
            null
        )

    const [viewport, setViewport] =
        useState<DesktopViewport>({

            width:
                window.innerWidth,

            height:
                window.innerHeight
        })

    const [zCounter, setZCounter] =
        useState(100)

    const [desktopReady, setDesktopReady] =
        useState(false)

    // =====================================================
    // Viewport Tracking
    // =====================================================

    useEffect(() => {

        const onResize = () => {

            setViewport({

                width:
                    window.innerWidth,

                height:
                    window.innerHeight
            })
        }

        window.addEventListener(
            "resize",
            onResize
        )

        return () => {

            window.removeEventListener(
                "resize",
                onResize
            )
        }

    }, [])

    // =====================================================
    // Workspace Restore
    // =====================================================

    useEffect(() => {

        const persisted =
            runtimeWorkspacePersistence
                .load()

        if (persisted) {

            for (
                const persistedWindow
                of persisted.windows
            ) {

                const target =
                    runtimeOS.workspace
                        .layout
                        .windows
                        .find(

                            (
                                window
                            ) => (

                                window.id
                                === persistedWindow.id
                            )
                        )

                if (!target) {

                    continue
                }

                target.x =
                    persistedWindow.x

                target.y =
                    persistedWindow.y

                target.width =
                    persistedWindow.width

                target.height =
                    persistedWindow.height

                target.minimized =
                    persistedWindow.minimized

                target.maximized =
                    persistedWindow.maximized

                target.focused =
                    persistedWindow.focused
            }
        }

        setDesktopReady(true)

    }, [runtimeOS])

    // =====================================================
    // Workspace Save
    // =====================================================

    useEffect(() => {

        if (!desktopReady) {

            return
        }

        const interval =
            window.setInterval(() => {

                runtimeWorkspacePersistence
                    .save({

                        version: 1,

                        updatedAt:
                            Date.now(),

                        windows:

                            runtimeOS.workspace
                                .layout
                                .windows
                                .map(

                                    (
                                        window
                                    ) => ({

                                        id:
                                            window.id,

                                        x:
                                            window.x,

                                        y:
                                            window.y,

                                        width:
                                            window.width,

                                        height:
                                            window.height,

                                        minimized:
                                            window.minimized,

                                        maximized:
                                            window.maximized,

                                        focused:
                                            window.focused
                                    })
                                ),

                        overlays: {

                            replayTimeline:
                                false,

                            receiptInspector:
                                false,

                            sidebarVisible:
                                true
                        },

                        viewport: {

                            cameraX: 0,

                            cameraY: 0,

                            cameraZ: 12,

                            targetX: 0,

                            targetY: 0,

                            targetZ: 0,

                            zoom: 1
                        }
                    })

            }, 2000)

        return () => {

            window.clearInterval(
                interval
            )
        }

    }, [

        desktopReady,

        runtimeOS
    ])

    // =====================================================
    // Window Ordering
    // =====================================================

    const orderedWindows =
        useMemo(() => {

            return [

                ...runtimeOS.workspace
                    .layout
                    .windows

            ].sort(

                (
                    a,
                    b
                ) => {

                    if (
                        a.focused
                    ) {

                        return 1
                    }

                    if (
                        b.focused
                    ) {

                        return -1
                    }

                    return 0
                }
            )

        }, [

            runtimeOS.workspace
                .layout
                .windows
        ])

    // =====================================================
    // Focus Window
    // =====================================================

    const focusWindow = (
        windowId: string
    ) => {

        runtimeOS.focusWindow(
            windowId
        )

        setZCounter(
            (previous) => (

                previous + 1
            )
        )
    }

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            ref={rootRef}
            className="
                absolute
                inset-0
                overflow-hidden
                bg-neutral-950
            "
        >

            {/* ================================================= */}
            {/* Viewport */}
            {/* ================================================= */}

            <RuntimeViewport
                runtimeOS={runtimeOS}
            />

            {/* ================================================= */}
            {/* Ambient Overlay */}
            {/* ================================================= */}

            <div
                className="
                    absolute
                    inset-0
                    pointer-events-none
                    bg-[radial-gradient(circle_at_center,rgba(0,255,255,0.04),transparent_70%)]
                "
            />

            {/* ================================================= */}
            {/* Desktop Grid */}
            {/* ================================================= */}

            <div
                className="
                    absolute
                    inset-0
                    pointer-events-none
                    opacity-[0.04]
                    bg-[linear-gradient(to_right,#ffffff_1px,transparent_1px),linear-gradient(to_bottom,#ffffff_1px,transparent_1px)]
                    bg-[size:48px_48px]
                "
            />

            {/* ================================================= */}
            {/* Runtime Windows */}
            {/* ================================================= */}

            <div
                className="
                    absolute
                    inset-0
                    overflow-hidden
                "
            >

                {
                    orderedWindows.map(

                        (
                            runtimeWindow,
                            index
                        ) => {

                            if (
                                runtimeWindow
                                    .minimized
                            ) {

                                return null
                            }

                            return (

                                <RuntimeWindowManager
                                    key={
                                        runtimeWindow.id
                                    }

                                    runtimeOS={
                                        runtimeOS
                                    }

                                    runtimeWindow={
                                        runtimeWindow
                                    }

                                    desktopWidth={
                                        viewport.width
                                    }

                                    desktopHeight={
                                        viewport.height
                                    }

                                    zIndex={
                                        zCounter
                                        +
                                        index
                                    }

                                    onFocus={() => {

                                        focusWindow(

                                            runtimeWindow.id
                                        )
                                    }}
                                />
                            )
                        }
                    )
                }

            </div>

            {/* ================================================= */}
            {/* Runtime Command Bar */}
            {/* ================================================= */}

            <RuntimeCommandBar
                runtimeOS={runtimeOS}
            />

            {/* ================================================= */}
            {/* Desktop Metrics */}
            {/* ================================================= */}

            <div
                className="
                    absolute
                    bottom-4
                    right-4
                    z-[2500]
                    rounded-2xl
                    border
                    border-neutral-800
                    bg-neutral-900/80
                    backdrop-blur-xl
                    px-4
                    py-3
                    text-xs
                    font-mono
                    text-neutral-300
                    flex
                    flex-col
                    gap-2
                    min-w-[220px]
                "
            >

                <DesktopMetric
                    label="viewport"
                    value={

                        `${viewport.width}×${viewport.height}`
                    }
                />

                <DesktopMetric
                    label="windows"
                    value={
                        String(

                            orderedWindows
                                .length
                        )
                    }
                />

                <DesktopMetric
                    label="runtime"
                    value={

                        runtimeOS.state.connected

                            ? "online"

                            : "offline"
                    }
                />

                <DesktopMetric
                    label="events"
                    value={
                        String(

                            runtimeOS.state
                                .totalEvents
                        )
                    }
                />

            </div>

        </div>
    )
}

// =========================================================
// Desktop Metric
// =========================================================

interface DesktopMetricProps {

    label: string

    value: string
}

const DesktopMetric: React.FC<
    DesktopMetricProps
> = ({
    label,
    value
}) => {

    return (

        <div
            className="
                flex
                items-center
                justify-between
                gap-6
            "
        >

            <div
                className="
                    opacity-50
                "
            >
                {label}
            </div>

            <div>
                {value}
            </div>

        </div>
    )
}