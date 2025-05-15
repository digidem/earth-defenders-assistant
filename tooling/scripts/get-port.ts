//@ts-ignore
import { config } from "@eda/config";

const serviceName = process.argv[2];

if (!serviceName) {
  console.error("Service name required");
  process.exit(1);
}

// Special handling for Neo4j
if (serviceName === "neo4j") {
  console.log(config.ports.db.neo4j.http);
  process.exit(0);
}

// Get port from config
const port = config.ports[serviceName as keyof typeof config.ports];

if (port) {
  console.log(port);
  process.exit(0);
}

// Handle nested ports in db section
const dbPort = config.ports.db[serviceName as keyof typeof config.ports.db];
if (dbPort) {
  console.log(dbPort);
  process.exit(0);
}

process.exit(1);
