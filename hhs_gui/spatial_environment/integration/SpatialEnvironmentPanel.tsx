import React from "react"

export interface SpatialEnvironmentPanelProps {
  className?: string
  title?: string
  source?: string
}

/**
 * Additive Stage 004 integration surface for the existing HHS React/Vite Runtime OS.
 * The spatial environment remains projection/orchestration only and uses
 * same-origin relative VM81 API and WebSocket routes.
 */
export const SpatialEnvironmentPanel: React.FC<SpatialEnvironmentPanelProps> = ({
  className = "",
  title = "VM81 Spatial Environment Stage 004",
  source = "/spatial_environment/index.html"
}) => (
  <iframe
    className={className}
    title={title}
    src={source}
    allow="fullscreen; gamepad"
    style={{ width: "100%", height: "100%", border: 0, background: "#020712" }}
  />
)

export default SpatialEnvironmentPanel
