import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeConsole
} from "./RuntimeConsole"

import {
    RuntimeCalculator
} from "../../runtime_apps/calculator/RuntimeCalculator"

import {
    RuntimeBreadboard
} from "../../runtime_apps/breadboard/RuntimeBreadboard"

export interface RuntimeWindowContentProps {

    runtimeOS: RuntimeOS

    applicationId: string
}

export const RuntimeWindowContent: React.FC<
    RuntimeWindowContentProps
> = ({
    runtimeOS,
    applicationId
}) => {

    /**
     * ---------------------------------------------------
     * Runtime Application Router
     * ---------------------------------------------------
     */

    switch (applicationId) {

        /**
         * --------------------------------------------
         * Runtime Console
         * --------------------------------------------
         */

        case "runtime_console":

            return (

                <RuntimeConsole
                    runtimeOS={runtimeOS}
                />
            )

        /**
         * --------------------------------------------
         * Calculator
         * --------------------------------------------
         */

        case "calculator":

            return (
                <RuntimeCalculator />
            )

        /**
         * --------------------------------------------
         * Breadboard
         * --------------------------------------------
         */

        case "breadboard":

            return (
                <RuntimeBreadboard />
            )

        /**
         * --------------------------------------------
         * Graph Debugger
         * --------------------------------------------
         */

        case "graph_debugger":

            return (

                <PlaceholderApplication
                    title="
                        Graph Debugger
                    "
                    description="
                        Runtime graph topology
                        inspection surface for
                        deterministic replay
                        structures and transport
                        synchronization.
                    "
                />
            )

        /**
         * --------------------------------------------
         * Tensor Inspector
         * --------------------------------------------
         */

        case "tensor_inspector":

            return (

                <PlaceholderApplication
                    title="
                        Tensor Inspector
                    "
                    description="
                        Tensor manifold
                        inspection surface for
                        runtime projection
                        analysis and multimodal
                        topology visualization.
                    "
                />
            )

        /**
         * --------------------------------------------
         * Replay Viewer
         * --------------------------------------------
         */

        case "replay_viewer":

            return (

                <PlaceholderApplication
                    title="
                        Replay Viewer
                    "
                    description="
                        Deterministic replay
                        inspection surface for
                        branch continuity,
                        replay topology, and
                        execution reconstruction.
                    "
                />
            )

        /**
         * --------------------------------------------
         * Physics Sandbox
         * --------------------------------------------
         */

        case "physics_sandbox":

            return (

                <PlaceholderApplication
                    title="
                        Physics Sandbox
                    "
                    description="
                        Deterministic simulation
                        environment for tensor
                        interactions and
                        replay-linked runtime
                        physics projection.
                    "
                />
            )

        /**
         * --------------------------------------------
         * Visual IDE
         * --------------------------------------------
         */

        case "visual_ide":

            return (

                <PlaceholderApplication
                    title="
                        Visual IDE
                    "
                    description="
                        Graph-native visual
                        runtime compiler and
                        deterministic manifold
                        orchestration environment.
                    "
                />
            )

        /**
         * --------------------------------------------
         * Unknown Application
         * --------------------------------------------
         */

        default:

            return (

                <PlaceholderApplication
                    title="
                        Unknown Application
                    "
                    description={`
                        No runtime projection
                        registered for:

                        ${applicationId}
                    `}
                />
            )
    }
}

/**
 * ===================================================
 * Placeholder Application
 * ===================================================
 */

export interface PlaceholderApplicationProps {

    title: string

    description: string
}

export const PlaceholderApplication:
React.FC<
    PlaceholderApplicationProps
> = ({
    title,
    description
}) => {

    return (

        <div
            className="
                w-full
                h-full
                bg-neutral-950
                text-neutral-100
                flex
                flex-col
                items-center
                justify-center
                p-8
                text-center
            "
        >

            <div
                className="
                    flex
                    flex-col
                    items-center
                    gap-5
                    max-w-xl
                "
            >

                <div
                    className="
                        text-3xl
                        font-bold
                        tracking-wide
                    "
                >
                    {title}
                </div>

                <div
                    className="
                        text-sm
                        opacity-60
                        leading-relaxed
                    "
                >
                    {description}
                </div>

                <div
                    className="
                        text-[10px]
                        opacity-40
                        font-mono
                    "
                >
                    Runtime projection surface
                    initialized
                </div>

            </div>

        </div>
    )
}