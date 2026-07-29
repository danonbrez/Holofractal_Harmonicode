import React from "react"
import ReactDOM from "react-dom/client"

import RuntimeDesktop from "./runtime_os/core/RuntimeDesktop"
import { RuntimeOS } from "./runtime_os/core/RuntimeOS"

import "./index.css"

const runtimeOS = new RuntimeOS({
    runtimeEndpoint: "/ws/runtime",
    replayEndpoint: "/ws/replay",
    graphEndpoint: "/ws/graph",
    transportEndpoint: "/ws/transport",
    diagnosticsEnabled: true,
    mobileMode: window.matchMedia("(max-width: 900px)").matches
})

const rootElement = document.getElementById("root")

if (!rootElement) {
    throw new Error("Missing root element")
}

const root = ReactDOM.createRoot(rootElement)

root.render(
    <React.StrictMode>
        <RuntimeDesktop runtimeOS={runtimeOS} />
    </React.StrictMode>
)

;(window as typeof window & {
    __HHS_RUNTIME_OS__?: RuntimeOS
}).__HHS_RUNTIME_OS__ = runtimeOS

async function bootstrap(): Promise<void> {
    try {
        await runtimeOS.initialize()
        console.log("[main] RuntimeOS initialized")
    } catch (error) {
        console.warn(
            "[main] RuntimeOS mounted in disconnected projection mode",
            error
        )
    }
}

void bootstrap()

if (import.meta.hot) {
    import.meta.hot.dispose(() => {
        runtimeOS.destroy()
    })
}
