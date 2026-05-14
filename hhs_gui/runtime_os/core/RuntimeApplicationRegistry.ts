/**
 * =========================================================
 * RuntimeApplicationRegistry
 * =========================================================
 *
 * Canonical Runtime OS application authority layer.
 *
 * Responsibilities:
 *
 * - Runtime application registration
 * - Lazy application loading
 * - Capability metadata
 * - Window presets
 * - Runtime authority tagging
 * - Mount policies
 * - Optional application continuity
 *
 * IMPORTANT:
 * ---------------------------------------------------------
 * Runtime applications MUST be treated as optional
 * authorities during active upstream development.
 *
 * Missing applications MUST NOT crash the Runtime OS.
 */

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

    // -----------------------------------------------------

    public has(
        id: string
    ): boolean {

        return this.applications.has(
            id
        )
    }

    // -----------------------------------------------------

    public all():
        RuntimeApplicationDefinition[] {

        return [

            ...this.applications
                .values()
        ]
    }

    // -----------------------------------------------------

    public byAuthority(

        authority:
            RuntimeApplicationAuthority

    ):
        RuntimeApplicationDefinition[] {

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
    // Lazy Resolution
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
// Registration
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

            import(
                "./RuntimeWindowContent"
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

// ---------------------------------------------------------

runtimeApplicationRegistry.register({

    id:
        "calculator",

    title:
        "Calculator",

    authority:
        "runtime",

    description:
        "HHS calculator runtime surface",

    lazyLoader:
        async () =>

            import(
                "../../runtime_apps/calculator/HHSCalculatorSurface"
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 700,

        height: 520,

        minWidth: 420,

        minHeight: 320,

        resizable: true
    },

    mobileSupported: true
})

// ---------------------------------------------------------

runtimeApplicationRegistry.register({

    id:
        "breadboard",

    title:
        "Breadboard",

    authority:
        "graph",

    description:
        "Runtime transport topology surface",

    lazyLoader:
        async () =>

            import(
                "../../runtime_apps/breadboard/HHSBreadboardSurface"
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 820,

        height: 520,

        minWidth: 520,

        minHeight: 360,

        resizable: true
    },

    experimental: true
})

// ---------------------------------------------------------

runtimeApplicationRegistry.register({

    id:
        "receipt_inspector",

    title:
        "Receipt Inspector",

    authority:
        "instrument",

    description:
        "Runtime receipt lineage inspector",

    lazyLoader:
        async () =>

            import(
                "../../runtime_apps/instruments/ReceiptInspector"
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 980,

        height: 640,

        minWidth: 720,

        minHeight: 420,

        resizable: true
    }
})

// ---------------------------------------------------------

runtimeApplicationRegistry.register({

    id:
        "replay_timeline",

    title:
        "Replay Timeline",

    authority:
        "instrument",

    description:
        "Runtime replay inspection surface",

    lazyLoader:
        async () =>

            import(
                "../../runtime_apps/instruments/ReplayTimeline"
            ),

    fallback:
        UnknownApplicationFallback,

    windowPreset: {

        width: 980,

        height: 640,

        minWidth: 720,

        minHeight: 420,

        resizable: true
    }
})