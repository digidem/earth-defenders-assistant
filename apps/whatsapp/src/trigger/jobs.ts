import { eventTrigger } from "@trigger.dev/sdk";
import { messagePayloadSchema } from "../schemas";
import type { MessagePayload, MessageResponse } from "../types";
import { client } from "./client";

export const sendMessageJob = client.defineJob({
  id: "send-message-job",
  name: "Send Message to API",
  version: "1.0.0",
  trigger: eventTrigger({
    name: "message.send",
    schema: messagePayloadSchema,
  }),
  run: async (payload: MessagePayload): Promise<MessageResponse> => {
    const response = await fetch("http://localhost:3001/api/messages/send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { result: data.result };
  },
});
