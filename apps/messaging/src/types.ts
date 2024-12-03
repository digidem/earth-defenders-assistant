import { z } from "zod";

export const messageSchema = z.object({
  userId: z.string(),
  text: z.string(),
  platform: z.enum(["whatsapp", "telegram", "simulator"]),
  meta: z.record(z.any()).optional(),
});

export const queryParamsSchema = z.object({
  userId: z.string().optional(),
  limit: z.number().int().min(0).optional(),
  offset: z.number().int().min(0).optional(),
  platform: z.enum(["whatsapp", "telegram", "simulator"]).optional(),
});

export type Message = z.infer<typeof messageSchema>;
export type QueryParams = z.infer<typeof queryParamsSchema>;
