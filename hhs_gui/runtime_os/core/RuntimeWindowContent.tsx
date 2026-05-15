import React, {
    Suspense
} from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

// =========================================================
// Safe Runtime Import
// =========================================================

async function safeRuntimeImport(

    loader: () => Promise<any>,

    fallback: React.ComponentType<any>

): Promise<{

    default: React.ComponentType<any>
}> {

    try {

        return await loader()

    } catch (error) {

        console.error(

            "[RuntimeWindowContent] optional runtime surface missing",

            error
        )

        return {

            default:
                fallback
        }
    }
}

// =========================================================
// Lazy Runtime Applications
// =========================================================

const HHSCalculatorSurface =
    React.lazy(() =>

        safeRuntimeImport(

            () => import(
                "../../runtime_apps/calculator/HHSCalculatorSurface"
            ),

            CalculatorFallbackSurface
        )
    )

// ---------------------------------------------------------

const HHSCalculatorGraphProjection =
    React.lazy(() =>

        safeRuntimeImport(

            () => import(
                "../../runtime_apps/calculator/HHSCalculatorGraphProjection"
            ),

            GraphProjectionFallbackSurface
        )
    )

// ---------------------------------------------------------

const HHSBreadboardSurface =
    React.lazy(() =>

        safeRuntimeImport(

            () => import(
                "../../runtime_apps/breadboard/HHSBreadboardSurface"
            ),

            BreadboardFallbackSurface
        )
    )

// ---------------------------------------------------------

const HHSTransportOverlay =
    React.lazy(() =>

        safeRuntimeImport(

            () => import(
                "../../runtime_apps/breadboard/HHSTransportOverlay"
            ),

            OverlayFallbackSurface
        )
    )

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

    // =====================================================
    // Runtime Console
    // =====================================================

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

    // =====================================================
    // Calculator
    // =====================================================

    if (
        applicationId
        === "calculator"
    ) {

        return (

            <Suspense
                fallback={
                    <LoadingSurface
                        label="calculator"
                    />
                }
            >

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

            </Suspense>
        )
    }

    // =====================================================
    // Breadboard
    // =====================================================

    if (
        applicationId
        === "breadboard"
    ) {

        return (

            <Suspense
                fallback={
                    <LoadingSurface
                        label="breadboard"
                    />
                }
            >

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

            </Suspense>
        )
    }

    // =====================================================
    // Graph Debugger
    // =====================================================

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

    // =====================================================
    // Tensor Inspector
    // =====================================================

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

    // =====================================================
    // Replay Viewer
    // =====================================================

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

    // =====================================================
    // Unknown
    // =====================================================

    return (

        <UnknownApplicationSurface
            applicationId={
                applicationId
            }
        />
    )
}

// =========================================================
// Runtime Console
// =========================================================

interface RuntimeConsoleSurfaceProps {

    runtimeOS: RuntimeOS
}

const RuntimeConsoleSurface: React.FC<
    RuntimeConsoleSurfaceProps
> = ({
    runtimeOS
}) => {

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

            <pre
                className="
                    whitespace-pre-wrap
                    break-all
                    opacity-70
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
// Graph Debugger
// =========================================================

interface GraphDebuggerSurfaceProps {

    runtimeOS: RuntimeOS
}

const GraphDebuggerSurface: React.FC<
    GraphDebuggerSurfaceProps
> = ({
    runtimeOS
}) => {

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
                    text-cyan-400
                    font-semibold
                    mb-4
                "
            >
                Runtime Graph Debugger
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

                        runtimeOS
                            .store
                            .getGraphNodes(),

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
> = () => {

    return (

        <div
            className="
                w-full
                h-full
                bg-neutral-950
                text-white
                p-6
                overflow-auto
            "
        >

            <div
                className="
                    text-purple-400
                    text-lg
                    font-semibold
                    mb-6
                "
            >
                Tensor Inspector
            </div>

            <div
                className="
                    grid
                    grid-cols-3
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
                                rounded-xl
                                border
                                border-neutral-800
                                bg-neutral-900
                                flex
                                items-center
                                justify-center
                                text-xl
                                font-mono
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
> = ({
    runtimeOS
}) => {

    const replay =
        runtimeOS
            .store
            .getTimeline()

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
                    mb-2
                "
            >
                Replay Timeline
            </div>

            {
                replay
                    .slice()
                    .reverse()
                    .map(

                        (
                            frame,
                            index
                        ) => (

                            <div
                                key={index}
                                className="
                                    border-b
                                    border-neutral-900
                                    pb-2
                                "
                            >

                                <div>
                                    {
                                        frame
                                            .event_type
                                    }
                                </div>

                                <div
                                    className="
                                        opacity-50
                                    "
                                >
                                    seq:
                                    {" "}
                                    {
                                        frame
                                            .sequence_id
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
// Loading Surface
// =========================================================

interface LoadingSurfaceProps {

    label: string
}

const LoadingSurface: React.FC<
    LoadingSurfaceProps
> = ({
    label
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
                text-cyan-400
                font-mono
                text-sm
            "
        >

            loading_runtime_app:
            {" "}
            {label}

        </div>
    )
}

// =========================================================
// Calculator Fallback
// =========================================================

const CalculatorFallbackSurface: React.FC =
() => {

    return (

        <FallbackSurface
            title="Calculator Surface Missing"
            description="
                upstream runtime calculator module
                not yet available
            "
        />
    )
}

// =========================================================
// Graph Projection Fallback
// =========================================================

const GraphProjectionFallbackSurface:
React.FC = () => {

    return (

        <FallbackSurface
            title="
                Graph Projection Missing
            "
            description="
                upstream graph projection
                module not yet available
            "
        />
    )
}

// =========================================================
// Breadboard Fallback
// =========================================================

const BreadboardFallbackSurface:
React.FC = () => {

    return (

        <FallbackSurface
            title="
                Breadboard Missing
            "
            description="
                upstream breadboard
                module not yet available
            "
        />
    )
}

// =========================================================
// Overlay Fallback
// =========================================================

const OverlayFallbackSurface:
React.FC = () => {

    return null
}

// =========================================================
// Shared Fallback
// =========================================================

interface FallbackSurfaceProps {

    title: string

    description: string
}

const FallbackSurface: React.FC<
    FallbackSurfaceProps
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
                flex
                items-center
                justify-center
                p-8
            "
        >

            <div
                className="
                    max-w-md
                    rounded-2xl
                    border
                    border-neutral-800
                    bg-neutral-900
                    p-6
                    text-center
                    flex
                    flex-col
                    gap-4
                "
            >

                <div
                    className="
                        text-lg
                        text-yellow-400
                        font-semibold
                    "
                >
                    {title}
                </div>

                <div
                    className="
                        text-sm
                        text-neutral-400
                        leading-relaxed
                    "
                >
                    {description}
                </div>

            </div>

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