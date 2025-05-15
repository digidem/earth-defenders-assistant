import { resolve } from "node:path";
import { URL, fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: "::",
    port: "8081",
  },
  define: {
    "process.env.VITE_OPENPANEL_CLIENT_ID": JSON.stringify(
      process.env.VITE_OPENPANEL_CLIENT_ID,
    ),
  },
  base: process.env.BASE_URL || "/",
  plugins: [react()],
  resolve: {
    alias: [
      {
        find: "@",
        replacement: fileURLToPath(new URL("./src", import.meta.url)),
      },
      {
        find: "lib",
        replacement: resolve(__dirname, "lib"),
      },
    ],
  },
});
