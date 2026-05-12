import React, {
    useEffect,
    useMemo,
    useRef,
    useState
} from "react"

import {
    Canvas,
    useFrame
} from "@react-three/fiber"

import {
    OrbitControls,
    Grid
} from "@react-three/drei"

import * as THREE from "three"

import { RuntimeWorkspace } from "./RuntimeWorkspace"

/**
 * HHS Runtime Viewport
 * ---------------------------------------------------
 * GPU-native Runtime OS viewport root.
 *
 * Responsibilities:
 *
 * - Runtime manifold projection
 * - Graph-native visualization
 * - Runtime world rendering
 * - ECS projection
 * - Tensor visualization
 * - Replay overlays
 * - Transport flow rendering
 * - Runtime interaction surface
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeViewportProps {

    workspace: RuntimeWorkspace
}

export interface RuntimeViewportState {

    initialized: boolean

    rendering: boolean

    graphVisible: boolean

    tensorVisible: boolean

    replayVisible: boolean

    diagnosticsVisible: boolean
}

interface RuntimeGraphNode {

    id: string

    position: [number, number, number]

    scale: number

    color: string
}

/**
 * ---------------------------------------------------
 * Runtime Graph Field
 * ---------------------------------------------------
 */

const RuntimeGraphField: React.FC = () => {

    const groupRef =
        useRef<THREE.Group>(null)

    const nodes =
        useMemo<RuntimeGraphNode[]>(() => {

            const graphNodes: RuntimeGraphNode[] = []

            for (let i = 0; i < 81; i++) {

                const x =
                    (i % 9) * 2 - 8

                const z =
                    Math.floor(i / 9) * 2 - 8

                graphNodes.push({

                    id: `node-${i}`,

                    position: [x, 0, z],

                    scale:
                        0.35 + Math.random() * 0.2,

                    color:
                        i % 3 === 0
                            ? "#4ade80"
                            : i % 3 === 1
                                ? "#38bdf8"
                                : "#c084fc"
                })
            }

            return graphNodes

        }, [])

    useFrame((state) => {

        if (!groupRef.current) {

            return
        }

        groupRef.current.rotation.y += 0.0008

        groupRef.current.position.y =
            Math.sin(
                state.clock.elapsedTime * 0.25
            ) * 0.2
    })

    return (

        <group ref={groupRef}>

            {
                nodes.map((node) => (

                    <mesh
                        key={node.id}
                        position={node.position}
                    >

                        <sphereGeometry
                            args={[node.scale, 16, 16]}
                        />

                        <meshStandardMaterial
                            color={node.color}
                            emissive={node.color}
                            emissiveIntensity={0.5}
                        />

                    </mesh>
                ))
            }

        </group>
    )
}

/**
 * ---------------------------------------------------
 * Runtime Tensor Ring
 * ---------------------------------------------------
 */

const RuntimeTensorRing: React.FC = () => {

    const meshRef =
        useRef<THREE.Mesh>(null)

    useFrame((state) => {

        if (!meshRef.current) {

            return
        }

        meshRef.current.rotation.x += 0.002

        meshRef.current.rotation.y += 0.003

        meshRef.current.rotation.z += 0.001

        meshRef.current.scale.setScalar(

            1 +
            Math.sin(
                state.clock.elapsedTime
            ) * 0.05
        )
    })

    return (

        <mesh
            ref={meshRef}
            position={[0, 4, 0]}
        >

            <torusGeometry
                args={[6, 0.08, 32, 256]}
            />

            <meshStandardMaterial
                color="#60a5fa"
                emissive="#60a5fa"
                emissiveIntensity={1.2}
            />

        </mesh>
    )
}

/**
 * ---------------------------------------------------
 * Runtime Transport Lines
 * ---------------------------------------------------
 */

const RuntimeTransportLines: React.FC = () => {

    const lineGroup =
        useRef<THREE.Group>(null)

    useFrame((state) => {

        if (!lineGroup.current) {

            return
        }

        lineGroup.current.rotation.y -= 0.001

        lineGroup.current.position.y =
            Math.cos(
                state.clock.elapsedTime * 0.5
            ) * 0.15
    })

    const lines = []

    for (let i = 0; i < 24; i++) {

        const angle =
            (Math.PI * 2 * i) / 24

        const x =
            Math.cos(angle) * 9

        const z =
            Math.sin(angle) * 9

        lines.push(

            <line key={i}>

                <bufferGeometry>

                    <bufferAttribute
                        attach="attributes-position"
                        args={[
                            new Float32Array([

                                0, 0, 0,

                                x, 0, z
                            ]),
                            3
                        ]}
                    />

                </bufferGeometry>

                <lineBasicMaterial
                    color="#22d3ee"
                    transparent
                    opacity={0.35}
                />

            </line>
        )
    }

    return (

        <group ref={lineGroup}>

            {lines}

        </group>
    )
}

/**
 * ---------------------------------------------------
 * Runtime Viewport Component
 * ---------------------------------------------------
 */

export const RuntimeViewport: React.FC<
    RuntimeViewportProps
> = ({ workspace }) => {

    const [state, setState] =
        useState<RuntimeViewportState>({

            initialized: false,

            rendering: false,

            graphVisible: true,

            tensorVisible: true,

            replayVisible: true,

            diagnosticsVisible: false
        })

    useEffect(() => {

        console.log(
            "[RuntimeViewport] initialize"
        )

        setState((previous) => ({

            ...previous,

            initialized: true,

            rendering: true
        }))

    }, [])

    /**
     * ---------------------------------------------------
     * Runtime Overlay Metrics
     * ---------------------------------------------------
     */

    const metrics =
        workspace.getMetrics()

    /**
     * ---------------------------------------------------
     * Runtime Viewport
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
            {/* GPU Runtime Canvas */}
            {/* -------------------------------- */}

            <Canvas

                camera={{

                    position: [0, 12, 18],

                    fov: 60
                }}

                gl={{

                    antialias: true,

                    alpha: false
                }}
            >

                {/* -------------------------------- */}
                {/* Scene Lighting */}
                {/* -------------------------------- */}

                <ambientLight intensity={0.6} />

                <directionalLight

                    position={[12, 20, 8]}

                    intensity={1.5}
                />

                <pointLight

                    position={[-10, 8, -10]}

                    intensity={1.2}

                    color={"#38bdf8"}
                />

                {/* -------------------------------- */}
                {/* Runtime Grid */}
                {/* -------------------------------- */}

                <Grid

                    args={[200, 200]}

                    cellSize={1}

                    sectionSize={9}

                    fadeDistance={120}

                    fadeStrength={1}
                />

                {/* -------------------------------- */}
                {/* Runtime Projection Systems */}
                {/* -------------------------------- */}

                {
                    state.graphVisible && (

                        <RuntimeGraphField />
                    )
                }

                {
                    state.tensorVisible && (

                        <RuntimeTensorRing />
                    )
                }

                {
                    state.replayVisible && (

                        <RuntimeTransportLines />
                    )
                }

                {/* -------------------------------- */}
                {/* Camera Controls */}
                {/* -------------------------------- */}

                <OrbitControls

                    enableDamping

                    dampingFactor={0.08}

                    rotateSpeed={0.7}

                    zoomSpeed={0.8}

                    panSpeed={0.6}
                />

            </Canvas>

            {/* -------------------------------- */}
            {/* Runtime Overlay HUD */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    top-4
                    left-4
                    flex
                    flex-col
                    gap-2
                    text-xs
                    font-mono
                    pointer-events-none
                "
            >

                <div
                    className="
                        px-3
                        py-2
                        rounded-lg
                        bg-black/70
                        border
                        border-neutral-800
                        backdrop-blur-sm
                    "
                >
                    Runtime Viewport Active
                </div>

                <div
                    className="
                        px-3
                        py-2
                        rounded-lg
                        bg-black/70
                        border
                        border-neutral-800
                        backdrop-blur-sm
                    "
                >
                    windows:
                    {" "}
                    {
                        metrics.windows as number
                    }
                </div>

                <div
                    className="
                        px-3
                        py-2
                        rounded-lg
                        bg-black/70
                        border
                        border-neutral-800
                        backdrop-blur-sm
                    "
                >
                    overlays:
                    {" "}
                    {
                        metrics.overlays as number
                    }
                </div>

            </div>

            {/* -------------------------------- */}
            {/* Runtime Projection Label */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    bottom-4
                    right-4
                    px-4
                    py-2
                    rounded-xl
                    bg-black/70
                    border
                    border-neutral-800
                    backdrop-blur-sm
                    text-xs
                    font-mono
                    text-neutral-300
                "
            >
                HHS Runtime Projection Manifold
            </div>

        </div>
    )
}