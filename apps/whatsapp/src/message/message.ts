import { config } from "@eda/config";
import { logger } from "@eda/logger";
import { type WAMessage, downloadMediaMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
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
    const messageContent =
      message.message?.conversation ||
      message.message?.extendedTextMessage?.text ||
      "";
    const phoneNumber = getPhoneNumber(message);

    // Format user_platform_id properly with platform prefix
    const platformUserId = `whatsapp_${phoneNumber}`;

    // Create multipart form data for the request
    const formData = new FormData();

    // Add text message if present
    if (messageContent) {
      formData.append("message", messageContent);
    }

    // Add properly formatted user platform id and platform
    formData.append("user_platform_id", platformUserId);
    formData.append("platform", "whatsapp");

    // Handle attachments (images, audio, etc.)
    if (
      message.message?.imageMessage ||
      message.message?.audioMessage ||
      message.message?.documentMessage ||
      message.message?.videoMessage
    ) {
      try {
        const media = await downloadMediaMessage(message, "buffer", {});

        // Get mimetype and filename from the message
        const mimetype =
          message.message?.imageMessage?.mimetype ||
          message.message?.audioMessage?.mimetype ||
          message.message?.documentMessage?.mimetype ||
          message.message?.videoMessage?.mimetype ||
          "application/octet-stream";

        // Fix the fileName access by using only document fileName
        // and generating names for other types
        let filename = message.message?.documentMessage?.fileName || "";

        // If no filename from document, generate one based on type and timestamp
        if (!filename) {
          const timestamp = Date.now();
          if (message.message?.imageMessage) {
            filename = `image-${timestamp}${getExtensionFromMimeType(mimetype)}`;
          } else if (message.message?.videoMessage) {
            filename = `video-${timestamp}${getExtensionFromMimeType(mimetype)}`;
          } else if (message.message?.audioMessage) {
            filename = `audio-${timestamp}${getExtensionFromMimeType(mimetype)}`;
          } else {
            filename = `attachment-${timestamp}${getExtensionFromMimeType(mimetype)}`;
          }
        }

        // Log attachment information
        logger.info("Processing attachment", {
          user_platform_id: platformUserId,
          mimetype,
          filename,
        });

        // Add attachment to form data
        if (media instanceof Buffer) {
          const blob = new Blob([media], { type: mimetype });
          formData.append("attachment", blob, filename);
        }
      } catch (attachmentError) {
        logger.error("Failed to process attachment", {
          error: attachmentError,
        });
      }
    }

    // Make API request to AI service
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 min timeout

    // Construct URL using config
    const aiApiUrl = `http://localhost:${config.ports.ai_api}/api/message_handler/handle`;

    logger.info(
      `Sending request to AI API: ${aiApiUrl}, user_platform_id: ${platformUserId}`,
    );

    const response = await fetch(aiApiUrl, {
      method: "POST",
      body: formData,
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

// Helper function to get file extension from mimetype
function getExtensionFromMimeType(mimetype: string): string {
  const mimeToExt: Record<string, string> = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/mp4": ".m4a",
    "audio/webm": ".webm",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "application/pdf": ".pdf",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
      ".xlsx",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
      ".docx",
    "text/plain": ".txt",
    "application/json": ".json",
  };

  return mimeToExt[mimetype] || "";
}
