import { type WAMessage, downloadMediaMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
import { BOT_PREFIX } from "../constants";
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
    // Extract message content and phone number
    const messageContent =
      message.message?.conversation ||
      message.message?.extendedTextMessage?.text ||
      "";
    const phoneNumber = getPhoneNumber(message);

    let audioBlob: Blob | undefined;

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

      if (isAudio && mimetype) {
        audioBlob = new Blob([media], { type: mimetype });
      }
    }

    // Create FormData
    const formData = new FormData();
    formData.append("message", messageContent);
    formData.append("session_id", phoneNumber);

    // Add audio if present
    if (audioBlob) {
      formData.append("audio", audioBlob, "audio.ogg");
    }

    // Make API request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minute timeout (10 * 60 * 1000 ms)

    const response = await fetch(
      "http://127.0.0.1:8083/api/classifier/classify",
      {
        method: "POST",
        headers: {
          accept: "application/json",
        },
        body: formData,
        signal: controller.signal,
      },
    );

    clearTimeout(timeoutId); // Clear timeout if request completes

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.result) return ERROR_MESSAGES.NO_RESPONSE;

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
