import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 4173,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true
      }
    }
  },
  preview: {
    port: 4173,
    host: "0.0.0.0",
    strictPort: true,
    cors: true,
    headers: {
      "Connection": "keep-alive",
      "Keep-Alive": "timeout=60"
    }
  }
});

