/**
 * HHS Runtime Execution Authority
 * ---------------------------------------------------
 * Canonical Runtime OS execution authority layer.
 *
 * Responsibilities:
 *
 * - Kernel-only execution enforcement
 * - Runtime execution authorization
 * - Receipt continuity enforcement
 * - Replay continuity enforcement
 * - Runtime command validation
 * - GUI execution bypass prevention
 * - Runtime authority centralization
 * - Deterministic execution routing
 *
 * CRITICAL:
 *
 * NO GUI COMPONENT MAY:
 *
 * - execute runtime algebra locally
 * - mutate graph state directly
 * - generate receipts
 * - generate replay chains
 * - simulate runtime execution
 * - bypass RuntimeKernelBridge
 * - fork runtime state
 * - fork transport state
 *
 * ALL EXECUTION MUST FLOW:
 *
 * GUI
 * → RuntimeExecutionAuthority
 * → RuntimeKernelBridge
 * → Canonical Runtime
 * → Kernel
 * → Receipt Commit
 * → Replay
 * → Projection Back To GUI
 *
 * Invariants:
 * Δe = 0
 * Ψ = 0
 * Θ15 = true
 * Ω = true
 */

import {
    RuntimeKernelBridge
} from "./RuntimeKernelBridge"

export interface RuntimeExecutionRequest {

    operation: string

    payload?: object

    requiresReceipt?: boolean

    requiresReplayLink?: boolean

    sourceComponent?: string

    timestamp?: number
}

export interface RuntimeExecutionReceipt {

    accepted: boolean

    operation: string

    receiptRequired: boolean

    replayLinked: boolean

    timestamp: number

    authorityPath: string[]
}

export interface RuntimeExecutionAuthorityState {

    initialized: boolean

    authorityLocked: boolean

    runtimeConnected: boolean

    replaySynchronized: boolean

    totalExecutions: number

    rejectedExecutions: number
}

export class RuntimeExecutionAuthority {

    private readonly kernelBridge:
        RuntimeKernelBridge

    public readonly state:
        RuntimeExecutionAuthorityState

    /**
     * ---------------------------------------------------
     * Forbidden Operations
     * ---------------------------------------------------
     */

    private readonly forbiddenPatterns:
        string[]

    constructor(
        kernelBridge: RuntimeKernelBridge
    ) {

        this.kernelBridge =
            kernelBridge

        this.state = {

            initialized: false,

            authorityLocked: true,

            runtimeConnected: false,

            replaySynchronized: false,

            totalExecutions: 0,

            rejectedExecutions: 0
        }

        this.forbiddenPatterns = [

            "local_execute",

            "generate_receipt",

            "generate_replay",

            "mutate_graph",

            "fork_runtime",

            "fork_replay",

            "fork_transport",

            "simulate_kernel",

            "simulate_runtime",

            "parallel_runtime"
        ]
    }

    /**
     * ---------------------------------------------------
     * Initialization
     * ---------------------------------------------------
     */

    public async initialize():
        Promise<void> {

        console.log(
            "[RuntimeExecutionAuthority] initialize"
        )

        this.state.runtimeConnected =
            this.kernelBridge
                .state.connected

        this.state.replaySynchronized =
            this.kernelBridge
                .state.replaySynchronized

        this.state.initialized = true

        console.log(
            "[RuntimeExecutionAuthority] authority locked"
        )
    }

    /**
     * ---------------------------------------------------
     * Execution Validation
     * ---------------------------------------------------
     */

    private validateRequest(
        request:
            RuntimeExecutionRequest
    ): boolean {

        const operation =
            request.operation
                .toLowerCase()

        for (
            const forbidden
            of this.forbiddenPatterns
        ) {

            if (
                operation.includes(
                    forbidden
                )
            ) {

                console.error(

                    "[RuntimeExecutionAuthority] forbidden operation",

                    forbidden
                )

                return false
            }
        }

        /**
         * Runtime bridge required
         */

        if (
            !this.kernelBridge
                .state.connected
        ) {

            console.error(

                "[RuntimeExecutionAuthority] runtime disconnected"
            )

            return false
        }

        return true
    }

    /**
     * ---------------------------------------------------
     * Canonical Execution Path
     * ---------------------------------------------------
     */

    public execute(
        request:
            RuntimeExecutionRequest
    ): RuntimeExecutionReceipt {

        this.state.totalExecutions += 1

        const valid =
            this.validateRequest(
                request
            )

        if (!valid) {

            this.state.rejectedExecutions += 1

            return {

                accepted: false,

                operation:
                    request.operation,

                receiptRequired:
                    true,

                replayLinked:
                    false,

                timestamp:
                    Date.now(),

                authorityPath: [

                    "GUI",

                    "RuntimeExecutionAuthority",

                    "REJECTED"
                ]
            }
        }

        /**
         * ------------------------------------------------
         * Canonical Execution Dispatch
         * ------------------------------------------------
         */

        this.kernelBridge.dispatchCommand(

            request.operation,

            {

                ...request.payload,

                authorityLocked: true,

                replayRequired:

                    request
                        .requiresReplayLink
                        ?? true,

                receiptRequired:

                    request
                        .requiresReceipt
                        ?? true,

                sourceComponent:

                    request
                        .sourceComponent
            }
        )

        console.log(

            "[RuntimeExecutionAuthority] execute",

            request.operation
        )

        return {

            accepted: true,

            operation:
                request.operation,

            receiptRequired:
                request
                    .requiresReceipt
                    ?? true,

            replayLinked:
                request
                    .requiresReplayLink
                    ?? true,

            timestamp:
                Date.now(),

            authorityPath: [

                "GUI",

                "RuntimeExecutionAuthority",

                "RuntimeKernelBridge",

                "CanonicalRuntime",

                "Kernel",

                "ReceiptCommit",

                "Replay",

                "Projection"
            ]
        }
    }

    /**
     * ---------------------------------------------------
     * Graph Mutation Protection
     * ---------------------------------------------------
     */

    public prohibitDirectGraphMutation():
        never {

        throw new Error(

            "[RuntimeExecutionAuthority] direct graph mutation prohibited"
        )
    }

    /**
     * ---------------------------------------------------
     * Replay Mutation Protection
     * ---------------------------------------------------
     */

    public prohibitReplayGeneration():
        never {

        throw new Error(

            "[RuntimeExecutionAuthority] local replay generation prohibited"
        )
    }

    /**
     * ---------------------------------------------------
     * Receipt Generation Protection
     * ---------------------------------------------------
     */

    public prohibitReceiptGeneration():
        never {

        throw new Error(

            "[RuntimeExecutionAuthority] local receipt generation prohibited"
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Simulation Protection
     * ---------------------------------------------------
     */

    public prohibitRuntimeSimulation():
        never {

        throw new Error(

            "[RuntimeExecutionAuthority] local runtime simulation prohibited"
        )
    }

    /**
     * ---------------------------------------------------
     * Runtime Metrics
     * ---------------------------------------------------
     */

    public getMetrics(): object {

        return {

            initialized:
                this.state.initialized,

            authorityLocked:
                this.state.authorityLocked,

            runtimeConnected:
                this.state.runtimeConnected,

            replaySynchronized:
                this.state.replaySynchronized,

            totalExecutions:
                this.state.totalExecutions,

            rejectedExecutions:
                this.state.rejectedExecutions
        }
    }

    /**
     * ---------------------------------------------------
     * Serialization
     * ---------------------------------------------------
     */

    public serialize(): object {

        return {

            state:
                this.state,

            forbiddenPatterns:
                this.forbiddenPatterns
        }
    }
}