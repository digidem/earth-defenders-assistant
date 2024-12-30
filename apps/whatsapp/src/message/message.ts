import { logger } from "@trigger.dev/sdk/v3";
import { type WAMessage, downloadMediaMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
import { BOT_PREFIX } from "../constants";
import { client } from "../trigger/client";
import type { MessagePayload, MessageResponse } from "../types";
import { getPhoneNumber, react } from "../utils";

const IMAGE_ERROR_MSG =
  "Não consigo processar imagens no momento. Por favor, me envie apenas mensagens de texto ou áudio.";

const WAITING_MSG =
  "Estou analisando sua mensagem... Como preciso pensar com cuidado, pode demorar alguns minutos.";

const ERROR_MESSAGES = {
  NO_RESPONSE: "Desculpe, não consegui gerar uma resposta. Tente novamente.",
  HTTP_ERROR: "Ops, tive um problema técnico. Pode tentar novamente?",
  TIMEOUT: "Desculpe, demorei muito para responder. Pode tentar novamente?",
  UNKNOWN: "Ocorreu um erro inesperado. Pode tentar novamente?",
};

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
    const messageContent =
      message.message?.conversation ||
      message.message?.extendedTextMessage?.text ||
      "";
    const phoneNumber = getPhoneNumber(message);

    // Initialize payload first
    const payload: MessagePayload = {
      message: messageContent,
      sessionId: phoneNumber,
    };

    if (message.message?.imageMessage || message.message?.audioMessage) {
      const media = await downloadMediaMessage(message, "buffer", {});
      const mimetype =
        message.message?.imageMessage?.mimetype ||
        message.message?.audioMessage?.mimetype;

      const isImage = mimetype?.includes("image");
      const isAudio = mimetype?.includes("audio");

      // Early return if image is detected
      if (isImage) {
        await sock.sendMessage(
          chatId,
          { text: IMAGE_ERROR_MSG, edit: streamingReply.key },
          { quoted: message },
        );
        await react(message, "done");
        return;
      }

      if (isAudio && mimetype && media instanceof Buffer) {
        logger.info("Received audio message", {
          sessionId: phoneNumber,
          hasAudio: true,
        });
        // Convert Buffer to base64
        payload.audio = media.toString("base64");
      }
    }

    // Use trigger.dev to send message
    const eventResponse = await client.sendEvent({
      name: "message.send",
      payload,
    });

    const result = eventResponse.payload as MessageResponse;

    if (!result?.result) {
      throw new Error("No result from API");
    }

    await sock.sendMessage(
      chatId,
      { text: result.result, edit: streamingReply.key },
      { quoted: message },
    );

    await react(message, "done");
  } catch (error) {
    console.error(error);
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
