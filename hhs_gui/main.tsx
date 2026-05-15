import React from "react"
import ReactDOM from "react-dom/client"

import RuntimeDesktop from "./runtime_os/core/RuntimeDesktop"

import {
    RuntimeOS
} from "./runtime_os/core/RuntimeOS"

// =========================================================
// Styles
// =========================================================

import "./index.css"

// =========================================================
// RuntimeOS
// =========================================================

const runtimeOS =
    new RuntimeOS({

        runtimeEndpoint:
            "/ws/runtime",

        replayEndpoint:
            "/ws/replay",

        graphEndpoint:
            "/ws/graph",

        transportEndpoint:
            "/ws/transport"
    })

// =========================================================
// Bootstrap
// =========================================================

async function bootstrap():

    try {

        console.log(
            "[main] bootstrapping RuntimeOS"
        )

        // -------------------------------------------------
        // Runtime Init
        // -------------------------------------------------

        await runtimeOS.initialize()

        // -------------------------------------------------
        // Root
        // -------------------------------------------------

        const rootElement =
            document.getElementById(
                "root"
            )

        if (!rootElement) {

            throw new Error(

                "Missing root element"
            )
        }

        const root =
            ReactDOM.createRoot(
                rootElement
            )

        // -------------------------------------------------
        // Render
        // -------------------------------------------------

        root.render(

            <React.StrictMode>

                <RuntimeDesktop
                    runtimeOS={
                        runtimeOS
                    }
                />

            </React.StrictMode>
        )

        // -------------------------------------------------
        // Dev Metrics
        // -------------------------------------------------

        if (
            typeof window
            !== "undefined"
        ) {

            ;(
                window as typeof window & {

                    __HHS_RUNTIME_OS__?:
                        RuntimeOS
                }

            ).__HHS_RUNTIME_OS__ =
                runtimeOS
        }

        console.log(
            "[main] RuntimeOS mounted"
        )

    } catch (error) {

        console.error(

            "[main] Runtime bootstrap failure",

            error
        )

        const fallback =
            document.getElementById(
                "root"
            )

        if (fallback) {

            fallback.innerHTML = `

                <div
                    style="
                        position:fixed;
                        inset:0;
                        background:#000;
                        color:#ff6b6b;
                        font-family:monospace;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        padding:32px;
                    "
                >

                    <div
                        style="
                            max-width:720px;
                        "
                    >

                        <h2>
                            Runtime Bootstrap Failure
                        </h2>

                        <pre
                            style="
                                white-space:pre-wrap;
                                overflow:auto;
                            "
                        >

${String(error)}

                        </pre>

                    </div>

                </div>
            `
        }
    }
}

// =========================================================
// Lifecycle
// =========================================================

bootstrap()

// =========================================================
// Hot Reload Cleanup
// =========================================================

if (
    import.meta.hot
) {

    import.meta.hot.dispose(
        () => {

            runtimeOS.destroy()
        }
    )
}