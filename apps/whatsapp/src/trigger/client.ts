import { TriggerClient } from "@trigger.dev/sdk";

export const client = new TriggerClient({
  id: "earth-defenders-whatsapp",
  apiUrl: process.env.TRIGGER_API_URL || "http://localhost:3040",
  apiKey: process.env.TRIGGER_API_KEY!,
});
