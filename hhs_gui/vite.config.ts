import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],

  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: false,
    cors: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },
      "/v1": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },
      "/ws": {
        target: "ws://127.0.0.1:8000",
        ws: true,
        changeOrigin: true,
        secure: false,
      },
    },
  },

  preview: {
    host: "0.0.0.0",
    port: 4173,
  },

  optimizeDeps: {
    include: ["react", "react-dom/client"],
  },

  build: {
    target: "es2018",
    cssTarget: "chrome61",
    modulePreload: { polyfill: true },
    sourcemap: true,
    chunkSizeWarningLimit: 2400,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },

  resolve: {
    // State/orchestration classes use .ts; React views use .tsx. Resolve the
    // class module first so a same-stem view can never replace a constructor.
    extensions: [".ts", ".tsx", ".jsx", ".js", ".json"],
  },

  define: {
    __HHS_RUNTIME__: true,
  },
})
