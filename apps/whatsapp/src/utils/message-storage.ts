import { config } from "@eda/config";
import { logger } from "@eda/logger";
import type { proto } from "@whiskeysockets/baileys";
import { downloadMediaMessage } from "@whiskeysockets/baileys";
import { getPhoneNumber, getRemoteJid } from "../utils";

export async function storeGroupMessage(message: proto.IWebMessageInfo) {
  try {
    const messageText =
      message.message?.conversation ||
      message.message?.extendedTextMessage?.text ||
      message.message?.imageMessage?.caption ||
      "";

    const senderNumber = getPhoneNumber(message);

    // Don't store bot's own messages
    if (message.key.fromMe) return;

    const groupId = getRemoteJid(message);
    const platformUserId = `whatsapp_${senderNumber}`;
    const senderName = message.pushName || senderNumber;

    // Handle different types of messages
    await handleTextMessage(
      messageText,
      platformUserId,
      groupId,
      senderName,
      message,
    );
    await handleDocumentMessage(message, platformUserId, groupId, senderName);
    await handleAudioMessage(message, platformUserId, groupId, senderName);
  } catch (error) {
    logger.error("Error storing group message:", error);
  }
}

async function handleTextMessage(
  messageText: string,
  platformUserId: string,
  groupId: string,
  senderName: string,
  message: proto.IWebMessageInfo,
) {
  // Only store text messages that have content
  if (!messageText.trim()) return;

  const aiApiUrl = `${config.services.whatsapp.ai_api_base_url}:${config.ports.ai_api}/api/message_handler/store-group-message`;

  const requestBody = {
    user_platform_id: platformUserId,
    platform: "whatsapp",
    message: messageText,
    group_id: groupId,
    sender_name: senderName,
    timestamp: new Date().toISOString(),
  };

  logger.info(
    `Storing group text message from ${senderName} (${platformUserId}) in group ${groupId}`,
  );

  try {
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
      logger.debug(
        `Group text message stored successfully for ${platformUserId}`,
      );
    }
  } catch (error) {
    logger.error("Error storing group text message:", error);
  }
}

async function handleDocumentMessage(
  message: proto.IWebMessageInfo,
  platformUserId: string,
  groupId: string,
  senderName: string,
) {
  const documentMsg = message.message?.documentMessage;
  if (!documentMsg) return;

  try {
    logger.info(
      `Processing document from ${senderName} in group ${groupId}: ${documentMsg.fileName}`,
    );

    const fileBuffer = await downloadMediaMessage(message, "buffer", {});
    if (!fileBuffer) {
      logger.error("Failed to download document");
      return;
    }

    const mimeType = documentMsg.mimetype || "application/octet-stream";

    // Only process PDF and CSV files
    if (!mimeType.includes("pdf") && !mimeType.includes("csv")) {
      logger.info(`Skipping unsupported document type: ${mimeType}`);
      return;
    }

    const formData = new FormData();
    formData.append(
      "file",
      new Blob([fileBuffer], { type: mimeType }),
      documentMsg.fileName ||
        (mimeType.includes("csv") ? "document.csv" : "document.pdf"),
    );
    formData.append(
      "ttl_days",
      config.services.whatsapp.group_document_ttl_days.toString(),
    );
    formData.append("user_platform_id", platformUserId);
    formData.append("platform", "whatsapp");
    formData.append("group_id", groupId);
    formData.append("sender_name", senderName);

    const uploadApiUrl = `${config.services.whatsapp.ai_api_base_url}:${config.ports.ai_api}/api/documents/upload`;
    const response = await fetch(uploadApiUrl, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      logger.error("Document upload error", {
        status: response.status,
        error: errorText,
        user: platformUserId,
        group: groupId,
        filename: documentMsg.fileName,
      });
      return;
    }

    const result = await response.json();
    logger.info(
      `Document uploaded successfully for ${senderName} in group ${groupId}: ${documentMsg.fileName}`,
    );
  } catch (error) {
    logger.error("Error processing group document:", {
      error,
      user: platformUserId,
      group: groupId,
      filename: documentMsg?.fileName,
    });
  }
}

async function handleAudioMessage(
  message: proto.IWebMessageInfo,
  platformUserId: string,
  groupId: string,
  senderName: string,
) {
  const audioMsg = message.message?.audioMessage;
  if (!audioMsg) return;

  try {
    logger.info(`Processing audio from ${senderName} in group ${groupId}`);

    const audioBuffer = await downloadMediaMessage(message, "buffer", {});
    if (!audioBuffer) {
      logger.error("Failed to download audio");
      return;
    }

    const formData = new FormData();
    formData.append(
      "file",
      new Blob([audioBuffer]),
      config.services.whatsapp.audio_filename,
    );
    formData.append(
      "language",
      config.services.whatsapp.transcription_language,
    );

    const transcriptionApiUrl = `${config.services.whatsapp.ai_api_base_url}:${config.ports.ai_api}/api/transcription/transcribe`;

    const transcriptionResponse = await fetch(transcriptionApiUrl, {
      method: "POST",
      body: formData,
    });

    if (!transcriptionResponse.ok) {
      const errorText = await transcriptionResponse.text();
      logger.error("Transcription API error", {
        status: transcriptionResponse.status,
        error: errorText,
        user: platformUserId,
        group: groupId,
      });
      return;
    }

    const transcriptionData = await transcriptionResponse.json();

    if (!transcriptionData.success || !transcriptionData.transcription) {
      logger.error("Transcription failed", {
        response: transcriptionData,
        user: platformUserId,
        group: groupId,
      });
      return;
    }

    logger.info(
      `Audio transcribed successfully for ${senderName} in group ${groupId}: "${transcriptionData.transcription.substring(
        0,
        50,
      )}..."`,
    );

    // Store the transcription as a text message
    await handleTextMessage(
      `[AUDIO TRANSCRIPTION]: ${transcriptionData.transcription}`,
      platformUserId,
      groupId,
      senderName,
      message,
    );
  } catch (error) {
    logger.error("Error processing group audio:", {
      error,
      user: platformUserId,
      group: groupId,
    });
  }
}
