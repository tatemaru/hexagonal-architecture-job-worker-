import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api/jobs/stream": {
        target: "http://api:8000",
        changeOrigin: true,
        headers: { Accept: "text/event-stream" },
      },
      "/api": {
        target: "http://api:8000",
        changeOrigin: true,
      },
    },
  },
});
