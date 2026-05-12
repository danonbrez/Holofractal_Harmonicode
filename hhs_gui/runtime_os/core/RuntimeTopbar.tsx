import React, {
    useEffect,
    useMemo,
    useState
} from "react"

import {
    RuntimeRouter
} from "./RuntimeRouter"

import {
    RuntimeApplicationRegistry
} from "./RuntimeApplicationRegistry"

import {
    RuntimeWindowManager
} from "./RuntimeWindowManager"

/**
 * HHS Runtime Topbar
 * ---------------------------------------------------
 * Canonical Runtime OS global orchestration bar.
 *
 * Responsibilities:
 *
 * - Runtime status visibility
 * - Workspace telemetry
 * - Replay continuity indicators
 * - Runtime graph state surfacing
 * - Global search
 * - Runtime command dispatch
 * - System-level orchestration controls
 * - Runtime diagnostics visibility
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeTopbarProps {

    router: RuntimeRouter

    registry: RuntimeApplicationRegistry

    windowManager: RuntimeWindowManager
}

export const RuntimeTopbar: React.FC<
    RuntimeTopbarProps
> = ({
    router,
    registry,
    windowManager
}) => {

    const [time, setTime] =
        useState<string>("")

    const [searchQuery, setSearchQuery] =
        useState("")

    /**
     * ---------------------------------------------------
     * Clock
     * ---------------------------------------------------
     */

    useEffect(() => {

        const updateClock = () => {

            setTime(

                new Date()
                    .toLocaleTimeString()
            )
        }

        updateClock()

        const interval =
            setInterval(
                updateClock,
                1000
            )

        return () => {

            clearInterval(interval)
        }

    }, [])

    /**
     * ---------------------------------------------------
     * Metrics
     * ---------------------------------------------------
     */

    const routerMetrics =
        useMemo(() => {

            return router.getMetrics()

        }, [router])

    const registryMetrics =
        useMemo(() => {

            return registry.getMetrics()

        }, [registry])

    const windowMetrics =
        useMemo(() => {

            return windowManager.getMetrics()

        }, [windowManager])

    /**
     * ---------------------------------------------------
     * Runtime Search
     * ---------------------------------------------------
     */

    const filteredApplications =
        useMemo(() => {

            if (!searchQuery.trim()) {

                return []
            }

            return registry
                .getApplications()
                .filter(

                    (application) => {

                        return (

                            application.name
                                .toLowerCase()
                                .includes(

                                    searchQuery
                                        .toLowerCase()
                                ) ||

                            application
                                .applicationType
                                .toLowerCase()
                                .includes(

                                    searchQuery
                                        .toLowerCase()
                                )
                        )
                    }
                )

        }, [
            registry,
            searchQuery
        ])

    /**
     * ---------------------------------------------------
     * Launch Search Result
     * ---------------------------------------------------
     */

    const launchApplication = (
        applicationId: string
    ) => {

        const application =
            registry.getApplication(
                applicationId
            )

        if (!application) {

            return
        }

        registry.mountApplication(
            application.id
        )

        windowManager.createWindow({

            title:
                application.name,

            applicationId:
                application.id
        })

        if (application.route) {

            router.navigate(
                application.route
            )
        }

        setSearchQuery("")
    }

    /**
     * ---------------------------------------------------
     * Runtime Topbar
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-full
                h-14
                border-b
                border-neutral-800
                bg-neutral-950/95
                backdrop-blur-xl
                flex
                items-center
                justify-between
                px-4
                relative
                z-50
            "
        >

            {/* -------------------------------- */}
            {/* Runtime Identity */}
            {/* -------------------------------- */}

            <div
                className="
                    flex
                    items-center
                    gap-4
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
                            text-sm
                            font-semibold
                            tracking-wide
                            text-cyan-300
                        "
                    >
                        HHS Runtime OS
                    </div>

                    <div
                        className="
                            text-[10px]
                            opacity-50
                            font-mono
                        "
                    >
                        deterministic graph manifold
                    </div>

                </div>

                <div
                    className="
                        h-8
                        w-px
                        bg-neutral-800
                    "
                />

                <div
                    className="
                        flex
                        items-center
                        gap-3
                        text-[10px]
                        font-mono
                        opacity-70
                    "
                >

                    <div>
                        Δe=0
                    </div>

                    <div>
                        Ψ=0
                    </div>

                    <div>
                        Θ15=true
                    </div>

                    <div>
                        Ω=true
                    </div>

                </div>

            </div>

            {/* -------------------------------- */}
            {/* Runtime Search */}
            {/* -------------------------------- */}

            <div
                className="
                    relative
                    w-[420px]
                "
            >

                <input

                    value={searchQuery}

                    onChange={(event) => {

                        setSearchQuery(
                            event.target.value
                        )
                    }}

                    placeholder="
                        Search runtime applications...
                    "

                    className="
                        w-full
                        h-10
                        rounded-xl
                        border
                        border-neutral-800
                        bg-neutral-900
                        px-4
                        text-sm
                        outline-none
                        focus:border-cyan-500
                        transition
                    "
                />

                {/* ---------------------------- */}
                {/* Search Results */}
                {/* ---------------------------- */}

                {
                    filteredApplications.length > 0 && (

                        <div
                            className="
                                absolute
                                top-12
                                left-0
                                right-0
                                rounded-xl
                                border
                                border-neutral-800
                                bg-neutral-950
                                overflow-hidden
                                shadow-2xl
                            "
                        >

                            {
                                filteredApplications.map(

                                    (application) => (

                                        <button

                                            key={
                                                application.id
                                            }

                                            onClick={() => {

                                                launchApplication(
                                                    application.id
                                                )
                                            }}

                                            className="
                                                w-full
                                                px-4
                                                py-3
                                                text-left
                                                border-b
                                                border-neutral-800
                                                hover:bg-neutral-900
                                                transition
                                                flex
                                                flex-col
                                            "
                                        >

                                            <div
                                                className="
                                                    text-sm
                                                "
                                            >
                                                {
                                                    application.name
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
                                                    application.applicationType
                                                }
                                            </div>

                                        </button>
                                    )
                                )
                            }

                        </div>
                    )
                }

            </div>

            {/* -------------------------------- */}
            {/* Runtime Metrics */}
            {/* -------------------------------- */}

            <div
                className="
                    flex
                    items-center
                    gap-6
                    text-[10px]
                    font-mono
                "
            >

                <div
                    className="
                        flex
                        flex-col
                        items-end
                    "
                >

                    <div
                        className="
                            opacity-40
                        "
                    >
                        routes
                    </div>

                    <div>
                        {
                            (
                                routerMetrics
                                as any
                            )
                                .registeredRoutes
                        }
                    </div>

                </div>

                <div
                    className="
                        flex
                        flex-col
                        items-end
                    "
                >

                    <div
                        className="
                            opacity-40
                        "
                    >
                        applications
                    </div>

                    <div>
                        {
                            (
                                registryMetrics
                                as any
                            )
                                .registeredApplications
                        }
                    </div>

                </div>

                <div
                    className="
                        flex
                        flex-col
                        items-end
                    "
                >

                    <div
                        className="
                            opacity-40
                        "
                    >
                        windows
                    </div>

                    <div>
                        {
                            (
                                windowMetrics
                                as any
                            )
                                .totalWindows
                        }
                    </div>

                </div>

                <div
                    className="
                        h-8
                        w-px
                        bg-neutral-800
                    "
                />

                <div
                    className="
                        text-xs
                        text-cyan-300
                    "
                >
                    {time}
                </div>

            </div>

        </div>
    )
}