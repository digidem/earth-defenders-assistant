import type { WAMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
import { BOT_PREFIX } from "../constants";
import { react } from "../utils/whatsapp";

export async function handleMessage(message: WAMessage) {
  await react(message, "working");

  const chatId = message.key.remoteJid;
  if (!chatId) {
    return console.error("Invalid chat ID");
  }

  const isGroup = chatId.endsWith("@g.us");
  const streamingReply = await sock.sendMessage(
    chatId,
    { text: "..." },
    { quoted: message },
  );

  if (!streamingReply) return console.error("No streaming reply");

  let response: string;

  response = "Hello World!";

  try {
    if (!response) return "No response found";

    await sock.sendMessage(
      chatId,
      { text: response, edit: streamingReply.key },
      { quoted: message },
    );

    await react(message, "done");
  } catch (error) {
    console.error(error);

    const errorReply = await sock.sendMessage(chatId, {
      text: BOT_PREFIX + (error as Error).message,
    });

    await react(message, "error");
  }
}
