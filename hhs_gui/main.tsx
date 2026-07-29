import React from "react"
import ReactDOM from "react-dom/client"

import ProductionApp from "./src/ProductionApp"
import "./src/styles/production.css"

type FatalBoundaryState = {
    error: Error | null
}

class FatalBoundary extends React.Component<React.PropsWithChildren, FatalBoundaryState> {
    public state: FatalBoundaryState = { error: null }

    public static getDerivedStateFromError(error: Error): FatalBoundaryState {
        return { error }
    }

    public componentDidCatch(error: Error, info: React.ErrorInfo): void {
        console.error("[HHS Runtime OS] frontend failure", error, info)
        document.documentElement.dataset.hhsMounted = "error"
        document.getElementById("runtime_boot_overlay")?.remove()
    }

    public render(): React.ReactNode {
        if (!this.state.error) return this.props.children
        return (
            <main className="hhs-fatal">
                <section className="hhs-fatal-card">
                    <h1>HHS Runtime OS could not render</h1>
                    <p>The interface stopped on a frontend exception. The error is shown instead of a blank screen.</p>
                    <pre>{this.state.error.stack ?? this.state.error.message}</pre>
                    <button className="hhs-primary" type="button" onClick={() => window.location.reload()}>
                        Reload interface
                    </button>
                </section>
            </main>
        )
    }
}

const rootElement = document.getElementById("root")

if (!rootElement) {
    throw new Error("Missing #root application mount")
}

ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
        <FatalBoundary>
            <ProductionApp />
        </FatalBoundary>
    </React.StrictMode>,
)
