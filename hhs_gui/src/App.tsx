import React from "react"

import {
    RuntimeShell
} from "../runtime_os/core/RuntimeShell"

import {
    RuntimeOS
} from "../runtime_os/core/RuntimeOS"

const runtimeOS = new RuntimeOS({

    runtimeEndpoint:
        "ws://localhost:8000/ws/runtime",

    replayEndpoint:
        "ws://localhost:8000/ws/replay",

    graphEndpoint:
        "ws://localhost:8000/ws/graph",

    transportEndpoint:
        "ws://localhost:8000/ws/transport",

    diagnosticsEnabled: true,

    mobileMode: true
})

export default function App() {

    return (
        <RuntimeShell
            runtimeOS={runtimeOS}
        />
    )
}