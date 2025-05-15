import { config } from "@eda/config";
import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  shared: {
    VERCEL_URL: z
      .string()
      .optional()
      .transform((v) => (v ? `https://${v}` : undefined)),
    PORT: z.coerce.number().default(config.ports.dashboard),
  },
  server: {
    OPENPANEL_SECRET_KEY: z.string().default(config.api_keys.openpanel.secret),
    RESEND_API_KEY: z.string().default(config.api_keys.resend),
    SUPABASE_SERVICE_KEY: z
      .string()
      .default(config.api_keys.supabase.service_key),
    UPSTASH_REDIS_REST_TOKEN: z
      .string()
      .default(config.services.upstash.redis_token),
    UPSTASH_REDIS_REST_URL: z
      .string()
      .default(config.services.upstash.redis_url),
  },
  client: {
    NEXT_PUBLIC_OPENPANEL_CLIENT_ID: z
      .string()
      .default(config.api_keys.openpanel.client_id),
    NEXT_PUBLIC_SUPABASE_ANON_KEY: z
      .string()
      .default(config.api_keys.supabase.anon_key),
    NEXT_PUBLIC_SUPABASE_URL: z.string().default(config.databases.supabase.url),
  },
  runtimeEnv: process.env,
  skipValidation: !!process.env.CI || !!process.env.SKIP_ENV_VALIDATION,
});
