import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "yaml";
import { z } from "zod";
import { type Config, ConfigSchema } from "./types";

function formatZodError(error: z.ZodError) {
  const errors = error.errors.map((err) => {
    const path = err.path.join(".");
    let details = "";

    if ("code" in err) {
      switch (err.code) {
        case "invalid_type":
          details = `\nReceived: ${(err as z.ZodInvalidTypeIssue).received}\nExpected: ${
            (err as z.ZodInvalidTypeIssue).expected
          }`;
          break;
        case "invalid_string":
          details = `\nValidation: ${(err as z.ZodInvalidStringIssue).validation}`;
          break;
        case "unrecognized_keys":
          details = `\nKeys: ${(err as z.ZodUnrecognizedKeysIssue).keys.join(", ")}`;
          break;
        default:
          details = "";
      }
    }

    return `[${path}]: ${err.message}${details}`;
  });

  return `Configuration Error:\n${errors.join("\n\n")}`;
}

function getConfig(): Config {
  try {
    const configPath = join(__dirname, "../../../..", "config.yaml");
    const configFile = readFileSync(configPath, "utf8");
    const configData = parse(configFile);

    // Pre-process template literals
    const processedConfig = JSON.parse(
      JSON.stringify(configData).replace(/\${ports\.db\.[^}]+}/g, (match) => {
        const path = match.slice(2, -1).split(".");
        let value = configData;
        for (const key of path) {
          value = value[key];
        }
        return value;
      }),
    );

    return ConfigSchema.parse(processedConfig);
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new Error(formatZodError(error));
    }
    throw error;
  }
}

export const config = getConfig();
export type { Config };
