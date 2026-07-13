import React, {
    useMemo,
    useState
} from "react"

import type {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeCommandClient,
    RuntimeCommandResult
} from "./RuntimeCommandClient"

export interface RuntimeCommandPanelProps {
    runtimeOS: RuntimeOS
}

const truncate = (value?: unknown): string => {
    const text = String(value ?? "—")
    if (text.length <= 18) {
        return text
    }
    return `${text.slice(0, 10)}…${text.slice(-6)}`
}

export const RuntimeCommandPanel: React.FC<RuntimeCommandPanelProps> = ({
    runtimeOS
}) => {
    const client = useMemo(
        () => RuntimeCommandClient.fromRuntimeEndpoint(
            runtimeOS.config.runtimeEndpoint
        ),
        [runtimeOS]
    )

    const [pending, setPending] =
        useState(false)

    const [lastResult, setLastResult] =
        useState<RuntimeCommandResult | undefined>()

    const [error, setError] =
        useState<string | undefined>()

    const submit = async (operation: string) => {
        setPending(true)
        setError(undefined)
        try {
            const result = await client.submitCommand(operation, {
                source: "RuntimeCommandPanel",
                gui_mutation_attempted: false
            })
            setLastResult(result)
        } catch (commandError) {
            setError(
                commandError instanceof Error
                    ? commandError.message
                    : String(commandError)
            )
        } finally {
            setPending(false)
        }
    }

    return (
        <div
            className="
                rounded-2xl
                border
                border-fuchsia-900/70
                bg-black/80
                backdrop-blur-xl
                p-4
                shadow-2xl
                font-mono
            "
            data-testid="runtime-command-panel"
        >
            <div
                className="
                    flex
                    items-center
                    justify-between
                    mb-3
                "
            >
                <div
                    className="
                        text-sm
                        font-semibold
                        tracking-wide
                        text-fuchsia-200
                    "
                >
                    Runtime Command Loop
                </div>

                <div
                    className="
                        text-[10px]
                        uppercase
                        tracking-[0.2em]
                        text-neutral-500
                    "
                >
                    REQUEST_ONLY_NO_DIRECT_MUTATION
                </div>
            </div>

            <div
                className="
                    grid
                    grid-cols-2
                    gap-2
                    mb-3
                "
            >
                <button
                    className="
                        rounded-lg
                        border
                        border-fuchsia-700
                        bg-fuchsia-950/60
                        px-3
                        py-2
                        text-xs
                        text-fuchsia-100
                        disabled:opacity-40
                    "
                    data-testid="runtime-command-tick"
                    disabled={pending}
                    onClick={() => submit("runtime.tick")}
                >
                    Request Tick
                </button>

                <button
                    className="
                        rounded-lg
                        border
                        border-cyan-700
                        bg-cyan-950/60
                        px-3
                        py-2
                        text-xs
                        text-cyan-100
                        disabled:opacity-40
                    "
                    data-testid="runtime-command-refresh"
                    disabled={pending}
                    onClick={() => submit("runtime.refresh_projection")}
                >
                    Refresh Projection
                </button>
            </div>

            <div
                className="
                    text-[10px]
                    text-neutral-500
                    break-all
                    mb-2
                "
            >
                endpoint: {client.getCommandEndpoint()}
            </div>

            <div
                className="
                    rounded-xl
                    border
                    border-neutral-800
                    bg-neutral-950/80
                    p-3
                    text-[10px]
                    text-neutral-400
                "
                data-testid="runtime-command-result"
            >
                <Field label="pending" value={pending ? "true" : "false"} />
                <Field label="status" value={String(lastResult?.status ?? "NO_COMMAND_SUBMITTED")} />
                <Field label="ok" value={String(lastResult?.ok ?? "—")} />
                <Field label="command" value={truncate(lastResult?.command_id)} />
                <Field label="decision" value={truncate(lastResult?.command_decision_hash72)} />
                <Field label="feedback" value={truncate((lastResult?.websocket_feedback as Record<string, unknown> | undefined)?.event_hash72)} />
                <Field label="error" value={error ?? "—"} />
            </div>

            <div
                className="
                    mt-2
                    text-[10px]
                    text-neutral-600
                "
            >
                GUI may request; kernel decides; WebSocket feedback updates projection.
            </div>
        </div>
    )
}

const Field: React.FC<{
    label: string
    value: string
}> = ({
    label,
    value
}) => (
    <div
        className="
            flex
            gap-1
            min-w-0
        "
    >
        <span className="text-neutral-600">{label}:</span>
        <span
            className="
                text-neutral-300
                truncate
            "
            title={value}
        >
            {value}
        </span>
    </div>
)

export default RuntimeCommandPanel
