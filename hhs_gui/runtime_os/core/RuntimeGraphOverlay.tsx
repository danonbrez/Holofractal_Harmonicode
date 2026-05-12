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
    Html
} from "@react-three/drei"

import {
    RuntimeKernelBridge
} from "./RuntimeKernelBridge"

/**
 * HHS Runtime Graph Overlay
 * ---------------------------------------------------
 * Canonical Runtime OS graph-overlay manifold.
 *
 * Responsibilities:
 *
 * - Runtime graph visualization
 * - Receipt-chain projection
 * - Runtime transport topology
 * - Replay graph continuity
 * - Live runtime graph synchronization
 * - Runtime execution path rendering
 * - Graph-linked telemetry overlays
 * - Deterministic runtime state projection
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeGraphOverlayProps {

    kernelBridge: RuntimeKernelBridge
}

interface RuntimeGraphNode {

    id: string

    position: [number, number, number]

    color: string

    label: string

    scale: number
}

interface RuntimeGraphEdge {

    id: string

    source: [number, number, number]

    target: [number, number, number]

    color: string
}

/**
 * ---------------------------------------------------
 * Runtime Graph Nodes
 * ---------------------------------------------------
 */

const RuntimeGraphNodes: React.FC<{

    nodes: RuntimeGraphNode[]

}> = ({ nodes }) => {

    const groupRef =
        useRef<THREE.Group>(null)

    useFrame((state) => {

        if (!groupRef.current) {

            return
        }

        groupRef.current.rotation.y += 0.0005

        groupRef.current.position.y =

            Math.sin(
                state.clock.elapsedTime * 0.4
            ) * 0.1
    })

    return (

        <group ref={groupRef}>

            {
                nodes.map((node) => (

                    <group
                        key={node.id}
                        position={node.position}
                    >

                        {/* ---------------- */}
                        {/* Graph Node */}
                        {/* ---------------- */}

                        <mesh>

                            <icosahedronGeometry
                                args={[
                                    node.scale,
                                    1
                                ]}
                            />

                            <meshStandardMaterial

                                color={node.color}

                                emissive={node.color}

                                emissiveIntensity={0.8}
                            />

                        </mesh>

                        {/* ---------------- */}
                        {/* Node Label */}
                        {/* ---------------- */}

                        <Html
                            distanceFactor={12}
                        >

                            <div
                                className="
                                    px-2
                                    py-1
                                    rounded-lg
                                    bg-black/70
                                    border
                                    border-neutral-700
                                    text-[10px]
                                    font-mono
                                    whitespace-nowrap
                                    text-cyan-200
                                "
                            >
                                {node.label}
                            </div>

                        </Html>

                    </group>
                ))
            }

        </group>
    )
}

/**
 * ---------------------------------------------------
 * Runtime Graph Edges
 * ---------------------------------------------------
 */

const RuntimeGraphEdges: React.FC<{

    edges: RuntimeGraphEdge[]

}> = ({ edges }) => {

    return (

        <group>

            {
                edges.map((edge) => (

                    <Line

                        key={edge.id}

                        points={[

                            edge.source,

                            edge.target
                        ]}

                        color={edge.color}

                        lineWidth={1.5}

                        transparent

                        opacity={0.45}
                    />
                ))
            }

        </group>
    )
}

/**
 * ---------------------------------------------------
 * Runtime Graph Overlay
 * ---------------------------------------------------
 */

export const RuntimeGraphOverlay:
React.FC<
    RuntimeGraphOverlayProps
> = ({
    kernelBridge
}) => {

    const [receiptCount, setReceiptCount] =
        useState(0)

    const [telemetry, setTelemetry] =
        useState<any>(null)

    /**
     * ---------------------------------------------------
     * Runtime Event Subscription
     * ---------------------------------------------------
     */

    useEffect(() => {

        const receiptHandler = () => {

            setReceiptCount(

                (previous) =>
                    previous + 1
            )
        }

        const telemetryHandler = (
            payload: any
        ) => {

            setTelemetry(payload)
        }

        kernelBridge.on(
            "receipt",
            receiptHandler
        )

        kernelBridge.on(
            "telemetry",
            telemetryHandler
        )

        return () => {

            kernelBridge.off(
                "receipt",
                receiptHandler
            )

            kernelBridge.off(
                "telemetry",
                telemetryHandler
            )
        }

    }, [kernelBridge])

    /**
     * ---------------------------------------------------
     * Graph Nodes
     * ---------------------------------------------------
     */

    const nodes =
        useMemo<
            RuntimeGraphNode[]
        >(() => {

            const graphNodes:
                RuntimeGraphNode[] = []

            for (let i = 0; i < 24; i++) {

                const angle =

                    (Math.PI * 2 * i) / 24

                const radius =
                    8 + (i % 3)

                graphNodes.push({

                    id:
                        `graph-node-${i}`,

                    position: [

                        Math.cos(angle) * radius,

                        Math.sin(angle * 2) * 2,

                        Math.sin(angle) * radius
                    ],

                    color:

                        i % 4 === 0
                            ? "#22d3ee"

                        : i % 4 === 1
                            ? "#4ade80"

                        : i % 4 === 2
                            ? "#c084fc"

                        : "#f59e0b",

                    label:
                        `RUNTIME_${i}`,

                    scale:
                        0.22 + (i % 4) * 0.04
                })
            }

            return graphNodes

        }, [])

    /**
     * ---------------------------------------------------
     * Graph Edges
     * ---------------------------------------------------
     */

    const edges =
        useMemo<
            RuntimeGraphEdge[]
        >(() => {

            const graphEdges:
                RuntimeGraphEdge[] = []

            for (
                let i = 0;
                i < nodes.length;
                i++
            ) {

                const source =
                    nodes[i]

                const target =
                    nodes[
                        (i + 1) % nodes.length
                    ]

                graphEdges.push({

                    id:
                        `edge-${i}`,

                    source:
                        source.position,

                    target:
                        target.position,

                    color:
                        "#22d3ee"
                })
            }

            return graphEdges

        }, [nodes])

    /**
     * ---------------------------------------------------
     * Runtime Graph Overlay
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                absolute
                inset-0
                pointer-events-none
            "
        >

            {/* -------------------------------- */}
            {/* Graph Canvas */}
            {/* -------------------------------- */}

            <Canvas

                camera={{

                    position: [0, 0, 20],

                    fov: 50
                }}

                gl={{

                    alpha: true,

                    antialias: true
                }}
            >

                <ambientLight intensity={0.8} />

                <pointLight

                    position={[10, 10, 10]}

                    intensity={1.5}
                />

                <RuntimeGraphEdges
                    edges={edges}
                />

                <RuntimeGraphNodes
                    nodes={nodes}
                />

            </Canvas>

            {/* -------------------------------- */}
            {/* Runtime Telemetry Overlay */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    top-4
                    right-4
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
                        bg-black/70
                        border
                        border-neutral-800
                        backdrop-blur-xl
                    "
                >
                    receipts:
                    {" "}
                    {receiptCount}
                </div>

                <div
                    className="
                        px-3
                        py-2
                        rounded-xl
                        bg-black/70
                        border
                        border-neutral-800
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

                {
                    telemetry && (

                        <div
                            className="
                                px-3
                                py-2
                                rounded-xl
                                bg-black/70
                                border
                                border-neutral-800
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
                                graphs:
                                {" "}
                                {
                                    telemetry.activeGraphs
                                }
                            </div>

                            <div>
                                replay:
                                {" "}
                                {
                                    telemetry.replayDepth
                                }
                            </div>

                        </div>
                    )
                }

            </div>

        </div>
    )
}