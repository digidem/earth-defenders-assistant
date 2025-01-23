//@ts-ignore
import { config } from "@eda/config";

const envVars = {
  // Core settings
  PORT: config.ports.langtrace,

  // Postgres settings
  POSTGRES_HOST: `${config.databases.langtrace_postgres.host}:5432`, // Add port to host
  POSTGRES_USER: config.databases.langtrace_postgres.user,
  POSTGRES_PASSWORD: config.databases.langtrace_postgres.password,
  POSTGRES_DATABASE: config.databases.langtrace_postgres.database,
  POSTGRES_DB: config.databases.langtrace_postgres.database,
  POSTGRES_URL: `postgres://${config.databases.langtrace_postgres.user}:${config.databases.langtrace_postgres.password}@${config.databases.langtrace_postgres.host}:5432/${config.databases.langtrace_postgres.database}`,
  POSTGRES_PRISMA_URL: `postgres://${config.databases.langtrace_postgres.user}:${config.databases.langtrace_postgres.password}@${config.databases.langtrace_postgres.host}:5432/${config.databases.langtrace_postgres.database}?pgbouncer=true&connect_timeout=15`,
  POSTGRES_URL_NO_SSL: `postgres://${config.databases.langtrace_postgres.user}:${config.databases.langtrace_postgres.password}@${config.databases.langtrace_postgres.host}:5432/${config.databases.langtrace_postgres.database}`,
  POSTGRES_URL_NON_POOLING: `postgres://${config.databases.langtrace_postgres.user}:${config.databases.langtrace_postgres.password}@${config.databases.langtrace_postgres.host}:5432/${config.databases.langtrace_postgres.database}`,
  POSTGRES_IMAGE_TAG: "16",
  POSTGRES_PORT: config.ports.db.langtrace_postgres,

  // App settings
  NEXT_PUBLIC_APP_NAME: `http://localhost:${config.ports.langtrace}/api/trace`,
  NEXT_PUBLIC_ENVIRONMENT: "production",
  NEXT_PUBLIC_HOST: `http://localhost:${config.ports.langtrace}`,
  NEXTAUTH_SECRET: config.services.dashboard.auth.nextauth_secret,
  NEXTAUTH_URL: `http://localhost:${config.ports.langtrace}`,
  NEXTAUTH_URL_INTERNAL: `http://localhost:${config.ports.langtrace}`,

  // Clickhouse settings
  CLICK_HOUSE_HOST: config.databases.langtrace_clickhouse.host,
  CLICK_HOUSE_USER: config.databases.langtrace_clickhouse.user,
  CLICK_HOUSE_PASSWORD: config.databases.langtrace_clickhouse.password,
  CLICK_HOUSE_DATABASE_NAME: config.databases.langtrace_clickhouse.database,
  CLICKHOUSE_PORT: config.ports.db.clickhouse,

  // Admin settings
  ADMIN_EMAIL: config.services.langtrace.admin.email,
  ADMIN_PASSWORD: config.services.langtrace.admin.password,
  NEXT_PUBLIC_ENABLE_ADMIN_LOGIN: config.services.langtrace.admin.enable_login,

  // Azure AD settings
  AZURE_AD_CLIENT_ID: config.services.dashboard.auth.azure.client_id,
  AZURE_AD_CLIENT_SECRET: config.services.dashboard.auth.azure.client_secret,
  AZURE_AD_TENANT_ID: config.services.dashboard.auth.azure.tenant_id,

  // Additional settings
  POSTHOG_HOST: config.services.langtrace.posthog.host,
  TELEMETRY_ENABLED: config.services.langtrace.telemetry.enabled,
};

for (const [key, value] of Object.entries(envVars)) {
  console.log(`${key}=${value}`);
}
