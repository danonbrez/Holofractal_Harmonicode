import React, {
    useMemo,
    useState
} from "react"

import type {
    RuntimeOS
} from "./RuntimeOS"

import {
    RuntimeMutationClient,
    RuntimeMutationResult
} from "./RuntimeMutationClient"

export interface RuntimeMutationPanelProps {
    runtimeOS: RuntimeOS
}

const truncate = (value?: unknown): string => {
    const text = String(value ?? "—")
    if (text.length <= 18) {
        return text
    }
    return `${text.slice(0, 10)}…${text.slice(-6)}`
}

export const RuntimeMutationPanel: React.FC<RuntimeMutationPanelProps> = ({
    runtimeOS
}) => {
    const client = useMemo(
        () => RuntimeMutationClient.fromRuntimeEndpoint(
            runtimeOS.config.runtimeEndpoint
        ),
        [runtimeOS]
    )

    const [pending, setPending] =
        useState(false)

    const [lastResult, setLastResult] =
        useState<RuntimeMutationResult | undefined>()

    const [error, setError] =
        useState<string | undefined>()

    const requestMutation = async (operation: string) => {
        setPending(true)
        setError(undefined)
        try {
            const result = await client.requestAuthorizedMutation(operation, {
                source: "RuntimeMutationPanel"
            })
            setLastResult(result)
        } catch (mutationError) {
            setError(
                mutationError instanceof Error
                    ? mutationError.message
                    : String(mutationError)
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
                border-emerald-900/70
                bg-black/80
                backdrop-blur-xl
                p-4
                shadow-2xl
                font-mono
            "
            data-testid="runtime-mutation-panel"
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
                        text-emerald-200
                    "
                >
                    Authorized Mutation Loop
                </div>

                <div
                    className="
                        text-[10px]
                        uppercase
                        tracking-[0.2em]
                        text-neutral-500
                    "
                >
                    NO_UI_EVENT_AS_TRUTH
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
                        border-emerald-700
                        bg-emerald-950/60
                        px-3
                        py-2
                        text-xs
                        text-emerald-100
                        disabled:opacity-40
                    "
                    data-testid="runtime-mutation-tick"
                    disabled={pending}
                    onClick={() => requestMutation("runtime.tick")}
                >
                    Authorized Tick
                </button>

                <button
                    className="
                        rounded-lg
                        border
                        border-teal-700
                        bg-teal-950/60
                        px-3
                        py-2
                        text-xs
                        text-teal-100
                        disabled:opacity-40
                    "
                    data-testid="runtime-mutation-status"
                    disabled={pending}
                    onClick={() => requestMutation("runtime.request_status_snapshot")}
                >
                    Status Snapshot
                </button>

                <button
                    className="
                        rounded-lg
                        border
                        border-amber-700
                        bg-amber-950/60
                        px-3
                        py-2
                        text-xs
                        text-amber-100
                        disabled:opacity-40
                    "
                    data-testid="runtime-mutation-decay-sweep"
                    disabled={pending}
                    onClick={() => requestMutation("expanded_state_decay.sweep")}
                >
                    Decay Sweep
                </button>

                <button
                    className="
                        rounded-lg
                        border
                        border-sky-700
                        bg-sky-950/60
                        px-3
                        py-2
                        text-xs
                        text-sky-100
                        disabled:opacity-40
                    "
                    data-testid="runtime-mutation-semantic-refresh"
                    disabled={pending}
                    onClick={() => requestMutation("semantic_cache.refresh_composition_index")}
                >
                    Refresh Cache
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
                data-testid="runtime-mutation-result"
            >
                <Field label="pending" value={pending ? "true" : "false"} />
                <Field label="status" value={String(lastResult?.status ?? "NO_MUTATION_REQUESTED")} />
                <Field label="ok" value={String(lastResult?.ok ?? "—")} />
                <Field label="mode" value={String(lastResult?.execution_mode ?? "—")} />
                <Field label="receipt" value={truncate(lastResult?.receipt_hash72)} />
                <Field label="pre" value={truncate(lastResult?.pre_state_hash72)} />
                <Field label="transform" value={truncate(lastResult?.transformation_hash72)} />
                <Field label="post" value={truncate(lastResult?.post_state_hash72)} />
                <Field label="feedback" value={truncate((lastResult?.websocket_feedback as Record<string, unknown> | undefined)?.event_hash72)} />
                <Field label="gui_mutated" value={String(lastResult?.gui_mutated_runtime_truth ?? false)} />
                <Field label="error" value={error ?? "—"} />
            </div>

            <div
                className="
                    mt-2
                    text-[10px]
                    text-neutral-600
                "
            >
                GUI may request mutation; kernel-derived authority decides; receipt + WebSocket feedback update projection.
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

export default RuntimeMutationPanel
