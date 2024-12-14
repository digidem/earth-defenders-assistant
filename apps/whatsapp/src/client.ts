import type { Boom } from "@hapi/boom";
import {
  DisconnectReason,
  type WASocket,
  fetchLatestBaileysVersion,
  makeWASocket,
  type proto,
  useMultiFileAuthState,
} from "@whiskeysockets/baileys";
import P from "pino";
import { handleCommand } from "./commands/commands_index";
import { CMD_PREFIX } from "./constants";
import { handleMessage } from "./message/message";
import {
  isGroupMessage,
  react,
  shouldIgnore,
  shouldIgnoreUnread,
  shouldReply,
} from "./utils/whatsapp";

const messageQueue: { [key: string]: proto.IWebMessageInfo[] } = {};
let isProcessingMessage = false;

async function processMessageQueue(chatId: string) {
  isProcessingMessage = true;

  while (messageQueue[chatId] && messageQueue[chatId].length > 0) {
    const message = messageQueue[chatId].shift();
    if (message) {
      await handleMessageWithQueue(message);
    }
  }

  isProcessingMessage = false;
}

async function handleMessageWithQueue(message: proto.IWebMessageInfo) {
  const messageBody = message.message?.conversation;
  const isCommand = messageBody?.startsWith(CMD_PREFIX);

  console.log("messageBody:", messageBody);

  if (isCommand) {
    await handleCommand(message);
  } else {
    await handleMessage(message);
  }
}

const { state, saveCreds } = await useMultiFileAuthState("wa_auth");
const { version, isLatest } = await fetchLatestBaileysVersion();
console.log(`using WA v${version.join(".")}, isLatest: ${isLatest}`);

// Create a custom logger with a higher log level
const logger = P({ level: "info" }); // Set to 'warn' to ignore info and debug logs

export let sock: WASocket = makeWASocket({
  version,
  logger,
  printQRInTerminal: true,
  auth: state,
  generateHighQualityLinkPreview: true,
});

const unreadCounts: { [key: string]: number } = {};

async function startSock() {
  sock.ev.process(async (events) => {
    if (events["connection.update"]) {
      const update = events["connection.update"];
      const { connection, lastDisconnect } = update;
      if (connection === "close") {
        if (
          (lastDisconnect?.error as Boom)?.output?.statusCode !==
          DisconnectReason.loggedOut
        ) {
          console.log("Connection closed. Attempting to reconnect...");
          await reconnect();
        } else {
          console.log("Connection closed. You are logged out.");
        }
      }

      console.log("connection update", update);
    }

    if (events["chats.update"]) {
      for (const chat of events["chats.update"]) {
        if (chat.id && chat.unreadCount !== undefined) {
          if (chat.unreadCount !== null) {
            unreadCounts[chat.id] = chat.unreadCount;
          }
        }
      }
    }

    if (events["messages.upsert"]) {
      const upsert = events["messages.upsert"];
      //console.log("recv messages ", JSON.stringify(upsert, undefined, 2));

      if (upsert.type === "notify") {
        for (const message of upsert.messages) {
          const chatId = message.key.remoteJid!;
          const unreadCount = unreadCounts[chatId] || 0;

          if (await shouldIgnore(message)) return;
          if (!(await shouldReply(message))) return;
          if (await shouldIgnoreUnread(message, unreadCount)) return;

          await react(message, "queued");

          // Add the message to the queue
          if (!messageQueue[chatId]) {
            messageQueue[chatId] = [];
          }
          messageQueue[chatId].push(message);

          // Process the queue if not already processing
          if (!isProcessingMessage) {
            await processMessageQueue(chatId);
          }
        }
      }
    }

    // Don't forget to save credentials whenever they are updated
    if (events["creds.update"]) {
      await saveCreds();
    }
  });
}

async function reconnect() {
  let connected = false;
  while (!connected) {
    try {
      sock = makeWASocket({
        version,
        logger,
        printQRInTerminal: true,
        auth: state,
        generateHighQualityLinkPreview: true,
      });
      await startSock();
      connected = true;
    } catch (error) {
      console.log("Reconnection failed, retrying in 5 seconds...", error);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }
}

await startSock();
