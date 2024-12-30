import { z } from "zod";

export const messagePayloadSchema = z.object({
  message: z.string(),
  sessionId: z.string(),
  audio: z.string().optional(),
});

export const messageResponseSchema = z.object({
  result: z.string(),
});
