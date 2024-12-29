import { z } from "zod";

export const messageSchema = z.object({
  message: z.string(),
  sessionId: z.string(),
  audio: z.string().optional(), // Changed from Blob to string
});

export const messageResponseSchema = z.object({
  result: z.string(),
  session_id: z.string().optional(),
});

export const queryParamsSchema = z.object({
  userId: z.string().optional(),
  limit: z.number().int().min(0).optional(),
  offset: z.number().int().min(0).optional(),
  platform: z.enum(["whatsapp", "telegram", "simulator"]).optional(),
});

export type Message = z.infer<typeof messageSchema>;
export type MessageResponse = z.infer<typeof messageResponseSchema>;
