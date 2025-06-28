import { config } from "@eda/config";
import { logger } from "@eda/logger";
import type { WAMessage } from "@whiskeysockets/baileys";
import { downloadMediaMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
import { getPhoneNumber, react } from "../utils";

export async function handleDocumentMessage(
  message: WAMessage,
): Promise<boolean> {
  const chatId = message.key.remoteJid;
  const documentMsg = message.message?.documentMessage;
  if (!documentMsg || !chatId) return false;

  try {
    const fileBuffer = await downloadMediaMessage(message, "buffer", {});
    if (!fileBuffer) {
      await sock.sendMessage(
        chatId,
        {
          text: config.services.whatsapp.error_messages
            .DOCUMENT_DOWNLOAD_FAILED,
        },
        { quoted: message },
      );
      await react(message, "error");
      return true;
    }

    const phoneNumber = getPhoneNumber(message);
    const platformUserId = `whatsapp_${phoneNumber}`;

    const mimeType = documentMsg.mimetype || "application/octet-stream";
    const formData = new FormData();
    formData.append(
      "file",
      new Blob([fileBuffer], { type: mimeType }),
      documentMsg.fileName ||
        (mimeType.includes("csv") ? "document.csv" : "document.pdf"),
    );
    formData.append(
      "ttl_days",
      config.services.whatsapp.private_document_ttl_days.toString(),
    );
    formData.append("user_platform_id", platformUserId);
    formData.append("platform", "whatsapp");

    logger.info(`Uploading document for user: ${platformUserId}`);

    const uploadApiUrl = `${config.services.whatsapp.ai_api_base_url}:${config.ports.ai_api}/api/documents/upload`;
    const response = await fetch(uploadApiUrl, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorText = await response.text();
      try {
        const errorJson = JSON.parse(errorText);
        errorText = errorJson.detail || errorText;
      } catch {
        // keep errorText as is
      }
      logger.error("Document upload error", {
        status: response.status,
        error: errorText,
        user: platformUserId,
      });
      await sock.sendMessage(
        chatId,
        { text: `Erro ao processar o arquivo: ${errorText}` },
        { quoted: message },
      );
      await react(message, "error");
      return true;
    }

    const result = await response.json();
    logger.info(
      `Document upload successful for user: ${platformUserId}`,
      result,
    );

    const fileType = mimeType.includes("csv") ? "CSV" : "PDF";
    const successMessage =
      config.services.whatsapp.success_messages.DOCUMENT_PROCESSED.replace(
        "{file_type}",
        fileType,
      ).replace(
        "{ttl_days}",
        config.services.whatsapp.private_document_ttl_days.toString(),
      );

    await sock.sendMessage(
      chatId,
      { text: successMessage },
      { quoted: message },
    );
    await react(message, "done");
    return true;
  } catch (error) {
    logger.error("Error in document upload:", error);
    await sock.sendMessage(
      chatId,
      {
        text: config.services.whatsapp.error_messages
          .DOCUMENT_PROCESSING_FAILED,
      },
      { quoted: message },
    );
    await react(message, "error");
    return true;
  }
}
