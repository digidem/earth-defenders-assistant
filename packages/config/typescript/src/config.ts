import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "yaml";
import { z } from "zod";

const ApiKeysSchema = z.object({
  groq: z.string(),
  huggingface: z.string(),
  serper: z.string(),
  langtrace: z.string(),
  trigger: z.string(),
});

const SupabaseConfigSchema = z.object({
  url: z.string(),
  service_key: z.string(),
});

const DatabaseConfigSchema = z.object({
  host: z.string(),
  port: z.number(),
  user: z.string(),
  password: z.string(),
  database: z.string(),
});

const AIModelConfig = z.object({
  provider: z.string(),
  model: z.string(),
  temperature: z.number(),
  description: z.string(),
});

const ReactionsSchema = z.object({
  queued: z.string(),
  working: z.string(),
  done: z.string(),
  error: z.string(),
});

const WhatsAppSchema = z.object({
  bot_prefix: z.string(),
  cmd_prefix: z.string(),
  bot_name: z.string(),
  enable_reactions: z.boolean(),
  reactions: ReactionsSchema,
});

const ConfigSchema = z.object({
  ports: z.record(z.string(), z.number()),
  api_keys: ApiKeysSchema,
  databases: z.object({
    supabase: SupabaseConfigSchema,
    postgres: DatabaseConfigSchema,
  }),
  ai_models: z.object({
    premium: AIModelConfig,
    standard: AIModelConfig,
    basic: AIModelConfig,
  }),
  whatsapp: WhatsAppSchema,
});

type Config = z.infer<typeof ConfigSchema>;

function getConfig(): z.infer<typeof ConfigSchema> {
  const configPath = join(__dirname, "../../../..", "config.yaml");
  const configFile = readFileSync(configPath, "utf8");
  const configData = parse(configFile);
  return ConfigSchema.parse(configData);
}

// Export the config instance and type
export const config = getConfig();
export type { Config };

// Usage example:
// import { ConfigLoader } from '@eda/config';
// const config = ConfigLoader.getConfig();
// const groqKey = config.api_keys.groq;
