import { motion } from "framer-motion";

export function RuntimeShell() {
  return (
    <div className="runtime-shell">
      <motion.div
        className="runtime-core"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{
          duration: 1.2
        }}
      >
        <div className="runtime-header">
          <div className="runtime-title">
            HHS Runtime OS
          </div>

          <div className="runtime-subtitle">
            Holofractal Harmonicode Execution Surface
          </div>
        </div>

        <div className="runtime-body">
          <div className="runtime-grid">
            <div className="runtime-panel">
              Runtime Kernel
            </div>

            <div className="runtime-panel">
              Tensor Manifold
            </div>

            <div className="runtime-panel">
              WebSocket Stream
            </div>

            <div className="runtime-panel">
              Constraint Graph
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}