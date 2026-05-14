import React, {
    useEffect,
    useState
} from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeDesktop
} from "./RuntimeDesktop"

import {
    RuntimeTopbar
} from "./RuntimeTopbar"

import {
    RuntimeSidebar
} from "./RuntimeSidebar"

import ReceiptInspector from
    "../../runtime_apps/instruments/ReceiptInspector"

import ReplayTimeline from
    "../../runtime_apps/instruments/ReplayTimeline"

// =========================================================
// Props
// =========================================================

export interface RuntimeShellProps {

    runtimeOS: RuntimeOS
}

// =========================================================
// RuntimeShell
// =========================================================

export const RuntimeShell: React.FC<
    RuntimeShellProps
> = ({
    runtimeOS
}) => {

    const [booted, setBooted] =
        useState(false)

    const [showSidebar, setShowSidebar] =
        useState(true)

    const [showReceipts, setShowReceipts] =
        useState(false)

    const [showReplay, setShowReplay] =
        useState(false)

    const [metrics, setMetrics] =
        useState(

            runtimeOS.getMetrics()
        )

    // =====================================================
    // Runtime Bootstrap
    // =====================================================

    useEffect(() => {

        let mounted = true

        runtimeOS.initialize()
            .then(() => {

                if (!mounted) {

                    return
                }

                setBooted(true)
            })

        const interval =
            window.setInterval(() => {

                if (!mounted) {

                    return
                }

                setMetrics(

                    runtimeOS
                        .getMetrics()
                )

            }, 250)

        return () => {

            mounted = false

            window.clearInterval(
                interval
            )

            runtimeOS.shutdown()
        }

    }, [runtimeOS])

    // =====================================================
    // Boot Surface
    // =====================================================

    if (!booted) {

        return (

            <BootSurface />
        )
    }

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            className="
                fixed
                inset-0
                overflow-hidden
                bg-neutral-950
                text-white
            "
        >

            {/* ================================================= */}
            {/* Runtime Desktop */}
            {/* ================================================= */}

            <RuntimeDesktop
                runtimeOS={runtimeOS}
            />

            {/* ================================================= */}
            {/* Topbar */}
            {/* ================================================= */}

            <RuntimeTopbar
                runtimeOS={runtimeOS}
            />

            {/* ================================================= */}
            {/* Sidebar */}
            {/* ================================================= */}

            {
                showSidebar && (

                    <RuntimeSidebar
                        runtimeOS={runtimeOS}
                    />
                )
            }

            {/* ================================================= */}
            {/* Runtime HUD */}
            {/* ================================================= */}

            <div
                className="
                    absolute
                    top-12
                    right-4
                    z-[3000]
                    flex
                    flex-col
                    gap-3
                    w-[340px]
                "
            >

                {/* --------------------------------------------- */}
                {/* Runtime Status */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        rounded-2xl
                        border
                        border-neutral-800
                        bg-neutral-900/80
                        backdrop-blur-xl
                        p-4
                        shadow-2xl
                    "
                >

                    <div
                        className="
                            flex
                            items-center
                            justify-between
                            mb-4
                        "
                    >

                        <div
                            className="
                                text-sm
                                font-semibold
                                tracking-wide
                            "
                        >
                            Runtime Status
                        </div>

                        <RuntimeIndicator
                            online={
                                Boolean(
                                    metrics.connected
                                )
                            }
                        />

                    </div>

                    <div
                        className="
                            grid
                            grid-cols-2
                            gap-3
                            text-xs
                            font-mono
                        "
                    >

                        <MetricField
                            label="runtime"
                            value={
                                metrics.connected
                                    ? "online"
                                    : "offline"
                            }
                        />

                        <MetricField
                            label="replay"
                            value={
                                metrics.replayReady
                                    ? "online"
                                    : "offline"
                            }
                        />

                        <MetricField
                            label="graph"
                            value={
                                metrics.graphReady
                                    ? "online"
                                    : "offline"
                            }
                        />

                        <MetricField
                            label="transport"
                            value={
                                metrics.transportReady
                                    ? "online"
                                    : "offline"
                            }
                        />

                        <MetricField
                            label="events"
                            value={
                                String(
                                    metrics.totalEvents
                                )
                            }
                        />

                        <MetricField
                            label="windows"
                            value={
                                String(
                                    metrics.workspaceWindows
                                )
                            }
                        />

                    </div>

                </div>

                {/* --------------------------------------------- */}
                {/* Runtime Instruments */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        rounded-2xl
                        border
                        border-neutral-800
                        bg-neutral-900/80
                        backdrop-blur-xl
                        p-4
                        shadow-2xl
                    "
                >

                    <div
                        className="
                            text-sm
                            font-semibold
                            tracking-wide
                            mb-4
                        "
                    >
                        Runtime Instruments
                    </div>

                    <div
                        className="
                            flex
                            flex-col
                            gap-2
                        "
                    >

                        <button
                            onClick={() => {

                                setShowReceipts(
                                    !showReceipts
                                )
                            }}
                            className="
                                runtime-button
                                w-full
                                px-3
                                py-2
                                text-sm
                                text-left
                            "
                        >

                            {
                                showReceipts
                                    ? "Hide"
                                    : "Show"
                            }

                            {" "}

                            Receipt Inspector

                        </button>

                        <button
                            onClick={() => {

                                setShowReplay(
                                    !showReplay
                                )
                            }}
                            className="
                                runtime-button
                                w-full
                                px-3
                                py-2
                                text-sm
                                text-left
                            "
                        >

                            {
                                showReplay
                                    ? "Hide"
                                    : "Show"
                            }

                            {" "}

                            Replay Timeline

                        </button>

                        <button
                            onClick={() => {

                                setShowSidebar(
                                    !showSidebar
                                )
                            }}
                            className="
                                runtime-button
                                w-full
                                px-3
                                py-2
                                text-sm
                                text-left
                            "
                        >

                            {
                                showSidebar
                                    ? "Hide"
                                    : "Show"
                            }

                            {" "}

                            Runtime Sidebar

                        </button>

                    </div>

                </div>

            </div>

            {/* ================================================= */}
            {/* Receipt Inspector Overlay */}
            {/* ================================================= */}

            {
                showReceipts && (

                    <OverlayWindow
                        title="Receipt Inspector"
                        onClose={() => {

                            setShowReceipts(
                                false
                            )
                        }}
                    >

                        <ReceiptInspector
                            runtimeStore={
                                runtimeOS.store
                            }
                        />

                    </OverlayWindow>
                )
            }

            {/* ================================================= */}
            {/* Replay Timeline Overlay */}
            {/* ================================================= */}

            {
                showReplay && (

                    <OverlayWindow
                        title="Replay Timeline"
                        onClose={() => {

                            setShowReplay(
                                false
                            )
                        }}
                    >

                        <ReplayTimeline
                            runtimeStore={
                                runtimeOS.store
                            }
                        />

                    </OverlayWindow>
                )
            }

        </div>
    )
}

// =========================================================
// Boot Surface
// =========================================================

const BootSurface: React.FC =
() => {

    return (

        <div
            className="
                fixed
                inset-0
                bg-black
                text-cyan-400
                flex
                items-center
                justify-center
                font-mono
            "
        >

            <div
                className="
                    flex
                    flex-col
                    items-center
                    gap-6
                "
            >

                <div
                    className="
                        text-3xl
                        font-semibold
                        tracking-[0.3em]
                    "
                >
                    HHS
                </div>

                <div
                    className="
                        text-sm
                        opacity-70
                    "
                >
                    Runtime OS Boot Sequence
                </div>

                <div
                    className="
                        w-64
                        h-[2px]
                        bg-neutral-900
                        overflow-hidden
                        relative
                    "
                >

                    <div
                        className="
                            absolute
                            inset-y-0
                            left-0
                            w-1/2
                            bg-cyan-400
                            animate-pulse
                        "
                    />

                </div>

            </div>

        </div>
    )
}

// =========================================================
// Overlay Window
// =========================================================

interface OverlayWindowProps {

    title: string

    children: React.ReactNode

    onClose: () => void
}

const OverlayWindow: React.FC<
    OverlayWindowProps
> = ({
    title,
    children,
    onClose
}) => {

    return (

        <div
            className="
                absolute
                inset-0
                z-[5000]
                bg-black/50
                backdrop-blur-sm
                flex
                items-center
                justify-center
                p-8
            "
        >

            <div
                className="
                    w-full
                    h-full
                    rounded-2xl
                    overflow-hidden
                    border
                    border-neutral-800
                    bg-neutral-950
                    shadow-2xl
                    flex
                    flex-col
                "
            >

                {/* --------------------------------------------- */}
                {/* Header */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        h-12
                        shrink-0
                        border-b
                        border-neutral-800
                        bg-neutral-900
                        px-4
                        flex
                        items-center
                        justify-between
                    "
                >

                    <div
                        className="
                            text-sm
                            font-semibold
                            tracking-wide
                        "
                    >
                        {title}
                    </div>

                    <button
                        onClick={onClose}
                        className="
                            runtime-button
                            px-3
                            py-1
                            text-xs
                        "
                    >
                        close
                    </button>

                </div>

                {/* --------------------------------------------- */}
                {/* Content */}
                {/* --------------------------------------------- */}

                <div
                    className="
                        flex-1
                        overflow-hidden
                    "
                >
                    {children}
                </div>

            </div>

        </div>
    )
}

// =========================================================
// Metric Field
// =========================================================

interface MetricFieldProps {

    label: string

    value: string
}

const MetricField: React.FC<
    MetricFieldProps
> = ({
    label,
    value
}) => {

    return (

        <div
            className="
                flex
                flex-col
                gap-1
            "
        >

            <div
                className="
                    opacity-50
                    uppercase
                    tracking-wide
                    text-[10px]
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

// =========================================================
// Runtime Indicator
// =========================================================

interface RuntimeIndicatorProps {

    online: boolean
}

const RuntimeIndicator: React.FC<
    RuntimeIndicatorProps
> = ({
    online
}) => {

    return (

        <div
            className="
                flex
                items-center
                gap-2
            "
        >

            <div
                className={`
                    w-2
                    h-2
                    rounded-full
                    ${
                        online
                            ? "bg-green-400"
                            : "bg-red-400"
                    }
                `}
            />

            <div
                className="
                    text-xs
                    uppercase
                    tracking-wide
                    opacity-60
                "
            >
                {
                    online
                        ? "online"
                        : "offline"
                }
            </div>

        </div>
    )
}