import { config } from "@eda/config";
import { logger } from "@eda/logger";
import type { WAMessage } from "@whiskeysockets/baileys";
import { downloadMediaMessage } from "@whiskeysockets/baileys";
import { sock } from "../client";
import { getPhoneNumber, react } from "../utils";

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

  try {
    const phoneNumber = getPhoneNumber(message);
    const platformUserId = `whatsapp_${phoneNumber}`;

    const stream = await downloadMediaMessage(message, "buffer", {});
    if (!stream) {
      await sock.sendMessage(
        chatId,
        { text: config.services.whatsapp.error_messages.AUDIO_DOWNLOAD_FAILED },
        { quoted: message },
      );
      await react(message, "error");
      return null;
    }

    const formData = new FormData();

    // WhatsApp audio is typically OGG Opus format, regardless of MIME type
    // Use the configured audio filename and let the server detect the format
    formData.append(
      "file",
      new Blob([stream], { type: "audio/ogg" }),
      config.services.whatsapp.audio_filename,
    );
    formData.append(
      "language",
      config.services.whatsapp.transcription_language,
    );

    logger.info(`Transcribing audio for user: ${platformUserId}`, {
      audioSize: stream.length,
      audioType: audioMsg.mimetype || "unknown",
    });

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
      });
      await sock.sendMessage(
        chatId,
        {
          text: config.services.whatsapp.error_messages
            .AUDIO_TRANSCRIPTION_FAILED,
        },
        { quoted: message },
      );
      await react(message, "error");
      return null;
    }

    const transcriptionData = await transcriptionResponse.json();

    if (!transcriptionData.success || !transcriptionData.transcription) {
      logger.error("Transcription failed", {
        response: transcriptionData,
        user: platformUserId,
      });
      await sock.sendMessage(
        chatId,
        {
          text: `Erro ao transcrever o áudio: ${
            transcriptionData.error || "desconhecido"
          }`,
        },
        { quoted: message },
      );
      await react(message, "error");
      return null;
    }

    logger.info(
      `Audio transcribed successfully for user: ${platformUserId}, transcription: "${transcriptionData.transcription.substring(
        0,
        50,
      )}..."`,
    );

    return transcriptionData.transcription;
  } catch (error) {
    const phoneNumber = getPhoneNumber(message);
    const platformUserId = `whatsapp_${phoneNumber}`;

    logger.error("Error in audio transcription:", {
      error,
      user: platformUserId,
    });
    await sock.sendMessage(
      chatId,
      {
        text: config.services.whatsapp.error_messages
          .AUDIO_TRANSCRIPTION_FAILED,
      },
      { quoted: message },
    );
    await react(message, "error");
    return null;
  }
}
