import { type WAMessage, downloadMediaMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
import { BOT_PREFIX } from "../constants";
import { getPhoneNumber, react } from "../utils";

const IMAGE_ERROR_MSG =
  "Desculpe, ainda não tenho suporte para processar imagens. Por favor, envie apenas mensagens de texto ou áudio.";

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
