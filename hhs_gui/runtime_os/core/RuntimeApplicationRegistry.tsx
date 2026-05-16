import React from "react"

// =========================================================
// Types
// =========================================================

export type RuntimeApplicationAuthority =

    | "runtime"
    | "instrument"
    | "graph"
    | "transport"
    | "workspace"
    | "experimental"

// ---------------------------------------------------------

export interface RuntimeApplicationWindowPreset {

    width: number

    height: number

    minWidth?: number

    minHeight?: number

    resizable?: boolean
}

// ---------------------------------------------------------

export interface RuntimeApplicationDefinition {

    id: string

    title: string

    icon?: string

    authority:
        RuntimeApplicationAuthority

    description?: string

    lazyLoader:
        () => Promise<{

            default:
                React.ComponentType<any>
        }>

    fallback?:
        React.ComponentType<any>

    windowPreset:
        RuntimeApplicationWindowPreset

    singleton?: boolean

    mobileSupported?: boolean

    experimental?: boolean
}

// =========================================================
// Safe Runtime Import
// =========================================================

async function safeRuntimeImport(

    loader: () => Promise<any>,

    fallback:
        React.ComponentType<any>

): Promise<{

    default:
        React.ComponentType<any>
}> {

    try {

        return await loader()

    } catch (error) {

        console.error(

            "[RuntimeApplicationRegistry] optional runtime module failure",

            error
        )

        return {

            default:
                fallback
        }
    }
}

// =========================================================
// Fallback
// =========================================================

const UnknownApplicationFallback:
React.FC = () => {

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

            runtime_application_missing

        </div>
    )
}

// =========================================================
// Registry
// =========================================================

export class RuntimeApplicationRegistry {

    private readonly applications =
        new Map<
            string,
            RuntimeApplicationDefinition
        >()

    // =====================================================
    // Register
    // =====================================================

    public register(
        definition:
            RuntimeApplicationDefinition
    ): void {

        this.applications.set(

            definition.id,

            definition
        )

        console.log(

            "[RuntimeApplicationRegistry] register",

            definition.id
        )
    }

    // =====================================================
    // Lookup
    // =====================================================

    public get(
        id: string
    ):
        RuntimeApplicationDefinition
        | undefined {

        return this.applications.get(
            id
        )
    }

    // =====================================================
    // Exists
    // =====================================================

    public has(
        id: string
    ): boolean {

        return this.applications.has(
            id
        )
    }

    // =====================================================
    // All
    // =====================================================

    public all():
        RuntimeApplicationDefinition[] {

        return [

            ...this.applications
                .values()
        ]
    }

    // =====================================================
    // Authority
    // =====================================================

    public byAuthority(

        authority:
            RuntimeApplicationAuthority

    ) {

        return this.all().filter(

            (
                application
            ) => (

                application.authority
                === authority
            )
        )
    }

    // =====================================================
    // Resolve
    // =====================================================

    public resolveLazyComponent(
        id: string
    ) {

        const definition =
            this.get(id)

        if (!definition) {

            return React.lazy(
                async () => ({

                    default:
                        UnknownApplicationFallback
                })
            )
        }

        return React.lazy(
            async () => {

                try {

                    return await definition
                        .lazyLoader()

                } catch (error) {

                    console.error(

                        "[RuntimeApplicationRegistry] lazy load failure",

                        id,

                        error
                    )

                    return {

                        default:

                            definition.fallback

                            ??

                            UnknownApplicationFallback
                    }
                }
            }
        )
    }

    // =====================================================
    // Metrics
    // =====================================================

    public metrics() {

        return {

            registeredApplications:

                this.applications.size,

            applicationIds:

                [...this.applications.keys()]
        }
    }
}

// =========================================================
// Global Registry
// =========================================================

export const runtimeApplicationRegistry =
    new RuntimeApplicationRegistry()

// =========================================================
// Runtime Console
// =========================================================

runtimeApplicationRegistry.register({

    id:
        "runtime_console",

    title:
        "Runtime Console",

    authority:
        "runtime",

    description:
        "Core runtime instrumentation surface",

    lazyLoader:
        async () =>

            safeRuntimeImport(

                () => import(
                    /* @vite-ignore */
                    "./RuntimeWindowContent"
                ),

                UnknownApplicationFallback
            ),

    windowPreset: {

        width: 520,

        height: 420,

        minWidth: 320,

        minHeight: 220,

        resizable: true
    },

    singleton: true
})

// =========================================================
// Calculator
// =========================================================

runtimeApplicationRegistry.register({

    id:
        "calculator",

    title:
        "Calculator",

    authority:
        "runtime",

    description:
        "HHS runtime calculator",

    lazyLoader:
        async () =>

            safeRuntimeImport(

                () => import(
                    /* @vite-ignore */
                    "../../runtime_apps/calculator/HHSCalculatorSurface"
                ),

                UnknownApplicationFallback
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 900,

        height: 620,

        minWidth: 480,

        minHeight: 320,

        resizable: true
    },

    mobileSupported: true
})

// =========================================================
// Graph Projection
// =========================================================

runtimeApplicationRegistry.register({

    id:
        "graph_projection",

    title:
        "Graph Projection",

    authority:
        "graph",

    description:
        "Runtime replay graph projection",

    lazyLoader:
        async () =>

            safeRuntimeImport(

                () => import(
                    /* @vite-ignore */
                    "../../runtime_apps/calculator/HHSCalculatorGraphProjection"
                ),

                UnknownApplicationFallback
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 720,

        height: 620,

        minWidth: 420,

        minHeight: 320,

        resizable: true
    }
})

// =========================================================
// Breadboard
// =========================================================

runtimeApplicationRegistry.register({

    id:
        "breadboard",

    title:
        "Breadboard",

    authority:
        "transport",

    description:
        "Runtime transport topology surface",

    lazyLoader:
        async () =>

            safeRuntimeImport(

                () => import(
                    /* @vite-ignore */
                    "../../runtime_apps/breadboard/HHSRuntimeBreadboard"
                ),

                UnknownApplicationFallback
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 980,

        height: 680,

        minWidth: 620,

        minHeight: 420,

        resizable: true
    },

    experimental: true
})

// =========================================================
// Receipt Inspector
// =========================================================

runtimeApplicationRegistry.register({

    id:
        "receipt_inspector",

    title:
        "Receipt Inspector",

    authority:
        "instrument",

    description:
        "Receipt lineage inspection surface",

    lazyLoader:
        async () =>

            safeRuntimeImport(

                () => import(
                    /* @vite-ignore */
                    "../../runtime_apps/instruments/ReceiptInspector"
                ),

                UnknownApplicationFallback
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 920,

        height: 620,

        minWidth: 520,

        minHeight: 320,

        resizable: true
    }
})

// =========================================================
// Replay Timeline
// =========================================================

runtimeApplicationRegistry.register({

    id:
        "replay_timeline",

    title:
        "Replay Timeline",

    authority:
        "instrument",

    description:
        "Replay continuity timeline surface",

    lazyLoader:
        async () =>

            safeRuntimeImport(

                () => import(
                    /* @vite-ignore */
                    "../../runtime_apps/instruments/ReplayTimeline"
                ),

                UnknownApplicationFallback
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 920,

        height: 620,

        minWidth: 520,

        minHeight: 320,

        resizable: true
    }
})