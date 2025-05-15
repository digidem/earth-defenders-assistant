import os from "node:os";
import path from "node:path";
import { logger } from "@eda/logger";
import dotenv from "dotenv";
import mongoose from "mongoose";
import qrcode from "qrcode-terminal";
import { Client, LocalAuth, RemoteAuth } from "whatsapp-web.js";
import { MongoStore } from "wwebjs-mongo";
import { handleMessage } from "./src/messageHandler";
const DEFAULT_APP_FOLDER = path.join(
  os.homedir(),
  ".earth-defenders-assistant",
);

dotenv.config();
const args =
  process.env.NODE_ENV === "production"
    ? ["--no-sandbox", "--disable-setuid-sandbox"]
    : undefined;

async function initializeClient() {
  let client: Client;

  if (process.env.MONGODB_URI) {
    try {
      logger.info("Connecting to MongoDB...");
      await mongoose.connect(process.env.MONGODB_URI);
      logger.info("MongoDB connected successfully");

      const store = new MongoStore({ mongoose: mongoose });
      logger.info("Creating client with RemoteAuth...");
      client = new Client({
        authStrategy: new RemoteAuth({
          store,
          backupSyncIntervalMs: 300000,
        }),
        webVersionCache: {
          type: "remote",
          remotePath:
            "https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2412.54.html",
        },
      });
    } catch (error) {
      logger.error(`Failed to connect to MongoDB: ${error}`);
      process.exit(1);
    }
  } else {
    logger.warn("MONGODB_URI not found, using LocalAuth...");
    client = new Client({
      webVersion: "2.2306.7", // this keeps the Whatsapp Verison with the latest version worked 👍
      puppeteer: {
        args,
      },
      authStrategy: new LocalAuth({
        dataPath: DEFAULT_APP_FOLDER,
      }),
    });
  }

  client.on("qr", (qr: string) => {
    logger.info("Scan the QR code below to log in:");
    qrcode.generate(qr, { small: true });
  });

  client.on("ready", () => {
    logger.info("Client is ready!");
  });

  client.on("message_create", (message) => {
    logger.info(`New message: ${message.body}`);
    handleMessage(message);
  });
  client.initialize();
}

initializeClient().catch((error) => logger.error(`Unhandled error: ${error}`));
