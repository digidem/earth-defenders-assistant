import { config } from "@eda/config";
import { logger } from "@eda/logger";
import type { proto } from "@whiskeysockets/baileys";
import { getPhoneNumber, getRemoteJid } from "../utils";

export async function storeGroupMessage(message: proto.IWebMessageInfo) {
  try {
    const messageText =
      message.message?.conversation ||
      message.message?.extendedTextMessage?.text ||
      message.message?.imageMessage?.caption ||
      "";

    // Skip empty messages or messages from the bot itself
    if (!messageText.trim()) return;

    const senderNumber = getPhoneNumber(message);
    const botNumber = message.key.fromMe ? "bot" : null;

    // Don't store bot's own messages
    if (message.key.fromMe) return;

    const groupId = getRemoteJid(message);
    const platformUserId = `whatsapp_${senderNumber}`;

    // Get sender name
    const senderName = message.pushName || senderNumber;

    // Call the AI API to store the message
    const aiApiUrl = `http://localhost:${config.ports.ai_api}/api/message_handler/store-group-message`;

    const requestBody = {
      user_platform_id: platformUserId,
      platform: "whatsapp",
      message: messageText,
      group_id: groupId,
      sender_name: senderName,
      timestamp: new Date().toISOString(),
    };

    logger.info(
      `Storing group message from ${senderName} (${platformUserId}) in group ${groupId}`,
    );

    const response = await fetch(aiApiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      logger.error("Failed to store group message", {
        status: response.status,
        error: errorText,
        user: platformUserId,
        group: groupId,
      });
    } else {
      logger.debug(`Group message stored successfully for ${platformUserId}`);
    }
  } catch (error) {
    logger.error("Error storing group message:", error);
  }
}
