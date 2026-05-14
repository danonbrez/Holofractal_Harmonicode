import React, {
    useEffect,
    useRef,
    useState
} from "react"

import {
    RuntimeOS
} from "./RuntimeOS"

export interface RuntimeConsoleMessage {

    id: string

    timestamp: number

    level:
        | "info"
        | "warn"
        | "error"
        | "runtime"

    message: string
}

export interface RuntimeConsoleProps {

    runtimeOS: RuntimeOS
}

export const RuntimeConsole: React.FC<
    RuntimeConsoleProps
> = ({ runtimeOS }) => {

    const [
        messages,
        setMessages
    ] = useState<
        RuntimeConsoleMessage[]
    >([])

    const [
        command,
        setCommand
    ] = useState("")

    const scrollRef =
        useRef<HTMLDivElement>(null)

    /**
     * ---------------------------------------------------
     * Console Bootstrap
     * ---------------------------------------------------
     */

    useEffect(() => {

        appendMessage({

            level: "runtime",

            message:
                "Runtime console initialized"
        })

        appendMessage({

            level: "info",

            message:
                "Runtime manifold synchronized"
        })

        appendMessage({

            level: "info",

            message:
                "Replay subsystem online"
        })

    }, [])

    /**
     * ---------------------------------------------------
     * Auto Scroll
     * ---------------------------------------------------
     */

    useEffect(() => {

        if (!scrollRef.current) {

            return
        }

        scrollRef.current.scrollTop =
            scrollRef.current.scrollHeight

    }, [messages])

    /**
     * ---------------------------------------------------
     * Message Append
     * ---------------------------------------------------
     */

    const appendMessage = (
        input: Omit<
            RuntimeConsoleMessage,
            "id" | "timestamp"
        >
    ) => {

        setMessages((prev) => [

            ...prev,

            {

                id:
                    crypto.randomUUID(),

                timestamp:
                    Date.now(),

                ...input
            }
        ])
    }

    /**
     * ---------------------------------------------------
     * Command Execution
     * ---------------------------------------------------
     */

    const executeCommand = () => {

        const trimmed =
            command.trim()

        if (!trimmed) {

            return
        }

        appendMessage({

            level: "runtime",

            message:
                `> ${trimmed}`
        })

        /**
         * --------------------------------------------
         * Placeholder Runtime Command Router
         * --------------------------------------------
         */

        switch (trimmed) {

            case "status":

                appendMessage({

                    level: "info",

                    message:
                        JSON.stringify(
                            runtimeOS.getMetrics(),
                            null,
                            2
                        )
                })

                break

            case "workspace":

                appendMessage({

                    level: "info",

                    message:
                        JSON.stringify(
                            runtimeOS
                                .workspace
                                .serialize(),
                            null,
                            2
                        )
                })

                break

            case "session":

                appendMessage({

                    level: "info",

                    message:
                        JSON.stringify(
                            runtimeOS
                                .session
                                .serialize(),
                            null,
                            2
                        )
                })

                break

            case "clear":

                setMessages([])

                break

            default:

                appendMessage({

                    level: "warn",

                    message:
                        `Unknown command: ${trimmed}`
                })
        }

        setCommand("")
    }

    /**
     * ---------------------------------------------------
     * Message Color
     * ---------------------------------------------------
     */

    const getMessageColor = (
        level:
            RuntimeConsoleMessage["level"]
    ) => {

        switch (level) {

            case "runtime":

                return
                    "text-cyan-400"

            case "warn":

                return
                    "text-yellow-400"

            case "error":

                return
                    "text-red-400"

            default:

                return
                    "text-neutral-300"
        }
    }

    /**
     * ---------------------------------------------------
     * Render
     * ---------------------------------------------------
     */

    return (

        <div
            className="
                w-full
                h-full
                flex
                flex-col
                bg-black
                text-neutral-100
                font-mono
            "
        >

            {/* -------------------------------- */}
            {/* Header */}
            {/* -------------------------------- */}

            <div
                className="
                    h-10
                    border-b
                    border-neutral-800
                    px-4
                    flex
                    items-center
                    justify-between
                    shrink-0
                    bg-neutral-950
                "
            >

                <div
                    className="
                        text-sm
                        font-semibold
                    "
                >
                    Runtime Console
                </div>

                <div
                    className="
                        text-[10px]
                        opacity-50
                    "
                >
                    deterministic execution
                    surface
                </div>

            </div>

            {/* -------------------------------- */}
            {/* Console Output */}
            {/* -------------------------------- */}

            <div
                ref={scrollRef}
                className="
                    flex-1
                    overflow-auto
                    p-4
                    flex
                    flex-col
                    gap-2
                "
            >

                {
                    messages.map((msg) => (

                        <div
                            key={msg.id}
                            className="
                                flex
                                gap-3
                                text-xs
                                leading-relaxed
                                break-all
                            "
                        >

                            <div
                                className="
                                    opacity-40
                                    shrink-0
                                "
                            >
                                {
                                    new Date(
                                        msg.timestamp
                                    )
                                    .toLocaleTimeString()
                                }
                            </div>

                            <div
                                className={
                                    getMessageColor(
                                        msg.level
                                    )
                                }
                            >
                                {msg.message}
                            </div>

                        </div>
                    ))
                }

            </div>

            {/* -------------------------------- */}
            {/* Command Surface */}
            {/* -------------------------------- */}

            <div
                className="
                    border-t
                    border-neutral-800
                    p-3
                    flex
                    items-center
                    gap-3
                    shrink-0
                    bg-neutral-950
                "
            >

                <div
                    className="
                        text-cyan-400
                        text-sm
                    "
                >
                    ❯
                </div>

                <input
                    value={command}
                    onChange={(event) =>
                        setCommand(
                            event.target.value
                        )
                    }
                    onKeyDown={(event) => {

                        if (
                            event.key === "Enter"
                        ) {

                            executeCommand()
                        }
                    }}
                    placeholder="
                        Enter runtime command...
                    "
                    className="
                        flex-1
                        bg-transparent
                        outline-none
                        text-sm
                    "
                />

                <button
                    onClick={
                        executeCommand
                    }
                    className="
                        px-3
                        py-1.5
                        rounded-lg
                        bg-cyan-600
                        hover:bg-cyan-500
                        transition
                        text-xs
                        font-semibold
                    "
                >
                    Execute
                </button>

            </div>

        </div>
    )
}