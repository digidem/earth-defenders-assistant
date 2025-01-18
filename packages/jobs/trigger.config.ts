import type { TriggerConfig } from "@trigger.dev/sdk/v3";
import { config as dotenvConfig } from "dotenv";

dotenvConfig();

export const config: TriggerConfig = {
  project: process.env.TRIGGER_PROJECT_ID ?? "",
  logLevel: "log",
  maxDuration: 360,
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
