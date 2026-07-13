/**
 * =========================================================
 * RuntimeCommandClient
 * =========================================================
 *
 * Browser-side command requester for Pass 047.
 *
 * IMPORTANT:
 * The GUI may request actions, but it may not mutate runtime truth directly.
 * Every command is submitted to FastAPI and must be admitted through the
 * zero-bypass / kernel-derived command authority loop before the GUI updates
 * from websocket feedback.
 */

export interface RuntimeCommandClientConfig {
    commandEndpoint: string
}

export interface RuntimeCommandEnvelope {
    schema: "HHS_LIVE_GUI_COMMAND_ENVELOPE_V1"
    command_id?: string
    surface_id: string
    requested_operation: string
    target_surface?: string
    contract_schema?: string
    client_sequence_id: number
    payload: Record<string, unknown>
    requires_admissibility: boolean
}

export interface RuntimeCommandResult {
    schema?: string
    ok?: boolean
    status?: string
    command_id?: string
    command?: RuntimeCommandEnvelope
    statuses?: string[]
    command_decision_hash72?: string
    websocket_feedback?: Record<string, unknown>
    receipt_hash72?: string
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

export class RuntimeCommandClient {
    private readonly commandEndpoint: string
    private clientSequenceId = 0
    private readonly history: RuntimeCommandResult[] = []

    constructor(config: RuntimeCommandClientConfig) {
        this.commandEndpoint = config.commandEndpoint
    }

    public static fromRuntimeEndpoint(runtimeEndpoint: string): RuntimeCommandClient {
        return new RuntimeCommandClient({
            commandEndpoint: deriveCommandEndpoint(runtimeEndpoint)
        })
    }

    public getCommandEndpoint(): string {
        return this.commandEndpoint
    }

    public getHistory(): RuntimeCommandResult[] {
        return [...this.history]
    }

    public async submitCommand(
        requestedOperation = "runtime.tick",
        payload: Record<string, unknown> = {}
    ): Promise<RuntimeCommandResult> {
        this.clientSequenceId += 1

        const envelope: RuntimeCommandEnvelope = {
            schema: "HHS_LIVE_GUI_COMMAND_ENVELOPE_V1",
            surface_id: "gui:runtime.command_panel",
            requested_operation: requestedOperation,
            client_sequence_id: this.clientSequenceId,
            payload,
            requires_admissibility: true
        }

        const response = await fetch(this.commandEndpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(envelope)
        })

        const result = await response.json() as RuntimeCommandResult
        this.history.push(result)
        while (this.history.length > 256) {
            this.history.shift()
        }
        return result
    }
}

export default RuntimeCommandClient
