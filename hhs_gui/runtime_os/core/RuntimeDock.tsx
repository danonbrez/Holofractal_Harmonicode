import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

export interface RuntimeDockApplication {

    id: string

    title: string

    icon: string
}

export interface RuntimeDockProps {

    runtimeOS: RuntimeOS
}

export const RuntimeDock: React.FC<
    RuntimeDockProps
> = ({ runtimeOS }) => {

    /**
     * ---------------------------------------------------
     * Runtime Applications
     * ---------------------------------------------------
     */

    const applications:
        RuntimeDockApplication[] = [

        {
            id: "runtime_console",

            title: "Runtime Console",

            icon: "⌘"
        },

        {
            id: "calculator",

            title: "Calculator",

            icon: "∑"
        },

        {
            id: "breadboard",

            title: "Breadboard",

            icon: "◈"
        },

        {
            id: "graph_debugger",

            title: "Graph Debugger",

            icon: "◎"
        },

        {
            id: "tensor_inspector",

            title: "Tensor Inspector",

            icon: "⬢"
        },

        {
            id: "replay_viewer",

            title: "Replay Viewer",

            icon: "⟳"
        }
    ]

    /**
     * ---------------------------------------------------
     * Launch Application
     * ---------------------------------------------------
     */

    const launchApplication = (
        app:
            RuntimeDockApplication
    ) => {

        runtimeOS.workspace.addWindow({

            id:
                crypto.randomUUID(),

            title:
                app.title,

            applicationId:
                app.id,

            position: {

                x:
                    220 +
                    Math.random() * 240,

                y:
                    120 +
                    Math.random() * 180
            },

            size: {

                width: 840,

                height: 560
            },

            minimized: false,

            maximized: false,

            focused: true,

            zIndex:
                runtimeOS.workspace
                    .layout.windows.length + 1
        })

        console.log(
            "[RuntimeDock] launched",
            app.id
        )
    }

    /**
     * ---------------------------------------------------
     * Render
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                absolute
                bottom-6
                left-1/2
                z-[1200]
            "
            style={{

                transform:
                    "translateX(-50%)"
            }}
        >

            <div
                className="
                    rounded-2xl
                    border
                    border-neutral-800
                    bg-neutral-900/80
                    backdrop-blur-xl
                    shadow-2xl
                    px-4
                    py-3
                    flex
                    items-end
                    gap-3
                "
            >

                {
                    applications.map((app) => (

                        <button
                            key={app.id}
                            onClick={() =>
                                launchApplication(
                                    app
                                )
                            }
                            className="
                                group
                                flex
                                flex-col
                                items-center
                                gap-2
                                transition
                                hover:scale-110
                            "
                        >

                            {/* ---------------- */}
                            {/* Icon */}
                            {/* ---------------- */}

                            <div
                                className="
                                    w-14
                                    h-14
                                    rounded-2xl
                                    border
                                    border-cyan-500/20
                                    bg-neutral-800
                                    flex
                                    items-center
                                    justify-center
                                    text-xl
                                    shadow-xl
                                    transition
                                    group-hover:bg-cyan-500/20
                                "
                            >
                                {app.icon}
                            </div>

                            {/* ---------------- */}
                            {/* Label */}
                            {/* ---------------- */}

                            <div
                                className="
                                    text-[10px]
                                    font-mono
                                    opacity-60
                                    whitespace-nowrap
                                "
                            >
                                {app.title}
                            </div>

                        </button>
                    ))
                }

            </div>

            {/* -------------------------------- */}
            {/* Dock Metrics */}
            {/* -------------------------------- */}

            <div
                className="
                    mt-3
                    text-center
                    text-[10px]
                    font-mono
                    opacity-40
                "
            >

                windows:
                {" "}
                {
                    runtimeOS.workspace
                        .layout.windows.length
                }

                {" • "}

                apps:
                {" "}
                {
                    runtimeOS.state
                        .applicationsMounted
                }

            </div>

        </div>
    )
}