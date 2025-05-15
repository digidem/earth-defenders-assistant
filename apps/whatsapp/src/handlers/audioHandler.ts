import { config } from "@eda/config";
import { logger } from "@eda/logger";
import type { WAMessage } from "@whiskeysockets/baileys";
import { downloadMediaMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
import { react } from "../utils";

export async function handleAudioMessage(
  message: WAMessage,
): Promise<string | null> {
  const audioMsg =
    message.message?.audioMessage ||
    message.message?.extendedTextMessage?.contextInfo?.quotedMessage
      ?.audioMessage;
  if (!audioMsg) return null;

  const chatId = message.key.remoteJid;
  if (!chatId) return null;

  const stream = await downloadMediaMessage(message, "buffer", {});
  if (!stream) {
    await sock.sendMessage(
      chatId,
      { text: "Não consegui baixar o áudio." },
      { quoted: message },
    );
    await react(message, "error");
    return null;
  }

  const formData = new FormData();
  formData.append("file", new Blob([stream]), "audio.ogg");
  formData.append("language", "pt");

  const transcriptionApiUrl = `http://localhost:${config.ports.ai_api}/api/transcription/transcribe`;

  const transcriptionResponse = await fetch(transcriptionApiUrl, {
    method: "POST",
    body: formData,
  });

  if (!transcriptionResponse.ok) {
    logger.error("Transcription API error", {
      status: transcriptionResponse.status,
    });
    await sock.sendMessage(
      chatId,
      { text: "Erro ao transcrever o áudio." },
      { quoted: message },
    );
    await react(message, "error");
    return null;
  }

  const transcriptionData = await transcriptionResponse.json();

  if (!transcriptionData.success || !transcriptionData.transcription) {
    await sock.sendMessage(
      chatId,
      {
        text: `Erro ao transcrever o áudio: ${transcriptionData.error || "desconhecido"}`,
      },
      { quoted: message },
    );
    await react(message, "error");
    return null;
  }

  return transcriptionData.transcription;
}
