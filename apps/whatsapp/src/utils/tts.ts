import { config } from "@eda/config";
import { logger } from "@eda/logger";
import { ENABLE_TTS } from "../constants";

export interface TTSOptions {
  text: string;
  language_code?: string;
  voice_name?: string;
  audio_encoding?: string;
  pitch?: number;
  speaking_rate?: number;
}

export async function generateTTSAudio(
  options: TTSOptions,
): Promise<Buffer | null> {
  if (!ENABLE_TTS) {
    logger.debug("TTS is disabled, skipping audio generation");
    return null;
  }

  try {
    const ttsApiUrl = `${config.services.whatsapp.ai_api_base_url}:${config.ports.ai_api}/api/tts/generate-and-download`;

    const requestBody = {
      text: options.text,
      language_code: options.language_code,
      voice_name: options.voice_name,
      audio_encoding: options.audio_encoding || "OGG_OPUS", // Default to OGG_OPUS for WhatsApp
      pitch: options.pitch,
      speaking_rate: options.speaking_rate,
    };

    logger.info(
      `Generating TTS audio for text: "${options.text.substring(0, 50)}..."`,
    );

    const response = await fetch(ttsApiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      logger.error("TTS API error", {
        status: response.status,
        statusText: response.statusText,
        error: errorText,
      });
      return null;
    }

    const audioBuffer = Buffer.from(await response.arrayBuffer());
    logger.info(
      `TTS audio generated successfully, size: ${audioBuffer.length} bytes`,
    );

    return audioBuffer;
  } catch (error) {
    logger.error("Error generating TTS audio:", error);
    return null;
  }
}

export function shouldUseTTS(messageLength: number): boolean {
  const result =
    ENABLE_TTS &&
    messageLength >= config.services.whatsapp.min_tts_length &&
    messageLength <= config.services.whatsapp.max_tts_length;
  return result;
}
