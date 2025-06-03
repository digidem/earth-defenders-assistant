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

  const mimeType = documentMsg.mimetype;
  if (
    mimeType !== "application/pdf" &&
    mimeType !== "text/csv" &&
    mimeType !== "application/csv"
  ) {
    return false;
  }

  try {
    const fileBuffer = await downloadMediaMessage(message, "buffer", {});
    if (!fileBuffer) {
      await sock.sendMessage(
        chatId,
        { text: "Não foi possível baixar o arquivo." },
        { quoted: message },
      );
      await react(message, "error");
      return true;
    }

    const phoneNumber = getPhoneNumber(message);
    const platformUserId = `whatsapp_${phoneNumber}`;

    const formData = new FormData();
    formData.append(
      "file",
      new Blob([fileBuffer], { type: mimeType }),
      documentMsg.fileName ||
        (mimeType.includes("csv") ? "document.csv" : "document.pdf"),
    );
    formData.append("ttl_days", "1"); // Changed from "30" to "1"
    formData.append("user_platform_id", platformUserId);
    formData.append("platform", "whatsapp");

    logger.info(`Uploading document for user: ${platformUserId}`);

    const uploadApiUrl = `http://localhost:${config.ports.ai_api}/api/documents/upload`;
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
      });
      await sock.sendMessage(
        chatId,
        { text: "Erro ao processar o arquivo. Por favor, tente novamente." },
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
    await sock.sendMessage(
      chatId,
      {
        text: `✅ ${fileType} processado com sucesso!\n\nAgora você pode fazer perguntas sobre o conteúdo deste arquivo diretamente por mensagem.\n\n⏰ O arquivo será mantido por 1 dia.`,
      },
      { quoted: message },
    );
    await react(message, "done");
    return true;
  } catch (error) {
    logger.error("Error in document upload:", error);
    await sock.sendMessage(
      chatId,
      { text: "Erro ao processar o arquivo. Por favor, tente novamente." },
      { quoted: message },
    );
    await react(message, "error");
    return true;
  }
}
