import path from "path";
import { config } from "@eda/config";
import { logger } from "@eda/logger";
import type { WAMessage } from "@whiskeysockets/baileys";
import { downloadMediaMessage } from "@whiskeysockets/baileys";
import { writeFile } from "fs/promises";
import { sock } from "../client";
import { handleAudioMessage } from "../handlers/audioHandler";
import { handleDocumentMessage } from "../handlers/documentHandler";
import { getPhoneNumber, react } from "../utils";

const WAITING_MSG =
  "Estou analisando sua mensagem... Como preciso pensar com cuidado, pode demorar alguns minutos.";

const ERROR_MESSAGES = {
  NO_RESPONSE: "Desculpe, não consegui gerar uma resposta. Tente novamente.",
  HTTP_ERROR: "Ops, tive um problema técnico. Pode tentar novamente?",
  TIMEOUT: "Desculpe, demorei muito para responder. Pode tentar novamente?",
  UNKNOWN: "Ocorreu um erro inesperado. Pode tentar novamente?",
};

interface MessagePayload {
  message?: string;
  user_platform_id: string;
  platform: string;
}

export async function handleMessage(message: WAMessage) {
  await react(message, "working");

  const chatId = message.key.remoteJid;
  if (!chatId) {
    return console.error("Invalid chat ID");
  }

  const streamingReply = await sock.sendMessage(
    chatId,
    { text: WAITING_MSG },
    { quoted: message },
  );

  if (!streamingReply) return console.error("No streaming reply");

  try {
    // 1. Handle document (PDF/CSV) uploads
    const handledDocument = await handleDocumentMessage(message);
    if (handledDocument) return;

    // 2. Handle audio messages
    let messageContent =
      message.message?.conversation ||
      message.message?.extendedTextMessage?.text ||
      "";

    const audioMsg =
      message.message?.audioMessage ||
      message.message?.extendedTextMessage?.contextInfo?.quotedMessage
        ?.audioMessage;

    if (audioMsg) {
      const transcription = await handleAudioMessage(message);
      if (!transcription) return;
      messageContent = transcription;
    }

    if (!messageContent.trim()) {
      throw new Error("No valid input provided");
    }

    const phoneNumber = getPhoneNumber(message);
    const platformUserId = `whatsapp_${phoneNumber}`;

    // Call message handler with JSON payload
    const aiApiUrl = `http://localhost:${config.ports.ai_api}/api/message_handler/handle`;

    const payload: MessagePayload = {
      message: messageContent,
      user_platform_id: platformUserId,
      platform: "whatsapp",
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 min timeout

    logger.info(
      `Sending request to AI API: ${aiApiUrl}, user_platform_id: ${platformUserId}`,
    );

    const response = await fetch(aiApiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      logger.error("AI API error response", {
        status: response.status,
        statusText: response.statusText,
      });
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.result) {
      throw new Error("No result from API");
    }

    await sock.sendMessage(
      chatId,
      { text: data.result, edit: streamingReply.key },
      { quoted: message },
    );

    await react(message, "done");
  } catch (error) {
    logger.error("Error handling message", { error });

    const errorMessage =
      error instanceof Error
        ? error.message.includes("timeout")
          ? ERROR_MESSAGES.TIMEOUT
          : error.message.includes("HTTP")
            ? ERROR_MESSAGES.HTTP_ERROR
            : ERROR_MESSAGES.UNKNOWN
        : ERROR_MESSAGES.UNKNOWN;

    await sock.sendMessage(
      chatId,
      { text: errorMessage, edit: streamingReply.key },
      { quoted: message },
    );

    await react(message, "error");
  }
}
