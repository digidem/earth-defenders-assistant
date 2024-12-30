import type { z } from "zod";
import type { messagePayloadSchema, messageResponseSchema } from "./schemas";

export type MessagePayload = z.infer<typeof messagePayloadSchema>;
export type MessageResponse = z.infer<typeof messageResponseSchema>;
