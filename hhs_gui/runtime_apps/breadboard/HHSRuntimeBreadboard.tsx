import React from "react"

// =========================================================
// Types
// =========================================================

export interface HHSRuntimeBreadboardProps {

    className?: string
}

// =========================================================
// HHSRuntimeBreadboard
// =========================================================

export const HHSRuntimeBreadboard: React.FC<
    HHSRuntimeBreadboardProps
> = ({
    className
}) => {

    return (

        <div
            className={

                `
                w-full
                h-full
                bg-neutral-950
                text-cyan-400
                overflow-hidden
                relative
                ${className ?? ""}
                `
            }
        >

            {/* =====================================================
                Grid Background
            ====================================================== */}

            <div
                className="
                    absolute
                    inset-0
                    opacity-20
                "
                style={{
                    backgroundImage: `
                        linear-gradient(
                            to right,
                            rgba(34,211,238,0.08) 1px,
                            transparent 1px
                        ),
                        linear-gradient(
                            to bottom,
                            rgba(34,211,238,0.08) 1px,
                            transparent 1px
                        )
                    `,
                    backgroundSize: "32px 32px"
                }}
            />

            {/* =====================================================
                Header
            ====================================================== */}

            <div
                className="
                    absolute
                    top-0
                    left-0
                    right-0
                    z-10
                    border-b
                    border-cyan-950
                    bg-black/70
                    backdrop-blur-md
                    px-4
                    py-3
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
                            font-semibold
                            text-sm
                            tracking-wide
                        "
                    >
                        HHS Runtime Breadboard
                    </div>

                    <div
                        className="
                            text-cyan-700
                            text-xs
                            font-mono
                        "
                    >
                        runtime_transport_projection_surface
                    </div>

                </div>

                <div
                    className="
                        text-[10px]
                        font-mono
                        text-cyan-600
                    "
                >
                    transport-ready
                </div>

            </div>

            {/* =====================================================
                Workspace
            ====================================================== */}

            <div
                className="
                    absolute
                    inset-0
                    pt-20
                    p-6
                    overflow-auto
                "
            >

                <div
                    className="
                        w-full
                        h-full
                        min-h-[600px]
                        rounded-2xl
                        border
                        border-cyan-950
                        bg-black/40
                        backdrop-blur-sm
                        relative
                        overflow-hidden
                    "
                >

                    {/* =============================================
                        Node Cluster
                    ============================================== */}

                    <div
                        className="
                            absolute
                            left-16
                            top-16
                            flex
                            flex-col
                            gap-8
                        "
                    >

                        <BreadboardNode
                            title="Runtime"
                            state="online"
                        />

                        <BreadboardNode
                            title="Replay"
                            state="pending"
                        />

                        <BreadboardNode
                            title="Graph"
                            state="pending"
                        />

                    </div>

                    {/* =============================================
                        Connection Layer
                    ============================================== */}

                    <svg
                        className="
                            absolute
                            inset-0
                            w-full
                            h-full
                            pointer-events-none
                        "
                    >

                        <line
                            x1="180"
                            y1="90"
                            x2="340"
                            y2="180"
                            stroke="rgba(34,211,238,0.4)"
                            strokeWidth="2"
                        />

                        <line
                            x1="180"
                            y1="210"
                            x2="340"
                            y2="180"
                            stroke="rgba(34,211,238,0.2)"
                            strokeWidth="2"
                        />

                    </svg>

                    {/* =============================================
                        Central Transport Core
                    ============================================== */}

                    <div
                        className="
                            absolute
                            left-1/2
                            top-1/2
                            -translate-x-1/2
                            -translate-y-1/2
                            w-48
                            h-48
                            rounded-full
                            border
                            border-cyan-500/40
                            bg-cyan-500/5
                            flex
                            items-center
                            justify-center
                            backdrop-blur-md
                            shadow-[0_0_60px_rgba(34,211,238,0.15)]
                        "
                    >

                        <div
                            className="
                                flex
                                flex-col
                                items-center
                                gap-2
                            "
                        >

                            <div
                                className="
                                    text-cyan-300
                                    text-sm
                                    font-semibold
                                "
                            >
                                Runtime Transport
                            </div>

                            <div
                                className="
                                    text-cyan-700
                                    text-[10px]
                                    font-mono
                                "
                            >
                                websocket_projection
                            </div>

                        </div>

                    </div>

                </div>

            </div>

        </div>
    )
}

// =========================================================
// Breadboard Node
// =========================================================

interface BreadboardNodeProps {

    title: string

    state: "online" | "pending" | "offline"
}

const BreadboardNode: React.FC<
    BreadboardNodeProps
> = ({
    title,
    state
}) => {

    const stateColor = (() => {

        switch (state) {

            case "online":
                return "bg-emerald-500"

            case "pending":
                return "bg-yellow-500"

            case "offline":
                return "bg-red-500"

            default:
                return "bg-neutral-500"
        }
    })()

    return (

        <div
            className="
                w-40
                rounded-xl
                border
                border-cyan-950
                bg-black/70
                backdrop-blur-sm
                px-4
                py-3
                flex
                items-center
                justify-between
            "
        >

            <div
                className="
                    text-cyan-300
                    text-sm
                    font-medium
                "
            >
                {title}
            </div>

            <div
                className={`
                    w-3
                    h-3
                    rounded-full
                    ${stateColor}
                `}
            />

        </div>
    )
}

// =========================================================
// Default Export
// =========================================================

export default HHSRuntimeBreadboard