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
    RuntimeDock
} from "./RuntimeDock"

export interface RuntimeShellProps {

    runtimeOS: RuntimeOS
}

export interface RuntimeShellState {

    bootComplete: boolean

    diagnosticsVisible: boolean
}

export const RuntimeShell: React.FC<
    RuntimeShellProps
> = ({ runtimeOS }) => {

    const [state, setState] =
        useState<RuntimeShellState>({

            bootComplete: false,

            diagnosticsVisible: false
        })

    /**
     * ---------------------------------------------------
     * Runtime Bootstrap
     * ---------------------------------------------------
     */

    useEffect(() => {

        let mounted = true

        const bootstrap =
            async () => {

            try {

                await runtimeOS
                    .initialize()

                if (!mounted) {

                    return
                }

                setState({

                    bootComplete: true,

                    diagnosticsVisible:
                        false
                })
            }
            catch (error) {

                console.error(
                    "[RuntimeShell] bootstrap failure",
                    error
                )
            }
        }

        bootstrap()

        return () => {

            mounted = false

            runtimeOS.shutdown()
        }

    }, [runtimeOS])

    /**
     * ---------------------------------------------------
     * Loading State
     * ---------------------------------------------------
     */

    if (!state.bootComplete) {

        return (

            <div
                className="
                    w-screen
                    h-screen
                    bg-black
                    text-cyan-400
                    flex
                    items-center
                    justify-center
                    font-mono
                    overflow-hidden
                    relative
                "
            >

                {/* -------------------------------- */}
                {/* Grid */}
                {/* -------------------------------- */}

                <div
                    className="
                        absolute
                        inset-0
                        opacity-[0.04]
                    "
                    style={{

                        backgroundImage:
                            `
                            linear-gradient(
                                rgba(255,255,255,0.08) 1px,
                                transparent 1px
                            ),
                            linear-gradient(
                                90deg,
                                rgba(255,255,255,0.08) 1px,
                                transparent 1px
                            )
                            `,

                        backgroundSize:
                            "32px 32px"
                    }}
                />

                {/* -------------------------------- */}
                {/* Boot Surface */}
                {/* -------------------------------- */}

                <div
                    className="
                        relative
                        z-10
                        flex
                        flex-col
                        items-center
                        gap-6
                    "
                >

                    <div
                        className="
                            text-3xl
                            font-bold
                            tracking-[0.25em]
                        "
                    >
                        HHS Runtime OS
                    </div>

                    <div
                        className="
                            text-sm
                            opacity-60
                            tracking-wide
                        "
                    >
                        deterministic manifold
                        bootstrap
                    </div>

                    <div
                        className="
                            w-72
                            h-[2px]
                            overflow-hidden
                            rounded-full
                            bg-neutral-800
                        "
                    >

                        <div
                            className="
                                h-full
                                w-1/2
                                bg-cyan-400
                                animate-pulse
                            "
                        />

                    </div>

                    <div
                        className="
                            text-xs
                            opacity-40
                            font-mono
                            flex
                            flex-col
                            items-center
                            gap-1
                        "
                    >

                        <div>
                            workspace bootstrap
                        </div>

                        <div>
                            replay synchronization
                        </div>

                        <div>
                            transport initialization
                        </div>

                        <div>
                            graph continuity restore
                        </div>

                    </div>

                </div>

            </div>
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Shell
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-screen
                h-screen
                overflow-hidden
                bg-neutral-950
                text-neutral-100
                relative
            "
        >

            {/* -------------------------------- */}
            {/* Desktop */}
            {/* -------------------------------- */}

            <RuntimeDesktop
                runtimeOS={runtimeOS}
            />

            {/* -------------------------------- */}
            {/* Runtime Dock */}
            {/* -------------------------------- */}

            <RuntimeDock
                runtimeOS={runtimeOS}
            />

            {/* -------------------------------- */}
            {/* Top Runtime Bar */}
            {/* -------------------------------- */}

            <div
                className="
                    absolute
                    top-0
                    left-0
                    right-0
                    h-10
                    z-[1500]
                    border-b
                    border-neutral-800
                    bg-neutral-950/80
                    backdrop-blur-xl
                    flex
                    items-center
                    justify-between
                    px-4
                    text-xs
                    font-mono
                "
            >

                {/* ---------------- */}
                {/* Left */}
                {/* ---------------- */}

                <div
                    className="
                        flex
                        items-center
                        gap-4
                    "
                >

                    <div
                        className="
                            font-semibold
                            tracking-wide
                            text-cyan-400
                        "
                    >
                        HHS
                    </div>

                    <div
                        className="
                            opacity-50
                        "
                    >
                        Runtime OS
                    </div>

                    <div
                        className="
                            opacity-30
                        "
                    >
                        Δe=0
                    </div>

                    <div
                        className="
                            opacity-30
                        "
                    >
                        Ψ=0
                    </div>

                    <div
                        className="
                            opacity-30
                        "
                    >
                        Θ15=true
                    </div>

                    <div
                        className="
                            opacity-30
                        "
                    >
                        Ω=true
                    </div>

                </div>

                {/* ---------------- */}
                {/* Right */}
                {/* ---------------- */}

                <div
                    className="
                        flex
                        items-center
                        gap-4
                    "
                >

                    <div>
                        windows:
                        {" "}
                        {
                            runtimeOS.workspace
                                .layout.windows
                                .length
                        }
                    </div>

                    <div>
                        apps:
                        {" "}
                        {
                            runtimeOS.state
                                .applicationsMounted
                        }
                    </div>

                    <div
                        className="
                            text-cyan-400
                        "
                    >
                        {
                            runtimeOS.state
                                .connected
                                    ? "online"
                                    : "offline"
                        }
                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Runtime Diagnostics */}
            {/* -------------------------------- */}

            {
                state.diagnosticsVisible && (

                    <div
                        className="
                            absolute
                            top-16
                            right-6
                            z-[1600]
                            w-[420px]
                            max-h-[70vh]
                            overflow-auto
                            rounded-2xl
                            border
                            border-neutral-800
                            bg-neutral-900/90
                            backdrop-blur-xl
                            shadow-2xl
                            p-5
                            text-xs
                            font-mono
                        "
                    >

                        <pre
                            className="
                                whitespace-pre-wrap
                                break-all
                            "
                        >
                            {
                                JSON.stringify(
                                    runtimeOS
                                        .getMetrics(),
                                    null,
                                    2
                                )
                            }
                        </pre>

                    </div>
                )
            }

        </div>
    )
}