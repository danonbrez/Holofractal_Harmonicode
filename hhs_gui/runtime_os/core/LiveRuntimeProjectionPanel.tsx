import React, {
    useEffect,
    useState
} from "react"

import type {
    RuntimeOS
} from "./RuntimeOS"

import type {
    RuntimeChannelHealth,
    RuntimeSocketEvent
} from "./RuntimeSocketManager"

export interface LiveRuntimeProjectionPanelProps {
    runtimeOS: RuntimeOS
}

const CHANNEL_LABELS: Record<string, string> = {
    runtime: "Runtime",
    replay: "Replay",
    graph: "Graph",
    transport: "Transport"
}

const truncateHash = (value?: string): string => {
    if (!value) {
        return "—"
    }

    if (value.length <= 18) {
        return value
    }

    return `${value.slice(0, 10)}…${value.slice(-6)}`
}

const statusClass = (status: RuntimeChannelHealth["status"]): string => {
    switch (status) {
        case "LIVE_KERNEL_CONNECTED":
            return "text-emerald-300"
        case "STALE_LIVE_KERNEL_STATE":
            return "text-amber-300"
        default:
            return "text-red-300"
    }
}

const latestEvents = (runtimeOS: RuntimeOS): Record<string, RuntimeSocketEvent | undefined> => ({
    runtime: runtimeOS.socketManager.state.lastRuntimeEvent,
    replay: runtimeOS.socketManager.state.lastReplayEvent,
    graph: runtimeOS.socketManager.state.lastGraphEvent,
    transport: runtimeOS.socketManager.state.lastTransportEvent
})

export const LiveRuntimeProjectionPanel: React.FC<
    LiveRuntimeProjectionPanelProps
> = ({
    runtimeOS
}) => {

    const [channelHealth, setChannelHealth] =
        useState<RuntimeChannelHealth[]>(
            runtimeOS.socketManager.getChannelHealth()
        )

    const [events, setEvents] =
        useState<Record<string, RuntimeSocketEvent | undefined>>(
            latestEvents(runtimeOS)
        )

    useEffect(() => {
        let mounted = true

        const refresh = () => {
            if (!mounted) {
                return
            }

            setChannelHealth(
                runtimeOS.socketManager.getChannelHealth()
            )

            setEvents(
                latestEvents(runtimeOS)
            )
        }

        refresh()

        const interval = window.setInterval(
            refresh,
            250
        )

        return () => {
            mounted = false
            window.clearInterval(interval)
        }
    }, [runtimeOS])

    return (
        <div
            className="
                rounded-2xl
                border
                border-cyan-900/70
                bg-black/80
                backdrop-blur-xl
                p-4
                shadow-2xl
                font-mono
            "
            data-testid="live-runtime-projection-panel"
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
                        text-cyan-200
                    "
                >
                    Live Kernel Projection
                </div>

                <div
                    className="
                        text-[10px]
                        uppercase
                        tracking-[0.2em]
                        text-neutral-500
                    "
                >
                    GUI projection only
                </div>
            </div>

            <div
                className="
                    grid
                    grid-cols-1
                    gap-2
                "
            >
                {
                    channelHealth.map((health) => {
                        const event = events[health.channel]

                        return (
                            <div
                                key={health.channel}
                                className="
                                    rounded-xl
                                    border
                                    border-neutral-800
                                    bg-neutral-950/80
                                    p-3
                                "
                                data-testid={`live-channel-${health.channel}`}
                            >
                                <div
                                    className="
                                        flex
                                        items-center
                                        justify-between
                                        gap-2
                                        mb-2
                                    "
                                >
                                    <div
                                        className="
                                            text-xs
                                            font-semibold
                                            text-white
                                        "
                                    >
                                        {CHANNEL_LABELS[health.channel] ?? health.channel}
                                    </div>

                                    <div
                                        className={`
                                            text-[10px]
                                            uppercase
                                            tracking-wide
                                            ${statusClass(health.status)}
                                        `}
                                    >
                                        {health.status}
                                    </div>
                                </div>

                                <div
                                    className="
                                        grid
                                        grid-cols-2
                                        gap-x-3
                                        gap-y-1
                                        text-[10px]
                                        text-neutral-400
                                    "
                                >
                                    <Field label="endpoint" value={health.endpoint} />
                                    <Field label="events" value={String(health.totalEvents)} />
                                    <Field label="seq" value={String(health.lastSequenceId ?? "—")} />
                                    <Field label="tick" value={String(health.lastKernelTick ?? "—")} />
                                    <Field label="age_ms" value={String(health.lastPacketAgeMs ?? "—")} />
                                    <Field label="receipt" value={truncateHash(health.lastReceiptHash72)} />
                                    <Field label="state" value={truncateHash(health.lastRuntimeStateHash72)} />
                                    <Field label="event" value={truncateHash(health.lastEventHash72)} />
                                </div>

                                <div
                                    className="
                                        mt-2
                                        text-[10px]
                                        text-neutral-500
                                        break-all
                                    "
                                >
                                    payload_keys: {event ? Object.keys(event.payload ?? {}).join(", ") || "none" : "no live kernel packet"}
                                </div>
                            </div>
                        )
                    })
                }
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

export default LiveRuntimeProjectionPanel
