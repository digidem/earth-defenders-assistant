//@ts-ignore
import { config } from "@eda/config";

const envVars = {
  NEO4J_AUTH: `${config.databases.neo4j.auth.user}/${config.databases.neo4j.auth.password}`,
  NEO4J_PLUGINS: JSON.stringify(config.databases.neo4j.plugins),
  HEALTHCHECK_INTERVAL: config.databases.neo4j.healthcheck.interval,
  HEALTHCHECK_TIMEOUT: config.databases.neo4j.healthcheck.timeout,
  HEALTHCHECK_RETRIES: config.databases.neo4j.healthcheck.retries,
  NEO4J_HTTP_PORT: config.ports.db.neo4j.http,
  NEO4J_BOLT_PORT: config.ports.db.neo4j.bolt,
};

for (const [key, value] of Object.entries(envVars)) {
  console.log(`${key}=${value}`);
}
