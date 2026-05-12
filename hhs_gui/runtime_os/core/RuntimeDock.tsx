import React, {
    useMemo,
    useState
} from "react"

import {
    RuntimeApplicationRegistry,
    RuntimeApplication
} from "./RuntimeApplicationRegistry"

import {
    RuntimeWindowManager
} from "./RuntimeWindowManager"

/**
 * HHS Runtime Dock
 * ---------------------------------------------------
 * Canonical Runtime OS application dock.
 *
 * Responsibilities:
 *
 * - Runtime application launching
 * - Application mounting
 * - Window orchestration
 * - Graph-native application access
 * - Replay-linked launch continuity
 * - Runtime process shortcuts
 * - Workspace application navigation
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeDockProps {

    registry: RuntimeApplicationRegistry

    windowManager: RuntimeWindowManager
}

export const RuntimeDock: React.FC<
    RuntimeDockProps
> = ({
    registry,
    windowManager
}) => {

    const [hoveredApp, setHoveredApp] =
        useState<string | null>(null)

    /**
     * ---------------------------------------------------
     * Visible Applications
     * ---------------------------------------------------
     */

    const applications =
        useMemo(() => {

            return registry
                .getApplications()
                .filter(

                    (application) =>
                        application.visible
                )

        }, [registry])

    /**
     * ---------------------------------------------------
     * Application Launch
     * ---------------------------------------------------
     */

    const launchApplication = (
        application: RuntimeApplication
    ) => {

        registry.mountApplication(
            application.id
        )

        windowManager.createWindow({

            title:
                application.name,

            applicationId:
                application.id,

            width: 960,

            height: 640
        })

        console.log(
            "[RuntimeDock] launch",
            application.id
        )
    }

    /**
     * ---------------------------------------------------
     * Icon Mapping
     * ---------------------------------------------------
     */

    const getIcon = (
        icon?: string
    ): string => {

        switch (icon) {

            case "terminal":

                return "⌘"

            case "calculator":

                return "∑"

            case "orbit":

                return "◉"

            case "network":

                return "◎"

            case "history":

                return "↺"

            case "atom":

                return "⚛"

            case "cpu":

                return "▣"

            case "code":

                return "{ }"

            default:

                return "◆"
        }
    }

    /**
     * ---------------------------------------------------
     * Runtime Dock
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                absolute
                bottom-4
                left-1/2
                -translate-x-1/2
                z-50
                pointer-events-auto
            "
        >

            <div
                className="
                    flex
                    items-end
                    gap-3
                    px-5
                    py-3
                    rounded-2xl
                    border
                    border-neutral-800
                    bg-black/70
                    backdrop-blur-xl
                    shadow-2xl
                "
            >

                {
                    applications.map(

                        (application) => {

                            const hovered =
                                hoveredApp ===
                                application.id

                            return (

                                <div
                                    key={
                                        application.id
                                    }
                                    className="
                                        relative
                                        flex
                                        flex-col
                                        items-center
                                    "
                                    onMouseEnter={() => {

                                        setHoveredApp(
                                            application.id
                                        )
                                    }}
                                    onMouseLeave={() => {

                                        setHoveredApp(
                                            null
                                        )
                                    }}
                                >

                                    {/* ---------------- */}
                                    {/* Tooltip */}
                                    {/* ---------------- */}

                                    {
                                        hovered && (

                                            <div
                                                className="
                                                    absolute
                                                    bottom-20
                                                    whitespace-nowrap
                                                    px-3
                                                    py-1
                                                    rounded-lg
                                                    bg-neutral-900
                                                    border
                                                    border-neutral-700
                                                    text-xs
                                                    font-mono
                                                    text-neutral-200
                                                "
                                            >
                                                {
                                                    application.name
                                                }
                                            </div>
                                        )
                                    }

                                    {/* ---------------- */}
                                    {/* App Icon */}
                                    {/* ---------------- */}

                                    <button

                                        onClick={() => {

                                            launchApplication(
                                                application
                                            )
                                        }}

                                        className={`
                                            w-14
                                            h-14
                                            rounded-2xl
                                            border
                                            transition-all
                                            duration-200
                                            flex
                                            items-center
                                            justify-center
                                            text-lg
                                            font-bold
                                            backdrop-blur-md

                                            ${
                                                hovered
                                                    ? `
                                                        scale-110
                                                        bg-cyan-500/20
                                                        border-cyan-400
                                                        text-cyan-300
                                                      `
                                                    : `
                                                        bg-neutral-900/80
                                                        border-neutral-700
                                                        text-neutral-200
                                                      `
                                            }
                                        `}
                                    >

                                        {
                                            getIcon(
                                                application.icon
                                            )
                                        }

                                    </button>

                                    {/* ---------------- */}
                                    {/* Mounted Indicator */}
                                    {/* ---------------- */}

                                    {
                                        application.mounted && (

                                            <div
                                                className="
                                                    mt-2
                                                    w-2
                                                    h-2
                                                    rounded-full
                                                    bg-cyan-400
                                                "
                                            />
                                        )
                                    }

                                </div>
                            )
                        }
                    )
                }

            </div>

        </div>
    )
}