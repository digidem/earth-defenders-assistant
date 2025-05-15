import type { TriggerConfig } from "@trigger.dev/sdk/v3";
import { config as dotenvConfig } from "dotenv";

dotenvConfig();

console.log("TRIGGER_API_URL", process.env.TRIGGER_API_URL);
console.log("TRIGGER_PROJECT_ID", process.env.TRIGGER_PROJECT_ID);

export const config: TriggerConfig = {
  project: process.env.TRIGGER_PROJECT_ID ?? "",
  logLevel: "log",
  retries: {
    enabledInDev: true,
    default: {
      maxAttempts: 3,
      minTimeoutInMs: 1000,
      maxTimeoutInMs: 10000,
      factor: 2,
      randomize: true,
    },
  },
};
