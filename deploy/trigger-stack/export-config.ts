//@ts-ignore
import { config } from "@eda/config";

const envVars = {
  // Core settings
  PORT: config.ports.trigger,
  REMIX_APP_PORT: config.ports.remix,
  NODE_ENV: "production",
  RUNTIME_PLATFORM: "docker-compose",
  V3_ENABLED: config.services.trigger.v3_enabled,

  // Database settings
  POSTGRES_USER: config.databases.trigger_postgres.user,
  POSTGRES_PASSWORD: config.databases.trigger_postgres.password,
  POSTGRES_DB: config.databases.trigger_postgres.database,
  DATABASE_HOST: "postgres:5432",
  DATABASE_URL: `postgresql://${config.databases.trigger_postgres.user}:${config.databases.trigger_postgres.password}@postgres:5432/${config.databases.trigger_postgres.database}`,
  DIRECT_URL: `postgresql://${config.databases.trigger_postgres.user}:${config.databases.trigger_postgres.password}@postgres:5432/${config.databases.trigger_postgres.database}`, // Add this line

  // Add database ports
  POSTGRES_PORT: config.ports.db.trigger_postgres, // Use trigger-specific port
  REDIS_PORT: config.ports.db.redis,

  // Redis settings
  REDIS_HOST: "redis",
  REDIS_TLS_DISABLED: config.databases.redis.tls_disabled,

  // Auth settings
  MAGIC_LINK_SECRET: config.services.trigger.auth.magic_link_secret,
  SESSION_SECRET: config.services.trigger.auth.session_secret,
  ENCRYPTION_KEY: config.services.trigger.auth.encryption_key,
  PROVIDER_SECRET: config.services.trigger.auth.provider_secret,
  COORDINATOR_SECRET: config.services.trigger.auth.coordinator_secret,

  // Hardcoded values (not in config)
  INTERNAL_OTEL_TRACE_DISABLED: "1",
  INTERNAL_OTEL_TRACE_LOGGING_ENABLED: "0",
  RESTART_POLICY: "unless-stopped",
  TRIGGER_IMAGE_TAG: "v3",
  POSTGRES_IMAGE_TAG: "16",
  REDIS_IMAGE_TAG: "7",
  ELECTRIC_IMAGE_TAG: "latest",
  DOCKER_PUBLISH_IP: "127.0.0.1",
  TRIGGER_PROTOCOL: "http",
  TRIGGER_DOMAIN: `localhost:${config.ports.trigger}`,

  // Worker settings
  HTTP_SERVER_PORT: config.services.trigger.deployment.worker.http_port,
  COORDINATOR_HOST: config.services.trigger.deployment.worker.coordinator_host,
  COORDINATOR_PORT: config.services.trigger.deployment.worker.coordinator_port,
};

for (const [key, value] of Object.entries(envVars)) {
  console.log(`${key}=${value}`);
}
