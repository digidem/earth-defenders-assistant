import { z } from "zod";

// Database Schemas
export const DatabaseConfigSchema = z.object({
  host: z.string(),
  port: z.number().optional(),
  user: z.string(),
  password: z.string(),
  database: z.string(),
});

export const Neo4jAuthSchema = z.object({
  user: z.string(),
  password: z.string(),
});

const Neo4jConfigSchema = z.object({
  host: z.string(),
  auth: Neo4jAuthSchema,
  plugins: z.array(z.string()),
  healthcheck: z.object({
    interval: z.number(),
    timeout: z.number(),
    retries: z.number(),
  }),
});

const RedisConfigSchema = z.object({
  host: z.string(),
  port: z.number().optional(), // Make port optional
  tls_disabled: z.boolean(),
});

const PocketBaseAdminSchema = z.object({
  email: z.string(),
  password: z.string(),
});

const PocketBaseConfigSchema = z.object({
  url: z.string(),
  admin: PocketBaseAdminSchema,
});

// Service Configs
const WhatsAppConfigSchema = z.object({
  bot_prefix: z.string(),
  cmd_prefix: z.string(),
  bot_name: z.string(),
  enable_reactions: z.boolean(),
  enable_tts: z.boolean(), // Add TTS enable flag
  reactions: z.object({
    queued: z.string(),
    working: z.string(),
    done: z.string(),
    error: z.string(),
  }),
  puppeteer_path: z.string(),
  ignore_messages_warning: z.boolean(),
  mongodb_uri: z.string(),
});

const TriggerConfigSchema = z.object({
  project_id: z.string(),
  api_url: z.string(),
  environment: z.string(),
  runtime: z.string(),
  v3_enabled: z.boolean(),
  concurrency: z.object({
    org_execution_limit: z.number(),
    env_execution_limit: z.number(),
  }),
  auth: z.object({
    magic_link_secret: z.string(),
    session_secret: z.string(),
    encryption_key: z.string(),
    provider_secret: z.string(),
    coordinator_secret: z.string(),
  }),
  deployment: z.object({
    worker: z.object({
      http_port: z.number(),
      coordinator_host: z.string(),
      coordinator_port: z.number(),
    }),
    docker: z.object({
      publish_ip: z.string(),
    }),
  }),
  sentry: z.object({
    auth_token: z.string(),
    dsn: z.string(),
    org: z.string(),
    project: z.string(),
  }),
});

const ResendConfigSchema = z.object({
  from_email: z.string(),
  reply_to: z.string(),
});

const LangTraceConfigSchema = z.object({
  api: z.object({
    host: z.string(),
  }),
  admin: z.object({
    email: z.string(),
    password: z.string(),
    enable_login: z.boolean(),
  }),
  telemetry: z.object({
    enabled: z.boolean(),
  }),
  posthog: z.object({
    host: z.string(),
  }),
});

const DashboardAuthConfigSchema = z.object({
  nextauth_secret: z.string(),
  azure: z.object({
    client_id: z.string(),
    client_secret: z.string(),
    tenant_id: z.string(),
  }),
  google: z.object({
    client_id: z.string(),
    secret: z.string(),
  }),
});

const DashboardConfigSchema = z.object({
  auth: DashboardAuthConfigSchema,
});

const UpstashConfigSchema = z.object({
  redis_url: z.string(),
  redis_token: z.string(),
});

// Add TTS Config Schema
const TTSConfigSchema = z.object({
  provider: z.string(),
  language_code: z.string(),
  voice_name: z.string(),
  audio_encoding: z.string(),
  effects_profile_id: z.array(z.string()),
  pitch: z.number(),
  speaking_rate: z.number(),
  output_format: z.string(),
});

// API Keys
export const ApiKeysSchema = z.object({
  groq: z.string(),
  huggingface: z.string(),
  serper: z.string(),
  langtrace: z.string(),
  trigger: z.string(),
  resend: z.string(),
  openai: z.string(),
  openrouter: z.string(),
  dub: z.string(),
  sentry: z.object({
    auth_token: z.string(),
  }),
  deepseek: z.string(),
  google_ai_studio: z.string(), // Added Google AI Studio API key
  google_cloud: z.object({
    service_account_path: z.string(),
  }),
});

// AI Models
const AIModelConfigSchema = z.object({
  provider: z.string(),
  model: z.string(),
  temperature: z.number(),
  description: z.string(),
});

// Update the AIApiConfig schema
const AIApiConfigSchema = z.object({
  debug: z.boolean(),
  conversation_history_limit: z.number().default(5),
  relevant_history_limit: z.number().default(3),
});

export const ConfigSchema = z.object({
  ports: z.object({
    messaging: z.number(),
    ai_api: z.number(),
    langtrace: z.number(),
    trigger: z.number(),
    remix: z.number(),
    whatsapp: z.number(),
    dashboard: z.number(),
    landingpage: z.number(),
    docs: z.number(),
    db: z.object({
      postgres: z.number(),
      trigger_postgres: z.number(), // Add new port
      langtrace_postgres: z.number(), // Add new port
      redis: z.number(),
      neo4j: z.object({
        http: z.number(),
        bolt: z.number(),
      }),
      clickhouse: z.number(),
    }),
  }),
  api_keys: ApiKeysSchema,
  databases: z.object({
    pocketbase: PocketBaseConfigSchema,
    langtrace_postgres: DatabaseConfigSchema,
    langtrace_clickhouse: z.object({
      host: z.string(),
      user: z.string(),
      password: z.string(),
      database: z.string(),
    }),
    trigger_postgres: DatabaseConfigSchema,
    redis: RedisConfigSchema,
    neo4j: Neo4jConfigSchema,
  }),
  services: z.object({
    ai_api: AIApiConfigSchema, // Use the schema defined above
    whatsapp: WhatsAppConfigSchema,
    trigger: TriggerConfigSchema,
    resend: ResendConfigSchema,
    langtrace: LangTraceConfigSchema,
    dashboard: DashboardConfigSchema,
    upstash: UpstashConfigSchema,
    tts: TTSConfigSchema, // Add TTS configuration
  }),
  ai_models: z.object({
    premium: AIModelConfigSchema,
    standard: AIModelConfigSchema,
    basic: AIModelConfigSchema,
  }),
  access: z.object({
    allowed_users: z.array(z.string()),
    blocked_users: z.array(z.string()),
  }),
});

export type Config = z.infer<typeof ConfigSchema>;
