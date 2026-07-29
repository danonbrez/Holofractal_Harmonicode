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
    // Do not ship unrestricted `esnext` syntax to the public mobile surface.
    // ES2018 covers the repository's runtime needs while remaining compatible
    // with older Chromium/Samsung Internet engines and Android WebViews.
    target: "es2018",
    cssTarget: "chrome61",
    modulePreload: { polyfill: true },
    sourcemap: true,
    chunkSizeWarningLimit: 2400,
    rollupOptions: {
      output: {
        // Keep React in the canonical entry chunk. A missing vendor chunk must
        // not prevent the bootstrap boundary from reporting the real failure.
        manualChunks: undefined,
      },
    },
  },

  resolve: {
    extensions: [".tsx", ".ts", ".jsx", ".js", ".json"],
  },

  define: {
    __HHS_RUNTIME__: true,
  },
})
