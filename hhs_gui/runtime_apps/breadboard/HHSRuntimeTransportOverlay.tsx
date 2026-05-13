import React, {
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
    Line,
    OrbitControls
} from "@react-three/drei"

import {
    RuntimeKernelBridge
} from "../../runtime_os/core/RuntimeKernelBridge"

/**
 * HHS Runtime Transport Overlay
 * ---------------------------------------------------
 * Runtime-authorized transport visualization manifold.
 *
 * CRITICAL:
 *
 * GUI DOES NOT:
 *
 * - compute transport locally
 * - infer replay propagation
 * - simulate execution flow
 * - generate synchronization state
 * - generate runtime topology
 *
 * GUI ONLY PROJECTS:
 *
 * Runtime
 * → transport events
 * → replay traversal
 * → receipt propagation
 * → synchronization flow
 * → execution continuity
 *
 * into GPU-side spatial visualization.
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface HHSRuntimeTransportOverlayProps {

    kernelBridge: RuntimeKernelBridge
}

export interface RuntimeTransportVector {

    id: string

    source: [number, number, number]

    target: [number, number, number]

    transportType: string

    intensity: number

    timestamp: number
}

interface TransportPulseProps {

    vector: RuntimeTransportVector
}

const TransportPulse: React.FC<
    TransportPulseProps
> = ({
    vector
}) => {

    const meshRef =
        useRef<THREE.Mesh>(null)

    useFrame((state) => {

        if (!meshRef.current) {

            return
        }

        /**
         * ------------------------------------------------
         * Runtime-authorized pulse projection only.
         * ------------------------------------------------
         */

        const elapsed =
            state.clock.elapsedTime

        const t =
            (
                elapsed * 0.4 +

                (vector.timestamp / 1000)
            ) % 1

        const x =

            vector.source[0] +

            (
                vector.target[0] -
                vector.source[0]
            ) * t

        const y =

            vector.source[1] +

            (
                vector.target[1] -
                vector.source[1]
            ) * t

        const z =

            vector.source[2] +

            (
                vector.target[2] -
                vector.source[2]
            ) * t

        meshRef.current.position.set(
            x,
            y,
            z
        )

        const pulse =

            1 +

            Math.sin(
                elapsed * 6
            ) * 0.15

        meshRef.current.scale.set(
            pulse,
            pulse,
            pulse
        )
    })

    const color =

        vector.transportType ===
        "receipt"

            ? "#22d3ee"

        : vector.transportType ===
        "replay"

            ? "#c084fc"

        : vector.transportType ===
        "synchronization"

            ? "#4ade80"

        : "#f59e0b"

    return (

        <mesh ref={meshRef}>

            <sphereGeometry
                args={[0.12, 12, 12]}
            />

            <meshStandardMaterial

                color={color}

                emissive={color}

                emissiveIntensity={1.4}
            />

        </mesh>
    )
}

export const HHSRuntimeTransportOverlay:
React.FC<
    HHSRuntimeTransportOverlayProps
> = ({
    kernelBridge
}) => {

    const [vectors, setVectors] =
        useState<
            RuntimeTransportVector[]
        >([])

    const [telemetry, setTelemetry] =
        useState<any>(null)

    /**
     * ---------------------------------------------------
     * Runtime Event Subscription
     * ---------------------------------------------------
     */

    useEffect(() => {

        const runtimeEventHandler = (
            payload: any
        ) => {

            /**
             * IMPORTANT:
             *
             * Runtime provides transport truth.
             *
             * GUI spatializes only.
             */

            const runtimeVectors =

                payload?.transportVectors ??

                []

            const projectedVectors:
                RuntimeTransportVector[] =

                runtimeVectors.map(

                    (
                        vector: any,
                        index: number
                    ) => {

                        const angleA =
                            index * 0.5

                        const angleB =
                            index * 0.7

                        return {

                            id:
                                crypto.randomUUID(),

                            transportType:

                                vector.transportType ??

                                "receipt",

                            intensity:

                                vector.intensity ??
                                1,

                            timestamp:
                                Date.now(),

                            source: [

                                Math.cos(angleA) * 8,

                                Math.sin(angleA * 2) * 2,

                                Math.sin(angleA) * 8
                            ],

                            target: [

                                Math.cos(angleB) * 8,

                                Math.sin(angleB * 2) * 2,

                                Math.sin(angleB) * 8
                            ]
                        }
                    }
                )

            setVectors(projectedVectors)
        }

        const telemetryHandler = (
            payload: any
        ) => {

            setTelemetry(payload)
        }

        kernelBridge.on(
            "runtime_event",
            runtimeEventHandler
        )

        kernelBridge.on(
            "telemetry",
            telemetryHandler
        )

        return () => {

            kernelBridge.off(
                "runtime_event",
                runtimeEventHandler
            )

            kernelBridge.off(
                "telemetry",
                telemetryHandler
            )
        }

    }, [kernelBridge])

    /**
     * ---------------------------------------------------
     * Runtime Flux Lines
     * ---------------------------------------------------
     */

    const fluxLines =
        useMemo(() => {

            return vectors.map(

                (vector) => {

                    const color =

                        vector.transportType ===
                        "receipt"

                            ? "#22d3ee"

                        : vector.transportType ===
                        "replay"

                            ? "#c084fc"

                        : vector.transportType ===
                        "synchronization"

                            ? "#4ade80"

                        : "#f59e0b"

                    return (

                        <Line

                            key={vector.id}

                            points={[

                                vector.source,

                                vector.target
                            ]}

                            color={color}

                            transparent

                            opacity={0.35}

                            lineWidth={
                                vector.intensity * 1.5
                            }
                        />
                    )
                }
            )

        }, [vectors])

    /**
     * ---------------------------------------------------
     * Projection Surface
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-full
                h-full
                bg-black
                relative
            "
        >

            {/* -------------------------------- */}
            {/* GPU Transport Projection */}
            {/* -------------------------------- */}

            <Canvas

                camera={{

                    position: [0, 10, 18],

                    fov: 60
                }}
            >

                <ambientLight intensity={0.7} />

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
                {/* Runtime Flux Lines */}
                {/* ---------------------------- */}

                {fluxLines}

                {/* ---------------------------- */}
                {/* Runtime Pulses */}
                {/* ---------------------------- */}

                {
                    vectors.map((vector) => (

                        <TransportPulse

                            key={vector.id}

                            vector={vector}
                        />
                    ))
                }

                {/* ---------------------------- */}
                {/* Controls */}
                {/* ---------------------------- */}

                <OrbitControls

                    enableDamping

                    dampingFactor={0.08}

                    rotateSpeed={0.7}

                    zoomSpeed={0.7}
                />

            </Canvas>

            {/* -------------------------------- */}
            {/* Overlay HUD */}
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
                    runtime-authorized transport only
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
                    transport vectors:
                    {" "}
                    {vectors.length}
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
                    replay sync:
                    {" "}
                    {
                        kernelBridge.state
                            .replaySynchronized

                            ? "ACTIVE"

                            : "DESYNC"
                    }
                </div>

            </div>

            {/* -------------------------------- */}
            {/* Telemetry Inspector */}
            {/* -------------------------------- */}

            {
                telemetry && (

                    <div
                        className="
                            absolute
                            bottom-4
                            right-4
                            w-[320px]
                            rounded-2xl
                            border
                            border-neutral-800
                            bg-black/80
                            backdrop-blur-xl
                            overflow-hidden
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
                            Runtime Transport Telemetry
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
    )
}