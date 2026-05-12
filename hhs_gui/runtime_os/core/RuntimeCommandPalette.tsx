import React, {
    useEffect,
    useMemo,
    useState
} from "react"

import {
    RuntimeApplicationRegistry,
    RuntimeApplication
} from "./RuntimeApplicationRegistry"

import {
    RuntimeRouter
} from "./RuntimeRouter"

import {
    RuntimeWindowManager
} from "./RuntimeWindowManager"

/**
 * HHS Runtime Command Palette
 * ---------------------------------------------------
 * Canonical Runtime OS command execution surface.
 *
 * Responsibilities:
 *
 * - Runtime command dispatch
 * - Global application launch
 * - Workspace orchestration
 * - Replay-linked command continuity
 * - Runtime search execution
 * - Graph-native navigation
 * - Runtime utility execution
 * - Deterministic command routing
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeCommandPaletteProps {

    registry: RuntimeApplicationRegistry

    router: RuntimeRouter

    windowManager: RuntimeWindowManager
}

interface RuntimeCommand {

    id: string

    label: string

    category: string

    action: () => void
}

export const RuntimeCommandPalette: React.FC<
    RuntimeCommandPaletteProps
> = ({
    registry,
    router,
    windowManager
}) => {

    const [open, setOpen] =
        useState(false)

    const [query, setQuery] =
        useState("")

    const [selectedIndex, setSelectedIndex] =
        useState(0)

    /**
     * ---------------------------------------------------
     * Global Shortcut
     * ---------------------------------------------------
     */

    useEffect(() => {

        const handler = (
            event: KeyboardEvent
        ) => {

            const isCommandPalette =

                (event.metaKey || event.ctrlKey) &&

                event.key.toLowerCase() === "k"

            if (!isCommandPalette) {

                return
            }

            event.preventDefault()

            setOpen((previous) => !previous)
        }

        window.addEventListener(
            "keydown",
            handler
        )

        return () => {

            window.removeEventListener(
                "keydown",
                handler
            )
        }

    }, [])

    /**
     * ---------------------------------------------------
     * Runtime Commands
     * ---------------------------------------------------
     */

    const commands =
        useMemo<
            RuntimeCommand[]
        >(() => {

            const applicationCommands =
                registry
                    .getApplications()
                    .map(

                        (
                            application:
                                RuntimeApplication
                        ) => ({

                            id:
                                application.id,

                            label:
                                `Launch ${application.name}`,

                            category:
                                application.applicationType,

                            action: () => {

                                registry.mountApplication(

                                    application.id
                                )

                                windowManager
                                    .createWindow({

                                        title:
                                            application.name,

                                        applicationId:
                                            application.id
                                    })

                                if (
                                    application.route
                                ) {

                                    router.navigate(

                                        application.route
                                    )
                                }

                                setOpen(false)

                                setQuery("")
                            }
                        })
                    )

            const systemCommands:
                RuntimeCommand[] = [

                {

                    id:
                        "tile_windows",

                    label:
                        "Tile Runtime Windows",

                    category:
                        "workspace",

                    action: () => {

                        windowManager
                            .tileWindows()

                        setOpen(false)
                    }
                },

                {

                    id:
                        "cascade_windows",

                    label:
                        "Cascade Runtime Windows",

                    category:
                        "workspace",

                    action: () => {

                        windowManager
                            .cascadeWindows()

                        setOpen(false)
                    }
                },

                {

                    id:
                        "navigate_root",

                    label:
                        "Navigate Root Workspace",

                    category:
                        "navigation",

                    action: () => {

                        router.navigate("/")

                        setOpen(false)
                    }
                }
            ]

            return [

                ...applicationCommands,

                ...systemCommands
            ]

        }, [
            registry,
            router,
            windowManager
        ])

    /**
     * ---------------------------------------------------
     * Filtered Commands
     * ---------------------------------------------------
     */

    const filteredCommands =
        useMemo(() => {

            if (!query.trim()) {

                return commands
            }

            return commands.filter(

                (command) => {

                    return (

                        command.label
                            .toLowerCase()
                            .includes(

                                query
                                    .toLowerCase()
                            ) ||

                        command.category
                            .toLowerCase()
                            .includes(

                                query
                                    .toLowerCase()
                            )
                    )
                }
            )

        }, [
            commands,
            query
        ])

    /**
     * ---------------------------------------------------
     * Keyboard Navigation
     * ---------------------------------------------------
     */

    useEffect(() => {

        if (!open) {

            return
        }

        const handler = (
            event: KeyboardEvent
        ) => {

            if (
                event.key === "ArrowDown"
            ) {

                event.preventDefault()

                setSelectedIndex(

                    (previous) =>

                        Math.min(

                            previous + 1,

                            filteredCommands.length - 1
                        )
                )
            }

            if (
                event.key === "ArrowUp"
            ) {

                event.preventDefault()

                setSelectedIndex(

                    (previous) =>

                        Math.max(
                            previous - 1,
                            0
                        )
                )
            }

            if (
                event.key === "Enter"
            ) {

                event.preventDefault()

                const command =
                    filteredCommands[
                        selectedIndex
                    ]

                command?.action()
            }

            if (
                event.key === "Escape"
            ) {

                setOpen(false)
            }
        }

        window.addEventListener(
            "keydown",
            handler
        )

        return () => {

            window.removeEventListener(
                "keydown",
                handler
            )
        }

    }, [
        open,
        filteredCommands,
        selectedIndex
    ])

    /**
     * ---------------------------------------------------
     * Closed State
     * ---------------------------------------------------
     */

    if (!open) {

        return null
    }

    /**
     * ---------------------------------------------------
     * Runtime Command Palette
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                absolute
                inset-0
                z-[999]
                bg-black/40
                backdrop-blur-sm
                flex
                items-start
                justify-center
                pt-32
            "
        >

            <div
                className="
                    w-[720px]
                    rounded-2xl
                    border
                    border-neutral-800
                    bg-neutral-950
                    shadow-2xl
                    overflow-hidden
                "
            >

                {/* -------------------------------- */}
                {/* Input */}
                {/* -------------------------------- */}

                <div
                    className="
                        border-b
                        border-neutral-800
                    "
                >

                    <input

                        autoFocus

                        value={query}

                        onChange={(event) => {

                            setQuery(
                                event.target.value
                            )

                            setSelectedIndex(0)
                        }}

                        placeholder="
                            Search runtime commands...
                        "

                        className="
                            w-full
                            h-16
                            bg-transparent
                            px-6
                            outline-none
                            text-lg
                            font-medium
                        "
                    />

                </div>

                {/* -------------------------------- */}
                {/* Commands */}
                {/* -------------------------------- */}

                <div
                    className="
                        max-h-[480px]
                        overflow-auto
                    "
                >

                    {
                        filteredCommands.map(

                            (
                                command,
                                index
                            ) => (

                                <button

                                    key={
                                        command.id
                                    }

                                    onClick={() => {

                                        command.action()
                                    }}

                                    className={`
                                        w-full
                                        flex
                                        flex-col
                                        items-start
                                        px-6
                                        py-4
                                        border-b
                                        border-neutral-900
                                        transition
                                        text-left

                                        ${
                                            index ===
                                            selectedIndex

                                                ? `
                                                    bg-cyan-500/10
                                                  `

                                                : `
                                                    hover:bg-neutral-900
                                                  `
                                        }
                                    `}
                                >

                                    <div
                                        className="
                                            text-sm
                                        "
                                    >
                                        {
                                            command.label
                                        }
                                    </div>

                                    <div
                                        className="
                                            text-[10px]
                                            opacity-50
                                            font-mono
                                        "
                                    >
                                        {
                                            command.category
                                        }
                                    </div>

                                </button>
                            )
                        )
                    }

                </div>

                {/* -------------------------------- */}
                {/* Footer */}
                {/* -------------------------------- */}

                <div
                    className="
                        h-10
                        border-t
                        border-neutral-800
                        flex
                        items-center
                        justify-between
                        px-4
                        text-[10px]
                        font-mono
                        opacity-50
                    "
                >

                    <div>
                        ENTER → execute
                    </div>

                    <div>
                        ESC → close
                    </div>

                    <div>
                        CTRL/CMD + K
                    </div>

                </div>

            </div>

        </div>
    )
}