import React, {
    useEffect,
    useMemo,
    useState
} from "react"

// =========================================================
// Types
// =========================================================

interface RuntimeGraphNode {

    id: string

    parent?: string

    runtime_id?: string

    branch_id?: string

    receipt_hash72?: string

    event_type?: string

    timestamp_ns?: number
}

// =========================================================
// Projection Node
// =========================================================

interface ProjectionNodeProps {

    node: RuntimeGraphNode

    active?: boolean
}

// =========================================================
// RuntimeGraphProjection
// =========================================================

export const HHSCalculatorGraphProjection:
React.FC = () => {

    // =====================================================
    // State
    // =====================================================

    const [

        graphNodes,

        setGraphNodes

    ] = useState<
        RuntimeGraphNode[]
    >([])

    const [

        loading,

        setLoading

    ] = useState(true)

    const [

        error,

        setError

    ] = useState<
        string | null
    >(null)

    // =====================================================
    // Runtime Endpoint
    // =====================================================

    const endpoint =
        useMemo(() => {

            return (

                `${window.location.origin}`

                +

                `/api/runtime/graph`
            )

        }, [])

    // =====================================================
    // Poll Graph
    // =====================================================

    useEffect(() => {

        let mounted = true

        let interval:
            number | undefined

        const pollGraph =
            async () => {

                try {

                    const response =
                        await fetch(
                            endpoint
                        )

                    if (
                        !response.ok
                    ) {

                        throw new Error(

                            `Graph request failed (${response.status})`
                        )
                    }

                    const json =
                        await response.json()

                    if (!mounted) {

                        return
                    }

                    // -------------------------------------------------
                    // Placeholder Graph Projection
                    // -------------------------------------------------

                    // Replace with:
                    //   RuntimeStateStore projection
                    //   live websocket graph stream
                    //   replay lineage
                    //   runtime topology engine

                    const nodes =
                        Array.isArray(
                            json.nodes
                        )

                            ? json.nodes

                            : []

                    setGraphNodes(nodes)

                    setLoading(false)

                    setError(null)

                } catch (error) {

                    console.error(

                        "[HHSCalculatorGraphProjection] graph projection failure",

                        error
                    )

                    if (!mounted) {

                        return
                    }

                    setLoading(false)

                    setError(

                        error instanceof Error

                            ? error.message

                            : "Graph projection failure"
                    )
                }
            }

        pollGraph()

        interval = window.setInterval(

            pollGraph,

            2000
        )

        return () => {

            mounted = false

            if (interval) {

                window.clearInterval(
                    interval
                )
            }
        }

    }, [endpoint])

    // =====================================================
    // Render
    // =====================================================

    return (

        <div
            className="
                w-full
                h-full
                bg-black
                text-white
                overflow-hidden
                flex
                flex-col
            "
        >

            {/* =================================================
                Header
            ================================================== */}

            <div
                className="
                    border-b
                    border-neutral-800
                    px-4
                    py-3
                    bg-black/70
                    backdrop-blur-md
                    flex
                    items-center
                    justify-between
                "
            >

                <div
                    className="
                        flex
                        flex-col
                    "
                >

                    <div
                        className="
                            text-cyan-300
                            text-sm
                            font-semibold
                        "
                    >
                        Runtime Graph Projection
                    </div>

                    <div
                        className="
                            text-neutral-500
                            text-[10px]
                            font-mono
                        "
                    >
                        replay_transport_projection
                    </div>

                </div>

                <div
                    className="
                        text-[10px]
                        font-mono
                        text-cyan-700
                    "
                >

                    {
                        loading

                            ? "loading"

                            : "online"
                    }

                </div>

            </div>

            {/* =================================================
                Error
            ================================================== */}

            {
                error && (

                    <div
                        className="
                            m-4
                            rounded-xl
                            border
                            border-red-900
                            bg-red-950/40
                            p-4
                            text-red-300
                            text-sm
                            font-mono
                        "
                    >

                        {error}

                    </div>
                )
            }

            {/* =================================================
                Projection Workspace
            ================================================== */}

            <div
                className="
                    flex-1
                    relative
                    overflow-hidden
                "
            >

                {/* =============================================
                    Grid
                ============================================== */}

                <div
                    className="
                        absolute
                        inset-0
                        opacity-10
                    "
                    style={{
                        backgroundImage: `
                            linear-gradient(
                                to right,
                                rgba(34,211,238,0.1) 1px,
                                transparent 1px
                            ),
                            linear-gradient(
                                to bottom,
                                rgba(34,211,238,0.1) 1px,
                                transparent 1px
                            )
                        `,
                        backgroundSize:
                            "28px 28px"
                    }}
                />

                {/* =============================================
                    Projection
                ============================================== */}

                <div
                    className="
                        absolute
                        inset-0
                        p-6
                        overflow-auto
                    "
                >

                    {
                        graphNodes.length
                        === 0

                            ? (

                                <div
                                    className="
                                        w-full
                                        h-full
                                        flex
                                        items-center
                                        justify-center
                                        text-neutral-600
                                        font-mono
                                        text-sm
                                    "
                                >

                                    awaiting_runtime_projection

                                </div>
                            )

                            : (

                                <div
                                    className="
                                        flex
                                        flex-wrap
                                        gap-4
                                    "
                                >

                                    {
                                        graphNodes.map(

                                            (
                                                node,
                                                index
                                            ) => (

                                                <ProjectionNode
                                                    key={
                                                        node.id
                                                        ??
                                                        index
                                                    }
                                                    node={
                                                        node
                                                    }
                                                    active={
                                                        index
                                                        ===
                                                        graphNodes.length - 1
                                                    }
                                                />
                                            )
                                        )
                                    }

                                </div>
                            )
                    }

                </div>

            </div>

        </div>
    )
}

// =========================================================
// Projection Node
// =========================================================

const ProjectionNode: React.FC<
    ProjectionNodeProps
> = ({
    node,
    active
}) => {

    return (

        <div
            className={`
                w-56
                rounded-2xl
                border
                backdrop-blur-md
                p-4
                flex
                flex-col
                gap-2
                transition-all
                ${
                    active

                        ? `
                            border-cyan-500/50
                            bg-cyan-500/10
                            shadow-[0_0_40px_rgba(34,211,238,0.15)]
                        `

                        : `
                            border-neutral-800
                            bg-neutral-950/80
                        `
                }
            `}
        >

            {/* =============================================
                Header
            ============================================== */}

            <div
                className="
                    flex
                    items-center
                    justify-between
                "
            >

                <div
                    className="
                        text-cyan-300
                        text-xs
                        font-semibold
                    "
                >
                    {
                        node.event_type
                        ??
                        "runtime"
                    }
                </div>

                <div
                    className="
                        text-[10px]
                        font-mono
                        text-neutral-500
                    "
                >
                    active
                </div>

            </div>

            {/* =============================================
                Event Hash
            ============================================== */}

            <div
                className="
                    flex
                    flex-col
                    gap-1
                "
            >

                <div
                    className="
                        text-[10px]
                        uppercase
                        tracking-wide
                        text-neutral-600
                    "
                >
                    event_hash72
                </div>

                <div
                    className="
                        text-[10px]
                        font-mono
                        break-all
                        text-cyan-400
                    "
                >
                    {
                        node.id
                        ??
                        "pending"
                    }
                </div>

            </div>

            {/* =============================================
                Parent
            ============================================== */}

            {
                node.parent && (

                    <div
                        className="
                            flex
                            flex-col
                            gap-1
                        "
                    >

                        <div
                            className="
                                text-[10px]
                                uppercase
                                tracking-wide
                                text-neutral-600
                            "
                        >
                            parent
                        </div>

                        <div
                            className="
                                text-[10px]
                                font-mono
                                break-all
                                text-neutral-400
                            "
                        >
                            {node.parent}
                        </div>

                    </div>
                )
            }

            {/* =============================================
                Receipt
            ============================================== */}

            {
                node.receipt_hash72 && (

                    <div
                        className="
                            flex
                            flex-col
                            gap-1
                        "
                    >

                        <div
                            className="
                                text-[10px]
                                uppercase
                                tracking-wide
                                text-neutral-600
                            "
                        >
                            receipt_hash72
                        </div>

                        <div
                            className="
                                text-[10px]
                                font-mono
                                break-all
                                text-emerald-400
                            "
                        >
                            {
                                node.receipt_hash72
                            }
                        </div>

                    </div>
                )
            }

        </div>
    )
}

// =========================================================
// Default Export
// =========================================================

export default HHSCalculatorGraphProjection