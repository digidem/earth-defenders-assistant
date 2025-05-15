import { z } from "zod";

export const apiCallSchema = z.object({
  endpoint: z.string(),
  method: z.string(),
  statusCode: z.number(),
  duration: z.number(),
  timestamp: z.string(),
  sessionId: z.string(),
  error: z.string().optional(),
});

export type ApiCall = z.infer<typeof apiCallSchema>;
