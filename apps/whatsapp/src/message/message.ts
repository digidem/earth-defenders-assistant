import type { WAMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
import { BOT_PREFIX } from "../constants";
import { getPhoneNumber, react } from "../utils/whatsapp";

export async function handleMessage(message: WAMessage) {
  await react(message, "working");

  const chatId = message.key.remoteJid;
  if (!chatId) {
    return console.error("Invalid chat ID");
  }

  const streamingReply = await sock.sendMessage(
    chatId,
    { text: "..." },
    { quoted: message },
  );

  if (!streamingReply) return console.error("No streaming reply");

  try {
    // Extract message content and phone number
    const messageContent =
      message.message?.conversation ||
      message.message?.extendedTextMessage?.text ||
      "";
    const phoneNumber = getPhoneNumber(message);

    // Create FormData
    const formData = new FormData();
    formData.append("message", messageContent);
    formData.append("session_id", phoneNumber);

    // Make API request
    const response = await fetch(
      "http://127.0.0.1:8083/api/classifier/classify",
      {
        method: "POST",
        headers: {
          accept: "application/json",
        },
        body: formData,
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.result) return "No response found";

    console.log(data.result);

    await sock.sendMessage(
      chatId,
      { text: data.result, edit: streamingReply.key },
      { quoted: message },
    );

    await react(message, "done");
  } catch (error) {
    console.error(error);

    const errorMessage =
      error instanceof Error ? error.message : "An error occurred";
    await sock.sendMessage(chatId, {
      text: BOT_PREFIX + errorMessage,
    });

    await react(message, "error");
  }
}