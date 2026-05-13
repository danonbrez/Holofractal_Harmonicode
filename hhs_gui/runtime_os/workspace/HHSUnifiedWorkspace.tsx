import React, {
    useEffect,
    useMemo,
    useState
} from "react"

import {
    RuntimeApplicationRegistry
} from "../core/RuntimeApplicationRegistry"

import {
    RuntimeCommandPalette
} from "../core/RuntimeCommandPalette"

import {
    RuntimeDesktop
} from "../core/RuntimeDesktop"

import {
    RuntimeDock
} from "../core/RuntimeDock"

import {
    RuntimeExecutionAuthority
} from "../core/RuntimeExecutionAuthority"

import {
    RuntimeGraphOverlay
} from "../core/RuntimeGraphOverlay"

import {
    RuntimeKernelBridge
} from "../core/RuntimeKernelBridge"

import {
    RuntimeRouter
} from "../core/RuntimeRouter"

import {
    RuntimeSidebar
} from "../core/RuntimeSidebar"

import {
    RuntimeTopbar
} from "../core/RuntimeTopbar"

import {
    RuntimeWindowManager
} from "../core/RuntimeWindowManager"

import {
    RuntimeWorkspace
} from "../core/RuntimeWorkspace"

import {
    HHSCalculatorGraphProjection
} from "../../runtime_apps/calculator/HHSCalculatorGraphProjection"

import {
    HHSCalculatorSurface
} from "../../runtime_apps/calculator/HHSCalculatorSurface"

import {
    HHSRuntimeBreadboard
} from "../../runtime_apps/breadboard/HHSRuntimeBreadboard"

import {
    HHSRuntimeTransportOverlay
} from "../../runtime_apps/breadboard/HHSRuntimeTransportOverlay"

/**
 * HHS Unified Workspace
 * ---------------------------------------------------
 * Canonical Runtime OS operating manifold.
 *
 * Responsibilities:
 *
 * - Shared runtime world orchestration
 * - Runtime-authorized projection composition
 * - Unified graph manifold
 * - Unified replay continuity
 * - Unified transport topology
 * - Shared runtime telemetry
 * - Shared receipt-chain visibility
 * - Multi-surface runtime projection
 *
 * Core Rule:
 *
 * SINGLE RUNTIME STATE
 * MULTI-SURFACE PROJECTION
 *
 * Kernel
 * = execution truth
 *
 * Runtime
 * = orchestration truth
 *
 * GUI
 * = projection truth
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface HHSUnifiedWorkspaceProps {

    websocketUrl: string
}

export const HHSUnifiedWorkspace:
React.FC<
    HHSUnifiedWorkspaceProps
> = ({
    websocketUrl
}) => {

    /**
     * ---------------------------------------------------
     * Runtime Core
     * ---------------------------------------------------
     */

    const runtimeRouter =
        useMemo(() => {

            return new RuntimeRouter()

        }, [])

    const runtimeRegistry =
        useMemo(() => {

            return new RuntimeApplicationRegistry()

        }, [])

    const runtimeWindowManager =
        useMemo(() => {

            return new RuntimeWindowManager()

        }, [])

    const runtimeWorkspace =
        useMemo(() => {

            return new RuntimeWorkspace({

                id:
                    "hhs_unified_workspace",

                name:
                    "HHS Unified Workspace"
            })

        }, [])

    const kernelBridge =
        useMemo(() => {

            return new RuntimeKernelBridge({

                websocketUrl,

                reconnectIntervalMs:
                    3000
            })

        }, [websocketUrl])

    const executionAuthority =
        useMemo(() => {

            return new RuntimeExecutionAuthority(

                kernelBridge
            )

        }, [kernelBridge])

    /**
     * ---------------------------------------------------
     * Runtime State
     * ---------------------------------------------------
     */

    const [runtimeReady, setRuntimeReady] =
        useState(false)

    const [telemetry, setTelemetry] =
        useState<any>(null)

    /**
     * ---------------------------------------------------
     * Runtime Initialization
     * ---------------------------------------------------
     */

    useEffect(() => {

        const initialize =
            async () => {

                await kernelBridge.initialize()

                await executionAuthority.initialize()

                setRuntimeReady(true)
            }

        initialize()

    }, [
        kernelBridge,
        executionAuthority
    ])

    /**
     * ---------------------------------------------------
     * Runtime Telemetry
     * ---------------------------------------------------
     */

    useEffect(() => {

        const telemetryHandler = (
            payload: any
        ) => {

            setTelemetry(payload)
        }

        kernelBridge.on(
            "telemetry",
            telemetryHandler
        )

        return () => {

            kernelBridge.off(
                "telemetry",
                telemetryHandler
            )
        }

    }, [kernelBridge])

    /**
     * ---------------------------------------------------
     * Runtime Application Registration
     * ---------------------------------------------------
     */

    useEffect(() => {

        runtimeRegistry.registerApplication({

            id:
                "hhs_calculator",

            name:
                "HHS Calculator",

            applicationType:
                "symbolic",

            visible:
                true,

            mounted:
                false,

            route:
                "/calculator",

            icon:
                "calculator"
        })

        runtimeRegistry.registerApplication({

            id:
                "runtime_breadboard",

            name:
                "Runtime Breadboard",

            applicationType:
                "graph",

            visible:
                true,

            mounted:
                false,

            route:
                "/breadboard",

            icon:
                "network"
        })

        runtimeRegistry.registerApplication({

            id:
                "runtime_transport",

            name:
                "Runtime Transport",

            applicationType:
                "transport",

            visible:
                true,

            mounted:
                false,

            route:
                "/transport",

            icon:
                "orbit"
        })

    }, [runtimeRegistry])

    /**
     * ---------------------------------------------------
     * Runtime Projection Surface
     * ---------------------------------------------------
     */

    if (!runtimeReady) {

        return (

            <div
                className="
                    w-screen
                    h-screen
                    bg-black
                    flex
                    items-center
                    justify-center
                    text-cyan-300
                    font-mono
                "
            >

                initializing runtime manifold...

            </div>
        )
    }

    /**
     * ---------------------------------------------------
     * Unified Runtime Workspace
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-screen
                h-screen
                bg-black
                text-neutral-100
                overflow-hidden
                relative
                flex
            "
        >

            {/* -------------------------------- */}
            {/* Sidebar */}
            {/* -------------------------------- */}

            <RuntimeSidebar

                registry={runtimeRegistry}

                router={runtimeRouter}

                windowManager={
                    runtimeWindowManager
                }
            />

            {/* -------------------------------- */}
            {/* Main Runtime World */}
            {/* -------------------------------- */}

            <div
                className="
                    flex-1
                    flex
                    flex-col
                    relative
                    overflow-hidden
                "
            >

                {/* ---------------------------- */}
                {/* Topbar */}
                {/* ---------------------------- */}

                <RuntimeTopbar

                    router={runtimeRouter}

                    registry={runtimeRegistry}

                    windowManager={
                        runtimeWindowManager
                    }
                />

                {/* ---------------------------- */}
                {/* Runtime World */}
                {/* ---------------------------- */}

                <div
                    className="
                        flex-1
                        relative
                        overflow-hidden
                    "
                >

                    {/* ------------------------ */}
                    {/* Shared Runtime Desktop */}
                    {/* ------------------------ */}

                    <RuntimeDesktop

                        workspace={
                            runtimeWorkspace
                        }

                        registry={
                            runtimeRegistry
                        }

                        windowManager={
                            runtimeWindowManager
                        }
                    />

                    {/* ------------------------ */}
                    {/* Shared Runtime Graph */}
                    {/* ------------------------ */}

                    <RuntimeGraphOverlay

                        kernelBridge={
                            kernelBridge
                        }
                    />

                    {/* ------------------------ */}
                    {/* Calculator Projection */}
                    {/* ------------------------ */}

                    <div
                        className="
                            absolute
                            inset-0
                            pointer-events-none
                            opacity-40
                        "
                    >

                        <HHSCalculatorGraphProjection

                            kernelBridge={
                                kernelBridge
                            }
                        />

                    </div>

                    {/* ------------------------ */}
                    {/* Runtime Transport */}
                    {/* ------------------------ */}

                    <div
                        className="
                            absolute
                            inset-0
                            pointer-events-none
                            opacity-60
                        "
                    >

                        <HHSRuntimeTransportOverlay

                            kernelBridge={
                                kernelBridge
                            }
                        />

                    </div>

                </div>

                {/* ---------------------------- */}
                {/* Runtime Dock */}
                {/* ---------------------------- */}

                <RuntimeDock

                    registry={runtimeRegistry}

                    windowManager={
                        runtimeWindowManager
                    }
                />

            </div>

            {/* -------------------------------- */}
            {/* Runtime Command Palette */}
            {/* -------------------------------- */}

            <RuntimeCommandPalette

                registry={runtimeRegistry}

                router={runtimeRouter}

                windowManager={
                    runtimeWindowManager
                }
            />

            {/* -------------------------------- */}
            {/* Shared Runtime Applications */}
            {/* -------------------------------- */}

            <div
                className="
                    hidden
                "
            >

                {/* -------------------------------- */}
                {/* Calculator */}
                {/* -------------------------------- */}

                <HHSCalculatorSurface

                    authority={
                        executionAuthority
                    }
                />

                {/* -------------------------------- */}
                {/* Runtime Breadboard */}
                {/* -------------------------------- */}

                <HHSRuntimeBreadboard

                    authority={
                        executionAuthority
                    }

                    kernelBridge={
                        kernelBridge
                    }
                />

            </div>

            {/* -------------------------------- */}
            {/* Unified Runtime Telemetry */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    top-4
                    right-4
                    z-50
                    flex
                    flex-col
                    gap-2
                    text-[10px]
                    font-mono
                "
            >

                <div
                    className="
                        px-3
                        py-2
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black/70
                        backdrop-blur-xl
                    "
                >
                    unified runtime manifold
                </div>

                <div
                    className="
                        px-3
                        py-2
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black/70
                        backdrop-blur-xl
                    "
                >
                    kernel:
                    {" "}
                    {
                        kernelBridge.state
                            .connected

                            ? "CONNECTED"

                            : "DISCONNECTED"
                    }
                </div>

                <div
                    className="
                        px-3
                        py-2
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black/70
                        backdrop-blur-xl
                    "
                >
                    replay:
                    {" "}
                    {
                        kernelBridge.state
                            .replaySynchronized

                            ? "SYNC"

                            : "DESYNC"
                    }
                </div>

                <div
                    className="
                        px-3
                        py-2
                        rounded-xl
                        border
                        border-neutral-800
                        bg-black/70
                        backdrop-blur-xl
                    "
                >
                    authority:
                    {" "}
                    {
                        executionAuthority
                            .state
                            .authorityLocked

                            ? "LOCKED"

                            : "UNLOCKED"
                    }
                </div>

                {
                    telemetry && (

                        <div
                            className="
                                px-3
                                py-2
                                rounded-xl
                                border
                                border-neutral-800
                                bg-black/70
                                backdrop-blur-xl
                                flex
                                flex-col
                                gap-1
                            "
                        >

                            <div>
                                fps:
                                {" "}
                                {
                                    telemetry.runtimeFps
                                }
                            </div>

                            <div>
                                replay:
                                {" "}
                                {
                                    telemetry.replayDepth
                                }
                            </div>

                            <div>
                                receipts:
                                {" "}
                                {
                                    telemetry.receiptCount
                                }
                            </div>

                            <div>
                                graphs:
                                {" "}
                                {
                                    telemetry.activeGraphs
                                }
                            </div>

                        </div>
                    )
                }

            </div>

        </div>
    )
}