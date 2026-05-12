import React, {
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
 * HHS Runtime Sidebar
 * ---------------------------------------------------
 * Canonical Runtime OS graph-navigation sidebar.
 *
 * Responsibilities:
 *
 * - Runtime graph navigation
 * - Workspace region routing
 * - Runtime application launching
 * - Replay-linked navigation continuity
 * - Runtime topology exploration
 * - Graph-native process navigation
 * - Runtime diagnostics surfacing
 * - Workspace orchestration
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

export interface RuntimeSidebarProps {

    registry: RuntimeApplicationRegistry

    router: RuntimeRouter

    windowManager: RuntimeWindowManager
}

interface RuntimeSidebarSection {

    id: string

    title: string

    applications: RuntimeApplication[]
}

export const RuntimeSidebar: React.FC<
    RuntimeSidebarProps
> = ({
    registry,
    router,
    windowManager
}) => {

    const [collapsed, setCollapsed] =
        useState(false)

    const [activeSection, setActiveSection] =
        useState<string>("runtime")

    /**
     * ---------------------------------------------------
     * Section Topology
     * ---------------------------------------------------
     */

    const sections =
        useMemo<
            RuntimeSidebarSection[]
        >(() => {

            return [

                {

                    id: "runtime",

                    title: "Runtime",

                    applications:
                        registry
                            .getApplicationsByType(
                                "system"
                            )
                },

                {

                    id: "symbolic",

                    title: "Symbolic",

                    applications:
                        registry
                            .getApplicationsByType(
                                "symbolic"
                            )
                },

                {

                    id: "graph",

                    title: "Graph",

                    applications: [

                        ...registry
                            .getApplicationsByType(
                                "graph"
                            ),

                        ...registry
                            .getApplicationsByType(
                                "tensor"
                            ),

                        ...registry
                            .getApplicationsByType(
                                "replay"
                            )
                    ]
                },

                {

                    id: "simulation",

                    title: "Simulation",

                    applications: [

                        ...registry
                            .getApplicationsByType(
                                "simulation"
                            ),

                        ...registry
                            .getApplicationsByType(
                                "transport"
                            )
                    ]
                },

                {

                    id: "development",

                    title: "Development",

                    applications:
                        registry
                            .getApplicationsByType(
                                "development"
                            )
                }
            ]

        }, [registry])

    /**
     * ---------------------------------------------------
     * Application Launch
     * ---------------------------------------------------
     */

    const launchApplication = (
        application: RuntimeApplication
    ) => {

        if (application.route) {

            router.navigate(
                application.route
            )
        }

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
            "[RuntimeSidebar] launch",
            application.id
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Sidebar
     * ---------------------------------------------------
     */

    return (

        <div
            className={`
                h-full
                border-r
                border-neutral-800
                bg-neutral-950
                transition-all
                duration-300
                overflow-hidden

                ${
                    collapsed
                        ? "w-16"
                        : "w-80"
                }
            `}
        >

            {/* -------------------------------- */}
            {/* Sidebar Header */}
            {/* -------------------------------- */}

            <div
                className="
                    h-14
                    border-b
                    border-neutral-800
                    flex
                    items-center
                    justify-between
                    px-4
                "
            >

                {
                    !collapsed && (

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
                                "
                            >
                                Runtime Navigator
                            </div>

                            <div
                                className="
                                    text-[10px]
                                    opacity-50
                                    font-mono
                                "
                            >
                                Graph-native topology
                            </div>

                        </div>
                    )
                }

                <button

                    onClick={() => {

                        setCollapsed(
                            !collapsed
                        )
                    }}

                    className="
                        w-8
                        h-8
                        rounded-lg
                        border
                        border-neutral-700
                        bg-neutral-900
                        hover:bg-neutral-800
                        transition
                        text-xs
                    "
                >
                    {
                        collapsed
                            ? "→"
                            : "←"
                    }
                </button>

            </div>

            {/* -------------------------------- */}
            {/* Navigation Sections */}
            {/* -------------------------------- */}

            <div
                className="
                    flex-1
                    overflow-auto
                    p-3
                    flex
                    flex-col
                    gap-3
                "
            >

                {
                    sections.map(

                        (section) => {

                            const active =
                                activeSection ===
                                section.id

                            return (

                                <div
                                    key={
                                        section.id
                                    }
                                    className="
                                        border
                                        border-neutral-800
                                        rounded-xl
                                        overflow-hidden
                                    "
                                >

                                    {/* ------------ */}
                                    {/* Section Head */}
                                    {/* ------------ */}

                                    <button

                                        onClick={() => {

                                            setActiveSection(
                                                active
                                                    ? ""
                                                    : section.id
                                            )
                                        }}

                                        className="
                                            w-full
                                            flex
                                            items-center
                                            justify-between
                                            px-4
                                            py-3
                                            bg-neutral-900
                                            hover:bg-neutral-800
                                            transition
                                            text-sm
                                        "
                                    >

                                        {
                                            collapsed
                                                ? section.title[0]
                                                : section.title
                                        }

                                        {
                                            !collapsed && (

                                                <span
                                                    className="
                                                        text-xs
                                                        opacity-50
                                                    "
                                                >
                                                    {
                                                        active
                                                            ? "−"
                                                            : "+"
                                                    }
                                                </span>
                                            )
                                        }

                                    </button>

                                    {/* ------------ */}
                                    {/* Applications */}
                                    {/* ------------ */}

                                    {
                                        active &&
                                        !collapsed && (

                                            <div
                                                className="
                                                    flex
                                                    flex-col
                                                "
                                            >

                                                {
                                                    section
                                                        .applications
                                                        .map(

                                                            (
                                                                application
                                                            ) => (

                                                                <button

                                                                    key={
                                                                        application.id
                                                                    }

                                                                    onClick={() => {

                                                                        launchApplication(
                                                                            application
                                                                        )
                                                                    }}

                                                                    className="
                                                                        flex
                                                                        flex-col
                                                                        items-start
                                                                        px-4
                                                                        py-3
                                                                        border-t
                                                                        border-neutral-800
                                                                        hover:bg-neutral-900
                                                                        transition
                                                                        text-left
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
                            )
                        }
                    )
                }

            </div>

            {/* -------------------------------- */}
            {/* Runtime Metrics */}
            {/* -------------------------------- */}

            {
                !collapsed && (

                    <div
                        className="
                            border-t
                            border-neutral-800
                            p-4
                            flex
                            flex-col
                            gap-2
                            text-[10px]
                            font-mono
                            opacity-70
                        "
                    >

                        <div>
                            routes:
                            {" "}
                            {
                                (
                                    router
                                        .getMetrics()
                                    as any
                                )
                                    .registeredRoutes
                            }
                        </div>

                        <div>
                            applications:
                            {" "}
                            {
                                (
                                    registry
                                        .getMetrics()
                                    as any
                                )
                                    .registeredApplications
                            }
                        </div>

                        <div>
                            mounted:
                            {" "}
                            {
                                (
                                    registry
                                        .getMetrics()
                                    as any
                                )
                                    .mountedApplications
                            }
                        </div>

                    </div>
                )
            }

        </div>
    )
}