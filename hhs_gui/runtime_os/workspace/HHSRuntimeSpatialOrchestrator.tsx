import React, {
    createContext,
    useContext,
    useEffect,
    useMemo,
    useRef,
    useState
} from "react"

import * as THREE from "three"

import {
    Canvas,
    useFrame
} from "@react-three/fiber"

import {
    OrbitControls
} from "@react-three/drei"

import {
    RuntimeKernelBridge
} from "../core/RuntimeKernelBridge"

import {
    RuntimeExecutionAuthority
} from "../core/RuntimeExecutionAuthority"

/**
 * HHS Runtime Spatial Orchestrator
 * ---------------------------------------------------
 * Canonical Runtime OS spatial orchestration layer.
 *
 * Responsibilities:
 *
 * - Shared runtime world space
 * - Shared runtime timing
 * - Shared projection scheduling
 * - Shared transport timing
 * - Shared replay timing
 * - Shared interaction routing
 * - Shared scene-layer orchestration
 * - Shared projection visibility
 *
 * CRITICAL:
 *
 * This layer DOES NOT:
 *
 * - execute runtime logic
 * - mutate runtime state
 * - generate replay
 * - generate receipts
 * - simulate kernel execution
 *
 * This layer ONLY orchestrates:
 *
 * Runtime
 * → Spatial projection
 * → Shared timing
 * → Shared scheduling
 * → Shared visibility
 *
 * Runtime truth remains authoritative.
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeSpatialLayer {

    id: string

    priority: number

    visible: boolean

    opacity: number

    projectionType: string
}

export interface RuntimeSpatialClock {

    elapsed: number

    delta: number

    replayTime: number

    transportTime: number

    synchronizationTime: number
}

export interface RuntimeSpatialSelection {

    id: string

    source: string

    type: string
}

export interface RuntimeSpatialContextValue {

    clock: RuntimeSpatialClock

    selectedObject?:
        RuntimeSpatialSelection

    layers:
        RuntimeSpatialLayer[]

    setSelectedObject:
        (
            selection?:
                RuntimeSpatialSelection
        ) => void
}

const RuntimeSpatialContext =
    createContext<
        RuntimeSpatialContextValue
    >(
        undefined as any
    )

export const useRuntimeSpatial =
    (): RuntimeSpatialContextValue => {

        return useContext(
            RuntimeSpatialContext
        )
    }

export interface HHSRuntimeSpatialOrchestratorProps {

    kernelBridge: RuntimeKernelBridge

    authority: RuntimeExecutionAuthority

    children?: React.ReactNode
}

/**
 * ---------------------------------------------------
 * Runtime Clock Driver
 * ---------------------------------------------------
 */

const RuntimeClockDriver:
React.FC<{

    setClock:
        React.Dispatch<
            React.SetStateAction<
                RuntimeSpatialClock
            >
        >

}> = ({
    setClock
}) => {

    useFrame((state, delta) => {

        /**
         * ------------------------------------------------
         * Shared runtime timing manifold.
         * ------------------------------------------------
         */

        setClock({

            elapsed:
                state.clock.elapsedTime,

            delta,

            replayTime:
                state.clock.elapsedTime * 0.75,

            transportTime:
                state.clock.elapsedTime * 1.25,

            synchronizationTime:
                state.clock.elapsedTime * 0.5
        })
    })

    return null
}

/**
 * ---------------------------------------------------
 * Runtime Projection Scheduler
 * ---------------------------------------------------
 */

const RuntimeProjectionScheduler:
React.FC<{

    layers:
        RuntimeSpatialLayer[]

}> = ({
    layers
}) => {

    const schedulerRef =
        useRef<THREE.Group>(null)

    useFrame(() => {

        if (!schedulerRef.current) {

            return
        }

        /**
         * ------------------------------------------------
         * Shared projection orchestration.
         *
         * NO runtime execution.
         * ------------------------------------------------
         */

        schedulerRef.current.children
            .forEach(

                (
                    child,
                    index
                ) => {

                    const layer =
                        layers[index]

                    if (!layer) {

                        return
                    }

                    child.visible =
                        layer.visible
                }
            )
    })

    return (

        <group ref={schedulerRef} />
    )
}

/**
 * ---------------------------------------------------
 * Main Orchestrator
 * ---------------------------------------------------
 */

export const HHSRuntimeSpatialOrchestrator:
React.FC<
    HHSRuntimeSpatialOrchestratorProps
> = ({
    kernelBridge,
    authority,
    children
}) => {

    /**
     * ---------------------------------------------------
     * Shared Runtime Clock
     * ---------------------------------------------------
     */

    const [clock, setClock] =
        useState<
            RuntimeSpatialClock
        >({

            elapsed: 0,

            delta: 0,

            replayTime: 0,

            transportTime: 0,

            synchronizationTime: 0
        })

    /**
     * ---------------------------------------------------
     * Shared Selection Routing
     * ---------------------------------------------------
     */

    const [selectedObject, setSelectedObject] =
        useState<
            RuntimeSpatialSelection | undefined
        >()

    /**
     * ---------------------------------------------------
     * Shared Runtime Layers
     * ---------------------------------------------------
     */

    const [layers, setLayers] =
        useState<
            RuntimeSpatialLayer[]
        >([

            {

                id:
                    "runtime_graph",

                priority: 1,

                visible: true,

                opacity: 1,

                projectionType:
                    "graph"
            },

            {

                id:
                    "runtime_transport",

                priority: 2,

                visible: true,

                opacity: 0.7,

                projectionType:
                    "transport"
            },

            {

                id:
                    "runtime_interaction",

                priority: 3,

                visible: true,

                opacity: 1,

                projectionType:
                    "interaction"
            },

            {

                id:
                    "runtime_overlay",

                priority: 4,

                visible: true,

                opacity: 1,

                projectionType:
                    "overlay"
            }
        ])

    /**
     * ---------------------------------------------------
     * Runtime Telemetry Synchronization
     * ---------------------------------------------------
     */

    const [telemetry, setTelemetry] =
        useState<any>(null)

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
     * Shared Spatial Context
     * ---------------------------------------------------
     */

    const contextValue =
        useMemo<
            RuntimeSpatialContextValue
        >(() => {

            return {

                clock,

                selectedObject,

                layers,

                setSelectedObject
            }

        }, [

            clock,

            selectedObject,

            layers
        ])

    /**
     * ---------------------------------------------------
     * Projection Surface
     * ---------------------------------------------------
     */

    return (

        <RuntimeSpatialContext.Provider
            value={contextValue}
        >

            <div
                className="
                    absolute
                    inset-0
                    overflow-hidden
                "
            >

                {/* -------------------------------- */}
                {/* Shared Runtime World */}
                {/* -------------------------------- */}

                <Canvas

                    camera={{

                        position: [0, 12, 20],

                        fov: 60
                    }}

                    gl={{

                        antialias: true,

                        alpha: true
                    }}
                >

                    <ambientLight
                        intensity={0.7}
                    />

                    <pointLight

                        position={[10, 10, 10]}

                        intensity={1.7}
                    />

                    <pointLight

                        position={[-10, -5, -10]}

                        intensity={0.8}

                        color="#22d3ee"
                    />

                    {/* ---------------------------- */}
                    {/* Shared Runtime Clock */}
                    {/* ---------------------------- */}

                    <RuntimeClockDriver
                        setClock={setClock}
                    />

                    {/* ---------------------------- */}
                    {/* Projection Scheduler */}
                    {/* ---------------------------- */}

                    <RuntimeProjectionScheduler
                        layers={layers}
                    />

                    {/* ---------------------------- */}
                    {/* Shared Runtime Children */}
                    {/* ---------------------------- */}

                    {children}

                    {/* ---------------------------- */}
                    {/* Shared Controls */}
                    {/* ---------------------------- */}

                    <OrbitControls

                        enableDamping

                        dampingFactor={0.08}

                        rotateSpeed={0.7}

                        zoomSpeed={0.7}
                    />

                </Canvas>

                {/* -------------------------------- */}
                {/* Runtime Spatial HUD */}
                {/* -------------------------------- */}

                <div
                    className="
                        absolute
                        top-4
                        left-4
                        flex
                        flex-col
                        gap-2
                        text-[10px]
                        font-mono
                        z-50
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
                        shared runtime world space
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
                        runtime layers:
                        {" "}
                        {
                            layers.length
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
                            authority.state
                                .authorityLocked

                                ? "LOCKED"

                                : "UNLOCKED"
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

                </div>

                {/* -------------------------------- */}
                {/* Shared Runtime Clock Inspector */}
                {/* -------------------------------- */}

                <div
                    className="
                        absolute
                        bottom-4
                        left-4
                        w-[320px]
                        rounded-2xl
                        border
                        border-neutral-800
                        bg-black/80
                        backdrop-blur-xl
                        overflow-hidden
                        z-50
                    "
                >

                    <div
                        className="
                            px-4
                            py-3
                            border-b
                            border-neutral-800
                            text-sm
                            font-semibold
                            text-cyan-300
                        "
                    >
                        Runtime Spatial Clock
                    </div>

                    <div
                        className="
                            p-4
                            flex
                            flex-col
                            gap-3
                            text-[10px]
                            font-mono
                        "
                    >

                        <div>
                            elapsed:
                            {" "}
                            {
                                clock.elapsed
                                    .toFixed(3)
                            }
                        </div>

                        <div>
                            delta:
                            {" "}
                            {
                                clock.delta
                                    .toFixed(5)
                            }
                        </div>

                        <div>
                            replayTime:
                            {" "}
                            {
                                clock.replayTime
                                    .toFixed(3)
                            }
                        </div>

                        <div>
                            transportTime:
                            {" "}
                            {
                                clock.transportTime
                                    .toFixed(3)
                            }
                        </div>

                        <div>
                            synchronizationTime:
                            {" "}
                            {
                                clock
                                    .synchronizationTime
                                    .toFixed(3)
                            }
                        </div>

                    </div>

                </div>

                {/* -------------------------------- */}
                {/* Runtime Selection Inspector */}
                {/* -------------------------------- */}

                {
                    selectedObject && (

                        <div
                            className="
                                absolute
                                bottom-4
                                right-4
                                w-[360px]
                                rounded-2xl
                                border
                                border-neutral-800
                                bg-black/80
                                backdrop-blur-xl
                                overflow-hidden
                                z-50
                            "
                        >

                            <div
                                className="
                                    px-4
                                    py-3
                                    border-b
                                    border-neutral-800
                                    text-sm
                                    font-semibold
                                    text-cyan-300
                                "
                            >
                                Runtime Selection
                            </div>

                            <div
                                className="
                                    p-4
                                    flex
                                    flex-col
                                    gap-3
                                    text-[10px]
                                    font-mono
                                "
                            >

                                <div>
                                    id:
                                    {" "}
                                    {
                                        selectedObject.id
                                    }
                                </div>

                                <div>
                                    source:
                                    {" "}
                                    {
                                        selectedObject.source
                                    }
                                </div>

                                <div>
                                    type:
                                    {" "}
                                    {
                                        selectedObject.type
                                    }
                                </div>

                            </div>

                        </div>
                    )
                }

                {/* -------------------------------- */}
                {/* Runtime Telemetry */}
                {/* -------------------------------- */}

                {
                    telemetry && (

                        <div
                            className="
                                absolute
                                top-4
                                right-4
                                w-[280px]
                                rounded-2xl
                                border
                                border-neutral-800
                                bg-black/80
                                backdrop-blur-xl
                                overflow-hidden
                                z-50
                            "
                        >

                            <div
                                className="
                                    px-4
                                    py-3
                                    border-b
                                    border-neutral-800
                                    text-sm
                                    font-semibold
                                    text-cyan-300
                                >
                                    Runtime Telemetry
                                </div>

                            <div
                                className="
                                    p-4
                                    flex
                                    flex-col
                                    gap-3
                                    text-[10px]
                                    font-mono
                                "
                            >

                                <div>
                                    runtimeFps:
                                    {" "}
                                    {
                                        telemetry.runtimeFps ??
                                        "n/a"
                                    }
                                </div>

                                <div>
                                    replayDepth:
                                    {" "}
                                    {
                                        telemetry.replayDepth ??
                                        "n/a"
                                    }
                                </div>

                                <div>
                                    receiptCount:
                                    {" "}
                                    {
                                        telemetry.receiptCount ??
                                        "n/a"
                                    }
                                </div>

                                <div>
                                    activeGraphs:
                                    {" "}
                                    {
                                        telemetry.activeGraphs ??
                                        "n/a"
                                    }
                                </div>

                                <div>
                                    activeWindows:
                                    {" "}
                                    {
                                        telemetry.activeWindows ??
                                        "n/a"
                                    }
                                </div>

                            </div>

                        </div>
                    )
                }

            </div>

        </RuntimeSpatialContext.Provider>
    )
}