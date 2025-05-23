import { createHash } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import Cerebras from "@cerebras/cerebras_cloud_sdk";
import { config } from "@eda/config";
import { logger } from "@eda/logger";
import { Groq } from "groq-sdk";
import type { Messages } from "./types";

const DEFAULT_APP_FOLDER = path.join(
  os.homedir(),
  ".earth-defenders-assistant",
);

// Replace environment variables with config
const groqKey = config.api_keys.groq;

// Initialize client with Groq by default
const client = new Groq({
  apiKey: groqKey,
});

// Use the AI model from config
const MODEL = config.ai_models.standard.model;

interface CachedItem<T> {
  data: T;
  timestamp: number;
}

interface CacheOptions {
  duration?: number; // Duration in milliseconds
  subfolder?: string; // Subfolder within DEFAULT_APP_FOLDER
}

// Default cache duration is 1 hour
const DEFAULT_CACHE_DURATION = 60 * 60 * 1000;

function createCache<T>(options: CacheOptions = {}) {
  const { duration = DEFAULT_CACHE_DURATION, subfolder = "simulator/.cache" } =
    options;

  const cacheDir = path.join(DEFAULT_APP_FOLDER, subfolder);
  logger.debug(`Cache directory: ${cacheDir}`);

  async function get(key: string): Promise<T | null> {
    try {
      const cacheFile = path.join(cacheDir, `${key}.json`);
      logger.debug(`Attempting to read cache file: ${cacheFile}`);
      const data = await fs.promises.readFile(cacheFile, "utf8");
      const cached = JSON.parse(data) as CachedItem<T>;

      if (Date.now() - cached.timestamp < duration) {
        logger.debug(`Cache hit for key: ${key}`);
        return cached.data;
      }
      logger.debug(`Cache expired for key: ${key}`);
      return null;
    } catch (error) {
      console.error(error);
      logger.debug(`Cache miss for key: ${key}`, { error });
      return null;
    }
  }

  async function set(key: string, data: T): Promise<void> {
    const item: CachedItem<T> = {
      data,
      timestamp: Date.now(),
    };

    logger.debug(`Creating cache directory: ${cacheDir}`);
    await fs.promises.mkdir(cacheDir, { recursive: true });

    const cacheFile = path.join(cacheDir, `${key}.json`);
    logger.debug(`Writing to cache file: ${cacheFile}`);
    await fs.promises.writeFile(cacheFile, JSON.stringify(item));
  }

  return { get, set };
}

// Create cache instance for message generation
const messageCache = createCache<{
  id: string;
  timestamp: number;
  [key: string]: unknown;
}>();

export async function generateWhatsAppMessage(messages: Messages) {
  const cacheKey = createHash("md5")
    .update(JSON.stringify(messages))
    .digest("hex");

  logger.debug(`Generated cache key: ${cacheKey}`);

  try {
    // Try to get from cache first
    logger.debug("Attempting to retrieve from cache");
    const cached = await messageCache.get(cacheKey);
    if (cached) {
      logger.debug("Found message in cache");
      return cached;
    }

    logger.debug("Cache miss, generating new message");
    const params: ChatCompletionCreateParamsNonStreaming = {
      messages: messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      })),
      model: MODEL,
      response_format: { type: "json_object" },
    };

    logger.debug("Calling AI service", { model: MODEL });
    const generatedMessage = await client.chat.completions.create(params);
    if (!generatedMessage.choices[0]?.message?.content) {
      logger.error("Invalid response from AI service");
      throw new Error("Invalid response from OpenAI");
    }

    const content = generatedMessage.choices[0].message.content;
    const payload = {
      ...JSON.parse(content),
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    };

    logger.debug("Caching generated message");
    await messageCache.set(cacheKey, payload);

    return payload;
  } catch (error) {
    logger.error("Error in message generation:", { error });
    throw error;
  }
}
