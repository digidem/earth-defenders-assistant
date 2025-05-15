import { createServer } from "node:http";
import { config } from "@eda/config";
import next from "next";
import { env } from "./env.mjs";

const dev = process.env.NODE_ENV !== "production";
const app = next({ dev });
const handle = app.getRequestHandler();

async function startServer() {
  try {
    await app.prepare();
    const port = env.PORT || config.ports.dashboard;

    createServer(handle).listen(port, () => {
      console.log(`> Ready on http://localhost:${port}`);
    });
  } catch (error) {
    console.error("Error starting server:", error);
    process.exit(1);
  }
}

if (require.main === module) {
  startServer();
}

export default startServer;
