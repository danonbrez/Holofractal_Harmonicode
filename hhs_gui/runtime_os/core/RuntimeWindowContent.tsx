import React from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

/**
 * =========================================================
 * Existing Runtime Applications
 * =========================================================
 *
 * IMPORTANT:
 * ---------------------------------------------------------
 * These imports intentionally target the richer upstream
 * runtime application surfaces discovered during repo scan.
 *
 * Fallback surfaces remain below for incomplete modules.
 */

import HHSCalculatorSurface from
    "../../runtime_apps/calculator/HHSCalculatorSurface"

import HHSCalculatorGraphProjection from
    "../../runtime_apps/calculator/HHSCalculatorGraphProjection"

import HHSBreadboardSurface from
    "../../runtime_apps/breadboard/HHSBreadboardSurface"

import HHSTransportOverlay from
    "../../runtime_apps/breadboard/HHSTransportOverlay"

// =========================================================
// Props
// =========================================================

export interface RuntimeWindowContentProps {

    runtimeOS: RuntimeOS

    applicationId: string
}

// =========================================================
// RuntimeWindowContent
// =========================================================

export const RuntimeWindowContent: React.FC<
    RuntimeWindowContentProps
> = ({

    runtimeOS,

    applicationId
}) => {

    /**
     * -----------------------------------------------------
     * Runtime Console
     * -----------------------------------------------------
     */

    if (
        applicationId
        === "runtime_console"
    ) {

        return (

            <RuntimeConsoleSurface
                runtimeOS={runtimeOS}
            />
        )
    }

    /**
     * -----------------------------------------------------
     * Calculator
     * -----------------------------------------------------
     */

    if (
        applicationId
        === "calculator"
    ) {

        return (

            <div
                className="
                    w-full
                    h-full
                    grid
                    grid-cols-2
                    overflow-hidden
                "
            >

                <div
                    className="
                        border-r
                        border-neutral-800
                        overflow-hidden
                    "
                >

                    <HHSCalculatorSurface />

                </div>

                <div
                    className="
                        overflow-hidden
                    "
                >

                    <HHSCalculatorGraphProjection />

                </div>

            </div>
        )
    }

    /**
     * -----------------------------------------------------
     * Breadboard
     * -----------------------------------------------------
     */

    if (
        applicationId
        === "breadboard"
    ) {

        return (

            <div
                className="
                    relative
                    w-full
                    h-full
                    overflow-hidden
                "
            >

                <HHSBreadboardSurface />

                <HHSTransportOverlay />

            </div>
        )
    }

    /**
     * -----------------------------------------------------
     * Graph Debugger
     * -----------------------------------------------------
     */

    if (
        applicationId
        === "graph_debugger"
    ) {

        return (

            <GraphDebuggerSurface
                runtimeOS={runtimeOS}
            />
        )
    }

    /**
     * -----------------------------------------------------
     * Tensor Inspector
     * -----------------------------------------------------
     */

    if (
        applicationId
        === "tensor_inspector"
    ) {

        return (

            <TensorInspectorSurface
                runtimeOS={runtimeOS}
            />
        )
    }

    /**
     * -----------------------------------------------------
     * Replay Viewer
     * -----------------------------------------------------
     */

    if (
        applicationId
        === "replay_viewer"
    ) {

        return (

            <ReplayViewerSurface
                runtimeOS={runtimeOS}
            />
        )
    }

    /**
     * -----------------------------------------------------
     * Unknown
     * -----------------------------------------------------
     */

    return (

        <UnknownApplicationSurface
            applicationId={
                applicationId
            }
        />
    )
}

// =========================================================
// Runtime Console Surface
// =========================================================

interface RuntimeConsoleSurfaceProps {

    runtimeOS: RuntimeOS
}

const RuntimeConsoleSurface: React.FC<
    RuntimeConsoleSurfaceProps
> = ({ runtimeOS }) => {

    const metrics =
        runtimeOS.getMetrics()

    return (

        <div
            className="
                w-full
                h-full
                bg-black
                text-cyan-400
                font-mono
                text-xs
                overflow-auto
                p-4
                flex
                flex-col
                gap-3
            "
        >

            <div
                className="
                    text-cyan-300
                    font-semibold
                "
            >
                HHS Runtime Console
            </div>

            <div>
                runtime_status:
                {" "}
                {
                    runtimeOS.state
                        .connected
                            ? "online"
                            : "offline"
                }
            </div>

            <div>
                replay_ready:
                {" "}
                {
                    runtimeOS.state
                        .replayReady
                            ? "true"
                            : "false"
                }
            </div>

            <div>
                graph_ready:
                {" "}
                {
                    runtimeOS.state
                        .graphReady
                            ? "true"
                            : "false"
                }
            </div>

            <div>
                transport_ready:
                {" "}
                {
                    runtimeOS.state
                        .transportReady
                            ? "true"
                            : "false"
                }
            </div>

            <div
                className="
                    mt-4
                    opacity-70
                "
            >
                metrics:
            </div>

            <pre
                className="
                    whitespace-pre-wrap
                    break-all
                    opacity-60
                "
            >
                {
                    JSON.stringify(
                        metrics,
                        null,
                        2
                    )
                }
            </pre>

        </div>
    )
}

// =========================================================
// Graph Debugger Surface
// =========================================================

interface GraphDebuggerSurfaceProps {

    runtimeOS: RuntimeOS
}

const GraphDebuggerSurface: React.FC<
    GraphDebuggerSurfaceProps
> = ({ runtimeOS }) => {

    const graphEvent =
        runtimeOS.sockets.state
            .lastGraphEvent

    return (

        <div
            className="
                w-full
                h-full
                overflow-auto
                bg-neutral-950
                text-white
                font-mono
                text-xs
                p-4
                flex
                flex-col
                gap-4
            "
        >

            <div
                className="
                    text-cyan-400
                    font-semibold
                "
            >
                Runtime Graph Debugger
            </div>

            <div>
                graph_connected:
                {" "}
                {
                    runtimeOS.sockets
                        .state
                        .graphConnected
                            ? "true"
                            : "false"
                }
            </div>

            <pre
                className="
                    whitespace-pre-wrap
                    break-all
                    opacity-70
                "
            >
                {
                    JSON.stringify(
                        graphEvent,
                        null,
                        2
                    )
                }
            </pre>

        </div>
    )
}

// =========================================================
// Tensor Inspector
// =========================================================

interface TensorInspectorSurfaceProps {

    runtimeOS: RuntimeOS
}

const TensorInspectorSurface: React.FC<
    TensorInspectorSurfaceProps
> = ({ runtimeOS }) => {

    return (

        <div
            className="
                w-full
                h-full
                overflow-auto
                bg-neutral-950
                text-white
                font-mono
                text-xs
                p-4
            "
        >

            <div
                className="
                    text-purple-400
                    font-semibold
                    mb-4
                "
            >
                Tensor Inspector
            </div>

            <div
                className="
                    grid
                    grid-cols-2
                    gap-4
                "
            >

                {
                    Array.from({

                        length: 9

                    }).map((_, i) => (

                        <div
                            key={i}
                            className="
                                aspect-square
                                border
                                border-neutral-800
                                rounded-lg
                                bg-neutral-900
                                flex
                                items-center
                                justify-center
                                text-lg
                            "
                        >
                            {i + 1}
                        </div>
                    ))
                }

            </div>

        </div>
    )
}

// =========================================================
// Replay Viewer
// =========================================================

interface ReplayViewerSurfaceProps {

    runtimeOS: RuntimeOS
}

const ReplayViewerSurface: React.FC<
    ReplayViewerSurfaceProps
> = ({ runtimeOS }) => {

    const replay =
        runtimeOS.sockets.state
            .replayHistory

    return (

        <div
            className="
                w-full
                h-full
                overflow-auto
                bg-black
                text-green-400
                font-mono
                text-xs
                p-4
                flex
                flex-col
                gap-2
            "
        >

            <div
                className="
                    text-green-300
                    font-semibold
                "
            >
                Replay Timeline
            </div>

            {
                replay.map(
                    (
                        event,
                        index
                    ) => (

                        <div
                            key={index}
                            className="
                                border-b
                                border-neutral-800
                                pb-2
                            "
                        >

                            <div>
                                seq:
                                {" "}
                                {
                                    event
                                        .sequence_id
                                }
                            </div>

                            <div>
                                tick:
                                {" "}
                                {
                                    String(
                                        event
                                            .payload
                                            .replay_tick
                                    )
                                }
                            </div>

                            <div
                                className="
                                    opacity-60
                                "
                            >
                                {
                                    JSON.stringify(
                                        event.payload
                                    )
                                }
                            </div>

                        </div>
                    )
                )
            }

        </div>
    )
}

// =========================================================
// Unknown Surface
// =========================================================

interface UnknownApplicationSurfaceProps {

    applicationId: string
}

const UnknownApplicationSurface: React.FC<
    UnknownApplicationSurfaceProps
> = ({
    applicationId
}) => {

    return (

        <div
            className="
                w-full
                h-full
                flex
                items-center
                justify-center
                bg-neutral-950
                text-neutral-500
                font-mono
                text-sm
            "
        >

            unknown_application:
            {" "}
            {applicationId}

        </div>
    )
}