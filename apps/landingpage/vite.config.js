import { resolve } from "node:path";
import { URL, fileURLToPath } from "node:url";
import { config } from "@eda/config";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    host: "::",
    port: config.ports.landingpage,
  },
  define: {
    "process.env.VITE_OPENPANEL_CLIENT_ID": JSON.stringify(
      config.api_keys.openpanel.client_id,
    ),
  },
  base: "/",
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
