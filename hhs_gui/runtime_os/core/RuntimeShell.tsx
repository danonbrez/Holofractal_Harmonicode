import React, { useEffect, useState } from "react"

import { RuntimeOS } from "./RuntimeOS"

export interface RuntimeShellProps {

    runtimeOS: RuntimeOS
}

export interface RuntimeShellState {

    bootComplete: boolean

    activeWorkspace?: string

    sidebarVisible: boolean

    diagnosticsVisible: boolean
}

export const RuntimeShell: React.FC<
    RuntimeShellProps
> = ({ runtimeOS }) => {

    const [state, setState] =
        useState<RuntimeShellState>({

            bootComplete: false,

            sidebarVisible: true,

            diagnosticsVisible: false
        })

    /**
     * ---------------------------------------------------
     * Runtime Bootstrap
     * ---------------------------------------------------
     */

    useEffect(() => {

        let mounted = true

        const bootstrap = async () => {

            try {

                await runtimeOS.initialize()

                if (!mounted) {

                    return
                }

                setState({

                    bootComplete: true,

                    activeWorkspace:
                        runtimeOS.state.activeWorkspace,

                    sidebarVisible: true,

                    diagnosticsVisible: false
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
                    text-green-400
                    flex
                    items-center
                    justify-center
                    font-mono
                    text-sm
                "
            >
                <div
                    className="
                        flex
                        flex-col
                        gap-4
                        items-center
                    "
                >
                    <div>
                        HHS Runtime OS Bootstrapping...
                    </div>

                    <div
                        className="
                            animate-pulse
                            text-xs
                            opacity-70
                        "
                    >
                        Initializing runtime manifold
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
                flex
                flex-col
            "
        >

            {/* -------------------------------- */}
            {/* Top Bar */}
            {/* -------------------------------- */}

            <div
                className="
                    h-12
                    border-b
                    border-neutral-800
                    flex
                    items-center
                    justify-between
                    px-4
                    bg-neutral-900
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-3
                    "
                >

                    <div
                        className="
                            font-semibold
                            tracking-wide
                        "
                    >
                        HHS Runtime OS
                    </div>

                    <div
                        className="
                            text-xs
                            opacity-60
                            font-mono
                        "
                    >
                        Δe=0 Ψ=0 Θ15 Ω
                    </div>

                </div>

                <div
                    className="
                        flex
                        items-center
                        gap-3
                        text-xs
                        font-mono
                    "
                >

                    <div>
                        apps:
                        {" "}
                        {runtimeOS.state.applicationsMounted}
                    </div>

                    <div>
                        replay:
                        {" "}
                        {
                            runtimeOS.state.replayReady
                                ? "online"
                                : "offline"
                        }
                    </div>

                    <div>
                        graph:
                        {" "}
                        {
                            runtimeOS.state.graphReady
                                ? "online"
                                : "offline"
                        }
                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Main Runtime Layout */}
            {/* -------------------------------- */}

            <div
                className="
                    flex
                    flex-1
                    overflow-hidden
                "
            >

                {/* -------------------------------- */}
                {/* Sidebar */}
                {/* -------------------------------- */}

                {
                    state.sidebarVisible && (

                        <div
                            className="
                                w-72
                                border-r
                                border-neutral-800
                                bg-neutral-900
                                flex
                                flex-col
                            "
                        >

                            <div
                                className="
                                    p-4
                                    border-b
                                    border-neutral-800
                                    text-sm
                                    font-semibold
                                "
                            >
                                Runtime Navigation
                            </div>

                            <div
                                className="
                                    flex-1
                                    overflow-auto
                                    p-3
                                    flex
                                    flex-col
                                    gap-2
                                "
                            >

                                {
                                    [
                                        "Runtime Console",

                                        "Calculator",

                                        "Tensor Inspector",

                                        "Replay Viewer",

                                        "Graph Debugger",

                                        "Physics Sandbox",

                                        "Breadboard",

                                        "Visual IDE"
                                    ].map((item) => (

                                        <button
                                            key={item}
                                            className="
                                                w-full
                                                text-left
                                                px-3
                                                py-2
                                                rounded-lg
                                                bg-neutral-800
                                                hover:bg-neutral-700
                                                transition
                                                text-sm
                                            "
                                        >
                                            {item}
                                        </button>
                                    ))
                                }

                            </div>

                        </div>
                    )
                }

                {/* -------------------------------- */}
                {/* Runtime Viewport */}
                {/* -------------------------------- */}

                <div
                    className="
                        flex-1
                        relative
                        overflow-hidden
                        bg-neutral-950
                    "
                >

                    {/* -------------------------------- */}
                    {/* Runtime Grid */}
                    {/* -------------------------------- */}

                    <div
                        className="
                            absolute
                            inset-0
                            opacity-[0.08]
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
                    {/* Runtime Workspace */}
                    {/* -------------------------------- */}

                    <div
                        className="
                            absolute
                            inset-0
                            flex
                            items-center
                            justify-center
                        "
                    >

                        <div
                            className="
                                text-center
                                flex
                                flex-col
                                gap-4
                            "
                        >

                            <div
                                className="
                                    text-3xl
                                    font-bold
                                "
                            >
                                Runtime Workspace
                            </div>

                            <div
                                className="
                                    text-sm
                                    opacity-60
                                    font-mono
                                "
                            >
                                Workspace:
                                {" "}
                                {state.activeWorkspace}
                            </div>

                            <div
                                className="
                                    text-xs
                                    opacity-40
                                    max-w-xl
                                    leading-relaxed
                                "
                            >
                                Deterministic graph-native
                                operating environment
                                with replay-linked runtime
                                continuity and multimodal
                                projection topology.
                            </div>

                        </div>

                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Runtime Footer */}
            {/* -------------------------------- */}

            <div
                className="
                    h-8
                    border-t
                    border-neutral-800
                    bg-neutral-900
                    flex
                    items-center
                    justify-between
                    px-4
                    text-xs
                    font-mono
                    opacity-70
                "
            >

                <div>
                    Runtime OS Active
                </div>

                <div>
                    uptime:
                    {" "}
                    {
                        Math.floor(
                            runtimeOS.getMetrics()
                                .uptimeMs as number
                        )
                    }
                    ms
                </div>

            </div>

        </div>
    )
}