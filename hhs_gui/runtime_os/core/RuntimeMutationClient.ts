/**
 * =========================================================
 * RuntimeMutationClient
 * =========================================================
 *
 * Browser-side request client for Pass 048 authorized live mutations.
 *
 * The GUI may request a mutation, but it may not mutate runtime truth directly.
 * Success is not assumed until FastAPI returns a mutation receipt and the
 * websocket projection reports the resulting kernel/runtime feedback.
 */

export interface RuntimeMutationClientConfig {
    commandEndpoint: string
}

export interface RuntimeMutationCommandEnvelope {
    schema: "HHS_LIVE_GUI_COMMAND_ENVELOPE_V1"
    surface_id: string
    requested_operation: string
    target_surface?: string
    contract_schema?: string
    client_sequence_id: number
    payload: Record<string, unknown>
    requires_admissibility: boolean
    execution_mode: "AUTHORIZED_MUTATION"
}

export interface RuntimeMutationResult {
    ok?: boolean
    status?: string
    command_id?: string
    execution_mode?: string
    receipt_hash72?: string
    pre_state_hash72?: string
    transformation_hash72?: string
    post_state_hash72?: string
    mutation_receipt?: Record<string, unknown>
    websocket_feedback?: Record<string, unknown>
    gui_mutated_runtime_truth?: boolean
    [key: string]: unknown
}

const deriveCommandEndpoint = (runtimeEndpoint: string): string => {
    try {
        const url = new URL(runtimeEndpoint)
        url.protocol = url.protocol === "wss:" ? "https:" : "http:"
        url.pathname = "/api/runtime/gui/command"
        url.search = ""
        url.hash = ""
        return url.toString()
    } catch (_error) {
        return "/api/runtime/gui/command"
    }
}

export class RuntimeMutationClient {
    private readonly commandEndpoint: string
    private clientSequenceId = 0
    private readonly history: RuntimeMutationResult[] = []

    constructor(config: RuntimeMutationClientConfig) {
        this.commandEndpoint = config.commandEndpoint
    }

    public static fromRuntimeEndpoint(runtimeEndpoint: string): RuntimeMutationClient {
        return new RuntimeMutationClient({
            commandEndpoint: deriveCommandEndpoint(runtimeEndpoint)
        })
    }

    public getCommandEndpoint(): string {
        return this.commandEndpoint
    }

    public getHistory(): RuntimeMutationResult[] {
        return [...this.history]
    }

    public async requestAuthorizedMutation(
        requestedOperation = "runtime.request_status_snapshot",
        payload: Record<string, unknown> = {}
    ): Promise<RuntimeMutationResult> {
        this.clientSequenceId += 1

        const envelope: RuntimeMutationCommandEnvelope = {
            schema: "HHS_LIVE_GUI_COMMAND_ENVELOPE_V1",
            surface_id: "gui:runtime.mutation_panel",
            requested_operation: requestedOperation,
            client_sequence_id: this.clientSequenceId,
            payload: {
                ...payload,
                gui_mutation_attempted: false,
                assume_success_locally: false
            },
            requires_admissibility: true,
            execution_mode: "AUTHORIZED_MUTATION"
        }

        const response = await fetch(this.commandEndpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(envelope)
        })

        const result = await response.json() as RuntimeMutationResult
        this.history.push(result)
        while (this.history.length > 256) {
            this.history.shift()
        }
        return result
    }
}

export default RuntimeMutationClient
