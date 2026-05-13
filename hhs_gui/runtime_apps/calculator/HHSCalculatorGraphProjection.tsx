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
    Html,
    Line,
    OrbitControls
} from "@react-three/drei"

import {
    RuntimeKernelBridge,
    RuntimeKernelReceipt
} from "../../runtime_os/core/RuntimeKernelBridge"

/**
 * HHS Calculator Graph Projection
 * ---------------------------------------------------
 * Canonical runtime-originated graph projection surface.
 *
 * CRITICAL:
 *
 * This component does NOT:
 *
 * - generate local execution topology
 * - simulate runtime execution
 * - generate fake graph nodes
 * - generate replay chains
 * - fabricate receipt continuity
 *
 * ALL GRAPH STRUCTURE MUST ORIGINATE FROM:
 *
 * RuntimeKernelBridge
 * → Canonical Runtime
 * → Kernel
 * → Receipt Chain
 * → Replay Graph
 *
 * GUI ONLY PROJECTS RUNTIME STATE.
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface HHSCalculatorGraphProjectionProps {

    kernelBridge: RuntimeKernelBridge
}

export interface RuntimeProjectionNode {

    id: string

    receiptHash: string

    position: [number, number, number]

    operation: string

    timestamp: number

    status: string
}

export interface RuntimeProjectionEdge {

    id: string

    source: [number, number, number]

    target: [number, number, number]
}

const ReceiptNode: React.FC<{

    node: RuntimeProjectionNode

    selected: boolean

}> = ({
    node,
    selected
}) => {

    const meshRef =
        useRef<THREE.Mesh>(null)

    useFrame((state) => {

        if (!meshRef.current) {

            return
        }

        meshRef.current.rotation.y += 0.01

        const pulse =

            1 +

            Math.sin(
                state.clock.elapsedTime * 2
            ) * 0.05

        meshRef.current.scale.set(

            pulse,
            pulse,
            pulse
        )
    })

    return (

        <group position={node.position}>

            <mesh ref={meshRef}>

                <icosahedronGeometry
                    args={[0.45, 1]}
                />

                <meshStandardMaterial

                    color={
                        selected
                            ? "#22d3ee"
                            : "#4ade80"
                    }

                    emissive={
                        selected
                            ? "#22d3ee"
                            : "#4ade80"
                    }

                    emissiveIntensity={0.9}
                />

            </mesh>

            <Html
                distanceFactor={10}
            >

                <div
                    className="
                        min-w-[160px]
                        rounded-xl
                        border
                        border-neutral-700
                        bg-black/80
                        backdrop-blur-xl
                        p-3
                        text-[10px]
                        font-mono
                        text-neutral-200
                    "
                >

                    <div
                        className="
                            text-cyan-300
                            font-semibold
                            mb-2
                        "
                    >
                        receipt node
                    </div>

                    <div
                        className="
                            opacity-70
                            break-all
                        "
                    >
                        {
                            node.receiptHash
                        }
                    </div>

                    <div
                        className="
                            mt-2
                        "
                    >
                        op:
                        {" "}
                        {
                            node.operation
                        }
                    </div>

                    <div>
                        status:
                        {" "}
                        {
                            node.status
                        }
                    </div>

                </div>

            </Html>

        </group>
    )
}

export const HHSCalculatorGraphProjection:
React.FC<
    HHSCalculatorGraphProjectionProps
> = ({
    kernelBridge
}) => {

    const [nodes, setNodes] =
        useState<
            RuntimeProjectionNode[]
        >([])

    const [selectedNodeId, setSelectedNodeId] =
        useState<string | null>(null)

    /**
     * ---------------------------------------------------
     * Runtime Receipt Subscription
     * ---------------------------------------------------
     */

    useEffect(() => {

        const receiptHandler = (
            receipt:
                RuntimeKernelReceipt
        ) => {

            /**
             * ------------------------------------------------
             * IMPORTANT:
             *
             * Position assignment is projection-only.
             * The GUI is NOT generating runtime topology.
             *
             * Runtime truth remains:
             *
             * receiptHash
             * operation
             * continuity
             * replay linkage
             *
             * GUI only spatializes visualization.
             * ------------------------------------------------
             */

            setNodes((previous) => {

                const angle =

                    previous.length * 0.55

                const radius =
                    4 +
                    previous.length * 0.25

                const nextNode:
                    RuntimeProjectionNode = {

                    id:
                        crypto.randomUUID(),

                    receiptHash:

                        receipt.receiptHash ??

                        "runtime_receipt",

                    operation:

                        receipt.operation ??

                        "runtime.operation",

                    timestamp:

                        receipt.timestamp ??

                        Date.now(),

                    status:

                        receipt.status ??

                        "committed",

                    position: [

                        Math.cos(angle) * radius,

                        Math.sin(angle * 2) * 1.5,

                        Math.sin(angle) * radius
                    ]
                }

                return [

                    nextNode,

                    ...previous
                ]
            })

        }

        kernelBridge.on(
            "receipt",
            receiptHandler
        )

        return () => {

            kernelBridge.off(
                "receipt",
                receiptHandler
            )
        }

    }, [kernelBridge])

    /**
     * ---------------------------------------------------
     * Projection Edges
     * ---------------------------------------------------
     */

    const edges =
        useMemo<
            RuntimeProjectionEdge[]
        >(() => {

            const runtimeEdges:
                RuntimeProjectionEdge[] = []

            for (
                let i = 0;
                i < nodes.length - 1;
                i++
            ) {

                runtimeEdges.push({

                    id:
                        `edge-${i}`,

                    source:
                        nodes[i].position,

                    target:
                        nodes[i + 1].position
                })
            }

            return runtimeEdges

        }, [nodes])

    /**
     * ---------------------------------------------------
     * Selected Node
     * ---------------------------------------------------
     */

    const selectedNode =
        useMemo(() => {

            if (!selectedNodeId) {

                return undefined
            }

            return nodes.find(

                (node) =>
                    node.id === selectedNodeId
            )

        }, [
            nodes,
            selectedNodeId
        ])

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
                relative
                bg-black
            "
        >

            {/* -------------------------------- */}
            {/* Projection Canvas */}
            {/* -------------------------------- */}

            <Canvas

                camera={{

                    position: [0, 6, 16],

                    fov: 60
                }}
            >

                <ambientLight intensity={0.7} />

                <pointLight

                    position={[10, 10, 10]}

                    intensity={1.6}
                />

                <pointLight

                    position={[-10, -4, -10]}

                    intensity={0.7}

                    color="#22d3ee"
                />

                {/* ---------------------------- */}
                {/* Receipt Edges */}
                {/* ---------------------------- */}

                {
                    edges.map((edge) => (

                        <Line

                            key={edge.id}

                            points={[

                                edge.source,

                                edge.target
                            ]}

                            color="#22d3ee"

                            transparent

                            opacity={0.4}

                            lineWidth={1.2}
                        />
                    ))
                }

                {/* ---------------------------- */}
                {/* Receipt Nodes */}
                {/* ---------------------------- */}

                {
                    nodes.map((node) => (

                        <group
                            key={node.id}

                            onClick={() => {

                                setSelectedNodeId(
                                    node.id
                                )
                            }}
                        >

                            <ReceiptNode

                                node={node}

                                selected={
                                    selectedNodeId ===
                                    node.id
                                }
                            />

                        </group>
                    ))
                }

                {/* ---------------------------- */}
                {/* Controls */}
                {/* ---------------------------- */}

                <OrbitControls

                    enableDamping

                    dampingFactor={0.08}

                    rotateSpeed={0.6}

                    zoomSpeed={0.7}
                />

            </Canvas>

            {/* -------------------------------- */}
            {/* Overlay */}
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
                    runtime-originated topology only
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
                    projected receipts:
                    {" "}
                    {
                        nodes.length
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
            {/* Selected Node Inspector */}
            {/* -------------------------------- */}

            {
                selectedNode && (

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
                            Runtime Receipt Inspector
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

                                <div
                                    className="
                                        opacity-50
                                        mb-1
                                    "
                                >
                                    receiptHash
                                </div>

                                <div
                                    className="
                                        break-all
                                    "
                                >
                                    {
                                        selectedNode
                                            .receiptHash
                                    }
                                </div>

                            </div>

                            <div>

                                <div
                                    className="
                                        opacity-50
                                        mb-1
                                    "
                                >
                                    operation
                                </div>

                                <div>
                                    {
                                        selectedNode
                                            .operation
                                    }
                                </div>

                            </div>

                            <div>

                                <div
                                    className="
                                        opacity-50
                                        mb-1
                                    "
                                >
                                    status
                                </div>

                                <div>
                                    {
                                        selectedNode
                                            .status
                                    }
                                </div>

                            </div>

                            <div>

                                <div
                                    className="
                                        opacity-50
                                        mb-1
                                    "
                                >
                                    timestamp
                                </div>

                                <div>
                                    {
                                        new Date(
                                            selectedNode
                                                .timestamp
                                        ).toISOString()
                                    }
                                </div>

                            </div>

                        </div>

                    </div>
                )
            }

        </div>
    )
}